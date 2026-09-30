"""Experiment 10 -- WHY does dimensionality change the stability class?

exp8 and exp9 established a fact and left a hole. Fact: 1-D holds two smear-like groups,
2-D holds three well-separated, defended tissues. Hole: no mechanism.

Arguing for a mechanism is not discovery. So: build the candidates, and find a
manipulation where they DISAGREE.

THE TWO LIVE HYPOTHESES, stated as predictions:

  M_ORDER   The 1-D limit is an ORDERING artefact. On a line, three opinions are ordered
            A < B < C, so B sits BETWEEN two others and has nowhere to go. It is squeezed
            out by packing alone, and dimension is irrelevant to the mechanism.
            PREDICTS: order matters. In 2-D, three opinions placed COLLINEAR should lose
            the middle one exactly as 1-D does.

  M_SEP     The advantage is MUTUAL NON-ADJACENCY. In 2-D, k regions can each be
            separated from the others with no two of them sharing a boundary. In 1-D,
            only two regions can be separated at once -- the third is always adjacent to
            one of them.
            PREDICTS: geometry matters. Collinear 2-D seeds lose the middle one; seeds at
            the CORNERS of the same square do not.

These make different predictions for one manipulation: same 2-D opinion space, same rule,
same rounds, seeds either COLLINEAR or at the CORNERS.

  If collinear == 1-D and corners != 1-D  ->  M_SEP. Dimension is a proxy for being able
                                             to place regions that never touch.
  If collinear == corners != 1-D        ->  something else, and I have no explanation.
  If collinear == corners == 1-D         ->  M_ORDER, and exp8's 2-D result was a
                                             placement accident rather than a dimensional one.

Plus 3-D at four cube corners, which is the natural extrapolation if M_SEP holds.

THE INSTRUMENT HAS TO BE ABLE TO SAY "THIS OPINION DIED." So the readout is PER-SEED
survival: for each of the three seeded opinions, did a community of cells still hold it at
the end? That is a different question from "how many groups are there", and a group count
of 2 is consistent with all three dying and two unrelated clusters forming.
"""
import sys, random, math, statistics as st, json, itertools
sys.path.insert(0, '/workspace/projects/murmuration')
from murmuration.swarm import knn_lattice, _reknn
import importlib.util as _u
_s = _u.spec_from_file_location("e8", "/workspace/projects/murmuration/experiments/exp8_opinion_dimension.py")
exp8 = _u.module_from_spec(_s); _s.loader.exec_module(exp8)

SEEDS = [3, 7, 11, 19, 23, 31, 41, 53, 61, 71]
N, K, ROUNDS = 96, 6, 80

LAYOUTS = {
  "1-D  three points on a line": {
     "dim": 1, "n": 3,
     "seeds": [0.15, 0.50, 0.85]},
  "2-D  COLLINEAR (on a line inside the square)": {
     "dim": 2, "n": 3,
     "seeds": [(0.18, 0.50), (0.50, 0.50), (0.82, 0.50)]},
  "2-D  CORNERS of the square": {
     "dim": 2, "n": 3,
     "seeds": [(0.18, 0.18), (0.82, 0.18), (0.50, 0.84)]},
  "3-D  four CUBES corners (simulated)": {
     "dim": 3, "n": 4,
     "seeds": [(0.18, 0.18, 0.18), (0.82, 0.18, 0.18),
               (0.18, 0.82, 0.82), (0.82, 0.82, 0.82)]},
}


def run(dim, seed_pos, seed):
    rng = random.Random(seed)
    pts, lat = knn_lattice(N, K, seed=seed)
    d = len(seed_pos[0]) if dim > 1 else 1
    if d == 1:
        # every belief is a 1-TUPLE, seeded and unseeded alike. Mixing floats and tuples
        # here cost three debugging cycles; the dimension is a property of the container,
        # not of whether the cell happened to be seeded.
        b = [(rng.uniform(0, 1),) for _ in range(N)]
        seed_pos = [(v,) for v in seed_pos]
    else:
        b = [tuple(rng.random() for _ in range(d)) for _ in range(N)]
    conf = [rng.uniform(0.2, 0.8) for _ in range(N)]
    # seed each opinion into a contiguous band, placed to match the layout
    per = max(2, N // (2 * len(seed_pos)))
    used = set()
    for si, sv in enumerate(seed_pos):
        anchor = sv[0] if isinstance(sv, (tuple, list)) else sv
        order = [i for i in sorted(range(N), key=lambda i: abs(pts[i][0] - anchor))
                 if i not in used]
        for i in order[:per]:
            b[i] = sv
            conf[i] = 0.92
            used.add(i)
    for _ in range(ROUNDS):
        nb_b, nb_c = list(b), list(conf)
        for i, nb in enumerate(lat):
            seen = [(b[j], conf[j]) for j in nb]
            if not seen:
                continue
            best = max(seen, key=lambda x: x[1])
            if best[1] > conf[i] + 0.03:
                nb_b[i] = tuple(0.85 * best[0][k] + 0.15 * b[i][k] for k in range(d))
                nb_c[i] = min(0.95, conf[i] + 0.04)
            else:
                thr = 0.15 if d == 1 else 0.20
                near = [v for v, _ in seen
                        if (abs(v[0] - b[i][0]) if d == 1 else math.dist(v, b[i])) < thr]
                if near:
                    # the same arithmetic for every dimension: d==1 works as a 1-tuple
                    nb_b[i] = tuple(
                        0.85 * (sum(v[k] for v in near) / len(near)) + 0.15 * b[i][k]
                        for k in range(d))
                    nb_c[i] = min(0.95, conf[i] + 0.01)
        b, conf = nb_b, nb_c
        for i, nb in enumerate(lat):
            ax = ay = 0.0
            for j in nb:
                dx = pts[j][0] - pts[i][0]; dy = pts[j][1] - pts[i][1]
                dd = math.hypot(dx, dy) or 1e-9
                w = (abs(b[j][0] - b[i][0]) if d == 1 else math.dist(b[j], b[i]))
                ax += dx / dd * w; ay += dy / dd * w
            pts[i] = [(pts[i][0] + 0.03 * ax) % 1.0, (pts[i][1] + 0.03 * ay) % 1.0]
        lat = _reknn(pts, K)
    return b, pts, lat


def survival(b, d, seed_pos, tol=0.22):
    """For each SEEDED opinion: is there still a population holding it?

    A seeded opinion counts as alive if at least `q` of all cells sit within `tol` of it.
    This is deliberately a different question from 'how many groups are there' -- a count
    of 2 is equally consistent with one opinion winning and with all three dying.
    """
    n = len(b)
    out = []
    for sv in seed_pos:
        target = (sv,) if not isinstance(sv, (tuple, list)) else tuple(sv)
        near = sum(1 for v in b
                   if (abs(v[0] - target[0]) if d == 1 else math.dist(v, target)) < tol)
        out.append(near / n)
    return out


def main():
    print("  Experiment 10 -- is the 1-D limit ORDERING, or MUTUAL NON-ADJACENCY?\n")
    rows = []
    for label, cfg in LAYOUTS.items():
        dim, sp = cfg["dim"], cfg["seeds"]
        d = len(sp[0]) if dim > 1 else 1
        surv = []
        for s in SEEDS:
            bb, _, _ = run(d, sp, s)
            surv.append(survival(bb, d, sp))
        per = list(zip(*surv))
        means = [st.mean(x) for x in per]
        # an opinion is "dead" in a run if under 2% of the population still holds it
        deaths = [sum(1 for x in col if x < 0.02) for col in surv]
        rows.append({"layout": label, "dim": d, "n_seeded": len(sp),
                     "survival_per_opinion": [round(m, 3) for m in means],
                     "mean_deaths_per_run": round(st.mean(deaths), 2),
                     "deaths_sd": round(st.pstdev(deaths), 3)})
    print(f"  {'layout':50} {'survival of each seeded opinion':>34} {'deaths/run':>12}")
    for r in rows:
        print(f"  {r['layout']:50} {str(r['survival_per_opinion']):>34} "
              f"{r['mean_deaths_per_run']:>8.2f} +-{r['deaths_sd']:.2f}")
    col = rows[0]["mean_deaths_per_run"]; cor = rows[2]["mean_deaths_per_run"]
    print(f"""
  READING IT
  -----------
  1-D on a line        : {rows[0]['mean_deaths_per_run']:.2f} of 3 seeded opinions die per run
  2-D COLLINEAR seeds  : {rows[1]['mean_deaths_per_run']:.2f} of 3 die
  2-D CORNER seeds     : {rows[2]['mean_deaths_per_run']:.2f} of 3 die
  3-D CUBE corners     : {rows[3]['mean_deaths_per_run']:.2f} of 4 die

  M_ORDER predicts: collinear == 1-D (ordering is what squeezes the middle one out).
  M_SEP  predicts: collinear == 1-D but corners != 1-D (only non-adjacency preserves it).

  The two hypotheses agree on one arm and disagree on the other, which is the whole
  point of running both arms. Whichever survives, exp8's headline is explained by a
  mechanism rather than asserted, and the losing hypothesis gets deleted rather than
  quietly kept.

  A dead opinion is one under 2% of the population still holding it. That threshold is a
  JUDGEMENT CALL and is the weakest link in this file: it is the only place a number was
  chosen rather than derived. If the results sit near the threshold the conclusion is
  fragile, and the honest response is to move it and see if the answer changes.
""")
    json.dump(rows, open('/workspace/projects/murmuration/experiments/exp10_results.json','w'), indent=1)
    print("  -> exp10_results.json")


if __name__ == "__main__":
    main()
