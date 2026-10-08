# Actions & CTAs — specs

Files: `button`, `icon-button`, `link`, `button-group`, `toggle-button`, `segmented-control`, `split-button`, `menu`, `fab`, `close-button`, `copy-button`, `toolbar`.

## button (primary, secondary, tertiary/ghost, destructive, with icon)
- `<button type="button|submit">`. Anatomy: container, label, optional leading/trailing icon (`aria-hidden`), optional inline spinner.
- Variants map 1:1 to `color.action.{primary,secondary,ghost,danger}.*`. One primary per region; destructive actions confirm via alert dialog or offer undo.
- Sizes sm/md/lg → `--button-height-*` = `--size-control-*`; full-width variant for mobile forms.
- States: hover/active via tokens; `disabled` attribute (removes from tab order) vs `aria-disabled="true"` (stays focusable, explains why via tooltip) — document when to use each.
- Loading: keep width stable (spinner overlays label, label `visibility:hidden`), set `aria-busy="true"` and keep the accessible name; prevent double submit.
- Labels: verb-first, sentence case, ≤ 3 words where possible.
- A `<a class="btn">` is allowed only for navigation that should look like a button.

## icon-button
- `<button type="button" aria-label="Settings">` + icon `aria-hidden`. Square and circle; sizes match buttons. Always pair with a tooltip showing the same label. Toggle-type icon buttons use `aria-pressed`.

## link
- `<a href>` only. Inline links underlined (never color-only); standalone link may drop underline but needs another cue (icon/weight). External: `target="_blank"` only when necessary, with visually hidden "(opens in new tab)" + icon, `rel="noopener"`. Visited state for content sites.

## button-group
- `role="group"` + `aria-label`. Attached variant collapses inner radii and borders (`:first-child`/`:last-child` logical radii). Not for single-select toggles — that's segmented control.

## toggle-button
- `aria-pressed="true|false"` on a `<button>`; label stays constant ("Bold"), state shown visually. Don't change the label and the pressed state simultaneously.

## segmented-control
- Implement as radio group: `<fieldset>` + visually hidden radios + styled labels. Arrow keys move selection natively. For switching views; 2–5 options; equal widths.

## split-button
- Two buttons in a group: primary action + `aria-haspopup="menu" aria-expanded` chevron button labeled "More save options". Menu per `menu` spec.

## menu (menu button / dropdown menu, context menu)
- Trigger `<button aria-haspopup="menu" aria-expanded aria-controls>`; surface `[popover]` with `role="menu"`, items `role="menuitem"` / `menuitemcheckbox` / `menuitemradio`, groups with `role="group"` + separators.
- Keyboard (APG menu): Enter/Space/↓ opens & focuses first item, ↑ last; ↑/↓ move (wrap), Home/End, typeahead, Esc closes and returns focus, Tab closes. Submenu → / ←.
- Items: leading icon, label, shortcut hint (`kbd`), check mark; disabled items stay focusable with `aria-disabled`. Destructive item colored + confirm.
- Position with CSS anchor positioning (`position-anchor`, `position-try-fallbacks: flip-block`) and a JS fallback.
- Context menu: `contextmenu` event + Shift+F10 / Menu key equivalent; same menu markup.

## fab (enterprise)
- Fixed `inset-block-end/inset-inline-end` with safe-area insets; `z-index: var(--z-fixed)`; regular (icon + aria-label) and extended (icon + text). One per screen; must not cover content at 320px — add bottom padding to the page.

## close-button
- Icon button `aria-label="Close"` (or "Dismiss notification"), consistent placement (top inline-end) across modal, drawer, toast, alert, popover.

## copy-button
- Uses `navigator.clipboard.writeText`; copied state swaps icon + text for ~2s and announces via `role="status"` live region ("Copied"). Fallback: select text.

## toolbar
- `role="toolbar"` + `aria-label`; roving tabindex — one Tab stop, arrows move between controls; groups separated by `role="separator"`. Overflow → "More" menu.
