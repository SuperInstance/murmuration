# Iterations — what survived, what did not, and what the controls cost

Six experiments, run in order. Several of them took away something I had previously
written down. That is the point of running them.

| # | question | verdict |
|---|---|---|
| 1 | can a local opinion become a global one? | **yes** — 0.550, with a no-seed control at exactly 0.000 |
| 2 | what happens to an unresolvable disagreement? | it **partitions** — boundary 15.6x, sorted 1.25x |
| 3 | is that boundary a real structure? | **NO — refuted.** It dissolves and does not reform |
| 4 | can it hold a third opinion? | **no** — collapses to two, though confidence does matter |
| 5 | does structure peak at an intermediate k? | **yes** — boundary peaks at k=16, sorting at k=4 |
| 6 | does it learn anything? | **it estimates** — and the control shows it is just the mean |

## Exp 1 — propagation holds, and the control makes it mean something

Local seed → polarization 0.550, 41.4 communities. **Broadcast → 0.700 with sd 0.000
across all ten seeds and 50.6 communities, i.e. no structure at all.** No-seed → exactly
0.000.

Two mechanisms were wrong before this worked, and both were caught by a control rather
than by reading code:

- **Averaging has a fixed point at the prior.** Local averaging converged to *undecided*:
  polarization 0.008, stdev 0.0014.
- **Similarity gating cannot carry a belief.** A 0.12 threshold between a seed at 0.85 and
  neighbours at 0.5 was never satisfied. Polarization froze at 0.035, stdev 0.0000. A
  frozen number is not a weak result, it is a dead one.

## Exp 2 — a disagreement becomes a boundary (and I overcalled it)

Two opposed regions: polarization collapses 0.550 → 0.195, boundary disagreement rises
**15.6x**, and a degree-preserving rewiring gives neighbour agreement 0.907 vs 0.726
(**1.25x**) — the signature of sorting rather than scattering.

I called this a tissue. **Exp 3 took that back.**

## Exp 3 — the boundary does not survive being shoved. REFUTED.

| condition | boundary | sortedness |
|---|---|---|
| no perturbation | 0.0934 | 1.264 |
| 20% positional kick | 0.0417 | 1.270 |
| 5% opinion flip | 0.0516 | 1.270 |
| full scramble | 0.0417 | 1.230 |
| **60% kick + 180 rounds annealing** | **0.0038** | 1.237 |

The last row is the finding: after a large shove and three times the rounds, the swarm
heals into **unanimity** (neighbour agreement 0.996), not back into two tissues. The
boundary is a **transient** — a configuration the system tolerates but does not defend.
A tissue that cannot reform after damage is not a tissue yet. Exp 2's 15.6x is a property
of a fresh unperturbed two-view configuration, not of a robust structure.

**And the instrument failed too.** Sortedness barely moves: 1.264 control, 1.270 kicked,
1.230 fully scrambled. I chose it because a uniform colouring could not fake it — and it
cannot — but the system sorts under *every* condition tested, including ones designed to
destroy the thing being sorted. It is a real property and a useless discriminator. **A
near-constant metric supporting a stability claim is a vacuous claim.**

A third failure, mine: the first version of this experiment returned byte-identical
numbers for four different perturbations. The boundary was computed inside `swarm()`
before anything was perturbed, so I was measuring a stale value four times and calling the
result stability.

## Exp 4 — plurality collapses to two

| condition | groups | mid-opinion fraction |
|---|---|---|
| two regions (control) | 2.30 | — |
| third opinion, LOW confidence | 1.80 | 0.030 |
| third opinion, HIGH confidence | 2.00 | 0.063 |

Confidence gating **works** — a confident third view survives about twice as well. But the
system still collapses to two, and a third opinion at 0.85 is absorbed by the existing
0.85 tissue.

**T3 was a broken condition and I am not counting it.** I seeded the "third" opinion at
0.85, which is the same value as the first region, so it merged by construction. That is
my design error, not a finding about the system. The system as built lives on a 1-D
spectrum and is a partition into at most two; a genuine three-way plurality was not
tested.

## Exp 5 — structure peaks at an intermediate k, and the two scales differ

| k | polarization | boundary | sortedness | communities |
|---|---|---|---|---|
| 1 | 0.026 | 0.0052 | 1.129 | 54.9 |
| 4 | 0.196 | 0.0655 | **1.295** | 37.4 |
| 6 | 0.324 | 0.0756 | 1.216 | 34.2 |
| **16** | 0.356 | **0.1286** | 1.099 | 25.5 |
| 24 | 0.393 | 0.1063 | 1.045 | 20.0 |
| 40 | 0.452 | 0.1075 | 1.061 | 16.1 |

**Boundary peaks at k=16 and falls away at both ends** — an interior maximum, not a
smoothing curve. **Sortedness peaks much earlier, at k=4, and then collapses to 1.045.**
So spatial sorting and tissue contrast are *different scales*: the swarm is most
sorted at a small k, and most sharply divided at a larger one. Communities fall
monotonically 54.9 → 16.1, so high k genuinely produces large connected masses.

The k=16 regime is the one worth calling organ-scale: enough neighbours to divide, few
enough to stay independent. Note the honest limit — exp 3 showed the resulting structure
does not defend itself, so "organ" here describes a *shape*, not a robust organ.

## Exp 6 — it estimates, and the control shows it is just the mean

| theta | murmuration MAE | global MAE | alone MAE |
|---|---|---|---|
| 0.25 | 0.0332 | 0.0345 | 0.1755 |
| 0.50 | 0.0425 | 0.0250 | 0.1930 |
| 0.75 | 0.0345 | 0.0227 | 0.1807 |

Estimates **0.265 / 0.519 / 0.767** — they move with the latent value, so this is
estimation and not drifting to the midpoint. **5.3x better than a cell working alone.**

**Then the scramble control took back the interesting version.** The same multiset of
samples, handed out in rotated order: murmuration 0.0332 → **0.0344** (3%, within noise),
global 0.0345 → **0.0345** (unchanged, as it must be). If local sample-to-cell structure
contributed anything, scrambling it would have hurt the murmuration and left the mean
untouched. Neither happened.

- **REFUTED:** local structure adds information a global mean cannot reach.
- **SURVIVING:** a swarm with no global state, reading k neighbours at a time, recovers a
  latent parameter as accurately as the global average — MAE 0.0332 vs 0.0345, against a
  no-cooperation floor of 0.1755.

**Equivalence without a central state.** That is a real and non-trivial result, and it is
not superiority: the centralised estimator is marginally tighter on this task. The
cooperation is doing real work — 5x over a lone cell — but that work is *distributive*,
not *information-adding*.

The first version of this control was also broken and is worth recording: it set every
sample to exactly 0.5 with no noise, so MAE came back 0.0000 and proved nothing. A
control that cannot fail is not a control.

## What is left standing

1. Local opinion propagates to global consensus with no authority, and the no-seed control
   is exactly zero.
2. A central broadcast of the same opinion scores **higher**, is **bit-identical across
   seeds**, and leaves **no structure**. Authority is stronger and empty.
3. Unresolvable disagreement **partitions** rather than resolving, and the opinions
   **sort** rather than scatter (1.25x against a degree-matched rewiring).
4. Structure peaks at an intermediate k, and sorting and division peak at **different** k.
5. A decentralised swarm recovers a latent parameter **as well as the global mean** using
   only local contact.

**Refuted along the way:** the tissue is self-maintaining (exp 3), local structure adds
information a mean cannot reach (exp 6), and the swarm can hold three opinions (exp 4).

**Still untested:** whether the k=16 structure survives anything at all, whether the
third-opinion result holds with a genuine third value, and whether any of this survives
contact with a task that has non-stationarity.

---

## exp7–exp10: the round that removed most of the claims above

| # | question | verdict |
|---|---|---|
| 7 | is the *barrier* what matters, or voice diversity? | **barrier is decoration** — refutes result 1's framing |
| 8 | is the two-way limit the opinion space or the rule? | **neither** — and the experiment was buggy |
| 9 | do the 2-D tissues defend themselves? | **yes** — they recover, and sharpen under abuse |
| 10 | ordering or mutual non-adjacency? | **inconclusive**, but it found the exp8 bug |

**exp7 refutes result 1 as stated.** exp1's "local beats broadcast on structure" changed two
things at once: the information topology *and* the number of distinct voices each cell heard.
Holding cells, rule, input count and rounds identical and varying only whether the six inputs
can disagree: LOCAL 17.9 communities, BROADCAST 50.8, SKEPTIC (5 distinct + 1 forced) 13.8.
**The barrier is decoration; voice diversity is the driver.** And BROADCAST's sd of exactly
0.000 is arithmetic, not robustness — a deterministic mechanism has zero variance by
construction, and a zero-variance number cannot support a relational claim.

**exp8 was buggy and exp10 found it.** `cx = 0.5 if dim == 1` placed all three 1-D opinions
into the same spatial band — **verified 16/16 and 16/16 cell overlap** — so "plurality
collapses to two" was three opinions fighting over the same cells. The tell was exp10
reporting **0.00 opinion deaths in every condition, including 1-D**: the exact opposite of
exp8. Corrected, the law is:

| condition | groups | sd | sep/spread | sd |
|---|---|---|---|---|
| 1-D, 3 seeded | 2.50 | 0.81 | 3.69 | **4.68 — bimodal** |
| 2-D, 3 seeded | 3.10 | 0.30 | 11.02 | 3.25 |
| **2-D, 4 seeded** | **3.00** | **0.00** | 14.55 | 4.55 |
| **3-D, 4 seeded** | **4.00** | **0.00** | 12.29 | 2.56 |

**A d-dimensional opinion space sustains d+1 tissues.** 2-D *refuses* a fourth (one dies
every run); 3-D holds four. The 1-D column is bimodal and the file refuses to print its mean.

**The claim is much smaller than it was.** Not "1-D cannot hold three" — 1-D holds 2.50. It
is: **2-D makes plurality reliable where 1-D makes it a coin flip.**

## The instruments that lied, across all ten experiments

Seven, all caught, none of them by reading the code:

1. A boundary computed **before** the perturbation it measured — four identical numbers presented as stability.
2. A control that set every sample to an exact value — MAE 0.0000, and it could not fail.
3. A condition that seeded a "third" opinion at the same value as the first, so it merged by construction.
4. A min-pairwise-distance metric **pinned at 0.0000** by arithmetic over 4560 pairs.
5. A "3-layer MLP" that was `w·x + b`.
6. Unequal input widths (36 vs 4) that measured model capacity and reported it as representation quality.
7. A seeding bug placing three opinions in the same 16 cells, which produced a confident wrong result for three sessions.

**The pattern, not the list, is the lesson.** Every one of these produced a number that
looked fine. None was caught by asserting more carefully. All were caught by adding a
condition that was capable of failing — or by a later experiment producing a number that
contradicted an earlier one, which is what happened in case 7.
