# Skeleton

Category: Feedback · page `components/skeleton.html` · CSS `css/components/skeleton.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `skeleton` — Skeleton | core | ready · stable | variant:text variant:avatar variant:card variant:table |

## Usage

Use skeletons while the first load of a content area is in flight: the vehicle list, a work order card, the service history table. Matching the final layout keeps the page from jumping when data arrives.
- Match the real geometry: same number of rows a page usually shows, line widths that vary like real text, avatar circles where avatars go.
- For actions that the user started (saving, assigning), use a spinner or the button's loading state. For long measurable tasks, a progress bar .
- If loading takes longer than ~10 seconds, replace the skeleton with a message ("Still loading vehicles — the telematics service is slow").

## Anatomy

- Group — .skeleton-group[aria-busy="true"] around the loading area
- Status — one visually hidden role="status" ("Loading vehicles…")
- Blocks — .skeleton shapes inside an aria-hidden="true" wrapper

## Examples

### skeleton · variant:text

```html
<div class="skeleton-group" aria-busy="true">
              <span class="sr-only" role="status">Loading work order notes…</span>
              <div class="skeleton-lines" aria-hidden="true">
                <span class="skeleton skeleton--heading"></span>
                <span class="skeleton skeleton--text"></span>
                <span class="skeleton skeleton--text skeleton--w-80"></span>
                <span class="skeleton skeleton--text skeleton--w-60"></span>
              </div>
            </div>
```

### skeleton · variant:avatar

```html
<div class="skeleton-group" aria-busy="true">
              <span class="sr-only" role="status">Loading mechanics…</span>
              <div class="skeleton-lines" aria-hidden="true">
                <div class="skeleton-row"><span class="skeleton skeleton--avatar"></span><div class="skeleton-lines"><span class="skeleton skeleton--text skeleton--w-60"></span><span class="skeleton skeleton--text skeleton--w-40"></span></div></div>
                <div class="skeleton-row"><span class="skeleton skeleton--avatar"></span><div class="skeleton-lines"><span class="skeleton skeleton--text skeleton--w-80"></span><span class="skeleton skeleton--text skeleton--w-40"></span></div></div>
              </div>
            </div>
```

### skeleton · variant:card

```html
<div class="skeleton-group" aria-busy="true">
              <span class="sr-only" role="status">Loading vehicle KX-24…</span>
              <div class="skeleton-card" aria-hidden="true">
                <span class="skeleton skeleton--media"></span>
                <span class="skeleton skeleton--heading"></span>
                <span class="skeleton skeleton--text"></span>
                <span class="skeleton skeleton--text skeleton--w-60"></span>
              </div>
            </div>
```

### skeleton · variant:table

```html
<div class="skeleton-group" aria-busy="true">
              <span class="sr-only" role="status">Loading service history…</span>
              <div class="skeleton-table" aria-hidden="true">
                <div class="skeleton-table__row skeleton-table__row--head"><span class="skeleton skeleton--cell skeleton--w-60"></span><span class="skeleton skeleton--cell skeleton--w-80"></span><span class="skeleton skeleton--cell skeleton--w-60"></span><span class="skeleton skeleton--cell skeleton--w-40"></span></div>
                <div class="skeleton-table__row"><span class="skeleton skeleton--cell skeleton--w-80"></span><span class="skeleton skeleton--cell"></span><span class="skeleton skeleton--cell skeleton--w-80"></span><span class="skeleton skeleton--cell skeleton--w-60"></span></div>
                <div class="skeleton-table__row"><span class="skeleton skeleton--cell"></span><span class="skeleton skeleton--cell skeleton--w-60"></span><span class="skeleton skeleton--cell"></span><span class="skeleton skeleton--cell skeleton--w-40"></span></div>
                <div class="skeleton-table__row"><span class="skeleton skeleton--cell skeleton--w-60"></span><span class="skeleton skeleton--cell skeleton--w-80"></span><span class="skeleton skeleton--cell skeleton--w-60"></span><span class="skeleton skeleton--cell skeleton--w-60"></span></div>
              </div>
            </div>
```

## API

Hook | Values | Purpose
.skeleton-group[aria-busy="true"] | block + attribute | Loading region
.skeleton | block | One placeholder shape
.skeleton--text | --heading | --avatar | --media | --cell | modifier | Shape
.skeleton--w-40 | -60 | -80 | modifier | Line width (default 100%)
.skeleton-row , .skeleton-lines , .skeleton-card , .skeleton-table (+ __row , __row--head ) | layout helpers | Common compositions

## Do and don't

Do vary line widths so the placeholder reads as text.
Each skeleton block announced as "Loading" to screen readers.
Don't expose the blocks; hide them and use one status message per region.

## Accessibility

- The loading region gets aria-busy="true" ; remove it when content arrives.
- Blocks are inside an aria-hidden="true" wrapper; a single visually hidden role="status" says what's loading.
- Not focusable; there is nothing to operate.
- Reduced motion stops the shimmer (WCAG 2.2.2: nothing moves longer than 5 seconds without a way to stop it).
- Forced colors: blocks are drawn with a GrayText outline so the layout stays visible.

## Tokens

Custom property | Purpose
--color-bg-muted | Block fill
--color-bg-subtle | Shimmer highlight
--radius-sm | -md | -lg | -full | Lines, media, card, avatar
--size-control-md | Avatar size
--density-{comfortable|compact}-cell-padding-y | Table row height per density
--motion-duration-slower , --motion-easing-standard | Shimmer timing (× 3)
