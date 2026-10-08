# Text Field

Category: Forms · page `components/text-field.html` · CSS `css/components/text-field.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `text-field` — Text Field | core | ready · stable | state:default state:hover state:focus-visible state:filled state:disabled state:read-only state:invalid size:sm size:md size:lg variant:with-prefix variant:with-suffix |

## Usage

Use a text field for short, single-line answers: plate numbers, names, odometer readings, part numbers. Use a textarea for notes longer than a sentence, a select or radios when the answer comes from a short known list, and a combobox when the list is long.
- Always inside a form field with a visible label.
- Set the right type , inputmode and autocomplete — on a mechanic's tablet that decides which keyboard appears.
- Size the field to the expected answer (a postcode field is narrow) with --field-max .
- Placeholders are optional examples ("e.g. KX-219"), never instructions or labels.

## Anatomy

- Container — input.input , or div.input.input--affixed when it has affixes; 1px --input-border , 8px radius
- Value / placeholder text
- Prefix (optional) — .input__affix before .input__control : currency, icon
- Suffix (optional) — .input__affix after the control: unit

## Examples

### text-field · state:default

```html
<div class="field">
              <label class="label" for="tf-default">Plate number</label>
              <input class="input" id="tf-default" name="plate" type="text" placeholder="e.g. KX-219" autocapitalize="characters" spellcheck="false">
            </div>
```

### text-field · state:hover

```html
<div class="field">
              <label class="label" for="tf-hover">Plate number</label>
              <input class="input is-hover" id="tf-hover" name="plate" type="text" placeholder="e.g. KX-219">
            </div>
```

### text-field · state:focus-visible

```html
<div class="field">
              <label class="label" for="tf-focus">Plate number</label>
              <input class="input is-focus-visible" id="tf-focus" name="plate" type="text" value="KX-2">
            </div>
```

### text-field · state:filled

```html
<div class="field">
              <label class="label" for="tf-filled">Assigned mechanic</label>
              <input class="input" id="tf-filled" name="mechanic" type="text" value="Priya Nair" autocomplete="off">
            </div>
```

### text-field · state:disabled

```html
<div class="field">
              <label class="label" for="tf-disabled">Depot</label>
              <input class="input" id="tf-disabled" name="depot" type="text" value="North Yard" disabled aria-describedby="tf-disabled-hint">
              <p class="field__hint" id="tf-disabled-hint">Vehicles can't change depot while a work order is open.</p>
            </div>
```

### text-field · state:read-only

```html
<div class="field">
              <label class="label" for="tf-readonly">Vehicle identification number (VIN)</label>
              <input class="input" id="tf-readonly" name="vin" type="text" value="WF0XXXTTGXKJ12345" readonly>
            </div>
```

### text-field · state:invalid

```html
<div class="field">
              <label class="label" for="tf-invalid">Email for service reports</label>
              <input class="input" id="tf-invalid" name="email" type="email" value="dispatch@northyard" autocomplete="email" aria-invalid="true" aria-describedby="tf-invalid-msg">
              <p class="field__error" id="tf-invalid-msg">
                <svg class="field__error-icon" aria-hidden="true" focusable="false"><use href="#icon-alert-circle"></use></svg>
                <span><span class="sr-only">Error: </span>Enter an email address like name@depot.com.</span>
              </p>
            </div>
```

### text-field · size:sm size:md size:lg

```html
<div class="stack stack--gap-3">
              <div class="stack stack--horizontal stack--gap-2">
                <input class="input input--sm" type="search" aria-label="Search vehicles, small" placeholder="Search vehicles">
                <button type="button" class="btn btn--secondary btn--sm">Search</button>
              </div>
              <div class="stack stack--horizontal stack--gap-2">
                <input class="input" type="search" aria-label="Search vehicles, medium" placeholder="Search vehicles">
                <button type="button" class="btn btn--secondary">Search</button>
              </div>
              <div class="stack stack--horizontal stack--gap-2">
                <input class="input input--lg" type="search" aria-label="Search vehicles, large" placeholder="Search vehicles">
                <button type="button" class="btn btn--secondary btn--lg">Search</button>
              </div>
            </div>
```

### text-field · variant:with-prefix

```html
<div class="stack stack--gap-4">
              <div class="field">
                <label class="label" for="tf-cost">Labour cost</label>
                <div class="input input--affixed">
                  <span class="input__affix" id="tf-cost-prefix">€</span>
                  <input class="input__control" id="tf-cost" name="labour_cost" type="text" inputmode="decimal" value="123.50" aria-describedby="tf-cost-prefix">
                </div>
              </div>
              <div class="field">
                <label class="label" for="tf-find">Find a part</label>
                <div class="input input--affixed">
                  <span class="input__affix"><svg class="icon" aria-hidden="true" focusable="false"><use href="#icon-search"></use></svg></span>
                  <input class="input__control" id="tf-find" name="part" type="search" placeholder="Part number or name">
                </div>
              </div>
            </div>
```

### text-field · variant:with-suffix

```html
<div class="field">
              <label class="label" for="tf-odo">Odometer reading</label>
              <div class="input input--affixed">
                <input class="input__control" id="tf-odo" name="odometer" type="text" inputmode="numeric" value="84,210" aria-describedby="tf-odo-suffix">
                <span class="input__affix" id="tf-odo-suffix">km</span>
              </div>
            </div>
```

## API

Hook | Values | Purpose
.input | block class | Bordered text input (on input , or on the wrapper when affixed)
.input--sm | --lg | modifier class | 32 / 40 (default) / 48px — same as buttons
.input--affixed , .input__control , .input__affix | modifier / parts | Prefix and suffix inside the border
disabled / readonly | attribute | Not editable (disabled also not focusable or submitted)
aria-invalid="true" , :user-invalid | attribute / pseudo-class | Invalid styling; pair with a .field__error
type , inputmode , autocomplete | attribute | Keyboard and autofill (email, tel, postal-code…)
.is-hover | .is-focus-visible | docs-only class | Freezes a state

## Do and don't

Driver phone number Do use the matching type and autocomplete so the right keyboard and autofill appear. Plate number Don't disable a field just to display a value people need to read or copy — use readonly .

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Focuses the field (read-only fields are focusable, disabled ones are skipped)
Typing, ← → , Home End | Native text editing
- Role: native textbox (or searchbox for type="search" ). Name from <label for> ; hint, affix and error via aria-describedby .
- Focus: the 2px teal focus ring plus a focus-colored border, so focus doesn't rely on a subtle border change. With affixes the ring wraps the whole field.
- Invalid: border doubles in weight and turns red, an icon and message appear — never color alone. :user-invalid only applies after interaction, so empty required fields aren't red on load.
- Boundary contrast: --input-border is color.border.strong , checked at 3:1 against the canvas.
- Font size is 16px at md and lg, so iOS doesn't zoom on focus; heights of 32–48px meet the 24px target minimum.

## Tokens

Custom property | Purpose
--input-border , --input-bg , --input-radius | Component tokens
--size-control-sm | -md | -lg | Heights
--color-text-muted | Hover border, affix text
--color-border-focus , --focus-ring-* | Focus
--color-border-invalid | Invalid border
--color-bg-subtle , --color-border-default | Read-only
--color-bg-muted , --color-border-subtle , --color-text-disabled | Disabled
--color-text-subtle | Placeholder
