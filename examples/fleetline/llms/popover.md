# Popover

Category: Overlays · page `components/popover.html` · CSS `css/components/popover.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `popover` — Popover | core | ready · stable | state:closed state:open variant:with-arrow variant:placements |

## Usage

Use a popover for a small amount of related, optional content next to its trigger: a vehicle summary from a table row, quick actions on a work order, a short form like "Snooze reminder". The page stays usable while it's open, and clicking outside or pressing Esc closes it.
- Use a tooltip instead for a single non-interactive line; a menu for a list of commands; a modal when the user must decide before going on.
- Keep it under ~22rem wide and a few lines tall. If it needs scrolling, it should be a drawer or a page.
- Title in sentence case naming the object ("Vehicle KX-24"); actions are verb + object ("Schedule service").

## Anatomy

- Trigger — a <button> with commandfor + command="toggle-popover" and an anchor-name
- Surface — <div class="popover" popover role="dialog"> , overlay surface and shadow
- Header (optional) — .popover__title and a close button
- Body — .popover__body , may contain links and controls
- Footer (optional) — .popover__footer actions
- Arrow (optional) — .popover__arrow , decorative

## Examples

### popover · state:closed

```html
<div class="ds-demo__row">
              <button type="button" class="btn btn--secondary" commandfor="pop-kx24" command="toggle-popover" style="anchor-name: --pop-kx24;">
                <svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-truck"></use></svg>
                <span class="btn__label">KX-24 details</span>
              </button>
            </div>
            <p>Closed: the trigger only. Activate it to open the real popover below the button.</p>
```

### popover · state:open

```html
<div class="popover is-open" role="group" aria-labelledby="pv-kx24-title">
              <div class="popover__header">
                <h4 class="popover__title" id="pv-kx24-title">Vehicle KX-24</h4>
                <button type="button" class="btn btn--ghost btn--sm" aria-label="Close">
                  <svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg>
                </button>
              </div>
              <div class="popover__body">
                <p>Ford Transit, Northside Depot. 85,200 km — brake inspection is 1,200 km overdue.</p>
              </div>
              <div class="popover__footer">
                <button type="button" class="btn btn--primary btn--sm">Schedule service</button>
                <a class="btn btn--ghost btn--sm" href="#popover">View history</a>
              </div>
            </div>
```

### popover · variant:with-arrow

```html
<div class="popover popover--arrow is-open" role="group" aria-labelledby="pv-arrow-title" style="margin-block-start: var(--space-2);">
              <span class="popover__arrow" aria-hidden="true"></span>
              <div class="popover__body">
                <p id="pv-arrow-title"><strong>Odometer synced 4 min ago</strong> from the KX-24 telematics unit.</p>
              </div>
            </div>
            <div class="ds-demo__row">
              <button type="button" class="btn btn--secondary btn--sm" commandfor="pop-arrow" command="toggle-popover" style="anchor-name: --pop-arrow;">Sync status</button>
            </div>
```

### popover · variant:placements

```html
<div class="ds-demo__row">
              <button type="button" class="btn btn--secondary btn--sm" commandfor="pop-below" command="toggle-popover" style="anchor-name: --pop-below;">Below</button>
              <button type="button" class="btn btn--secondary btn--sm" commandfor="pop-above" command="toggle-popover" style="anchor-name: --pop-above;">Above</button>
              <button type="button" class="btn btn--secondary btn--sm" commandfor="pop-start" command="toggle-popover" style="anchor-name: --pop-start;">Inline start</button>
              <button type="button" class="btn btn--secondary btn--sm" commandfor="pop-end" command="toggle-popover" style="anchor-name: --pop-end;">Inline end</button>
            </div>
            <p>Placements are logical, so "inline start" is the left in English and the right in Arabic. Near a viewport edge the popover flips with the shared <code>--flip-block</code> / <code>--flip-inline</code> tries.</p>
```

## API

Hook | Values | Purpose
.popover[popover] | block | Surface; popover (auto) gives light dismiss and Esc
commandfor="id" command="toggle-popover | show-popover | hide-popover" | invoker attributes | Open/close without JS; the browser exposes the expanded state on the trigger
anchor-name / position-anchor | inline style per instance | Ties the surface to its trigger
.popover--block-start | --inline-start | --inline-end | modifier | Preferred placement (default below, aligned to the inline start)
.popover--arrow + .popover__arrow | modifier + part | Pointer toward the trigger (block placements)
.popover__header | __title | __body | __footer | parts | See anatomy
.is-open | docs-only class | Renders an open popover in page flow (same rule as :popover-open )

## Do and don't

Vehicle summary + "Schedule service" in a popover next to the row.
Do keep popovers short and related to their trigger.
A 12-field "Edit vehicle" form inside a popover.
Don't put long forms in a popover: a stray click outside discards them. Use a modal or a page.

## Accessibility

Keyboard interaction
Key | Behavior
Enter / Space on trigger | Toggles the popover
Tab | From the trigger moves into the popover (it follows the trigger in focus order); can leave it — not a trap
Esc | Closes the popover and returns focus to the trigger
- Role: role="dialog" (non-modal) with aria-labelledby pointing to the title, or an aria-label .
- The trigger's expanded/collapsed state is exposed by the browser for invoker-controlled popovers; add aria-expanded yourself only when opening from script.
- Light dismiss is native for popover="auto" ; focus returns to the invoker when the popover closes with focus inside.
- Without anchor positioning the popover opens centered in the viewport — still fully usable.
- The arrow is decorative ( aria-hidden ). Forced colors: a CanvasText border keeps the surface visible.

## Tokens

Custom property | Purpose
--color-elevation-surface-overlay | Surface
--overlay-radius , --overlay-shadow | Shape and elevation
--color-border-default | Border and arrow edge
--space-2 | -3 | Gap to the trigger (larger with arrow)
--motion-duration-base | -fast , --motion-easing-enter | -exit | Fade in and out
