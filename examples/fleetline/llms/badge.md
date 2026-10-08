# Badge

Category: Data Display · page `components/badge.html` · CSS `css/components/badge.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `badge` — Badge | core | ready · stable | variant:count variant:dot variant:neutral variant:info variant:success variant:warning variant:danger |

## Usage

Use a badge to label the status of an object (a vehicle "In service", a work order "Overdue") or a count ("7"). Badges are read-only; for filters use tags , for page-level messages use an alert.
- Neutral — states with no urgency: "Parked", "Draft".
- Info — scheduled or pending: "Scheduled", "Awaiting parts".
- Success — healthy: "In service", "Passed inspection".
- Warning — needs attention soon: "Due in 3 days".
- Danger — blocking or late: "Overdue", "Failed inspection".
- Count — a number; cap at "99+". Dot — "something new" when the number doesn't matter.
Content: one or two words, sentence case, with a number when it helps ("Due in 3 days"). Keep the vocabulary fixed across the product so "Overdue" always means the same thing.

## Anatomy

- Container — <span class="badge badge--{tone}">
- Icon (tones) — svg.badge__icon , a different shape per tone, aria-hidden
- Dot (optional) — .badge__dot instead of an icon
- Label — the status word or count
- Anchor (optional) — .badge-anchor pins a count or dot to the corner of a control

## Examples

### badge · variant:count

```html
<div class="ds-demo__row">
              <span class="badge-anchor">
                <button type="button" class="btn btn--secondary" aria-describedby="overdue-count">Overdue services</button>
                <span class="badge badge--count" id="overdue-count">7</span>
              </span>
              <span>Alerts <span class="badge badge--count">99+</span></span>
            </div>
```

### badge · variant:dot

```html
<span class="badge-anchor">
              <button type="button" class="btn btn--ghost" aria-label="Notifications, new updates"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-bell"></use></svg></button>
              <span class="badge badge--dot" aria-hidden="true"></span>
            </span>
```

### badge · variant:neutral

```html
<span class="badge badge--neutral"><span class="badge__dot"></span>Parked</span>
```

### badge · variant:info

```html
<span class="badge badge--info"><svg class="badge__icon" aria-hidden="true" focusable="false"><use href="#icon-info"></use></svg>Scheduled</span>
```

### badge · variant:success

```html
<span class="badge badge--success"><svg class="badge__icon" aria-hidden="true" focusable="false"><use href="#icon-circle-check"></use></svg>In service</span>
```

### badge · variant:warning

```html
<span class="badge badge--warning"><svg class="badge__icon" aria-hidden="true" focusable="false"><use href="#icon-triangle-alert"></use></svg>Due in 3 days</span>
```

### badge · variant:danger

```html
<span class="badge badge--danger"><svg class="badge__icon" aria-hidden="true" focusable="false"><use href="#icon-octagon-alert"></use></svg>Overdue</span>
```

## API

Hook | Values | Purpose
.badge | block class | Pill; neutral by default
.badge--neutral | --info | --success | --warning | --danger | modifier class | Tone → color.feedback.* fg/bg/border
.badge--count | modifier class | Solid inverse pill for numbers
.badge--dot | modifier class | Text-less dot; the parent carries the meaning
.badge__icon | __dot | part classes | Leading shape
.badge-anchor | wrapper class | Positions a count/dot on a button's corner

## Do and don't

Overdue Do combine tone, icon and a word. Don’t use an empty red pill to mean overdue.
"Due in 3 days"
Do give a number when timing matters.
Badges as buttons or filters
Don’t make badges clickable; use a tag or button instead.

## Accessibility

Badges are static text; they are not focusable and have no keyboard behavior.
- Status is never color alone: the label says it and each tone has its own icon shape (circle-check, info, triangle, octagon).
- Count and dot badges on a control: put the meaning in the control's accessible name ("Notifications, new updates") or link the count with aria-describedby ; hide the visual badge with aria-hidden when the name already says it.
- Live counts: announce changes through a role="status" region, not by making the badge live.
- Contrast: every tone uses color.feedback.{tone}.fg on color.feedback.{tone}.bg , checked at 4.5:1 in light, dark and high-contrast; count uses text.inverse on bg.inverse .
- Forced colors: badges keep a CanvasText border; dots render as CanvasText .

## Tokens

Custom property | Purpose
--color-feedback-{info|success|warning|danger}-{bg|fg|border|icon} | Tone colors (contrast-checked fg/bg)
--color-bg-subtle , --color-text-default , --color-border-default | Neutral tone
--color-bg-inverse , --color-text-inverse | Count badge
--radius-full | Pill shape
--font-size-xs , --font-weight-semibold | Label
--icon-size-sm | Tone icon
