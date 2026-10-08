# App Shell

Category: Patterns · page `patterns/app-shell.html` · CSS `css/patterns/app-shell.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `app-shell` — Application Shell | core | ready · beta | variant:sidebar variant:top-nav-only variant:mobile |

## Usage

The shell is the frame every signed-in Fleetline screen sits in. It only places components; it adds no colors, borders or type of its own.
- Sidebar — dispatch and workshop areas with a second level of navigation (work order queues, inspections, parts). Desktop dispatchers.
- Top-nav only — areas without sub-sections (Reports, a mechanic's job list). Main is capped at the extra-large container so lines stay readable on wide monitors.
- Mobile — tablets in portrait and phones in the yard. The top nav collapses behind Menu ; the side nav is not shown, so every side-nav destination must also be reachable from the area's landing page.
- Prefer document scroll. Only the top nav is sticky; the side nav and main scroll with the page, which keeps browser zoom and find-in-page working.
- One <main id="main"> per document, and the skip link is the first focusable element. The demos below use <div class="app-shell__main"> because this docs page already has its own <main> .

## Anatomy

- Skip link — a.skip-link[href="#main"] , first in the body
- Header — header.top-nav.top-nav--sticky.app-shell__header (banner landmark)
- Side navigation — nav.side-nav.app-shell__nav with its own aria-label (sidebar variant, ≥ 64rem)
- Main — main#main.app-shell__main[tabindex=-1] : page header, then content
- Aside (optional) — aside.app-shell__aside for related, non-essential content
- Footer (optional) — footer.app-shell__footer : version, status link

## Examples

### app-shell · variant:sidebar

```html
<p class="ds-demo__label">variant:sidebar — dispatch dashboard</p>
            <div style="--app-shell-min-block-size: 100%; block-size: 44rem; overflow: auto; border: var(--border-width-thin) solid var(--color-border-default); border-radius: var(--radius-md); background: var(--color-bg-canvas);">
              <div class="app-shell">
                <header class="top-nav top-nav--sticky app-shell__header">
                  <div class="top-nav__bar">
                    <button type="button" class="btn btn--ghost top-nav__toggle" aria-controls="as1-panel"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-menu"></use></svg><span class="btn__label">Menu</span></button>
                    <a class="top-nav__brand" href="#dispatch"><svg class="top-nav__logo" aria-hidden="true" focusable="false"><use href="#icon-truck"></use></svg>Fleetline</a>
                    <div class="top-nav__panel" id="as1-panel">
                      <nav class="top-nav__nav" aria-label="Main (sidebar shell example)"><ul class="top-nav__list"><li><a class="top-nav__link" href="#dispatch" aria-current="page">Dispatch</a></li><li><a class="top-nav__link" href="#vehicles">Vehicles</a></li><li><a class="top-nav__link" href="#work-orders">Work orders</a></li><li><a class="top-nav__link" href="#depots">Depots</a></li><li><a class="top-nav__link" href="#reports">Reports</a></li></ul></nav>
                      <form class="top-nav__search" role="search" action="#search"><label class="sr-only" for="as1-q">Search vehicles and work orders</label><svg class="top-nav__search-icon" aria-hidden="true" focusable="false"><use href="#icon-search"></use></svg><input class="top-nav__search-input" id="as1-q" type="search" name="q" placeholder="Plate, VIN or WO number" autocomplete="off"></form>
                    </div>
                    <div class="top-nav__actions">
                      <button type="button" class="icon-btn" aria-label="Notifications, 3 unread"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-bell"></use></svg><span class="icon-btn__badge" aria-hidden="true">3</span></button>
                      <button type="button" class="icon-btn icon-btn--circle" id="as1-profile-btn" aria-haspopup="menu" aria-expanded="false" aria-controls="as1-profile" commandfor="as1-profile" command="toggle-popover" style="anchor-name:--as1-profile" aria-label="Rosa Méndez, account menu"><span class="top-nav__avatar" aria-hidden="true">RM</span></button><div class="menu" id="as1-profile" popover role="menu" aria-labelledby="as1-profile-btn" style="position-anchor:--as1-profile"><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-user"></use></svg><span class="menu__label">Profile</span></button><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-settings"></use></svg><span class="menu__label">Notification settings</span></button><hr class="menu__separator" role="separator"><button type="button" class="menu__item" role="menuitem"><svg class="menu__icon" aria-hidden="true" focusable="false"><use href="#icon-log-out"></use></svg><span class="menu__label">Sign out</span></button></div>
                    </div>
                  </div>
                </header>

                <div class="app-shell__body">
                  <nav class="side-nav app-shell__nav" aria-label="Dispatch (sidebar shell example)">
                    <div class="side-nav__header"><button type="button" class="icon-btn icon-btn--sm side-nav__collapse" aria-expanded="true" aria-label="Collapse navigation"><svg class="icon-btn__icon side-nav__collapse-icon" aria-hidden="true" focusable="false"><use href="#icon-panel-left-close"></use></svg></button></div>
                    <div class="side-nav__section">
                      <h4 class="side-nav__heading" id="as1-sn-h1">Dispatch</h4>
                      <ul class="side-nav__list" aria-labelledby="as1-sn-h1">
                        <li><a class="side-nav__link" href="#board" aria-current="page"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-layout-dashboard"></use></svg><span class="side-nav__label">Dispatch board</span></a></li>
                        <li><a class="side-nav__link" href="#wo-open"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-clipboard-list"></use></svg><span class="side-nav__label">Open work orders</span><span class="side-nav__count">23</span></a></li>
                        <li><a class="side-nav__link" href="#inspections"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-wrench"></use></svg><span class="side-nav__label">Inspections</span><span class="side-nav__count">4</span></a></li>
                        <li><a class="side-nav__link" href="#calendar"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-calendar"></use></svg><span class="side-nav__label">Service calendar</span></a></li>
                      </ul>
                    </div>
                    <div class="side-nav__section">
                      <h4 class="side-nav__heading" id="as1-sn-h2">Fleet</h4>
                      <ul class="side-nav__list" aria-labelledby="as1-sn-h2">
                        <li><a class="side-nav__link" href="#vehicles"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-truck"></use></svg><span class="side-nav__label">Vehicles</span><span class="side-nav__count">128</span></a></li>
                        <li><a class="side-nav__link" href="#parts"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-package"></use></svg><span class="side-nav__label">Parts inventory</span></a></li>
                        <li><a class="side-nav__link" href="#mechanics"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-users"></use></svg><span class="side-nav__label">Mechanics</span></a></li>
                      </ul>
                    </div>
                  </nav>

                  <div class="app-shell__main" id="as1-main" tabindex="-1">
                    <header class="page-header"><div class="page-header__main"><div class="page-header__heading"><h4 class="page-header__title">Dispatch board</h4><p class="page-header__description">North Yard depot · Wednesday 8 October</p></div><div class="page-header__actions"><button type="button" class="btn btn--secondary"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-download"></use></svg><span class="btn__label">Export day sheet</span></button><button type="button" class="btn btn--primary"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-plus"></use></svg><span class="btn__label">New work order</span></button></div></div></header>

                    <div class="stat-group">
                      <div class="stat">
                        <dl class="stat__body"><dt class="stat__label">Vehicles on road</dt><dd class="stat__value">94<span class="stat__unit">of 128</span></dd></dl>
                        <p class="stat__delta stat__delta--good"><svg aria-hidden="true" focusable="false"><use href="#icon-arrow-up"></use></svg>Up 6 vs yesterday</p>
                      </div>
                      <div class="stat">
                        <dl class="stat__body"><dt class="stat__label">Overdue services</dt><dd class="stat__value">7</dd></dl>
                        <p class="stat__delta stat__delta--bad"><svg aria-hidden="true" focusable="false"><use href="#icon-arrow-up"></use></svg>Up 2 since Monday</p>
                        <p class="stat__note">Oldest: Truck TR-077, 9 days</p>
                      </div>
                      <div class="stat">
                        <dl class="stat__body"><dt class="stat__label">Open work orders</dt><dd class="stat__value">23</dd></dl>
                        <p class="stat__delta stat__delta--flat"><svg aria-hidden="true" focusable="false"><use href="#icon-arrow-right"></use></svg>Same as last week</p>
                      </div>
                    </div>

                    <section class="card" aria-labelledby="as1-wo-t">
                      <header class="card__header"><h5 class="card__title" id="as1-wo-t">Today's work orders</h5><p class="card__meta">Sorted by due time</p></header>
                      <div class="table-wrap" role="region" aria-label="Today's work orders, scrollable table" tabindex="0">
                        <table class="table">
                          <thead><tr><th scope="col">Work order</th><th scope="col">Vehicle</th><th scope="col">Mechanic</th><th scope="col">Status</th><th scope="col" class="table__num">Due</th></tr></thead>
                          <tbody>
                            <tr><th scope="row">WO-4185</th><td>Truck TR-077<span class="table__secondary">Volvo FH, 312,940 km</span></td><td>Idris Okafor</td><td><span class="badge badge--danger"><svg class="badge__icon" aria-hidden="true" focusable="false"><use href="#icon-octagon-alert"></use></svg>Overdue</span></td><td class="table__num"><time datetime="2026-10-08T08:00">08:00</time></td></tr>
                            <tr><th scope="row">WO-4182</th><td>Van KX-219<span class="table__secondary">Ford Transit, 84,212 km</span></td><td>Marta Quintero</td><td><span class="badge badge--info"><svg class="badge__icon" aria-hidden="true" focusable="false"><use href="#icon-clock"></use></svg>In progress</span></td><td class="table__num"><time datetime="2026-10-08T11:30">11:30</time></td></tr>
                            <tr><th scope="row">WO-4191</th><td>Van KX-224<span class="table__secondary">Mercedes Sprinter, 51,006 km</span></td><td>Lena Brandt</td><td><span class="badge badge--warning"><svg class="badge__icon" aria-hidden="true" focusable="false"><use href="#icon-triangle-alert"></use></svg>Waiting for parts</span></td><td class="table__num"><time datetime="2026-10-08T14:00">14:00</time></td></tr>
                            <tr><th scope="row">WO-4193</th><td>Pickup PU-012<span class="table__secondary">Toyota Hilux, 140,377 km</span></td><td>Marta Quintero</td><td><span class="badge badge--success"><svg class="badge__icon" aria-hidden="true" focusable="false"><use href="#icon-circle-check"></use></svg>Done</span></td><td class="table__num"><time datetime="2026-10-08T16:00">16:00</time></td></tr>
                          </tbody>
                        </table>
                      </div>
                    </section>
                  </div>
                </div>

                <footer class="app-shell__footer text-small text-muted">
                  <span>Fleetline 4.12</span>
                  <a class="link" href="#status">Service status: all systems running</a>
                </footer>
              </div>
            </div>
            <p>Desktop: header + side nav + main. Narrow the window below 64rem and the side nav steps aside for the top-nav Menu.</p>
```

### app-shell · variant:top-nav-only

```html
<p class="ds-demo__label">variant:top-nav-only — mechanic's job list with aside</p>
            <div style="--app-shell-min-block-size: 100%; block-size: 34rem; overflow: auto; border: var(--border-width-thin) solid var(--color-border-default); border-radius: var(--radius-md); background: var(--color-bg-canvas);">
              <div class="app-shell app-shell--top-nav-only">
                <header class="top-nav app-shell__header">
                  <div class="top-nav__bar">
                    <button type="button" class="btn btn--ghost top-nav__toggle" aria-controls="as2-panel"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-menu"></use></svg><span class="btn__label">Menu</span></button>
                    <a class="top-nav__brand" href="#jobs"><svg class="top-nav__logo" aria-hidden="true" focusable="false"><use href="#icon-truck"></use></svg>Fleetline</a>
                    <div class="top-nav__panel" id="as2-panel">
                      <nav class="top-nav__nav" aria-label="Main (top-nav-only shell example)"><ul class="top-nav__list"><li><a class="top-nav__link" href="#jobs" aria-current="page">My jobs</a></li><li><a class="top-nav__link" href="#vehicles">Vehicles</a></li><li><a class="top-nav__link" href="#parts">Parts</a></li></ul></nav>
                    </div>
                    <div class="top-nav__actions">
                      <button type="button" class="icon-btn" aria-label="Notifications, none unread"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-bell"></use></svg></button>
                    </div>
                  </div>
                </header>
                <div class="app-shell__body">
                  <div class="app-shell__main" id="as2-main" tabindex="-1">
                    <header class="page-header"><div class="page-header__main"><div class="page-header__heading"><h4 class="page-header__title">My jobs today</h4><p class="page-header__description">Lena Brandt · Bay 3 · 4 jobs, about 6.5 hours</p></div><div class="page-header__actions"><button type="button" class="btn btn--primary"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-wrench"></use></svg><span class="btn__label">Start next job</span></button></div></div></header>
                    <div class="table-wrap" role="region" aria-labelledby="as2-jobs-cap" tabindex="0">
                      <table class="table">
                        <caption id="as2-jobs-cap" class="sr-only">Jobs assigned to Lena Brandt today</caption>
                        <thead><tr><th scope="col">Job</th><th scope="col">Vehicle</th><th scope="col">Status</th><th scope="col" class="table__num">Labour (h)</th></tr></thead>
                        <tbody>
                          <tr><th scope="row">Brake pads, front axle</th><td>Van KX-224</td><td><span class="badge badge--warning"><svg class="badge__icon" aria-hidden="true" focusable="false"><use href="#icon-triangle-alert"></use></svg>Waiting for parts</span></td><td class="table__num">1.25</td></tr>
                          <tr><th scope="row">60,000 km service</th><td>Van KX-231</td><td><span class="badge badge--neutral">Not started</span></td><td class="table__num">3.0</td></tr>
                          <tr><th scope="row">Tachograph check</th><td>Truck TR-081</td><td><span class="badge badge--neutral">Not started</span></td><td class="table__num">0.75</td></tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                  <aside class="app-shell__aside" aria-labelledby="as2-aside-t">
                    <section class="card" aria-labelledby="as2-aside-t">
                      <header class="card__header"><h5 class="card__title" id="as2-aside-t">Parts arriving today</h5><p class="card__meta">From Harbour Road stores</p></header>
                      <p class="card__body">Front brake pads for Van KX-224, expected <time datetime="2026-10-08T12:15">12:15</time>.</p>
                    </section>
                  </aside>
                </div>
              </div>
            </div>
            <p>No side nav: the main column is capped at the extra-large container; the aside sits beside main from 64rem and drops below it on narrower screens.</p>
```

### app-shell · variant:mobile

```html
<p class="ds-demo__label">variant:mobile — 24rem frame</p>
            <div style="--app-shell-min-block-size: 100%; inline-size: min(100%, 24rem); block-size: 40rem; overflow: auto; border: var(--border-width-thin) solid var(--color-border-default); border-radius: var(--radius-md); background: var(--color-bg-canvas);">
              <div class="app-shell">
                <header class="top-nav top-nav--sticky app-shell__header">
                  <div class="top-nav__bar">
                    <button type="button" class="btn btn--ghost top-nav__toggle" aria-controls="as3-panel" aria-expanded="false"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-menu"></use></svg><span class="btn__label">Menu</span></button>
                    <a class="top-nav__brand" href="#dispatch"><svg class="top-nav__logo" aria-hidden="true" focusable="false"><use href="#icon-truck"></use></svg>Fleetline</a>
                    <div class="top-nav__panel" id="as3-panel">
                      <nav class="top-nav__nav" aria-label="Main (mobile shell example)"><ul class="top-nav__list"><li><a class="top-nav__link" href="#dispatch" aria-current="page">Dispatch</a></li><li><a class="top-nav__link" href="#vehicles">Vehicles</a></li><li><a class="top-nav__link" href="#work-orders">Work orders</a></li><li><a class="top-nav__link" href="#depots">Depots</a></li><li><a class="top-nav__link" href="#reports">Reports</a></li></ul></nav>
                      <form class="top-nav__search" role="search" action="#search"><label class="sr-only" for="as3-q">Search vehicles and work orders</label><svg class="top-nav__search-icon" aria-hidden="true" focusable="false"><use href="#icon-search"></use></svg><input class="top-nav__search-input" id="as3-q" type="search" name="q" placeholder="Plate, VIN or WO number" autocomplete="off"></form>
                    </div>
                    <div class="top-nav__actions">
                      <button type="button" class="icon-btn" aria-label="Notifications, 3 unread"><svg class="icon-btn__icon" aria-hidden="true" focusable="false"><use href="#icon-bell"></use></svg><span class="icon-btn__badge" aria-hidden="true">3</span></button>
                    </div>
                  </div>
                </header>
                <div class="app-shell__body">
                  <div class="app-shell__main" id="as3-main" tabindex="-1">
                    <header class="page-header"><div class="page-header__main"><div class="page-header__heading"><h4 class="page-header__title">Dispatch board</h4><p class="page-header__description">North Yard · 8 October</p></div><div class="page-header__actions"><button type="button" class="btn btn--primary"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-plus"></use></svg><span class="btn__label">New work order</span></button></div></div></header>
                    <div class="stat-group">
                      <div class="stat"><dl class="stat__body"><dt class="stat__label">Vehicles on road</dt><dd class="stat__value">94<span class="stat__unit">of 128</span></dd></dl></div>
                      <div class="stat"><dl class="stat__body"><dt class="stat__label">Overdue services</dt><dd class="stat__value">7</dd></dl><p class="stat__delta stat__delta--bad"><svg aria-hidden="true" focusable="false"><use href="#icon-arrow-up"></use></svg>Up 2 since Monday</p></div>
                    </div>
                    <div class="stack stack--gap-3">
                      <article class="card" aria-labelledby="as3-c1"><header class="card__header"><h5 class="card__title" id="as3-c1">WO-4185 · Truck TR-077</h5><p class="card__meta">Idris Okafor · due 08:00</p></header><p class="card__body"><span class="badge badge--danger"><svg class="badge__icon" aria-hidden="true" focusable="false"><use href="#icon-octagon-alert"></use></svg>Overdue</span></p></article>
                      <article class="card" aria-labelledby="as3-c2"><header class="card__header"><h5 class="card__title" id="as3-c2">WO-4182 · Van KX-219</h5><p class="card__meta">Marta Quintero · due 11:30</p></header><p class="card__body"><span class="badge badge--info"><svg class="badge__icon" aria-hidden="true" focusable="false"><use href="#icon-clock"></use></svg>In progress</span></p></article>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <p>Below 48rem the top nav folds links and search behind <em>Menu</em>; the side nav is hidden and work orders render as cards instead of a wide table.</p>
```

## API

Hook | Values | Purpose
.app-shell | block | Grid rows header / body / footer; size container for the breakpoints
.app-shell__body | part | Columns nav / main / aside (aside column appears when an .app-shell__aside child exists)
.app-shell__header | __nav | __main | __aside | __footer | parts | Grid placement only, added next to the component class
.app-shell--top-nav-only | modifier | No side nav; main capped at --size-container-xl
--app-shell-min-block-size | custom property | Minimum height (default 100dvh )
64rem / 40rem | container breakpoints | Side nav hides below lg; tighter gutters below sm

## Do and don't

Do let the document scroll and keep only the top nav sticky, with html { scroll-padding-top } set to its height. Don't make main a fixed-height scroll box inside the viewport: it breaks zoom, find-in-page and mobile address-bar collapse.

## Accessibility

Landmarks in reading order
Element | Landmark | Notes
a.skip-link | — | First tab stop; moves focus to #main (which has tabindex="-1" )
header.top-nav | banner | Only when it is a direct child of body (not inside main)
nav.top-nav__nav , nav.side-nav | navigation | Each with a distinct aria-label ("Main", "Dispatch")
main#main | main | Exactly one per document; holds the page's h1
aside | complementary | Name it with aria-labelledby
footer | contentinfo | Only when a direct child of body
Source order equals visual and tab order in every variant (no order or reversed grid areas). The sticky top nav needs scroll-padding-top so focused elements are never hidden under it (WCAG 2.4.11). At 320px wide and 400% zoom the shell is a single column with no horizontal scroll.

## Tokens

Custom property | Purpose
--space-4 , --space-6 , --space-8 , --space-10 | Main gutters and gap between page sections
--size-container-xl | Max width of main in the top-nav-only variant
--breakpoint-lg , --breakpoint-sm | Copied as literal 64rem / 40rem in the container queries
