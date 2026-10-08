# Typography

Category: Foundations · page `components/typography.html` · CSS `css/components/typography.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `headings` — Typography: Headings H1–H6 | core | ready · stable | variant:h1 variant:h2 variant:h3 variant:h4 variant:h5 variant:h6 variant:display |
| `body-text` — Typography: Body text | core | ready · stable | variant:lead variant:body variant:small variant:caption variant:overline |
| `code` — Typography: Code | core | ready · stable | variant:inline-code variant:code-block |
| `list` — Lists (ordered, unordered, unstyled) | core | ready · stable | variant:ul variant:ol variant:unstyled |

## Usage

Fleetline uses one family (Inter) for all UI text, chosen for legibility on tablets outdoors; data columns switch on tabular numerals with .text-tabular so mileage and costs line up. Type is applied through role classes , never raw sizes.
- Pick the heading element for document structure (one h1 per page, no skipped levels) and the class for visual size. A card title can be an h3 styled .text-h5 .
- Use .text-lead once, under a page title. Use .text-small for secondary metadata, .text-caption for figure and table captions, .text-overline for a short eyebrow above a title (two or three words).
- Body text stays within 65 characters per line ( --size-measure ). Headings balance their lines; paragraphs avoid orphans.
- Don't use bold or color as the only way to mark something important — say it in the text.

## Anatomy

- Font family — --typography-{role}-font-family
- Size — --typography-{role}-font-size (from the --font-size-* scale)
- Weight — --typography-{role}-font-weight
- Line height — --typography-{role}-line-height
- Measure — --size-measure for running text

## Examples

### headings · variant:display

```html
<p class="text-display">1,284 vehicles</p>
```

### headings · variant:h1

```html
<p class="text-h1">Fleet overview</p>
```

### headings · variant:h2

```html
<p class="text-h2">Open work orders</p>
```

### headings · variant:h3

```html
<p class="text-h3">Van KX-219 — brake inspection</p>
```

### headings · variant:h4

```html
<p class="text-h4">Parts and labour</p>
```

### headings · variant:h5

```html
<p class="text-h5">Assigned mechanic</p>
```

### headings · variant:h6

```html
<p class="text-h6">Service history</p>
```

### headings · variant:semantic-vs-visual

```html
<p class="text-overline">h2 element, h5 size</p>
            <p class="text-h5">Depot: North Yard</p>
```

### body-text · variant:lead

```html
<p class="text-lead">Track every vehicle's service schedule, assign repairs to mechanics and keep your fleet on the road.</p>
```

### body-text · variant:body

```html
<p class="text-body">The front brake pads on van KX-219 are at 3&nbsp;mm. Replace them before the next scheduled route on Thursday, and check the discs for scoring while the wheels are off.</p>
```

### body-text · variant:small

```html
<p class="text-small text-muted">Last updated by Priya Nair at 14:32 · Odometer <span class="text-tabular">84,210&nbsp;km</span></p>
```

### body-text · variant:caption

```html
<p class="text-caption">Figure 2. Average repair time per vehicle class, last 90 days.</p>
```

### body-text · variant:overline

```html
<p class="text-overline">Work order</p>
            <p class="text-h4">WO-4182 · Replace front brake pads</p>
```

### code · variant:inline-code

```html
<p class="text-body">Set the vehicle status to <code class="code">in_service</code> after the inspection passes, or call <code class="code">PATCH /vehicles/KX-219</code>.</p>
```

### code · variant:code-block

```html
<pre class="code-block" tabindex="0" aria-label="Example API response for a work order"><code>{
  "id": "WO-4182",
  "vehicle": "KX-219",
  "status": "in_progress",
  "assignee": "Priya Nair",
  "tasks": ["Replace front brake pads", "Inspect discs for scoring"]
}</code></pre>
```

### list · variant:ul

```html
<ul class="list">
              <li>Check tyre pressure and tread depth</li>
              <li>Top up coolant and washer fluid</li>
              <li>Test brake lights and indicators</li>
            </ul>
```

### list · variant:ol

```html
<ol class="list">
              <li>Lift the vehicle and remove the front wheels</li>
              <li>Remove the caliper and the worn pads</li>
              <li>Fit new pads and torque the caliper bolts to spec</li>
            </ol>
```

### list · variant:unstyled

```html
<ul class="list list--unstyled" role="list">
              <li>Van KX-219 · North Yard</li>
              <li>Truck HT-507 · Riverside depot</li>
              <li>Van KX-344 · North Yard</li>
            </ul>
```

## API

Hook | Values | Purpose
.text-display | .text-h1 … .text-h6 | class | Heading roles (balanced wrapping, tight tracking)
.text-lead | .text-body | .text-small | class | Running text, capped at --size-measure
.text-caption | .text-overline | class | Captions and eyebrows (muted)
.text-muted , .text-tabular | modifier class | Secondary color; tabular numerals for data
.code , .code-block | class | Inline code; scrollable block ( pre with tabindex="0" )
.list , .list--unstyled | class | Prose lists; marker-less list (keep role="list" )

## Do and don't

Assigned mechanic
Do keep the outline correct and pick the visual size with a class.
This vehicle is overdue for its annual safety inspection and must not be dispatched
Don't put sentences in an overline or use uppercase for long text.

## Accessibility

- Headings: screen-reader users navigate by heading level. Never skip levels to get a smaller size — use the class.
- Contrast: default text is ≥ 4.5:1 on canvas and surfaces in all themes; muted and subtle text are checked at 4.5:1 too, so they are safe for body copy.
- Zoom: all sizes are rem, so text scales with the user's browser setting and reflows at 320px.
- Code blocks scroll horizontally instead of wrapping; tabindex="0" plus an aria-label lets keyboard users reach and scroll them.
- Lists with list-style: none lose their semantics in Safari/VoiceOver; role="list" restores them.
Keyboard interaction
Key | Behavior
Tab , then ← / → | Focuses a code block and scrolls it horizontally

## Tokens

Custom property | Purpose
--typography-{display|h1…h6|lead|body|small|caption|code}-{font-family|font-size|font-weight|line-height} | Composite type roles
--font-tracking-tight | -wide | Heading and overline letter spacing
--font-weight-semibold | Overline weight
--size-measure | Max line length (65ch)
--color-text-default | -muted | Text colors
--color-bg-muted | -subtle , --color-border-default , --radius-sm | -md | Inline code and code block surfaces
