# Result Panel

Category: Feedback · page `components/result-panel.html` · CSS `css/components/result-panel.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `result-panel` — Result panel | core | ready · stable | variant:success variant:error variant:warning variant:info variant:no-permission variant:with-details |

## Usage

Use a result panel to show the outcome of a finished process when the outcome is the main content: after closing a work order, after a vehicle import, when a page can't be shown because of permissions. Confirmation, error and create-resource pages are built from it.
- For an outcome next to other content (a form that stays on screen), use an inline alert ; for background confirmations, a toast .
- Title states the outcome in plain words ("Work order WO-1042 closed", "We couldn't import the vehicle list"). Description says what happened and what to do next. Give a reference ID for anything support may need.
- One primary next action plus at most one secondary link.

## Anatomy

- Status icon — .result__icon , decorative, shape per tone
- Title — .result__title ; h1 on a full page, h2 in a region
- Description — .result__description , with a copyable code.result__reference
- Actions — .result__actions : primary button + secondary link
- Details (optional) — details.result__details with error ID, time, logs

## Examples

### result-panel · variant:success

```html
<section class="result result--success" aria-labelledby="r-success">
              <span class="result__icon" aria-hidden="true"><svg focusable="false"><use href="#icon-circle-check"></use></svg></span>
              <h4 class="result__title" id="r-success" tabindex="-1">Work order WO-1042 closed</h4>
              <p class="result__description">Brake inspection on KX-24 is logged and the invoice was sent to Northside Depot. Reference <code class="result__reference">INV-2026-0918</code>.</p>
              <div class="result__actions">
                <button type="button" class="btn btn--primary">Open next work order</button>
                <a class="btn btn--ghost" href="#result-panel">Back to dispatch board</a>
              </div>
            </section>
```

### result-panel · variant:error

```html
<section class="result result--error" aria-labelledby="r-error">
              <span class="result__icon" aria-hidden="true"><svg focusable="false"><use href="#icon-circle-x"></use></svg></span>
              <h4 class="result__title" id="r-error" tabindex="-1">We couldn't import the vehicle list</h4>
              <p class="result__description">The file has no VIN column. Add a column named “VIN” and upload it again. Nothing was changed.</p>
              <div class="result__actions">
                <button type="button" class="btn btn--primary">Upload file again</button>
                <a class="btn btn--ghost" href="#result-panel">Download CSV template</a>
              </div>
            </section>
```

### result-panel · variant:warning

```html
<section class="result result--warning" aria-labelledby="r-warning">
              <span class="result__icon" aria-hidden="true"><svg focusable="false"><use href="#icon-triangle-alert"></use></svg></span>
              <h4 class="result__title" id="r-warning" tabindex="-1">38 of 42 vehicles imported</h4>
              <p class="result__description">4 rows were skipped because their VINs already exist. Review them before dispatching.</p>
              <div class="result__actions">
                <button type="button" class="btn btn--primary">Review skipped rows</button>
                <a class="btn btn--ghost" href="#result-panel">Go to vehicles</a>
              </div>
            </section>
```

### result-panel · variant:info

```html
<section class="result result--info" aria-labelledby="r-info">
              <span class="result__icon" aria-hidden="true"><svg focusable="false"><use href="#icon-info"></use></svg></span>
              <h4 class="result__title" id="r-info" tabindex="-1">Report is being generated</h4>
              <p class="result__description">The September cost report covers 42 vehicles. We'll email it to you in about 5 minutes.</p>
              <div class="result__actions">
                <a class="btn btn--secondary" href="#result-panel">Back to reports</a>
              </div>
            </section>
```

### result-panel · variant:no-permission

```html
<section class="result result--no-permission" aria-labelledby="r-perm">
              <span class="result__icon" aria-hidden="true"><svg focusable="false"><use href="#icon-lock"></use></svg></span>
              <h4 class="result__title" id="r-perm" tabindex="-1">You don't have access to billing</h4>
              <p class="result__description">Only fleet admins can view invoices. Ask Priya Shah (fleet admin) to give you access.</p>
              <div class="result__actions">
                <button type="button" class="btn btn--primary">Request access</button>
                <a class="btn btn--ghost" href="#result-panel">Back to dispatch board</a>
              </div>
            </section>
```

### result-panel · variant:with-details

```html
<section class="result result--error" aria-labelledby="r-details">
              <span class="result__icon" aria-hidden="true"><svg focusable="false"><use href="#icon-circle-x"></use></svg></span>
              <h4 class="result__title" id="r-details" tabindex="-1">We couldn't save work order WO-1042</h4>
              <p class="result__description">Something went wrong on our side. Your changes are kept on this device — try again in a minute. If it keeps happening, contact support with reference <code class="result__reference">ERR-7F3A-21</code>.</p>
              <div class="result__actions">
                <button type="button" class="btn btn--primary">Try again</button>
                <a class="btn btn--ghost" href="#result-panel">Contact support</a>
              </div>
              <details class="result__details">
                <summary>Technical details</summary>
                <dl>
                  <dt>Error ID</dt><dd>ERR-7F3A-21</dd>
                  <dt>Time</dt><dd><time datetime="2026-10-08T14:32:07Z">8 Oct 2026, 14:32 UTC</time></dd>
                  <dt>Request</dt><dd>PATCH /work-orders/WO-1042 → 503</dd>
                </dl>
              </details>
            </section>
```

## API

Hook | Values | Purpose
.result | block | Centered outcome panel, one measure wide
.result--success | --error | --warning | --info | --no-permission | modifier | Icon tone
.result--page | modifier | Full-page spacing; title is the h1 and matches <title>
.result__icon | __title | __description | __reference | __actions | __details | parts | See anatomy
tabindex="-1" on the title | attribute | Lets script move focus to the outcome after an async action

## Do and don't

"We couldn't import the vehicle list. The file has no VIN column. Add a column named “VIN” and upload it again."
Do say what happened, why, and the next step.
"Oops! Something went wrong."
Don't leave people without a cause, a next step or a reference ID.

## Accessibility

- A full-page result uses the title as the page's h1 and the document <title> starts with the same words.
- In a region after an async action: insert the panel and move focus to its title ( tabindex="-1" ), or announce it with role="status" — not both, or it's read twice.
- The icon is decorative; the tone is in the title's words. Color is never the only signal.
- Reference codes use user-select: all so one click selects them for copying.
- <details> is keyboard operable with Enter/Space and announces its expanded state natively.

## Tokens

Custom property | Purpose
--color-feedback-{success|danger|warning|info}-bg | -icon | Icon disc and glyph
--color-bg-muted , --color-text-muted | No-permission tone, description text
--typography-h3-* , --typography-code-* | Title, reference
--size-measure | Max width
--space-8 | -16 | Icon size, block padding
