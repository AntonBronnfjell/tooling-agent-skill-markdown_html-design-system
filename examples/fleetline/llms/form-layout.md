# Form Layout

Category: Patterns · page `patterns/form-layout.html` · CSS `css/patterns/form-layout.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `form-layout` — Form Layout | core | ready · beta | variant:single-column variant:two-column variant:sections variant:sticky-actions state:invalid |

## Usage

Use this layout for every page-level form in Fleetline: logging a service, creating a work order, editing a vehicle. Dialog forms reuse the same fields but put actions in the modal footer.
- One column, label above the control. It is the fastest to scan and complete, and it survives gloves, tablets and 400% zoom.
- Two columns only for short related fields (labour hours + parts cost, town + postcode), and only once the form is at least 28rem wide.
- Sections with a heading and one sentence of description once a form has more than about six fields. Use fieldset + legend when the group is one question (which checks were done?), a section with a heading when it is just a topic.
- Actions: primary first (inline-start), then Cancel as a secondary button. Verb + noun labels: "Save service log", not a generic word. On long forms the action bar sticks to the bottom of the screen.
- Errors: validate on submit. Show an error summary at the top, move focus to it, and repeat each message next to its field. Prefix the page <title> with "Error: ".
- Mark the minority: if most fields are required, mark the optional ones "(optional)".

## Anatomy

- Error summary (invalid state) — .alert.alert--danger.form-layout__summary with links to each field
- Section — section.form-layout__section : .form-layout__intro (heading + description) and .form-layout__fields
- Fields — .field , fieldset.fieldset , fieldset.date-field , fieldset.checkbox-group
- Row (optional) — .form-layout__row for two short related fields
- Divider — hr.divider between sections
- Action bar — .form-layout__actions , optionally --sticky

## Examples

### form-layout · variant:single-column

```html
<p class="ds-demo__label">variant:single-column — quick log from a tablet</p>
            <form class="form-layout" action="#form-layout" novalidate aria-label="Log service, single column demo">
              <div class="form-layout__intro"><h4 class="text-h4" id="fl1-t">Log service</h4><p class="text-small text-muted">All fields are required unless marked optional.</p></div>
              <div class="form-layout__fields">
                <div class="field">
                  <label class="label" for="fl1-vehicle">Vehicle</label>
                  <div class="select"><select class="select__control" id="fl1-vehicle" name="vehicle" required><option value="">Choose a vehicle</option><option>Van KX-219 · Ford Transit</option><option>Van KX-224 · Mercedes Sprinter</option><option>Truck TR-077 · Volvo FH</option><option>Pickup PU-012 · Toyota Hilux</option></select></div>
                </div>
                <div class="field">
                  <label class="label" for="fl1-odo">Odometer reading</label>
                  <div class="input input--affixed"><input class="input__control" id="fl1-odo" name="odometer" type="text" inputmode="numeric" required aria-describedby="fl1-odo-hint"><span class="input__affix">km</span></div>
                  <p class="field__hint" id="fl1-odo-hint">As shown on the dashboard.</p>
                </div>
                <div class="field">
                  <label class="label" for="fl1-notes">Notes <span class="label__optional">(optional)</span></label>
                  <textarea class="textarea" id="fl1-notes" name="notes" rows="3"></textarea>
                </div>
              </div>
              <div class="form-layout__actions">
                <button type="submit" class="btn btn--primary">Save service log</button>
                <button type="button" class="btn btn--secondary">Cancel</button>
              </div>
            </form>
```

### form-layout · variant:two-column

```html
<p class="ds-demo__label">variant:two-column — short related fields only</p>
            <form class="form-layout" action="#form-layout" novalidate aria-label="Log service, two-column demo">
              <div class="form-layout__intro"><h4 class="text-h4" id="fl2-t">Close work order WO-4182</h4><p class="text-small text-muted">Van KX-219 · Marta Quintero</p></div>
              <div class="form-layout__fields">
                <div class="form-layout__row">
                  <div class="field">
                    <label class="label" for="fl2-hours">Labour</label>
                    <div class="input input--affixed"><input class="input__control" id="fl2-hours" name="labour" type="text" inputmode="decimal" value="3.5"><span class="input__affix">h</span></div>
                  </div>
                  <div class="field">
                    <label class="label" for="fl2-parts">Parts cost</label>
                    <div class="input input--affixed"><span class="input__affix">€</span><input class="input__control" id="fl2-parts" name="parts" type="text" inputmode="decimal" value="412.80"></div>
                  </div>
                </div>
                <div class="field">
                  <label class="label" for="fl2-summary">Work done</label>
                  <textarea class="textarea" id="fl2-summary" name="summary" rows="3">Replaced front brake pads and discs. Road-tested 5 km.</textarea>
                </div>
              </div>
              <div class="form-layout__actions">
                <button type="submit" class="btn btn--primary">Close work order</button>
                <button type="button" class="btn btn--secondary">Cancel</button>
              </div>
            </form>
            <p>Labour and parts sit side by side from 28rem of form width and stack below it. Longer fields always keep the full width.</p>
```

### form-layout · variant:sections variant:sticky-actions

```html
<p class="ds-demo__label">variant:sections variant:sticky-actions — full "Log service" form, scroll inside the frame</p>
            <div style="block-size: 36rem; overflow: auto; padding-block-start: var(--space-6); padding-inline: var(--space-4); border: var(--border-width-thin) solid var(--color-border-default); border-radius: var(--radius-md);" role="region" aria-label="Log service form (scrollable example)" tabindex="0">
              <form class="form-layout" action="#form-layout" novalidate aria-label="Log service, sections demo">
                <div class="form-layout__intro"><h4 class="text-h3" id="fl3-t">Log service</h4><p class="text-muted">Record a completed service so the next one is scheduled. All fields are required unless marked optional.</p></div>

                <section class="form-layout__section" aria-labelledby="fl3-s1">
                  <div class="form-layout__intro"><h5 class="text-h5" id="fl3-s1">Vehicle</h5><p class="text-small text-muted">The odometer reading sets when the next service is due.</p></div>
                  <div class="form-layout__fields">
                    <div class="field">
                      <label class="label" for="fl3-vehicle">Vehicle</label>
                      <div class="select"><select class="select__control" id="fl3-vehicle" name="vehicle" required><option value="">Choose a vehicle</option><option selected>Van KX-219 · Ford Transit</option><option>Van KX-224 · Mercedes Sprinter</option><option>Truck TR-077 · Volvo FH</option></select></div>
                    </div>
                    <div class="field">
                      <label class="label" for="fl3-odo">Odometer reading</label>
                      <div class="input input--affixed"><input class="input__control" id="fl3-odo" name="odometer" type="text" inputmode="numeric" value="84,212" required aria-describedby="fl3-odo-hint"><span class="input__affix">km</span></div>
                      <p class="field__hint" id="fl3-odo-hint">Last recorded: 79,950 km on 2 June 2026.</p>
                    </div>
                  </div>
                </section>

                <hr class="divider">

                <section class="form-layout__section" aria-labelledby="fl3-s2">
                  <div class="form-layout__intro"><h5 class="text-h5" id="fl3-s2">Service</h5><p class="text-small text-muted">What was done and when.</p></div>
                  <div class="form-layout__fields">
                    <fieldset class="fieldset date-field" aria-describedby="fl3-date-hint">
                      <legend class="fieldset__legend">Service date</legend>
                      <p class="field__hint" id="fl3-date-hint">For example, 8 10 2026</p>
                      <div class="date-field__inputs">
                        <div class="date-field__item" data-part="day"><label class="label" for="fl3-day">Day</label><input class="input date-field__input date-field__input--2ch" id="fl3-day" name="service-day" type="text" inputmode="numeric" spellcheck="false" value="8"></div>
                        <div class="date-field__item" data-part="month"><label class="label" for="fl3-month">Month</label><input class="input date-field__input date-field__input--2ch" id="fl3-month" name="service-month" type="text" inputmode="numeric" spellcheck="false" value="10"></div>
                        <div class="date-field__item" data-part="year"><label class="label" for="fl3-year">Year</label><input class="input date-field__input date-field__input--4ch" id="fl3-year" name="service-year" type="text" inputmode="numeric" spellcheck="false" value="2026"></div>
                      </div>
                    </fieldset>
                    <fieldset class="fieldset checkbox-group" aria-describedby="fl3-checks-hint">
                      <legend class="fieldset__legend">Which checks were done?</legend>
                      <p class="field__hint" id="fl3-checks-hint">Select all that apply.</p>
                      <div class="checkbox-group__items">
                        <div class="checkbox"><input class="checkbox__input" type="checkbox" id="fl3-c1" name="checks" value="oil" checked><label class="checkbox__label" for="fl3-c1">Oil and filter changed</label></div>
                        <div class="checkbox"><input class="checkbox__input" type="checkbox" id="fl3-c2" name="checks" value="brakes" checked><label class="checkbox__label" for="fl3-c2">Brake pads and discs</label></div>
                        <div class="checkbox"><input class="checkbox__input" type="checkbox" id="fl3-c3" name="checks" value="tyres"><label class="checkbox__label" for="fl3-c3">Tyres checked for wear and pressure</label></div>
                        <div class="checkbox"><input class="checkbox__input" type="checkbox" id="fl3-c4" name="checks" value="lights"><label class="checkbox__label" for="fl3-c4">Lights and indicators</label></div>
                      </div>
                    </fieldset>
                    <fieldset class="fieldset radio-group">
                      <legend class="fieldset__legend">Is the vehicle fit to drive?</legend>
                      <div class="radio-group__items">
                        <div class="radio"><input class="radio__input" type="radio" id="fl3-r1" name="roadworthy" value="yes" checked><label class="radio__label" for="fl3-r1">Yes, release to dispatch</label></div>
                        <div class="radio"><input class="radio__input" type="radio" id="fl3-r2" name="roadworthy" value="no"><label class="radio__label" for="fl3-r2">No, keep it off the road</label></div>
                      </div>
                    </fieldset>
                  </div>
                </section>

                <hr class="divider">

                <section class="form-layout__section" aria-labelledby="fl3-s3">
                  <div class="form-layout__intro"><h5 class="text-h5" id="fl3-s3">Notes and follow-up</h5><p class="text-small text-muted">Dispatch sees these on the vehicle record.</p></div>
                  <div class="form-layout__fields">
                    <div class="field">
                      <label class="label" for="fl3-notes">Notes <span class="label__optional">(optional)</span></label>
                      <textarea class="textarea" id="fl3-notes" name="notes" rows="4" data-counter="fl3-notes-count" aria-describedby="fl3-notes-hint fl3-notes-count">Rear left tyre at 3 mm, replace at next service.</textarea>
                      <p class="field__hint" id="fl3-notes-hint">Defects found, parts to order, anything the driver should know.</p>
                      <p class="field__counter" id="fl3-notes-count" data-max="500">Up to 500 characters</p>
                    </div>
                    <div class="checkbox">
                      <input class="checkbox__input" type="checkbox" id="fl3-notify" name="notify" checked>
                      <label class="checkbox__label" for="fl3-notify">Text the driver when the van is ready</label>
                    </div>
                  </div>
                </section>

                <div class="form-layout__actions form-layout__actions--sticky">
                  <button type="submit" class="btn btn--primary">Save service log</button>
                  <button type="button" class="btn btn--secondary">Cancel</button>
                </div>
              </form>
            </div>
            <p>Three sections with headings and one-line descriptions, separated by dividers. Scroll the frame: the action bar stays at the bottom edge, primary first.</p>
```

### form-layout · state:invalid

```html
<p class="ds-demo__label">state:invalid — after submit, focus moves to the summary</p>
            <form class="form-layout" action="#form-layout" novalidate aria-label="Log service, error demo">
              <div class="form-layout__intro"><h4 class="text-h4" id="fl4-t">Log service</h4></div>
              <div class="alert alert--danger error-summary form-layout__summary" id="fl4-summary" tabindex="-1" aria-labelledby="fl4-summary-t">
                <svg class="alert__icon" aria-hidden="true" focusable="false"><use href="#icon-circle-x"></use></svg>
                <div class="alert__content">
                  <h5 class="alert__title" id="fl4-summary-t">There are 3 problems with this service log</h5>
                  <ul class="list error-summary__list alert__description">
                    <li><a class="link" href="#fl4-vehicle">Choose the vehicle you serviced</a></li>
                    <li><a class="link" href="#fl4-odo">Enter a reading higher than the last one (79,950 km)</a></li>
                    <li><a class="link" href="#fl4-day">Service date must be a real date</a></li>
                  </ul>
                </div>
              </div>
              <div class="form-layout__fields">
                <div class="field">
                  <label class="label" for="fl4-vehicle">Vehicle</label>
                  <p class="field__error" id="fl4-vehicle-err"><svg class="field__error-icon" aria-hidden="true" focusable="false"><use href="#icon-alert-circle"></use></svg><span><span class="sr-only">Error: </span>Choose the vehicle you serviced.</span></p>
                  <div class="select"><select class="select__control" id="fl4-vehicle" name="vehicle" required aria-invalid="true" aria-describedby="fl4-vehicle-err"><option value="">Choose a vehicle</option><option>Van KX-219 · Ford Transit</option><option>Van KX-224 · Mercedes Sprinter</option></select></div>
                </div>
                <div class="field">
                  <label class="label" for="fl4-odo">Odometer reading</label>
                  <p class="field__hint" id="fl4-odo-hint">Last recorded: 79,950 km on 2 June 2026.</p>
                  <p class="field__error" id="fl4-odo-err"><svg class="field__error-icon" aria-hidden="true" focusable="false"><use href="#icon-alert-circle"></use></svg><span><span class="sr-only">Error: </span>Enter a reading higher than the last one (79,950 km).</span></p>
                  <div class="input input--affixed"><input class="input__control" id="fl4-odo" name="odometer" type="text" inputmode="numeric" value="7,995" aria-invalid="true" aria-describedby="fl4-odo-hint fl4-odo-err"><span class="input__affix">km</span></div>
                </div>
                <fieldset class="fieldset date-field" aria-describedby="fl4-date-hint fl4-date-err">
                  <legend class="fieldset__legend">Service date</legend>
                  <p class="field__hint" id="fl4-date-hint">For example, 8 10 2026</p>
                  <p class="field__error" id="fl4-date-err"><svg class="field__error-icon" aria-hidden="true" focusable="false"><use href="#icon-alert-circle"></use></svg><span><span class="sr-only">Error: </span>Service date must be a real date.</span></p>
                  <div class="date-field__inputs">
                    <div class="date-field__item" data-part="day"><label class="label" for="fl4-day">Day</label><input class="input date-field__input date-field__input--2ch" id="fl4-day" name="service-day" type="text" inputmode="numeric" spellcheck="false" value="31" aria-invalid="true"></div>
                    <div class="date-field__item" data-part="month"><label class="label" for="fl4-month">Month</label><input class="input date-field__input date-field__input--2ch" id="fl4-month" name="service-month" type="text" inputmode="numeric" spellcheck="false" value="9" aria-invalid="true"></div>
                    <div class="date-field__item" data-part="year"><label class="label" for="fl4-year">Year</label><input class="input date-field__input date-field__input--4ch" id="fl4-year" name="service-year" type="text" inputmode="numeric" spellcheck="false" value="2026" aria-invalid="true"></div>
                  </div>
                </fieldset>
              </div>
              <div class="form-layout__actions">
                <button type="submit" class="btn btn--primary">Save service log</button>
                <button type="button" class="btn btn--secondary">Cancel</button>
              </div>
            </form>
            <p>The summary title counts the problems; each link moves focus to its field and repeats the inline message word for word. Entered values are kept.</p>
```

## API

Hook | Values | Purpose
.form-layout | block on <form> | Single column, max --size-container-sm ; size container for rows
.form-layout__section | __intro | __fields | parts | Topic group, its heading + description, the field stack
.form-layout__row | part | Two short related fields side by side from 28rem
.form-layout__actions + --sticky | part + modifier | Action bar; sticky to the bottom of the scrollport
.form-layout__summary | part on .alert--danger | Error summary; tabindex="-1" so it can take focus
aria-invalid="true" + .field__error | attribute + part | Inline error, referenced by aria-describedby

## Do and don't

Do keep one column and put only short, related fields (labour + parts cost) in a row. Don't lay unrelated fields out in two columns: people skip the right-hand column and the tab order zig-zags.

## Accessibility

Keyboard and focus behavior
Moment | Behavior
Submit with errors | Focus moves to the error summary ( tabindex="-1" ); its heading is read first, then the list of links
Enter on a summary link | Moves focus to the field (or the first input of a date field); the inline error is read through aria-describedby
Tab | Follows the visual order: sections top to bottom, row fields left to right, then the action bar
- Every control has a visible <label> ; groups use fieldset + legend .
- Errors are never color alone: icon, thicker border and a message that starts with visually hidden "Error:".
- The sticky action bar never covers the focused field: focused elements scroll into view above it (WCAG 2.4.11). Keep it to one row of buttons.
- Without JavaScript the server renders the summary and inline errors; with it, the same markup is inserted and focused.

## Tokens

Custom property | Purpose
--size-container-sm | Maximum form width
--space-8 , --space-5 , --space-4 , --space-3 , --space-1 | Between sections, fields, row columns, actions, heading and description
--color-bg-surface , --color-border-default , --z-sticky | Sticky action bar surface, top rule and stacking
