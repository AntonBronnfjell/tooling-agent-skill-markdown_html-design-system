# Card

Category: Data Display · page `components/card.html` · CSS `css/components/card.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `card` — Card | core | ready · stable | variant:basic variant:media variant:interactive variant:with-actions state:selected state:hover |

## Usage

Use a card to summarize one object — a vehicle, a work order, a depot — in a grid or board, with a way to open it. Use a table when people compare many records field by field, and a list group for long single-column lists.
- Basic — title, meta and a short body; no interaction.
- Media — a photo or illustration of the vehicle on the sunken surface above the content.
- Interactive — the title is the one link; the whole card is its hit area. Never wrap the card in <a> .
- With actions — up to two buttons, one primary. More actions go in a menu.
- Selectable — a real checkbox for bulk actions ("Assign 3 vans").
Content: title is the object's name ("Van KX-219"), meta is one line of facts, body is two lines at most. Write status in words ("Oil change overdue by 6 days"), not only with color.

## Anatomy

- Container — <article class="card"> (or <li> in a list of cards) labelled by its title
- Media (optional) — .card__media , bleeds to the edges, 16:9
- Header — .card__header with .card__title (a heading) and .card__meta
- Body — .card__body
- Actions or footer (optional) — .card__actions / .card__footer , pinned to the bottom
- Primary link (interactive) — .card__link on the title; its ::after covers the card
- Select (selectable) — .card__select , label + native checkbox

## Examples

### card · variant:basic

```html
<article class="card" aria-labelledby="c1-t">
              <header class="card__header">
                <h4 id="c1-t" class="card__title">Van KX-219</h4>
                <p class="card__meta">Ford Transit · 84,212 km</p>
              </header>
              <p class="card__body">Brake pads at 3 mm on the front axle. Next service due in 1,800 km.</p>
            </article>
```

### card · variant:media

```html
<article class="card" aria-labelledby="c2-t">
              <div class="card__media"><svg viewBox="0 0 24 24" class="icon icon--lg" aria-hidden="true" focusable="false"><use href="#icon-truck"></use></svg></div>
              <header class="card__header">
                <h4 id="c2-t" class="card__title">Truck TR-077</h4>
                <p class="card__meta">Volvo FH · depot north</p>
              </header>
              <p class="card__body">In the workshop since 07:40 for a gearbox oil leak.</p>
            </article>
```

### card · variant:interactive

```html
<article class="card card--interactive" aria-labelledby="c3-t">
              <header class="card__header">
                <h4 id="c3-t" class="card__title"><a class="card__link" href="#card">WO-4185 · Gearbox oil leak</a></h4>
                <p class="card__meta">Truck TR-077 · Idris Okafor</p>
              </header>
              <p class="card__body">11 h labour logged, parts ordered.</p>
            </article>
```

### card · state:hover

```html
<article class="card card--interactive is-hover" aria-labelledby="c4-t">
              <header class="card__header">
                <h4 id="c4-t" class="card__title"><a class="card__link" href="#card">WO-4191 · Tyre rotation</a></h4>
                <p class="card__meta">Van KX-224 · Lena Brandt</p>
              </header>
              <p class="card__body">Scheduled for Thursday 10 Oct, 09:00.</p>
            </article>
```

### card · variant:with-actions

```html
<article class="card" aria-labelledby="c5-t">
              <header class="card__header">
                <h4 id="c5-t" class="card__title">Pickup PU-012</h4>
                <p class="card__meta">Oil change overdue by 6 days</p>
              </header>
              <p class="card__body">Last service 14 Mar at 132,100 km.</p>
              <div class="card__actions">
                <button type="button" class="btn btn--primary btn--sm">Book service</button>
                <button type="button" class="btn btn--ghost btn--sm">Snooze 7 days</button>
              </div>
            </article>
```

### card · state:selected

```html
<article class="card card--selectable" aria-labelledby="c6-t">
              <label class="card__select"><input type="checkbox" checked aria-labelledby="c6-t"> Selected</label>
              <header class="card__header">
                <h4 id="c6-t" class="card__title">Van KX-230</h4>
                <p class="card__meta">Renault Master · 22,480 km</p>
              </header>
              <p class="card__body">Ready for dispatch.</p>
            </article>
```

## API

Hook | Values | Purpose
.card | block class | Raised surface, border, 12px radius, padding from --card-padding
.card--interactive | modifier class | Hover elevation; focus ring drawn around the card when the link has focus
.card--selectable | modifier class | Selected styling when the inner checkbox is :checked
.card__media | __header | __title | __meta | __body | __actions | __footer | part classes | Content slots
.card__link | part class | The single primary link; stretched over the card
.card__select | part class | Checkbox row; sits above the stretched link
.is-hover | .is-focus-visible | docs-only class | Freeze hover (on the card) or focus (on the link)

## Do and don't

Title link "WO-4185 · Gearbox oil leak" + separate "Book service" button.
Do use one primary link and keep secondary buttons as separate controls.
<a href><article>…<button>
Don’t wrap the whole card in a link; buttons inside become unreachable and the link name becomes the entire card.
"Oil change overdue by 6 days"
Do state status in words, with numbers.
A red top border and no text.
Don’t rely on a colored edge to mean overdue.

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Moves to the card link, then to each action button or the checkbox
Enter | Follows the card link
Space | Toggles the select checkbox
- Role: <article> named by its title via aria-labelledby . In a grid of cards use <ul role="list"><li> .
- Interactive cards have exactly one link; its name is the title only, so link lists stay short. The stretched ::after enlarges the hit area without changing the name.
- Focus: the link's own ring is transparent and the 2px teal ring is drawn around the whole card ( :has(:focus-visible) ).
- Selected: native checkbox labelled by the card title; selection shows as a checked box plus a teal border.
- Forced colors: card border becomes CanvasText ; selected border becomes a 2px Highlight .

## Tokens

Custom property | Purpose
--card-radius | --card-padding | --card-shadow | Shape, inner spacing, resting shadow
--elevation-raised | Hover shadow of interactive cards
--color-elevation-surface-raised | -sunken | Card surface, media well
--color-border-default | -strong | Resting and hover border
--color-selected-border | Selected border
--typography-h5-* | Title
--z-raised | Actions above the stretched link
--motion-duration-fast | Shadow and border transition
