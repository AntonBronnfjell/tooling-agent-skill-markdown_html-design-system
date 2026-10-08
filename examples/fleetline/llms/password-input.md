# Password Input

Category: Forms · page `components/password-input.html` · CSS `css/components/password-input.css` · JS `js/password-input.js` (export `init(root)`)

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `password-input` — Password Input | core | ready · stable | state:hidden state:visible state:invalid variant:strength-meter |

## Usage

Use a password input for sign-in and for setting a new password on the Fleetline workshop tablet or dispatch console. Use a one-time-code input for SMS or authenticator codes.
- Always offer Show : mechanics type with gloves on shared tablets and need to check what they typed.
- autocomplete="current-password" on sign-in, "new-password" when creating one, so password managers fill or generate correctly.
- When creating a password, list the requirements up front and show strength as a bar and a word.
- Never block paste — it is how password managers work.

## Anatomy

- Container — .input.input--affixed.password (from text field)
- Input — input.input__control[type=password]
- Reveal toggle — button.password__toggle[aria-pressed] , icon + "Show" / "Hide"
- Strength (optional) — meter.password__meter + .password__strength-text
- Requirements (optional) — ul.password__rules , items with data-met

## Examples

### password-input · state:hidden

```html
<div class="field">
              <label class="label" for="pw-hidden">Password</label>
              <div class="input input--affixed password">
                <input class="input__control" id="pw-hidden" name="password" type="password" autocomplete="current-password" spellcheck="false" value="kx219-northyard">
                <button type="button" class="password__toggle" aria-controls="pw-hidden" aria-pressed="false" hidden><svg class="icon" aria-hidden="true" focusable="false"><use href="#icon-eye"></use></svg><span data-label>Show</span><span class="sr-only"> password</span></button>
              </div>
            </div>
```

### password-input · state:visible

```html
<div class="field">
              <label class="label" for="pw-visible">Password</label>
              <div class="input input--affixed password">
                <input class="input__control" id="pw-visible" name="password" type="text" autocomplete="current-password" spellcheck="false" value="kx219-northyard">
                <button type="button" class="password__toggle" aria-controls="pw-visible" aria-pressed="true" hidden><svg class="icon" aria-hidden="true" focusable="false"><use href="#icon-eye-off"></use></svg><span data-label>Hide</span><span class="sr-only"> password</span></button>
              </div>
            </div>
```

### password-input · state:invalid

```html
<div class="field">
              <label class="label" for="pw-invalid">Password</label>
              <div class="input input--affixed password">
                <input class="input__control" id="pw-invalid" name="password" type="password" autocomplete="current-password" spellcheck="false" required aria-invalid="true" aria-describedby="pw-invalid-err">
                <button type="button" class="password__toggle" aria-controls="pw-invalid" aria-pressed="false" hidden><svg class="icon" aria-hidden="true" focusable="false"><use href="#icon-eye"></use></svg><span data-label>Show</span><span class="sr-only"> password</span></button>
              </div>
              <p class="field__error" id="pw-invalid-err">
                <svg class="field__error-icon" aria-hidden="true" focusable="false"><use href="#icon-alert-circle"></use></svg>
                <span><span class="sr-only">Error: </span>Enter your password.</span>
              </p>
            </div>
```

### password-input · variant:strength-meter

```html
<div class="field">
              <label class="label" for="pw-new">Create a password</label>
              <div class="input input--affixed password">
                <input class="input__control" id="pw-new" name="password" type="password" autocomplete="new-password" spellcheck="false" value="depot-north-2026" data-strength="pw-new-meter" data-rules="pw-new-rules" aria-describedby="pw-new-hint">
                <button type="button" class="password__toggle" aria-controls="pw-new" aria-pressed="false" hidden><svg class="icon" aria-hidden="true" focusable="false"><use href="#icon-eye"></use></svg><span data-label>Show</span><span class="sr-only"> password</span></button>
              </div>
              <p class="field__hint" id="pw-new-hint">Use at least 12 characters. A short phrase is easier to type on a tablet.</p>
              <div class="password__strength">
                <meter class="password__meter" id="pw-new-meter" min="0" max="4" low="2" high="3" optimum="4" value="3" aria-labelledby="pw-new-strength-l" aria-describedby="pw-new-strength"></meter>
                <span class="password__strength-text"><span class="sr-only" id="pw-new-strength-l">Password strength: </span><span id="pw-new-strength" data-strength-text>Good</span></span>
              </div>
              <ul class="password__rules" id="pw-new-rules">
                <li data-rule="length:12" data-met="true"><svg class="password__rule-icon password__rule-icon--met" aria-hidden="true" focusable="false"><use href="#icon-check"></use></svg><svg class="password__rule-icon password__rule-icon--todo" aria-hidden="true" focusable="false"><use href="#icon-circle"></use></svg><span>At least 12 characters</span></li>
                <li data-rule="digit" data-met="true"><svg class="password__rule-icon password__rule-icon--met" aria-hidden="true" focusable="false"><use href="#icon-check"></use></svg><svg class="password__rule-icon password__rule-icon--todo" aria-hidden="true" focusable="false"><use href="#icon-circle"></use></svg><span>A number</span></li>
                <li data-rule="symbol" data-met="false"><svg class="password__rule-icon password__rule-icon--met" aria-hidden="true" focusable="false"><use href="#icon-check"></use></svg><svg class="password__rule-icon password__rule-icon--todo" aria-hidden="true" focusable="false"><use href="#icon-circle"></use></svg><span>A symbol, like ! or #</span></li>
              </ul>
            </div>
```

## API

Hook | Values | Purpose
.password | block class (with .input--affixed ) | Password field with an inline toggle
.password__toggle | part | Reveal button; aria-pressed true while visible; aria-controls → input id
autocomplete | current-password | new-password | Password manager behavior
data-strength | meter id | Drives meter.password__meter (0–4) and its text
data-rules | list id | Updates li[data-rule] → data-met ; rules: length:N , digit , upper , symbol
aria-invalid="true" | attribute | Invalid styling (on the input)
.is-hover | .is-focus-visible | docs-only class | Freezes a toggle state

## Do and don't

Password Show password Do show a reveal toggle with a text label and keep paste working. Password Don't hide the rules in a placeholder or cap the maximum length.

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Input, then the Show button
Enter / Space on the toggle | Shows or hides the password; focus stays on the toggle
- The toggle is a real button named "Show password" (visible "Show" + visually hidden " password") with aria-pressed , so screen readers announce "Show password, toggle button, pressed".
- The password is hidden again on submit so it never lands in form history as plain text.
- Strength is a native meter with text ("Good"); requirement changes are announced politely after a typing pause, as "2 of 3 requirements met".
- Requirements use a check or an empty circle icon plus text — not color alone.
- Without JavaScript the toggle stays hidden and the field is a plain password input.

## Tokens

Custom property | Purpose
--input-* , --focus-ring-* | Field border and focus (from text field)
--color-action-ghost-bg | -hover | -active , --color-action-ghost-fg | Toggle button
--color-feedback-success|warning|danger-icon | Meter fill by strength
--color-feedback-success-fg | Met requirement
--color-bg-muted | Meter track
