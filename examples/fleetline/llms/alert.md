# Alert

Category: Feedback · page `components/alert.html` · CSS `css/components/alert.css` · JS `js/alert.js` (export `init(root)`)

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `alert` — Alert Banner (inline) | core | ready · stable | variant:info variant:success variant:warning variant:danger variant:dismissible variant:with-actions |

## Usage

Use an inline alert for a message about the content it sits next to that should stay visible until resolved: an overdue vehicle on its detail page, a failed import above the table, a confirmation after saving a form.
- Info — neutral context ("Telematics sync runs every 15 minutes").
- Success — an action finished and the result is on this page.
- Warning — something needs attention soon ("Vehicle KX-24 is overdue for service").
- Danger — something failed or is blocked; say how to fix it.
For brief confirmations that don't need to stay, use a toast . Content: title states what happened in ≤ 8 words; description says why and what to do; actions are verb + object ("Schedule service"). Don't make every alert dismissible: danger alerts stay until the problem is fixed.

## Anatomy

- Container — .alert.alert--{tone} , tinted fill and a 4px inline-start bar
- Icon — svg.alert__icon , different shape per tone, aria-hidden
- Title — .alert__title
- Description — .alert__description
- Actions (optional) — .alert__actions
- Dismiss (optional) — .alert__dismiss icon button

## Examples

### alert · variant:info

```html
<div class="alert alert--info">
              <svg class="alert__icon" aria-hidden="true" focusable="false"><use href="#icon-info"></use></svg>
              <div class="alert__content">
                <p class="alert__title">Telematics sync every 15 minutes</p>
                <p class="alert__description">Odometer readings on this page can be up to 15 minutes old.</p>
              </div>
            </div>
```

### alert · variant:success

```html
<div class="alert alert--success">
              <svg class="alert__icon" aria-hidden="true" focusable="false"><use href="#icon-circle-check"></use></svg>
              <div class="alert__content">
                <p class="alert__title">Service plan saved</p>
                <p class="alert__description">KX-24 is next due for a brake inspection at 104,000 km.</p>
              </div>
            </div>
```

### alert · variant:warning

```html
<div class="alert alert--warning">
              <svg class="alert__icon" aria-hidden="true" focusable="false"><use href="#icon-triangle-alert"></use></svg>
              <div class="alert__content">
                <p class="alert__title">Vehicle KX-24 is overdue for service</p>
                <p class="alert__description">Brake inspection was due at 84,000 km. It's now at 85,200 km.</p>
              </div>
            </div>
```

### alert · variant:danger

```html
<div class="alert alert--danger">
              <svg class="alert__icon" aria-hidden="true" focusable="false"><use href="#icon-circle-x"></use></svg>
              <div class="alert__content">
                <p class="alert__title">We couldn't import 3 vehicles</p>
                <p class="alert__description">Rows 4, 9 and 17 have no VIN. Add the VINs to the file and import it again.</p>
              </div>
            </div>
```

### alert · variant:dismissible

```html
<div class="alert alert--info" id="alert-new-report">
              <svg class="alert__icon" aria-hidden="true" focusable="false"><use href="#icon-info"></use></svg>
              <div class="alert__content">
                <p class="alert__title">Fuel report moved</p>
                <p class="alert__description">Monthly fuel reports are now under Reports › Costs.</p>
              </div>
              <button type="button" class="btn btn--ghost btn--sm alert__dismiss" aria-label="Dismiss: Fuel report moved">
                <svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg>
              </button>
            </div>
```

### alert · variant:with-actions

```html
<div class="alert alert--warning">
              <svg class="alert__icon" aria-hidden="true" focusable="false"><use href="#icon-triangle-alert"></use></svg>
              <div class="alert__content">
                <p class="alert__title">Vehicle KX-24 is overdue for service</p>
                <p class="alert__description">Brake inspection is 1,200 km overdue. Book it before the next dispatch.</p>
                <div class="alert__actions">
                  <button type="button" class="btn btn--secondary btn--sm">Schedule service</button>
                  <a class="btn btn--ghost btn--sm" href="#alert">View service plan</a>
                </div>
              </div>
            </div>
```

## API

Hook | Values | Purpose
.alert | block | Container (info tone by default)
.alert--info | --success | --warning | --danger | modifier | Tone
.alert__icon | __content | __title | __description | __actions | __dismiss | parts | See anatomy
role="status" | "alert" | attribute | Only when inserted dynamically: polite / assertive announcement
data-alert-return="id" | attribute on dismiss | Where focus goes after dismissing (default: next focusable element)
alert:dismiss | event | Fired on the alert so apps can remember the choice

## Do and don't

We couldn't save WO-1042
The connection dropped. Your changes are kept — try again.
Do say what happened and how to fix it.
Error 500
Don't show codes without meaning, or rely on red alone to signal a problem.

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Reaches actions and the dismiss button in reading order
Enter / Space on dismiss | Hides the alert and moves focus to the next element, so focus isn't lost
- Static alerts have no role — they're read in order. Add role="status" or role="alert" only when inserting the alert after page load, and insert into an element that's already in the DOM.
- Tone is never color alone: each tone has its own icon shape and the title says what happened.
- The dismiss button's name includes the alert title ("Dismiss: Fuel report moved"), so it's clear out of context.
- Contrast: color.feedback.*.fg on color.feedback.*.bg pairs are checked at 4.5:1 in every theme.
- Forced colors: border and icon switch to CanvasText .

## Tokens

Custom property | Purpose
--color-feedback-{info|success|warning|danger}-bg | Fill
--color-feedback-{tone}-fg | Text
--color-feedback-{tone}-border | Border and inline-start bar
--color-feedback-{tone}-icon | Icon
--radius-md , --space-1 | -3 | -4 | Shape, bar width, padding
