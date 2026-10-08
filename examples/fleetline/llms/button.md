# Button

Category: Actions · page `components/button.html` · CSS `css/components/button.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `button-primary` — Primary Button | core | ready · stable | variant:primary state:default state:hover state:focus-visible state:active state:disabled state:loading size:sm size:md size:lg |
| `button-secondary` — Secondary Button | core | ready · stable | variant:secondary |
| `button-tertiary` — Tertiary / Ghost Button | core | ready · stable | variant:ghost |
| `button-destructive` — Destructive Button | core | ready · stable | variant:destructive |
| `button-with-icon` — Button with leading/trailing icon | core | ready · stable | variant:icon-leading variant:icon-trailing variant:full-width |

## Usage

Use a button to start an action on the current screen: save a work order, assign a mechanic, export a report. Use a link instead when the result is navigation to another page; a link styled as a button ( <a class="btn"> ) is allowed only for that case.
- Primary — the one main action of a region (a form, a dialog, a panel). Teal is reserved for this; never two primaries side by side.
- Secondary — alternatives next to the primary ("Save draft" next to "Close work order").
- Ghost (tertiary) — low-emphasis actions in dense areas: table rows, toolbars, "Cancel".
- Destructive — deletes or retires something. Always confirm in an alert dialog or offer undo.
Labels: verb + object, sentence case, three words or fewer ("Assign mechanic", "Export service log"). Avoid "OK", "Submit", "Click here". Keep paired labels parallel ("Save draft" / "Close work order"). Allow +40% length for translations — buttons wrap their row, never truncate the label.

## Anatomy

- Container — <button type="button|submit" class="btn"> , 8px radius, height from --button-height-*
- Label — .btn__label (required when an icon or spinner is present)
- Leading or trailing icon (optional) — svg.btn__icon , aria-hidden="true"
- Spinner (loading only) — .btn__spinner , overlays the label so the width doesn't change

## Examples

### button-primary · variant:primary state:default

```html
<div class="ds-demo__row"><button type="button" class="btn btn--primary">Assign mechanic</button></div>
```

### button-primary · state:hover

```html
<div class="ds-demo__row"><button type="button" class="btn btn--primary is-hover">Assign mechanic</button></div>
```

### button-primary · state:focus-visible

```html
<div class="ds-demo__row"><button type="button" class="btn btn--primary is-focus-visible">Assign mechanic</button></div>
```

### button-primary · state:active

```html
<div class="ds-demo__row"><button type="button" class="btn btn--primary is-active">Assign mechanic</button></div>
```

### button-primary · state:disabled

```html
<div class="ds-demo__row">
              <button type="button" class="btn btn--primary" disabled>Assign mechanic</button>
              <button type="button" class="btn btn--primary" aria-disabled="true" aria-describedby="assign-why">Close work order</button>
            </div>
            <p id="assign-why">Log at least one task before closing this work order.</p>
```

### button-primary · state:loading

```html
<div class="ds-demo__row">
              <button type="submit" class="btn btn--primary" aria-busy="true" aria-disabled="true">
                <span class="btn__label">Save work order</span>
                <span class="btn__spinner" aria-hidden="true"></span>
              </button>
              <span role="status" class="sr-only">Saving work order WO-4182…</span>
            </div>
```

### button-primary · size:sm

```html
<div class="ds-demo__row"><button type="button" class="btn btn--primary btn--sm">Assign mechanic</button></div>
```

### button-primary · size:md

```html
<div class="ds-demo__row"><button type="button" class="btn btn--primary">Assign mechanic</button></div>
```

### button-primary · size:lg

```html
<div class="ds-demo__row"><button type="button" class="btn btn--primary btn--lg">Assign mechanic</button></div>
```

### button-secondary · variant:secondary

```html
<div class="ds-demo__row">
              <button type="button" class="btn btn--secondary">Save draft</button>
              <button type="button" class="btn btn--secondary is-hover">Save draft</button>
              <button type="button" class="btn btn--secondary is-focus-visible">Save draft</button>
              <button type="button" class="btn btn--secondary is-active">Save draft</button>
              <button type="button" class="btn btn--secondary" disabled>Save draft</button>
            </div>
```

### button-secondary · variant:secondary size:sm size:lg

```html
<div class="ds-demo__row">
              <button type="button" class="btn btn--secondary btn--sm">Save draft</button>
              <button type="button" class="btn btn--secondary">Save draft</button>
              <button type="button" class="btn btn--secondary btn--lg">Save draft</button>
            </div>
```

### button-tertiary · variant:ghost

```html
<div class="ds-demo__row">
              <button type="button" class="btn btn--ghost">View history</button>
              <button type="button" class="btn btn--ghost is-hover">View history</button>
              <button type="button" class="btn btn--ghost is-focus-visible">View history</button>
              <button type="button" class="btn btn--ghost is-active">View history</button>
              <button type="button" class="btn btn--ghost" disabled>View history</button>
            </div>
```

### button-destructive · variant:destructive

```html
<div class="ds-demo__row">
              <button type="button" class="btn btn--destructive">Retire vehicle</button>
              <button type="button" class="btn btn--destructive is-hover">Retire vehicle</button>
              <button type="button" class="btn btn--destructive is-focus-visible">Retire vehicle</button>
              <button type="button" class="btn btn--destructive is-active">Retire vehicle</button>
              <button type="button" class="btn btn--destructive" disabled>Retire vehicle</button>
            </div>
```

### button-destructive · variant:destructive state:with-confirm

```html
<p>Retire van KX-219? It will be removed from dispatch and its open work orders will be cancelled.</p>
            <div class="ds-demo__row">
              <button type="button" class="btn btn--destructive">Retire van</button>
              <button type="button" class="btn btn--ghost">Keep in service</button>
            </div>
```

### button-with-icon · variant:icon-trailing

```html
<div class="ds-demo__row">
              <button type="button" class="btn btn--primary">
                <span class="btn__label">Continue to parts</span>
                <svg class="btn__icon icon--mirror-rtl" aria-hidden="true" focusable="false"><use href="#icon-arrow-right"></use></svg>
              </button>
            </div>
```

### button-with-icon · variant:icon-leading

```html
<div class="ds-demo__row">
              <button type="button" class="btn btn--primary">
                <svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-plus"></use></svg>
                <span class="btn__label">New work order</span>
              </button>
              <button type="button" class="btn btn--secondary">
                <svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-download"></use></svg>
                <span class="btn__label">Export service log</span>
              </button>
              <button type="button" class="btn btn--ghost btn--sm">
                <svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-trash"></use></svg>
                <span class="btn__label">Remove part</span>
              </button>
            </div>
```

### button-with-icon · variant:full-width

```html
<div style="max-inline-size: 22rem;">
              <button type="button" class="btn btn--primary btn--lg btn--full-width">
                <svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-wrench"></use></svg>
                <span class="btn__label">Start inspection</span>
              </button>
            </div>
```

## API

Hook | Values | Purpose
.btn | block class | Base button; without a variant it renders as secondary
.btn--primary | --secondary | --ghost | --destructive | modifier class | Emphasis
.btn--sm | --lg | modifier class | Size (md is default): 32 / 40 / 48px, same heights as .input--sm|lg
.btn--full-width | modifier class | Fills its container (mobile forms, tablet task screens)
.btn__label , .btn__icon , .btn__spinner | part classes | Label, decorative icon, loading spinner
disabled | attribute | Unavailable and removed from the tab order
aria-disabled="true" | attribute | Unavailable but focusable; pair with aria-describedby explaining why. Your click handler must ignore it.
aria-busy="true" | attribute | Loading: spinner replaces the label visually; also set aria-disabled="true" and ignore repeat activations
.is-hover | .is-focus-visible | .is-active | docs-only class | Freezes a state for documentation and visual tests

## Do and don't

Close work order Save draft Do use one primary per region, with parallel verb + object labels. OK Save Don't place two primaries side by side or use labels that don't say what happens. Retire van Keep in service Do name the object in destructive actions and confirm before acting. Delete Don't style destructive actions as primary, or let one click delete without confirmation or undo.

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Moves focus to the button (skipped when disabled ; kept when aria-disabled )
Enter / Space | Activates the button
- Role: native <button> (WAI-ARIA APG Button pattern). Always set type ; without it a button inside a form submits that form by accident.
- Name: the visible label. Icons inside a labelled button are aria-hidden="true" focusable="false" . Icon-only buttons belong to the icon-button component and need aria-label .
- Loading: the label stays in the accessibility tree (hidden with opacity , not visibility ), so the name doesn't change. Announce progress and the result in a role="status" region.
- Focus: 2px teal ring with 2px offset from --focus-ring-* (≥ 3:1 in every theme). It is never removed.
- Target size: smallest button is 32px high and at least 32px wide (WCAG 2.5.8 needs 24px). Use .btn--lg (48px) on tablet screens mechanics use with gloves.
- Contrast: label/background pairs color.action.*.fg on color.action.*.bg are checked at 4.5:1 by ds.py check . Disabled buttons are exempt but still readable.
- Forced colors: every variant keeps a 1px border so buttons stay visible when backgrounds are removed.

## Tokens

Custom property | Purpose
--button-radius | Corner radius (→ --radius-md , 8px)
--button-height-sm | -md | -lg | Heights (→ --size-control-* )
--button-font-weight | Label weight (semibold)
--color-action-{primary|secondary|ghost|danger}-{bg|bg-hover|bg-active|fg} | Variant colors per state
--color-action-secondary-border | Secondary outline
--color-bg-muted , --color-text-disabled | Disabled fill and label
--focus-ring-width | -offset | -color | Focus ring
--density-{comfortable|compact}-control-padding-x | Inline padding per density
--icon-size-sm | -md , --icon-stroke | Icon and spinner size
--motion-duration-fast , --motion-easing-standard | Color transitions
