const VERSION = 'v1';
const CACHE = `augiewalk-${VERSION}`;
const ASSETS = ['./', 'index.html', 'app.css', 'app.js', 'route.js', 'manifest.webmanifest',
  'lib/theme-bubbles/theme-bubbles.js', 'lib/theme-bubbles/theme-bubbles.css',
  'data/sdsu_graph.json', 'img/sdsu_map_sm.webp', 'img/sdsu_map.webp',
  'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png'];

async function precache(report) {
  const c = await caches.open(CACHE); let done = 0, failed = 0;
  await Promise.all(ASSETS.map(async u => {
    try { const r = await fetch(u, { cache: 'reload' }); if (!r.ok) throw 0; await c.put(u, r); } catch { failed++; }
    report && report({ type: 'progress', done: ++done, total: ASSETS.length, failed });
  }));
  return failed;
}
self.addEventListener('install', e => e.waitUntil(precache().then(() => self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(
  caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('augiewalk-') && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim())));
self.addEventListener('message', e => {
  if (e.data?.type === 'download') e.waitUntil(precache(m => e.source.postMessage(m)));
});
// Cache-first; fall back to network and cache the result; navigation falls back to the shell.
self.addEventListener('fetch', e => {
  const req = e.request; if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  e.respondWith(caches.match(req, { ignoreSearch: true }).then(hit => hit || fetch(req).then(r => {
    if (r.ok) { const copy = r.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
    return r;
  }).catch(() => req.mode === 'navigate' ? caches.match('index.html') : Response.error())));
});
