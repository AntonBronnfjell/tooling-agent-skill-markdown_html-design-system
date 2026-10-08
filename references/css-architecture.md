# CSS architecture

How the generated CSS is organized and which modern platform features are defaults vs progressive enhancements. Baseline data below is from `web-features` 3.40.1 (browser releases through Chrome 154 / Firefox 157 / Safari 27, Sept 2026); "newly" = works in the latest Chrome, Edge, Firefox and Safari; "widely" = newly + 30 months. Re-check with `npx web-features` or webstatus.dev before changing a default.

## Contents
- 1. Cascade layers — order instead of `!important` (Baseline widely)
- 2. `@scope` for components (Baseline newly, 2026-03)
- 3. Invoker commands — default for dialogs and popovers (Baseline newly, 2025-12)
- 4. Anchor positioning — primary path with a shared fallback set
- 5. Selectors & layout everyone may use (Baseline widely)
- 6. Progressive-enhancement matrix (limited / newly available)
- 7. Color: `light-dark()`, `color-mix()`, relative color, OKLCH/P3
- 8. Checklist for new CSS


## 1. Cascade layers — order instead of `!important` (Baseline widely)

Declare the order once, first thing in the entry stylesheet:

```css
@layer reset, tokens, base, components, patterns, utilities;
@import url("dist/tokens.css") layer(tokens);
@import url("css/base.css") layer(base);           /* reset rules may live in base.css under @layer reset */
@import url("css/components/button.css") layer(components);
@import url("css/patterns/dashboard.css") layer(patterns);
@import url("css/utilities.css") layer(utilities);
@import url("vendor/datepicker.css") layer(components.vendor);  /* third-party: contained, overridable */
```

- Later layers win regardless of specificity: a `.u-hidden` utility beats `.card .card__body button` without `!important`, and patterns override components without selector escalation. That's what lets the contract ban `!important` in components.
- **`!important` inverts layer order**: an important declaration in `reset` beats one in `utilities`. Use it only where the earliest layer must be unbeatable — `[hidden] { display: none !important }` and the reduced-motion neutralizer belong in `reset`. `.sr-only` moves to `utilities` and drops its `!important`s.
- **Unlayered CSS beats every layer.** App code that consumes the system should either stay unlayered (wins — intended for app overrides) or append `@layer app;` after `utilities`. Never leave system CSS unlayered.
- Inside a component file wrap rules in `@layer components { … }` when files are concatenated instead of imported with `layer()`. Keep `:where()` for zero-specificity defaults within a layer.

## 2. `@scope` for components (Baseline newly, 2026-03)

```css
@scope (.card) to (.card__slot) {   /* donut: don't style nested content projected into the slot */
  :scope { padding: var(--card-padding); }
  .title { font: var(--typography-h4-font-weight) var(--typography-h4-font-size)/1.3 var(--typography-h4-font-family); }
}
```

- Value: proximity (inner theme wins over outer), donut scope so a card's rules don't leak into a nested card or user content, shorter selectors.
- **Fallback is not graceful:** browsers without `@scope` drop the whole block. Until it's widely available (~2028-09) keep BEM-style class selectors (`.card__title`) as the primary mechanism and use `@scope` only for refinements (the donut lower bound) whose absence is harmless. Never rely on it alone for layout or visibility.

## 3. Invoker commands — default for dialogs and popovers (Baseline newly, 2025-12)

```html
<button commandfor="confirm" command="show-modal">Delete…</button>
<dialog id="confirm" role="alertdialog" aria-labelledby="confirm-title">
  <h2 id="confirm-title">Delete project?</h2>
  <button commandfor="confirm" command="close">Cancel</button>
</dialog>
<button commandfor="help" command="toggle-popover" aria-expanded="false">?</button>
<div id="help" popover>…</div>
```

- Built-ins: `show-modal`, `close`, `request-close` (fires `cancel`, can be prevented — *verify support per engine; fall back to `close`*), `show-popover`, `hide-popover`, `toggle-popover`; custom commands start with `--` (`command="--next-slide"`) and arrive as a `command` event on the target.
- Declarative = works before JS loads, focus returns to the invoker automatically for popovers, and fewer listeners (INP).
- **Fallback:** `js/lib/invokers.js` — if `!('command' in HTMLButtonElement.prototype)`, delegate one `click` listener on `document` that maps `command` → `showModal()/close()/togglePopover()` and dispatches a synthetic `command` event. For popovers, `popovertarget` (Baseline 2025-01) is an alternative no-JS fallback. JS still owns: `aria-expanded` sync where the platform doesn't set it, alert-dialog close prevention, returning focus for dialogs opened by custom code.
- `closedby="any"` (light dismiss for dialogs): Chrome/Firefox only, not Baseline — enhancement; keep an explicit close button.

## 4. Anchor positioning — primary path with a shared fallback set

Core properties (`anchor-name`, `position-area`, `anchor()`, `position-try-fallbacks`, `@position-try`) ship in Chrome 125–129, Firefox 147 and Safari 26, so every current engine supports the core since Jan 2026. `web-features` still marks the umbrella feature not-Baseline because of newer sub-features (`position-visibility: anchors-valid` etc. — Safari 27 only) *(uncertain: it also lists `position-anchor` as Chrome/Firefox 151 / Safari 27, likely a spec behavior change; verify before relying on implicit anchors)*.

```css
@layer components {
  [popover].is-anchored, .menu, .tooltip, .toggletip {
    position-area: block-end span-inline-end;
    position-try-fallbacks: --ds-below-end, flip-block, --ds-inline-end, flip-block flip-inline;
    margin: var(--space-1);
    max-block-size: calc(100dvh - 2 * var(--space-4));
  }
}
@position-try --ds-below-end  { position-area: block-end span-inline-start; }
@position-try --ds-inline-end { position-area: inline-end center; }
```

- One shared try-set (in `css/base.css`, `components` layer) used by popover, menu, tooltip, toggletip, combobox, date picker, hover-card, chart tooltip — identical flipping everywhere. Use logical `position-area` values so RTL works.
- Anchor names: set inline per instance (`style="anchor-name:--a-17"` + `position-anchor:--a-17`) or rely on the implicit anchor of popovers opened by an invoker.
- **Fallback:** `js/lib/position.js` runs only when `!CSS.supports('anchor-name: --a')`: computes coordinates with the same try order (below-start → below-end → above → inline-end), on open + `resize`/`scroll` (rAF-throttled). Never ship a component whose overlay is unusable without anchoring — worst case it opens centered/fixed.

## 5. Selectors & layout everyone may use (Baseline widely)

- **`:has()`** (widely 2026-06): `label.choice-card:has(:checked)`, `.form-field:has(:user-invalid)` error styling, `.card:has(.card__media)` layout switch, `body:has(dialog[open]) { overflow: hidden }`. Keep `:has()` selectors shallow and anchored to a class (perf) and never inside `:has()` that matches `:hover` on large lists.
- **Nesting** (widely 2026-06): one level for states/parts (`&:hover`, `&[aria-expanded="true"]`, `& .btn__icon`), max 3 levels; nested selectors keep their own specificity (`:is()` semantics — `&` in a list becomes `:is(a, b)`), so don't nest IDs or heavy lists.
- **Subgrid** (widely 2026-03): card grids aligning header/body/footer rows across cards (`grid-template-rows: subgrid; grid-row: span 3`), form-layout label/control columns, description lists, data-table toolbars aligned to columns.
- Container queries (widely 2025-08) for slot-adaptive components (already in the contract).

## 6. Progressive-enhancement matrix (limited / newly available)

Rule for every row: **never rely on it alone** — the fallback must deliver the same task, only less polished. Feature-detect in CSS with `@supports`, in JS with property checks; never browser sniff.

| Feature | Status (web-features 3.40.1) | Use for | Required fallback |
|---|---|---|---|
| `interestfor` (interest invokers) | Limited — Chrome/Edge 142 only | Hover/focus-triggered tooltips & hover-cards | `js/lib/tooltip.js` (hover+focus delay, Esc) with `aria-describedby`; content also reachable elsewhere |
| `popover="hint"` | Limited — Chrome 151, Firefox 153, no Safari | Tooltips that don't close auto popovers | `popover="manual"` managed by tooltip JS |
| `container-type: scroll-state` / `scroll-state()` queries | Limited — Chrome 133 | Stuck headers shadow, snapped-slide styling, scroll hints | Static shadow, or IntersectionObserver sentinel toggling a class |
| `::scroll-button()` / `::scroll-marker` | Limited — Chrome 135 | Carousel prev/next and dots without JS | Real `<button>`s + carousel JS (APG carousel). Don't ship both visible — hide JS controls under `@supports selector(::scroll-marker)` only if the CSS ones meet the APG spec *(uncertain: a11y of generated markers is still evolving — prefer real buttons)* |
| `if()` | Limited — Chrome 137 | Inline conditional values (density/size from a custom property) | Modifier classes / data attributes (`[data-density=compact]`) |
| `reading-flow` | Limited — Chrome 137 | Tab order following visual order in reordered grid/flex | Make DOM order match visual order (the real fix); avoid `order`/`grid-auto-flow: dense` on interactive content |
| `contrast-color()` | Newly 2026-04 (Chrome 147, Firefox 146, Safari 26) | Auto fg on user-chosen colors (tags, avatars) | Explicit fg token per bg in `contrast_pairs`; it only picks black/white and doesn't guarantee 4.5:1 for mid-tones |
| Container style queries (`@container style(--x: y)`) | Newly 2026-05 (Firefox 151 last) | Variant switching from a custom property on an ancestor | Modifier classes; treat as refinement |
| Scroll-driven animations (`animation-timeline`) | Limited — Chrome 115, Safari 26, no Firefox | Reading progress bar, reveal-on-scroll | No animation (content fully visible by default); wrap in `@supports (animation-timeline: scroll())` **and** `prefers-reduced-motion: no-preference` |
| Cross-document view transitions (`@view-transition { navigation: auto }`) | Limited — Chrome 126, Safari 18.2, no Firefox | MPA page transitions in docs/patterns | Normal navigation (it's an enhancement by design); same-document `startViewTransition` is newly 2025-10 |
| `field-sizing: content` | Newly 2026-06 | Auto-grow textarea/composer | `rows` + small resize script or `resize: vertical` |
| Customizable `<select>` (`appearance: base-select`) | Limited — Chrome 135, Safari 27 | Styled select pickers | Native styled `<select>` |
| `interpolate-size` / `::details-content` | Chrome only / newly 2025-09 | Accordion height animation | Instant open (no animation) |

## 7. Color: `light-dark()`, `color-mix()`, relative color, OKLCH/P3

- **Themes stay attribute-driven** (`[data-theme]`, `.theme-x` from `ds.py build`) because high-contrast and brand themes can't be expressed with two values. `light-dark()` (newly 2024-05; widely 2026-11) is for **component-local** pairs that don't deserve a semantic token and for consumers: it follows `color-scheme`, which every theme sets — so `.theme-dark` subtrees flip it too. *(Option for ds.py: emit light/dark semantic pairs as `light-dark()` in `:root` and keep explicit overrides only for high-contrast — evaluate; contrast checking must then resolve both branches.)*
- **`color-mix()`** (widely): derive non-text states from tokens — hover/pressed tints, state layers (see conventions.md), translucent overlays: `background: color-mix(in oklch, var(--color-action-primary-bg) 88%, var(--color-text-default))`. Mix in `oklch`/`oklab` for perceptually even steps.
- **Relative color** (newly 2024-09): `oklch(from var(--color-selected-bg) l c h / 0.12)` for alpha variants and lightness nudges.
- **Contrast rule:** computed colors are invisible to `ds.py check`. Any derived color used for **text or a 3:1 boundary** must be precomputed into a token (hex) and listed in `contrast_pairs`; runtime mixing is only for decorative fills, state overlays and shadows.
- **OKLCH for authoring** (widely): generate primitive ramps in OKLCH (even lightness steps, constant hue), export hex sRGB for tokens (the contrast checker reads hex). **P3:** optionally add wide-gamut primitives behind `@media (color-gamut: p3) { :root { --color-blue-600: oklch(55% 0.24 262); } }`; semantic tokens alias primitives so everything upgrades. Contrast is verified on the sRGB values — keep P3 variants within ±0.01 L of them so ratios hold. *(DTCG 2025.10 color objects support `colorSpace` — ds.py currently expects hex; uncertain whether to adopt.)*
- Forced colors: none of these survive `forced-colors: active`; system colors take over — keep borders on anything distinguished only by fill.

## 8. Checklist for new CSS
1. File is in the right layer; no `!important` outside `reset`/`utilities`.
2. Overlays open with `command`/`commandfor` (or `popovertarget`), position with the shared try-set, and still work with the JS fallbacks forced on (`?nofeatures` docs toggle sets `data-force-fallbacks`).
3. Every row of §6 used by the component has its fallback demoed on the page.
4. Derived colors used for text/boundaries are tokens with contrast pairs.

## Sources

Browser support (all Baseline statuses in css-architecture.md / performance.md / specs.md)
- web-features 3.40.1 data (`https://unpkg.com/web-features/data.json`, downloaded 2026-10-08; browser releases through Chrome 154, Firefox 157, Safari 27) — https://github.com/web-platform-dx/web-features
- Baseline definitions — https://web.dev/baseline · status dashboard https://webstatus.dev
- Can I use — https://caniuse.com (cross-check)
- MDN: Cascade layers, `@scope`, invoker commands (`command`/`commandfor`), CSS anchor positioning & `@position-try`, `:has()`, nesting, subgrid, `light-dark()`, `color-mix()`, relative colors, `content-visibility`, `@font-face` descriptors (`size-adjust`, `ascent-override`), Custom Highlight API, Navigation API — https://developer.mozilla.org

Accessibility & patterns
- WAI-ARIA Authoring Practices Guide: Window Splitter, Menubar, Menu Button, Tree View, Grid, Listbox, Combobox, Toolbar, Dialog, Feed, Carousel — https://www.w3.org/WAI/ARIA/apg/patterns/
- WCAG 2.2 (1.4.11 non-text contrast, 1.4.13 content on hover/focus, 2.1.2 no keyboard trap, 2.2.1 timing adjustable, 2.4.11 focus not obscured, 2.5.7 dragging movements, 2.5.8 target size) — https://www.w3.org/TR/WCAG22/
- GOV.UK Design System patterns & components: question pages, check answers, confirmation pages, start using a service, task list, step by step navigation, service unavailable pages, exit this page, addresses, names, telephone numbers, payment card details, dates (memorable date), complete multiple tasks, error summary, input widths, "mark optional fields" — https://design-system.service.gov.uk
- HMRC timeout dialog (session-timeout reference) — https://design.tax.service.gov.uk/hmrc-design-patterns/
- Heydon Pickering, Inclusive Components: Tooltips & Toggletips; Cards; Toggle buttons — https://inclusive-components.design
- Salesforce / Atlassian / Adobe drag-and-drop accessibility guidance (keyboard grab mode, announcements) — https://atlassian.design/components/pragmatic-drag-and-drop/ · https://react-spectrum.adobe.com/blog/drag-and-drop.html

Design-system conventions
- Atlassian Design System — elevation (surface + shadow tokens) — https://atlassian.design/foundations/elevation
- Material Design 3 — state layers & opacity values — https://m3.material.io/foundations/interaction/states/state-layers
- Fluent 2 — button appearances (subtle, transparent, outline) — https://fluent2.microsoft.design/components/web/react/core/button/usage
- Shopify Polaris — tone & variant props (Badge, Button, Text) — https://polaris-react.shopify.com
- Radix Primitives — `data-state`/`data-disabled`/`data-side` styling attributes — https://www.radix-ui.com/primitives/docs/guides/styling
- AWS Cloudscape — attribute editor, app layout split/side panels, result/status patterns — https://cloudscape.design
- Carbon — data visualization (legends, tooltips, axes, color order), selection / batch actions — https://carbondesignsystem.com/data-visualization/
- Ant Design — Result, TreeSelect, Splitter; Spectrum — Toggletip / ContextualHelp, Meter — https://ant.design · https://spectrum.adobe.com

Data visualization
- WCAG non-text contrast applied to charts; Chartability heuristics — https://chartability.fizz.studio
- Datawrapper / Highcharts accessibility guidance (direct labels, patterns, data-table fallback) — https://www.highcharts.com/docs/accessibility/accessibility-module

Performance
- web.dev: INP, LCP, CLS thresholds; Optimize long tasks (`scheduler.yield`); `content-visibility`; font fallbacks with `size-adjust` — https://web.dev/articles/inp · https://web.dev/articles/optimize-long-tasks · https://web.dev/articles/content-visibility · https://web.dev/articles/css-size-adjust
- `web-vitals` library (attribution build) — https://github.com/GoogleChrome/web-vitals
- Lighthouse CI — https://github.com/GoogleChrome/lighthouse-ci
- Fontaine / Capsize (fallback metric generation) — https://github.com/unjs/fontaine · https://seek-oss.github.io/capsize/

Notes on certainty
- Baseline facts were read from web-features data, not from web.dev pages directly; web.dev/caniuse were not re-fetched in this pass. Two anomalies flagged inline: `position-anchor` listed as Chrome/Firefox 151 + Safari 27 (possibly a behavior change), and `popover="hint"` listed as Chrome 151 (I recalled an earlier Chrome ship around 133 — unverified, possibly reverted or re-specced).
- Vendor-specific numbers (M3 opacities, GOV.UK width classes) are from memory of those systems; verify against the linked pages before publishing.

## Bleeding-edge syntax and build tools
Unrecognized **at-rules or functions** (for example `@container anchored(...)`, very new `@function`/`if()` forms) can make build-time CSS parsers such as lightningcss (used by Vite, so Storybook builds and many app bundlers) fail the **whole build**, not just skip the rule. Browsers ignore what they don't understand; minifiers don't. Before shipping a not-yet-Baseline feature, check that `npx storybook build` (or the consuming app's build) still passes. If it doesn't, leave the feature out or move it to a separate, unminified stylesheet. Unknown *properties and values* (`position-try-fallbacks`, `interpolate-size`) are generally passed through safely.

