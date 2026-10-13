// Pure routing logic (no DOM) — shared by the app and node tests.
export function buildGraph(data) {
  const nodes = new Map(data.nodes.map(n => [n.id, n]));
  const adj = new Map(data.nodes.map(n => [n.id, []]));
  for (const e of data.edges) {
    const w = e[data.weight || 'px'] ?? Math.hypot(nodes.get(e.from).x - nodes.get(e.to).x, nodes.get(e.from).y - nodes.get(e.to).y);
    adj.get(e.from).push([e.to, w]); adj.get(e.to).push([e.from, w]);
  }
  return { data, nodes, adj, mpp: data.meters_per_pixel || 1, speed: data.walk_speed_mps || 1.35 };
}

class Heap { // binary min-heap on [priority, ...]
  constructor() { this.a = []; }
  get size() { return this.a.length; }
  push(v) { const a = this.a; a.push(v); let i = a.length - 1;
    while (i) { const p = (i - 1) >> 1; if (a[p][0] <= a[i][0]) break; [a[p], a[i]] = [a[i], a[p]]; i = p; } }
  pop() { const a = this.a, top = a[0], last = a.pop();
    if (a.length) { a[0] = last; let i = 0;
      for (;;) { const l = 2 * i + 1, r = l + 1; let m = i;
        if (l < a.length && a[l][0] < a[m][0]) m = l; if (r < a.length && a[r][0] < a[m][0]) m = r;
        if (m === i) break; [a[m], a[i]] = [a[i], a[m]]; i = m; } }
    return top; }
}

export function astar(g, start, goal, useHeuristic = true) {
  const G = g.nodes.get(goal);
  const h = id => { if (!useHeuristic) return 0; const n = g.nodes.get(id); return n.x == null ? 0 : Math.hypot(n.x - G.x, n.y - G.y); };
  const dist = new Map([[start, 0]]), prev = new Map(), done = new Set(), pq = new Heap();
  pq.push([h(start), 0, start]);
  while (pq.size) {
    const [, d, u] = pq.pop();
    if (done.has(u)) continue; done.add(u);
    if (u === goal) { const path = [u]; while (path[0] !== start) path.unshift(prev.get(path[0])); return { path, cost: d, expanded: done.size }; }
    for (const [v, w] of g.adj.get(u)) { const nd = d + w;
      if (nd < (dist.get(v) ?? Infinity)) { dist.set(v, nd); prev.set(v, u); pq.push([nd + h(v), nd, v]); } }
  }
  return null;
}

// Turn-by-turn steps. Turns are relative so they work on the rotated map.
export function directions(g, path) {
  const P = path.map(id => g.nodes.get(id)), steps = [];
  let acc = 0, startIdx = 0;
  const bs = [...g.nodes.values()].filter(n => n.type !== 'junction');
  const label = n => n.type !== 'junction' ? n.name :
    'the junction near ' + bs.reduce((b, c) => Math.hypot(c.x - n.x, c.y - n.y) < Math.hypot(b.x - n.x, b.y - n.y) ? c : b).name;
  for (let i = 1; i < P.length; i++) {
    acc += Math.hypot(P[i].x - P[i - 1].x, P[i].y - P[i - 1].y);
    const last = i === P.length - 1;
    let turn = null;
    if (!last) {
      const ax = P[i].x - P[i - 1].x, ay = P[i].y - P[i - 1].y, bx = P[i + 1].x - P[i].x, by = P[i + 1].y - P[i].y;
      const ang = Math.atan2(ax * by - ay * bx, ax * bx + ay * by) * 180 / Math.PI; // + = right (screen y down)
      turn = Math.abs(ang) < 25 ? null : ang > 0 ? (ang > 120 ? 'sharp right' : ang < 50 ? 'slight right' : 'right')
                                               : (ang < -120 ? 'sharp left' : ang > -50 ? 'slight left' : 'left');
    }
    if (turn || last || P[i].type !== 'junction') {
      const m = acc * g.mpp;
      steps.push({ at: path[i], from: startIdx, to: i, meters: m,
        text: last ? `Arrive at ${P[i].name}` : turn ? `Turn ${turn} at ${label(P[i])}` : `Continue past ${P[i].name}`,
        turn: last ? 'arrive' : turn || 'straight' });
      acc = 0; startIdx = i;
    }
  }
  return steps;
}

export function latLngToPx(geo, lat, lng) {
  const [X, Y] = geo.px_from_latlng;
  return { x: X[0] * lat + X[1] * lng + X[2], y: Y[0] * lat + Y[1] * lng + Y[2] };
}
