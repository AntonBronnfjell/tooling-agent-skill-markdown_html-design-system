# Component contract (Definition of Done)

Every component in `assets/manifest.json` is "done" only when all of this holds. `ds.py coverage` machine-checks items marked ⚙; the rest you verify by reading your own output (and with `/accesslint` or a browser when available).

## Contents
1. Files & markup convention
2. The state matrix
3. CSS rules
4. JavaScript policy (native first)
5. Accessibility checklist
6. Documentation sections
7. Review checklist before marking done

## 1. Files & markup convention

```
components/<file>.html     docs/demo page (patterns go in patterns/<file>.html)   ⚙
css/components/<file>.css  styles (patterns: css/patterns/<file>.css)              ⚙
js/<file>.js               only if native HTML can't do it (see §4)
```

- `<file>` comes from the manifest `file` field. Several components share a file (all buttons live in `button`), so build per **file**, not per component — `ds.py plan` groups them.
- Each manifest component gets `<section id="<component-id>">` on its page ⚙.
- Each manifest demo marker is shown by an element with `data-demo="<marker>"` ⚙. One element may carry several markers separated by spaces: `data-demo="variant:primary state:default size:md"`.
- Class naming: block = file name or a short alias declared at the top of the CSS (`.btn`), modifiers `--variant`/`--size`, internal parts `__part`. State classes `is-hover`, `is-focus-visible`, `is-active` exist **only** so docs can freeze a state; they share the selector with the real pseudo-class:
  ```css
  .btn--primary:hover, .btn--primary.is-hover { background: var(--color-action-primary-bg-hover); }
  ```
- Real states use real attributes, not classes: `disabled`, `aria-disabled`, `aria-invalid`, `aria-expanded`, `aria-pressed`, `aria-selected`, `aria-current`, `aria-busy`, `[open]`, `:checked`, `:indeterminate`, `:user-invalid`, `:read-only`.

## 2. The state matrix

Show every state the manifest lists, and design the ones that apply even if not listed:

| Family | States |
|---|---|
| Interactive (button, link, tab, menu item, chip) | default · hover · focus-visible · active/pressed · disabled · loading (if async) · selected/current (if applicable) |
| Fields | default · hover · focus-visible · filled · placeholder · disabled · read-only · invalid (+ message) · required/optional label |
| Choice (checkbox, radio, switch) | unchecked · checked · indeterminate (checkbox) · hover · focus-visible · disabled (both values) · invalid |
| Overlays | closed (trigger) · open · with long content (scroll) · mobile layout |
| Async content | loading (skeleton/spinner) · empty · error · partial · success |
| Content variants | short/long text (truncation, wrapping), with/without icon, RTL, compact density |

Sizes: if the manifest lists `size:*`, sizes must align to `--size-control-*` so a sm button, sm input, and sm select line up in a row.

## 3. CSS rules (the PostToolUse hook lints these)

- **Cascade layers:** component CSS lives in `@layer components { … }`, pattern CSS in `@layer patterns { … }`. The bundle declares `@layer reset, tokens, base, components, patterns, utilities;`, so layer order — not specificity — decides conflicts, and app CSS (unlayered) overrides the system without `!important`. Details, `@scope`, and the progressive-enhancement matrix: `references/css-architecture.md`.

- Only `var(--…)` for color, space, radius, shadow, z-index, duration/easing. Fallbacks inside `var()` are allowed.
- No `!important`, no IDs in selectors, specificity ≤ one class + one pseudo/attribute where possible. Use `:where()` to keep defaults overridable.
- Logical properties only (`padding-inline`, `margin-block-start`, `inset-inline-end`) — RTL for free.
- Never remove focus outlines without a `:focus-visible` replacement that meets 3:1.
- Hit area ≥ 24×24px (WCAG 2.5.8); aim for `--size-touch-target` on touch-first components.
- Motion uses `--motion-*` tokens; base.css neutralizes it under `prefers-reduced-motion`. Do not animate layout properties when transform/opacity work.
- Support `forced-colors: active`: borders on things that are only distinguished by background; `CanvasText`/`Highlight` system colors where needed.
- Layout with flex/grid + `gap`; avoid margins on component roots (the parent's Stack decides spacing).
- Container queries (`@container`) for components that must adapt to their slot (card, data table toolbar).

## 4. JavaScript policy (native first)

Reach for the platform before writing JS (this is where `/ponytail` thinking pays off):

| Need | Native first | JS only for |
|---|---|---|
| Modal / alert dialog | `<dialog>` opened by an **invoker**: `<button commandfor="dlg" command="show-modal">` and `command="close"` (Baseline 2025) — focus trap, Esc, inert background, top layer, no JS | Older browsers: a 5-line fallback that wires `[commandfor]` clicks to `showModal()`; preventing close on alert dialogs |
| Popover, menu surface, tooltip, toast host | `popover` attribute (`auto`/`manual`; `hint` where supported), `commandfor` + `command="toggle-popover"` (or `popovertarget`), **CSS anchor positioning as the primary placement** with `position-try-fallbacks: --flip-block, --flip-inline` from base.css | Menu roving focus & typeahead, tooltip delay; JS positioning only as a legacy fallback |
| Accordion / disclosure | `<details>`/`<summary>` (`name=""` for exclusive accordions) | Nothing |
| Select | `<select>` (and customizable select `appearance: base-select` where supported) | Combobox filtering |
| Date / time / color / range / number | `input[type=date|time|color|range|number]` as baseline | Custom calendar grid (enterprise) |
| Validation | Constraint validation + `:user-invalid` | Error summary aggregation, custom messages |
| Autocomplete hints | `<datalist>` | Async combobox |
| Progress / meter | `<progress>`, `<meter>` | Nothing |

When JS is needed: one small vanilla ES module per file in `js/`, progressive enhancement (page still usable without it), no dependencies, follows the WAI-ARIA APG keyboard model for its pattern.

**Module contract:** export `init(root = document)` that enhances every matching element inside `root` and is safe to call twice (mark enhanced elements with `data-enhanced`). Storybook and the docs pages call `init(storyRoot)`; apps call it after rendering. No side effects on import.

**Shared behaviors first:** before overlays and composite widgets, build `js/lib/` once — `roving-focus.js` (toolbar, tabs, menu, radio-like groups), `dismiss.js` (Esc + outside click + focus return), `position.js` (anchor positioning fallback with flip), `hotkey.js` (⌘K, `/`), `live-region.js` (polite/assertive announcer). Every component module imports these instead of re-implementing them — that's what keeps 40 widgets behaving identically.

## 5. Accessibility checklist (WCAG 2.2 AA)

- Correct role from native element first; ARIA only to fill gaps. Manifest `aria` field names the APG pattern.
- Accessible name for every control (visible label > `aria-labelledby` > `aria-label`). Icon-only controls get `aria-label` and a tooltip.
- Keyboard: everything operable; order follows reading order; no positive tabindex; composite widgets (tabs, toolbar, menu, radio group, listbox, tree, grid) use roving tabindex/arrow keys per APG.
- Focus: visible (`:focus-visible`), not obscured by sticky headers (`scroll-padding-top`), returned to the trigger when an overlay closes.
- Status messages via live regions (`role=status` polite, `role=alert` assertive, only for urgent).
- Color is never the only signal (status dot + text, invalid field + icon + message).
- Contrast: text 4.5:1 (3:1 for ≥24px/19px bold), UI boundaries and focus 3:1 — add new pairs to `contrast_pairs`.
- Targets ≥ 24px; dragging has a non-drag alternative (slider keys, file input button, transfer list buttons).
- Respect `prefers-reduced-motion`, `prefers-contrast`, `forced-colors`, 200% zoom & 320px reflow.

## 6. Documentation sections ⚙

Every page contains `data-doc="usage"`, `"anatomy"`, `"examples"`, `"accessibility"`, `"tokens"`:
- **usage** — when to use / when not (and the alternative), content guidelines (labels, tone, length limits).
- **anatomy** — numbered parts.
- **examples** — the demo sections with live markup + copyable code.
- **accessibility** — role, keyboard table, ARIA attributes, focus behavior, screen-reader announcement.
- **tokens** — component tokens and the semantic tokens it consumes.

## 7. Framework adapters (when `targets` includes React/Vue/Svelte/Angular/Web Components)

The HTML/CSS system stays the source of truth; adapters render **the same markup and classes** and reuse the same CSS and `js/lib` behaviors.

- **Folder per component:** `Button/Button.tsx` · `Button.module.css` (or plain classes from the system CSS) · `Button.stories.tsx` · `Button.test.tsx` · `index.ts`. One public barrel `src/index.ts`.
- **Layers, imports only point downward:** `ui` (foundations + simple actions/display) → `base` (stateful controls, overlays, forms) → `layout` (navigation, app shell) → `sections` (patterns). Map from manifest categories: foundations/actions/most data-display → ui; forms/overlays/feedback → base; navigation → layout; patterns → sections.
- **API conventions:**
  - `variant`/`size` props use the manifest's names; state props mirror ARIA (`pressed`, `expanded`, `invalid`, `loading`).
  - Controlled **and** uncontrolled (`value`/`defaultValue`/`onValueChange`) via one `useControllableState` helper.
  - Router-agnostic links: `renderLink`/`asChild`/`as` prop so apps plug in their router's `<Link>`; export class helpers (`buttonClassName({ variant })`) for non-component use.
  - Field composition: `<Field label hint error>{(props) => <Combobox {...props} />}</Field>` so ids/`aria-describedby` are wired once.
  - Imperative APIs only where it's the natural model (`toast()`, `confirm()`), backed by a provider/host component.
  - Forward refs / expose the root element; spread remaining props onto the root; never swallow `className`/`style`.
- **Order of work per component:** test (role, keyboard, axe) → component → story. See `testing.md` and `storybook.md`.

## 8. Review checklist before marking done

1. `ds.py coverage <dir>` shows the file's components as `[x]`.
2. `ds.py check <dir>` has no token errors and no lint issues for this file.
3. Toggle theme (light/dark/high-contrast), density, RTL on the page — nothing breaks, nothing illegible.
4. Tab through the page: every interactive demo reachable, focus always visible.
5. If a browser tool is available (`/webapp-testing`, Chrome MCP) screenshot it; if `/accesslint` is available, run `audit_html` on the page.
