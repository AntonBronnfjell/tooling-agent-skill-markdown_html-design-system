# Foundations & primitives — specs

Build these first: every later component composes them. Files: `box`, `stack`, `grid`, `aspect-ratio`, `icon`, `typography`, `divider`, `visually-hidden`, `image`, `scroll-area`.

## box
- Thin wrapper exposing token-driven padding, surface, border, radius via modifiers (`.box--pad-4`, `.box--surface-subtle`, `.box--bordered`, `.box--radius-lg`). Only token steps — no arbitrary values.
- It's the escape hatch that keeps people from writing ad-hoc CSS; keep the modifier set small and documented.

## stack (stack, cluster)
- `.stack` = `display:flex; flex-direction:column; gap: var(--stack-gap, var(--space-4))`; `.stack--horizontal`; gap modifiers map to the space scale (`variant:gap-scale` demo shows all).
- `.cluster` = `flex-wrap: wrap` + gap + `align-items:center` for tags, button rows, toolbars.
- Owning spacing in the parent is the rule that keeps components margin-free.

## grid (grid, container)
- 12-column grid: `grid-template-columns: repeat(12, minmax(0,1fr))` + span utilities (`.col-span-6`), responsive spans at sm/md/lg/xl breakpoints (literal rem values mirroring breakpoint tokens).
- Auto-fit grid: `repeat(auto-fit, minmax(min(100%, var(--grid-min, 16rem)), 1fr))` — no media queries needed.
- `.container`: `max-width: var(--size-container-xl); margin-inline:auto; padding-inline: var(--space-4)` growing at breakpoints.

## aspect-ratio
- `aspect-ratio: 16/9` etc. with `object-fit: cover` children. Demo 16:9, 1:1, 4:3.

## icon
- Wrapper `.icon` sizing to `--icon-size-*`, `fill/stroke: currentColor` so it inherits text color.
- Decorative: `aria-hidden="true" focusable="false"`. Meaningful standalone: `role="img" aria-label="…"` (demo both).
- Pick one icon set (Lucide/Phosphor/Heroicons — MIT, consistent stroke) and record it as an ADR; ship an SVG sprite (`<symbol>` + `<use>`) rather than an icon font. Directional icons (arrows, chevrons) mirror in RTL.

## typography (headings, body-text, code, kbd, blockquote, list, prose)
- Utility classes per role: `.text-display`, `.text-h1`…`.text-h6`, `.text-lead`, `.text-body`, `.text-small`, `.text-caption`, `.text-overline` consuming `--typography-*` sub-properties. Semantic level (`h2`) is independent from visual size (`.text-h4`) — demo that.
- Body measure ≤ `--size-measure` (65ch). `text-wrap: balance` on headings, `pretty` on paragraphs.
- Code: inline `code` with subtle bg + radius; `pre > code` scrollable (`overflow-x:auto`, `tabindex="0"` so keyboard users can scroll), no wrapping by default.
- `kbd` styled as a key cap. `blockquote` with `figure/figcaption` attribution.
- Lists: default markers, `.list--unstyled` (keep `role="list"` because Safari drops list semantics with `list-style:none`).
- `.prose` styles raw HTML from CMS/markdown: vertical rhythm with `> * + *` margins, tables, images, hr — because real content is never pre-classed.

## divider
- `<hr>` for thematic breaks (semantic), `role="separator"` + `aria-orientation="vertical"` for vertical, decorative ones `aria-hidden`. Labeled divider ("or") with flex lines.

## visually-hidden
- `.sr-only` and `.sr-only--focusable` (already in base.css) — document them; demo the focusable variant with a skip link.

## image
- Responsive `img` (`max-width:100%; height:auto`), `figure/figcaption`, rounded variant, `loading="lazy"` + `decoding="async"`, explicit `width/height` to prevent layout shift. Loading state = skeleton bg; error state = fallback block with icon + alt text visible.

## scroll-area (enterprise)
- `overflow:auto` region with `tabindex="0"`, `role="region"` + `aria-label` so keyboard users can scroll; thin themed scrollbar via `scrollbar-color`/`scrollbar-width`; scroll shadows to hint overflow.
