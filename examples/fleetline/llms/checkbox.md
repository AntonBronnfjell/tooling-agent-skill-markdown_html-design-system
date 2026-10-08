# Checkbox

Category: Forms · page `components/checkbox.html` · CSS `css/components/checkbox.css` · JS `js/checkbox.js` (export `init(root)`)

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `checkbox` — Checkbox | core | ready · stable | state:unchecked state:checked state:hover state:focus-visible state:disabled state:invalid state:indeterminate |
| `checkbox-group` — Checkbox Group | core | ready · stable | variant:group-vertical variant:group-horizontal variant:group-error |

## Usage

Use checkboxes when people can pick any number of options (including none) — inspection items, vehicle features, which depots to include in a report — or to confirm a single statement. Use radios when only one answer is allowed, and a switch for a setting that applies immediately.
- Group related checkboxes in a fieldset with a legend that asks the question.
- Write labels as the thing being chosen ("Tachograph calibrated"), not "Yes".
- Vertical by default; horizontal only for 2–3 short options.
- Indeterminate is only for a parent "select all" whose children are partly selected.

## Anatomy

- Box — input[type=checkbox].checkbox__input (native, appearance: none ), 24px
- Check / dash mark — masked ::before
- Label — label.checkbox__label[for] , part of the hit area
- Hint (optional) — .checkbox__hint , wired with aria-describedby
- Group — fieldset.checkbox-group with legend, hint, error and .checkbox-group__items

## Examples

### checkbox · state:unchecked

```html
<div class="checkbox">
              <input class="checkbox__input" type="checkbox" id="cb-off">
              <label class="checkbox__label" for="cb-off">Tyres checked for wear and pressure</label>
            </div>
```

### checkbox · state:checked

```html
<div class="checkbox">
              <input class="checkbox__input" type="checkbox" id="cb-on" checked>
              <label class="checkbox__label" for="cb-on">Tyres checked for wear and pressure</label>
            </div>
```

### checkbox · state:hover

```html
<div class="stack stack--gap-3">
            <div class="checkbox">
              <input class="checkbox__input is-hover" type="checkbox" id="cb-hover">
              <label class="checkbox__label" for="cb-hover">Lights and indicators working</label>
            </div>
            <div class="checkbox">
              <input class="checkbox__input is-hover" type="checkbox" id="cb-hover-on" checked>
              <label class="checkbox__label" for="cb-hover-on">Mirrors adjusted</label>
            </div>
            </div>
```

### checkbox · state:focus-visible

```html
<div class="checkbox">
              <input class="checkbox__input is-focus-visible" type="checkbox" id="cb-focus">
              <label class="checkbox__label" for="cb-focus">Windscreen free of chips</label>
            </div>
```

### checkbox · state:disabled

```html
<div class="stack stack--gap-3">
            <div class="checkbox">
              <input class="checkbox__input" type="checkbox" id="cb-dis" disabled aria-describedby="cb-dis-hint">
              <label class="checkbox__label" for="cb-dis">Brake test complete</label>
              <p class="checkbox__hint" id="cb-dis-hint">Available after the vehicle is on the rolling road.</p>
            </div>
            <div class="checkbox">
              <input class="checkbox__input" type="checkbox" id="cb-dis-on" checked disabled>
              <label class="checkbox__label" for="cb-dis-on">Pre-trip check submitted</label>
            </div>
            </div>
```

### checkbox · state:invalid

```html
<div class="field">
              <div class="checkbox">
                <input class="checkbox__input" type="checkbox" id="cb-inv" required aria-invalid="true" aria-describedby="cb-inv-err">
                <label class="checkbox__label" for="cb-inv">I confirm KX-219 is safe to return to service</label>
              </div>
              <p class="field__error" id="cb-inv-err">
                <svg class="field__error-icon" aria-hidden="true" focusable="false"><use href="#icon-alert-circle"></use></svg>
                <span><span class="sr-only">Error: </span>Confirm the vehicle is safe before closing the work order.</span>
              </p>
            </div>
```

### checkbox · state:indeterminate

```html
<div class="stack stack--gap-3">
            <div class="checkbox">
              <input class="checkbox__input" type="checkbox" id="cb-all" data-select-all aria-controls="cb-n1 cb-n2 cb-n3 cb-n4 cb-n5" data-indeterminate>
              <label class="checkbox__label" for="cb-all">All North Yard vehicles (3 of 5)</label>
            </div>
            <div class="stack stack--gap-3" style="padding-inline-start: var(--space-8)">
            <div class="checkbox">
              <input class="checkbox__input" type="checkbox" id="cb-n1" checked>
              <label class="checkbox__label" for="cb-n1">KX-219 · Ford Transit</label>
            </div>
            <div class="checkbox">
              <input class="checkbox__input" type="checkbox" id="cb-n2" checked>
              <label class="checkbox__label" for="cb-n2">KX-220 · Ford Transit</label>
            </div>
            <div class="checkbox">
              <input class="checkbox__input" type="checkbox" id="cb-n3" checked>
              <label class="checkbox__label" for="cb-n3">LM-044 · Iveco Daily</label>
            </div>
            <div class="checkbox">
              <input class="checkbox__input" type="checkbox" id="cb-n4">
              <label class="checkbox__label" for="cb-n4">LM-051 · Iveco Daily</label>
            </div>
            <div class="checkbox">
              <input class="checkbox__input" type="checkbox" id="cb-n5">
              <label class="checkbox__label" for="cb-n5">PT-310 · Mercedes Sprinter</label>
            </div>
            </div>
            </div>
```

### checkbox-group · variant:group-vertical

```html
<fieldset class="fieldset checkbox-group" aria-describedby="cg-v-hint">
              <legend class="fieldset__legend">Which checks were done?</legend>
              <p class="field__hint" id="cg-v-hint">Select all that apply.</p>
              <div class="checkbox-group__items">
                <div class="checkbox">
                  <input class="checkbox__input" type="checkbox" id="cg-v1" name="checks" checked>
                  <label class="checkbox__label" for="cg-v1">Oil and coolant levels</label>
                </div>
                <div class="checkbox">
                  <input class="checkbox__input" type="checkbox" id="cg-v2" name="checks" aria-describedby="cg-v2-hint">
                  <label class="checkbox__label" for="cg-v2">Brake pads and discs</label>
                  <p class="checkbox__hint" id="cg-v2-hint">Measure pad thickness on both axles.</p>
                </div>
                <div class="checkbox">
                  <input class="checkbox__input" type="checkbox" id="cg-v3" name="checks">
                  <label class="checkbox__label" for="cg-v3">Wiper blades</label>
                </div>
              </div>
            </fieldset>
```

### checkbox-group · variant:group-horizontal

```html
<fieldset class="fieldset checkbox-group checkbox-group--horizontal">
              <legend class="fieldset__legend">Fuel type</legend>
              <div class="checkbox-group__items">
                <div class="checkbox">
                  <input class="checkbox__input" type="checkbox" id="cg-h1" name="fuel" checked>
                  <label class="checkbox__label" for="cg-h1">Diesel</label>
                </div>
                <div class="checkbox">
                  <input class="checkbox__input" type="checkbox" id="cg-h2" name="fuel">
                  <label class="checkbox__label" for="cg-h2">Electric</label>
                </div>
                <div class="checkbox">
                  <input class="checkbox__input" type="checkbox" id="cg-h3" name="fuel">
                  <label class="checkbox__label" for="cg-h3">Hybrid</label>
                </div>
              </div>
            </fieldset>
```

### checkbox-group · variant:group-error

```html
<fieldset class="fieldset checkbox-group" aria-describedby="cg-e-hint cg-e-err">
              <legend class="fieldset__legend">Which depots should the report include?</legend>
              <p class="field__hint" id="cg-e-hint">Select all that apply.</p>
              <p class="field__error" id="cg-e-err">
                <svg class="field__error-icon" aria-hidden="true" focusable="false"><use href="#icon-alert-circle"></use></svg>
                <span><span class="sr-only">Error: </span>Select at least one depot.</span>
              </p>
              <div class="checkbox-group__items">
                <div class="checkbox">
                  <input class="checkbox__input" type="checkbox" id="cg-e1" name="depots">
                  <label class="checkbox__label" for="cg-e1">North Yard</label>
                </div>
                <div class="checkbox">
                  <input class="checkbox__input" type="checkbox" id="cg-e2" name="depots">
                  <label class="checkbox__label" for="cg-e2">Harbour Road</label>
                </div>
                <div class="checkbox">
                  <input class="checkbox__input" type="checkbox" id="cg-e3" name="depots">
                  <label class="checkbox__label" for="cg-e3">Airport Logistics Park</label>
                </div>
              </div>
            </fieldset>
```

## API

Hook | Values | Purpose
.checkbox , .checkbox__input , .checkbox__label , .checkbox__hint | block / parts | One checkbox
.checkbox--sm | modifier class | 20px box for dense tables
.checkbox-group (+ .fieldset ), .checkbox-group__items | block / part | Group
.checkbox-group--horizontal | modifier class | Wrapping row of short options
checked , disabled , required | attribute | Native states
aria-invalid="true" , :user-invalid | attribute / pseudo-class | Single checkbox error
.field__error inside the group | part | Group error (left rule + red boxes)
data-indeterminate , data-select-all + aria-controls | attribute (js/checkbox.js) | Indeterminate and select-all
.is-hover | .is-focus-visible | docs-only class | Freezes a state

## Do and don't

Vehicle features Tail lift Refrigerated body Do group related options under a legend that asks the question. Yes No Don't use checkboxes for mutually exclusive answers — use radios.

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Moves to the next checkbox (each is a tab stop)
Space | Toggles the focused checkbox
- Role: native checkbox ; the indeterminate state is announced as "mixed" / "half checked".
- Name from <label for> ; clicking the label toggles, so the hit area is the whole text (box is 24px).
- Group: fieldset + legend gives the question; hint and error are linked to the fieldset with aria-describedby .
- Checked uses a check mark on a filled box, indeterminate a dash — shape plus color. Boxes have a 2px border at 3:1.
- Forced colors: the box uses CanvasText / Highlight and the mark stays visible.

## Tokens

Custom property | Purpose
--input-border , --input-bg | Unchecked box
--color-action-primary-bg | -hover , --color-action-primary-fg | Checked box and mark
--color-border-invalid | Invalid box, group error rule
--color-bg-muted , --color-text-disabled | Disabled
--icon-size-lg | -md , --radius-sm , --border-width-thick | Box size and shape
--focus-ring-* | Focus
