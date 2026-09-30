"""Experiment 8 -- is the two-way limit the OPINION SPACE, or the RULE?

Every result so far lives on a line: a belief is a scalar in [0,1]. That single choice
does enormous unacknowledged work:

  * exp4's "plurality collapses to two" may not be a property of the LOCAL RULE at all --
    it may simply be that a line cannot hold three well-separated opinions.
  * bounded-confidence work (Hegselmann-Krause, Deffuant) is also 1-D. Two components on a
    line is close to degenerate. If this system is 1-D too, it is living in someone
    else's regime and cannot be distinguished from their result by any experiment I ran.

So: make the belief a POINT IN 2-D and run the identical local rule. Same cells, same
deferece-to-confidence update, same k-nearest lattice, same rounds, same three seeds.

  1D, 3 seeds   three opinions at 0.15 / 0.50 / 0.85 on a line
  2D, 3 seeds   three opinions at three CORNERS of the square -- maximally separated in
                the only sense that matters for a clustering rule

THE PREDICTION, stated before running: if the two-way limit comes from the LINE, then 2-D
will hold three tissues and 1-D will not. If both give the same answer, the limit is the
RULE, and the opinion space was never the constraint.

This is also the only experiment here that is NOT prior art. Bounded confidence is
overwhelmingly 1-D; a 2-D local rule that sustains three stable communities is a
different object, and I have found no prior for it.
"""
import sys, random, math, statistics as st, json
sys.path.insert(0, '/workspace/projects/murmuration')
from murmuration.swarm import knn_lattice, _reknn

SEEDS = [3, 7, 11, 19, 23, 31, 41, 53, 61, 71]
N, K, ROUNDS = 96, 6, 80


def run(dim, n_seeds, seed):
    rng = random.Random(seed)
    pts, lat = knn_lattice(N, K, seed=seed)
    if dim == 1:
        b = [rng.uniform(0, 1) for _ in range(N)]
        seeds_pos = [0.15, 0.50, 0.85][:n_seeds]
    else:
        b = [(rng.random(), rng.random()) for _ in range(N)]
        seeds_pos = [(0.18, 0.18), (0.82, 0.18), (0.50, 0.84)][:n_seeds]
    conf = [rng.uniform(0.2, 0.8) for _ in range(N)]

    # seed each opinion into a contiguous spatial region so the comparison is fair
    for si, sv in enumerate(seeds_pos):
        cx = 0.5 if dim == 1 else seeds_pos[si][0]
        order = sorted(range(N), key=lambda i: abs(pts[i][0] - cx))
        for i in order[:max(2, N // (2 * n_seeds))]:
            b[i] = sv
            conf[i] = 0.92

    for _ in range(ROUNDS):
        nb_b = list(b)
        nb_c = list(conf)
        for i, nb in enumerate(lat):
            seen = [(b[j], conf[j]) for j in nb]
            if not seen:
                continue
            def dist(v):
                return abs(v - b[i]) if dim == 1 else math.dist(v, b[i])
            best = max(seen, key=lambda x: x[1])
            if best[1] > conf[i] + 0.03:
                if dim == 1:
                    nb_b[i] = 0.85 * best[0] + 0.15 * b[i]
                else:
                    nb_b[i] = (0.85 * best[0][0] + 0.15 * b[i][0],
                               0.85 * best[0][1] + 0.15 * b[i][1])
                nb_c[i] = min(0.95, conf[i] + 0.04)
            else:
                near = [v for v, _ in seen if dist(v) < (0.15 if dim == 1 else 0.20)]
                if near:
                    if dim == 1:
                        nb_b[i] = 0.85 * (sum(near) / len(near)) + 0.15 * b[i]
                    else:
                        mx = sum(v[0] for v in near) / len(near)
                        my = sum(v[1] for v in near) / len(near)
                        nb_b[i] = (0.85 * mx + 0.15 * b[i][0], 0.85 * my + 0.15 * b[i][1])
                    nb_c[i] = min(0.95, conf[i] + 0.01)
        b, conf = nb_b, nb_c
        # position drifts toward similar beliefs -- the same assortative rule as before
        for i, nb in enumerate(lat):
            ax = ay = 0.0
            for j in nb:
                dx = pts[j][0] - pts[i][0]; dy = pts[j][1] - pts[i][1]
                d = math.hypot(dx, dy) or 1e-9
                w = (abs(b[j] - b[i]) if dim == 1 else math.dist(b[j], b[i]))
                ax += dx / d * w; ay += dy / d * w
            pts[i] = [(pts[i][0] + 0.03 * ax) % 1.0, (pts[i][1] + 0.03 * ay) % 1.0]
        lat = _reknn(pts, K)
    return b, conf, pts, lat


def n_groups(b, dim):
    """How many distinct opinion-communities survived."""
    srt = sorted(b)
    if dim == 1:
        cuts = [i for i in range(1, len(srt)) if srt[i] - srt[i-1] > 0.15]
    else:
        # single-link clustering on a 0.20 radius
        parent = list(range(len(b)))
        def find(a):
            while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
            return a
        for i in range(len(b)):
            for j in range(i+1, len(b)):
                if math.dist(b[i], b[j]) < 0.20:
                    x, y = find(i), find(j)
                    if x != y: parent[x] = y
        cuts = [0] * (len({find(i) for i in range(len(b))}) - 1)
    return len(cuts) + 1


def separation(b, dim):
    """BETWEEN-cluster separation / WITHIN-cluster spread. A ratio, not a minimum.

    The first version of this was the minimum pairwise opinion distance, and it returned
    exactly 0.0000 with sd 0.0000 in every condition -- which is not a measurement, it is
    arithmetic: with 96 cells there are 4560 pairs and two of them hitting the same value
    is certain, so the minimum is pinned at zero forever. A metric that cannot come out
    of zero cannot support a relational claim, however true its neighbours look.

    The ratio is the right observable because it is scale-free and cannot be pinned: it
    asks whether the clusters are further apart than they are wide. A value near 1 means
    the "clusters" are a partition of a smear, which is what three arbitrary groups of a
    continuous distribution would also give you.
    """
    g = assign(b, dim)
    groups = {}
    for i, c in enumerate(g):
        groups.setdefault(c, []).append(i)
    if len(groups) < 2:
        return 0.0
    cents = []
    for _, idxs in groups.items():
        if dim == 1:
            cents.append(sum(b[i] for i in idxs) / len(idxs))
        else:
            cents.append((sum(b[i][0] for i in idxs) / len(idxs),
                          sum(b[i][1] for i in idxs) / len(idxs)))
    def d(u, v):
        return abs(u - v) if dim == 1 else math.dist(u, v)
    between = min(d(cents[a], cents[b_]) for a in range(len(cents)) for b_ in range(len(cents)) if a != b_)
    within = 0.0
    for ci, idxs in groups.items():
        for i in idxs:
            within += d(b[i], cents[ci])
    within /= len(b)
    return between / max(within, 1e-9)


def assign(b, dim):
    """Label each cell with its opinion-community, for both dimensionalities."""
    if dim == 1:
        srt = sorted(range(len(b)), key=lambda i: b[i])
        lab, c, prev = [0]*len(b), 0, None
        for i in srt:
            if prev is not None and b[i] - prev > 0.15:
                c += 1
            lab[i] = c; prev = b[i]
        return lab
    parent = list(range(len(b)))
    def find(a):
        while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for i in range(len(b)):
        for j in range(i+1, len(b)):
            if math.dist(b[i], b[j]) < 0.20:
                x, y = find(i), find(j)
                if x != y: parent[x] = y
    roots = {}
    out = [0]*len(b)
    for i in range(len(b)):
        r = find(i)
        if r not in roots: roots[r] = len(roots)
        out[i] = roots[r]
    return out


def main():
    rows = []
    for dim, ns in [(1, 3), (2, 3)]:
        rs = [run(dim, ns, s) for s in SEEDS]
        g = [n_groups(r[0], dim) for r in rs]
        sep = [separation(r[0], dim) for r in rs]
        rows.append({"condition": ("1-D" if dim == 1 else "2-D") + f", {ns} seeded opinions",
                     "groups_mean": round(st.mean(g), 2), "groups_sd": round(st.pstdev(g), 2),
                     "sep_over_spread": round(st.mean(sep), 3),
                     "sep_over_spread_sd": round(st.pstdev(sep), 3),
                     "non_degenerate": st.pstdev(g) > 1e-3 or st.pstdev(sep) > 1e-4})

    print("  Experiment 8 -- is the two-way limit the opinion space or the rule?\n")
    print(f"  {'condition':28} {'groups':>7} {'sd':>7} {'sep/spread':>12} {'sd':>8}")
    for r in rows:
        print(f"  {r['condition']:28} {r['groups_mean']:>7.2f} {r['groups_sd']:>7.3f} "
              f"{r['sep_over_spread']:>12.3f} {r['sep_over_spread_sd']:>8.3f}")

    o, t = rows
    print(f"""
      READING IT
      -----------
      1-D with three seeded opinions: {o['groups_mean']:.2f} groups, separation/spread
      ratio {o['sep_over_spread']:.3f} (sd {o['sep_over_spread_sd']:.3f}).
      2-D with three seeded opinions: {t['groups_mean']:.2f} groups, separation/spread
      ratio {t['sep_over_spread']:.3f} (sd {t['sep_over_spread_sd']:.3f}).

      A ratio near 1.0 means the communities are a partition of a smear -- three arbitrary
      groups of a continuous distribution give the same thing. A ratio well above 1 means
      the communities are genuinely separated, and that is the difference between "three
      groups exist" and "three tissues exist".

      If the two-way ceiling in exp4 was a property of the LINE, 2-D holds three and 1-D does
      not, and the difference is a property of the opinion space rather than of the local
      rule. That would make "plurality collapses to two" a statement about scalar opinions,
      not about decentralised deference -- and it would place this outside bounded confidence,
      which is also 1-D.

      If both give the same answer, the ceiling is the RULE, the opinion space was never the
      binding constraint, and exp4 stands as I wrote it.
    """)
    json.dump(rows, open('/workspace/projects/murmuration/experiments/exp8_results.json','w'), indent=1)
    print("  -> exp8_results.json")


if __name__ == "__main__":
    main()
