# theme-bubbles

Tiny (≈2 KB) framework-agnostic theme picker: a row of round "bubble" swatches that
apply a set of CSS custom properties to `<html>`, persist the choice to `localStorage`,
and respect `prefers-color-scheme` on first visit. Keyboard accessible (radiogroup, arrow keys).

```html
<link rel="stylesheet" href="lib/theme-bubbles/theme-bubbles.css">
<div id="themes"></div>
<script type="module">
  import { mountThemeBubbles, WANDER_THEMES } from './lib/theme-bubbles/theme-bubbles.js';
  const picker = mountThemeBubbles(document.getElementById('themes'), {
    themes: WANDER_THEMES,          // [{id,label,scheme:'light'|'dark',swatch:[a,b],vars:{'--color-bg':..}}]
    onChange: t => console.log(t.id),
    storageKey: 'my-app:theme',     // optional
  });
  picker.set('lab');                // programmatic
</script>
```

API: `mountThemeBubbles(el, opts) → { set(id), get(), destroy() }`, `applyTheme(theme)`, `WANDER_THEMES`.
Tokens exposed: `--color-bg, --color-fg, --color-surface, --color-surface-2, --color-muted,
--color-primary, --color-primary-fg, --color-border, --color-ring, --color-accent`.
Also updates `<meta name="theme-color">` and `color-scheme`.

## Credit
Theme tokens come from [yohanneshabte/wander](https://github.com/yohanneshabte/wander):
`src/styles.css` (the `cream` default `@theme` and `html[data-house="lab"]` dark palette, applied by
`src/components/house-theme.tsx`, theme ids from `src/lib/platform/types.ts`) and the `gemini` branch
`src/index.css` (sage / warm-stone / dark-wood palette). wander has no standalone bubble-picker
component, so the picker UI itself is new; the `contrast` theme was added for AugieWalk Go mode.
