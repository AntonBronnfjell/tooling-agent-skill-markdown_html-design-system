# Progress

Category: Feedback · page `components/progress.html` · CSS `css/components/progress.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `progress-bar` — Progress Bar | core | ready · stable | state:determinate state:indeterminate state:complete state:error |

## Usage

Use a progress bar for tasks that take more than a couple of seconds and whose progress you can measure: uploading inspection photos, importing a vehicle CSV, generating a monthly cost report. Use the indeterminate state when the total is unknown.
- For measurements that aren't progress (tank level, disk usage) use a meter . For short waits under ~2s, a spinner ; for loading page content, a skeleton .
- Always pair the bar with a visible label naming the task and text stating progress ("12 of 20 photos"). On completion or failure, change the text too, not just the color.

## Anatomy

- Label — <label class="progress__label" for> naming the task
- Value — .progress__value , percentage in tabular numerals
- Track and fill — native <progress class="progress__bar">
- Hint — .progress__hint , counts or the outcome, with an icon on complete/error

## Examples

### progress-bar · state:determinate

```html
<div class="progress">
              <div class="progress__header"><label class="progress__label" for="pb-photos">Uploading inspection photos</label><span class="progress__value" aria-hidden="true">60%</span></div>
              <progress id="pb-photos" class="progress__bar" max="100" value="60" aria-describedby="pb-photos-hint">60%</progress>
              <p class="progress__hint" id="pb-photos-hint">12 of 20 photos</p>
            </div>
```

### progress-bar · state:indeterminate

```html
<div class="progress">
              <div class="progress__header"><label class="progress__label" for="pb-import">Importing vehicles from CSV</label></div>
              <progress id="pb-import" class="progress__bar" max="100" aria-describedby="pb-import-hint">Importing…</progress>
              <p class="progress__hint" id="pb-import-hint">Checking VINs. This can take a minute.</p>
            </div>
```

### progress-bar · state:complete

```html
<div class="progress" data-state="complete">
              <div class="progress__header"><label class="progress__label" for="pb-report">Monthly cost report</label><span class="progress__value" aria-hidden="true">100%</span></div>
              <progress id="pb-report" class="progress__bar" max="100" value="100" aria-describedby="pb-report-hint">100%</progress>
              <p class="progress__hint" id="pb-report-hint" role="status"><svg aria-hidden="true" focusable="false"><use href="#icon-circle-check"></use></svg>Report ready — September 2026, 42 vehicles</p>
            </div>
```

### progress-bar · state:error

```html
<div class="progress" data-state="error">
              <div class="progress__header"><label class="progress__label" for="pb-fail">Uploading inspection photos</label><span class="progress__value" aria-hidden="true">35%</span></div>
              <progress id="pb-fail" class="progress__bar" max="100" value="35" aria-describedby="pb-fail-hint">35%</progress>
              <p class="progress__hint" id="pb-fail-hint" role="alert"><svg aria-hidden="true" focusable="false"><use href="#icon-circle-x"></use></svg>Upload stopped at 7 of 20 photos. Check your connection and try again.</p>
            </div>
```

### progress-bar · variant:thin

```html
<div class="progress progress--thin">
              <progress class="progress__bar" max="100" value="40" aria-label="Loading work orders">40%</progress>
            </div>
            <p>Thin bar for page-top loading; needs an <code>aria-label</code> because it has no visible label.</p>
```

## API

Hook | Values | Purpose
.progress | block | Wrapper for label, bar and hint
progress.progress__bar value / max | native attributes | Determinate; omit value for indeterminate
data-state="complete | error" | attribute | Outcome tone (success / danger)
.progress--thin | modifier | 4px track for page-top loading
.progress__header | __label | __value | __hint | parts | See anatomy

## Do and don't

"Uploading inspection photos — 12 of 20 photos"
Do name the task and give a count people can trust.
A bar that jumps to 99% and waits there.
Don't fake progress. If you can't measure it, use the indeterminate state.

## Accessibility

- Role: native <progress> exposes progressbar with its value; indeterminate exposes no value. Name it with a <label for> (or aria-label for the thin bar).
- The visible percentage is aria-hidden because the bar already announces it; the hint is linked with aria-describedby .
- Don't announce every percent. Announce the outcome once: role="status" on completion, role="alert" on failure.
- The bar is not focusable and has no keyboard interaction.
- Contrast: fill ( --color-action-primary-bg , success and danger icon colors) is ≥ 3:1 against the surface. Reduced motion stops the indeterminate sweep; the hint text still says what's happening.
- Forced colors: the track gets a border and the fill uses Highlight .

## Tokens

Custom property | Purpose
--color-bg-muted | Track
--color-action-primary-bg | Fill (in progress)
--color-feedback-success-icon | -fg | Complete fill and hint
--color-feedback-danger-icon | -fg | Error fill and hint
--space-2 | -1 , --radius-full | Track height (default / thin) and shape
--motion-duration-base | -slower | Value change, indeterminate sweep
