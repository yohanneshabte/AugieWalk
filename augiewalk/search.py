"""Shortest-path search: Dijkstra and A* (Euclidean heuristic)."""
from __future__ import annotations

import heapq
from dataclasses import dataclass

from .graph import CampusGraph


@dataclass
class Route:
    path: list[str]
    cost: float
    expanded: int

    def meters(self, g: CampusGraph) -> float | None:
        return self.cost * g.meters_per_unit if g.meters_per_unit else None

    def seconds(self, g: CampusGraph) -> float | None:
        if g.seconds_per_unit:
            return self.cost * g.seconds_per_unit
        m = self.meters(g)
        return m / g.walk_speed_mps if m is not None else None


def _search(g: CampusGraph, start: str, goal: str, h) -> Route:
    if start not in g.nodes or goal not in g.nodes:
        raise KeyError("start/goal not in graph")
    dist = {start: 0.0}
    prev: dict[str, str] = {}
    pq = [(h(start), 0.0, start)]
    done: set[str] = set()
    while pq:
        _, d, u = heapq.heappop(pq)
        if u in done:
            continue
        done.add(u)
        if u == goal:
            path = [u]
            while path[-1] != start:
                path.append(prev[path[-1]])
            return Route(path[::-1], d, len(done))
        for v, w in g.adj[u].items():
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v], prev[v] = nd, u
                heapq.heappush(pq, (nd + h(v), nd, v))
    raise ValueError(f"no route from {start} to {goal}")


def dijkstra(g: CampusGraph, start: str, goal: str) -> Route:
    return _search(g, start, goal, lambda _n: 0.0)


def astar(g: CampusGraph, start: str, goal: str) -> Route:
    # Euclidean distance is admissible because edge weights are >= straight-line pixel distance.
    h = (lambda n: g.euclid(n, goal)) if g.has_coords else (lambda _n: 0.0)
    return _search(g, start, goal, h)
