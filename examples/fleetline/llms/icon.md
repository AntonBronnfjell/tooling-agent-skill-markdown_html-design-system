# Icon

Category: Foundations · page `components/icon.html` · CSS `css/components/icon.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `icon` — Icon Wrapper | core | ready · stable | size:sm size:md size:lg variant:decorative variant:labelled |

## Usage

Icons help dispatchers scan dense screens and mechanics recognise actions at arm's length. They support text; they rarely replace it. Fleetline uses one outline set (Lucide-style, ISC licence) at a single stroke weight, delivered as an SVG sprite — never an icon font.
- Decorative — next to text that already says the same thing ("Calendar" icon + "Due 12 Nov"). Hidden from assistive tech.
- Labelled — the icon alone carries meaning (a status glyph in a table cell). Give it a name.
- An icon that triggers an action is an icon button , not an icon: it needs a <button> and an aria-label .
- Status is never icon or color alone: pair "Overdue" text with the alert icon.

## Anatomy

- Sprite symbol — <symbol id="icon-NAME" viewBox="0 0 24 24"> , stroke = currentColor
- Instance — <svg class="icon"><use href="#icon-NAME"></use></svg>
- Size — .icon--sm | --md | --lg (16 / 20 / 24px)
- Accessible name (labelled only) — role="img" + aria-label

## Examples

### icon · size:sm

```html
<div class="ds-demo__row">
              <svg class="icon icon--sm" aria-hidden="true" focusable="false"><use href="#icon-truck"></use></svg>
              <svg class="icon icon--sm" aria-hidden="true" focusable="false"><use href="#icon-wrench"></use></svg>
              <svg class="icon icon--sm" aria-hidden="true" focusable="false"><use href="#icon-calendar"></use></svg>
            </div>
```

### icon · size:md

```html
<div class="ds-demo__row">
              <svg class="icon" aria-hidden="true" focusable="false"><use href="#icon-truck"></use></svg>
              <svg class="icon" aria-hidden="true" focusable="false"><use href="#icon-wrench"></use></svg>
              <svg class="icon" aria-hidden="true" focusable="false"><use href="#icon-calendar"></use></svg>
            </div>
```

### icon · size:lg

```html
<div class="ds-demo__row">
              <svg class="icon icon--lg" aria-hidden="true" focusable="false"><use href="#icon-truck"></use></svg>
              <svg class="icon icon--lg" aria-hidden="true" focusable="false"><use href="#icon-wrench"></use></svg>
              <svg class="icon icon--lg" aria-hidden="true" focusable="false"><use href="#icon-calendar"></use></svg>
            </div>
```

### icon · variant:decorative

```html
<div class="stack stack--gap-2">
              <span class="icon-text text-body"><svg class="icon icon--sm" aria-hidden="true" focusable="false"><use href="#icon-calendar"></use></svg>Due 12 Nov</span>
              <span class="icon-text text-body"><svg class="icon icon--sm" aria-hidden="true" focusable="false"><use href="#icon-truck"></use></svg>Truck HT-507</span>
            </div>
```

### icon · variant:labelled

```html
<div class="stack stack--gap-2">
              <span class="icon-text text-body"><svg class="icon" role="img" aria-label="Inspection passed" focusable="false"><use href="#icon-check-circle"></use></svg>Van KX-219</span>
              <span class="icon-text text-body"><svg class="icon" role="img" aria-label="Service overdue" focusable="false"><use href="#icon-alert-circle"></use></svg>Pickup PU-118</span>
            </div>
```

### icon · variant:mirror-rtl

```html
<span class="icon-text text-body">Next vehicle <svg class="icon icon--sm icon--mirror-rtl" aria-hidden="true" focusable="false"><use href="#icon-arrow-right"></use></svg></span>
```

## API

Hook | Values | Purpose
.icon | block class | Sizes the SVG, inherits currentColor , sets stroke weight
.icon--sm | --md | --lg | modifier class | 16 / 20 (default) / 24px
.icon--mirror-rtl | modifier class | Flips directional glyphs in right-to-left pages
.icon-text | class | Aligns an icon with adjacent text
aria-hidden="true" focusable="false" | attributes | Decorative icon
role="img" aria-label="…" | attributes | Labelled icon

## Do and don't

Overdue Do pair status icons with text. Don't rely on an unlabelled icon to communicate meaning.

## Accessibility

- Decorative: aria-hidden="true" removes the icon from the accessibility tree; focusable="false" stops legacy browsers from adding an SVG tab stop.
- Labelled: role="img" + aria-label . Write what it means ("Service overdue"), not what it shows ("Red circle").
- Icons inherit text color, so they meet the same contrast as their text; standalone meaningful icons need 3:1 against their background.
- Forced colors: icons render in CanvasText (or the system color of their control).
- No keyboard interaction. Interactive icons are icon buttons.

## Tokens

Custom property | Purpose
--icon-size-sm | -md | -lg | 16 / 20 / 24px
--icon-stroke | Stroke width (1.5) for the whole set
--space-1-5 | Gap between icon and text
