# List Group

Category: Data Display · page `components/list-group.html` · CSS `css/components/list-group.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `list-group` — List Group | core | ready · stable | variant:simple variant:with-meta variant:interactive variant:with-actions |

## Usage

Use a list group for a single column of similar items, each with a title and one or two details: upcoming services, mechanics on shift, a vehicle's open work orders. Use a table when people compare several fields across rows, and cards when items need media or more text.
- Simple — titles only.
- With meta — trailing number, date or status badge.
- Interactive — each row opens a detail; the title is the link and the whole row is its hit area.
- With actions — one or two row buttons; no stretched link in the same row.
Content: primary text is the object's name; secondary text is one line of context. Trailing meta is short ("12 Nov", "5.5 h", "6 days overdue").

## Anatomy

- List — <ul class="list-group" role="list">
- Row — li.list-group__item
- Leading (optional) — .list-group__leading : avatar or icon
- Content — .list-group__primary and .list-group__secondary
- Trailing meta (optional) — .list-group__meta
- Actions (optional) — .list-group__actions
- Link (interactive) — a.list-group__link , stretched over the row

## Examples

### list-group · variant:simple

```html
<ul class="list-group" role="list">
              <li class="list-group__item"><div class="list-group__content"><span class="list-group__primary">Depot north</span></div></li>
              <li class="list-group__item"><div class="list-group__content"><span class="list-group__primary">Depot south</span></div></li>
              <li class="list-group__item"><div class="list-group__content"><span class="list-group__primary">Mobile workshop van MW-02</span></div></li>
            </ul>
```

### list-group · variant:with-meta

```html
<ul class="list-group" role="list">
              <li class="list-group__item">
                <span class="list-group__leading"><svg class="icon" aria-hidden="true" focusable="false"><use href="#icon-truck"></use></svg></span>
                <div class="list-group__content"><span class="list-group__primary">Pickup PU-012</span><span class="list-group__secondary">Oil change · last done 14 Mar</span></div>
                <span class="list-group__meta"><span class="badge badge--danger"><svg class="badge__icon" aria-hidden="true" focusable="false"><use href="#icon-octagon-alert"></use></svg>6 days overdue</span></span>
              </li>
              <li class="list-group__item">
                <span class="list-group__leading"><svg class="icon" aria-hidden="true" focusable="false"><use href="#icon-truck"></use></svg></span>
                <div class="list-group__content"><span class="list-group__primary">Van KX-219</span><span class="list-group__secondary">Brake pads · 1,800 km left</span></div>
                <span class="list-group__meta"><span class="badge badge--warning"><svg class="badge__icon" aria-hidden="true" focusable="false"><use href="#icon-triangle-alert"></use></svg>Due soon</span></span>
              </li>
              <li class="list-group__item">
                <span class="list-group__leading"><svg class="icon" aria-hidden="true" focusable="false"><use href="#icon-truck"></use></svg></span>
                <div class="list-group__content"><span class="list-group__primary">Truck TR-077</span><span class="list-group__secondary">Tachograph calibration</span></div>
                <span class="list-group__meta">12 Nov</span>
              </li>
            </ul>
```

### list-group · variant:interactive

```html
<nav aria-label="Mechanics on shift">
              <ul class="list-group list-group--interactive" role="list">
                <li class="list-group__item">
                  <span class="list-group__leading"><span class="avatar avatar--sm avatar--tone-teal" aria-hidden="true"><span class="avatar__initials" aria-hidden="true">MQ</span></span></span>
                  <div class="list-group__content"><a class="list-group__link list-group__primary" href="#list-group" aria-current="page">Marta Quintero</a><span class="list-group__secondary">2 open work orders</span></div>
                  <span class="list-group__meta">5.5 h</span>
                </li>
                <li class="list-group__item is-hover">
                  <span class="list-group__leading"><span class="avatar avatar--sm avatar--tone-blue" aria-hidden="true"><span class="avatar__initials" aria-hidden="true">IO</span></span></span>
                  <div class="list-group__content"><a class="list-group__link list-group__primary" href="#list-group">Idris Okafor</a><span class="list-group__secondary">1 open work order</span></div>
                  <span class="list-group__meta">11.0 h</span>
                </li>
                <li class="list-group__item is-focus-visible">
                  <span class="list-group__leading"><span class="avatar avatar--sm avatar--tone-neutral" aria-hidden="true"><span class="avatar__initials" aria-hidden="true">LB</span></span></span>
                  <div class="list-group__content"><a class="list-group__link list-group__primary" href="#list-group">Lena Brandt</a><span class="list-group__secondary">No open work orders</span></div>
                  <span class="list-group__meta">0.0 h</span>
                </li>
              </ul>
            </nav>
```

### list-group · variant:with-actions

```html
<ul class="list-group" role="list">
              <li class="list-group__item">
                <div class="list-group__content"><span class="list-group__primary" id="lg-wo1">WO-4182 · Brake pads, front</span><span class="list-group__secondary">Van KX-219 · Marta Quintero</span></div>
                <div class="list-group__actions">
                  <button type="button" class="btn btn--ghost btn--sm" aria-describedby="lg-wo1"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-pencil"></use></svg><span class="btn__label">Edit</span></button>
                  <button type="button" class="btn btn--secondary btn--sm" aria-describedby="lg-wo1">Close</button>
                </div>
              </li>
              <li class="list-group__item">
                <div class="list-group__content"><span class="list-group__primary" id="lg-wo2">WO-4193 · Wiper blades</span><span class="list-group__secondary">Pickup PU-012 · Marta Quintero</span></div>
                <div class="list-group__actions">
                  <button type="button" class="btn btn--ghost btn--sm" aria-describedby="lg-wo2"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-pencil"></use></svg><span class="btn__label">Edit</span></button>
                  <button type="button" class="btn btn--secondary btn--sm" aria-describedby="lg-wo2">Close</button>
                </div>
              </li>
            </ul>
```

## API

Hook | Values | Purpose
.list-group | block class | Bordered list
.list-group--interactive | modifier class | Hover fill on rows with a .list-group__link
.list-group__item | __leading | __content | __primary | __secondary | __meta | __actions | part classes | Row slots
.list-group__link | part class | Row link; focus ring is drawn on the row
aria-current="page" | attribute on the link | Current row: teal fill and start bar
.is-hover | .is-focus-visible | docs-only class (on the row) | Freeze states

## Do and don't

Row link "Marta Quintero" + trailing "5.5 h"
Do make the title the link and keep meta as text.
Stretched row link plus Edit and Close buttons in the same row
Don’t mix a whole-row link with several row buttons; pick one.
"6 days overdue" badge
Do say status in words in the meta slot.
<div> rows without a list
Don’t drop list semantics; screen readers announce item counts from ul .

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Moves to each row link, or to each row's action buttons
Enter | Follows the row link / activates the focused button
- Role: list with role="list" kept explicitly (Safari drops list semantics when list-style: none ).
- Interactive rows: the link name is the title only; the whole row is clickable through the stretched ::after . Focus ring is drawn inset around the row.
- Row buttons repeat a short label ("Edit") and are described by the row title via aria-describedby , so they read "Edit, WO-4182 · Brake pads, front".
- Current row: aria-current="page" on the link, shown with a fill and a start-edge bar (not color alone).
- Rows are at least 44px high.

## Tokens

Custom property | Purpose
--color-elevation-surface-raised | List surface
--color-border-default | Border and row dividers
--color-action-ghost-bg-hover | Row hover
--color-selected-bg | -fg | -border | Current row
--color-text-muted | Secondary text, meta, leading icon
--size-touch-target | Minimum row height
--density-compact-cell-padding-y | Compact row padding
--focus-ring-* | Row focus ring
