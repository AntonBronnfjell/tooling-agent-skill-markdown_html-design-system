# Page Header

Category: Navigation · page `components/page-header.html` · CSS `css/components/page-header.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `page-header` — Page Header | core | ready · stable | variant:title-only variant:with-actions variant:with-breadcrumbs variant:with-tabs |

## Usage

Every Fleetline page opens with a page header: where you are (breadcrumbs), what this is (title + status), and what you can do (actions). It sits at the top of <main> , below the top nav.
- The title is the page's only <h1> and matches the last breadcrumb and the document <title> . (Demos below use h2 so this docs page keeps one h1.)
- Meta: status (dot + word), place, owner, last update as relative time with the exact time in datetime .
- One primary action. Two or three visible actions at most; the rest go into "More actions".
- Use tabs underneath only when the object has several sections with their own URLs.

## Anatomy

- Breadcrumbs (optional) — .page-header__breadcrumbs
- Title — h1.page-header__title
- Description (optional) — .page-header__description
- Meta — ul.page-header__meta with .page-header__status[data-tone]
- Actions — .page-header__actions : buttons + overflow menu button
- Section tabs (optional) — nav.tabs.page-header__tabs

## Examples

### page-header · variant:title-only

```html
<header class="page-header"><div class="page-header__main"><div class="page-header__heading"><h2 class="page-header__title">Depots</h2><p class="page-header__description">6 depots · 128 vehicles · 41 mechanics</p></div></div></header>
```

### page-header · variant:with-actions

```html
<header class="page-header"><div class="page-header__main"><div class="page-header__heading"><h2 class="page-header__title">Van KX-219</h2><ul class="page-header__meta"><li class="page-header__meta-item"><span class="page-header__status" data-tone="success">In service</span></li><li class="page-header__meta-item"><svg class="page-header__meta-icon" aria-hidden="true" focusable="false"><use href="#icon-map-pin"></use></svg>North Yard depot</li><li class="page-header__meta-item"><svg class="page-header__meta-icon" aria-hidden="true" focusable="false"><use href="#icon-clock"></use></svg>Updated <time datetime="2026-10-08T09:40">2 hours ago</time></li></ul></div><div class="page-header__actions"><button type="button" class="btn btn--secondary"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-printer"></use></svg><span class="btn__label">Print job sheet</span></button><button type="button" class="btn btn--primary"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-wrench"></use></svg><span class="btn__label">New work order</span></button><button type="button" class="icon-btn icon-btn--outline" id="ph2-more-btn" aria-haspopup="menu" aria-expanded="false" aria-controls="ph2-more" commandfor="ph2-more" command="toggle-popover" style="anchor-name:--ph2-more" aria-label="More actions for Van KX-219"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-more-horizontal"></use></svg></button><div class="menu" id="ph2-more" popover role="menu" aria-labelledby="ph2-more-btn" style="position-anchor:--ph2-more"><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-pencil"></use></svg><span class="menu__label">Edit details</span></button><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-map-pin"></use></svg><span class="menu__label">Move to depot</span></button><hr class="menu__separator" role="separator"><button type="button" class="menu__item menu__item--danger" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-trash"></use></svg><span class="menu__label">Retire vehicle</span></button></div></div></div></header>
            <p>One primary action; secondary actions in a button and the overflow menu.</p>
```

### page-header · variant:with-breadcrumbs

```html
<header class="page-header"><nav class="breadcrumbs page-header__breadcrumbs" aria-label="Breadcrumb (ph3)"><ol class="breadcrumbs__list"><li class="breadcrumbs__item"><a class="breadcrumbs__link" href="#fleet">Fleet</a></li><li class="breadcrumbs__item"><a class="breadcrumbs__link" href="#vans">Vans</a></li><li class="breadcrumbs__item"><span class="breadcrumbs__current" aria-current="page">Van KX-219</span></li></ol></nav><div class="page-header__main"><div class="page-header__heading"><h2 class="page-header__title">Van KX-219</h2><ul class="page-header__meta"><li class="page-header__meta-item"><span class="page-header__status" data-tone="success">In service</span></li><li class="page-header__meta-item"><svg class="page-header__meta-icon" aria-hidden="true" focusable="false"><use href="#icon-map-pin"></use></svg>North Yard depot</li><li class="page-header__meta-item"><svg class="page-header__meta-icon" aria-hidden="true" focusable="false"><use href="#icon-clock"></use></svg>Updated <time datetime="2026-10-08T09:40">2 hours ago</time></li></ul></div></div></header>
```

### page-header · variant:with-tabs

```html
<header class="page-header"><nav class="breadcrumbs page-header__breadcrumbs" aria-label="Breadcrumb (ph4)"><ol class="breadcrumbs__list"><li class="breadcrumbs__item"><a class="breadcrumbs__link" href="#fleet">Fleet</a></li><li class="breadcrumbs__item"><a class="breadcrumbs__link" href="#vans">Vans</a></li><li class="breadcrumbs__item"><span class="breadcrumbs__current" aria-current="page">Van KX-219</span></li></ol></nav><div class="page-header__main"><div class="page-header__heading"><h2 class="page-header__title">Van KX-219</h2><ul class="page-header__meta"><li class="page-header__meta-item"><span class="page-header__status" data-tone="success">In service</span></li><li class="page-header__meta-item"><svg class="page-header__meta-icon" aria-hidden="true" focusable="false"><use href="#icon-map-pin"></use></svg>North Yard depot</li><li class="page-header__meta-item"><svg class="page-header__meta-icon" aria-hidden="true" focusable="false"><use href="#icon-clock"></use></svg>Updated <time datetime="2026-10-08T09:40">2 hours ago</time></li></ul></div><div class="page-header__actions"><button type="button" class="btn btn--secondary"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-printer"></use></svg><span class="btn__label">Print job sheet</span></button><button type="button" class="btn btn--primary"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-wrench"></use></svg><span class="btn__label">New work order</span></button><button type="button" class="icon-btn icon-btn--outline" id="ph4-more-btn" aria-haspopup="menu" aria-expanded="false" aria-controls="ph4-more" commandfor="ph4-more" command="toggle-popover" style="anchor-name:--ph4-more" aria-label="More actions for Van KX-219"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-more-horizontal"></use></svg></button><div class="menu" id="ph4-more" popover role="menu" aria-labelledby="ph4-more-btn" style="position-anchor:--ph4-more"><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-pencil"></use></svg><span class="menu__label">Edit details</span></button><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-map-pin"></use></svg><span class="menu__label">Move to depot</span></button><hr class="menu__separator" role="separator"><button type="button" class="menu__item menu__item--danger" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-trash"></use></svg><span class="menu__label">Retire vehicle</span></button></div></div></div><nav class="tabs tabs--underline page-header__tabs" aria-label="Van KX-219 sections"><ul class="tabs__list"><li><a class="tabs__tab" href="#overview" aria-current="page">Overview</a></li><li><a class="tabs__tab" href="#history">Service history <span class="tabs__count">12</span></a></li><li><a class="tabs__tab" href="#inspections">Inspections</a></li><li><a class="tabs__tab" href="#documents">Documents</a></li></ul></nav></header>
            <p>Each tab is its own URL, so these are links with <code>aria-current</code>, not ARIA tabs.</p>
```

## API

Hook | Values | Purpose
.page-header | block class | <header> inside <main> ; inline-size container
.page-header__breadcrumbs | __main | __heading | __title | __description | __meta | __meta-item | __meta-icon | __actions | __tabs | parts | See anatomy
.page-header__status[data-tone] | part + attribute | success | warning | danger | info dot next to the status word

## Do and don't

Title "Van KX-219" · status "In service" · actions "Print job sheet", "New work order" , "More actions"
Do show one primary action and move the rest into the overflow menu.
Title "Details" · five primary buttons
Don't use a generic title or several primary actions.

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Breadcrumb links → actions → overflow menu → section tabs
↓ / Enter (More actions) | Opens the overflow menu (see Menu button)
- Inside <main> , <header> has no landmark role — the page's banner is the top nav.
- Status is a word plus a colored dot, never the dot alone (principle: status is never color alone).
- <time datetime> carries the absolute time; show it in a tooltip on hover/focus where it matters.
- Section tabs that change the URL are links with aria-current="page" .

## Tokens

Custom property | Purpose
--typography-h1-font-family | -weight | -line-height , --typography-h2-font-size | Title
--color-text-muted | Description and meta
--color-feedback-{success|warning|danger|info}-icon | Status dot
--space-* | Rhythm between rows
--size-measure | Description line length
