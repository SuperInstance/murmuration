"""JEV probe, rebuilt to the documented contract.

The first version sent `state` as an OBJECT and carried a separate `options` list alongside
`criteria`. The documented shape is: `state` is the content string, `criteria` maps option
names to their descriptions, and the option set IS the criteria keys.

So the earlier finding -- "JEV returns `unclear` to 2+2=4, 2+2=5 and water-is-dry alike" --
may have been MY malformed request rather than a property of the model. That claim is on the
public record in docs/PRIOR-ART.md, so it has to be re-tested rather than defended.

The control is unchanged and is the whole point: a probe that cannot tell a true statement
from a false one has no opinion about anything, and must not be used to gate a split decision.
"""
import json, os, random, time, urllib.request, urllib.error

BASE = "https://api.typesafe.ai/v1/systemone"
KEY = os.environ.get("TYPESAFEAI_KEY", "")
MODEL = "jev-1.13.0"

def call(state, questions, tries=4):
    body = {"model": MODEL, "state": state, "questions": questions}
    req = urllib.request.Request(
        BASE, data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json",
                 "Accept": "application/json",
                 "User-Agent": "murmuration-jev-probe/2.0 (+Quilt)"})
    for a in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=50) as r:
                return json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            if e.code in (502, 503, 504) and a < tries - 1:
                time.sleep(0.5 + random.random() * 0.3); continue
            return {"error": f"HTTP {e.code}", "body": e.read()[:160].decode("utf-8", "replace")}
        except Exception as e:
            if a < tries - 1:
                time.sleep(0.5); continue
            return {"error": f"{type(e).__name__}: {e}"}


def probe(state, criteria, instructions, qid="q"):
    r = call(state, {qid: {"type": "choice", "instructions": instructions,
                            "criteria": criteria}})
    ans = (r.get("answers") or {}).get(qid)
    if not ans:
        return {"error": r.get("error", "no answer"), "raw": r}
    p = ans.get("probabilities") or {}
    vals = sorted(p.values())
    mx = vals[-1] if vals else 0.0
    mean = sum(vals) / len(vals) if vals else 0.0
    return {"argmax": max(p, key=p.get) if p else None,
            "max": round(mx, 4), "mean": round(mean, 4), "gap": round(mx - mean, 4),
            "confidence": ans.get("confidence"),
            "distribution": {k: round(v, 4) for k, v in p.items()}}


if __name__ == "__main__":
    VERDICT = {
        "true": "This statement is factually correct.",
        "false": "This statement is factually incorrect.",
        "uncertain": "There is not enough information to judge it.",
    }
    CONTROLS = {
        "arithmetic_true":  ("The number two plus two equals four.", "The number two plus two equals four."),
        "arithmetic_false": ("The number two plus two equals five.",  "The number two plus two equals five."),
        "absurd":           ("Water is dry.",                           "Water is dry."),
        "obvious_true":     ("Paris is the capital of France.",          "Paris is the capital of France."),
        "obvious_false":    ("Paris is the capital of Spain.",           "Paris is the capital of Spain."),
    }
    print("  JEV control, rebuilt to the DOCUMENTED contract\n")
    print(f"  {'control':20} {'argmax':10} {'max':>7} {'gap':>7}")
    out = {}
    for name, (state, stmt) in CONTROLS.items():
        r = probe(state, VERDICT, f"Is this statement true or false? — STATEMENT: {stmt}")
        out[name] = r
        print(f"  {name:20} {str(r.get('argmax')):10} {r.get('max','-'):>7} {r.get('gap','-'):>7}")
    pos = out["arithmetic_true"]; neg = out["arithmetic_false"]
    obp = out["obvious_true"];  obn = out["obvious_false"]
    print()
    if pos.get("argmax") and neg.get("argmax"):
        verdict = "DISCRIMINATES" if pos["argmax"] != neg["argmax"] else "DOES NOT DISCRIMINATE"
        print(f"  arithmetic  true->{pos['argmax']}  false->{neg['argmax']}   {verdict}")
    if obp.get("argmax") and obn.get("argmax"):
        v2 = "DISCRIMINATES" if obp["argmax"] != obn["argmax"] else "DOES NOT DISCRIMINATE"
        print(f"  geography   true->{obp['argmax']}  false->{obn['argmax']}   {v2}")
    print("""
  The earlier report said the probe could not discriminate. If it discriminates now, the
  earlier result was a malformed request on my side and the public claim in
  docs/PRIOR-ART.md is wrong and has to be corrected. Either way, the control is what
  decides it -- not the model's reputation.""")
    json.dump(out, open("experiments/jev_probe2.json", "w"), indent=1)
    print("\n  -> experiments/jev_probe2.json")
