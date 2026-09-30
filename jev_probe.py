"""JEV as a RELEVANCE PROBE. Explicitly not an oracle.

Correctness constraints, all of them earned by getting it wrong first:

  * endpoint is POST /v1/systemone with `model`, top-level `state`, and `questions`
  * a choice spec is {"type":"choice", "criteria": {label: description}, "options":[labels]}
    -- criteria maps the OPTION LABEL to its description; a criteria dict keyed "text"
       makes JEV treat "text" as the only option label
  * Cloudflare 1010 rejects urllib's default User-Agent; send a real one
  * Authorization: Bearer is required, or every call is 403
  * transient 503 from the DNS cache overflow; retry with backoff
  * `score` mode is a near-constant generator and is NOT used for gating here

What this file is FOR: triaging which emergent claims deserve compute next. It cannot
tell me whether the murmuration forms tissues. Only the experiment can, by measuring.
If JEV and the experiment disagree, the experiment is right and JEV was measuring
relevance rather than truth.
"""
import json, os, random, time, urllib.request, urllib.error

BASE = "https://api.typesafe.ai/v1/systemone"
KEY = os.environ.get("TYPESAFEAI_KEY", "")

STATE = {
    "context": "A cellular-architecture research programme. Cells are first-person "
               "perspectives that read only their k nearest neighbours and update by "
               "local deference. No central loss, no orchestrator, no global vote.",
    "measured_so_far": "Experiment 1 (10 seeds, n=80, k=6): local seeding reaches "
                       "polarization 0.55 with real structure; central broadcast reaches "
                       "0.70 with zero variance and no structure; no-seed control reaches "
                       "0.00. Experiment 2: two opposed regions form a boundary "
                       "(15.6x edge disagreement) with polarization falling to 0.195, and "
                       "neighbour agreement 1.25x higher than a degree-matched rewiring.",
    "caution": "These are the results of one small simulation. The claims below are "
               "interpretations of them, and are being probed for RELEVANCE, not truth.",
}

SCALE = {
    "contradicts": "The claim is wrong: the system does not behave this way.",
    "unsupported": "The claim is not supported by the evidence given; too weak or unfalsifiable.",
    "unclear": "The claim is ambiguous or not yet testable with what is described.",
    "supported": "The claim follows from the evidence given, within its stated limits.",
    "strong":    "The claim follows necessarily and is the best current explanation.",
}

CLAIMS = {
  "murmuration_forms_tissues":
    "A swarm in which each cell reads only its k nearest neighbours and updates by "
    "deference to local confidence will sort into spatial communities with a sharp "
    "boundary between opposed opinions, with no central authority anywhere in the loop.",
  "central_authority_destroys_structure":
    "Broadcasting one opinion to every cell at once reaches higher consensus but yields "
    "fewer communities than local propagation, because structure comes from the "
    "interaction graph rather than from the message.",
  "backprop_is_a_central_authority":
    "Gradient descent through a layered network is a centralised control scheme: a single "
    "scalar loss reaches every parameter, which is the same shape as a broadcast rather "
    "than the same shape as a murmuration.",
  "boundary_beats_forced_consensus":
    "When a decentralised system holds two equally-supported opposing views, a persistent "
    "boundary is more informative than a forced resolution, because the boundary marks "
    "where the evidence actually runs out.",
}


def call(spec, qid, tries=4):
    body = {"model": "jev-latest", "state": STATE,
            "questions": {qid: {"type": "choice", "criteria": SCALE,
                                 "options": list(SCALE)}}}
    req = urllib.request.Request(
        BASE, data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json",
                 "Accept": "application/json",
                 "User-Agent": "murmuration-jev-probe/1.0 (+Quilt)"})
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


def interpret(resp, qid):
    """Read the FULL DISTRIBUTION, not the argmax.

    A confident argmax over a nearly flat distribution means the probe is not
    discriminating, and reporting only the argmax would hide exactly that.
    """
    ans = (resp.get("answers") or {}).get(qid)   # the ACTUAL qid, not the first one
    if not ans:
        return None
    probs = ans.get("probabilities") or ans.get("legend") or {}
    if not isinstance(probs, dict) or not probs:
        return {"raw_answer": str(ans)[:200]}
    vals = sorted(float(v) for v in probs.values())
    mx, mean = vals[-1], sum(vals) / len(vals)
    best = max(probs, key=lambda k: probs[k])
    return {"argmax": best, "max": round(mx, 4), "mean": round(mean, 4),
            "gap": round(mx - mean, 4),
            "discriminating": (mx - mean) > 0.05,
            "distribution": {k: round(float(v), 4) for k, v in probs.items()}}


if __name__ == "__main__":
    out = {}
    for i, (name, claim) in enumerate(CLAIMS.items()):
        qid = list(CLAIMS)[i]
        r = call(CLAIMS[name], qid)
        r.pop("usage", None)
        out[name] = {"claim": claim, "result": r, "read": interpret(r, qid)}
        rd = out[name]["read"] or {}
        print(f"  {name:38} {rd.get('argmax','?'):12} max={rd.get('max','?')} "
              f"gap={rd.get('gap','?')} {'DISCRIMINATES' if rd.get('discriminating') else 'FLAT'}")
        time.sleep(0.4)
    json.dump(out, open("experiments/jev_probe.json", "w"), indent=1)
    print("\n  -> experiments/jev_probe.json")
    print("  Read as relevance triage. Not a verdict on the physics.")
