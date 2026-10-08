# Switch

Category: Forms · page `components/switch.html` · CSS `css/components/switch.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `switch` — Switch / Toggle | core | ready · stable | state:off state:on state:focus-visible state:disabled variant:with-label |

## Usage

Use a switch for a setting that takes effect immediately — notifications, showing retired vehicles on the map, auto-assigning work orders. Use a checkbox when the choice is only applied after pressing a Save or Submit button.
- The label names the setting that is on ("Text drivers about schedule changes"), never "On/Off" or a question.
- The setting changes the moment it is toggled — no Save button for it.
- If the change is saved to the server, set aria-busy="true" on the switch while saving and revert with an error message if it fails.

## Anatomy

- Track — input[type=checkbox][role=switch].switch__input (native, appearance: none ), 44 × 24px
- Thumb — ::before , moves to the end when on
- Label — label.switch__label[for]
- Hint (optional) — .switch__hint

## Examples

### switch · state:off

```html
<div class="switch">
              <input class="switch__input" type="checkbox" role="switch" id="sw-off">
              <label class="switch__label" for="sw-off">Show retired vehicles on the map</label>
            </div>
```

### switch · state:on

```html
<div class="switch">
              <input class="switch__input" type="checkbox" role="switch" id="sw-on" checked>
              <label class="switch__label" for="sw-on">Show retired vehicles on the map</label>
            </div>
```

### switch · state:focus-visible

```html
<div class="stack stack--gap-3">
            <div class="switch">
              <input class="switch__input is-focus-visible" type="checkbox" role="switch" id="sw-focus">
              <label class="switch__label" for="sw-focus">Auto-assign new work orders</label>
            </div>
            <div class="switch">
              <input class="switch__input is-hover" type="checkbox" role="switch" id="sw-hover" checked>
              <label class="switch__label" for="sw-hover">Auto-assign new work orders</label>
            </div>
            </div>
```

### switch · state:disabled

```html
<div class="stack stack--gap-3">
            <div class="switch">
              <input class="switch__input" type="checkbox" role="switch" id="sw-dis" disabled aria-describedby="sw-dis-hint">
              <label class="switch__label" for="sw-dis">Allow drivers to edit odometer readings</label>
              <p class="switch__hint" id="sw-dis-hint">Only fleet admins can change this.</p>
            </div>
            <div class="switch">
              <input class="switch__input" type="checkbox" role="switch" id="sw-dis-on" checked disabled>
              <label class="switch__label" for="sw-dis-on">Record GPS location with inspections</label>
            </div>
            </div>
```

### switch · variant:with-label

```html
<div class="stack stack--gap-4">
            <div class="switch">
              <input class="switch__input" type="checkbox" role="switch" id="sw-lbl" checked aria-describedby="sw-lbl-hint">
              <label class="switch__label" for="sw-lbl">Text drivers about schedule changes</label>
              <p class="switch__hint" id="sw-lbl-hint">Drivers get an SMS when their vehicle's service date moves.</p>
            </div>
            <div class="switch switch--label-start">
              <input class="switch__input" type="checkbox" role="switch" id="sw-lbl-end" aria-describedby="sw-lbl-end-hint">
              <label class="switch__label" for="sw-lbl-end">Daily defect summary email</label>
              <p class="switch__hint" id="sw-lbl-end-hint">Sent to depot managers at 07:00.</p>
            </div>
            </div>
```

## API

Hook | Values | Purpose
.switch , .switch__input , .switch__label , .switch__hint | block / parts | One switch
role="switch" | attribute (required) | Announced as on/off instead of checked
.switch--label-start | modifier class | Label first, switch at the inline end (settings lists)
checked , disabled | attribute | On; not operable (both values shown)
aria-busy="true" on .switch | attribute | Saving: thumb pulses, pointer input ignored
.is-hover | .is-focus-visible | docs-only class | Freezes a state

## Do and don't

Text drivers about schedule changes Do name the setting and let it apply immediately. On / Off
Changes apply when you press Save.
Don't label a switch "On/Off" or use it where a Save button applies the change — use a checkbox.

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Moves to the switch
Space | Toggles on/off (native checkbox behavior)
- Role: switch on a native checkbox, so screen readers say "Text drivers about schedule changes, switch, on".
- State is shown by thumb position and track fill, not color alone; the track border is 3:1 against the surface.
- Clicking the label toggles it; track 44 × 24px meets the 24px target minimum.
- Async failures: revert the switch and show an error message next to it, announced with role="alert" .

## Tokens

Custom property | Purpose
--color-bg-muted , --input-border , --color-text-muted | Off track, border, thumb
--color-action-primary-bg | -hover , --color-action-primary-fg | On track and thumb
--icon-size-lg , --radius-full | Track size and shape
--color-bg-subtle , --color-text-disabled | Disabled
--motion-duration-fast , --opacity-disabled | Thumb movement, saving pulse
