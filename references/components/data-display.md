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
