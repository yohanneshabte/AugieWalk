/*! theme-bubbles: tiny framework-agnostic theme picker (round "bubble" swatches).
 * Theme tokens adapted from yohanneshabte/wander (src/styles.css "cream"/"lab" houses,
 * gemini branch src/index.css sage palette). MIT. */
export const WANDER_THEMES = [
  { id: 'cream', label: 'Cream', scheme: 'light', swatch: ['#f3ebdd', '#4f6b55'], vars: {
    '--color-bg': '#f3ebdd', '--color-fg': '#2c2118', '--color-surface': '#fbf6ec', '--color-surface-2': '#ebe1d0',
    '--color-muted': '#6f6456', '--color-primary': '#4f6b55', '--color-primary-fg': '#f7f3ea',
    '--color-border': '#d9cfbe', '--color-ring': '#4f6b55', '--color-accent': '#c8902b' } },
  { id: 'sage', label: 'Sage', scheme: 'light', swatch: ['#fffdf0', '#6e755b'], vars: {
    '--color-bg': '#fbf9ee', '--color-fg': '#3e2723', '--color-surface': '#ffffff', '--color-surface-2': '#d7ccc8',
    '--color-muted': '#6e675f', '--color-primary': '#6e755b', '--color-primary-fg': '#ffffff',
    '--color-border': '#b2bba0', '--color-ring': '#8f9779', '--color-accent': '#b5651d' } },
  { id: 'lab', label: 'Lab (dark)', scheme: 'dark', swatch: ['#121714', '#6b8f72'], vars: {
    '--color-bg': '#121714', '--color-fg': '#efe8d8', '--color-surface': '#1c2420', '--color-surface-2': '#27322c',
    '--color-muted': '#a39a88', '--color-primary': '#6b8f72', '--color-primary-fg': '#f4efe4',
    '--color-border': '#334038', '--color-ring': '#6b8f72', '--color-accent': '#e8b43c' } },
  { id: 'contrast', label: 'High contrast', scheme: 'dark', swatch: ['#000000', '#ffd400'], vars: {
    '--color-bg': '#000000', '--color-fg': '#ffffff', '--color-surface': '#111111', '--color-surface-2': '#222222',
    '--color-muted': '#cccccc', '--color-primary': '#ffd400', '--color-primary-fg': '#000000',
    '--color-border': '#555555', '--color-ring': '#ffd400', '--color-accent': '#00e5ff' } },
];

const KEY = 'theme-bubbles:theme';

export function applyTheme(theme, root = document.documentElement) {
  for (const [k, v] of Object.entries(theme.vars || {})) root.style.setProperty(k, v);
  root.dataset.theme = theme.id;
  root.style.colorScheme = theme.scheme || 'light';
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta && theme.vars) meta.content = theme.vars['--color-bg'];
}

/** mountThemeBubbles(el, {themes, onChange, storageKey, initial}) -> {set, get, destroy} */
export function mountThemeBubbles(el, opts = {}) {
  const themes = opts.themes || WANDER_THEMES;
  const key = opts.storageKey || KEY;
  let saved = null;
  try { saved = localStorage.getItem(key); } catch {}
  const prefersDark = typeof matchMedia === 'function' && matchMedia('(prefers-color-scheme: dark)').matches;
  let current = themes.find(t => t.id === (saved || opts.initial)) ||
    (prefersDark && themes.find(t => t.scheme === 'dark')) || themes[0];
  el.classList.add('tb');
  el.setAttribute('role', 'radiogroup');
  el.setAttribute('aria-label', opts.label || 'Theme');
  el.replaceChildren(...themes.map(t => {
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'tb-bubble'; b.dataset.id = t.id;
    b.setAttribute('role', 'radio'); b.title = b.ariaLabel = t.label;
    b.style.setProperty('--tb-a', t.swatch[0]); b.style.setProperty('--tb-b', t.swatch[1]);
    return b;
  }));
  const render = () => el.querySelectorAll('.tb-bubble').forEach(b => {
    const on = b.dataset.id === current.id;
    b.setAttribute('aria-checked', on); b.tabIndex = on ? 0 : -1;
  });
  const set = (id, persist = true) => {
    const t = themes.find(x => x.id === id); if (!t) return;
    current = t; applyTheme(t); render();
    if (persist) try { localStorage.setItem(key, id); } catch {}
    opts.onChange && opts.onChange(t);
  };
  const onClick = e => { const b = e.target.closest('.tb-bubble'); if (b) set(b.dataset.id); };
  const onKey = e => {
    const d = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key]; if (!d) return;
    e.preventDefault();
    const i = (themes.indexOf(current) + d + themes.length) % themes.length;
    set(themes[i].id); el.querySelector(`[data-id="${themes[i].id}"]`).focus();
  };
  el.addEventListener('click', onClick); el.addEventListener('keydown', onKey);
  set(current.id, false);
  return { set, get: () => current, destroy() { el.removeEventListener('click', onClick); el.removeEventListener('keydown', onKey); el.replaceChildren(); } };
}
