# murmuration

A swarm of first-person cells that read only their `k` nearest neighbours and reach
consensus by local deference, with no central authority anywhere in the loop.

The framing it starts from: **gradient descent is a centralised control scheme wearing the
costume of a local rule.** One scalar loss reaches every parameter. A murmuration has no
such scalar — and the interesting question is what lives on the other side of that.

## What is actually established

- A local opinion seeded into 5% of cells propagates to global consensus (polarization
  0.550), and a **no-seed control returns exactly 0.000**, so the number is not the swarm
  being agreeable with itself.
- A **central broadcast of the same opinion scores higher (0.700) with sd 0.000 across
  ten seeds and leaves no structure (50.6 communities vs 41.4).** Authority is stronger,
  perfectly repeatable, and empty.
- **Two equally-supported opposing views do not resolve — they partition.** Polarization
  falls to 0.195, boundary disagreement rises 15.6x, and a degree-preserving rewiring
  control confirms the opinions are spatially *sorted* (1.25x) rather than scattered.
- **The JEV probes are a null.** A control showed the probe returns `unclear` to
  "2+2=4", "2+2=5" and "water is dry" alike. They are reported as carrying no information.

## Run it

```bash
python3 experiments/exp1_propagation.py     # propagation + no-seed + broadcast control
python3 experiments/exp2_boundary.py        # disagreement, with the rewiring control
TYPESAFEAI_KEY=... python3 jev_control.py   # is the JEV probe functioning at all?
```

## Two things that were wrong before they were right

Both were caught by controls, not by reading the code:

1. **Averaging has a fixed point at the prior.** Local averaging converged to *undecided*
   and stayed there — polarization 0.008, stdev 0.0014. Replaced with deference to
   confidence.
2. **Similarity gating cannot carry a belief anywhere.** A 0.12 threshold between a seed at
   0.85 and neighbours at 0.5 was never satisfied; polarization froze at 0.035, stdev
   0.0000. A frozen number is not a weak result, it is a dead one.

Full write-up, including the null result and the degenerate-measurement rule applied
throughout: [`docs/RESEARCH-DIRECTION.md`](docs/RESEARCH-DIRECTION.md).

## The rule this is built to obey

A relational claim over a constant measurement is vacuously true. So a check run against
a degenerate signal is not a check — it agrees with itself. Every claim here is scored
**INCONCLUSIVE** when the signal has `std == 0`, never PASSED. Two of the four conditions
here were degenerate before the controls caught them.
