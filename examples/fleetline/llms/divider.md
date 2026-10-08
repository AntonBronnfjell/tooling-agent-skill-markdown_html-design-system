# Divider

Category: Foundations · page `components/divider.html` · CSS `css/components/divider.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `divider` — Divider / Separator | core | ready · stable | variant:horizontal variant:vertical variant:with-label |

## Usage

Use a divider to separate groups that spacing alone can't separate: the totals row of a parts list, two groups of toolbar actions, alternative sign-in methods. Prefer whitespace first — every line adds visual noise to dense dispatcher screens.
- Horizontal — <hr> for a thematic break in content (it is announced as a separator).
- Vertical — between inline groups (toolbar sections, metadata items).
- With label — a short word that explains the break ("or", "Earlier"). One or two words, sentence case.

## Anatomy

- Line — 1px --color-border-default ( .divider--strong for 3:1)
- Label (optional) — centered text between two lines, .divider-label

## Examples

### divider · variant:horizontal

```html
<div class="stack stack--gap-3">
              <p class="text-body">Front brake pads (set) · 2 × €48.00</p>
              <hr class="divider">
              <p class="text-body"><strong>Parts total · €96.00</strong></p>
            </div>
```

### divider · variant:vertical

```html
<div class="stack stack--horizontal stack--gap-3">
              <span class="text-small">Van KX-219</span>
              <span class="divider divider--vertical" role="separator" aria-orientation="vertical"></span>
              <span class="text-small">84,210 km</span>
              <span class="divider divider--vertical" role="separator" aria-orientation="vertical"></span>
              <span class="text-small">Bay 4</span>
            </div>
```

### divider · variant:with-label

```html
<div class="stack stack--gap-3">
              <button type="button" class="btn btn--primary btn--full-width">Scan vehicle QR code</button>
              <div class="divider-label"><span>or</span></div>
              <button type="button" class="btn btn--secondary btn--full-width">Enter plate number</button>
            </div>
```

## API

Hook | Values | Purpose
hr.divider | block class | Horizontal semantic separator
.divider--vertical + role="separator" aria-orientation="vertical" | modifier + ARIA | Vertical separator in a row
.divider--strong | modifier class | 3:1 line when the line itself must be perceived
.divider-label | block class | Labelled break
aria-hidden="true" | attribute | Purely decorative divider that shouldn't be announced

## Do and don't

Labour · 1.5 h
Total · €171.00
Do use a divider to set off a summary row.
Plate
Make
Model
Don't put a line between every item; use spacing or a list.

## Accessibility

- <hr> has the implicit separator role; screen readers announce it. Add aria-hidden="true" when the break is purely visual.
- Vertical separators need role="separator" and aria-orientation="vertical" . Inside a toolbar they group controls for assistive tech.
- The labelled divider isn't a separator role (separator children are hidden from the accessibility tree); its word is read as normal text.
- Decorative lines are 1px border.default ; lines in forced colors use CanvasText .
- Not focusable, no keyboard interaction. (Resizable separators are the splitter component.)

## Tokens

Custom property | Purpose
--border-width-thin | Line weight
--color-border-default | -strong | Line color
--color-text-muted , --typography-small-* | Label text
--space-3 | -6 | Label gap; minimum vertical length
