# murmuration

A swarm of first-person cells that read only their `k` nearest neighbours and reach
consensus by local deference, with no central authority and **no objective at any time**.

**Read [`docs/PRIOR-ART.md`](docs/PRIOR-ART.md) first.** An adversarial review against the
literature killed several of the original claims, and the corrections are more useful than
the claims were. Three of them:

- **The murmuration motivation was backwards.** Cavagna et al. 2010 (PNAS) found starling
  flocks are *scale-free correlated* and "cannot be divided into independent subparts" —
  the opposite of the stable-subgroup framing this project started from. (Ballerini 2008's
  6–7 neighbours is also where `k=6` came from.)
- **"Local beats broadcast on structure" was a confound.** `exp7` holds cells, rule, input
  count and rounds identical and varies only whether the inputs can disagree. The barrier
  is decoration; **voice diversity is the driver.** That result is now annotated as refuted.
- **The partition result is textbook bounded confidence** — the polarization phase of
  Hegselmann–Krause, ~2002, with its 1/(2ε) cluster law.

What is actually left is much smaller — and one piece of it is new. Read
[`docs/TISSUES.md`](docs/TISSUES.md):

**On a line, this system can hold two smear-like groups. In a plane, the same rule holds
three well-separated communities that survive being kicked** (separation/spread 11.0 vs
0.78; after a 20% belief kick it drops to 5.5 and recovers; after the kick that destroyed
the 1-D boundary it comes back *sharper*, 17.0). Bounded confidence is 1-D, so a 2-D local
rule sustaining three separated communities is a different object.

So dimensionality does not only change how many opinions fit — **it decides whether the
structure is an attractor or a transient.** On a line, tissue is something the system
tolerates and then dissolves. In the plane, it restores.

Also left: a novel **control** (degree-preserving rewiring, separating spatial sorting from
an edge-count artefact), structure peaking at an intermediate `k` with sorting and division
peaking at *different* `k`, and **decentralised estimation matching the global mean while
being 5× better than a lone cell** — with the scramble control showing it is the mean,
computed the long way.

## Run it

```bash
python3 experiments/exp1_propagation.py            # propagation + controls
python3 experiments/exp2_boundary.py               # disagreement + rewiring control
python3 experiments/exp3_boundary_stability.py     # REFUTES the tissue claim
python3 experiments/exp4_third_opinion.py          # plurality collapses to two
python3 experiments/exp5_k_sweep.py                # two different scales
python3 experiments/exp6_does_it_train.py          # the scramble control refutes the good version
python3 experiments/exp7_isolating_the_barrier.py  # REFUTES result 2
python3 experiments/exp8_opinion_dimension.py     # 1-D vs 2-D: the ceiling is the line
python3 experiments/exp9_2d_tissue_stability.py   # 2-D tissues are an attractor
TYPESAFEAI_KEY=... python3 jev_control.py          # the JEV probe does not discriminate
```

## Mechanisms that were dead before they were alive

Caught by controls, not by reading code:

1. **Averaging has a fixed point at the prior.** Local averaging converged to *undecided* —
   polarization 0.008, stdev 0.0014. Replaced with deference to confidence.
2. **Similarity gating cannot carry a belief anywhere.** A 0.12 threshold between a seed at
   0.85 and neighbours at 0.5 was never satisfied. Polarization froze at 0.035, stdev
   0.0000. A frozen number is not a weak result, it is a dead one.
3. **The tissue does not defend itself.** A 60% kick plus 180 rounds of annealing heals the
   swarm into *unanimity* (agreement 0.996), not back into two tissues.

## The rule this is built to obey

A relational claim over a constant measurement is vacuously true. Any claim resting on a
signal with `std == 0` is scored **INCONCLUSIVE, never PASSED** — and that rule cuts both
ways. It refused three of my own numbers that looked like results: the no-seed control at
exactly 0.000, the broadcast's sd of 0.000 across ten seeds, and a sortedness metric so
flat it could not discriminate anything.

Three of my own instruments also lied during this work and were caught: a boundary
computed before the perturbation it was supposed to measure, a control that set every
sample to an exact value and could not fail, and a condition that seeded a "third"
opinion at the same value as the first, so it merged by construction.
