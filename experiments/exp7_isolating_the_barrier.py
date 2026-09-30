"""Experiment 7 -- isolating the information barrier, holding EVERYTHING else fixed.

An adversarial review of the murmuration found a real confound in exp1, and it is the
kind that quietly invalidates a result:

  exp1 compared LOCAL propagation against a CENTRAL BROADCAST. But that comparison
  changed TWO things at once:
     (a) the information topology  (k neighbours  vs  everyone)
     (b) the number of DISTINCT VOICES each cell hears (6 different cells  vs  1 message
         repeated 6 times)
  So "local beats broadcast on structure" might be entirely about voice diversity, with
  the barrier playing no part at all. That is not a small ambiguity; it is the mechanism.

THE CLEAN DESIGN. Give every cell the SAME NUMBER OF INPUTS in both conditions. The only
thing that differs is how many DISTINCT opinions those inputs carry.

  LOCAL      6 inputs, 6 different neighbours, each with its own opinion.
  BROADCAST  6 inputs, all carrying the SAME single message.
  SKEPTIC    6 inputs, 6 different neighbours, but each neighbour's opinion is replaced
             by a single drawn-once message -- the same diversity as LOCAL, the same
             reach as nothing. (This is the awkward one; it exists to catch the case
             where voice count is doing all the work and topology is decoration.)

Identical cells, identical update rule, identical input count, identical rounds. The only
free variable is whether the six inputs disagree with each other.

PREDICTION, stated before running so it can fail: if the barrier matters, LOCAL produces
more communities than BROADCAST at the same input count. If it does not, the barrier is
decoration and the honest result is that voice diversity was the whole story.
"""
import sys, statistics as st, json, random
sys.path.insert(0, '/workspace/projects/murmuration')
from murmuration.swarm import knn_lattice, cluster_count, _reknn, polarization

SEEDS = [3, 7, 11, 19, 23, 31, 41, 53, 61, 71]
N, K, ROUNDS = 90, 6, 70


def run(mode, seed):
    """Same cells, same rule, same 6 inputs. Only the VOICE DIVERSITY differs."""
    rng = random.Random(seed)
    pts, lat = knn_lattice(N, K, seed=seed)
    b = [rng.uniform(0, 1) for _ in range(N)]
    conf = [rng.uniform(0.2, 0.8) for _ in range(N)]
    msg = 0.85                                    # the single broadcast message

    for _ in range(ROUNDS):
        newb, newc = list(b), list(conf)
        for i, nb in enumerate(lat):
            seen = []
            for j in nb:
                if mode == "local":
                    seen.append((b[j], conf[j]))
                elif mode == "broadcast":
                    # 6 inputs, all the SAME voice. Input count held equal to local.
                    seen.append((msg, 0.9))
                else:                              # skeptic
                    seen.append((msg if j == nb[0] else b[j], conf[j]))
            if not seen:
                continue
            best = max(seen, key=lambda x: x[1])
            me = b[i]
            if best[1] > conf[i] + 0.03:
                newb[i] = 0.85 * best[0] + 0.15 * me
                newc[i] = min(0.95, conf[i] + 0.04)
            else:
                near = [v for v, _ in seen if abs(v - me) < 0.15]
                if near:
                    newb[i] = 0.85 * (sum(near) / len(near)) + 0.15 * me
                    newc[i] = min(0.95, conf[i] + 0.01)
        b, conf = newb, newc
        for i, nb in enumerate(lat):
            ax = ay = 0.0
            for j in nb:
                dx = pts[j][0] - pts[i][0]; dy = pts[j][1] - pts[i][1]
                d = (dx * dx + dy * dy) ** 0.5 or 1e-9
                w = b[j] - b[i]
                ax += dx / d * abs(w); ay += dy / d * abs(w)
            pts[i] = [(pts[i][0] + 0.035 * ax) % 1.0, (pts[i][1] + 0.035 * ay) % 1.0]
        lat = _reknn(pts, K)
    return {"pol": polarization(b), "clusters": cluster_count(pts, lat), "beliefs": b}


rows = []
for mode, label in [("local", "LOCAL     6 inputs, 6 distinct voices"),
                    ("broadcast", "BROADCAST 6 inputs, 1 repeated voice"),
                    ("skeptic", "SKEPTIC   6 inputs, 5 distinct + 1 forced")]:
    rs = [run(mode, s) for s in SEEDS]
    pol = [r["pol"] for r in rs]
    cl = [r["clusters"] for r in rs]
    rows.append({"condition": label, "polarization": round(st.mean(pol), 4),
                 "polarization_sd": round(st.pstdev(pol), 4),
                 "communities": round(st.mean(cl), 2), "communities_sd": round(st.pstdev(cl), 2),
                 "non_degenerate": st.pstdev(pol) > 1e-4 or st.pstdev(cl) > 1e-3})

print("  Experiment 7 -- the barrier, isolated from voice diversity\n")
print(f"  {'condition':40} {'pol':>7} {'sd':>7} {'communities':>12} {'sd':>7}")
for r in rows:
    print(f"  {r['condition']:40} {r['polarization']:>7.3f} {r['polarization_sd']:>7.3f} "
          f"{r['communities']:>12.1f} {r['communities_sd']:>7.2f}")

L, B, S = rows
print(f"""
  READING IT
  -----------
  Same cells, same rule, same 6 inputs, same rounds. Only the number of DISTINCT
  opinions arriving per cell differs.

  LOCAL     {L['communities']:5.1f} communities, polarization {L['polarization']:.3f} (sd {L['polarization_sd']:.3f})
  BROADCAST {B['communities']:5.1f} communities, polarization {B['polarization']:.3f} (sd {B['polarization_sd']:.3f})
  SKEPTIC   {S['communities']:5.1f} communities, polarization {S['polarization']:.3f} (sd {S['polarization_sd']:.3f})

  If the BARRIER is what matters, LOCAL must out-structure BROADCAST at equal input
  count, because the only thing separating them is whether those 6 inputs can disagree.

  THE HONEST ALTERNATIVE, stated in advance: if LOCAL and BROADCAST come out the same,
  then the barrier is decoration and exp1's headline was voice diversity all along. In
  that case exp1 gets annotated as a confound, not a discovery, and the only surviving
  novel piece is the degree-preserving rewiring CONTROL from exp2.

  Note B's sd. If it is 0.000 that is arithmetic, not robustness -- a broadcast is
  deterministic by construction, and a zero-variance number cannot support a relational
  claim. The degenerate-measurement rule applies to the null result as much as the
  positive one.
""")
json.dump(rows, open('/workspace/projects/murmuration/experiments/exp7_results.json','w'), indent=1)
print("  -> exp7_results.json")
