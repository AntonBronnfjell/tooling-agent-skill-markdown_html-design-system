# Textarea

Category: Forms · page `components/textarea.html` · CSS `css/components/textarea.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `textarea` — Textarea | core | ready · stable | state:default state:hover state:focus-visible state:filled state:disabled state:read-only state:invalid variant:auto-grow variant:with-counter |

## Usage

Use a textarea for answers longer than a sentence: defect descriptions, handover notes, reasons for a rejected inspection. Use a text field for single-line answers like a plate number or a part code.
- Always inside a form field with a visible label that says what to write ("Defect description", not "Notes").
- Size it to the expected answer with rows ; use .textarea--auto-grow when length varies a lot.
- When there is a limit, show a counter. Don't use maxlength : it silently cuts pasted text.

## Anatomy

- Container — textarea.textarea ; same border, radius and states as the text field
- Value / placeholder text
- Resize handle (vertical only; hidden when auto-grow, read-only or disabled)
- Counter (optional) — .field__counter wired with data-counter

## Examples

### textarea · state:default

```html
<div class="field">
              <label class="label" for="ta-default">Defect description</label>
              <textarea class="textarea" id="ta-default" name="notes" rows="4" placeholder="e.g. Brake warning light on after cold start"></textarea>
            </div>
```

### textarea · state:hover

```html
<div class="field">
              <label class="label" for="ta-hover">Defect description</label>
              <textarea class="textarea is-hover" id="ta-hover" name="notes" rows="4"></textarea>
            </div>
```

### textarea · state:focus-visible

```html
<div class="field">
              <label class="label" for="ta-focus">Defect description</label>
              <textarea class="textarea is-focus-visible" id="ta-focus" name="notes" rows="4">Coolant level low</textarea>
            </div>
```

### textarea · state:filled

```html
<div class="field">
              <label class="label" for="ta-filled">Work carried out</label>
              <textarea class="textarea" id="ta-filled" name="notes" rows="4">Front nearside tyre worn to 2 mm. Replaced with stock tyre from North Yard. Torque checked at 450 Nm.</textarea>
            </div>
```

### textarea · state:disabled

```html
<div class="field">
              <label class="label" for="ta-disabled">Handover notes</label>
              <textarea class="textarea" id="ta-disabled" name="notes" rows="4" disabled aria-describedby="ta-disabled-hint">Vehicle moved to bay 4 for overnight charging.</textarea>
            <p class="field__hint" id="ta-disabled-hint">Notes are locked once the work order is closed.</p>
            </div>
```

### textarea · state:read-only

```html
<div class="field">
              <label class="label" for="ta-readonly">Driver's defect report</label>
              <textarea class="textarea" id="ta-readonly" name="notes" rows="4" readonly>Vibration through steering wheel above 80 km/h. Reported by Tomás Ruiz, route 12.</textarea>
            </div>
```

### textarea · state:invalid

```html
<div class="field">
              <label class="label" for="ta-invalid">Reason for failing the inspection</label>
              <textarea class="textarea" id="ta-invalid" name="reason" rows="4" required aria-invalid="true" aria-describedby="ta-invalid-msg"></textarea>
            <p class="field__error" id="ta-invalid-msg">
              <svg class="field__error-icon" aria-hidden="true" focusable="false"><use href="#icon-alert-circle"></use></svg>
              <span><span class="sr-only">Error: </span>Enter the reason the vehicle failed inspection.</span>
            </p>
            </div>
```

### textarea · variant:auto-grow

```html
<div class="field">
              <label class="label" for="ta-grow">Handover notes</label>
              <textarea class="textarea textarea--auto-grow" id="ta-grow" name="notes" rows="4" rows="2" aria-describedby="ta-grow-hint"></textarea>
            <p class="field__hint" id="ta-grow-hint">Grows as you type, up to 12 lines.</p>
            </div>
```

### textarea · variant:with-counter

```html
<div class="field">
              <label class="label" for="ta-count">Message to driver</label>
              <textarea class="textarea" id="ta-count" name="message" rows="3" data-counter="ta-count-n" aria-describedby="ta-count-hint ta-count-n">KX-219 is ready for collection at North Yard, bay 2.</textarea>
              <p class="field__hint" id="ta-count-hint">Sent as a text message to the driver's phone.</p>
              <p class="field__counter" id="ta-count-n" data-max="160">Up to 160 characters</p>
            </div>
```

## API

Hook | Values | Purpose
.textarea | block class | Bordered multi-line input
.textarea--auto-grow | modifier class | Content-sized between min and max rows
--textarea-min-rows , --textarea-max-rows | custom property (number) | Auto-grow bounds (3 / 12)
rows | attribute | Initial height and the no- field-sizing fallback
data-counter + .field__counter[data-max] | attribute / part | Live counter (js/form-field.js); over the limit sets aria-invalid but never blocks typing
disabled / readonly / aria-invalid="true" | attribute | States
.is-hover | .is-focus-visible | docs-only class | Freezes a state

## Do and don't

Defect description Do label the field with what to write and give it room for the expected answer. Don't rely on a placeholder as the label or squeeze a long answer into one row.

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Moves focus into and out of the textarea (Tab is never captured)
Enter | Inserts a new line
Typing, arrows, Home End | Native text editing
- Role: native multi-line textbox . Name from <label for> ; hint, counter and error via aria-describedby .
- Counter: visible text updates on every keystroke; a separate polite status region announces it after a typing pause.
- Invalid: thicker red border, icon and message — never color alone. :user-invalid only applies after interaction.
- Text is 16px so iOS does not zoom; resize is vertical only so it never breaks the layout at 320px.

## Tokens

Custom property | Purpose
--input-border , --input-bg , --input-radius | Shared with text field
--size-control-md | Minimum height (2 × control)
--color-border-focus , --focus-ring-* | Focus
--color-border-invalid | Invalid border
--color-bg-subtle , --color-bg-muted , --color-text-disabled | Read-only and disabled
--color-text-subtle | Placeholder
