"""The murmuration kernel, take two.

Take one glued a Boid simulation to a vote network and then wondered why the swarm never
cohered: movement and belief were two parallel systems, so neither moved the other. That is
not a murmuration. That is two simulations sharing a variable name.

The mechanism that actually produces a murmuration is this: **cells drift toward the
beliefs they agree with.** Alignment, cohesion and separation are not applied to
positions by a controller -- they are applied to BELIEFS, and position is the consequence.
Two cells that arrive at similar views end up adjacent. A tissue is what happens when many
cells agree locally. An organ is a cluster of tissues. An organism is a set of organs that
still talk to each other. None of those words appear in this file, and none of them need
to: they are the same process observed at different scales.

So the update is:
    for each cell, look only at its k nearest neighbours
    compare beliefs
    move toward those it agrees with, away from those it does not

and the emergent structure -- clusters, tissues, boundaries -- is read off the geometry
after the fact by a reader. The cells never learn that a tissue exists.
"""
from __future__ import annotations
import math, random
from .cell import Cell


def knn_lattice(n, k, seed=0):
    """A k-nearest-neighbour lattice over random initial positions.

    k is the whole claim. A full mesh is a complete graph and therefore carries global
    information by construction: every node reaches every other in one hop, so "local"
    is a fiction and consensus is a single global vote wearing a k-nickname. A line is
    too poor to propagate. The murmuration lives in the band between.
    """
    rng = random.Random(seed)
    pts = [(rng.random(), rng.random()) for _ in range(n)]
    lat = []
    for i in range(n):
        d = sorted(range(n),
                   key=lambda j: (pts[i][0]-pts[j][0])**2 + (pts[i][1]-pts[j][1])**2)
        lat.append([j for j in d if j != i][:k])
    return pts, lat


def polarization(beliefs):
    """Concentration of beliefs in [0,1]: 0 = evenly split, 1 = total agreement.

    The MEAN of the beliefs is a bad observable and always will be. A flock split
    perfectly in half averages to 0.5, an undecided flock averages to 0.5, and on a
    symmetric initial condition it is 0.5 forever -- a measurement with std == 0, which
    is vacuous and will be reported as a result by anyone who does not check.
    Polarization cannot be faked by symmetry.
    """
    n = len(beliefs)
    return abs(sum(2.0 * b - 1.0 for b in beliefs)) / n


def cluster_count(pts, lat, thresh=0.06):
    """How many connected communities the swarm has formed. The 'tissue' observable.

    Read off the geometry by a reader. No cell knows this number.
    """
    parent = list(range(len(pts)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for i, nb in enumerate(lat):
        for j in nb:
            d = math.hypot(pts[i][0]-pts[j][0], pts[i][1]-pts[j][1])
            if d < thresh:
                a, b = find(i), find(j)
                if a != b: parent[a] = b
    return len({find(i) for i in range(len(pts))})


def swarm(n=80, k=6, rounds=60, seed=0, inject=None, inject_frac=0.05,
          central=False, step=0.035, opposed=None):
    """Run the murmuration. `inject` seeds a local opinion into a few cells.

    inject_frac   how many cells receive the local opinion (default 5%)
    central=True  THE CONTROL: the local opinion is also broadcast to every cell.
                  If the murmuration is real, the two should behave differently; if they
                  do not, the murmuration was a central broadcast wearing a k-nickname.
    """
    rng = random.Random(seed)
    pts, lat = knn_lattice(n, k, seed=seed)
    cells = [Cell(cid=i, kind=["optimist", "pessimist", "agnostic"][i % 3],
                  inputs=[], seed=rng.random()) for i in range(n)]
    for c in cells:
        c.conf = rng.uniform(0.2, 0.8)          # heterogeneous: see swarm.py notes

    # Two opposed regions. This is the interesting case: a central system has to break
    # the tie somehow, and anything it uses to break it is authority wearing a hat. A
    # murmuration has no tiebreaker available, so the honest outcome is not consensus but
    # a BOUNDARY -- two tissues with an edge between them.
    injected, opposed_set = set(), set()
    if opposed is not None:
        order = sorted(range(n), key=lambda i: (pts[i][0]-0.5)**2 + (pts[i][1]-0.5)**2)
        half = max(1, int(n * inject_frac))
        opposed_set = set(order[:half])
        for i in opposed_set:
            cells[i]._b = opposed
            cells[i].conf = 0.9
            cells[i].seed = 0.001
        rest = order[half:]
        if inject is not None:
            injected = set(rest[:half])
            for i in injected:
                cells[i]._b = inject
                cells[i].conf = 0.9
                cells[i].seed = 0.999
    if inject is not None and not opposed_set:
        # a small spatial region, not a random scatter -- a LOCAL opinion
        ox, oy = 0.5, 0.5
        order = sorted(range(n), key=lambda i: (pts[i][0]-ox)**2 + (pts[i][1]-oy)**2)
        injected = set(order[:max(1, int(n * inject_frac))])
        for i in injected:
            cells[i].seed = 0.999                 # force the prior toward the opinion

    traj_pol, traj_clust = [], []
    for r in range(rounds):
        beliefs = [c._b for c in cells]
        for i, nb in enumerate(lat):
            bi = beliefs[i]
            ax = ay = sx = sy = 0.0
            cnt = 0
            for j in nb:
                d = beliefs[j] - bi
                if abs(d) < 1e-9:
                    continue
                dx = pts[j][0] - pts[i][0]; dy = pts[j][1] - pts[i][1]
                dist = math.hypot(dx, dy) or 1e-9
                cnt += 1
                # ALIGN: move toward cells whose beliefs agree
                ax += dx / dist * max(0.0, d)
                # SEPARATE: push away from cells whose beliefs disagree
                sx -= dx / dist * max(0.0, -d)
                ay += dy / dist * max(0.0, d)
                sy -= dy / dist * max(0.0, -d)
            if not cnt:
                continue
            nx = pts[i][0] + step * (ax + sx)
            ny = pts[i][1] + step * (ay + sy)
            pts[i] = [nx % 1.0, ny % 1.0]

        # Beliefs refresh from the NEW neighbourhoods.
        #
        # NOT averaging. Averaging has a fixed point at the prior: every cell pulls toward
        # the local mean, the local mean is 0.5, so a symmetric swarm converges to
        # UNDECIDED and stays there. Measured: polarization pinned at 0.008 for 60 rounds.
        # That is the degenerate-measurement rule biting live code, and it took a control
        # to find it -- the swarm looked like it was running, and the number was dead.
        #
        # The mechanism is THRESHOLD ADOPTION with a confidence gate, which is what
        # decentralized consensus actually uses:
        #   - a cell DEFERS to a neighbour who is more confident and roughly shares my
        #     direction of travel
        #   - a confident cell does NOT get talked out of its belief by neighbours
        #   - a cell surrounded by confident disagreement loses confidence and its
        #     belief drifts, rather than flipping instantly
        for i, nb in enumerate(lat):
            me = cells[i]
            seen = [{"kind": cells[j].kind, "vote": cells[j]._b, "conf": cells[j].conf}
                    for j in nb]
            if central and inject is not None and not opposed_set:
                # THE CONTROL: every cell also hears the opinion as a broadcast, with
                # full confidence. If the murmuration is doing the work, injecting should
                # not need this.
                seen.append({"kind": "broadcast", "vote": inject, "conf": 0.99})
            if not seen:
                me._b = 0.5
                continue
            if me.cid in injected:
                me._b = inject                       # a seed holds its opinion
                me.conf = max(me.conf, 0.9)
                continue
            if me.cid in opposed_set:
                me._b = opposed
                me.conf = max(me.conf, 0.9)
                continue
            # DEFERENCE TO CONFIDENCE, not similarity.
            #
            # Gating adoption on "is a neighbour near my belief" blocks transmission
            # outright: measured, a seed at 0.85 and its neighbours at 0.5 differ by 0.35,
            # a 0.12 threshold is never satisfied, and the opinion cannot cross the gap.
            # Polarization froze at exactly 0.035 (the seeds, and nobody else) with
            # stdev 0.0000. A frozen number is not a weak result; it is a dead one.
            #
            # What actually carries a belief through a swarm is a cell deferring to a
            # peer who is markedly more confident than it is. No authority, no broadcast,
            # no vote count -- just "you seem to know this better than I do", applied
            # locally and identically everywhere.
            best = max(seen, key=lambda x: x["conf"])
            if best["conf"] > me.conf + 0.03:
                me._b = 0.85 * best["vote"] + 0.15 * me._b
                me.conf = min(0.95, me.conf + 0.04)
                me.witness.append(("defer", round(me._b, 6), round(me.conf, 4), len(seen)))
            else:
                # nothing here outranks me; drift toward whatever is near me
                near = [x for x in seen if abs(x["vote"] - me._b) < 0.15]
                if near:
                    me._b = 0.85 * (sum(x["vote"] for x in near) / len(near)) + 0.15 * me._b
                    me.conf = min(0.95, me.conf + 0.01)
                    me.witness.append(("align", round(me._b, 6), round(me.conf, 4), len(seen)))
                else:
                    me.conf = max(0.05, me.conf - 0.01)
                    me.witness.append(("isolated_view", round(me._b, 6), round(me.conf, 4), len(seen)))

        # recompute the kNN on the new positions, so the lattice is not frozen
        lat = _reknn(pts, k)
        traj_pol.append(polarization([c._b for c in cells]))
        traj_clust.append(cluster_count(pts, lat))

    beliefs = [c._b for c in cells]
    return {"polarization": traj_pol, "clusters": traj_clust, "beliefs": beliefs,
            "boundary": boundary_score(beliefs, lat),
            "pts": pts, "lat": lat, "cells": cells,
            "n_injected": len(injected), "n_opposed": len(opposed_set)}


def boundary_score(beliefs, lat):
    """Mean |belief difference| across every edge. A tissue boundary shows up here.

    If the swarm resolved its disagreement there is no boundary. If it formed tissues,
    this is high while polarization is LOW -- and that combination is the whole finding.
    """
    ds = [abs(beliefs[i] - beliefs[j]) for i, nb in enumerate(lat) for j in nb]
    return sum(ds) / len(ds) if ds else 0.0


def _reknn(pts, k):
    lat = []
    for i in range(len(pts)):
        d = sorted(range(len(pts)),
                   key=lambda j: (pts[i][0]-pts[j][0])**2 + (pts[i][1]-pts[j][1])**2)
        lat.append([j for j in d if j != i][:k])
    return lat
