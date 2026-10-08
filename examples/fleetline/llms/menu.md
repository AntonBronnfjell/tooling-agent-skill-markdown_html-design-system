# Menu

Category: Actions · page `components/menu.html` · CSS `css/components/menu.css` · JS `js/menu.js` (export `init(root)`)

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `menu-button` — Menu Button / Dropdown Menu | core | ready · stable | state:closed state:open variant:with-icons variant:with-shortcuts variant:checkable variant:submenu state:disabled-item |

## Usage

Use a menu button to offer a short list of actions on one thing: a work order, a van, a table view. For choosing a value in a form, use a select or combobox; for navigation, use links (top nav, side nav) — never role="menu" for site navigation.
- Keep menus to 3–9 items; group with separators and group labels. Put destructive items last, in red, and confirm them.
- Item labels are verb-first and sentence case ("Print job sheet"). The trigger names the object or "Actions"; icon-only triggers name the item ("More actions for van KX-219").
- Checkable items ( menuitemcheckbox , menuitemradio ) keep the menu open; plain actions close it.
- One submenu level at most; deeper trees belong in a dialog or page.

## Anatomy

- Trigger — .btn or .icon-btn with aria-haspopup="menu" , aria-expanded , aria-controls , commandfor / command="toggle-popover"
- Surface — div.menu[popover][role=menu] , anchored with CSS anchor positioning
- Item — button.menu__item[role=menuitem|menuitemcheckbox|menuitemradio]
- Leading icon / check — .menu__icon / .menu__check
- Label — .menu__label
- Shortcut or submenu chevron — kbd.menu__shortcut / .menu__chevron
- Group + label, separator — .menu__group[role=group] , .menu__group-label , hr.menu__separator

## Examples

### menu-button · state:closed variant:with-icons

```html
<div class="ds-demo__row"><button type="button" class="btn btn--secondary" id="m-wo-btn" aria-haspopup="menu" aria-expanded="false" aria-controls="m-wo" commandfor="m-wo" command="toggle-popover" style="anchor-name:--m-wo"><span class="btn__label">Actions</span><svg class="menu-trigger__chevron" aria-hidden="true" focusable="false"><use href="#icon-chevron-down"></use></svg></button><div class="menu" id="m-wo" popover role="menu" aria-labelledby="m-wo-btn" style="position-anchor:--m-wo"><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-pencil"></use></svg><span class="menu__label">Edit work order</span></button><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-copy"></use></svg><span class="menu__label">Duplicate</span></button><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-printer"></use></svg><span class="menu__label">Print job sheet</span></button><hr class="menu__separator" role="separator"><button type="button" class="menu__item menu__item--danger" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-trash"></use></svg><span class="menu__label">Delete work order</span></button></div></div>
            <p>Live: click, or focus and press <kbd>↓</kbd>. Esc closes and returns focus.</p>
```

### menu-button · state:open

```html
<div inert><div class="ds-demo__row"><button type="button" class="btn btn--secondary" aria-expanded="true"><span class="btn__label">Actions</span><svg class="menu-trigger__chevron" aria-hidden="true" focusable="false"><use href="#icon-chevron-down"></use></svg></button></div><div class="menu menu--static" role="menu" aria-label="Work order actions"><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-pencil"></use></svg><span class="menu__label">Edit work order</span></button><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-copy"></use></svg><span class="menu__label">Duplicate</span></button><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-printer"></use></svg><span class="menu__label">Print job sheet</span></button><hr class="menu__separator" role="separator"><button type="button" class="menu__item menu__item--danger" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-trash"></use></svg><span class="menu__label">Delete work order</span></button></div></div>
            <p>Frozen preview of the open surface.</p>
```

### menu-button · variant:with-shortcuts

```html
<div class="ds-demo__row"><button type="button" class="btn btn--secondary" id="m-sc-btn" aria-haspopup="menu" aria-expanded="false" aria-controls="m-sc" commandfor="m-sc" command="toggle-popover" style="anchor-name:--m-sc"><span class="btn__label">Work order</span><svg class="menu-trigger__chevron" aria-hidden="true" focusable="false"><use href="#icon-chevron-down"></use></svg></button><div class="menu" id="m-sc" popover role="menu" aria-labelledby="m-sc-btn" style="position-anchor:--m-sc"><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-users"></use></svg><span class="menu__label">Assign mechanic</span><kbd class="menu__shortcut">A</kbd></button><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-copy"></use></svg><span class="menu__label">Duplicate</span><kbd class="menu__shortcut">⌘D</kbd></button><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-printer"></use></svg><span class="menu__label">Print job sheet</span><kbd class="menu__shortcut">⌘P</kbd></button><hr class="menu__separator" role="separator"><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-archive"></use></svg><span class="menu__label">Archive</span><kbd class="menu__shortcut">E</kbd></button></div></div>
            <p>Shortcuts are hints; the real shortcuts work without opening the menu.</p>
```

### menu-button · variant:checkable

```html
<div class="ds-demo__row"><button type="button" class="btn btn--ghost" id="m-cols-btn" aria-haspopup="menu" aria-expanded="false" aria-controls="m-cols" commandfor="m-cols" command="toggle-popover" style="anchor-name:--m-cols"><span class="btn__label">View options</span><svg class="menu-trigger__chevron" aria-hidden="true" focusable="false"><use href="#icon-chevron-down"></use></svg></button><div class="menu" id="m-cols" popover role="menu" aria-labelledby="m-cols-btn" style="position-anchor:--m-cols"><div class="menu__group" role="group" aria-labelledby="m-cols-g1"><div class="menu__group-label" id="m-cols-g1">Show columns</div><button type="button" class="menu__item" role="menuitemcheckbox" aria-checked="true"><svg class="menu__check" aria-hidden="true" focusable="false"><use href="#icon-check"></use></svg><span class="menu__label">Odometer</span></button><button type="button" class="menu__item" role="menuitemcheckbox" aria-checked="true"><svg class="menu__check" aria-hidden="true" focusable="false"><use href="#icon-check"></use></svg><span class="menu__label">Next service</span></button><button type="button" class="menu__item" role="menuitemcheckbox" aria-checked="false"><svg class="menu__check" aria-hidden="true" focusable="false"><use href="#icon-check"></use></svg><span class="menu__label">Assigned mechanic</span></button></div><hr class="menu__separator" role="separator"><div class="menu__group" role="group" aria-labelledby="m-cols-g2"><div class="menu__group-label" id="m-cols-g2">Sort by</div><button type="button" class="menu__item" role="menuitemradio" aria-checked="true"><svg class="menu__check" aria-hidden="true" focusable="false"><use href="#icon-check"></use></svg><span class="menu__label">Due date</span></button><button type="button" class="menu__item" role="menuitemradio" aria-checked="false"><svg class="menu__check" aria-hidden="true" focusable="false"><use href="#icon-check"></use></svg><span class="menu__label">Vehicle</span></button><button type="button" class="menu__item" role="menuitemradio" aria-checked="false"><svg class="menu__check" aria-hidden="true" focusable="false"><use href="#icon-check"></use></svg><span class="menu__label">Depot</span></button></div></div></div><div inert><div class="menu menu--static" role="menu" aria-label="View options"><div class="menu__group" role="group" aria-labelledby="m-colsp-g1"><div class="menu__group-label" id="m-colsp-g1">Show columns</div><button type="button" class="menu__item" role="menuitemcheckbox" aria-checked="true"><svg class="menu__check" aria-hidden="true" focusable="false"><use href="#icon-check"></use></svg><span class="menu__label">Odometer</span></button><button type="button" class="menu__item" role="menuitemcheckbox" aria-checked="true"><svg class="menu__check" aria-hidden="true" focusable="false"><use href="#icon-check"></use></svg><span class="menu__label">Next service</span></button><button type="button" class="menu__item" role="menuitemcheckbox" aria-checked="false"><svg class="menu__check" aria-hidden="true" focusable="false"><use href="#icon-check"></use></svg><span class="menu__label">Assigned mechanic</span></button></div><hr class="menu__separator" role="separator"><div class="menu__group" role="group" aria-labelledby="m-colsp-g2"><div class="menu__group-label" id="m-colsp-g2">Sort by</div><button type="button" class="menu__item" role="menuitemradio" aria-checked="true"><svg class="menu__check" aria-hidden="true" focusable="false"><use href="#icon-check"></use></svg><span class="menu__label">Due date</span></button><button type="button" class="menu__item" role="menuitemradio" aria-checked="false"><svg class="menu__check" aria-hidden="true" focusable="false"><use href="#icon-check"></use></svg><span class="menu__label">Vehicle</span></button><button type="button" class="menu__item" role="menuitemradio" aria-checked="false"><svg class="menu__check" aria-hidden="true" focusable="false"><use href="#icon-check"></use></svg><span class="menu__label">Depot</span></button></div></div></div>
```

### menu-button · variant:submenu

```html
<div class="ds-demo__row"><button type="button" class="btn btn--secondary" id="m-sub-btn" aria-haspopup="menu" aria-expanded="false" aria-controls="m-sub" commandfor="m-sub" command="toggle-popover" style="anchor-name:--m-sub"><span class="btn__label">Van KX-219</span><svg class="menu-trigger__chevron" aria-hidden="true" focusable="false"><use href="#icon-chevron-down"></use></svg></button><div class="menu" id="m-sub" popover role="menu" aria-labelledby="m-sub-btn" style="position-anchor:--m-sub"><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-pencil"></use></svg><span class="menu__label">Edit details</span></button><button type="button" class="menu__item" role="menuitem" id="m-sub-move-btn" aria-haspopup="menu" aria-expanded="false" aria-controls="m-sub-move" commandfor="m-sub-move" command="toggle-popover" style="anchor-name:--m-sub-move"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-map-pin"></use></svg><svg class="menu__chevron" aria-hidden="true" focusable="false"><use href="#icon-chevron-right"></use></svg><span class="menu__label">Move to depot</span></button><div class="menu menu--sub" id="m-sub-move" popover role="menu" aria-labelledby="m-sub-move-btn" style="position-anchor:--m-sub-move"><button type="button" class="menu__item" role="menuitem"><span class="menu__label">North Yard</span></button><button type="button" class="menu__item" role="menuitem"><span class="menu__label">Harbor Road</span></button><button type="button" class="menu__item" role="menuitem"><span class="menu__label">Eastgate</span></button><button type="button" class="menu__item" role="menuitem" aria-disabled="true"><span class="menu__label">Airport depot</span></button></div><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-printer"></use></svg><span class="menu__label">Print job sheet</span></button></div></div>
            <p><kbd>→</kbd> opens the submenu, <kbd>←</kbd> closes it (mirrored in RTL).</p>
```

### menu-button · state:disabled-item

```html
<div class="ds-demo__row"><button type="button" class="btn btn--secondary" id="m-dis-btn" aria-haspopup="menu" aria-expanded="false" aria-controls="m-dis" commandfor="m-dis" command="toggle-popover" style="anchor-name:--m-dis"><span class="btn__label">Work order WO-4182</span><svg class="menu-trigger__chevron" aria-hidden="true" focusable="false"><use href="#icon-chevron-down"></use></svg></button><div class="menu" id="m-dis" popover role="menu" aria-labelledby="m-dis-btn" style="position-anchor:--m-dis"><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-users"></use></svg><span class="menu__label">Reassign to Rosa Méndez</span></button><button type="button" class="menu__item" role="menuitem" aria-disabled="true"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-check"></use></svg><span class="menu__label">Close work order</span></button><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-printer"></use></svg><span class="menu__label">Print job sheet</span></button></div></div><p>Disabled items stay focusable so people can discover them; the reason goes next to the trigger: "Log at least one task before closing".</p>
```

### menu-button · variant:icon-trigger

```html
<div class="ds-demo__row"><button type="button" class="icon-btn" id="m-row-btn" aria-haspopup="menu" aria-expanded="false" aria-controls="m-row" commandfor="m-row" command="toggle-popover" style="anchor-name:--m-row" aria-label="More actions for van KX-219"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-more-vertical"></use></svg></button><div class="menu" id="m-row" popover role="menu" aria-labelledby="m-row-btn" style="position-anchor:--m-row"><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-pencil"></use></svg><span class="menu__label">Edit work order</span></button><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-copy"></use></svg><span class="menu__label">Duplicate</span></button><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-printer"></use></svg><span class="menu__label">Print job sheet</span></button><hr class="menu__separator" role="separator"><button type="button" class="menu__item menu__item--danger" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-trash"></use></svg><span class="menu__label">Delete work order</span></button></div></div>
```

## API

Hook | Values | Purpose
.menu | block class | Popover surface; role="menu"
.menu--sub | modifier | Submenu, opens inline-end
.menu--static | docs-only modifier | In-flow preview of an open menu
.menu__item , .menu__item--danger | part / modifier | Item, destructive item
.menu__icon | __check | __label | __shortcut | __chevron | part | Item content
.menu__group , .menu__group-label , .menu__separator | part | Grouping
.menu-trigger__chevron | part (trigger) | Rotates when aria-expanded="true"
aria-checked | attribute | Checkable item state
aria-disabled="true" | attribute | Unavailable, still focusable
menu-select | event | Fired on the item: detail { item, value, checked }
init(root) | JS (js/menu.js) | Enhances every [aria-haspopup=menu][aria-controls]

## Do and don't

Edit work order Print job sheet Delete work order Do group related actions and put destructive ones last. Dashboard Vehicles Depots Reports Don't use a menu for site navigation — use links in a nav.

## Accessibility

Keyboard interaction
Key | Behavior
Enter / Space / ↓ (trigger) | Opens and focuses the first item
↑ (trigger) | Opens and focuses the last item
↓ / ↑ | Next / previous item (wraps)
Home / End | First / last item
Letter keys | Typeahead to the next item starting with those letters
Enter / Space (item) | Runs the action and closes; toggles checkable items
→ / ← | Open / close a submenu (mirrored in RTL)
Esc | Closes the current level; focus returns to its trigger
Tab | Closes the whole menu and moves on
- Pattern: WAI-ARIA APG Menu Button. The trigger's aria-expanded is kept in sync on every open and close.
- Disabled items use aria-disabled="true" , stay reachable with arrows, and do nothing when activated.
- Checked state: a check icon plus aria-checked — never color alone.
- Placement: CSS anchor positioning with the shared try set ( --flip-block , --flip-inline ); without anchor support it opens centered in the top layer, still usable.
- Fallback: browsers without invoker commands get togglePopover() on click from js/menu.js .

## Tokens

Custom property | Purpose
--color-elevation-surface-overlay , --overlay-radius , --overlay-shadow | Surface
--z-dropdown | Stacking (top layer when open as a popover)
--size-control-md | -sm | Item height (comfortable / compact)
--color-action-ghost-bg-hover | Highlighted item
--color-feedback-danger-fg | -bg | Destructive item
--color-text-disabled | Disabled item
--color-selected-fg | Check mark
--motion-duration-fast , --motion-easing-enter | Open animation (skipped with reduced motion)
