# Overlays & feedback — specs

Overlay files: `modal` (modal, alert-dialog), `drawer` (drawer, bottom-sheet), `popover`, `tooltip`, `menu` (context menu — see actions.md), `coachmark`, `lightbox`.
Feedback files: `alert` (alert, callout, global-banner), `toast`, `progress` (progress-bar, meter), `spinner` (spinner, inline-spinner), `skeleton`, `notification-center`.

## Layering
All overlays use the browser **top layer** (`dialog.showModal()` / `popover`) so z-index wars disappear; tokens `--z-*` remain for non-top-layer fixed elements (sticky headers, FAB). Backdrop via `::backdrop` with `--color-bg-overlay`. Entry/exit animations with `@starting-style` + `transition-behavior: allow-discrete`, durations from motion tokens.

## modal
- `<dialog aria-labelledby aria-describedby>` opened with `showModal()`: focus moves inside (first focusable or the dialog heading with `autofocus`), Esc closes, background inert automatically. On close, return focus to the trigger.
- Anatomy: header (title + close button), scrollable body (`overflow:auto`, header/footer stay), footer actions (primary at inline-end, cancel beside it). Sizes sm/md/lg; fullscreen on mobile (`max-height:100dvh`). Don't stack modals; don't use for non-blocking info.
- Light-dismiss (click backdrop) only for non-destructive, non-form dialogs (`closedby="any"` where supported).

## alert-dialog
- `role="alertdialog"` on `<dialog>`; no light-dismiss; initial focus on the **least destructive** action (Cancel); title states the consequence ("Delete 3 projects?"), body explains irreversibility, destructive button names the action ("Delete projects"), not "OK".

## drawer & bottom-sheet
- `<dialog>` positioned at inline-start/inline-end (bottom for sheet) with slide transition; modal variant (`showModal`) vs non-modal (`show()`, no backdrop, page stays interactive — e.g. filters panel). Width tokens; full-width on mobile. Bottom sheet: drag handle is decorative; always provide a close button; snap heights optional.

## popover
- `[popover]` + `popovertarget` trigger with `aria-expanded` (set by JS or implied); positioned via CSS anchor positioning with flip fallbacks; optional arrow. Non-modal: Tab can leave it; light-dismiss is native for `popover=auto`. Interactive content allowed (unlike tooltips).

## tooltip
- Short, non-interactive text, shown on hover **and** focus after ~300–500ms, dismissable with Esc without moving focus (WCAG 1.4.13), hoverable (pointer can move onto it). `popover="hint"` where supported; associate via `aria-describedby` (supplemental) — or use it as the name source (`aria-labelledby`) for icon buttons. Never put essential info or links in tooltips; not on disabled buttons (use `aria-disabled` instead so it can receive focus).

## coachmark (enterprise)
- Non-modal popover anchored to a target, "Step 2 of 4", Next/Back/Skip tour; highlights the target (outline ring, not a full-screen mask that blocks screen readers); remembers dismissal; never auto-starts more than once.

## lightbox (enterprise)
- Modal dialog with image, caption, previous/next (←/→), counter "3 of 12", zoom optional, close; focus trapped; image `alt` preserved.

## alert (inline), callout, global-banner
- Anatomy: icon (`aria-hidden`), title, description, actions, optional dismiss. Tones info/success/warning/danger via `feedback.*`.
- Announce only when dynamically inserted: `role="status"` (polite) for info/success, `role="alert"` for errors/urgent. Static alerts present at page load need no role.
- Callout: static `<aside>` for docs/notes. Global banner: full-width above the header for system-wide notices (maintenance, trial expiring), dismissible with persistence.

## toast
- Region container (`[popover=manual]` or fixed, `aria-live="polite"`, placed bottom inline-end or top center) stacking newest on top/bottom consistently; max 3 visible.
- Auto-dismiss ≥ 5s (longer with actions), **paused on hover and focus**; errors that require action should not auto-dismiss (use alert instead). Action button ("Undo") reachable via keyboard (provide a shortcut or keep it until focus leaves). Close button on each.

## progress (progress-bar, meter)
- `<progress value max>` with visible label + percentage text; indeterminate = no `value` (animated stripe, reduced-motion safe); complete and error states change tone and text. Thin variant for page-top loading.
- `<meter min max low high optimum value>` for measurements (disk usage, password strength) — different semantics from progress; color zones from feedback tokens plus text.

## spinner & inline-spinner
- SVG/CSS spinner inside `role="status"` with visually hidden "Loading…" (or a visible label variant). Inline variant sized to the font (`1em`) for buttons; the button carries `aria-busy`. Show only after ~300ms to avoid flashes; prefer skeletons for content areas.

## skeleton
- Blocks matching the final layout's geometry (text lines of varying width, avatar circle, card, table rows) with subtle shimmer (disabled under reduced motion). Container `aria-busy="true"`; skeleton blocks `aria-hidden="true"`; a single visually hidden "Loading content" status.

## notification-center (enterprise)
- Bell icon button with unread count in its name → popover/drawer listing notifications (`<ul>` feed), unread indicator (dot + "Unread" text), mark-as-read / mark-all, filters (All/Unread), empty state, links to settings.

## Layer order (z-index)
Native `dialog`/`popover` live in the top layer and ignore z-index. For fixed or JS-positioned layers the token order is: sticky < fixed < overlay < **modal < dropdown/popover** < toast < tooltip — anything that can open *from* a dialog must sit above it.

Overlay files added: `toggletip`, `side-panel`, `floating-panel`. Feedback files added: `result-panel`.

## toggletip (contextual help)
- An "i"/"?" icon button (`aria-label="More info about billing cycle"`, `aria-expanded`) that toggles a `[popover]` (use `popovertarget` or `command="toggle-popover"`). Opens on **click/Enter**, not hover. Content may include rich text and links (unlike tooltip).
- When opened, the content is announced via a `role="status"` region inside the bubble (inject text after opening) **or** focus stays on the button and the bubble is `aria-describedby` — pick one (Heydon Pickering's inclusive-components approach uses the live region). Esc closes; light dismiss via `popover=auto`.
- Anchor-positioned with the shared fallback set; arrow optional. Don't put the field's required instructions only here — they belong in hint text.

## side-panel (push / inline, non-modal)
- An `<aside aria-labelledby>` (complementary) or `role="region"` inside the layout grid, toggled by a button with `aria-expanded aria-controls`. **Push:** grid column animates from `0` to `--side-panel-width` and the main area reflows; **inline:** occupies a column in a split layout permanently (optionally resizable with `splitter`).
- Non-modal: page stays interactive; opening doesn't trap focus. Move focus to the panel heading only when the user opened it explicitly; closing returns focus to the toggle. Esc closes when focus is inside.
- Below `lg` it becomes a modal drawer (`variant:mobile-overlay`) because there's no room to push. Collapsed panel content is `hidden`/`inert` (not just zero width).
- Pitfalls: push animation of `grid-template-columns` is a layout animation — keep it `fast`, or skip under reduced motion.

## floating-panel (enterprise)
- Non-modal `dialog.show()` (or `[popover=manual]`) with a header bar (title, minimize, dock, close). Draggable by the header with Pointer Events; **keyboard move**: a "Move panel" button enables arrow-key movement (Shift = larger steps), Enter/Esc to finish; resizing via handles + keyboard equivalent (WCAG 2.5.7).
- Keep it within the viewport on resize; remember position. F6 (or a documented shortcut) cycles focus between the page and the panel. Minimized state = small bar with restore button. Not for anything that needs a decision — that's a modal.

## result-panel
- Anatomy: status icon (decorative, tone from `feedback.*`), title stating the outcome ("Payment sent"), description (what happened, reference number in a copyable `code`), primary next action + secondary link, optional details (`<details>` with error id/logs).
- Full page: the title is the `<h1>` and the document `<title>` matches; in a region after an async action, insert it and move focus to its heading (`tabindex="-1"`), or announce via `role="status"` — don't do both.
- Tone conveyed by icon + words, not color. Used by `confirmation-page`, `error-page`, `create-resource`.

## progress (circular variant — note only)
- A circular/ring progress is a visual variant of `progress-bar`, not a new component: keep a real `<progress>` (visually hidden) or `role="progressbar" aria-valuenow aria-valuemin aria-valuemax aria-label`, draw the ring with SVG `stroke-dasharray` or `conic-gradient`, show the percentage as text in the center. Indeterminate = rotating arc, stopped under reduced motion (show text "Loading…"). Track ≥ 3:1 vs filled arc.
