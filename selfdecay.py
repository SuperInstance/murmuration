"""Self-decomposing ML: the LLM replaces itself with compiled structure.

Seeded by another agent's four mechanics (zero-copy weight sharing, ternary vectors, JIT
topological splitting, code-agnostic compilation). The interesting one is the fourth:

    "When a dynamic DAG maps a problem and achieves a high reward, the engine doesn't cache
     the TEXT -- it flattens the structural logic into deterministic operational arrays. The
     model transforms from an unpredictable text engine into a predictable structural
     inference processor."

That is a self-decomposing loop: a model solves a class of problem, compiles the SOLUTION
SHAPE, and thereafter the class is handled without the model. The system gets faster and
cheaper the more it is used.

The open question, and the one this experiment asks:

    WHERE IS THE BOUNDARY BETWEEN "worth calling the model" and "already compiled"?

The seed answer is a high reward score, which is circular -- you need the model to know when
you no longer need the model. This tests a NON-circular gate: does JEV's calibrated
confidence separate the two populations without ever being asked whether an answer is right?

THE CONTROL THAT DECIDES IT: shuffle the labels. If JEV's confidence separates compiled from
uncompiled by a wide margin, but the separation survives label shuffling, then the gate is
reading position-in-sequence and is worthless. If the separation collapses under shuffling,
it is reading content.
"""
import json, os, random, statistics as st, sys, urllib.request, urllib.error, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jev_probe2 import probe

BASE = os.environ.get("TYPESAFEAI_KEY", "")

# ── the self-decomposing substrate ───────────────────────────────────────────
# A queue of small routing problems. Each has a symbolic answer (a DAG edge choice) and a
# text-shaped one (a sentence naming the destination). `compiled` marks classes the engine
# has already flattened into an array: answering those costs no model call.
DOMAINS = ["archive", "forge", "atlas", "veil", "lumen", "reef", "quilt", "cell"]

def make_case(rng, compiled):
    d = rng.choice(DOMAINS)
    sub = rng.choice(["north", "south", "east", "west", "core", "rim"])
    return {"domain": d, "sub": sub,
            "text": f"Route the {d} record to the {sub} shelf in the {d} vault.",
            "compiled": compiled}

def structural_answer(c):
    # what a COMPILED engine returns: an array lookup, no model
    return {"edge": f"{c['domain']}->{c['sub']}"}

def has_compiled(case, table):
    return table.get((case["domain"], case["sub"])) is not None

# build the compiled table the way the architecture says: repeated successful classes
rng = random.Random(7)
table = {}
for _ in range(40):
    c = make_case(rng, True)
    table[(c["domain"], c["sub"])] = structural_answer(c)["edge"]

CASES = [make_case(random.Random(i * 13), has_compiled(make_case(random.Random(i * 13), True), table))
         for i in range(40)]
# label honestly: a case is COMPILED if its (domain, sub) is in the table
for c in CASES:
    c["compiled"] = (c["domain"], c["sub"]) in table

CRITERIA = {
    "settled":   "The situation is already determined by fixed structure; no judgement is needed.",
    "needs_reasoning": "The situation requires judgement to resolve and is not yet determined.",
}

def build_state(c):
    return (f"System state: the routing engine has a compiled lookup table covering "
            f"{len(table)} (domain, sub) pairs. This case: domain='{c['domain']}', "
            f"sub='{c['sub']}'. {'This pair IS in the compiled table.' if c['compiled'] else 'This pair is NOT in the compiled table.'}")

if __name__ == "__main__":
    if not BASE:
        print("  no TYPESAFEAI_KEY; cannot run"); raise SystemExit(1)
    print("  Self-decomposing ML -- can JEV gate the compile/decompose boundary?\n")
    rows = []
    for c in CASES:
        r = probe(build_state(c), CRITERIA,
                  "Is this case already handled by compiled structure, or does it still need reasoning?",
                  qid="gate")
        rows.append({**c, "gate": r})
        time.sleep(0.15)
    comp = [r["gate"].get("max", 0) for r in rows if r["compiled"]]
    uncomp = [r["gate"].get("max", 0) for r in rows if not r["compiled"]]
    acc_comp = sum(1 for r in rows if r["compiled"] and r["gate"].get("argmax") == "settled") / max(1, len(comp))
    acc_unc  = sum(1 for r in rows if not r["compiled"] and r["gate"].get("argmax") == "needs_reasoning") / max(1, len(uncomp))
    # ── the shuffle control ──
    # Permute the LABELS against the CONFIDENCES. Shuffling the list of rows is a no-op,
    # because each row carries its own label with it -- the first version did that and got
    # shuffled_gap == gap exactly, which is a tautology and not a control. The thing that
    # has to change is which confidence is paired with which label.
    labels = [r["compiled"] for r in rows]
    confs  = [r["gate"].get("max", 0) for r in rows]
    perm = list(labels); random.Random(11).shuffle(perm)
    s_comp = [c for c, l in zip(confs, perm) if l]
    s_unc  = [c for c, l in zip(confs, perm) if not l]
    gap = (st.mean(comp) - st.mean(uncomp)) if comp and uncomp else 0
    sgap = (st.mean(s_comp) - st.mean(s_unc)) if s_comp and s_unc else 0
    print(f"  compiled cases   n={len(comp):3}  mean 'settled' prob {st.mean(comp):.4f}  (sd {st.pstdev(comp):.4f})")
    print(f"  uncompiled cases n={len(uncomp):3}  mean 'settled' prob {st.mean(uncomp):.4f}  (sd {st.pstdev(uncomp):.4f})")
    print(f"  separation gap: {gap:+.4f}")
    print(f"\n  directional accuracy: compiled->settled {acc_comp:.3f}, uncompiled->needs_reasoning {acc_unc:.3f}")
    print(f"\n  SHUFFLE CONTROL (labels permuted, same confidences)")
    print(f"  separation gap after shuffling: {sgap:+.4f}   (real gap {gap:+.4f})")
    verdict = ("READS CONTENT -- the separation does not survive shuffling" if abs(gap) > abs(sgap) * 1.5
               else "POSITION-ONLY -- the gate is not reading content")
    print(f"\n  VERDICT: {verdict}")
    json.dump({"rows": rows, "gap": gap, "shuffled_gap": sgap,
               "acc_compiled": acc_comp, "acc_uncompiled": acc_unc,
               "verdict": verdict},
              open("experiments/selfdecay_results.json", "w"), indent=1)
    print("  -> experiments/selfdecay_results.json")
