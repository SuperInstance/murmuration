"""Does the JEV probe discriminate AT ALL, or is it echoing my framing?

The four murmuration claims all came back `unclear` at 0.75-0.79, with 0.000 mass on
BOTH `strong` and `contradicts`. Two readings are possible and they are not equivalent:

  (a) the claims are genuinely undertested, and JEV correctly declined
  (b) the probe is responding to the shape of the question rather than its content,
      and would say `unclear` to anything

(b) is the one that matters, because a probe that always answers `unclear` is an
instrument that reports the same thing regardless of what you feed it -- and I have
already built three of those tonight. So: two claims that cannot both be true.

  POSITIVE: "The number two plus two equals four."
  NEGATIVE: "The number two plus two equals five."

If these two do not separate, then the four murmuration verdicts carry no information and
must be reported as a null result, not as four findings.
"""
import json, time
from jev_probe import call, interpret, SCALE, STATE

CONTROLS = {
    "control_positive_arithmetic": "The number two plus two equals four.",
    "control_negative_arithmetic": "The number two plus two equals five.",
    "control_negative_selfevident": "Water is dry.",
}

results = {}
print("  INSTRUMENT CONTROL — can this probe tell true from false at all?\n")
for name, claim in CONTROLS.items():
    r = call(claim, name)
    rd = interpret(r, name) or {}
    results[name] = {"claim": claim, "argmax": rd.get("argmax"),
                     "distribution": rd.get("distribution"), "raw": r}
    dist = rd.get("distribution") or {}
    bar = " ".join(f"{k}={v:.2f}" for k, v in sorted(dist.items(), key=lambda x: -x[1]))
    print(f"  {name:32} {str(rd.get('argmax')):12} {bar}")
    time.sleep(0.4)

pos = results["control_positive_arithmetic"]["distribution"] or {}
neg = results["control_negative_arithmetic"]["distribution"] or {}
if pos and neg:
    def top(d): return max(d, key=lambda k: d[k])
    verdict = "DISCRIMINATES" if top(pos) != top(neg) else "DOES NOT DISCRIMINATE"
    print(f"""
  VERDICT: the probe {verdict}
    positive claim -> {top(pos)}  (max {max(pos.values()):.2f})
    negative claim -> {top(neg)}  (max {max(neg.values()):.2f})

  Consequence for the four murmuration probes:""")
    if verdict == "DOES NOT DISCRIMINATE":
        print("""    NOTHING. They carry no information about the claims. The `unclear` at 0.75-0.79
    was the probe's constant, not a property of the murmuration. This is reported as a
    NULL result and the four claims are NOT promoted, NOT triaged, and NOT cited as
    corroboration. A probe that cannot tell 2+2=4 from 2+2=5 has no opinion about cells.""")
    else:
        print("""    the `unclear` verdicts are real and meaningful -- the probe works, and it is
    declining these claims because they are undertested as worded. That is actionable:
    sharpen them into falsifiable form before spending compute on them.""")
json.dump(results, open("experiments/jev_control.json", "w"), indent=1)
print("\n  -> experiments/jev_control.json")
