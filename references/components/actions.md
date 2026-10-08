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

## theme-toggle
- Ships with `js/theme.js` (`initTheme`, `setTheme`, `getTheme`, `onThemeChange`, `init` for `[data-theme-cycle]`). Two forms: a cycling `<button>` labelled "Theme: dark" (name updates with the state), or a radio group (System / Light / Dark) in settings. "System" is the default and follows `prefers-color-scheme`.
- The page `<head>` carries the no-flash inline snippet from `theme.js` so the first paint already uses the saved theme. Storage access is wrapped in try/catch (private mode), and tabs stay in sync via the `storage` event.

Files added: `selection-action-bar`, `overflow-menu`.

## selection-action-bar
- Appears when ≥ 1 item is selected in a table/list/card collection; replaces or overlays the toolbar. Anatomy: count ("3 selected" in an `<output>`/`role="status"`), "Select all 248" (select-all-matching escape hatch for paged data), bulk actions (buttons; destructive last + confirm), overflow menu, "Clear selection" button.
- `role="toolbar"` + `aria-label="Bulk actions"` with roving focus (see toolbar). Count changes announced politely and debounced (not per checkbox in a shift-range).
- Placement: sticky top of the collection or floating bottom (`variant:sticky-bottom`, safe-area insets, page gets bottom padding — WCAG 2.4.11 focus not obscured).
- Don't move focus when it appears. On "Clear selection", return focus to the collection.
- Pitfalls: disabled actions should explain why (`aria-disabled` + toggletip); actions that only apply to some selected items say so ("Archive 2 of 3 — 1 is locked").

## overflow-menu (kebab, Priority+)
- Kebab: icon button `aria-label="More actions for <item>"` (always include the item context in lists), `aria-haspopup="menu" aria-expanded` → menu per the menu spec. Prefer three vertical dots for row actions, horizontal for toolbars; pick one and ADR it.
- Priority+ (toolbars, tabs, nav): items render inline in priority order; a `ResizeObserver` on the container moves trailing items into a "More" menu when they don't fit. Overflowed items keep their accessible name and state (pressed/current). Never overflow the primary action.
- CSS-first option: for nav, horizontal scroll with scroll-snap + fade masks needs no JS; use Priority+ only when hidden items must stay discoverable.
- Pitfalls: oscillation at threshold widths (hysteresis: measure with the "More" button included); focus loss when the focused item moves into the menu (move focus to "More"); hidden items still in tab order (`hidden` them inline).
