# Tag

Category: Data Display · page `components/tag.html` · CSS `css/components/tag.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `tag` — Tag / Chip | core | ready · stable | variant:static variant:removable variant:selectable state:selected state:focus-visible |

## Usage

Use a static tag for metadata people scan (vehicle features, depot). Use a removable tag to show applied filters that can be cleared one by one. Use a selectable chip for quick on/off filters above a list. Use a badge for status, and checkboxes in a form when the choice is part of data entry.
- Keep labels to one to three words ("Refrigerated", "Depot north"). Long labels truncate at 16rem; put the full text in title and make sure it also appears elsewhere (a detail view), because title isn't keyboard accessible.
- Remove buttons say what they remove: "Remove filter: Overdue".
- Filter chips in a group get a group label: "Filter by status".

## Anatomy

- Container — span.tag (static/removable) or button.tag.tag--selectable
- Leading icon (optional) — .tag__icon ; check mark .tag__check appears when selected
- Label — .tag__label , truncates
- Remove button (removable) — button.tag__remove , 24×24 minimum

## Examples

### tag · variant:static

```html
<ul class="tag-list" role="list" aria-label="Vehicle tags">
              <li><span class="tag">Refrigerated</span></li>
              <li><span class="tag"><svg class="tag__icon" aria-hidden="true" focusable="false"><use href="#icon-map-pin"></use></svg><span class="tag__label">Depot north</span></span></li>
              <li><span class="tag"><span class="tag__label" title="Hazardous goods certified (ADR class 3)">Hazardous goods certified (ADR class 3)</span></span></li>
            </ul>
```

### tag · variant:removable

```html
<ul class="tag-list" role="list" aria-label="Active filters">
              <li><span class="tag tag--removable"><span class="tag__label">Overdue</span><button type="button" class="tag__remove" aria-label="Remove filter: Overdue"><svg class="" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button></span></li>
              <li><span class="tag tag--removable"><span class="tag__label">Vans</span><button type="button" class="tag__remove is-hover" aria-label="Remove filter: Vans"><svg class="" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button></span></li>
            </ul>
```

### tag · variant:selectable

```html
<div class="tag-list" role="group" aria-label="Filter by vehicle type">
              <button type="button" class="tag tag--selectable" aria-pressed="false"><svg class="tag__check" aria-hidden="true" focusable="false"><use href="#icon-check"></use></svg><span class="tag__label">Vans</span></button>
              <button type="button" class="tag tag--selectable" aria-pressed="false"><svg class="tag__check" aria-hidden="true" focusable="false"><use href="#icon-check"></use></svg><span class="tag__label">Trucks</span></button>
              <button type="button" class="tag tag--selectable is-hover" aria-pressed="false"><svg class="tag__check" aria-hidden="true" focusable="false"><use href="#icon-check"></use></svg><span class="tag__label">Pickups</span></button>
              <button type="button" class="tag tag--selectable" aria-pressed="false" disabled><svg class="tag__check" aria-hidden="true" focusable="false"><use href="#icon-check"></use></svg><span class="tag__label">Trailers</span></button>
            </div>
```

### tag · state:selected

```html
<div class="tag-list" role="group" aria-label="Filter by status">
              <button type="button" class="tag tag--selectable" aria-pressed="true"><svg class="tag__check" aria-hidden="true" focusable="false"><use href="#icon-check"></use></svg><span class="tag__label">Overdue</span></button>
              <button type="button" class="tag tag--selectable" aria-pressed="true"><svg class="tag__check" aria-hidden="true" focusable="false"><use href="#icon-check"></use></svg><span class="tag__label">In workshop</span></button>
              <button type="button" class="tag tag--selectable" aria-pressed="false"><svg class="tag__check" aria-hidden="true" focusable="false"><use href="#icon-check"></use></svg><span class="tag__label">In service</span></button>
            </div>
```

### tag · state:focus-visible

```html
<div class="tag-list">
              <button type="button" class="tag tag--selectable is-focus-visible" aria-pressed="false"><svg class="tag__check" aria-hidden="true" focusable="false"><use href="#icon-check"></use></svg><span class="tag__label">Due this week</span></button>
              <span class="tag tag--removable"><span class="tag__label">Depot south</span><button type="button" class="tag__remove is-focus-visible" aria-label="Remove filter: Depot south"><svg class="" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button></span>
            </div>
```

## API

Hook | Values | Purpose
.tag | block class | Static tag
.tag--removable + .tag__remove | modifier + part | Tag with a remove button
.tag--selectable on <button aria-pressed> | modifier + attribute | Filter chip; aria-pressed="true" = selected
.tag__label | __icon | __check | part classes | Content
.tag-list | wrapper class | Wrapping row with gaps (use ul role="list" or role="group" )
disabled | attribute | Unavailable chip
.is-hover | .is-focus-visible | docs-only class | Freeze states

## Do and don't

Overdue Do show selection with a check mark and fill.
Selected only by a slightly darker fill.
Don’t rely on color to show which filters are on.
aria-label="Remove filter: Overdue"
Do name the remove button after the tag.
aria-label="Remove" on every tag
Don’t use the same name for every remove button.

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Moves to each chip or remove button
Enter / Space | Toggles a chip; activates a remove button
- Selectable chips are toggle buttons ( aria-pressed ), announced as "Overdue, toggle button, pressed".
- After removing a tag, move focus to the next tag's remove button, or to the filter field when none remain, and announce "Filter Overdue removed" in a role="status" region.
- Hit area: chips are 32px high; remove buttons are 24×24px (WCAG 2.5.8).
- Contrast: selected uses selected.fg / selected.bg (checked pair).
- Forced colors: borders become CanvasText ; selected border becomes 2px Highlight .

## Tokens

Custom property | Purpose
--size-control-sm | Tag height
--radius-md | Shape (8px, same as controls)
--color-bg-subtle , --color-border-default , --color-text-default | Resting tag
--color-selected-bg | -fg | -border | Selected chip
--color-action-secondary-bg-hover , --color-action-ghost-bg-hover | Hover fills
--color-bg-muted , --color-text-disabled | Disabled chip
--focus-ring-* | Focus ring
