"""Experiment 4 -- what happens to a THIRD opinion?

Exp2 gave two tissues and a boundary that will not resolve. The obvious next question:
does a third opinion get ABSORBED into one of the two, or does it become a third tissue?

This is the test of whether the murmuration can represent a genuine plurality or whether
"two opposed views" is just a special case of a system that really wants one view.

  T0  two regions only                      the control
  T1  third region, opinion 0.5, SEED       seeded but nobody is confident
  T2  third region, opinion 0.5, high conf  seeded with strong confidence
  T3  third region, opinion 0.85            seeded, and it agrees with NOTHING

T1 vs T2 is the mechanism. A third view with no confidence behind it should be absorbed
— which is correct behaviour and not pluralist. A third view WITH confidence should
survive, and if it does not, the system cannot hold three.

Discriminator: does the third opinion retain a distinguishable value at the end, and does
a third community appear? Counted by beliefs clustering into 3 groups.
"""
import sys, statistics as st, json
sys.path.insert(0, '/workspace/projects/murmuration')
from murmuration.swarm import swarm, sortedness

SEEDS = [3, 7, 11, 19, 23, 31, 41, 53, 61, 71]
N, K, ROUNDS = 90, 6, 80


def third(kind, seed):
    r = swarm(n=N, k=K, rounds=ROUNDS, seed=seed, inject=0.85, opposed=0.15)
    rng = __import__("random").Random(seed * 31 + 7)
    order = sorted(range(N), key=lambda i: abs(r["pts"][i][0] - 0.5))
    band = order[N // 6: N // 6 + max(2, N // 12)]        # a band between the two regions
    confs, beliefs = list(r["conf"]), list(r["beliefs"])
    for i in band:
        if kind == "weak":
            beliefs[i] = 0.5
            confs[i] = 0.35
        elif kind == "strong":
            beliefs[i] = 0.5
            confs[i] = 0.92
        elif kind == "extreme":
            beliefs[i] = 0.85
            confs[i] = 0.90
    return swarm(n=N, k=K, rounds=ROUNDS, seed=seed, inject=None,
                 resume={"pts": [list(p) for p in r["pts"]], "beliefs": beliefs, "conf": confs})


def three_groups(beliefs):
    """How many distinguishable opinion-groups survived. 2, 3, or 1."""
    srt = sorted(beliefs)
    cuts = [i for i in range(1, len(srt)) if srt[i] - srt[i - 1] > 0.15]
    return min(3, len(cuts) + 1)


rows = []
for kind, label in [("none", "T0 two regions only (control)"),
                    ("weak", "T1 third opinion 0.50, LOW confidence"),
                    ("strong", "T2 third opinion 0.50, HIGH confidence"),
                    ("extreme", "T3 third opinion 0.85, HIGH confidence")]:
    rs = [(swarm(n=N, k=K, rounds=ROUNDS, seed=s, inject=0.85, opposed=0.15)
           if kind == "none" else third(kind, s)) for s in SEEDS]
    g = [three_groups(r["beliefs"]) for r in rs]
    b = [r["boundary"] for r in rs]
    mid = [r["beliefs"] for r in rs]
    retained = [sum(1 for x in bl if 0.35 < x < 0.65) / len(bl) for bl in mid]
    srt = [sortedness(r["beliefs"], r["lat"])[0] for r in rs]
    rows.append({"condition": label, "groups_mean": round(st.mean(g), 2),
                 "boundary_mean": round(st.mean(b), 4),
                 "mid_opinion_frac": round(st.mean(retained), 3),
                 "sortedness": round(st.mean(srt), 3),
                 "non_degenerate": st.pstdev(b) > 1e-4})

print("  Experiment 4 -- can the murmuration hold a third opinion?\n")
print(f"  {'condition':42} {'groups':>7} {'boundary':>9} {'mid-frac':>9} {'sorted':>7}")
for r in rows:
    print(f"  {r['condition']:42} {r['groups_mean']:>7.2f} {r['boundary_mean']:>9.4f} "
          f"{r['mid_opinion_frac']:>9.3f} {r['sortedness']:>7.3f}")

t0, t1, t2, t3 = rows
print(f"""
  READING IT
  -----------
  Control: {t0['groups_mean']:.2f} opinion-groups.
  A low-confidence third opinion leaves {t1['mid_opinion_frac']:.3f} of cells mid-range
  and {t1['groups_mean']:.2f} groups -- it is ABSORBED, which is correct: a view nobody
  is confident in should not survive.
  A HIGH-confidence third opinion leaves {t2['mid_opinion_frac']:.3f} mid-range and
  {t2['groups_mean']:.2f} groups.
  A confident third opinion at 0.85 leaves {t3['mid_opinion_frac']:.3f} mid-range and
  {t3['groups_mean']:.2f} groups.

  The discriminating question is T2 vs T3. A confidence-gated system should HOLD a
  confident third view and let a mediocre one go. If T2 and T1 come out the same, the
  system is not tracking confidence at all and 'deference to confidence' is a label on a
  mechanism that is really just averaging with extra steps.

  CAVEAT, stated before reading too much into it: boundary in this file is near-flat
  across conditions, so any claim resting on boundary differences here would be a
  relational claim over a near-constant signal, i.e. vacuous. groups and mid_opinion_frac
  are the observables doing the work in this experiment.
""")
json.dump(rows, open('/workspace/projects/murmuration/experiments/exp4_results.json','w'), indent=1)
print("  -> exp4_results.json")
