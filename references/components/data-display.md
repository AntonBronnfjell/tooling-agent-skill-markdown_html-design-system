# Data display & content — specs

Files: `table`, `data-table` (data-table, tree-table), `card`, `accordion` (accordion, disclosure), `avatar` (avatar, avatar-group), `badge` (badge, status-indicator), `tag`, `list-group`, `description-list`, `timeline`, `carousel`, `stat`, `chart`, `hover-card`, `truncate`.

## table
- Semantic `<table>` with `<caption>` (visible or `.sr-only`), `<th scope="col|row">`. Numeric columns right-aligned with `font-variant-numeric: tabular-nums`. Striped / compact (density) / bordered variants. Wrap in a focusable scroll container (`role="region" aria-label tabindex="0"`) for horizontal overflow.

## data-table
- Builds on table: toolbar (search, filters, column visibility, density toggle, export), sortable headers (`<button>` inside `th`, `aria-sort="ascending|descending"` on the `th`), row selection checkboxes with header "select all" (indeterminate), bulk-action bar replacing the toolbar when rows selected ("3 selected" + actions), sticky header and first column, pagination footer, row actions menu.
- States: loading (skeleton rows, `aria-busy`), empty (empty-state inside the table body spanning all columns), error with retry, no results for filter (with "Clear filters").
- Use plain table semantics unless cells are interactive with arrow-key navigation — only then APG `role="grid"`.
- Tree data table (enterprise): `role="treegrid"`, expand buttons in first cell with `aria-expanded`, `aria-level` on rows, indent per level.

## card
- `<article>` (or `<li>` in a list of cards) with optional media, heading, body, meta, actions. Interactive card: one primary link on the heading with a pseudo-element stretched over the card (`.card__link::after { inset: 0 }`) — not a giant `<a>` wrapping everything, and secondary buttons still clickable above it. Selected state for selectable cards (checkbox inside). Hover elevation via `shadow` tokens; equal heights in grids via `grid` + `height:100%`.

## accordion & disclosure
- `<details><summary>`; exclusive accordion via shared `name` attribute. Summary is the heading's content (`<summary><h3>` is invalid — style the summary as a heading or use the APG button pattern if heading semantics are required). Chevron rotates (respect reduced motion), mirrors in RTL. Animate with `interpolate-size: allow-keywords` + `::details-content` where supported.

## avatar & avatar-group
- Image with `alt` = person's name (or `alt=""` when the name is printed beside it). Fallbacks: initials (deterministic bg color from a token palette by name hash, contrast-checked) → generic icon. Status badge (online/busy) with text equivalent. Sizes from icon/control scale.
- Group: negative inline margin overlap with a ring of `--color-bg-surface`; "+5" overflow element with full list in tooltip/popover.

## badge & status-indicator
- Count badge (cap "99+"), dot badge (needs text equivalent on the parent: "Inbox, 3 unread"), tonal variants mapping to `feedback.*` tokens. Not interactive. Add each tone's fg/bg to `contrast_pairs`.
- Status indicator: dot + visible label ("Online"), never color alone.

## tag (chip)
- Static (metadata), removable (`<button aria-label="Remove tag: Design">` inside), selectable/filter chips (`<button aria-pressed>` or checkbox semantics). Truncate long labels with tooltip.

## list-group
- `<ul role="list">` rows with leading avatar/icon, primary + secondary text, trailing meta/action. Interactive rows: the row's main link/button is the hit target; avoid nested interactive conflicts.

## description-list
- `<dl>` with `<div>` wrappers around `dt/dd` pairs (valid HTML) to style rows; stacked (mobile) and horizontal (grid two columns) variants; empty value shows "—" with `aria-label="Not set"`.

## timeline
- `<ol>` chronological; each item: marker (icon or dot), title, `<time datetime>`, description. Current/latest item emphasized. Vertical line via pseudo-element using border token.

## carousel (enterprise)
- APG carousel: region `aria-roledescription="carousel"` + label; slides `role="group" aria-roledescription="slide" aria-label="2 of 5"`; previous/next buttons; dots (see navigation). **No autoplay by default**; if autoplay, a visible pause button and pause on hover/focus. Scroll-snap based for touch.

## stat (metric)
- Label, large value (`tabular-nums`), unit, delta with arrow icon + text ("+12% vs last month") — direction not color-only; optional sparkline (decorative SVG `aria-hidden` with the summary in text). Loading skeleton.

## chart (chart container & dataviz palette, enterprise)
- `<figure>` with title, subtitle, legend, the chart (SVG `role="img"` + `aria-label` summary, or a data table alternative via disclosure), and source note. Palettes: `dataviz.categorical.*` (color-blind safe; max 8 series, then group "Other"), `sequential`, `diverging`. Axis/grid lines use border tokens; labels use text tokens. Empty and loading states. Delegate actual chart rendering guidance to `/dataviz` if available.

## hover-card (enterprise)
- Preview card on hover **and focus** of a link (user mention, link preview), `[popover]` with delay; content must not be the only way to reach info; non-modal, dismiss on Esc and pointer leave.

## truncate
- `line-clamp` (`-webkit-line-clamp` + `display:-webkit-box`) with a "Show more" `<button aria-expanded>`; single-line ellipsis utility with full text in `title`/tooltip only when focusable.

## post-card
- `<article aria-labelledby>` in a feed: author row (avatar, name link, `<time datetime>` relative + absolute in `title`), body (`.prose`, truncate long text), optional media (media-stage or image grid), action bar (like/comment/share as toggle buttons with counts in the accessible name: "Like, 12 likes"). Loading skeleton matches the geometry. Whole-card link follows the card pattern (one stretched primary link).

## media-stage
- Hero media surface: `<figure>` that renders on an always-dark subtree (`class="theme-dark"`) regardless of page theme, so overlays and captions keep contrast over imagery. Variants: image, video (native `<video controls>` with captions `<track>`), audio, live (red "Live" badge with text, never color only). Scrim gradient from tokens behind overlaid text; duration badge (`<time>` with `datetime="PT3M20S"`); caption via `figcaption`. No autoplay with sound; `prefers-reduced-motion` disables autoplaying video previews.

## stat (addition)
- Optional count-up on first reveal: animate only under full motion, render the final value in the DOM from the start (screen readers and no-JS see the real number), never re-run on re-render.

Files added: `card-collection`, `sortable-list`, `board`, `formatters`, `comment-thread`, `qr-code`, `chart-parts`.

## card-collection (grid list)
- Static: `<ul role="list">` of `<li>` → card. Nothing new beyond card + grid.
- Selectable: each card has a real checkbox (multi) or radio (single) labelled by the card title; `:has(:checked)` styles selected. This keeps native semantics and needs no ARIA grid.
- Only if arrow-key navigation between cards is required (large galleries, file managers): APG grid/listbox with roving tabindex, Space toggles, Ctrl/Cmd+A selects all, Shift+arrows extend; announce selection count. Don't combine with in-card buttons unless you implement grid cell navigation.
- Pairs with `selection-action-bar`. Empty and loading (skeleton cards matching geometry) states.

## sortable-list (enterprise)
- Every drag interaction has a non-drag alternative (WCAG 2.5.7): per-item "Move up"/"Move down" buttons or a "Move…" menu (to top, to position N), **and/or** keyboard grab mode on the handle: Space/Enter picks up (`state:grabbed`, announced "Picked up Item 3, position 3 of 8"), ↑/↓ move, Space drops, Esc cancels (restores position).
- Handle: `<button aria-label="Reorder Item 3" aria-describedby="<instructions id>">`; instructions visually hidden. All announcements via the shared polite live region ("Item 3 moved to position 2 of 8").
- `aria-grabbed`/`aria-dropeffect` are deprecated — don't use. Pointer: Pointer Events (not HTML5 DnD — no touch, poor a11y), auto-scroll near edges, placeholder with the item's height, drop indicator line ≥ 3:1.
- Focus stays on the moved item's handle after a move. Respect reduced motion (no settle animation).

## board (kanban, enterprise)
- Columns are `<section aria-labelledby>` with an `<h2>` ("In progress, 4 items") and a `<ul>` of cards. Cards are cards (one primary link), plus a "Move to…" menu (column + position) — the required non-drag path. Optional keyboard grab mode as in sortable-list, with ←/→ changing column.
- WIP limit: count/limit in header text ("4 of 5"), over-limit state uses warning tone + text. Empty column shows an empty state and stays a drop target. Horizontal scroll region is focusable (`role="region" tabindex="0"`).
- Announce moves ("Moved 'Fix login' to Done, position 1 of 3"). Persist optimistically and roll back with an error toast on failure.

## formatters (relative-time, number-format)
- Pure presentation helpers in `js/formatters.js` (no DOM state): `formatRelative(date, {now, locale})` via `Intl.RelativeTimeFormat` with `numeric:"auto"` ("yesterday"), `formatNumber`, `formatCurrency` (`style:"currency"`, ISO code required), `formatPercent`, `formatCompact` (`notation:"compact"`), `formatBytes` (`style:"unit"` with `byte`/`kilobyte`/…; decide 1000 vs 1024 and label kB vs KiB — ADR), `formatRange` (`formatRange`).
- Markup: `<time datetime="2026-10-08T09:30Z" title="8 October 2026, 09:30 UTC">3 hours ago</time>`; numbers in `<data value="1234.5">1,234.50</data>`. The machine value is always in the DOM; server renders an absolute fallback so no-JS is correct.
- Auto-update relative times on a single shared interval (≥ 60s, paused when the tab is hidden); **never** wrap them in a live region. Absolute time on hover **and** focus or via an always-available detail view (title alone isn't keyboard/touch accessible).
- `tabular-nums` in tables; currency symbol position, decimal separators, and negative formats come from the locale, never hand-built strings. Compact numbers ("1.2K") need the full value accessible (title + `aria-label` or adjacent sr text).

## comment-thread
- `<ol>` of comments, each `<article aria-labelledby>` with author (avatar + name), `<time>` (relative-time), body (`.prose`), actions (Reply, Edit, Delete, Resolve, reactions as `aria-pressed` toggle buttons with counts in their names). Replies are a nested `<ol>`; cap visual nesting at 2 levels, flatten deeper with "Replying to @name".
- Composer per composer spec; reply opens an inline composer and moves focus into it; Esc/cancel returns focus to the Reply button. Editing replaces the body with a textarea in place (inline-edit rules).
- Resolved thread collapses to a summary disclosure ("Resolved by Ana · 3 replies"). Deleted comment leaves a tombstone ("Comment deleted") to keep reply context. Mentions are links; new comments from others don't steal focus — show a "2 new comments" button (feed rule).

## qr-code
- Generate SVG (one `<path>`, `shape-rendering="crispEdges"`) server-side or with a small library; `role="img"` + `aria-label="QR code for example.com/pair"` and **always** show the URL/code as text and a copy/link fallback beside it (`variant:with-fallback-link`).
- Contrast: dark modules on light background in every theme (don't invert in dark mode — many scanners fail on inverted codes); quiet zone ≥ 4 modules; minimum rendered size ~2cm / 128px. Logo overlay only with error correction level H, ≤ ~20% area.
- Pitfalls: QR as the only way to continue (desktop users on the same device can't scan it).

## chart-parts (chart-legend, chart-tooltip, chart-axis, sparkline)
Dataviz rules (apply to `chart` and every part):
- **Categorical order is fixed:** series map to `dataviz.categorical.1…8` in data order, and the same entity keeps the same color across every chart on a page. Max 8; beyond that group as "Other" (neutral). Don't use feedback colors for ordinary series; reserve red/green for meaning.
- **Graphical contrast ≥ 3:1** (WCAG 1.4.11) for marks, lines and the legend swatch against the chart background — add each `dataviz.*` vs `bg.surface` to `contrast_pairs` in every theme. Adjacent fills that touch need a 1–2px `bg.surface` separator stroke.
- **Never color-only:** pair color with a second channel — direct labels, marker shapes, dash patterns, or pattern fills (`<pattern>` defs) for categorical fills; the legend shows the same shape/dash.
- **Table fallback always:** each chart has the underlying data as a `<table>` (in a `<details>` "Show data table" or a toggle) — the accessible source of truth. The SVG gets `role="img"` + `aria-label` with the takeaway ("Revenue grew 12% from Q1 to Q4") and `aria-describedby` to a longer summary.
- Sequential palettes for ordered magnitude, diverging only with a meaningful midpoint (zero, target). Forced-colors: lines use `CanvasText`, fills fall back to patterns.

### chart-legend
- `<ul>` with swatch (shape matching the mark) + label in data order; place above or beside the chart (not below long charts). Prefer **direct labels** at line ends when ≤ 5 series (`variant:direct-labels`) and drop the legend.
- Interactive legend: each item a `<button aria-pressed="true">` "Show Revenue"; hidden series keep their color slot (no reassignment), state shown with a struck/hollow swatch + text, and at least one series must stay visible.

### chart-tooltip
- Appears on pointer hover **and** keyboard focus of a data point (points focusable via a roving-focus group or arrow keys across the x-axis), Esc dismisses (WCAG 1.4.13), hoverable, doesn't cover the pointed mark (anchor-positioned with flip). Content: x value, series swatch + name + formatted value (formatters), sorted to match visual stack order.
- Not announced as a live region on pointer moves; keyboard focus on a point exposes the same text via the point's accessible name. Never the only path to values — the table fallback is.

### chart-axis (axis & gridlines)
- Axis labels and tick labels use `text.muted` (≥ 4.5:1), axis lines `border.strong`, gridlines `border.subtle` (decorative, may be < 3:1 — they're not required to identify data). Zero baseline emphasized (`border.strong`). Tick labels formatted with `formatters` (compact numbers, dates by locale), ≤ ~7 ticks, no rotated labels (wrap or abbreviate instead). Axis titles include units.
- Bar charts start at zero; truncated axes must be marked. SVG text uses `font-variant-numeric: tabular-nums`. The axis group is `aria-hidden="true"` — values reach AT through the table fallback.

### sparkline
- Word-sized (`1em`–`2em` tall) inline SVG, no axes; optional end-point dot and min/max markers. Standalone: `role="img" aria-label="Trend: up 8% over 30 days"`; inside `stat` it stays `aria-hidden` (stat already has the text). In tables, one sparkline per row in its own column with the summary as sr text. Stroke ≥ 1.5px and ≥ 3:1.

## status-indicator (extension — no new item)
- Severity scale: add `variant:severity-critical|high|medium|low|info` demos to `status-indicator`: shape icon (octagon/triangle/circle/info) + text label + tone; order and naming fixed system-wide; tones map to `feedback.*`, critical vs high differ by icon and label, not just shade.
