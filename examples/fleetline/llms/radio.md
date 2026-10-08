# Radio

Category: Forms · page `components/radio.html` · CSS `css/components/radio.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `radio` — Radio | core | ready · stable | state:unchecked state:checked state:hover state:focus-visible state:disabled state:invalid |
| `radio-group` — Radio Group | core | ready · stable | variant:group-vertical variant:group-horizontal variant:cards |

## Usage

Use radios when people must choose exactly one option from a short list (up to about 6) and it helps to see all options at once — service type, priority, which bay. Use a select for longer lists, checkboxes when several answers are allowed.
- Always in a fieldset whose legend asks the question.
- Order options logically (by frequency, severity or time) and avoid preselecting an answer people must think about.
- Cards add a description per option; use them when options need explaining (service plans), not for "Yes / No".

## Anatomy

- Circle — input[type=radio].radio__input (native, appearance: none ), 24px
- Dot — ::before , scales in when checked
- Label — label.radio__label[for] ; optional .radio__title for cards
- Hint (optional) — .radio__hint
- Group — fieldset.radio-group with legend, hint, error and .radio-group__items

## Examples

### radio · state:unchecked

```html
<div class="radio">
              <input class="radio__input" type="radio" id="rd-off" name="r1">
              <label class="radio__label" for="rd-off">Scheduled service</label>
            </div>
```

### radio · state:checked

```html
<div class="radio">
              <input class="radio__input" type="radio" id="rd-on" name="r2" checked>
              <label class="radio__label" for="rd-on">Scheduled service</label>
            </div>
```

### radio · state:hover

```html
<div class="stack stack--gap-3">
            <div class="radio">
              <input class="radio__input is-hover" type="radio" id="rd-hover" name="r3">
              <label class="radio__label" for="rd-hover">Roadside repair</label>
            </div>
            <div class="radio">
              <input class="radio__input is-hover" type="radio" id="rd-hover-on" name="r3" checked>
              <label class="radio__label" for="rd-hover-on">Workshop repair</label>
            </div>
            </div>
```

### radio · state:focus-visible

```html
<div class="radio">
              <input class="radio__input is-focus-visible" type="radio" id="rd-focus" name="r4" checked>
              <label class="radio__label" for="rd-focus">Workshop repair</label>
            </div>
```

### radio · state:disabled

```html
<div class="stack stack--gap-3">
            <div class="radio">
              <input class="radio__input" type="radio" id="rd-dis" name="r5" disabled aria-describedby="rd-dis-hint">
              <label class="radio__label" for="rd-dis">Bay 3 — lift</label>
              <p class="radio__hint" id="rd-dis-hint">Out of service until 14 March.</p>
            </div>
            <div class="radio">
              <input class="radio__input" type="radio" id="rd-dis-on" name="r6" checked disabled>
              <label class="radio__label" for="rd-dis-on">Bay 1 — pit</label>
            </div>
            </div>
```

### radio · state:invalid

```html
<fieldset class="fieldset radio-group" aria-describedby="rd-inv-err">
              <legend class="fieldset__legend">How urgent is the repair?</legend>
              <p class="field__error" id="rd-inv-err">
                <svg class="field__error-icon" aria-hidden="true" focusable="false"><use href="#icon-alert-circle"></use></svg>
                <span><span class="sr-only">Error: </span>Select how urgent the repair is.</span>
              </p>
              <div class="radio-group__items">
                <div class="radio">
                  <input class="radio__input" type="radio" id="rd-inv1" name="urgency" required>
                  <label class="radio__label" for="rd-inv1">Off the road now</label>
                </div>
                <div class="radio">
                  <input class="radio__input" type="radio" id="rd-inv2" name="urgency">
                  <label class="radio__label" for="rd-inv2">Within 48 hours</label>
                </div>
                <div class="radio">
                  <input class="radio__input" type="radio" id="rd-inv3" name="urgency">
                  <label class="radio__label" for="rd-inv3">At next service</label>
                </div>
              </div>
            </fieldset>
```

### radio-group · variant:group-vertical

```html
<fieldset class="fieldset radio-group">
              <legend class="fieldset__legend">Which bay should KX-219 go to?</legend>
              <div class="radio-group__items">
                <div class="radio">
                  <input class="radio__input" type="radio" id="rg-v1" name="bay" checked>
                  <label class="radio__label" for="rg-v1">Bay 1 — pit</label>
                </div>
                <div class="radio">
                  <input class="radio__input" type="radio" id="rg-v2" name="bay" aria-describedby="rg-v2-hint">
                  <label class="radio__label" for="rg-v2">Bay 2 — lift</label>
                  <p class="radio__hint" id="rg-v2-hint">Max 3.5 t.</p>
                </div>
                <div class="radio">
                  <input class="radio__input" type="radio" id="rg-v3" name="bay">
                  <label class="radio__label" for="rg-v3">Bay 4 — EV charging</label>
                </div>
              </div>
            </fieldset>
```

### radio-group · variant:group-horizontal

```html
<fieldset class="fieldset radio-group radio-group--horizontal">
              <legend class="fieldset__legend">Odometer unit</legend>
              <div class="radio-group__items">
                <div class="radio">
                  <input class="radio__input" type="radio" id="rg-h1" name="unit" checked>
                  <label class="radio__label" for="rg-h1">Kilometres</label>
                </div>
                <div class="radio">
                  <input class="radio__input" type="radio" id="rg-h2" name="unit">
                  <label class="radio__label" for="rg-h2">Miles</label>
                </div>
              </div>
            </fieldset>
```

### radio-group · variant:cards

```html
<fieldset class="fieldset radio-group radio-group--cards">
              <legend class="fieldset__legend">Service plan</legend>
              <div class="radio-group__items">
                <div class="radio">
                  <input class="radio__input" type="radio" id="rg-c1" name="plan" checked aria-describedby="rg-c1-hint">
                  <label class="radio__label" for="rg-c1"><span class="radio__title">Interim</span></label>
                  <p class="radio__hint" id="rg-c1-hint">Every 10,000 km or 6 months. Oil, filters, safety check.</p>
                </div>
                <div class="radio">
                  <input class="radio__input" type="radio" id="rg-c2" name="plan" aria-describedby="rg-c2-hint">
                  <label class="radio__label" for="rg-c2"><span class="radio__title">Full</span></label>
                  <p class="radio__hint" id="rg-c2-hint">Every 20,000 km or 12 months. Adds brakes, coolant, belts.</p>
                </div>
                <div class="radio">
                  <input class="radio__input" type="radio" id="rg-c3" name="plan" disabled aria-describedby="rg-c3-hint">
                  <label class="radio__label" for="rg-c3"><span class="radio__title">Major</span></label>
                  <p class="radio__hint" id="rg-c3-hint">Not available for vehicles under 3 years old.</p>
                </div>
              </div>
            </fieldset>
```

## API

Hook | Values | Purpose
.radio , .radio__input , .radio__label , .radio__title , .radio__hint | block / parts | One option
.radio-group (+ .fieldset ), .radio-group__items | block / part | Group
.radio-group--horizontal | modifier class | Row of 2–3 short options
.radio-group--cards | modifier class | Bordered tiles; label stretches over the tile
name , checked , disabled , required | attribute | Native states and grouping
.field__error inside the group, :user-invalid | part / pseudo-class | Invalid
.is-hover | .is-focus-visible | docs-only class | Freezes a state

## Do and don't

Priority High Normal Low Do ask the question in the legend and list every option. Send me service reminders Don't use a single radio for an opt-in — it can't be unchecked. Use a checkbox.

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Into the group (focuses the checked radio, or the first) and out of it — one tab stop
↓ → / ↑ ← | Next / previous option, selecting it (native, wraps)
Space | Selects the focused radio if none is checked
- Role: native radio in a fieldset (group) — arrow keys come from sharing a name .
- Checked = filled dot inside a teal ring, not color alone; circles are 24px with a 2px border at 3:1.
- Cards: the label's ::after covers the tile, so the whole card is clickable; the tile shows the focus ring and a 2px selected border plus tint.
- Hints are linked with aria-describedby ; the group error is linked to the fieldset.

## Tokens

Custom property | Purpose
--input-border , --input-bg | Unchecked circle
--color-action-primary-bg | -hover | Checked ring and dot
--color-selected-bg , --color-selected-border | Selected card
--color-border-default , --color-bg-surface , --radius-md | Card
--color-border-invalid | Invalid
--color-bg-muted , --color-text-disabled | Disabled
