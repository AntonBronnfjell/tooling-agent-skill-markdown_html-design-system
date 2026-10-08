# Performance

A design system sets the performance floor for every product built on it. Budgets are checked on the docs/pattern pages, which stand in for real screens.

## Budgets (p75, mobile, 4× CPU throttle)
| Metric | Budget | Owner in the system |
|---|---|---|
| INP | ≤ 200 ms (aim ≤ 100 ms per component interaction) | `js/` modules, overlays, data-table, sortable, formatters |
| LCP | ≤ 2.5 s | image, hero, fonts |
| CLS | ≤ 0.1 | image dims, skeletons that match geometry, fonts, toasts/banners that push content |
| CSS | ≤ 60 kB gz for all components; per-file CSS importable | layers + per-file `@import` |
| JS | ≤ 5 kB gz per `js/<file>.js`, ≤ 25 kB gz for `js/lib/` total; zero dependencies | component-contract §4 |

## INP: no long tasks in `js/`
- Every event handler does the visible update first, then defers the rest: `await yieldToMain()` before analytics, persistence, re-sorting, network.
  ```js
  export const yieldToMain = () =>
    globalThis.scheduler?.yield ? scheduler.yield() : new Promise((r) => setTimeout(r, 0));
  ```
  `scheduler.yield()` ships in Chrome 129 and Firefox 142, not Safari (not Baseline) — the fallback is mandatory.
- No task > 50 ms on a mid-range phone. Chunk loops over large collections (select-all on 10k rows, filtering, formatting) into batches with a yield between them, or move them to a Worker.
- Event delegation: one listener per root (`init(root)`), not one per row/option. Passive `pointermove`/`touchmove`/`wheel` listeners; throttle pointer-driven layout writes to `requestAnimationFrame` (splitter, sortable, floating-panel).
- Never read layout (`getBoundingClientRect`, `offsetWidth`) after writing styles in the same frame (layout thrash). Batch reads, then writes.
- Prefer platform features that move work off JS: invoker commands, `popover`, `<dialog>`, `<details>`, anchor positioning (see css-architecture.md).
- `beforeunload` only while a form is dirty; `unload` never (both hurt bfcache).
- Debounce input-driven work (combobox, search) at 150–250 ms and abort stale requests with `AbortController`.

## Long lists and long documents
- `content-visibility: auto` + `contain-intrinsic-size: auto 20rem` on off-screen sections of long pages (docs pages, settings, feed items, comment threads, board columns). Baseline newly available 2025-09 (Safari 26); in older browsers it is simply ignored. Content stays in the accessibility tree and find-in-page.
- Don't put it on elements whose size you measure (sticky headers, anchors of open popovers) or on the first screen (it can delay LCP).
- Lists beyond ~500 rendered rows: paginate or "Load more" first; virtualize only in data-table/tree enterprise variants, keeping `aria-rowcount`/`aria-rowindex` (or `aria-setsize`/`aria-posinset`) correct and the focused row mounted.
- Skeletons render the final geometry so swapping in content causes no shift.

## Fonts
- Self-host WOFF2, subset (Latin + needed ranges via `unicode-range`), ≤ 2 families × 3 weights or one variable font.
- `<link rel="preload" as="font" type="font/woff2" href="…" crossorigin>` for the one or two faces used above the fold only (body regular + heading). Preloading everything delays LCP.
- `font-display: swap` for text faces (`optional` for a strict CLS budget on repeat visits); icon/sprite SVG instead of icon fonts.
- Metric-matched fallback so the swap doesn't shift layout:
  ```css
  @font-face { font-family: "Inter Fallback"; src: local("Arial");
    size-adjust: 107%; ascent-override: 90%; descent-override: 22%; line-gap-override: 0%; }
  --font-family-sans: "Inter", "Inter Fallback", system-ui, sans-serif;
  ```
  Compute values with Fontaine/Capsize (or Next.js `next/font`). `size-adjust` works in all engines; `ascent/descent/line-gap-override` are Chrome/Firefox only (not Safari) *(per web-features 3.40.1)* — Safari users get a smaller residual shift. `font-size-adjust` (Baseline 2024-07) is an alternative for x-height matching.

## Images
- Always `width`/`height` attributes (or `aspect-ratio`); `srcset` + `sizes`; AVIF/WebP via `<picture>` with JPEG/PNG fallback.
- LCP image: `fetchpriority="high"`, never `loading="lazy"`, no CSS background for it. Everything below the fold: `loading="lazy" decoding="async"`.
- SVG icons via sprite; inline only small decorative SVGs. Avatars/thumbnails served at 2× display size max.

## Measuring
- **Lighthouse CI** (`@lhci/cli`) on the built docs pages and pattern pages in CI: assert LCP, CLS, TBT (lab proxy for INP; TBT ≤ 200 ms), and byte budgets (`budgets.json`). Run mobile preset; 3 runs, median.
- **Playwright** for interaction latency: emulate a slow CPU via CDP (`Emulation.setCPUThrottlingRate { rate: 4 }`), inject the `web-vitals` library (`onINP` with `reportAllChanges`, attribution build) or a `PerformanceObserver({ type: 'event', durationThreshold: 16 })`, drive the interaction (open menu, select-all, sort, drag via keyboard), and assert the max event duration < 200 ms. Event Timing is Baseline newly 2025-12; run perf tests in Chromium. Also observe `longtask` (Chromium) to assert no task > 50 ms during the interaction.
- **CLS in Playwright:** `PerformanceObserver({ type: 'layout-shift', buffered: true })` while loading each page, including fonts loading and toasts appearing.
- Field data (in consuming apps): `web-vitals` → analytics; the system documents the attribution fields to log (`interactionTarget`, `longAnimationFrameEntries`, Chromium only).
- Run perf tests with `data-reduced-motion` off **and** on; animations must not be the long task.

Sources: see `css-architecture.md` → Sources.
