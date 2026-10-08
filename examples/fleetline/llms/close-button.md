# Close Button

Category: Actions · page `components/close-button.html` · CSS `css/components/close-button.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `close-button` — Close Button | core | ready · stable | state:default state:hover state:focus-visible state:active state:disabled |

## Usage

Use the close button to dismiss an overlay or a dismissible message: dialogs, drawers, toasts, alerts, popovers. It always sits in the top inline-end corner so mechanics and dispatchers find it in the same place everywhere.
- Name it "Close" in dialogs and drawers; be specific where several sit on one screen ("Dismiss notification", "Close vehicle details").
- Closing must not lose work silently: if a form is dirty, confirm or keep a draft.
- Don't use it to delete or cancel something — that is a destructive button with a label.

## Anatomy

- Container — <button type="button" class="close-btn" aria-label="Close"> , ghost, square
- Icon — svg.close-btn__icon ("x"), aria-hidden="true"

## Examples

### close-button · state:default

```html
<div class="ds-demo__row"><button type="button" class="close-btn" aria-label="Close"><svg class="close-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button><button type="button" class="close-btn close-btn--sm" aria-label="Dismiss notification"><svg class="close-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button><button type="button" class="close-btn close-btn--lg" aria-label="Close"><svg class="close-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button></div>
```

### close-button · state:hover

```html
<div class="ds-demo__row"><button type="button" class="close-btn is-hover" aria-label="Close"><svg class="close-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button></div>
```

### close-button · state:focus-visible

```html
<div class="ds-demo__row"><button type="button" class="close-btn is-focus-visible" aria-label="Close"><svg class="close-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button></div>
```

### close-button · state:active

```html
<div class="ds-demo__row"><button type="button" class="close-btn is-active" aria-label="Close"><svg class="close-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button></div>
```

### close-button · state:disabled

```html
<div class="ds-demo__row"><button type="button" class="close-btn" aria-label="Close" disabled><svg class="close-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button></div>
            <p>Only while a dialog is saving; say so in the dialog ("Saving work order…").</p>
```

### close-button · variant:placement

```html
<div style="display:grid; grid-template-columns:1fr auto; gap:var(--space-3); align-items:start; padding:var(--space-4); border:var(--border-width-thin) solid var(--color-border-default); border-radius:var(--radius-lg); max-inline-size:24rem;">
              <div><strong>Van KX-219</strong><p>Next service due in 3 days at North Yard depot.</p></div>
              <button type="button" class="close-btn" aria-label="Close vehicle details"><svg class="close-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button>
            </div>
            <p>Top inline-end corner, the same place in dialogs, drawers, toasts, alerts and popovers.</p>
```

## API

Hook | Values | Purpose
.close-btn | block class | 40px ghost close button
.close-btn--sm | --lg | modifier | 32px (toasts, alerts) / 48px (tablet)
.close-btn__icon | part | The x icon
aria-label | attribute (required) | "Close" or a specific name
commandfor + command="close" | attribute | Closes a <dialog> declaratively
disabled | attribute | Only while saving
.is-hover | .is-focus-visible | .is-active | docs-only class | Freeze a state

## Do and don't

Do give it a specific name when several dismiss buttons share a screen. X Don't use a letter "X" as text — screen readers read "X".

## Accessibility

Keyboard interaction
Key | Behavior
Enter / Space | Closes the surface
Esc | Handled by the surface (dialog/popover), not the button — keep both
- Focus returns to the element that opened the surface (native for <dialog> and invoker popovers).
- The icon is muted by default but meets 3:1 against surfaces ( --color-text-muted ); hover raises it to the default text color.
- Forced colors: shows a border on hover so the target is visible.

## Tokens

Custom property | Purpose
--button-height-* , --button-radius | Size and shape
--color-text-muted | -default | Icon color, rest / hover
--color-action-ghost-bg-hover | -bg-active | State fills
--icon-size-* , --icon-stroke | Icon
--focus-ring-* | Focus ring
