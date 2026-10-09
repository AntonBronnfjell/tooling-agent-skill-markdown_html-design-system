# Testing & accessibility automation

`ds.py check --strict` guarantees structure (tokens, contrast, lint, coverage). Behavior and real accessibility need tests in a browser. Pick the layer that matches the project's targets.

## 1. Storybook (all targets) — cheapest wide net
`ds.py storybook` configures `@storybook/addon-a11y` with `parameters.a11y.test = 'error'`: axe runs on every story (every state of every component) in the Accessibility panel. To fail CI, add Storybook's Vitest integration (`npx storybook add @storybook/addon-vitest`, then `npx vitest --project=storybook`) — stories become tests and a11y violations fail them. Run it in the four combinations that matter: light, dark, high-contrast, RTL (globals per test or per story `globals`).

## 2. Static HTML system — Playwright + axe

**Generate it:** `ds.py playwright <dir>` writes `playwright.config.mjs` and `tests/design-system.spec.mjs` (yours to edit; only `--force` regenerates). It covers every docs page × every theme × desktop and mobile, plus RTL, with:
- visual regression via `toHaveScreenshot()`, baselines committed in `tests/__screenshots__`;
- axe accessibility, failing with the element and measured contrast;
- a keyboard check that every Tab stop shows a visible focus indicator.

The web server is `ds.py serve`, so there's no app to run. It's free and local: create baselines on the same OS as CI (the Playwright Docker image), because font rendering differs per OS. Lost Pixel's open-source mode and BackstopJS are no longer actively maintained; Argos is an open-source alternative if you want hosted review.

The hand-written equivalent, for reference:
For each `components/*.html` and `patterns/*.html` page, in each theme:

```js
// tests/a11y.spec.js  (npm i -D @playwright/test @axe-core/playwright)
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { readdirSync } from 'node:fs';
const pages = ['components', 'patterns'].flatMap((d) => readdirSync(d).filter((f) => f.endsWith('.html')).map((f) => `${d}/${f}`));
for (const theme of ['light', 'dark', 'high-contrast']) for (const page of pages) {
  test(`${page} [${theme}]`, async ({ page: p }) => {
    await p.goto(`http://127.0.0.1:8000/${page}`);           // `ds.py serve .` in webServer config
    await p.evaluate((t) => (document.documentElement.dataset.theme = t), theme);
    const { violations } = await new AxeBuilder({ page: p }).disableRules(['region']).analyze();
    expect(violations).toEqual([]);
  });
}
```

Add keyboard tests for composite widgets straight from each page's accessibility keyboard table (Tab reaches it once, arrows move, Esc closes and returns focus).

## 3. Framework adapters (React/Vue/Svelte/Angular) — unit + a11y
Per component: `Name.test.tsx` next to the component, Testing Library + `jest-axe`/`vitest-axe`:
- Assert **roles and names** (`getByRole('button', { name: 'Save' })`), not classes.
- Assert **states** through ARIA (`aria-pressed`, `aria-expanded`, `aria-busy`, `aria-invalid`) and **keyboard** (`user.keyboard('{ArrowDown}')`).
- `expect(await axe(container)).toHaveNoViolations()` per variant (disable `region` for isolated components).
- Shared setup shims for jsdom: `matchMedia`, `ResizeObserver`, `IntersectionObserver`, `HTMLDialogElement.showModal`, `offsetParent`; mock animation libraries so animations resolve instantly.
- Order of work per component: test → component → story. The test encodes the contract from `component-contract.md`; the story documents it.

## 4. Performance budgets
Interaction to Next Paint (INP) ≤ 200 ms on mid-range mobile, no long tasks (> 50 ms) in `js/` modules, `content-visibility: auto` for long lists and docs pages, metric-matched font fallbacks. Measurement recipes (Playwright traces, Lighthouse CI): `references/performance.md`.

## 5. Visual regression (optional)
Chromatic, Playwright `toHaveScreenshot()`, or Storybook's visual tests across themes and viewports. Gate only on reviewed baselines; skip shimmer/animated stories or force reduced motion.

## 6. Native apps — snapshot parity with the web
`ds.py mobile scaffold` writes snapshot tests per platform (swift-snapshot-testing, Roborazzi + Robolectric, Flutter `matchesGoldenFile`, a react-native-view-shot capture screen) that render each component at the web reference size, with the web copy, named `<file>--<demo>--<theme>.png`. Run them, then `ds.py mobile verify <ds> --native <folder>`: per-snapshot drift %, size check, diff images and a report; exit 1 on drift, so it can gate CI. Use the real fonts and a fixed simulator/emulator image. Details: `references/mobile.md`.

## 7. What CI runs (`ds.py ci` generates the first two)
1. `ds.py check . --strict` 2. Storybook build (+ Vitest a11y if configured) 3. Playwright/axe or unit tests 4. publish.
