# Search Input

Category: Forms · page `components/search-input.html` · CSS `css/components/search-input.css` · JS `js/search-input.js` (export `init(root)`)

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `search-input` — Search Input | core | ready · stable | state:empty state:filled state:loading variant:with-shortcut |

## Usage

Use a search input to find vehicles, work orders or parts by free text. Use filters (selects, checkboxes) when people narrow a list by known attributes, and a combobox when they must pick exactly one item from a long list.
- Wrap it in <search> so it is a landmark; keep a label (visible, or visually hidden when a page heading already says what is searched).
- Placeholder shows what can be searched ("Plate, VIN or depot"), never the label.
- Show the / shortcut only for the main search on a page.
- Searching takes longer than about a second? Show the spinner and announce "Searching…".

## Anatomy

- Landmark — <search class="search"> with a form
- Field — .input.input--affixed.search__box (from text field)
- Search icon (decorative) — .search__icon
- Input — input[type=search].search__control
- Spinner / shortcut hint — .search__spinner , kbd.search__kbd
- Clear button — button.search__clear[aria-label="Clear search"]
- Status — .search__status[role=status] (visually hidden)

## Examples

### search-input · state:empty

```html
<search class="search">
              <form class="search__form" action="#" method="get">
                <label class="label" for="si-empty">Search vehicles</label>
                <div class="input input--affixed search__box">
                  <svg class="search__icon" aria-hidden="true" focusable="false"><use href="#icon-search"></use></svg>
                  <input class="input__control search__control" id="si-empty" name="q" type="search" placeholder="Plate, VIN or depot" autocomplete="off" spellcheck="false">
                  <span class="search__spinner" aria-hidden="true"></span>
                  <button type="button" class="search__clear" aria-label="Clear search" hidden><svg class="icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button>
                </div>
                <p class="search__status sr-only" role="status"></p>
              </form>
            </search>
```

### search-input · state:filled

```html
<search class="search">
              <form class="search__form" action="#" method="get">
                <label class="label" for="si-filled">Search vehicles</label>
                <div class="input input--affixed search__box">
                  <svg class="search__icon" aria-hidden="true" focusable="false"><use href="#icon-search"></use></svg>
                  <input class="input__control search__control" id="si-filled" name="q" type="search" placeholder="Plate, VIN or depot" autocomplete="off" spellcheck="false" value="North Yard">
                  <span class="search__spinner" aria-hidden="true"></span>
                  <button type="button" class="search__clear" aria-label="Clear search"><svg class="icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button>
                </div>
                <p class="search__status sr-only" role="status"></p>
              </form>
            </search>
```

### search-input · state:loading

```html
<search class="search">
              <form class="search__form" action="#" method="get">
                <label class="label" for="si-loading">Search vehicles</label>
                <div class="input input--affixed search__box" aria-busy="true">
                  <svg class="search__icon" aria-hidden="true" focusable="false"><use href="#icon-search"></use></svg>
                  <input class="input__control search__control" id="si-loading" name="q" type="search" placeholder="Plate, VIN or depot" autocomplete="off" spellcheck="false" value="WF0XXXTTGXKJ">
                  <span class="search__spinner" aria-hidden="true"></span>
                  <button type="button" class="search__clear" aria-label="Clear search"><svg class="icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button>
                </div>
                <p class="search__status sr-only" role="status">Searching…</p>
              </form>
            </search>
```

### search-input · variant:with-shortcut

```html
<search class="search" data-shortcut="/">
              <form class="search__form" action="#" method="get">
                <label class="sr-only" for="si-kbd">Search work orders</label>
                <div class="input input--affixed search__box">
                  <svg class="search__icon" aria-hidden="true" focusable="false"><use href="#icon-search"></use></svg>
                  <input class="input__control search__control" id="si-kbd" name="q" type="search" placeholder="Plate, VIN or depot" autocomplete="off" spellcheck="false" aria-keyshortcuts="/">
                  <span class="search__spinner" aria-hidden="true"></span>
                  <kbd class="search__kbd" aria-hidden="true">/</kbd>
                  <button type="button" class="search__clear" aria-label="Clear search" hidden><svg class="icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button>
                </div>
                <p class="search__status sr-only" role="status"></p>
              </form>
            </search>
            <p class="field__hint">Press <kbd>/</kbd> anywhere on the page to jump here.</p>
```

## API

Hook | Values | Purpose
.search | block class on <search> | Landmark wrapper; data-enhanced once JS runs
data-shortcut="/" | attribute | Global key that focuses the field (ignored while typing elsewhere)
.search__box[aria-busy="true"] | attribute | Loading: spinner replaces the shortcut hint
.search__clear | part | Shown while filled; clears and returns focus
.search__status | part (role=status) | Polite loading/result announcements — the app writes the text
.input--sm | --lg | modifier on the box | Sizes from text field
.is-hover | .is-focus-visible | docs-only class | Freezes the clear button

## Do and don't

Search vehicles
Do keep a label and say in the placeholder what can be searched. Don't drop the landmark and search type, or use a vague placeholder like "Search…".

## Accessibility

Keyboard interaction
Key | Behavior
/ | Focuses the search field (when shortcut enabled and not typing elsewhere)
Enter | Submits the search
Esc | Clears the field (native for type=search )
Tab | Input, then Clear search (when shown)
- Landmark: <search> exposes a search landmark so screen-reader users can jump straight to it.
- The input role is searchbox ; the shortcut is exposed with aria-keyshortcuts="/" , and the visible kbd hint is hidden from assistive tech.
- Clear search is a labelled icon button; after clearing, focus returns to the input.
- Loading and result counts are announced through the polite role=status paragraph, not by moving focus.

## Tokens

Custom property | Purpose
--input-* , --size-control-* | Field border, height (from text field)
--color-text-muted | Icon, clear button
--color-action-ghost-bg-hover | Clear button hover
--color-bg-subtle , --color-border-default , --font-family-mono | Shortcut hint
--color-action-primary-bg , --motion-duration-slower | Spinner
