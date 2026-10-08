# Description List

Category: Data Display · page `components/description-list.html` · CSS `css/components/description-list.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `description-list` — Description List | core | ready · stable | variant:stacked variant:horizontal |

## Usage

Use a description list for the fields of one object: a vehicle's registration, odometer, next service. Use a table to compare several objects, and a form when the values are editable.
- Stacked — label above value; side panels, tablet and narrow cards.
- Horizontal — two aligned columns; detail pages on desktop. It switches to stacked automatically in narrow containers.
Content: terms are nouns in sentence case ("Next service"), values include units ("84,212 km"). Show an em dash for empty values with "Not set" for screen readers — never leave a value blank.

## Anatomy

- List — <dl class="dl">
- Row — div.dl__row wrapping one dt / dd pair (valid HTML)
- Term — <dt>
- Value — <dd> ; numbers get .dl__num
- Empty value — .dl__empty em dash + .sr-only "Not set"

## Examples

### description-list · variant:stacked

```html
<dl class="dl">
              <div class="dl__row"><dt>Registration</dt><dd>KX-219</dd></div>
              <div class="dl__row"><dt>Make and model</dt><dd>Ford Transit 350 L3</dd></div>
              <div class="dl__row"><dt>Odometer</dt><dd class="dl__num">84,212 km</dd></div>
              <div class="dl__row"><dt>Next service</dt><dd>21 Oct 2026 or 86,000 km</dd></div>
              <div class="dl__row"><dt>Assigned driver</dt><dd><span class="dl__empty" aria-hidden="true">—</span><span class="sr-only">Not set</span></dd></div>
            </dl>
```

### description-list · variant:horizontal

```html
<dl class="dl dl--horizontal">
              <div class="dl__row"><dt>Registration</dt><dd>KX-219</dd></div>
              <div class="dl__row"><dt>Make and model</dt><dd>Ford Transit 350 L3</dd></div>
              <div class="dl__row"><dt>Odometer</dt><dd class="dl__num">84,212 km</dd></div>
              <div class="dl__row"><dt>Next service</dt><dd>21 Oct 2026 or 86,000 km</dd></div>
              <div class="dl__row"><dt>Assigned driver</dt><dd><span class="dl__empty" aria-hidden="true">—</span><span class="sr-only">Not set</span></dd></div>
            </dl>
```

## API

Hook | Values | Purpose
.dl | block class | Stacked list with row dividers
.dl--horizontal | modifier class | Two columns aligned with subgrid; stacked under 28rem container width
.dl__row | part class | Row wrapper
.dl__num | part class | Tabular numerals
.dl__empty | part class | Muted dash for missing values
[data-density="compact"] | ancestor attribute | Tighter rows

## Do and don't

Odometer: 84,212 km
Do include the unit with the value.
Assigned driver: (blank)
Don’t leave an empty value; show — with "Not set".
<div><dt><dd></div>
Do wrap pairs in div to style rows.
A two-column table for one vehicle's fields
Don’t use a table for key/value pairs of one item.

## Accessibility

Description lists are static content; no keyboard behavior.
- Screen readers announce the list and its term/definition pairs ("description list, 5 items").
- div wrappers around dt / dd are valid HTML and don't change semantics.
- Empty values: the dash is aria-hidden ; "Not set" is read instead.
- Reflow: the horizontal layout becomes stacked in narrow containers, so 320px and 400% zoom work without horizontal scrolling.

## Tokens

Custom property | Purpose
--color-text-muted | Terms, empty dash
--color-text-default | Values
--color-border-default | Row dividers
--space-3 | -2 | -6 | Row padding (comfortable / compact), column gap
--font-size-sm , --font-weight-medium | Term text
