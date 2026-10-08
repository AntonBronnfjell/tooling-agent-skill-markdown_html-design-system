# Form Field

Category: Forms · page `components/form-field.html` · CSS `css/components/form-field.css` · JS `js/form-field.js` (export `init(root)`)

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `label` — Label | core | ready · stable | variant:label variant:required variant:optional |
| `form-field` — Form Field Wrapper | core | ready · stable | variant:with-helper variant:with-error variant:with-counter variant:horizontal |
| `fieldset` — Fieldset / Legend | core | ready · stable | variant:fieldset |

## Usage

Every Fleetline form control sits inside a form field: a visible label, the control, optional helper text, and an error message when validation fails. The field wires these together with for / id and aria-describedby once, so every control behaves the same.
- Labels are nouns ("Plate number", "Odometer reading"), sentence case, no colon. Placeholders never replace labels.
- Helper text explains format or why we ask ("In kilometres, as shown on the dashboard"). It never repeats the label.
- Errors say what to do: "Enter a reading higher than the last one (84,210 km)". No blame, no "invalid input".
- Required vs optional : in long forms most fields are required, so mark the few optional ones with "(optional)". In short forms mark required fields with * and explain it once above the form.
- Use fieldset to group controls that answer one question: an address, a set of checkboxes, the parts of a date.

## Anatomy

- Field — .field , a grid with a 6px gap
- Label — label.label[for] , with optional .label__required or .label__optional
- Control — any form control ( .input , select, textarea…)
- Helper text — .field__hint , referenced by aria-describedby
- Error — .field__error : icon + visually hidden "Error:" + message, referenced by aria-describedby
- Counter (optional) — .field__counter , updated by js/form-field.js

## Examples

### label · variant:label

```html
<div class="field">
              <label class="label" for="lb-plate">Plate number</label>
              <input class="input" id="lb-plate" name="plate" type="text" autocomplete="off" autocapitalize="characters" spellcheck="false">
            </div>
```

### label · variant:required

```html
<p class="text-small text-muted">Fields marked * are required.</p>
            <div class="field">
              <label class="label" for="lb-vin">Vehicle identification number (VIN) <span class="label__required" aria-hidden="true">*</span></label>
              <input class="input" id="lb-vin" name="vin" type="text" required autocomplete="off" autocapitalize="characters" spellcheck="false">
            </div>
```

### label · variant:optional

```html
<div class="field">
              <label class="label" for="lb-nick">Fleet nickname <span class="label__optional">(optional)</span></label>
              <input class="input" id="lb-nick" name="nickname" type="text" autocomplete="off">
            </div>
```

### form-field · variant:with-helper

```html
<div class="field">
              <label class="label" for="ff-odo">Odometer reading</label>
              <input class="input" id="ff-odo" name="odometer" type="text" inputmode="numeric" aria-describedby="ff-odo-hint">
              <p class="field__hint" id="ff-odo-hint">In kilometres, as shown on the dashboard.</p>
            </div>
```

### form-field · variant:with-error

```html
<div class="field">
              <label class="label" for="ff-odo-err">Odometer reading</label>
              <input class="input" id="ff-odo-err" name="odometer" type="text" inputmode="numeric" value="8421" aria-invalid="true" aria-describedby="ff-odo-err-hint ff-odo-err-msg">
              <p class="field__hint" id="ff-odo-err-hint">In kilometres, as shown on the dashboard.</p>
              <p class="field__error" id="ff-odo-err-msg">
                <svg class="field__error-icon" aria-hidden="true" focusable="false"><use href="#icon-alert-circle"></use></svg>
                <span><span class="sr-only">Error: </span>Enter a reading higher than the last one (84,210 km).</span>
              </p>
            </div>
```

### form-field · variant:with-counter

```html
<div class="field">
              <label class="label" for="ff-title">Work order title</label>
              <input class="input" id="ff-title" name="title" type="text" value="Replace front brake pads" data-counter="ff-title-count" aria-describedby="ff-title-hint ff-title-count">
              <p class="field__hint" id="ff-title-hint">Mechanics see this on their task list. Keep it short.</p>
              <p class="field__counter" id="ff-title-count" data-max="60">Up to 60 characters</p>
            </div>
```

### form-field · variant:horizontal

```html
<div class="stack stack--gap-4">
              <div class="field field--horizontal">
                <label class="label" for="ff-h-plate">Plate number</label>
                <input class="input" id="ff-h-plate" name="plate" type="text" value="KX-219">
              </div>
              <div class="field field--horizontal">
                <label class="label" for="ff-h-depot">Home depot</label>
                <input class="input" id="ff-h-depot" name="depot" type="text" value="North Yard" aria-describedby="ff-h-depot-hint">
                <p class="field__hint" id="ff-h-depot-hint">Where the vehicle parks overnight.</p>
              </div>
            </div>
```

### fieldset · variant:fieldset

```html
<fieldset class="fieldset">
            <legend class="fieldset__legend">Depot address</legend>
            <div class="fieldset__body">
              <div class="field">
                <label class="label" for="fs-street">Street address</label>
                <input class="input" id="fs-street" name="street" type="text" autocomplete="street-address">
              </div>
              <div class="field">
                <label class="label" for="fs-city">Town or city</label>
                <input class="input" id="fs-city" name="city" type="text" autocomplete="address-level2">
              </div>
              <div class="field" style="--field-max: 12rem">
                <label class="label" for="fs-postcode">Postcode</label>
                <input class="input" id="fs-postcode" name="postcode" type="text" autocomplete="postal-code" autocapitalize="characters">
              </div>
            </div>
          </fieldset>
```

## API

Hook | Values | Purpose
.field , .field--horizontal | block / modifier | Field wrapper; label beside control from 48rem
--field-max | custom property | Max width (default 32rem); size fields to the expected answer
.label , .label__required , .label__optional | block / parts | Label and its markers
.field__hint , .field__error , .field__error-icon , .field__counter | parts | Helper, error, counter (reference all by aria-describedby )
required , aria-invalid="true" | attribute on the control | Required and invalid states
data-counter="<counter id>" , data-max | attribute | Enables the live counter ( js/form-field.js , init(root) )
.fieldset , .fieldset__legend , .fieldset__body | block / parts | Grouped controls

## Do and don't

Odometer reading
In kilometres.
Do keep a visible label and put format help in the hint. Don't use the placeholder as the label; it disappears as soon as someone types.

## Accessibility

- Name: <label for> gives the control its accessible name and makes the label a click target. Groups get their name from <legend> .
- Description: hint, error and counter ids go in aria-describedby , hint first. Screen readers read them after the name.
- Required: the required attribute is announced; the visual * is aria-hidden and explained once in text.
- Errors are never color alone: border weight changes, an icon appears and the message starts with visually hidden "Error:". Show inline errors after submit or blur, not on every keystroke; on submit, move focus to an error summary.
- Counter: the visible count updates live; a separate polite status region announces it after typing pauses (800ms) so speech isn't flooded. Typing past the limit is allowed and marked invalid.
Keyboard interaction
Key | Behavior
Tab / Shift + Tab | Moves between controls in reading order; labels, hints and legends aren't focusable

## Tokens

Custom property | Purpose
--font-size-sm | -md , --font-weight-semibold | Label and legend type
--color-text-default | -muted | Label, hint and counter text
--color-feedback-danger-fg | -icon | Error message, required marker and error icon
--space-1-5 | -4 | Gap inside a field; gap between fields
--icon-size-sm , --icon-stroke | Error icon
