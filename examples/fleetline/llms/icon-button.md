# Icon Button

Category: Actions · page `components/icon-button.html` · CSS `css/components/icon-button.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `icon-button` — IconButton | core | ready · stable | variant:square variant:circle size:sm size:md size:lg state:default state:hover state:focus-visible state:active state:disabled |

## Usage

Use an icon button for frequent, well-known actions where space is tight: row actions in the work-order table, toolbar actions, the notification bell. If the icon isn't instantly recognizable to a new dispatcher, use a button with a text label instead.
- Name every icon button with aria-label using verb + object, including the item in lists ("Edit work order WO-4182", not "Edit").
- Pair with a tooltip that shows the same text (tooltip component) — sighted mouse users need the name too.
- Square is the default; circle is for overflow ("more") and floating actions.
- Toggle icon buttons (pin, mute) keep their label and switch aria-pressed .

## Anatomy

- Container — <button type="button" class="icon-btn" aria-label="…"> , square of the button height
- Icon — svg.icon-btn__icon , aria-hidden="true"
- Badge (optional) — .icon-btn__badge , decorative; the count lives in the accessible name

## Examples

### icon-button · variant:square state:default

```html
<div class="ds-demo__row"><button type="button" class="icon-btn icon-btn--square" aria-label="Edit work order WO-4182"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-pencil"></use></svg></button><button type="button" class="icon-btn icon-btn--square icon-btn--outline" aria-label="Edit work order WO-4182"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-pencil"></use></svg></button><button type="button" class="icon-btn icon-btn--square icon-btn--primary" aria-label="Duplicate work order WO-4182"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-copy"></use></svg></button></div>
```

### icon-button · variant:circle

```html
<div class="ds-demo__row"><button type="button" class="icon-btn icon-btn--circle" aria-label="More actions for van KX-219"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-more-vertical"></use></svg></button><button type="button" class="icon-btn icon-btn--circle icon-btn--outline" aria-label="More actions for van KX-219"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-more-vertical"></use></svg></button></div>
```

### icon-button · size:sm

```html
<div class="ds-demo__row"><button type="button" class="icon-btn icon-btn--sm icon-btn--outline" aria-label="Remove filter: Depot North Yard"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button></div>
            <p>32px — dense tables and toolbars.</p>
```

### icon-button · size:md

```html
<div class="ds-demo__row"><button type="button" class="icon-btn icon-btn--outline" aria-label="Print inspection sheet"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-printer"></use></svg></button></div>
            <p>40px — default.</p>
```

### icon-button · size:lg

```html
<div class="ds-demo__row"><button type="button" class="icon-btn icon-btn--lg icon-btn--primary" aria-label="Start inspection"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-wrench"></use></svg></button></div>
            <p>48px — tablet screens used with gloves.</p>
```

### icon-button · state:hover

```html
<div class="ds-demo__row"><button type="button" class="icon-btn icon-btn--outline is-hover" aria-label="Edit work order WO-4182"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-pencil"></use></svg></button><button type="button" class="icon-btn is-hover" aria-label="Edit work order WO-4182"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-pencil"></use></svg></button></div>
```

### icon-button · state:focus-visible

```html
<div class="ds-demo__row"><button type="button" class="icon-btn icon-btn--outline is-focus-visible" aria-label="Edit work order WO-4182"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-pencil"></use></svg></button></div>
```

### icon-button · state:active

```html
<div class="ds-demo__row"><button type="button" class="icon-btn icon-btn--outline is-active" aria-label="Edit work order WO-4182"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-pencil"></use></svg></button></div>
```

### icon-button · state:disabled

```html
<div class="ds-demo__row"><button type="button" class="icon-btn icon-btn--outline" aria-label="Delete work order WO-4182" disabled><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-trash"></use></svg></button><button type="button" class="icon-btn icon-btn--outline" aria-label="Archive van KX-219" aria-disabled="true" aria-describedby="ib-why"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-archive"></use></svg></button></div>
            <p><span id="ib-why">Close the 2 open work orders before archiving this van.</span></p>
```

### icon-button · variant:toggle

```html
<div class="ds-demo__row"><button type="button" class="icon-btn icon-btn--outline" aria-label="Pin van KX-219" aria-pressed="false"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-star"></use></svg></button><button type="button" class="icon-btn icon-btn--outline" aria-label="Pin van KX-219" aria-pressed="true"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-star"></use></svg></button></div>
            <p>Toggle icon buttons keep the same label and use <code>aria-pressed</code>.</p>
```

### icon-button · variant:badge

```html
<div class="ds-demo__row"><button type="button" class="icon-btn icon-btn--outline" aria-label="Notifications, 3 unread"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-bell"></use></svg><span class="icon-btn__badge" aria-hidden="true">3</span></button></div>
```

## API

Hook | Values | Purpose
.icon-btn | block class | Ghost icon button (default emphasis), square
.icon-btn--square | --circle | modifier | Shape
.icon-btn--outline | --primary | modifier | Emphasis: secondary outline, primary fill
.icon-btn--sm | --lg | modifier | 32 / 48px (md 40px default), same as .btn--sm|lg
.icon-btn__icon , .icon-btn__badge | part | Icon and decorative count
aria-label | attribute (required) | Accessible name
aria-pressed | attribute | Toggle state (selected colors + border)
disabled / aria-disabled="true" | attribute | Unavailable; aria-disabled stays focusable and explains why
.is-hover | .is-focus-visible | .is-active | docs-only class | Freeze a state

## Do and don't

Do name the action and the object in aria-label . Don't use ambiguous icons or generic names; when in doubt, show a text label.

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Moves focus to the button (skipped when disabled )
Enter / Space | Activates; toggles aria-pressed for toggle buttons
- Role: native <button> . Name: aria-label (the lint in ds.py check flags icon-only buttons without one).
- Badges: put the count in the name ("Notifications, 3 unread"), hide the visual badge with aria-hidden .
- Target size: 32px minimum (WCAG 2.5.8 needs 24px); use --lg on tablet screens.
- Pressed state is shown by fill and border, never color alone; forced colors use Highlight .

## Tokens

Custom property | Purpose
--button-height-sm | -md | -lg | Square size
--button-radius , --radius-full | Square / circle shape
--color-action-{ghost|secondary|primary}-* | Emphasis colors per state
--color-selected-bg | -fg | -border | Pressed state
--color-action-danger-bg | -fg | Badge
--icon-size-sm | -md | -lg , --icon-stroke | Icon
--focus-ring-* | Focus ring
--motion-duration-fast | Color transitions
