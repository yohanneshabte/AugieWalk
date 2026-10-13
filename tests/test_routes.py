import json
import pytest
from augiewalk import astar, dijkstra, load_campus, available_campuses
from augiewalk.cli import main


@pytest.fixture(scope="module")
def sdsu():
    return load_campus("sdsu")


def test_campuses():
    assert {"sdsu", "augustana"} <= set(available_campuses())


def test_sdsu_connected(sdsu):
    start = next(iter(sdsu.nodes))
    seen, stack = {start}, [start]
    while stack:
        for v in sdsu.adj[stack.pop()]:
            if v not in seen:
                seen.add(v); stack.append(v)
    assert seen == set(sdsu.nodes)


def test_required_buildings(sdsu):
    names = {n.name for n in sdsu.buildings()}
    for b in ["Love Library", "Viejas Arena", "Hepner Hall", "Aztec Student Union", "Engineering", "ENS 700"]:
        assert b in names


def test_astar_matches_dijkstra_everywhere(sdsu):
    ids = [n.id for n in sdsu.buildings()]
    for s in ids[::3]:
        for t in ids[1::4]:
            a, d = astar(sdsu, s, t), dijkstra(sdsu, s, t)
            assert a.cost == pytest.approx(d.cost)
            assert a.expanded <= d.expanded


def test_resolve_fuzzy(sdsu):
    assert sdsu.nodes[sdsu.resolve("love library")].name == "Love Library"
    assert sdsu.nodes[sdsu.resolve("Viejas")].name == "Viejas Arena"
    with pytest.raises(KeyError):
        sdsu.resolve("Hogwarts")


def test_route_metrics(sdsu):
    r = astar(sdsu, sdsu.resolve("Love Library"), sdsu.resolve("Viejas Arena"))
    assert 200 < r.meters(sdsu) < 1500
    assert r.seconds(sdsu) == pytest.approx(r.meters(sdsu) / sdsu.walk_speed_mps)


def test_augustana_legacy():
    g = load_campus("augustana")
    r = dijkstra(g, g.resolve("Solberg"), g.resolve("Library"))
    assert r.cost == 267  # same as original AugieBuddy_V3 shortestPath
    assert astar(g, "1", "9").cost == 267


def test_web_copy_in_sync():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    assert json.loads((root / "web/data/sdsu_graph.json").read_text()) == json.loads((root / "data/sdsu_graph.json").read_text())


def test_cli(capsys):
    assert main(["route", "Love Library", "Viejas Arena", "--campus", "sdsu"]) == 0
    out = capsys.readouterr().out
    assert "Distance" in out and "Viejas Arena" in out
    assert main(["route", "nowhere", "Viejas Arena"]) == 2
