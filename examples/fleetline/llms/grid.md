# Grid

Category: Foundations · page `components/grid.html` · CSS `css/components/grid.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `grid` — Grid (container, row, column) | core | ready · stable | variant:12-col variant:auto-fit variant:responsive |
| `container` — Container / Page width | core | ready · stable | variant:container |

## Usage

Use Grid for two-dimensional layout: dashboards, vehicle card lists, form columns. Use Container once per page to cap line length and center the content column.
- Auto-fit is the default for repeating items (vehicle cards, depot tiles): it needs no breakpoints and adapts to its slot.
- 12-column spans are for page regions with fixed proportions (a 9 + 3 work order view with a side panel).
- Every child spans all 12 columns on small screens unless a responsive span says otherwise — mobile is the default.
- Use Stack, not Grid, for a single column of items.

## Anatomy

- Grid — .grid (12 equal tracks) or .grid--auto-fit
- Item span — .col-span-N and .col-span-{sm|md|lg|xl}-N
- Gap — --grid-gap (default --space-4 )
- Container — .container , max width --size-container-xl , growing gutters

## Examples

### grid · variant:12-col

```html
<div class="grid" style="--grid-gap: var(--space-2)">
              <div class="col-span-12 box box--pad-2 box--surface-subtle box--radius-md text-small">12</div>
              <div class="col-span-6 box box--pad-2 box--surface-subtle box--radius-md text-small">6</div>
              <div class="col-span-6 box box--pad-2 box--surface-subtle box--radius-md text-small">6</div>
              <div class="col-span-4 box box--pad-2 box--surface-subtle box--radius-md text-small">4</div>
              <div class="col-span-4 box box--pad-2 box--surface-subtle box--radius-md text-small">4</div>
              <div class="col-span-4 box box--pad-2 box--surface-subtle box--radius-md text-small">4</div>
              <div class="col-span-3 box box--pad-2 box--surface-subtle box--radius-md text-small">3</div>
              <div class="col-span-9 box box--pad-2 box--surface-subtle box--radius-md text-small">9</div>
            </div>
```

### grid · variant:auto-fit

```html
<div class="grid grid--auto-fit" style="--grid-min: 12rem">
              <div class="box box--pad-4 box--bordered box--radius-md"><p class="text-h6">Van KX-219</p><p class="text-small text-muted">In workshop · Bay 4</p></div>
              <div class="box box--pad-4 box--bordered box--radius-md"><p class="text-h6">Truck HT-507</p><p class="text-small text-muted">On route · Riverside</p></div>
              <div class="box box--pad-4 box--bordered box--radius-md"><p class="text-h6">Van KX-344</p><p class="text-small text-muted">Available · North Yard</p></div>
              <div class="box box--pad-4 box--bordered box--radius-md"><p class="text-h6">Pickup PU-118</p><p class="text-small text-muted">Service due in 3 days</p></div>
            </div>
```

### grid · variant:responsive

```html
<div class="grid">
              <div class="col-span-md-8 col-span-lg-9 box box--pad-4 box--bordered box--radius-md"><p class="text-h6">Work order WO-4182</p><p class="text-small text-muted">Full width on phones, 8 of 12 from 48rem, 9 of 12 from 64rem.</p></div>
              <div class="col-span-md-4 col-span-lg-3 box box--pad-4 box--surface-subtle box--radius-md"><p class="text-h6">Vehicle details</p><p class="text-small text-muted">Side panel</p></div>
            </div>
```

### container · variant:container

```html
<div class="box box--surface-sunken box--radius-md">
            <div class="container container--md">
              <div class="box box--pad-4 box--surface box--bordered box--radius-md">
                <p class="text-h6">Settings</p>
                <p class="text-small text-muted">Centered column, max 48rem (<code>.container--md</code>) with a 16px gutter that grows to 24px and 32px on wider screens.</p>
              </div>
            </div>
          </div>
```

## API

Hook | Values | Purpose
.grid | block class | 12 equal columns; children span 12 by default
.col-span-{1|2|3|4|6|8|9|12} | class | Span at every width
.col-span-sm-{4|6|12} , -md-{3|4|6|8} , -lg-{3|4|8|9} , -xl-{2|3} | class | Span from 40 / 48 / 64 / 80rem (mirrors --breakpoint-* )
.grid--auto-fit | modifier class | As many columns as fit, each ≥ --grid-min
--grid-gap , --grid-min | custom property | Gap token; track minimum (default 16rem)
.container , .container--md | --lg | block / modifier | Centered page column, 80 / 48 / 64rem max

## Do and don't

Vehicle cards in .grid--auto-fit with --grid-min: 14rem .
Do let repeating content fit itself; it works in any slot width.
.col-span-3 on cards with no responsive span.
Don't use fixed small spans without a mobile default — four columns at 320px are unreadable.

## Accessibility

- Layout only: no roles. When grid items are a collection (vehicle cards), use ul / li with role="list" so the count is announced.
- Don't use grid-auto-flow: dense , explicit placement or order on interactive content: focus order must follow visual order.
- Reflow: every layout collapses to one column at 320px wide (WCAG 1.4.10).

## Tokens

Custom property | Purpose
--space-4 (gap), --space-4 | -6 | -8 (container gutters) | Spacing
--size-container-md | -lg | -xl | Container widths
--breakpoint-sm | -md | -lg | -xl | Mirrored as literal rem in media queries
