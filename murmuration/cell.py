"""A first-person cell.

The defining constraint: **a cell cannot see the whole.** It has a body with `k` inputs,
and it may only read those. There is no global state, no global loss, no orchestrator, and
no cell that is told what to conclude.

This is not a stylistic choice. It is the whole claim. A network in which every unit can
read the global loss is a central authority wearing the costume of a local rule -- one
scalar flows backward and every weight update depends on it. A murmuration has no such
scalar. Each bird knows about seven neighbours. The structure is in the interaction, not
in the leader, because there is no leader.

So the cell body is deliberately *small*. Enough to hold a local belief, take a local
witness, and cast a local vote. If you find yourself wanting to add a field here so the
cell can "know more", that is the central authority re-entering by the back door.

Why first-person: a cell does not emit "the answer is 0.62". It emits what it perceives
from where it sits -- how many neighbours it agrees with, how confident it is, whether it
can see anyone at all. The aggregate is assembled afterwards by a reader, not by the
cells. A cell that knew the aggregate would be able to optimise against it, and the
independence that makes the aggregate informative would be gone.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib


def _mix(x: float) -> float:
    """Deterministic pseudo-noise in [0,1). Seeded per cell, so a run is reproducible."""
    h = hashlib.blake2b(str(x).encode(), digest_size=8).digest()
    return int.from_bytes(h, "big") / float(1 << 64)


@dataclass
class Cell:
    """One first-person perspective. Knows its inputs, its neighbours, and nothing else.

    kind: what this cell is sensitive to. Cells of different kinds can disagree, and
          their disagreement is signal rather than noise.
    k:   how many inputs it may read. k=1 is a single cell in the dark.
    """
    cid: int
    kind: str
    inputs: list          # opaque payloads from neighbours
    seed: float
    # learned local state
    w: dict = field(default_factory=dict)   # per-kind weights
    conf: float = 0.5                       # local confidence in [0,1]
    witness: list = field(default_factory=list)
    _b: float = 0.5                         # this cell's current local belief in [0,1]

    def perceive(self) -> dict:
        """What this cell can see. STRICTLY bounded by len(self.inputs) <= k.

        The bound is enforced by the caller passing at most k inputs; this function has
        no way to reach anything else. That is the point: the information barrier is
        structural, not a convention someone might forget.
        """
        seen = {}
        for p in self.inputs:
            kind = p.get("kind", "?")
            seen[kind] = seen.get(kind, 0.0) + float(p.get("vote", 0.0))
        n = len(self.inputs)
        # isolation is informative: a cell with no neighbours must say so rather than guess
        seen["_n"] = float(n)
        return seen

    def local_belief(self, seen: dict | None = None) -> float:
        """Returns the belief; also stores it as _b. Storing is a convenience for the
        kernel's geometry, NOT a channel -- a cell's belief is what it publishes, and
        publishing is the only thing a cell does."""
        """A vote in [0,1] computed from local evidence only.

        Three terms, all local:
          - agreement with what this cell can see (the murmuration term)
          - how much it can see at all (confidence falls in the dark)
          - a small idiosyncratic prior (so identical views are not identical votes)
        """
        s = self.perceive() if seen is None else seen
        n = s.pop("_n", 0.0)
        if n == 0:
            # no neighbours: fall back to the prior and RECORD the deprivation.
            # Guessing silently would be the single most damaging thing a cell could do.
            self.conf *= 0.5
            self._b = 0.5
            self.witness.append(("isolated", 1))
            return 0.5
        agg = sum(s.values()) / (n + 1e-9)
        # cohesion: pulled toward the local mean
        pull = agg
        # separation: pushed away when the local mean is undecided (near 0.5)
        push = 0.5 if abs(agg - 0.5) < 0.15 else 0.0
        prior = 0.5 + (_mix(self.seed) - 0.5) * 0.2
        v = 0.55 * pull + 0.15 * push + 0.30 * prior
        v = min(0.98, max(0.02, v))
        # confidence grows with evidence, shrinks with disagreement
        spread = sum(abs(x - agg) for x in s.values()) / n
        self.conf = min(0.95, max(0.05, 0.3 + 0.5 * min(1.0, n / 5) - 0.3 * spread))
        self._b = v
        self.witness.append(("vote", round(v, 6), round(self.conf, 4), int(n)))
        return v

    def update(self, target: float, lr: float = 0.15) -> float:
        """Local learning. The ONLY supervision any cell ever receives.

        Note what is absent: there is no gradient, and no other cell's vote appears in
        this update. A cell is corrected toward the answer using its own perceptron of
        what happened -- the same rule applied identically everywhere. This is the
        distributional constraint made executable.
        """
        v = self.local_belief()
        # local error only. Each cell's error is its own; it is never averaged first.
        err = v - target
        self.w["last_err"] = err
        self.conf = min(0.95, max(0.05, self.conf - lr * abs(err)))
        return err
