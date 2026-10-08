# Date Field

Category: Forms · page `components/date-field.html` · CSS `css/components/date-field.css` · JS `js/date-field.js` (export `init(root)`)

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `date-field` — Date field (memorable date, segmented) | core | ready · stable | state:default state:focus-visible state:invalid state:partial-invalid state:disabled variant:day-month-year variant:month-year variant:locale-order |

## Usage

Use a date field for dates people know or can copy from a document: last service date, registration date, MOT expiry on a certificate, a driver's date of birth. Use a date picker when people need to find a date relative to today (booking a bay next Tuesday).
- Ask the question in the legend ("When was the vehicle last serviced?") and give an example in the hint ("For example, 14 3 2026").
- Plain text inputs with inputmode="numeric" — not type=number (spinners, lost leading zeros).
- Accept "3", "03" and month names ("March"); check real dates (no 31 February) and ranges ("must be in the past").
- Never auto-advance between inputs.

## Anatomy

- Fieldset + legend — the question ( fieldset.fieldset.date-field )
- Hint — example date, linked to the fieldset
- Error (optional) — one message for the whole date
- Day, Month, Year — .date-field__item each with a label and a .input.date-field__input sized in characters

## Examples

### date-field · state:default variant:day-month-year

```html
<fieldset class="fieldset date-field" aria-describedby="df-default-hint">
              <legend class="fieldset__legend">When was the vehicle last serviced?</legend>
              <p class="field__hint" id="df-default-hint">For example, 14 3 2026</p>
              <div class="date-field__inputs">
                <div class="date-field__item" data-part="day">
                  <label class="label" for="df-default-day">Day</label>
                  <input class="input date-field__input date-field__input--2ch" id="df-default-day" name="df-default-day" type="text" inputmode="numeric" spellcheck="false">
                </div>
                <div class="date-field__item" data-part="month">
                  <label class="label" for="df-default-month">Month</label>
                  <input class="input date-field__input date-field__input--2ch" id="df-default-month" name="df-default-month" type="text" inputmode="numeric" spellcheck="false">
                </div>
                <div class="date-field__item" data-part="year">
                  <label class="label" for="df-default-year">Year</label>
                  <input class="input date-field__input date-field__input--4ch" id="df-default-year" name="df-default-year" type="text" inputmode="numeric" spellcheck="false">
                </div>
              </div>
            </fieldset>
```

### date-field · state:focus-visible

```html
<fieldset class="fieldset date-field" aria-describedby="df-focus-hint">
              <legend class="fieldset__legend">When was the vehicle last serviced?</legend>
              <p class="field__hint" id="df-focus-hint">For example, 14 3 2026</p>
              <div class="date-field__inputs">
                <div class="date-field__item" data-part="day">
                  <label class="label" for="df-focus-day">Day</label>
                  <input class="input date-field__input date-field__input--2ch" id="df-focus-day" name="df-focus-day" type="text" inputmode="numeric" spellcheck="false" value="14">
                </div>
                <div class="date-field__item" data-part="month">
                  <label class="label" for="df-focus-month">Month</label>
                  <input class="input is-focus-visible date-field__input date-field__input--2ch" id="df-focus-month" name="df-focus-month" type="text" inputmode="numeric" spellcheck="false">
                </div>
                <div class="date-field__item" data-part="year">
                  <label class="label" for="df-focus-year">Year</label>
                  <input class="input date-field__input date-field__input--4ch" id="df-focus-year" name="df-focus-year" type="text" inputmode="numeric" spellcheck="false">
                </div>
              </div>
            </fieldset>
```

### date-field · state:invalid

```html
<fieldset class="fieldset date-field" aria-describedby="df-invalid-hint df-invalid-err">
              <legend class="fieldset__legend">When was the vehicle last serviced?</legend>
              <p class="field__hint" id="df-invalid-hint">For example, 14 3 2026</p>
              <p class="field__error" id="df-invalid-err">
                <svg class="field__error-icon" aria-hidden="true" focusable="false"><use href="#icon-alert-circle"></use></svg>
                <span><span class="sr-only">Error: </span>Date the vehicle was last serviced must be a real date.</span>
              </p>
              <div class="date-field__inputs">
                <div class="date-field__item" data-part="day">
                  <label class="label" for="df-invalid-day">Day</label>
                  <input class="input date-field__input date-field__input--2ch" id="df-invalid-day" name="df-invalid-day" type="text" inputmode="numeric" spellcheck="false" value="31" aria-invalid="true">
                </div>
                <div class="date-field__item" data-part="month">
                  <label class="label" for="df-invalid-month">Month</label>
                  <input class="input date-field__input date-field__input--2ch" id="df-invalid-month" name="df-invalid-month" type="text" inputmode="numeric" spellcheck="false" value="2" aria-invalid="true">
                </div>
                <div class="date-field__item" data-part="year">
                  <label class="label" for="df-invalid-year">Year</label>
                  <input class="input date-field__input date-field__input--4ch" id="df-invalid-year" name="df-invalid-year" type="text" inputmode="numeric" spellcheck="false" value="2026" aria-invalid="true">
                </div>
              </div>
            </fieldset>
```

### date-field · state:partial-invalid

```html
<fieldset class="fieldset date-field" aria-describedby="df-partial-hint df-partial-err">
              <legend class="fieldset__legend">When was the vehicle registered?</legend>
              <p class="field__hint" id="df-partial-hint">For example, 27 3 2019</p>
              <p class="field__error" id="df-partial-err">
                <svg class="field__error-icon" aria-hidden="true" focusable="false"><use href="#icon-alert-circle"></use></svg>
                <span><span class="sr-only">Error: </span>Date the vehicle was registered must include a year.</span>
              </p>
              <div class="date-field__inputs">
                <div class="date-field__item" data-part="day">
                  <label class="label" for="df-partial-day">Day</label>
                  <input class="input date-field__input date-field__input--2ch" id="df-partial-day" name="df-partial-day" type="text" inputmode="numeric" spellcheck="false" value="27">
                </div>
                <div class="date-field__item" data-part="month">
                  <label class="label" for="df-partial-month">Month</label>
                  <input class="input date-field__input date-field__input--2ch" id="df-partial-month" name="df-partial-month" type="text" inputmode="numeric" spellcheck="false" value="3">
                </div>
                <div class="date-field__item" data-part="year">
                  <label class="label" for="df-partial-year">Year</label>
                  <input class="input date-field__input date-field__input--4ch" id="df-partial-year" name="df-partial-year" type="text" inputmode="numeric" spellcheck="false" aria-invalid="true">
                </div>
              </div>
            </fieldset>
```

### date-field · state:disabled

```html
<fieldset class="fieldset date-field" aria-describedby="df-disabled-hint" disabled>
              <legend class="fieldset__legend">When was the vehicle last serviced?</legend>
              <p class="field__hint" id="df-disabled-hint">Set automatically when the work order is closed.</p>
              <div class="date-field__inputs">
                <div class="date-field__item" data-part="day">
                  <label class="label" for="df-disabled-day">Day</label>
                  <input class="input date-field__input date-field__input--2ch" id="df-disabled-day" name="df-disabled-day" type="text" inputmode="numeric" spellcheck="false" value="14">
                </div>
                <div class="date-field__item" data-part="month">
                  <label class="label" for="df-disabled-month">Month</label>
                  <input class="input date-field__input date-field__input--2ch" id="df-disabled-month" name="df-disabled-month" type="text" inputmode="numeric" spellcheck="false" value="3">
                </div>
                <div class="date-field__item" data-part="year">
                  <label class="label" for="df-disabled-year">Year</label>
                  <input class="input date-field__input date-field__input--4ch" id="df-disabled-year" name="df-disabled-year" type="text" inputmode="numeric" spellcheck="false" value="2026">
                </div>
              </div>
            </fieldset>
```

### date-field · variant:month-year

```html
<fieldset class="fieldset date-field" aria-describedby="df-my-hint">
              <legend class="fieldset__legend">When does the operator licence expire?</legend>
              <p class="field__hint" id="df-my-hint">For example, 9 2027</p>
              <div class="date-field__inputs">
                <div class="date-field__item" data-part="month">
                  <label class="label" for="df-my-month">Month</label>
                  <input class="input date-field__input date-field__input--2ch" id="df-my-month" name="df-my-month" type="text" inputmode="numeric" spellcheck="false">
                </div>
                <div class="date-field__item" data-part="year">
                  <label class="label" for="df-my-year">Year</label>
                  <input class="input date-field__input date-field__input--4ch" id="df-my-year" name="df-my-year" type="text" inputmode="numeric" spellcheck="false">
                </div>
              </div>
            </fieldset>
```

### date-field · variant:locale-order

```html
<fieldset class="fieldset date-field" aria-describedby="df-us-hint" data-locale-order="en-US" lang="en-US">
              <legend class="fieldset__legend">When was the vehicle last serviced?</legend>
              <p class="field__hint" id="df-us-hint">For example, 3 14 2026 (month, day, year)</p>
              <div class="date-field__inputs">
                <div class="date-field__item" data-part="month">
                  <label class="label" for="df-us-month">Month</label>
                  <input class="input date-field__input date-field__input--2ch" id="df-us-month" name="df-us-month" type="text" inputmode="numeric" spellcheck="false" value="3">
                </div>
                <div class="date-field__item" data-part="day">
                  <label class="label" for="df-us-day">Day</label>
                  <input class="input date-field__input date-field__input--2ch" id="df-us-day" name="df-us-day" type="text" inputmode="numeric" spellcheck="false" value="14">
                </div>
                <div class="date-field__item" data-part="year">
                  <label class="label" for="df-us-year">Year</label>
                  <input class="input date-field__input date-field__input--4ch" id="df-us-year" name="df-us-year" type="text" inputmode="numeric" spellcheck="false" value="2026">
                </div>
              </div>
            </fieldset>
```

## API

Hook | Values | Purpose
.date-field (+ .fieldset ) | block class on fieldset | Groups the three parts under the question
.date-field__inputs , .date-field__item[data-part] | parts | Row of labelled inputs; data-part = day | month | year
.date-field__input--2ch | --4ch | modifier class | Character-based widths (day/month, year)
aria-invalid="true" | attribute on inputs | Only on the wrong part(s); all three when the whole date is wrong
disabled on the fieldset | attribute | Disables every part
data-locale-order | attribute (js/date-field.js) | Reorders parts for a locale (empty = page locale)
autocomplete="bday-*" | attribute | Birth dates only

## Do and don't

When was the vehicle last serviced?
For example, 14 3 2026
Day Month Year Do ask a clear question, label each part and show an example. Last service Don't use one masked field or a placeholder as the only format hint.

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Day → Month → Year (in locale order); focus never jumps on its own
Typing | Numbers, or a month name in Month (normalised on blur)
- Group: fieldset + legend , so each input is announced as "When was the vehicle last serviced?, group, Day, edit text".
- Hint and error are linked to the fieldset with aria-describedby ; aria-invalid marks only the part(s) to fix.
- No auto-advance: it breaks correcting a typo and confuses screen-reader users.
- Locale order changes the DOM, so reading and tab order match what is seen.

## Tokens

Custom property | Purpose
--input-* , --focus-ring-* , --color-border-invalid | Inputs (from text field)
--space-3 , --space-4 , --border-width-thin | Character widths and gaps
--color-border-invalid , --border-width-thick | Error rule
--color-text-disabled | Disabled labels
