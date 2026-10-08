# Tooltip

Category: Overlays · page `components/tooltip.html` · CSS `css/components/tooltip.css` · JS `js/tooltip.js` (export `init(root)`)

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `tooltip` — Tooltip | core | ready · stable | state:hidden state:visible variant:placements |

## Usage

Use a tooltip to name an icon-only button ("Schedule service") or add one short supplemental fact ("Synced from telematics 4 minutes ago"). It appears on hover and on keyboard focus.
- One short sentence, no links, no buttons. Interactive or longer content belongs in a toggletip or popover .
- Never hide essential information in a tooltip: touch users and mechanics wearing gloves may never see it.
- Don't put tooltips on disabled buttons (they can't be focused); use aria-disabled="true" and an inline reason instead.

## Anatomy

- Trigger — a focusable element with aria-describedby (or aria-labelledby for icon buttons) and data-tooltip-trigger
- Bubble — <div class="tooltip" popover="hint" role="tooltip"> , inverse surface, one line of text

## Examples

### tooltip · state:hidden

```html
<div class="ds-demo__row">
              <button type="button" class="btn btn--ghost" aria-labelledby="tt-schedule" data-tooltip-trigger="tt-schedule">
                <svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-calendar"></use></svg>
              </button>
              <div id="tt-schedule" class="tooltip" popover="hint" role="tooltip">Schedule service</div>
            </div>
            <p>Hover or Tab to the button: the tooltip appears after 400ms. Press Esc to hide it without moving focus.</p>
```

### tooltip · state:visible

```html
<div style="display: grid; justify-items: start; gap: var(--space-1-5);">
              <div class="tooltip is-open" role="tooltip" id="pv-tt-odo">Synced from telematics 4 minutes ago</div>
              <button type="button" class="btn btn--secondary btn--sm" aria-describedby="pv-tt-odo">Odometer 85,200 km</button>
            </div>
```

### tooltip · variant:placements

```html
<div class="ds-demo__row">
              <button type="button" class="btn btn--secondary btn--sm" aria-describedby="tt-top" data-tooltip-trigger="tt-top">Above</button>
              <div id="tt-top" class="tooltip" popover="hint" role="tooltip">Shows above, flips below at the top edge</div>
              <button type="button" class="btn btn--secondary btn--sm" aria-describedby="tt-bottom" data-tooltip-trigger="tt-bottom">Below</button>
              <div id="tt-bottom" class="tooltip tooltip--block-end" popover="hint" role="tooltip">Shows below</div>
              <button type="button" class="btn btn--secondary btn--sm" aria-describedby="tt-start" data-tooltip-trigger="tt-start">Inline start</button>
              <div id="tt-start" class="tooltip tooltip--inline-start" popover="hint" role="tooltip">Shows at the inline start</div>
              <button type="button" class="btn btn--ghost btn--sm" aria-labelledby="tt-end" data-tooltip-trigger="tt-end">
                <svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-trash"></use></svg>
              </button>
              <div id="tt-end" class="tooltip tooltip--inline-end" popover="hint" role="tooltip">Remove part</div>
            </div>
```

## API

Hook | Values | Purpose
.tooltip[popover="hint"][role="tooltip"] | block | Bubble; hint falls back to manual where unsupported
.tooltip--block-end | --inline-start | --inline-end | modifier | Preferred placement (default above)
data-tooltip-trigger="id" | attribute | Wires hover/focus/Esc behavior in js/tooltip.js
aria-describedby | aria-labelledby | attribute | Supplemental description, or the name of an icon-only button
init(root) | JS | Enhances every trigger in root ; safe to call twice
.is-open | docs-only class | Visible tooltip in page flow (same rule as :popover-open )

## Do and don't

Schedule service Do keep it to a few words that name or clarify. Vehicle KX-24 is overdue. Click here to open the service planner and book a slot. Don't put instructions, links or essential warnings in a tooltip. Use an alert.

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Focusing the trigger shows the tooltip after 400ms; leaving hides it
Esc | Hides the tooltip; focus stays on the trigger (inside a dialog, only the tooltip closes)
- Role tooltip ; the text reaches screen readers through aria-describedby / aria-labelledby whether or not it's visible (APG Tooltip).
- WCAG 1.4.13: dismissable (Esc), hoverable (the pointer can move onto the bubble), persistent (stays until hover/focus leaves).
- Contrast: --color-text-inverse on --color-bg-inverse is a checked 4.5:1 pair.
- Forced colors: the bubble switches to Canvas / CanvasText with a border.
- Where interestfor ships (Chrome 142+) it can replace the JS later; the JS stays the fallback.

## Tokens

Custom property | Purpose
--color-bg-inverse , --color-text-inverse | Bubble colors
--radius-sm , --shadow-md | Shape and lift
--font-size-xs , --font-weight-medium | Text
--space-1-5 | -2 | Padding and gap to trigger
--motion-duration-fast | Fade
