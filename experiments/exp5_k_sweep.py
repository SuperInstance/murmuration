"""Experiment 5 -- does ORGAN-SCALE STRUCTURE emerge as k grows?

Every murmuration result so far used k=6. k is the whole claim: it is the size of the
information barrier, the number of peers each cell can hear, and therefore the only lever
that moves the system between "an isolated opinion" and "one fluid mass".

  k=1  a cell can hear exactly one peer. The belief is transmitted, not integrated.
  k=6  the working point everything else was measured at.
  k=12 a large neighbourhood: much smoother, slower to sort.
  k=20 nearly everything, on a 90-cell swarm: close to global, which is the point.

The hypothesis worth testing is that k controls a genuine transition -- from transmission,
through organisation, to dissolution -- rather than just making things smoother. A smooth
monotone curve is boring and is what "more neighbours = more mixing" predicts. A
NON-monotone curve with an interior maximum is the interesting shape: an intermediate k
where organisation is strongest, with both too-small and too-large k worse.

If the curve is monotone, the honest report is "k is a smoothing parameter and I
overlooked it" -- which is a fine result, just not a structural one.
"""
import sys, statistics as st, json
sys.path.insert(0, '/workspace/projects/murmuration')
from murmuration.swarm import swarm, sortedness, cluster_count

SEEDS = [3, 7, 11, 19, 23, 31, 41, 53, 61, 71]
N, ROUNDS = 90, 70
KS = [1, 2, 4, 6, 10, 16, 24, 40]

rows = []
for k in KS:
    rs = [swarm(n=N, k=k, rounds=ROUNDS, seed=s, inject=0.85, opposed=0.15) for s in SEEDS]
    pol = [r["polarization"][-1] for r in rs]
    bnd = [r["boundary"] for r in rs]
    srt = [sortedness(r["beliefs"], r["lat"])[0] for r in rs]
    clu = [r["clusters"][-1] for r in rs]
    rows.append({"k": k,
                 "polarization": round(st.mean(pol), 4), "polarization_sd": round(st.pstdev(pol), 4),
                 "boundary": round(st.mean(bnd), 4), "boundary_sd": round(st.pstdev(bnd), 4),
                 "sortedness": round(st.mean(srt), 3), "sortedness_sd": round(st.pstdev(srt), 3),
                 "communities": round(st.mean(clu), 2),
                 "non_degenerate": st.pstdev(bnd) > 1e-4 or st.pstdev(srt) > 1e-3})

print("  Experiment 5 -- does structure peak at an intermediate k?\n")
print(f"  {'k':>3} {'pol':>7} {'boundary':>9} {'sorted':>7} {'sd(sorted)':>11} {'communities':>12}")
for r in rows:
    print(f"  {r['k']:>3} {r['polarization']:>7.3f} {r['boundary']:>9.4f} {r['sortedness']:>7.3f} "
          f"{r['sortedness_sd']:>11.4f} {r['communities']:>12.1f}")

b = [r["boundary"] for r in rows]
sk = [r["sortedness"] for r in rows]
peak_b = KS[b.index(max(b))]
peak_s = KS[sk.index(max(sk))]
print(f"""
  READING IT
  -----------
  boundary peaks at k={peak_b} (max {max(b):.4f}); sortedness peaks at k={peak_s} (max {max(sk):.3f}).

  If the curve is monotone, the honest reading is "k is a smoothing parameter and I
  mistook a dial for a structure." If it has an interior maximum, then there is a
  genuine intermediate regime where the swarm is most organised -- a scale at which
  cells can hear enough to coordinate and few enough to stay independent. That scale
  is the one worth calling an organ.

  Watch the sortedness_sd column especially. A peak in the MEAN is only meaningful if
  the peak is also VARIABLE; a mean with std ~0 is a constant wearing a number.
""")
json.dump(rows, open('/workspace/projects/murmuration/experiments/exp5_results.json','w'), indent=1)
print("  -> exp5_results.json")
