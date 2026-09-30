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
