# Top Nav

Category: Navigation · page `components/top-nav.html` · CSS `css/components/top-nav.css` · JS `js/top-nav.js` (export `init(root)`)

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `top-nav` — Global Navigation Bar | core | ready · stable | state:default variant:mobile-collapsed variant:mobile-open state:current |

## Usage

The top nav is the app header on every Fleetline screen: product logo (home), the 4–6 main areas, search, notifications and the profile menu. Use the side nav for the second level inside an area (e.g. the workshop sections).
- Link labels are short nouns for places: "Dispatch", "Work orders". Don't put actions ("New work order") in the nav — they go in the page header.
- The current area is marked with aria-current="page" plus weight and a bar.
- Notification counts go in the name ("Notifications, 3 unread").
- Sticky variant: set html { scroll-padding-top } to the bar height so focused elements aren't hidden under it.
- The layout reacts to its own width (container query at 48rem), so it also collapses in narrow split views on desktop.

## Anatomy

- Menu toggle — .top-nav__toggle (narrow only)
- Brand — a.top-nav__brand to the home dashboard
- Main nav — nav.top-nav__nav[aria-label=Main] with .top-nav__link items
- Search — form.top-nav__search[role=search]
- Actions — notifications .icon-btn and the profile menu button

## Examples

### top-nav · state:default state:current

```html
<header class="top-nav">
              <div class="top-nav__bar">
                <button type="button" class="btn btn--ghost top-nav__toggle" aria-controls="tn1-panel"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-menu"></use></svg><span class="btn__label">Menu</span></button>
                <a class="top-nav__brand" href="#home"><svg class="top-nav__logo" aria-hidden="true" focusable="false"><use href="#icon-truck"></use></svg>Fleetline</a>
                <div class="top-nav__panel" id="tn1-panel">
                  <nav class="top-nav__nav" aria-label="Main (desktop example)"><ul class="top-nav__list"><li><a class="top-nav__link" href="#dispatch">Dispatch</a></li><li><a class="top-nav__link" href="#vehicles">Vehicles</a></li><li><a class="top-nav__link" href="#work-orders" aria-current="page">Work orders</a></li><li><a class="top-nav__link" href="#depots">Depots</a></li><li><a class="top-nav__link" href="#reports">Reports</a></li></ul></nav>
                  <form class="top-nav__search" role="search" action="#search"><label class="sr-only" for="tn1-q">Search vehicles and work orders</label><svg class="top-nav__search-icon" aria-hidden="true" focusable="false"><use href="#icon-search"></use></svg><input class="top-nav__search-input" id="tn1-q" type="search" name="q" placeholder="Plate, VIN or WO number" autocomplete="off"></form>
                </div>
                <div class="top-nav__actions">
                  <button type="button" class="icon-btn" aria-label="Notifications, 3 unread"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-bell"></use></svg><span class="icon-btn__badge" aria-hidden="true">3</span></button>
                  <button type="button" class="icon-btn icon-btn--circle" id="tn1-profile-btn" aria-haspopup="menu" aria-expanded="false" aria-controls="tn1-profile" commandfor="tn1-profile" command="toggle-popover" style="anchor-name:--tn1-profile" aria-label="Rosa Méndez, account menu"><span class="top-nav__avatar" aria-hidden="true">RM</span></button><div class="menu" id="tn1-profile" popover role="menu" aria-labelledby="tn1-profile-btn" style="position-anchor:--tn1-profile"><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-user"></use></svg><span class="menu__label">Profile</span></button><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-settings"></use></svg><span class="menu__label">Notification settings</span></button><hr class="menu__separator" role="separator"><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-log-out"></use></svg><span class="menu__label">Sign out</span></button></div>
                </div>
              </div>
            </header>
            <p>Current page: "Work orders" — semibold text and a bottom bar, not color alone.</p>
```

### top-nav · variant:mobile-collapsed

```html
<div style="max-inline-size: 24rem; border: var(--border-width-thin) dashed var(--color-border-default);"><header class="top-nav">
              <div class="top-nav__bar">
                <button type="button" class="btn btn--ghost top-nav__toggle" aria-controls="tn2-panel" aria-expanded="false"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-menu"></use></svg><span class="btn__label">Menu</span></button>
                <a class="top-nav__brand" href="#home"><svg class="top-nav__logo" aria-hidden="true" focusable="false"><use href="#icon-truck"></use></svg>Fleetline</a>
                <div class="top-nav__panel" id="tn2-panel">
                  <nav class="top-nav__nav" aria-label="Main (mobile example, collapsed)"><ul class="top-nav__list"><li><a class="top-nav__link" href="#dispatch">Dispatch</a></li><li><a class="top-nav__link" href="#vehicles">Vehicles</a></li><li><a class="top-nav__link" href="#work-orders" aria-current="page">Work orders</a></li><li><a class="top-nav__link" href="#depots">Depots</a></li><li><a class="top-nav__link" href="#reports">Reports</a></li></ul></nav>
                  <form class="top-nav__search" role="search" aria-label="Search, demo 2" action="#search"><label class="sr-only" for="tn2-q">Search vehicles and work orders</label><svg class="top-nav__search-icon" aria-hidden="true" focusable="false"><use href="#icon-search"></use></svg><input class="top-nav__search-input" id="tn2-q" type="search" name="q" placeholder="Plate, VIN or WO number" autocomplete="off"></form>
                </div>
                <div class="top-nav__actions">
                  <button type="button" class="icon-btn" aria-label="Notifications, 3 unread"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-bell"></use></svg><span class="icon-btn__badge" aria-hidden="true">3</span></button>
                  
                </div>
              </div>
            </header></div>
            <p>Narrow container: links and search move behind the Menu button.</p>
```

### top-nav · variant:mobile-open

```html
<div style="max-inline-size: 24rem; border: var(--border-width-thin) dashed var(--color-border-default);"><header class="top-nav">
              <div class="top-nav__bar">
                <button type="button" class="btn btn--ghost top-nav__toggle" aria-controls="tn3-panel" aria-expanded="true"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-menu"></use></svg><span class="btn__label">Menu</span></button>
                <a class="top-nav__brand" href="#home"><svg class="top-nav__logo" aria-hidden="true" focusable="false"><use href="#icon-truck"></use></svg>Fleetline</a>
                <div class="top-nav__panel" id="tn3-panel">
                  <nav class="top-nav__nav" aria-label="Main (mobile example, open)"><ul class="top-nav__list"><li><a class="top-nav__link" href="#dispatch">Dispatch</a></li><li><a class="top-nav__link" href="#vehicles">Vehicles</a></li><li><a class="top-nav__link" href="#work-orders" aria-current="page">Work orders</a></li><li><a class="top-nav__link" href="#depots">Depots</a></li><li><a class="top-nav__link" href="#reports">Reports</a></li></ul></nav>
                  <form class="top-nav__search" role="search" aria-label="Search, demo 3" action="#search"><label class="sr-only" for="tn3-q">Search vehicles and work orders</label><svg class="top-nav__search-icon" aria-hidden="true" focusable="false"><use href="#icon-search"></use></svg><input class="top-nav__search-input" id="tn3-q" type="search" name="q" placeholder="Plate, VIN or WO number" autocomplete="off"></form>
                </div>
                <div class="top-nav__actions">
                  <button type="button" class="icon-btn" aria-label="Notifications, 3 unread"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-bell"></use></svg><span class="icon-btn__badge" aria-hidden="true">3</span></button>
                  
                </div>
              </div>
            </header></div>
            <p>Open: search first, then links with a 44px touch target. Esc closes and returns focus to Menu.</p>
```

## API

Hook | Values | Purpose
.top-nav | block class | App header; inline-size container named top-nav
.top-nav--sticky | modifier | Sticks to the top ( --z-sticky )
.top-nav__bar | __brand | __logo | __panel | __nav | __list | __link | __search | __search-input | __search-icon | __actions | __avatar | parts | See anatomy
.top-nav__toggle[aria-controls] | part | Menu button; js/top-nav.js adds and toggles aria-expanded
aria-current="page" | attribute | Current area

## Do and don't

"Dispatch · Vehicles · Work orders · Depots · Reports"
Do keep 4–6 top-level places with short noun labels.
"Home · Fleet · New WO · Settings · Help · Billing · Reports · More"
Don't mix actions and utilities into the main links or exceed what fits at tablet width.

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Moves through Menu (narrow), brand, links, search, notifications, profile
Enter / Space (Menu) | Opens / closes the panel
Esc | Closes the open panel and returns focus to Menu
- Landmarks: <header> is the banner at page level; the links are in <nav aria-label="Main"> ; search is role="search" with a real (visually hidden) label.
- Without JavaScript the Menu button stays hidden and the panel is open, so navigation always works.
- Mobile links are 44px tall ( --size-touch-target ).
- Forced colors: the current link adds an underline because box-shadow bars disappear.

## Tokens

Custom property | Purpose
--color-bg-surface , --color-border-default | Bar
--color-text-muted | -default | Link rest / hover and current
--color-selected-border | -bg | -fg | Current bar (and mobile current fill)
--input-bg | -border | -radius | Search field
--size-control-md | -lg , --size-touch-target | Heights
--z-sticky | Sticky variant
