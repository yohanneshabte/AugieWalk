# AugieWalk
Shortest walking routes between campus buildings — originally for Augustana University,
now with a full **San Diego State University (SDSU)** campus graph, a Python package/CLI
(Dijkstra + A*), and an offline-capable mobile web app.

## Python CLI
```bash
pip install -r requirements.txt
python -m augiewalk route "Love Library" "Viejas Arena" --campus sdsu
python -m augiewalk route Solberg Library --campus augustana
python -m augiewalk --campus sdsu list           # all buildings
python -m augiewalk route "maya" "engineering" --algo dijkstra --all
pytest -q
```
Names are matched case-insensitively with fuzzy fallback.

Package layout: `augiewalk/graph.py` (JSON loader, name resolution), `augiewalk/search.py`
(Dijkstra and A* with a Euclidean heuristic, which is admissible since edge weights are pixel
distances), `augiewalk/cli.py`.

## Data
* `data/sdsu_graph.json` — 54 buildings/landmarks + 36 walkway junctions, 139 edges, pixel
  coordinates on `data/sdsu_map.jpg` (1836×1466; north arrow points bottom-left).
  Edge weights: `px` and `m` (≈0.59 m/px). `lat`/`lng` per node and a `geo.px_from_latlng`
  affine transform are **approximate**, fitted on three public reference points
  (Viejas Arena, Love Library, Hepner Hall). Regenerate with `python tools/build_sdsu_graph.py`
  (then copy to `web/data/`).
* `data/augustana_graph.json` — the original Augustana graph (walk-time seconds) ported from
  `AugieBuddy_V3.py`. The legacy Tk GUI (`AugieBuddy_GUI.py`) is unchanged.

## Web app (`/web`)
Static, no build step, no framework (~25 KB of HTML/CSS/JS + map webp).
* Pan / pinch-zoom map (GPU transforms, rAF batched), searchable From/To pickers, route overlay,
  distance and walk time, shareable `#from=…&to=…` URLs.
* A* runs client-side (`web/route.js`) on the same JSON.
* **Go mode**: full-screen, big next-turn card, step-by-step, high-contrast dark theme,
  Screen Wake Lock, `watchPosition` GPS dot with auto-advance (approximate geo-registration),
  manual ‹ › always available (also arrow keys).
* PWA: manifest + icons, add to home screen, safe-area insets, service worker with versioned
  cache-first precache and a **Download for offline** button with progress.
* Theme bubbles (`web/lib/theme-bubbles/`): standalone picker module, tokens from
  [yohanneshabte/wander](https://github.com/yohanneshabte/wander) (see its README for details).

Run locally: `cd web && python3 -m http.server 8000` → http://localhost:8000
(geolocation and service workers need `localhost` or HTTPS).

Deploy: `.github/workflows/pages.yml` publishes `/web` on pushes to `master`. Enable it once in
**Settings → Pages → Source: GitHub Actions**.

## Limitations
Building positions and walkways were hand-digitised from a photo of the campus map, so routes
are straight-line approximations of paths; stairs/elevators/accessibility are not modelled.
GPS mapping is a 3-point affine fit and may be off by tens of metres.

### Original preview
![preview](https://github.com/yohanneshabte/AugieWalk/blob/master/preview.png)
