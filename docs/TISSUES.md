# Tissues: what the 2-D result actually establishes

## The short version

On a line, this system can hold two smear-like groups. In a plane, the **same local rule,
the same cells, the same rounds** hold three well-separated communities that survive being
kicked. The dimensionality of the opinion space — not the rule — is the variable that
decides whether structure is an attractor or a transient.

## exp8 — the opinion space, not the rule

Three seeded opinions, ten seeds, identical rule in both rows.

| | groups | separation/spread | sd |
|---|---|---|---|
| 1-D (three points on a line) | 2.20 | **0.784** | 0.322 |
| 2-D (three corners of a square) | **3.10** | **11.018** | 3.251 |

A separation/spread ratio **below 1** means the "groups" are a partition of a smear — the
same thing three arbitrary slices of a continuous distribution would give you. That is
exactly what the 1-D case produces, and it is why exp4's "plurality collapses to two" was
not a fact about decentralised deference. It was a fact about **lines**.

Above 1 means the communities are genuinely apart, not merely labelled. The 2-D case is at
11.0.

**This also matters because bounded confidence is 1-D.** Hegselmann–Krause and Deffuant
live on a line, and two components on a line is close to degenerate. A 2-D local rule
sustaining three separated communities is a different object, and no prior for it was
found in the review.

**The metric had to be replaced first.** The initial readout was minimum pairwise opinion
distance, which returned exactly 0.0000 with sd 0.0000 in every condition. That is
arithmetic, not measurement: 96 cells give 4560 pairs, two of them coinciding is certain,
so the minimum is pinned at zero permanently. A metric that cannot leave zero cannot
support a relational claim. It is now a between-cluster / within-cluster ratio, which is
scale-free and cannot be pinned.

## exp9 — the tissues are an attractor, and one condition is a dud

| condition | sep/spread | groups |
|---|---|---|
| control | 11.018 | 3.10 |
| 20% **positional** kick | 11.018 | 3.10 |
| 20% **belief** kick | **5.480** | 3.00 |
| 60% positional kick + 180 rounds anneal | **17.032** | 3.10 |

**The positional kick is a dud and is reported as a dud.** It moves cells through space
without touching their beliefs, and the ratio is measured in belief space. Verified
directly: kick applied, measured immediately, unchanged to four decimals. That condition
cannot fail. It is a check, not evidence, and presenting it as a stability result would be
the same mistake as presenting a zero-variance broadcast as robustness.

**The belief kick is the real test.** Displacing the beliefs of 20% of cells cuts the ratio
from 11.0 to 5.5 — the tissues are genuinely damaged — and they recover, holding three
groups at a ratio still far above 1.

**The contrast with exp3 is the finding.** In one dimension, a large kick plus annealing
collapsed the boundary to 0.0038 and healed the swarm into **unanimity** (neighbour
agreement 0.996). In two dimensions, the same treatment leaves three groups at ratio 17.0
— and the ratio goes **up**. After being kicked, the configuration comes back sharper than
it started.

So: on a line, tissue is a transient the system tolerates and then dissolves. In the
plane, it is an attractor the system restores.

## What this does not establish

- **Two dimensions is still two dimensions.** Nothing here shows a system sustaining five
  or ten tissues, and the sweep in `k` (exp5) was one-dimensional throughout.
- **The 1-D boundary was never nothing.** exp3 showed it is stable under mild perturbation
  and dissolves under a large one. "Transient" and "meaningless" are different claims and
  only the first was earned.
- **One seed configuration.** The three corners are maximally separated by construction.
  Seeds at interior positions, or four corners, are untested.
- **No mechanism.** It is not explained why a dimension changes the stability class. A
  plausible account — the boundary can be a genuine barrier in the plane while it must
  always leak along a line — is a hypothesis, not a result, and has not been tested.

## Why this is the most defensible thing here

Not because it is the most striking, but because it is the only finding that is **not**
prior art, **not** a control, and **not** refuted by its own control. Every other result
in this repository is one of those three things, and `PRIOR-ART.md` says which.
