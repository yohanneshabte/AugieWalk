"""Command line interface: python -m augiewalk route FROM TO --campus sdsu"""
from __future__ import annotations

import argparse
import sys

from .graph import available_campuses, load_campus
from .search import astar, dijkstra


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="augiewalk", description="Campus walking routes")
    p.add_argument("--campus", default="sdsu", choices=available_campuses())
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("route", help="shortest route between two locations")
    r.add_argument("start")
    r.add_argument("goal")
    r.add_argument("--campus", dest="campus_r", choices=available_campuses())
    r.add_argument("--algo", choices=["astar", "dijkstra"], default="astar")
    r.add_argument("--all", action="store_true", help="also list walkway junctions")
    ls = sub.add_parser("list", help="list buildings")
    ls.add_argument("--campus", dest="campus_r", choices=available_campuses())
    a = p.parse_args(argv)
    g = load_campus(a.campus_r or a.campus)
    if a.cmd == "list":
        for n in g.buildings():
            print(n.name)
        return 0
    try:
        s, t = g.resolve(a.start), g.resolve(a.goal)
    except KeyError as e:
        print(f"error: {e.args[0]}", file=sys.stderr)
        return 2
    route = (astar if a.algo == "astar" else dijkstra)(g, s, t)
    print(f"{g.nodes[s].name} -> {g.nodes[t].name} ({g.name}, {a.algo})")
    m, sec = route.meters(g), route.seconds(g)
    if m is not None:
        print(f"Distance: ~{m:.0f} m")
    if sec is not None:
        mm, ss = divmod(round(sec), 60)
        print(f"Walk time: ~{mm} min {ss} s")
    step = 0
    for nid in route.path:
        n = g.nodes[nid]
        if n.type == "junction" and not a.all and nid not in (s, t):
            continue
        step += 1
        print(f"{step:>2}. {n.name}")
    return 0
