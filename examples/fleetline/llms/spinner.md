# Spinner

Category: Feedback · page `components/spinner.html` · CSS `css/components/spinner.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `spinner` — Spinner / Loader | core | ready · stable | size:sm size:md size:lg variant:with-label |
| `inline-spinner` — Inline Spinner | core | ready · stable | variant:in-button |

## Usage

Use a spinner for short waits (about 1–5 seconds) where you can't show progress or the shape of the result: checking a VIN, assigning a mechanic, refreshing a vehicle's location. It fades in only after 320ms, so fast responses never flash a loader.
- Loading page content (lists, cards, tables)? Use a skeleton . Measurable tasks? Use a progress bar .
- Say what is loading ("Loading service history…"), not just "Loading". Use the visible label variant when the wait may pass 2 seconds.
- Inside a button, use the button's own loading state ( aria-busy ) or the inline spinner next to a label that says what's happening.

## Anatomy

- Container — .spinner[role="status"]
- Ring — .spinner__ring , aria-hidden
- Label — .sr-only text, or visible .spinner__label
- Inline spinner — .inline-spinner , 1em, current text color

## Examples

### spinner · size:sm

```html
<div class="spinner spinner--sm" role="status"><span class="spinner__ring" aria-hidden="true"></span><span class="sr-only">Refreshing location of KX-24…</span></div>
```

### spinner · size:md

```html
<div class="spinner" role="status"><span class="spinner__ring" aria-hidden="true"></span><span class="sr-only">Loading service history…</span></div>
```

### spinner · size:lg

```html
<div class="spinner spinner--lg" role="status"><span class="spinner__ring" aria-hidden="true"></span><span class="sr-only">Loading depot map…</span></div>
```

### spinner · variant:with-label

```html
<div class="spinner spinner--labelled" role="status"><span class="spinner__ring" aria-hidden="true"></span><span class="spinner__label">Checking VIN 1FTBW3XM6HKA38291…</span></div>
            <div class="spinner spinner--labelled spinner--lg spinner--stacked" role="status"><span class="spinner__ring" aria-hidden="true"></span><span class="spinner__label">Loading service history…</span></div>
```

### inline-spinner · variant:in-button

```html
<div class="ds-demo__row">
              <button type="button" class="btn btn--secondary" aria-disabled="true">
                <span class="inline-spinner" aria-hidden="true"></span>
                <span class="btn__label">Assigning mechanic…</span>
              </button>
              <span class="sr-only" role="status">Assigning Lee Park to WO-1042…</span>
            </div>
            <p>Checking availability <span class="inline-spinner" aria-hidden="true"></span></p>
```

## API

Hook | Values | Purpose
.spinner[role="status"] | block | Container and live region
.spinner--sm | --lg | modifier | 16px / 40px (24px default)
.spinner--labelled (+ .spinner--stacked ) | modifier | Visible label beside (or below) the ring
.spinner__ring | __label | parts | Ring and visible label
.inline-spinner | block | 1em ring in text or controls; always aria-hidden

## Do and don't

Loading service history… Do say what is loading.
Six spinners in a dashboard, one per card.
Don't fill a page with spinners. Use skeletons for content areas.

## Accessibility

- Role status (polite): screen readers announce the label when the spinner is inserted. Insert the spinner into the page when loading starts; don't keep a hidden one.
- When loading ends, replace the spinner with the result or a short status ("Service history loaded") so the end is announced too.
- The region that's loading can carry aria-busy="true" ; controls that are waiting carry aria-disabled="true" so they stay focusable.
- Not focusable, no keyboard interaction. Inline spinners are always aria-hidden ; the text next to them does the talking.
- Reduced motion stops the rotation; the ring and the label still say "loading". Forced colors: the ring uses CanvasText .

## Tokens

Custom property | Purpose
--color-action-primary-bg | Ring color
--icon-size-sm | -lg , --size-control-md | Sizes sm / md / lg
--border-width-thick | Ring stroke
--motion-duration-slow | Reveal delay
--motion-duration-slower | Rotation period (× 1.6)
