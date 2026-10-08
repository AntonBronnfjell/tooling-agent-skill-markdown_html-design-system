# Error Summary

Category: Forms · page `components/error-summary.html` · CSS `css/components/error-summary.css` · JS `js/error-summary.js` (export `init(root)`)

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `error-summary` — Error Summary | core | ready · stable | state:with-errors |

## Usage

Show an error summary at the top of a form when the user submits and anything is invalid. It lists every problem as a link to the field, receives focus so screen-reader and keyboard users land on it, and the page title gets an "Error: " prefix. Use it together with inline field errors, never instead of them.
Don't use it for a single-field form where the inline error is right next to the button, or for system errors (use an alert).
Copy: the title says how many problems there are ("There are 2 problems with this service log"); each item uses the same words as the inline error.

## Anatomy

- Container (danger alert surface, focusable with tabindex="-1" )
- Icon
- Title with the number of problems
- List of links, one per invalid field, in field order

## Examples

### error-summary · state:with-errors

```html
<div class="alert alert--danger error-summary" id="es1" tabindex="-1" aria-labelledby="es1-t">
              <svg class="alert__icon" aria-hidden="true" focusable="false"><use href="#icon-circle-x"></use></svg>
              <div class="alert__content">
                <h4 class="alert__title" id="es1-t">There are 2 problems with this service log</h4>
                <ul class="list error-summary__list">
                  <li><a class="link" href="#es-vehicle">Choose the vehicle you serviced</a></li>
                  <li><a class="link" href="#es-odo">Enter a reading higher than the last one (79,950 km)</a></li>
                </ul>
              </div>
            </div>
            <p class="text-small">Fields: <span id="es-vehicle">Vehicle</span> · <span id="es-odo">Odometer reading</span></p>
```

## API

Hook | Values | Purpose
.error-summary | on .alert.alert--danger | Focus ring and list spacing
tabindex="-1" | attribute | Lets js/error-summary.js move focus to it
init(root) | js/error-summary.js | Focuses the first summary on load and prefixes the title with "Error: "; links move focus to their field

## Do and don't

Link each problem to its field, using the same words as the inline error.
Do keep the summary and inline errors in sync.
"Please correct the errors below."
Don't show a generic message without the list of problems.

## Accessibility

- Focus moves to the summary after a failed submit, so its title and list are read first; it isn't a live region (focus already announces it).
- The page <title> gets an "Error: " prefix (WCAG 3.3.1).
- Each link targets the field's id; following it moves focus to the field, whose aria-describedby includes the inline error.
- Color is not the only signal: icon, title text and the list itself.

## Tokens

Uses the alert's danger tokens ( --color-feedback-danger-* ) and --focus-ring-* .
