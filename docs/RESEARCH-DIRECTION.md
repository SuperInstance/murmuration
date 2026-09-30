# The murmuration: collective intelligence without a central authority

## The observation this is built on

Gradient descent through a layered network is a **centralised control scheme wearing the
costume of a local rule.** One scalar loss is computed at the top, and it reaches every
parameter in the network. Each unit's update depends on a global quantity. The word
"neuron" makes it sound like a cell; the information flow makes it a broadcast.

A starling murmuration is the opposite. No bird is in charge. Each tracks roughly seven
neighbours. Every rule is local and identical everywhere. The structure — the shape of the
flock, the shear lines, the density waves — is real, and *nobody chose it.*

Those are the two shapes. This asks whether anything interesting lives in the second one,
and it takes "nothing" seriously: the cells here have no global state, no global loss, no
orchestrator, and no way to see more than `k` neighbours.

## What was built

- `murmuration/cell.py` — a first-person cell. It reads its inputs, forms a local belief,
  records a local witness, and nothing else. The information barrier is **structural**: the
  kernel passes it at most `k` payloads, so "global knowledge" is not a rule someone might
  break, it is a thing the cell has no access to.
- `murmuration/swarm.py` — the kernel. Cells drift toward the beliefs they agree with and
  away from those they do not. A `k`-nearest-neighbour lattice is rewired every round, so
  neighbourhoods are consequences of the current geometry rather than a frozen choice.
- `experiments/exp1_propagation.py` — can a local opinion become a global one?
- `experiments/exp2_boundary.py` — what happens to a disagreement with no tiebreaker?
- `jev_probe.py` / `jev_control.py` — JEV, and whether JEV can be trusted to say anything.

## The two mechanisms that were wrong first

Both were found by controls, not by reading the code, and both are the kind of thing that
produces a number that looks like a result.

**Averaging has a fixed point at the prior.** The first kernel pulled every cell toward the
local mean. The local mean was 0.5. So a symmetric swarm converges to *undecided* and stays
there: polarization pinned at **0.008** for 60 rounds, stdev 0.0014. A decentralised system
that averages its way to "no opinion" is not wrong in an interesting way, it is simply
dead. Replaced with **deference to confidence** — a cell adopts when a peer is markedly
more confident than it is.

**Similarity gating cannot carry a belief anywhere.** Gating adoption on "is a neighbour
near my belief" blocks transmission outright. A seed at 0.85 and its neighbours at 0.5
differ by 0.35, a 0.12 threshold is never satisfied, and the opinion cannot cross the gap.
Polarization froze at exactly **0.035** — the seeds, and nobody else — with stdev **0.0000**.
A frozen number is not a weak result. It is a dead one.

## Result 1 — local seeding propagates, and the no-seed control holds

n=80, k=6, 60 rounds, 10 seeds.

| condition | final polarization | sd across seeds | communities |
|---|---|---|---|
| **A** local seed, 5% of cells, one region | **0.550** | 0.103 | **41.4** |
| **B** broadcast to every cell (authority) | 0.700 | **0.000** | 50.6 |
| **C** no seed at all (control) | 0.000 | 0.000 | 50.6 |

C is the one that makes A and B mean something. Without an injection, polarization is
**exactly zero** — so a rising polarization reflects the injected opinion propagating, not
a swarm that cohered on its own.

**B is the interesting row.** Authority reaches higher consensus (0.700 vs 0.550) and gets
*bit-identical results on all ten seeds* — sd 0.000. And it produces **50.6 communities,
i.e. no structure at all**, against A's 41.4. The central system is stronger, perfectly
repeatable, and structurally empty. The murmuration is weaker, variable, and organised.

That is a real trade-off and not an artefact: it is what the difference between "everyone
is told" and "everyone finds out" looks like when you measure the structure that is left
behind.

## Result 2 — a disagreement with no tiebreaker becomes a boundary, not a resolution

Two opposed regions, equal size, equal confidence. There is no rule that says which wins,
and no mechanism available to break the tie.

| | polarization | boundary | sd(seeds) |
|---|---|---|---|
| single seeded region | 0.550 | 0.0060 | 0.103 |
| **two opposed regions** | **0.195** | **0.0934** | 0.177 |

Polarization **collapses** and boundary disagreement rises **15.6x**. The swarm did not
resolve the disagreement. It *partitioned*.

**The control that decides it.** A high boundary score proves nothing on its own: if the
two opinions were scattered at random, every edge would be a boundary and the score would
be high for the wrong reason. So the real neighbour graph is compared against a
**degree-preserving random rewiring** of itself:

```
agreeing case : neighbour agreement 0.994 real  vs 0.901 rewired   (1.10x)
opposed case  : neighbour agreement 0.907 real  vs 0.726 rewired   (1.25x)
```

The real graph agrees substantially more than a rewired one. That ratio is the signature
of **sorting**: the beliefs organised in space. Had it come out near 1.0, the high boundary
would have been an artefact of edge count and the finding would have been reported as a
null.

Two tissues, and an edge between them, out of local deference applied identically to every
cell. Nobody chose it, because there was no rule that could have.

## Result 3 — the JEV probes are a NULL, and here is the control that says so

Four claims were submitted to JEV in `choice` mode. All four returned `unclear` at
0.75–0.79, with **0.000 probability on both `strong` and `contradicts`**, and near-identical
distributions across four very different claims. That uniformity is suspicious, so the
probe was tested on claims that cannot both be true:

```
control_positive_arithmetic    "two plus two equals four"   -> unclear 0.74
control_negative_arithmetic    "two plus two equals five"    -> unclear 0.79
control_negative_selfevident   "water is dry"               -> unclear 0.73
```

**The probe does not discriminate.** It returns the same answer to a true statement, a
false one, and an absurd one. In this configuration the `unclear` at ~0.76 is the
instrument's constant, not a property of the murmuration.

**Consequence, stated plainly: the four JEV probes carry zero information.** They are
recorded as a null result. They are not cited as corroboration for anything, and no claim
in this document is promoted on their basis. A probe that cannot tell 2+2=4 from 2+2=5
has no opinion about cells.

The likely cause is the `criteria` mapping — JEV is probably being asked to match the
claim against five *option descriptions* rather than five *verdicts*, and `unclear` is the
hedge when none of them fit. That is a fixable bug, not a reason to keep quoting the
number. **The control is reusable:** `jev_control.py` should be run before any future JEV
battery, because a probe that always answers `unclear` looks exactly like a probe that is
carefully declining.

## The degenerate-measurement rule, applied throughout

Every claim here is a relational claim — "polarization rose", "boundary exceeded X", "the
real graph agrees more than the rewired one" — over a measured signal. Per the rule, any
of them measured over a degenerate signal (std == 0) is **vacuous and reported INCONCLUSIVE,
never PASSED.** Two of the four conditions in this document *were* degenerate before the
controls were run (stdev 0.0014 and 0.0000), and both were caught that way rather than
reported as weak positive results. The no-seed control (C) exists so that a rising number
cannot be mistaken for a swarm that is simply agreeable.

## What this suggests, and what it does not

**Suggests:** structure is a property of the interaction graph, not of the message. The
same opinion delivered by broadcast and by propagation produced a swarm and an empty plane
respectively. If that holds, "collective intelligence" and "organisation into tissues" may
be the same phenomenon viewed at two scales, and the k in the neighbourhood is the lever
that moves between them.

**Does not suggest:** that this is better. Central broadcast scored *higher* on consensus.
What it got was a number. What the murmuration got was 41 communities and a boundary — and
which of those is more valuable is not a question this experiment answers, because the
experiment has no metric for value.

**Open and untested:** whether the boundary is stable under perturbation, whether a
third opinion is absorbed or spawns a third tissue, and whether an organ-scale structure
emerges if `k` is raised. None of that has been run. It is the obvious next round.
