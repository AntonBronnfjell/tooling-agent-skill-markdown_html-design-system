# Select

Category: Forms · page `components/select.html` · CSS `css/components/select.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `select` — Select | core | ready · stable | state:default state:hover state:focus-visible state:filled state:disabled state:read-only state:invalid variant:with-groups |

## Usage

Use a select to pick one option from a known list of about 5–15 items — depot, service type, vehicle class. Use radios for 2–5 options people should compare, and a combobox when the list is long or people know what they are looking for (a part number, one of 400 vehicles).
- Start with a prompt option ("Choose a depot", value="" ) unless there is a safe default.
- Group long lists with optgroup ; order options alphabetically or by frequency.
- It's a native <select> : the OS picker works with touch, screen readers and gloves.

## Anatomy

- Wrapper — .select , draws the chevron ( ::after , masked currentColor )
- Control — native select.select__control , same border, radius and heights as the text field
- Value or prompt option
- Picker — the OS list, or a token-styled ::picker(select) where customizable select is supported

## Examples

### select · state:default

```html
<div class="field">
              <label class="label" for="sl-default">Home depot</label>
              <div class="select">
                <select class="select__control" id="sl-default" name="depot">
                <option value="">Choose a depot</option>
                <option>North Yard</option>
                <option>Harbour Road</option>
                <option>Airport Logistics Park</option>
                <option>Westgate Industrial Estate</option>
                </select>
              </div>
            </div>
```

### select · state:hover

```html
<div class="field">
              <label class="label" for="sl-hover">Home depot</label>
              <div class="select">
                <select class="select__control is-hover" id="sl-hover" name="depot">
                <option value="">Choose a depot</option>
                <option>North Yard</option>
                <option>Harbour Road</option>
                <option>Airport Logistics Park</option>
                <option>Westgate Industrial Estate</option>
                </select>
              </div>
            </div>
```

### select · state:focus-visible

```html
<div class="field">
              <label class="label" for="sl-focus">Home depot</label>
              <div class="select">
                <select class="select__control is-focus-visible" id="sl-focus" name="depot">
                <option value="">Choose a depot</option>
                <option>North Yard</option>
                <option selected>Harbour Road</option>
                <option>Airport Logistics Park</option>
                <option>Westgate Industrial Estate</option>
                </select>
              </div>
            </div>
```

### select · state:filled

```html
<div class="field">
              <label class="label" for="sl-filled">Home depot</label>
              <div class="select">
                <select class="select__control" id="sl-filled" name="depot">
                <option value="">Choose a depot</option>
                <option selected>North Yard</option>
                <option>Harbour Road</option>
                <option>Airport Logistics Park</option>
                <option>Westgate Industrial Estate</option>
                </select>
              </div>
            </div>
```

### select · state:disabled

```html
<div class="field">
              <label class="label" for="sl-disabled">Home depot</label>
              <div class="select">
                <select class="select__control" id="sl-disabled" name="depot" disabled aria-describedby="sl-disabled-hint">
                <option value="">Choose a depot</option>
                <option selected>North Yard</option>
                <option>Harbour Road</option>
                <option>Airport Logistics Park</option>
                <option>Westgate Industrial Estate</option>
                </select>
              </div>
              <p class="field__hint" id="sl-disabled-hint">Vehicles can't change depot while a work order is open.</p>
            </div>
```

### select · state:read-only

```html
<div class="field">
              <label class="label" for="sl-readonly">Home depot</label>
              <div class="select">
                <select class="select__control" id="sl-readonly" name="depot" aria-readonly="true" aria-describedby="sl-readonly-hint">
                <option selected>Airport Logistics Park</option>
                </select>
              </div>
              <p class="field__hint" id="sl-readonly-hint">Set by the leasing contract.</p>
            </div>
```

### select · state:invalid

```html
<div class="field">
              <label class="label" for="sl-invalid">Home depot</label>
              <div class="select">
                <select class="select__control" id="sl-invalid" name="depot" required aria-invalid="true" aria-describedby="sl-invalid-err">
                <option value="">Choose a depot</option>
                <option>North Yard</option>
                <option>Harbour Road</option>
                <option>Airport Logistics Park</option>
                <option>Westgate Industrial Estate</option>
                </select>
              </div>
              <p class="field__error" id="sl-invalid-err">
                <svg class="field__error-icon" aria-hidden="true" focusable="false"><use href="#icon-alert-circle"></use></svg>
                <span><span class="sr-only">Error: </span>Select the depot where the vehicle parks overnight.</span>
              </p>
            </div>
```

### select · variant:with-groups

```html
<div class="field">
              <label class="label" for="sl-groups">Service type</label>
              <div class="select">
                <select class="select__control" id="sl-groups" name="depot">
                <option value="">Choose a service type</option>
                <optgroup label="Preventive">
                  <option>Interim service</option>
                  <option selected>Full service</option>
                  <option>Tachograph calibration</option>
                </optgroup>
                <optgroup label="Repair">
                  <option>Brakes</option>
                  <option>Suspension and steering</option>
                  <option>Electrical</option>
                </optgroup>
                <optgroup label="Compliance">
                  <option>Annual roadworthiness test</option>
                  <option>Emissions test</option>
                </optgroup>
                </select>
              </div>
            </div>
```

## API

Hook | Values | Purpose
.select + .select__control | block / part | Wrapper with chevron + native select
.select--sm | --lg | modifier class | 32 / 40 (default) / 48px — same as inputs and buttons
disabled , required | attribute | Native states
aria-invalid="true" , :user-invalid | attribute / pseudo-class | Invalid
aria-readonly="true" + one option | attribute | Read-only (focusable, submitted, no chevron)
option[value=""] | markup | Prompt option, shown muted while selected
.is-hover | .is-focus-visible | docs-only class | Freezes a state

## Do and don't

Home depot Choose a depot North Yard Harbour Road Airport Logistics Park Westgate Industrial Estate Do use a native select with a prompt option for a short, known list. Vehicle KX-219 KX-220 … 412 more vehicles Don't use a select for hundreds of options — use a combobox with search.

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Focuses the select
Space / Enter / Alt + ↓ | Opens the picker
↑ ↓ , typing | Moves between options / jumps by first letters
Esc | Closes the picker without changing the value
- Role: native combobox / listbox (by platform) — all keyboard and screen-reader behavior is native.
- The chevron is decorative (on the wrapper) and uses currentColor , so it follows themes and forced colors.
- Invalid: thicker red border, icon and message, linked with aria-describedby .
- Read-only keeps the value focusable and announced; only one option is rendered so it can't be changed.

## Tokens

Custom property | Purpose
--input-border , --input-bg , --input-radius | Shared with text field
--size-control-sm | -md | -lg | Heights
--color-text-muted | Chevron, prompt option
--color-border-focus , --focus-ring-* , --color-border-invalid | Focus, invalid
--color-bg-overlay , --overlay-radius , --overlay-shadow , --color-selected-* | Customizable picker
