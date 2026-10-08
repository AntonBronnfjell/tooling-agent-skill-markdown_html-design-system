# Box

Category: Foundations · page `components/box.html` · CSS `css/components/box.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `box` — Box | core | ready · stable | state:default |

## Usage

Use Box when you need a padded, optionally bordered surface and no richer component fits — a summary panel, a group of fields, a placeholder slot. It exposes only token steps, so apps never invent a 13px padding or a one-off grey.
- Reach for Card when the block has a title, actions or links; for Stack or Grid when you only need spacing between children.
- Box never sets an outer margin. The parent layout decides spacing.
- Use --surface-raised only for things that float above the page; flat panels use --surface-subtle or a border.

## Anatomy

- Container — .box (any element: div , section , li )
- Padding — .box--pad-{2|3|4|6|8}
- Surface — .box--surface | -subtle | -sunken | -raised
- Border and radius — .box--bordered , .box--radius-{md|lg}

## Examples

### box · state:default

```html
<div class="box box--pad-4 box--bordered box--radius-md">
              <p class="text-overline">Next service</p>
              <p class="text-body">Truck HT-507 · 12 Nov · Oil and filter change</p>
            </div>
```

### box · variant:surface-subtle

```html
<div class="box box--pad-4 box--surface-subtle box--radius-md">
              <p class="text-body">3 vehicles are due for inspection this week.</p>
            </div>
```

### box · variant:surface-sunken

```html
<div class="box box--pad-3 box--surface-sunken box--radius-md">
              <p class="text-small">Drop a photo of the damage here, or attach it from the work order.</p>
            </div>
```

### box · variant:surface-raised

```html
<div class="box box--pad-6 box--surface-raised box--radius-lg">
              <p class="text-h5">Van KX-219</p>
              <p class="text-small text-muted">In workshop · Bay 4</p>
            </div>
```

### box · variant:padding-scale

```html
<div class="ds-demo__row">
              <div class="box box--pad-2 box--bordered box--radius-md"><span class="text-small">pad-2</span></div>
              <div class="box box--pad-3 box--bordered box--radius-md"><span class="text-small">pad-3</span></div>
              <div class="box box--pad-4 box--bordered box--radius-md"><span class="text-small">pad-4</span></div>
              <div class="box box--pad-6 box--bordered box--radius-md"><span class="text-small">pad-6</span></div>
              <div class="box box--pad-8 box--bordered box--radius-md"><span class="text-small">pad-8</span></div>
            </div>
```

## API

Hook | Values | Purpose
.box | block class | Block container with no margin
.box--pad-2 | -3 | -4 | -6 | -8 | modifier class | Padding from --space-*
.box--surface | -surface-subtle | -surface-sunken | -surface-raised | modifier class | Background (raised adds elevation shadow)
.box--bordered | modifier class | 1px default border
.box--radius-md | -lg | modifier class | Corner radius (md = Fleetline's 8px shape)
--box-padding , --box-radius | custom property | Override with another token, never a raw value

## Do and don't

Bay 4 · 2 vehicles waiting
Do combine token modifiers instead of writing new CSS.
Bay 4
Don't nest raised boxes; stacked shadows read as clutter.

## Accessibility

- Box is presentational: it adds no role. Use a semantic element ( section with a heading, li ) when the content needs one.
- No keyboard interaction. Don't make a Box clickable; put a link or button inside it.
- Surfaces that differ only by fill get a visible border in forced-colors mode.
- Text on every surface keeps ≥ 4.5:1 ( color.text.default on sunken and raised surfaces is a checked contrast pair).

## Tokens

Custom property | Purpose
--space-2 | -3 | -4 | -6 | -8 | Padding steps
--color-bg-surface | -subtle , --color-elevation-surface-sunken | -raised | Surfaces
--elevation-raised | Raised shadow
--color-border-default , --border-width-thin | Border
--radius-md | -lg | Radius
