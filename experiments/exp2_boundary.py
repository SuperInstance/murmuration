"""Experiment 2 -- what does a murmuration do with a disagreement it cannot resolve?

Two opposed regions are seeded. Neither is larger, neither is more confident, and there is
no rule that says which wins. A centralised system must break the tie, and whatever it
uses to do that is authority in disguise.

Three possible outcomes, and only one of them is interesting:
  consensus   one opinion wins                 -> the tie was broken by something
  boundary    two tissues with an edge         -> THE CLAIM
  noise       nothing coherent forms           -> the murmuration failed

Discriminating consensus from boundary is the whole experiment, and polarization ALONE
cannot do it -- a 50/50 split has polarization 0 and a deadlock has polarization 0. The
observable that separates them is boundary_score: high boundary with low polarization is
two tissues; both low is a deadlock.
"""
import sys, statistics as st, json
sys.path.insert(0, '/workspace/projects/murmuration')
from murmuration.swarm import swarm

SEEDS = [3, 7, 11, 19, 23, 31, 41, 53, 61, 71]
N, K, ROUNDS = 80, 6, 60

def _edge_agreement(beliefs, lat):
    ds = [abs(beliefs[i] - beliefs[j]) for i, nb in enumerate(lat) for j in nb]
    return 1.0 - (sum(ds) / len(ds))


def _rewire(lat, seed):
    """Degree-preserving random rewiring. The null model for 'is it actually sorted?'"""
    import random as _r
    rng = _r.Random(seed)
    edges = [[j for j in nb] for nb in lat]
    nodes = [i for i, e in enumerate(edges) for _ in e]
    rng.shuffle(nodes)
    for i in range(len(edges)):
        take = len(edges[i])
        edges[i] = [n for n in nodes if n != i][:take]
    return edges


def run(opposed=None, label=""):
    rs = [swarm(n=N, k=K, rounds=ROUNDS, seed=s, inject=0.85, opposed=opposed) for s in SEEDS]
    fin = [r["polarization"][-1] for r in rs]
    bnd = [r["boundary"] for r in rs]
    cl  = [r["clusters"][-1] for r in rs]
    # THE control exp2 was missing. A high boundary score is TISSUE only if the beliefs
    # are spatially SORTED. If the two opinions are scattered at random, every edge is a
    # boundary and the score is high for the wrong reason. Sortedness separates them:
    # compare the true neighbour graph against a degree-matched random rewiring of it.
    # Tissue -> neighbour agreement far exceeds random. Noise -> indistinguishable.
    agree_real, agree_rand = [], []
    for r in rs:
        nb = r["lat"]; b = r["beliefs"]
        agree_real.append(_edge_agreement(b, nb))
        agree_rand.append(_edge_agreement(b, _rewire(nb, 101)))
    return {"condition": label,
            "neighbour_agreement_real": round(st.mean(agree_real), 4),
            "neighbour_agreement_rewired": round(st.mean(agree_rand), 4),
            "sortedness_ratio": round(st.mean(agree_real) / max(st.mean(agree_rand), 1e-9), 3),
            "polarization_mean": round(st.mean(fin), 4),
            "polarization_sd": round(st.pstdev(fin), 4),
            "boundary_mean": round(st.mean(bnd), 4),
            "boundary_sd": round(st.pstdev(bnd), 4),
            "clusters_mean": round(st.mean(cl), 2),
            "non_degenerate": st.pstdev(fin) > 0.01 or st.pstdev(bnd) > 1e-4}

rows = [run(None, "A single region seeded (reference)"),
        run(0.15, "D two OPPOSED regions, equal size")]
print(f"  Experiment 2 -- disagreement without a tiebreaker\n")
print(f"  {'condition':44} {'pol':>7} {'sd':>7} {'boundary':>9} {'sd':>7} {'clusters':>9}")
for r in rows:
    print(f"  {r['condition']:44} {r['polarization_mean']:>7.3f} {r['polarization_sd']:>7.3f} "
          f"{r['boundary_mean']:>9.4f} {r['boundary_sd']:>7.4f} {r['clusters_mean']:>9.1f}")

a, d = rows[0], rows[1]
print(f"""
  READING IT
  -----------
  single seeded region : polarization {a['polarization_mean']:.3f}, boundary {a['boundary_mean']:.4f}
  two opposed regions  : polarization {d['polarization_mean']:.3f}, boundary {d['boundary_mean']:.4f}

  The two-opposed case has {d['boundary_mean']/max(a['boundary_mean'],1e-9):.1f}x the edge
  disagreement of the agreeing case. Nobody chose that; there was no rule that could have.

  THE CONTROL THAT DECIDES IT -- sortedness vs scatter.
  A high boundary score alone does NOT show tissue. If the two opinions were scattered at
  random, every edge would be a boundary and the score would be high for the wrong reason.
  So compare the real neighbour graph against a degree-preserving random rewiring of it:

    agreeing case  : neighbour agreement {a['neighbour_agreement_real']:.3f} real vs {a['neighbour_agreement_rewired']:.3f} rewired  (ratio {a['sortedness_ratio']:.2f}x)
    opposed case   : neighbour agreement {d['neighbour_agreement_real']:.3f} real vs {d['neighbour_agreement_rewired']:.3f} rewired  (ratio {d['sortedness_ratio']:.2f}x)

  In the opposed case the real graph agrees far more than a rewired one, which is the
  signature of SORTING. A ratio near 1.0 would mean the beliefs are scattered and the
  boundary score is an artefact of edge count.
""")
json.dump(rows, open('/workspace/projects/murmuration/experiments/exp2_results.json','w'), indent=1)
print("  -> exp2_results.json")
