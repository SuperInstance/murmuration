# Prior art, and what survives it

An adversarial scout reviewed this work against the literature. It was right about almost
everything, and two of its findings forced rewrites. Recorded here so the corrections are
durable and so nobody re-derives them.

## The two findings that hurt

**1. The murmuration motivation is backwards.**

Cavagna et al. 2010, *PNAS* 107(26):11865–11870, doi `10.1073/pnas.1005766107` — verified
against the paper's own text, not a summary:

> "The group cannot be divided into independent subparts, because the behavioral change of
> one individual influences and is influenced by the behavioral change of all other
> individuals in the group."

Starling flocks are the textbook example of **scale-free integration**. This project used
them to motivate stable subgroups with boundaries. That is the opposite of what the
canonical murmuration paper says. Related: Ballerini et al. 2008 found topological
interaction at **6–7 nearest neighbours** — the `k=6` used throughout is Ballerini's
number, not a free parameter.

**The inversion is better than the original framing, and it is true:** *tissue is what
starlings famously are not. Here is a local rule that makes it.* That claim is now the
one this project makes, and it no longer leans on a paper that contradicts it.

**2. The partition result is textbook bounded confidence.**

Hegselmann–Krause (2002) and Deffuant et al. (2000): agents average only opinions within a
confidence bound ε, producing stable clusters with hard boundaries — "the probability that
an agent is influenced by an agent from another cluster is zero" — with cluster count ≈
**1/(2ε)**. The phase names are already in the literature: one cluster is *consensus*, two
is **polarization**, more is *fragmentation*.

So "two opposed regions → polarization collapses, the swarm partitions, boundary
disagreement spikes 15.6x" is the **polarization phase of Hegselmann–Krause**, roughly
twenty years old. It was presented here as a finding. It is not one.

## What was already published before this project

- **"Local rules produce global agreement on a property no cell can see"** — Randazzo et
  al. 2020, *Self-classifying MNIST digits*, Distill, doi `10.23915/distill.00027.002`, asks
  this in so many words and answers yes. Density-classification NCA work frames
  local-to-global consensus as "a defining problem of collective intelligence."
- **"No global coordination"** — Mordvintsev et al. 2020, *Growing NCA*, Distill, doi
  `10.23915/distill.00023`: "Cells can only see the states of the cells in their tiny
  neighbourhood." Claimed explicitly.
- **Predictive coding** — Rao & Ballard 1999; Whittington & Bogacz 2017, *Neural
  Computation* 29(5):1229–1262. Local errors, converging weight updates.

**The narrowing that survives:** NCA and predictive coding both have a **global objective
at training time** (L2/perceptual loss; `E = Σ_ℓ‖ε_ℓ‖²`). This project has **no objective
at any time, and the update rule is not derived from one.** That is a real difference and
it is the honest one. It is also why there is no optimality guarantee — and why the
averaging failure documented in `ITERATIONS.md` is not surprising.

## DeGroot is NOT the threat — and the reason is structural

DeGroot (1974) is linear: `x(t+1) = P x(t)` with P row-stochastic. Consensus requires
strong connectivity and aperiodicity; the limit is `1πᵀ` — rank one — so the fixed point is
necessarily a **single number**.

This project's rule is **discontinuous** — adopt, don't average. There is no linear map, so
there is no spectral contraction, so **no DeGroot theorem forces a single number.** The
bifurcation between consensus and permanent partition is precisely what a linear
contraction *forbids*. That is a structural distinction, not a technicality.

Friedkin–Johnsen (1977) gets non-consensus by adding a stubbornness diagonal Λ. But its
clustering is **topological, not spatial** — which is the next point.

## What is genuinely not published

**The degree-preserving rewiring control.** Comparing the real neighbour graph against a
degree-matched random rewiring of itself to ask *is this actually sorted, or is the
boundary score an artefact of edge count* — no direct prior was found.

**But note what it is: a control design, not a phenomenon.** The phenomenon it
disambiguates is Hegselmann–Krause's. A novel experimental control is worth having and is
not the same as a novel result.

## The result that did not survive its own control: exp7

An earlier claim was "local propagation beats central broadcast on emergent structure."
That comparison changed two things at once — the information topology **and** the number of
distinct voices each cell heard. So it might have been entirely about voice diversity with
the barrier playing no part.

`experiments/exp7_isolating_the_barrier.py` holds cells, rule, **input count**, and rounds
identical, and varies only whether the 6 inputs can disagree:

| condition | communities | polarization | sd |
|---|---|---|---|
| LOCAL — 6 inputs, 6 distinct voices | 17.9 | 0.157 | 0.114 |
| BROADCAST — 6 inputs, 1 repeated voice | 50.8 | 0.700 | **0.000** |
| SKEPTIC — 6 inputs, 5 distinct + 1 forced | **13.8** | 0.258 | 0.191 |

Fewer, larger communities means more structure. SKEPTIC has the *most*, LOCAL next,
BROADCAST least — and SKEPTIC is closer to LOCAL than to BROADCAST.

**The barrier is decoration. Voice diversity is the driver.** exp1's headline is annotated
as a **confound, not a discovery.**

And BROADCAST's sd of exactly 0.000 is arithmetic, not robustness: a broadcast is
deterministic by construction, so a zero-variance number cannot support a relational claim.
The degenerate-measurement rule cuts both ways — it also refuses to let a dead number be
cited as a strong one.

## Corrected status of every result

| # | result | status |
|---|---|---|
| 1 | local rules → global consensus, no authority | **prior art** (Randazzo 2020; k=6 is Ballerini's) |
| 2 | local beats broadcast on structure | **REFUTED as a barrier claim** — exp7 shows it is voice diversity |
| 3 | no-seed control → 0.000 | **a control, never a finding** — zero variance is vacuous |
| — | JEV as a claim probe | **RETRACTED.** The probe discriminates perfectly; the null was a malformed request on my side. A negative control sharing the call under test cannot detect a fault in that path. |
| 4 | two opposed regions partition, 15.6x boundary | **prior art** (Hegselmann–Krause polarization) |
| 5 | boundary peaks at k=16, sorting at k=4 | **uncorroborated**; no prior found either way |
| 6 | decentralised ≈ global estimation, 5x better than alone | **survives** — but the scramble control shows it is the mean, computed locally |
| 7 | the barrier vs voice diversity | **new** — and it refutes result 2 |
| 8 | degree-preserving rewiring as a sorting control | **new**, and it is a control design, not a phenomenon |

**What is genuinely novel here is narrower than it was this morning, and it is honest
narrower:** a control that separates spatial sorting from edge-count artefacts, and the
finding that the barrier everyone reaches for is not the variable that does the work.
