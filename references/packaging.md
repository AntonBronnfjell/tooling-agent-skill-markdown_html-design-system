# Packaging & distribution

A design system nobody can install is a style guide. `ds.py package <dir>` turns the folder into an npm package; `ds.py ci` adds the release pipeline.

## What the package exposes (`ds.py package`)
| Export | File | Use |
|---|---|---|
| `.` / `./ds.css` | `dist/ds.css` | Everything: tokens + base + all components |
| `./tokens.css` | `dist/tokens.css` | Tokens and themes only (for apps styling their own components) |
| `./tokens.json` · `./tokens.scss` | `dist/tokens.*` | Build-time values: JS animations, media queries (`@include up(md)`), charts |
| `./css/*` | `css/components/*.css` | Per-component CSS for apps that want only a few components (still needs tokens + base) |
| `./js/*` | `js/*.js` | Progressive-enhancement modules (`theme.js`, menus, combobox…) — each exports `init(root)` |
| `./tokens/*` | DTCG sources | Style Dictionary / Tokens Studio / Figma variables |
| `./DESIGN.md` | contract | Shipped so consuming apps and their AI agents can read the rules |

`sideEffects: ["*.css"]` keeps bundlers from tree-shaking CSS imports; `files` whitelists what's published. `prepack` rebuilds `dist/` and `DESIGN.md` so a publish can't ship stale tokens.

## Fonts
Self-host instead of a third-party CDN (privacy, performance, offline): put WOFF2 files in `fonts/`, declare `@font-face` in `css/base.css` (or `css/fonts.css`) with relative URLs, `font-display: swap`, and a `unicode-range` subset per script (Latin first; add others only for supported locales). Variable fonts cut requests. Storybook serves `fonts/` at `/fonts` automatically. For open fonts, `@fontsource/*` packages are the easy source — copy the needed files at build time rather than depending on them at runtime.

## Framework packages (React/Vue/Svelte/Angular targets)
- Library build (Vite library mode / tsup / ng-packagr): ESM (+ CJS if consumers need it), one CSS file (`cssCodeSplit: false`) or CSS per component, types rolled into a single `.d.ts`.
- Framework and heavy libs (React, animation libs) are **peerDependencies**, never bundled.
- Exports map: `.` (components), `./styles` (CSS), `./tokens` (SCSS/JSON). Mark CSS as side effects.
- Ship a `css.d.ts` / module declaration if consumers import CSS from TS.
- A small playground app (Vite dev server importing from `src/`) for manual testing next to Storybook.

## Versioning & release
- semver per `governance.md`; bump `version` in `package.json` in the PR. CI publishes **only if that version isn't on the registry yet** and creates the `vX.Y.Z` tag itself — never tag by hand, never publish from laptops.
- Every major release has a migration section (renamed tokens/classes/props, removed components, before → after snippets) and keeps deprecated token aliases (`"$deprecated"` in token JSON) for one major version.
- Private registries: set `publishConfig.registry` and `access: restricted`; the CI templates read `NPM_TOKEN`.
