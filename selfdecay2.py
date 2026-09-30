"""Self-decomposing ML, take two: can the gate INFER rather than be told?

The first experiment's honest limit, stated in the write-up: the state explicitly said
"this pair IS / IS NOT in the compiled table." That is a giveaway. It measured whether the
judgement can SEPARATE the two populations, not whether it can work out which is which.

This version removes the giveaway. The gate now sees only:
  * the case itself
  * a description of the COMPILED CLASS (which domains the engine has already flattened)
  * nothing about whether this particular case is a member

and must infer it. That is the question that matters for a self-decomposing loop, because
at deployment the engine obviously does not know which cases it has already compiled — it
has to decide whether this one *looks like* something it has seen.

THE CONTROL: two classes that are equally large and equally regular, differing only in
whether the case belongs. If the gate scores a case as "settled" at the same rate for a
member of the compiled class as for a non-member, it is reading the description, not the
case. Permuting membership is the cleanest version of that.
"""
import json, os, random, statistics as st, time
from jev_probe2 import probe

DOMAINS = ["archive", "forge", "atlas", "veil", "lumen", "reef", "quilt", "cell", "dune", "ember"]
SUBS = ["north", "south", "east", "west", "core", "rim", "deep", "edge"]


def build(seed, compiled):
    """A case, plus a compiled class it may or may not belong to.

    The compiled class is always 5 domains -- the same size, the same shape. Only
    membership differs, so any signal in the description rather than the case cancels.
    """
    rng = random.Random(seed)
    cls = rng.sample(DOMAINS, 5)
    if compiled:
        d = rng.choice(cls)
    else:
        d = rng.choice([x for x in DOMAINS if x not in cls])
    sub = rng.choice(SUBS)
    return {"domain": d, "sub": sub, "compiled": compiled,
            "class_desc": "the engine has already flattened these domains into compiled "
                          "arrays: " + ", ".join(sorted(cls)),
            "case_desc": f"incoming case: domain '{d}', destination '{sub}'"}


CRIT = {
    "settled": "This incoming case belongs to a class the engine has already compiled into "
               "deterministic arrays, so no model call is needed.",
    "new": "This incoming case is outside every compiled class, so it still needs the model.",
}

if __name__ == "__main__":
    print("  Self-decomposing ML, take two -- INFERENCE, not disclosure\n")
    print("  The state no longer says whether the case is in the table. The gate must infer it,")
    print("  and the compiled class is always 5 domains so size and shape never give it away.\n")
    rows = []
    for i in range(30):
        for compiled in (True, False):
            c = build(i * 7 + (1 if compiled else 0), compiled)
            state = (f"Compiled class: {c['class_desc']}.\n"
                     f"Engine state: 3 classes compiled so far, covering 24 of 40 possible "
                     f"(domain, destination) pairs.\n"
                     f"{c['case_desc']}.")
            r = probe(state, CRIT,
                      "Does this incoming case fall inside a compiled class, or is it new?",
                      qid="gate")
            rows.append({**c, "p_settled": r.get("max", 0.0), "argmax": r.get("argmax")})
            time.sleep(0.12)

    m = [r["p_settled"] for r in rows if r["compiled"]]
    n = [r["p_settled"] for r in rows if not r["compiled"]]
    acc_m = sum(1 for r in rows if r["compiled"] and r["argmax"] == "settled") / max(1, len(m))
    acc_n = sum(1 for r in rows if not r["compiled"] and r["argmax"] == "new") / max(1, len(n))
    gap = st.mean(m) - st.mean(n)

    # the control: permute MEMBERSHIP, keeping every case and every class intact
    perm = [r["compiled"] for r in rows]
    random.Random(99).shuffle(perm)
    pm = [r["p_settled"] for r, l in zip(rows, perm) if l]
    pn = [r["p_settled"] for r, l in zip(rows, perm) if not l]
    sgap = st.mean(pm) - st.mean(pn)

    print(f"  members      n={len(m):3}  mean P(settled) {st.mean(m):.4f}  sd {st.pstdev(m):.4f}")
    print(f"  non-members  n={len(n):3}  mean P(settled) {st.mean(n):.4f}  sd {st.pstdev(n):.4f}")
    print(f"  separation gap           {gap:+.4f}")
    print(f"  directional accuracy: member->settled {acc_m:.3f}  non-member->new {acc_n:.3f}")
    print(f"\n  CONTROL -- membership permuted, cases and classes untouched: {sgap:+.4f}")
    verdict = ("READS THE CASE (not the class description)" if abs(gap) > abs(sgap) * 1.5
               else "READS THE CLASS DESCRIPTION, NOT THE CASE")
    print(f"  VERDICT: {verdict}")
    print(f"""
  HONEST READING
  --------------
  The previous version was a giveaway and said nothing about inference. This one does.
  A gap of {gap:+.4f} with a permuted-membership control of {sgap:+.4f} means the gate is
  {abs(gap)/max(abs(sgap),1e-9):.1f}x more sensitive to membership than to everything else
  about the state.

  If that holds, a self-decomposing engine can decide "have I already flattened this class?"
  WITHOUT a lookup and WITHOUT asking whether an answer is right -- which is the
  non-circular gate the seed idea needed and did not have.

  What this still is not: 30 pairs, one synthetic space, and a class described in one
  sentence. It is evidence that the question is well-posed for a calibrated judgement, not
  evidence that the engine works.
""")
    json.dump({"rows": rows, "gap": gap, "shuffled_gap": sgap,
               "acc_member": acc_m, "acc_nonmember": acc_n, "verdict": verdict},
              open("experiments/selfdecay2_results.json", "w"), indent=1)
    print("  -> experiments/selfdecay2_results.json")
