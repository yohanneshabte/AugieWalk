"""Graph model and JSON loader."""
from __future__ import annotations

import difflib
import json
import math
from dataclasses import dataclass, field
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@dataclass
class Node:
    id: str
    name: str
    type: str = "building"
    x: float | None = None
    y: float | None = None
    lat: float | None = None
    lng: float | None = None


@dataclass
class CampusGraph:
    campus: str
    name: str
    nodes: dict[str, Node]
    adj: dict[str, dict[str, float]] = field(default_factory=dict)
    unit: str = "px"
    meters_per_unit: float | None = None
    walk_speed_mps: float = 1.35
    seconds_per_unit: float | None = None  # for graphs weighted in seconds

    @classmethod
    def from_dict(cls, d: dict) -> "CampusGraph":
        nodes = {n["id"]: Node(**{k: n.get(k) for k in Node.__dataclass_fields__ if k in n}) for n in d["nodes"]}
        g = cls(d["campus"], d.get("name", d["campus"]), nodes, {k: {} for k in nodes},
                d.get("weight", "px"), d.get("meters_per_pixel"), d.get("walk_speed_mps", 1.35),
                1.0 if d.get("weight") == "seconds" else None)
        for e in d["edges"]:
            a, b = e["from"], e["to"]
            if a not in nodes or b not in nodes:
                raise ValueError(f"edge references unknown node: {a}-{b}")
            w = e.get(g.unit)
            if w is None:
                w = g.euclid(a, b)
            g.adj[a][b] = g.adj[b][a] = float(w)
        return g

    def euclid(self, a: str, b: str) -> float:
        na, nb = self.nodes[a], self.nodes[b]
        if na.x is None or nb.x is None:
            return 0.0
        return math.hypot(na.x - nb.x, na.y - nb.y)

    @property
    def has_coords(self) -> bool:
        return self.unit == "px" and all(n.x is not None for n in self.nodes.values())

    def buildings(self) -> list[Node]:
        return sorted((n for n in self.nodes.values() if n.type != "junction"), key=lambda n: n.name)

    def resolve(self, query: str) -> str:
        """Resolve an id or (fuzzy, case-insensitive) building name to a node id."""
        if query in self.nodes:
            return query
        q = query.strip().lower()
        names = {n.name.lower(): n.id for n in self.buildings()}
        if q in names:
            return names[q]
        subs = [i for nm, i in names.items() if q in nm]
        if len(subs) == 1:
            return subs[0]
        close = difflib.get_close_matches(q, list(names), n=1, cutoff=0.6)
        if close:
            return names[close[0]]
        hint = f" (ambiguous: {', '.join(self.nodes[i].name for i in subs)})" if subs else ""
        raise KeyError(f"unknown location: {query!r}{hint}")


def available_campuses() -> list[str]:
    return sorted(p.stem.replace("_graph", "") for p in DATA_DIR.glob("*_graph.json"))


def load_campus(campus: str = "sdsu", path: str | Path | None = None) -> CampusGraph:
    p = Path(path) if path else DATA_DIR / f"{campus}_graph.json"
    return CampusGraph.from_dict(json.loads(p.read_text()))
