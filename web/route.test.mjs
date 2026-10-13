import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
import { buildGraph, astar, directions, latLngToPx } from './route.js';
const data = JSON.parse(readFileSync(new URL('./data/sdsu_graph.json', import.meta.url)));
const g = buildGraph(data), id = n => data.nodes.find(x => x.name === n).id;
const b = data.nodes.filter(n => n.type === 'building');
let checked = 0;
for (const s of b) for (const t of b) { if (s === t) continue;
  const a = astar(g, s.id, t.id), d = astar(g, s.id, t.id, false);
  assert.ok(a && Math.abs(a.cost - d.cost) < 1e-6); checked++; }
const r = astar(g, id('Love Library'), id('Viejas Arena'));
const steps = directions(g, r.path);
assert.equal(steps.at(-1).turn, 'arrive');
const lib = data.nodes.find(n => n.name === 'Love Library'), p = latLngToPx(data.geo, lib.lat, lib.lng);
assert.ok(Math.hypot(p.x - lib.x, p.y - lib.y) < 2);
console.log(`ok: ${checked} A*/Dijkstra pairs agree; ${steps.length} steps Love Library -> Viejas (${Math.round(r.cost * g.mpp)} m)`);
