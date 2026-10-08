# Stack

Category: Foundations · page `components/stack.html` · CSS `css/components/stack.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `stack` — Stack (vertical & horizontal) | core | ready · stable | variant:vertical variant:horizontal variant:gap-scale |

## Usage

Stack spaces its children evenly along one axis; it is how Fleetline keeps components margin-free. A form is a vertical stack of fields; a header is a horizontal stack of title and actions. Use Cluster for items that should wrap onto new lines (button rows, filter chips, tags), and Grid for two dimensions.
- Pick the gap from the scale: 2–3 inside a component, 4 between fields, 6–8 between sections.
- Never add margins to children to "fix" spacing — change the parent's gap or nest another stack.

## Anatomy

- Container — .stack (column) or .stack--horizontal (row), or .cluster (wrapping row)
- Gap — .stack--gap-{1|2|3|4|6|8} or --stack-gap / --cluster-gap
- Children — any elements, no margins

## Examples

### stack · variant:vertical

```html
<div class="stack stack--gap-3">
              <div class="box box--pad-3 box--bordered box--radius-md">WO-4182 · Replace front brake pads</div>
              <div class="box box--pad-3 box--bordered box--radius-md">WO-4185 · Annual safety inspection</div>
              <div class="box box--pad-3 box--bordered box--radius-md">WO-4190 · Replace wiper blades</div>
            </div>
```

### stack · variant:horizontal

```html
<div class="stack stack--horizontal stack--gap-2">
              <button type="button" class="btn btn--primary btn--sm">Assign mechanic</button>
              <button type="button" class="btn btn--ghost btn--sm">View history</button>
            </div>
```

### stack · variant:gap-scale

```html
<div class="stack stack--gap-4">
              <div class="stack stack--horizontal stack--gap-1"><span class="box box--pad-2 box--surface-subtle box--radius-md">gap-1</span><span class="box box--pad-2 box--surface-subtle box--radius-md">4px</span></div>
              <div class="stack stack--horizontal stack--gap-2"><span class="box box--pad-2 box--surface-subtle box--radius-md">gap-2</span><span class="box box--pad-2 box--surface-subtle box--radius-md">8px</span></div>
              <div class="stack stack--horizontal stack--gap-3"><span class="box box--pad-2 box--surface-subtle box--radius-md">gap-3</span><span class="box box--pad-2 box--surface-subtle box--radius-md">12px</span></div>
              <div class="stack stack--horizontal stack--gap-4"><span class="box box--pad-2 box--surface-subtle box--radius-md">gap-4</span><span class="box box--pad-2 box--surface-subtle box--radius-md">16px</span></div>
              <div class="stack stack--horizontal stack--gap-6"><span class="box box--pad-2 box--surface-subtle box--radius-md">gap-6</span><span class="box box--pad-2 box--surface-subtle box--radius-md">24px</span></div>
              <div class="stack stack--horizontal stack--gap-8"><span class="box box--pad-2 box--surface-subtle box--radius-md">gap-8</span><span class="box box--pad-2 box--surface-subtle box--radius-md">32px</span></div>
            </div>
```

### cluster · variant:cluster

```html
<div class="cluster">
              <button type="button" class="btn btn--secondary btn--sm">North Yard</button>
              <button type="button" class="btn btn--secondary btn--sm">Riverside depot</button>
              <button type="button" class="btn btn--secondary btn--sm">Airport hub</button>
              <button type="button" class="btn btn--secondary btn--sm">Harbour garage</button>
              <button type="button" class="btn btn--secondary btn--sm">East workshop</button>
            </div>
```

### cluster · variant:cluster-between

```html
<div class="cluster cluster--between">
              <span class="text-h6">Open work orders (12)</span>
              <button type="button" class="btn btn--primary btn--sm">New work order</button>
            </div>
```

## API

Hook | Values | Purpose
.stack | block class | Vertical flex column with gap
.stack--horizontal , .stack--align-center | modifier class | Row direction; center alignment
.stack--gap-1 | -2 | -3 | -4 | -6 | -8 | modifier class | Gap from --space-* (4 is default)
.cluster , .cluster--between | block / modifier | Wrapping row; push items to the ends
--stack-gap , --cluster-gap | custom property | Assign a --space-* token

## Do and don't

Assign mechanic Save draft Do use Cluster for button rows so they wrap on narrow screens and long translations. Assign mechanic Save draft Don't put long or many items in a non-wrapping horizontal stack — it overflows at 320px.

## Accessibility

- Layout only: no roles, no keyboard behavior.
- Keep DOM order equal to visual order; don't reorder with order or flex-direction: row-reverse , or Tab order and reading order will diverge.
- Gaps use logical flow, so RTL needs nothing extra.

## Tokens

Custom property | Purpose
--space-1 | -2 | -3 | -4 | -6 | -8 | Gap steps
--stack-gap (default --space-4 ), --cluster-gap (default --space-2 ) | Component-level gap hooks
