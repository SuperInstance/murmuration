# Tissues: how many, and what a dimension buys you

## The short version

A `d`-dimensional opinion space sustains **`d+1` well-separated, defended tissues** under
one fixed local rule. 2-D holds three and *fails* to hold four. 3-D holds four, every
seed, with zero variance. At `d=1` the behaviour is bimodal and should not be quoted as a
mean at all.

**None of this existed an hour ago and the first version of it was a bug.** The 1-D arm of
this experiment seeded all three opinions into the same spatial band — 16/16 cell overlap
— so "plurality collapses to two" was three opinions fighting over the same cells. It was
caught by a later experiment, not by reading the code.

## exp8 corrected — the scaling law

| condition | groups | sd | sep/spread | sd | bimodal? |
|---|---|---|---|---|---|
| 1-D, 3 seeded | 2.50 | 0.81 | 3.69 | **4.68** | **YES** |
| 2-D, 3 seeded | 3.10 | 0.30 | 11.02 | 3.25 | no |
| 2-D, 4 seeded | **3.00** | **0.00** | 14.55 | 4.55 | no |
| 3-D, 4 seeded | **4.00** | **0.00** | 12.29 | 2.56 | no |

**The ceiling is real and it is tested.** 2-D asked to hold four opinions gives three, with
sd 0.000 — one opinion dies every single run. 3-D asked to hold four gives four, sd 0.000.
That is not a monotone "more dimensions is better"; it is a specific limit, and the
experiment that establishes it is the one where the extra opinion is refused.

**The 1-D column is a warning, not a number.** Its spread (4.68) is larger than its mean
(3.69), which is the signature of a bimodal distribution: some seeds hold three opinions
apart, some collapse. A mean over two different phenomena summarises neither. The file
detects this itself and refuses to present the column cleanly.

## exp9 — the tissues are an attractor

| condition | sep/spread | groups |
|---|---|---|
| control | 11.018 | 3.10 |
| 20% **positional** kick | 11.018 | 3.10 |
| 20% **belief** kick | **5.480** | 3.00 |
| 60% kick + 180 rounds anneal | **17.032** | 3.10 |

**The positional kick is a dud and is reported as a dud.** It moves cells through space
without touching their beliefs, and the ratio is measured in belief space — verified by
applying the kick and measuring immediately, unchanged to four decimals. That condition
cannot fail. Presenting it as stability would be the same error as citing a zero-variance
broadcast as robustness.

The **belief** kick is the real test: displacing 20% of beliefs cuts the ratio from 11.0
to 5.5 and it recovers. And under the same large kick that collapsed the 1-D boundary in
exp3, the 2-D configuration returns at **17.0** — sharper than it started.

## The mechanism is still not known

exp10 set up the discriminating test — ORDERING (a middle opinion on a line gets squeezed)
versus MUTUAL NON-ADJACENCY (only corners avoid contact) — and **the bug was found before
either prediction could be evaluated.** The corrected exp8 now shows 1-D is not a clean
2-way limit at all, so the ORDERING hypothesis needs restating before it can be tested.

What is *not* in doubt is the shape: dimension sets how many tissues fit, and 1-D is
bimodal where 2-D and 3-D are not. Whether that is about adjacency, about packing, or
about the *volume* of opinion space available to each region is untested.

## What this does not establish

- **Not five or ten tissues.** The law is tested at d=1,2,3 and n=3,4. Extrapolating past
  that is arithmetic, not evidence.
- **No mechanism.** A hypothesis, not a result.
- **One seed geometry.** Seeds are placed at the corners, maximally separated by
  construction. Interior placements are untested.
- **Prior art is thin but not empty.** Bounded confidence is 1-D, so a multi-dimensional
  local rule is a different object — but the review found no prior *and* no strong evidence
  of a gap, and absence of prior art in a field with no spatial tissue to form is weak
  evidence of novelty.

## Status

This is the only finding in the repository that is **not** prior art, **not** a control, and
**not** refuted by its own control. It is also the only one that was once wrong and got
caught by a later experiment rather than by inspection — which is the strongest argument in
the whole project for building the mechanism test *and* the seeding test before trusting
any of it.
