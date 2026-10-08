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
| Modal / alert dialog | `<dialog>` + `showModal()` (focus trap, Esc, inert background, top layer) | Opening, returning focus to trigger, preventing close on alert dialogs |
| Popover, menu surface, tooltip, toast host | `popover` attribute (`auto`/`manual`/`hint`), `popovertarget`, CSS anchor positioning with a fallback | Menu roving focus & typeahead, tooltip delay |
| Accordion / disclosure | `<details>`/`<summary>` (`name=""` for exclusive accordions) | Nothing |
| Select | `<select>` (and customizable select `appearance: base-select` where supported) | Combobox filtering |
| Date / time / color / range / number | `input[type=date|time|color|range|number]` as baseline | Custom calendar grid (enterprise) |
| Validation | Constraint validation + `:user-invalid` | Error summary aggregation, custom messages |
| Autocomplete hints | `<datalist>` | Async combobox |
| Progress / meter | `<progress>`, `<meter>` | Nothing |

When JS is needed: one small vanilla ES module per file in `js/`, progressive enhancement (page still usable without it), no dependencies, follows the WAI-ARIA APG keyboard model for its pattern.

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

## 7. Review checklist before marking done

1. `ds.py coverage <dir>` shows the file's components as `[x]`.
2. `ds.py check <dir>` has no token errors and no lint issues for this file.
3. Toggle theme (light/dark/high-contrast), density, RTL on the page — nothing breaks, nothing illegible.
4. Tab through the page: every interactive demo reachable, focus always visible.
5. If a browser tool is available (`/webapp-testing`, Chrome MCP) screenshot it; if `/accesslint` is available, run `audit_html` on the page.
