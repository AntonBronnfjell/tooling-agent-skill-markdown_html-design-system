# Conventions borrowed from mature systems

Each convention names its source and the concrete tokens/classes this skill uses. Add the tokens to `semantic.json` (and themes) and contrast pairs where noted.

## 1. Elevation = surface + shadow pairs (Atlassian)
Elevation is never a shadow alone; each level pairs a surface color with a shadow, so dark mode (where shadows barely show) still separates layers via lighter surfaces.

| Level | Surface token | Shadow token | Used by |
|---|---|---|---|
| sunken | `color.elevation.surface.sunken` | none | wells, board columns, code blocks, page canvas behind cards |
| default | `color.elevation.surface.default` (= `bg.surface`) | none | cards at rest, tables, panels |
| raised | `color.elevation.surface.raised` | `shadow.raised` | draggable/hoverable cards, sticky headers, side-panel |
| overlay | `color.elevation.surface.overlay` | `shadow.overlay` | popover, menu, toggletip, floating-panel, dialog, toast |

- Each surface also has `-hovered`/`-pressed` (or use state layers, §2). Dark theme: surfaces get progressively *lighter* per level; shadows stronger but secondary.
- Components consume only these pairs: `card.shadow → {shadow.raised}` on hover/draggable; `overlay.shadow → {shadow.overlay}`. Existing `bg.raised` aliases `elevation.surface.raised` (deprecate via `$deprecated`).
- Contrast pairs: `text.default` on every surface; `border.default` ≥ 3:1 where a surface is the only separation in high-contrast.

## 2. State layers (Material 3)
Hover/focus/pressed/dragged expressed as a translucent overlay of the content color over any container, instead of a hand-picked hover color per variant.
- Tokens: `opacity.state.hover = 0.08`, `focus = 0.10`, `pressed = 0.10`, `dragged = 0.16` (M3 values), plus `opacity.disabled.container = 0.12`, `opacity.disabled.content = 0.38`.
- Implementation: `.state-layer` mixin via pseudo-element: `::before { background: currentColor; opacity: 0 } :hover::before { opacity: var(--opacity-state-hover) }`, or `color-mix(in oklch, var(--_bg), var(--_fg) 8%)`.
- Use for ghost/subtle buttons, list rows, menu items, chips, table rows, cards. Keep explicit `bg-hover` tokens for primary/danger buttons (contrast-checked). Disabled-by-opacity text must still be identifiable; it's exempt from 4.5:1 but don't go below ~0.38.

## 3. Appearances (Fluent 2)
Separate *appearance* (how much chrome) from *intent*: `appearance: primary | secondary (default) | outline | subtle | transparent`.
- `subtle`: no bg at rest, state-layer bg on hover — toolbars, dense tables. `transparent`: no bg on hover either; only text color changes — inline actions in text.
- Class API: `.btn--subtle`, `.btn--transparent`; same for icon-button, toggle-button, menu trigger, input (`.field--filled | --outline | --underline` if needed). Map the existing `ghost` variant to `subtle` (alias, one release).

## 4. Tone × variant independence (Polaris)
Tone (meaning) and variant (emphasis) are orthogonal axes, so the matrix composes without new tokens per combo.
- Tones: `neutral | info | success | warning | critical | brand` → `feedback.*` / `action.*` tokens. Variants: `solid | soft | outline | plain`.
- Classes: `.badge--tone-critical.badge--variant-soft`, `.btn--tone-critical.btn--variant-plain` (destructive link-button), `.alert--tone-warning`. Implement with local custom properties: tone sets `--_fg/--_bg/--_border`; variant decides which to use. Every used (tone, variant) pair goes into `contrast_pairs`. Keep `button-destructive` as the documented shortcut for `tone-critical + solid`.

## 5. Fixed input widths (GOV.UK)
Field width signals the expected answer length; full-width fields for short answers mislead.
- Character widths: `.width-2ch` (day, month), `.width-3ch`, `.width-4ch` (year, CVC), `.width-5ch`, `.width-10ch` (postcode), `.width-20ch` (phone, name), `.width-30ch`. Implement as `max-inline-size: calc(Nch + padding + border)` with `inline-size: 100%` so they shrink on small screens.
- Fluid widths: `.width-full`, `.width-3-4`, `.width-2-3`, `.width-1-2`, `.width-1-3`, `.width-1-4`.
- Use in date-field, payment-card-entry, address-entry, phone-entry, number-input. Lint suggestion: inputs with `autocomplete="postal-code|bday-*|cc-csc"` should carry a width class.

## 6. `data-state` / `data-disabled` styling hooks (Radix / Headless UI)
For states that have no native attribute or ARIA equivalent, components expose data attributes instead of state classes:
- `data-state="open|closed|checked|unchecked|indeterminate|active|inactive|on|off"`, `data-disabled`, `data-highlighted` (virtual focus in listbox/combobox), `data-orientation`, `data-side="top|bottom|…"` and `data-align` (resolved placement after flipping, for arrows), `data-dragging`, `data-dirty`.
- Precedence rule: **style the native/ARIA attribute when one exists** (`[aria-expanded="true"]`, `:checked`, `[aria-selected]`, `:disabled`) — it can't drift from what AT hears; `data-*` only fills gaps (animation phases, placement, virtual highlight). Contract: `is-*` classes remain docs-only freezes.
- Framework adapters forward the same attributes so consumer CSS works identically.

## 7. Necessity indicator
Pick one and record an ADR; never mix within a form.
- **Mark optional** (GOV.UK, default for this skill): label suffix "(optional)" — most fields in good forms are required, so fewer marks. Class `.label__optional`, text in the label so it's read.
- **Mark required** (dense enterprise forms where most are optional): `*` with `aria-hidden="true"` + `required` on the input + a legend line "Fields marked * are required"; or the word "(required)". Asterisk color uses `text.default`/`feedback.danger.fg` with ≥ 4.5:1, not color-only meaning.
- Demo markers already exist: `label variant:required variant:optional`.

## 8. Density modes
- `[data-density="comfortable" (default) | "compact" | "spacious"]` on `<html>` or a subtree (data-table, board). Tokens: `density.<mode>.control-padding-x`, `cell-padding-y`, plus add `control-height` (maps to `size.control.*`: compact sm, comfortable md, spacious lg), `gap`, `row-height`.
- Components read `--_pad: var(--density-control-padding-x)` resolved by a density block that swaps the vars (one rule per mode, no per-component overrides). Touch targets stay ≥ 24px in compact (WCAG 2.5.8); compact is opt-in per surface, never forced on touch-only layouts (`@media (pointer: coarse)` resets to comfortable).
- Typography doesn't shrink with density by default (keep body ≥ 14px).

Sources: see `css-architecture.md` → Sources.
