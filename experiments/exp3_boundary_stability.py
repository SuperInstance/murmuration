"""Experiment 3 -- is the boundary a structure, or an accident of where the seeds landed?

Exp2 showed two opposed regions form a boundary. That is a snapshot, and a snapshot does
not say whether the boundary is maintained or merely coincidental.

So: shove it, then RE-RUN the dynamics and see what reforms. Measuring a perturbation
without re-running measures a stale value — the first version of this file returned
byte-identical numbers for four different perturbations and looked stable. The numbers
were frozen because the boundary was computed before anything was perturbed.

  P0  no perturbation    the control
  P1  positional kick    20% of cells displaced
  P2  opinion flip       5% of cells flipped
  P3  full scramble      every position re-randomised
  P4  anneal kick        displace 60%, then give it 3x the rounds to recover

P4 is the interesting one. A structure the system actively maintains reforms after a shove
it could not fully recover from in the short run. One that does not reform was an
accident of initialisation.
"""
import sys, random, statistics as st, json
sys.path.insert(0, '/workspace/projects/murmuration')
from murmuration.swarm import swarm, sortedness

SEEDS = [3, 7, 11, 19, 23, 31, 41, 53, 61, 71]
N, K, ROUNDS = 80, 6, 60


def shove(kind, mag, seed):
    r = swarm(n=N, k=K, rounds=ROUNDS, seed=seed, inject=0.85, opposed=0.15)
    rng = random.Random(seed * 977 + 13)
    pts = [list(p) for p in r["pts"]]
    beliefs = list(r["beliefs"])
    if kind == "kick":
        for i in rng.sample(range(N), int(N * mag)):
            pts[i] = [(pts[i][0] + rng.uniform(-.35, .35)) % 1.0,
                      (pts[i][1] + rng.uniform(-.35, .35)) % 1.0]
    elif kind == "flip":
        for i in rng.sample(range(N), max(1, int(N * mag))):
            beliefs[i] = 1.0 - beliefs[i]
    elif kind == "scramble":
        pts = [[rng.random(), rng.random()] for _ in range(N)]
    return swarm(n=N, k=K, rounds=ROUNDS, seed=seed, inject=None,
                 resume={"pts": pts, "beliefs": beliefs, "conf": r["conf"]})


def measure(kind, mag, label, extra_rounds=0):
    rs = [swarm(n=N, k=K, rounds=ROUNDS + extra_rounds, seed=s, inject=0.85, opposed=0.15)
          if kind == "none" else
          shove(kind, mag, s) for s in SEEDS]
    # anneal: re-run the shoved state for extra rounds
    if extra_rounds:
        annealed = []
        for s, r in zip(SEEDS, rs):
            rr = swarm(n=N, k=K, rounds=extra_rounds, seed=s, inject=None,
                       resume={"pts": [list(p) for p in r["pts"]],
                               "beliefs": list(r["beliefs"]), "conf": r["conf"]})
            annealed.append(rr)
        rs = annealed
    b = [r["boundary"] for r in rs]
    srt = [sortedness(r["beliefs"], r["lat"]) for r in rs]
    return {"condition": label, "boundary_mean": round(st.mean(b), 4),
            "boundary_sd": round(st.pstdev(b), 4),
            "sortedness_ratio": round(st.mean(x[0] for x in srt), 3),
            "real_agreement": round(st.mean(x[1] for x in srt), 4),
            "rewired_agreement": round(st.mean(x[2] for x in srt), 4),
            "non_degenerate": st.pstdev(b) > 1e-4}


rows = [measure("none", 0.0, "P0 no perturbation (control)"),
        measure("kick", 0.20, "P1 positional kick to 20%"),
        measure("flip", 0.05, "P2 opinion flip in 5%"),
        measure("scramble", 1.0, "P3 full position scramble"),
        measure("kick", 0.60, "P4 kick 60% + 180 rounds anneal", extra_rounds=180)]

print("  Experiment 3 -- does the boundary survive being shoved?\n")
print(f"  {'condition':36} {'boundary':>9} {'sd':>7} {'sorted':>7} {'real':>6} {'rewired':>8}")
for r in rows:
    print(f"  {r['condition']:36} {r['boundary_mean']:>9.4f} {r['boundary_sd']:>7.4f} "
          f"{r['sortedness_ratio']:>7.3f} {r['real_agreement']:>6.3f} {r['rewired_agreement']:>8.3f}")

b = {r["condition"][:2]: r["boundary_mean"] for r in rows}
sc = {r["condition"][:2]: r["sortedness_ratio"] for r in rows}
agree4 = rows[4]["real_agreement"]
p1, p2, p3, p4 = b["P1"]/b["P0"], b["P2"]/b["P0"], b["P3"]/b["P0"], b["P4"]/b["P0"]
s0, s1, s3 = sc["P0"], sc["P1"], sc["P3"]

print(f"""
  READING IT -- and it partly KILLS the claim made in exp2
  ------------------------------------------------------
  A 20% positional kick leaves  {p1:.2f}x of the boundary.
  A 5% opinion flip leaves      {p2:.2f}x.
  A full scramble leaves        {p3:.2f}x.
  A 60% kick + 180 rounds of annealing leaves {p4:.2f}x, with neighbour agreement
  rising to {agree4:.3f}.

  That last row is the finding, and it is a NEGATIVE result about my own claim. The
  two-tissue structure does not REGENERATE. Given enough rounds after a large shove the
  swarm heals into UNANIMITY ({agree4:.3f} agreement) instead of rebuilding two tissues
  with a boundary between them. The boundary in exp2 is therefore not a self-maintaining
  structure -- it is stable under mild perturbation and then dissolves, permanently, into
  consensus.

  I called it a tissue in exp2. More honestly it is a TRANSIENT: a configuration the
  system tolerates but does not defend. A tissue that cannot reform after being damaged
  is not a tissue yet. exp2's 15.6x is a property of a FRESH, UNPERTURBED two-view
  configuration, not of a robust structure.

  SECOND FINDING, and it is about the instrument rather than the swarm: SORTEDNESS BARELY
  MOVES. {s0:.2f}x control, {s1:.2f}x kicked, {s3:.2f}x fully scrambled. A metric this
  flat across conditions cannot support a claim about stability -- it is near-constant,
  and a relational claim over a near-constant signal is vacuous. I chose sortedness
  precisely because a uniform colouring could not fake it, and it cannot be faked. But the
  system sorts under EVERY condition tested, including ones designed to destroy the thing
  being sorted, so it is a real property and a useless discriminator here.

  What does discriminate is boundary, and it discriminates downward: every perturbation
  reduces it, and the largest annihilates it.
""")
json.dump(rows, open('/workspace/projects/murmuration/experiments/exp3_results.json','w'), indent=1)
print("  -> exp3_results.json")
