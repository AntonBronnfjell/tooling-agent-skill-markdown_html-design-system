# Stat

Category: Data Display · page `components/stat.html` · CSS `css/components/stat.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `stat` — Metric / Statistic | core | ready · stable | variant:basic variant:with-trend-up variant:with-trend-down variant:with-sparkline state:loading |

## Usage

Use a stat to show one key number on a dashboard: fleet uptime, overdue services, mean time to repair. Group three to five in a .stat-group . Use a chart when the shape over time matters more than the current value, and a table for many numbers.
- Basic — label, value, unit.
- With trend — a delta pill with an arrow and words. Tone follows meaning: more uptime is good, more overdue services is bad.
- With sparkline — a small trend line; decorative, the delta text says the trend.
- Loading — keep the label; skeletons replace value and delta.
Content: label says what and over which period ("Fleet uptime, last 7 days"). Deltas are full phrases with the comparison: "Up 1.2 points vs last week". Round to what people act on (97.4%, not 97.4183%).

## Anatomy

- Container — .stat
- Label — dt.stat__label
- Value — dd.stat__value with tabular numerals, plus .stat__unit
- Delta (optional) — .stat__delta--good|bad|flat : arrow icon + text
- Note (optional) — .stat__note
- Sparkline (optional) — svg.stat__sparkline , aria-hidden

## Examples

### stat · variant:basic

```html
<div class="stat">
              <dl class="stat__body">
                <dt class="stat__label">Vehicles in service</dt>
                <dd class="stat__value">118<span class="stat__unit">of 126</span></dd>
              </dl>
            </div>
```

### stat · variant:with-trend-up

```html
<div class="stat">
              <dl class="stat__body">
                <dt class="stat__label">Fleet uptime, last 7 days</dt>
                <dd class="stat__value">97.4<span class="stat__unit">%</span></dd>
              </dl>
              <p class="stat__delta stat__delta--good"><svg class="" aria-hidden="true" focusable="false"><use href="#icon-arrow-up"></use></svg>Up 1.2 points vs last week</p>
            </div>
```

### stat · variant:with-trend-down

```html
<div class="stat">
              <dl class="stat__body">
                <dt class="stat__label">Overdue services</dt>
                <dd class="stat__value">7</dd>
              </dl>
              <p class="stat__delta stat__delta--good"><svg class="" aria-hidden="true" focusable="false"><use href="#icon-arrow-down"></use></svg>Down 3 vs last week</p>
              <p class="stat__note">Oldest: Pickup PU-012, 6 days</p>
            </div>
```

### stat · variant:with-sparkline

```html
<div class="stat">
              <dl class="stat__body">
                <dt class="stat__label">Mean time to repair</dt>
                <dd class="stat__value">4.6<span class="stat__unit">h</span></dd>
              </dl>
              <p class="stat__delta stat__delta--bad"><svg class="" aria-hidden="true" focusable="false"><use href="#icon-arrow-up"></use></svg>Up 0.8 h over 30 days</p>
              <svg class="stat__sparkline" viewBox="0 0 120 32" preserveAspectRatio="none" aria-hidden="true" focusable="false">
                <path d="M0 22 L15 20 L30 24 L45 18 L60 19 L75 14 L90 12 L105 9 L120 6" vector-effect="non-scaling-stroke"/>
              </svg>
            </div>
```

### stat · state:loading

```html
<div class="stat" aria-busy="true">
              <p class="stat__label">Parts spend, this month</p>
              <span class="stat__skeleton stat__skeleton--value" aria-hidden="true"></span>
              <span class="stat__skeleton stat__skeleton--delta" aria-hidden="true"></span>
              <span class="sr-only">Loading parts spend</span>
            </div>
```

## API

Hook | Values | Purpose
.stat | block class | Tile
.stat__body | __label | __value | __unit | __note | part classes | Content (use dl/dt/dd for label and value)
.stat__delta--good | --bad | --flat | part modifier | Delta tone by meaning → feedback success/danger/neutral
.stat__sparkline | part class | Decorative trend line ( --dataviz-categorical-1 )
aria-busy="true" | attribute | Loading; use .stat__skeleton ( --value | --delta ) and an .sr-only message
.stat-group | companion block | Auto-fit grid of stats

## Do and don't

"Down 3 vs last week" in green for overdue services
Do color by meaning and say the direction in words.
Red for every downward arrow
Don’t tie color to arrow direction.
"Fleet uptime, last 7 days"
Do state the period in the label.
A sparkline with no text trend
Don’t make the sparkline the only place the trend appears.

## Accessibility

Stats are static; no keyboard behavior.
- Label and value are a dt / dd pair, read as "Fleet uptime, last 7 days: 97.4 %".
- The delta's direction is in words ("Up", "Down"); the arrow is aria-hidden and the tone color is never the only signal.
- Sparklines are aria-hidden ; the delta text carries the trend. Link to the full chart or table for details.
- Loading: aria-busy="true" plus an .sr-only "Loading parts spend". When the value arrives, don't announce it unless the user asked for the refresh.
- Contrast: delta pills use contrast-checked feedback.*.fg / feedback.*.bg pairs.

## Tokens

Custom property | Purpose
--color-elevation-surface-raised , --card-radius | Tile surface and shape
--font-size-3xl , --font-tracking-tight | Value
--color-feedback-success-* | -danger-* | Good / bad delta
--dataviz-categorical-1 | Sparkline stroke
--color-bg-muted , --motion-duration-slower | Skeleton fill and pulse
--icon-size-sm | Delta arrow
