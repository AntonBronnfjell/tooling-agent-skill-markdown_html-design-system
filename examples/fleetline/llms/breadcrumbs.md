# Breadcrumbs

Category: Navigation · page `components/breadcrumbs.html` · CSS `css/components/breadcrumbs.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `breadcrumbs` — Breadcrumbs | core | ready · stable | state:default variant:collapsed state:current |

## Usage

Use breadcrumbs on pages three or more levels deep (Fleet › depot › vehicle type › vehicle) so people can see where they are and step back up. Don't use them on top-level pages or for step-by-step flows (use a stepper).
- Each crumb is the title of that page, sentence case, short ("North Yard depot", not "Depot details for North Yard").
- The current page comes last and is not a link.
- Above 4 levels, collapse the middle into "…"; on phones only the parent remains.

## Anatomy

- Landmark — nav.breadcrumbs[aria-label=Breadcrumb]
- Ordered list — ol.breadcrumbs__list
- Ancestor link — a.breadcrumbs__link
- Separator — "/" drawn by CSS, not read aloud
- Current page — span.breadcrumbs__current[aria-current=page]
- Overflow (optional) — button.breadcrumbs__more + ul.breadcrumbs__overflow[popover]

## Examples

### breadcrumbs · state:default state:current

```html
<nav class="breadcrumbs" aria-label="Breadcrumb"><ol class="breadcrumbs__list"><li class="breadcrumbs__item"><a class="breadcrumbs__link" href="#fleet">Fleet</a></li><li class="breadcrumbs__item"><a class="breadcrumbs__link" href="#north-yard">North Yard depot</a></li><li class="breadcrumbs__item"><a class="breadcrumbs__link" href="#vans">Vans</a></li><li class="breadcrumbs__item"><span class="breadcrumbs__current" aria-current="page">Van KX-219</span></li></ol></nav>
            <p>The last item is the current page: plain text with <code>aria-current="page"</code>.</p>
```

### breadcrumbs · variant:collapsed

```html
<nav class="breadcrumbs" aria-label="Breadcrumb (collapsed example)"><ol class="breadcrumbs__list"><li class="breadcrumbs__item"><a class="breadcrumbs__link" href="#fleet">Fleet</a></li><li class="breadcrumbs__item"><button type="button" class="breadcrumbs__more" aria-label="Show 3 more levels" aria-expanded="false" aria-controls="bc-more" commandfor="bc-more" command="toggle-popover" style="anchor-name:--bc-more">…</button><ul class="breadcrumbs__overflow" id="bc-more" popover style="position-anchor:--bc-more"><li><a class="breadcrumbs__link" href="#north-yard">North Yard depot</a></li><li><a class="breadcrumbs__link" href="#vans">Vans</a></li><li><a class="breadcrumbs__link" href="#kx-219">Van KX-219</a></li></ul></li><li class="breadcrumbs__item"><a class="breadcrumbs__link" href="#wo-4182">Work order WO-4182</a></li><li class="breadcrumbs__item"><span class="breadcrumbs__current" aria-current="page">Brake inspection</span></li></ol></nav>
            <p>More than 4 levels: middle levels collapse into a list behind "…".</p>
```

### breadcrumbs · variant:mobile

```html
<div style="max-inline-size: 20rem;"><nav class="breadcrumbs" aria-label="Breadcrumb (mobile example)"><ol class="breadcrumbs__list"><li class="breadcrumbs__item"><a class="breadcrumbs__link" href="#fleet">Fleet</a></li><li class="breadcrumbs__item"><a class="breadcrumbs__link" href="#north-yard">North Yard depot</a></li><li class="breadcrumbs__item"><a class="breadcrumbs__link" href="#vans">Vans</a></li><li class="breadcrumbs__item"><span class="breadcrumbs__current" aria-current="page">Van KX-219</span></li></ol></nav></div>
            <p>Narrow container: only the parent shows, as "← Vans".</p>
```

### breadcrumbs · state:hover state:focus-visible

```html
<nav class="breadcrumbs" aria-label="Breadcrumb (states example)"><ol class="breadcrumbs__list"><li class="breadcrumbs__item"><a class="breadcrumbs__link is-hover" href="#fleet">Fleet</a></li><li class="breadcrumbs__item"><a class="breadcrumbs__link is-focus-visible" href="#north-yard">North Yard depot</a></li></ol></nav>
```

## API

Hook | Values | Purpose
.breadcrumbs | block class | <nav> ; inline-size container
.breadcrumbs__list | __item | __link | __current | parts | Trail
.breadcrumbs__more , .breadcrumbs__overflow | parts | Collapsed levels (popover via invoker)
aria-current="page" | attribute | Current page

## Do and don't

- Fleet
- Vans
- Van KX-219
Do end with the current page as plain text.
Fleet > Vans > Van KX-219 (link to itself)
Don't make the current page a link or type separators into the text.

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Moves through the links (and the "…" button)
Enter | Follows a link; on "…" opens the hidden levels
Esc | Closes the hidden-levels list, focus returns to "…"
- Screen readers announce "Breadcrumb, navigation" and "list, 4 items"; separators use CSS alt text content: "/" / "" , so they aren't read.
- Current page: aria-current="page" plus semibold, no underline.
- "…" has a name that says what it reveals ("Show 3 more levels").

## Tokens

Custom property | Purpose
--color-text-link | Ancestor links
--color-text-default | Current page
--color-text-subtle | Separator
--color-elevation-surface-overlay , --overlay-radius | -shadow | Overflow list
--focus-ring-* | Focus ring
