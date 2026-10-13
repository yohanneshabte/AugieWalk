import { buildGraph, astar, directions, latLngToPx } from './route.js';
import { mountThemeBubbles } from './lib/theme-bubbles/theme-bubbles.js';

const $ = id => document.getElementById(id);
const W = 1836, H = 1466;
const themes = mountThemeBubbles($('themes'), { storageKey: 'augiewalk:theme' });

/* ---------- pan / pinch-zoom (transform only, rAF batched) ---------- */
const map = $('map'), stage = $('stage');
const view = { s: 1, x: 0, y: 0 }; let raf = 0;
const minScale = () => Math.min(innerWidth / W, innerHeight / H);
const clamp = () => {
  view.s = Math.max(minScale() * 0.9, Math.min(4, view.s));
  const w = W * view.s, h = H * view.s;
  view.x = w < innerWidth ? (innerWidth - w) / 2 : Math.min(0, Math.max(innerWidth - w, view.x));
  view.y = h < innerHeight ? (innerHeight - h) / 2 : Math.min(innerHeight * .3, Math.max(innerHeight * .7 - h, view.y));
};
const draw = () => { raf = 0; stage.style.transform = `translate3d(${view.x}px,${view.y}px,0) scale(${view.s})`; };
const schedule = () => { clamp(); raf ||= requestAnimationFrame(draw); };
const zoomAt = (k, cx, cy) => { const s = view.s; view.s *= k; clamp(); const r = view.s / s;
  view.x = cx - (cx - view.x) * r; view.y = cy - (cy - view.y) * r; schedule(); };
const ptrs = new Map(); let last = null;
map.addEventListener('pointerdown', e => { map.setPointerCapture(e.pointerId); ptrs.set(e.pointerId, e); last = null; });
map.addEventListener('pointermove', e => {
  if (!ptrs.has(e.pointerId)) return; ptrs.set(e.pointerId, e);
  const p = [...ptrs.values()];
  const cur = p.length > 1 ? { x: (p[0].clientX + p[1].clientX) / 2, y: (p[0].clientY + p[1].clientY) / 2,
    d: Math.hypot(p[0].clientX - p[1].clientX, p[0].clientY - p[1].clientY) } : { x: e.clientX, y: e.clientY, d: 0 };
  if (last) { view.x += cur.x - last.x; view.y += cur.y - last.y; if (cur.d && last.d) zoomAt(cur.d / last.d, cur.x, cur.y); else schedule(); }
  last = cur; following = false;
});
const up = e => { ptrs.delete(e.pointerId); last = null; };
map.addEventListener('pointerup', up); map.addEventListener('pointercancel', up);
map.addEventListener('wheel', e => { e.preventDefault(); zoomAt(Math.exp(-e.deltaY * 0.0015), e.clientX, e.clientY); }, { passive: false });
map.addEventListener('dblclick', e => zoomAt(1.8, e.clientX, e.clientY));
addEventListener('resize', schedule);
function fit(pts, pad = 60) {
  const xs = pts.map(p => p.x), ys = pts.map(p => p.y);
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
  const top = document.body.classList.contains('going') ? 190 : 70;
  const bottom = innerWidth >= 760 ? 20 : (document.body.classList.contains('going') ? 110 : innerHeight * .45);
  const right = innerWidth >= 760 && !document.body.classList.contains('going') ? 400 : 0;
  const aw = innerWidth - right - 2 * pad, ah = innerHeight - top - bottom - pad;
  view.s = Math.min(2.2, aw / Math.max(60, x1 - x0), ah / Math.max(60, y1 - y0));
  view.x = pad + (aw - (x1 - x0) * view.s) / 2 - x0 * view.s;
  view.y = top + (ah - (y1 - y0) * view.s) / 2 - y0 * view.s; schedule();
}
view.s = Math.max(minScale(), innerHeight / H * 0.9); schedule();

// Swap in full-res map after first paint.
const full = new Image(); full.decoding = 'async'; full.src = 'img/sdsu_map.webp';
full.decode?.().then(() => { $('mapimg').src = full.src; }).catch(() => {});

/* ---------- data / routing ---------- */
const SVGNS = 'http://www.w3.org/2000/svg';
let g, steps = [], route = null, stepIdx = 0, following = true;
const fmtM = m => m < 1000 ? `${Math.round(m / 5) * 5} m` : `${(m / 1000).toFixed(2)} km`;
const fmtT = m => `${Math.max(1, Math.round(m / g.speed / 60))} min`;
const byName = new Map();

fetch('data/sdsu_graph.json').then(r => r.json()).then(data => {
  g = buildGraph(data);
  const bs = data.nodes.filter(n => n.type !== 'junction').sort((a, b) => a.name.localeCompare(b.name));
  $('places').replaceChildren(...bs.map(n => { byName.set(n.name.toLowerCase(), n); const o = document.createElement('option'); o.value = n.name; return o; }));
  const q = new URLSearchParams(location.hash.slice(1));
  $('from').value = q.get('from') || ''; $('to').value = q.get('to') || '';
  update();
});
const find = v => { v = v.trim().toLowerCase(); if (!v) return null;
  return byName.get(v) || [...byName.values()].find(n => n.name.toLowerCase().includes(v)); };
['from', 'to'].forEach(id => { $(id).addEventListener('change', update); $(id).addEventListener('input', () => byName.has($(id).value.toLowerCase()) && update()); });
$('swap').onclick = () => { [$('from').value, $('to').value] = [$('to').value, $('from').value]; update(); };
$('form').onsubmit = e => { e.preventDefault(); update(); };

function mark(n, color) { const c = document.createElementNS(SVGNS, 'circle');
  c.setAttribute('cx', n.x); c.setAttribute('cy', n.y); c.setAttribute('r', 20); c.setAttribute('fill', color); return c; }

function update() {
  if (!g) return;
  const a = find($('from').value), b = find($('to').value);
  $('marks').replaceChildren(...[a && mark(a, '#2e7d32'), b && mark(b, '#c62828')].filter(Boolean));
  route = a && b && a !== b ? astar(g, a.id, b.id) : null;
  $('summary').hidden = !route;
  if (!route) { $('routeLine').setAttribute('points', ''); $('steps').replaceChildren(); if (a || b) fit([a || b]); return; }
  history.replaceState(null, '', `#from=${encodeURIComponent(a.name)}&to=${encodeURIComponent(b.name)}`);
  const pts = route.path.map(id => g.nodes.get(id));
  $('routeLine').setAttribute('points', pts.map(p => `${p.x},${p.y}`).join(' '));
  steps = directions(g, route.path);
  const m = route.cost * g.mpp; $('dist').textContent = fmtM(m); $('time').textContent = fmtT(m);
  $('steps').replaceChildren(...steps.map(s => { const li = document.createElement('li'); li.textContent = s.text;
    const sm = document.createElement('small'); sm.textContent = fmtM(s.meters); li.append(sm); return li; }));
  fit(pts);
}

/* ---------- Go mode ---------- */
const ARROWS = { straight: '↑', 'slight left': '↖', left: '←', 'sharp left': '↙', 'slight right': '↗', right: '→', 'sharp right': '↘', arrive: '◉' };
let wake = null, watch = null, prevTheme = null;
async function keepAwake() { try { wake = await navigator.wakeLock?.request('screen'); } catch {} }
document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible' && !$('gomode').hidden) keepAwake(); });

function showStep() {
  const s = steps[stepIdx]; if (!s) return;
  $('goArrow').textContent = ARROWS[s.turn] || '↑';
  $('goText').textContent = s.text;
  $('goSub').textContent = `In ${fmtM(s.meters)} · step ${stepIdx + 1}/${steps.length}`;
  const rest = steps.slice(stepIdx).reduce((t, x) => t + x.meters, 0);
  $('goLeft').textContent = `${fmtM(rest)} · ${fmtT(rest)}`;
  $('prev').disabled = stepIdx === 0; $('next').disabled = stepIdx === steps.length - 1;
  const seg = route.path.slice(s.from, s.to + 1).map(id => g.nodes.get(id));
  fit(seg, 50);
  navigator.vibrate?.(30);
}
$('go').onclick = () => {
  if (!route) return;
  prevTheme = themes.get().id; if (themes.get().scheme !== 'dark') themes.set('contrast', false);
  document.body.classList.add('going'); $('gomode').hidden = false; stepIdx = 0; following = true;
  document.documentElement.requestFullscreen?.().catch(() => {});
  keepAwake(); showStep(); startGps();
};
$('exit').onclick = () => {
  document.body.classList.remove('going'); $('gomode').hidden = true;
  wake?.release?.(); wake = null; if (watch != null) navigator.geolocation.clearWatch(watch); watch = null;
  if (document.fullscreenElement) document.exitFullscreen?.();
  if (prevTheme) themes.set(prevTheme, false); update();
};
$('next').onclick = () => { if (stepIdx < steps.length - 1) { stepIdx++; showStep(); } };
$('prev').onclick = () => { if (stepIdx > 0) { stepIdx--; showStep(); } };
addEventListener('keydown', e => { if ($('gomode').hidden) return;
  if (e.key === 'ArrowRight') $('next').click(); if (e.key === 'ArrowLeft') $('prev').click(); if (e.key === 'Escape') $('exit').click(); });

function onPos(pos, inGo) {
  const geo = g.data.geo; if (!geo) return;
  const p = latLngToPx(geo, pos.coords.latitude, pos.coords.longitude);
  const me = $('me'); const onMap = p.x > -200 && p.y > -200 && p.x < W + 200 && p.y < H + 200;
  me.hidden = !onMap; me.setAttribute('cx', p.x); me.setAttribute('cy', p.y);
  $('goGps').textContent = onMap ? `GPS ±${Math.round(pos.coords.accuracy)} m (approx.)` : 'GPS: off campus — use › ‹';
  if (!onMap || !inGo) return;
  // Auto-advance when within ~20 m (plus accuracy slack) of the current step's target.
  const t = g.nodes.get(steps[stepIdx].at), dm = Math.hypot(p.x - t.x, p.y - t.y) * g.mpp;
  if (dm < 20 + Math.min(pos.coords.accuracy, 25) && stepIdx < steps.length - 1) { stepIdx++; showStep(); }
}
function startGps() {
  if (!navigator.geolocation || !g.data.geo) { $('goGps').textContent = 'No GPS — use › ‹'; return; }
  watch = navigator.geolocation.watchPosition(p => onPos(p, true), () => { $('goGps').textContent = 'GPS unavailable — use › ‹'; },
    { enableHighAccuracy: true, maximumAge: 5000, timeout: 20000 });
}
$('locate').onclick = () => navigator.geolocation?.getCurrentPosition(p => { onPos(p, false);
  const me = $('me'); if (!me.hidden) fit([{ x: +me.getAttribute('cx'), y: +me.getAttribute('cy') }]); else alert('You appear to be off campus.'); },
  () => alert('Location unavailable'), { enableHighAccuracy: true, timeout: 15000 });

/* ---------- offline ---------- */
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js');
  navigator.serviceWorker.addEventListener('message', e => {
    const d = e.data || {}; if (d.type !== 'progress') return;
    $('prog').hidden = false; $('prog').value = d.done / d.total;
    if (d.done === d.total) { $('offline').textContent = d.failed ? '⚠ Retry download' : '✓ Available offline'; setTimeout(() => $('prog').hidden = true, 1200); }
  });
  caches.has && caches.keys().then(k => { if (k.some(x => x.startsWith('augiewalk-'))) $('offline').textContent = '✓ Available offline'; });
}
$('offline').onclick = async () => {
  const reg = await navigator.serviceWorker?.ready; if (!reg?.active) return alert('Offline mode is not supported in this browser.');
  $('offline').textContent = 'Downloading…'; reg.active.postMessage({ type: 'download' });
  navigator.storage?.persist?.();
};
