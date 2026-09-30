"""Experiment 1 -- does a LOCAL opinion become a GLOBAL one without an authority?

Four conditions, run on identical seeds. The design point is the LAST two: without them
a rising polarization is uninterpretable, because a swarm that cohered on its own would
look identical to a swarm that was told what to think.

  A  local-seed    5% of cells seeded with one opinion, in one spatial region
  B  broadcast     the same opinion pushed to every cell at once (the central authority)
  C  no-seed       nothing injected. If this also coheres, polarization proves nothing.
  D  split         two OPPOSED regions seeded. Does it resolve, or form a boundary?

Claim under test: a murmuration can carry a local opinion to a global one using only
local rules, and the resulting structure is the same KIND of object whether it got there
by seed or by broadcast -- but not the same SPEED, and not in the same shape for C.
"""
import sys, statistics as st, json
sys.path.insert(0, '/workspace/projects/murmuration')
from murmuration.swarm import swarm, polarization, cluster_count

SEEDS = [3, 7, 11, 19, 23, 31, 41, 53, 61, 71]
ROUNDS, N, K = 60, 80, 6


def summarise(tag, runs, extra=None):
    fin = [r["polarization"][-1] for r in runs]
    sd  = [st.pstdev(r["polarization"]) for r in runs]
    cl  = [r["clusters"][-1] for r in runs]
    row = {"condition": tag, "final_polarization_mean": round(st.mean(fin), 4),
           "final_polarization_sd_across_seeds": round(st.pstdev(fin), 4),
           "mean_stdev_within_run": round(st.mean(sd), 4),
           "final_clusters_mean": round(st.mean(cl), 2),
           "n_seeds": len(runs)}
    if extra: row.update(extra)
    # THE RULE: a relational claim over a degenerate signal is vacuous.
    row["non_degenerate"] = st.mean(sd) > 0.01
    return row


print(f"  Experiment 1 -- local opinion -> global consensus, no authority")
print(f"  n={N} cells, k={K} neighbours, {ROUNDS} rounds, {len(SEEDS)} seeds\n")
rows = []
rows.append(summarise("A local-seed (5%, one region)",
                      [swarm(n=N, k=K, rounds=ROUNDS, seed=s, inject=0.85) for s in SEEDS]))
rows.append(summarise("B broadcast (central authority)",
                      [swarm(n=N, k=K, rounds=ROUNDS, seed=s, inject=0.85, central=True) for s in SEEDS]))
rows.append(summarise("C no-seed (control for DANGER)",
                      [swarm(n=N, k=K, rounds=ROUNDS, seed=s, inject=None) for s in SEEDS]))

# D: two opposed regions
split = []
for s in SEEDS:
    r = swarm(n=N, k=K, rounds=ROUNDS, seed=s, inject=0.85)
    # force the opposite half
    half = sorted(range(N), key=lambda i: r["pts"][i][0])
    for i in half[N//2:]:
        r["cells"][i].seed = 0.001
        r["cells"][i]._b = 0.15
    r2 = swarm(n=N, k=K, rounds=ROUNDS, seed=s, inject=0.85)
    split.append(r2)
rows.append(summarise("D re-run A (placeholder for split)", split))

print(f"  {'condition':38} {'final pol':>10} {'sd(seeds)':>10} {'sd(round)':>10} {'clusters':>9}  valid?")
for r in rows:
    print(f"  {r['condition']:38} {r['final_polarization_mean']:>10.3f} "
          f"{r['final_polarization_sd_across_seeds']:>10.3f} {r['mean_stdev_within_run']:>10.4f} "
          f"{r['final_clusters_mean']:>9.1f}  {'yes' if r['non_degenerate'] else 'NO'}")
json.dump(rows, open('/workspace/projects/murmuration/experiments/exp1_results.json', 'w'), indent=1)
print("\n  -> exp1_results.json")
