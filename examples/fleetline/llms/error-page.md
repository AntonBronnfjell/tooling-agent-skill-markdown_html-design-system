# Error Page

Category: Patterns · page `patterns/error-page.html` · CSS `css/patterns/error-page.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `error-page` — Error Pages (404/500) | core | ready · beta | variant:404 variant:500 variant:offline variant:403 |

## Usage

Use these full pages when a whole screen can't be shown. For a failure inside one part of a screen (a tile that didn't load, a save that failed) use an inline alert or the result panel in place, and keep the rest of the screen working.
- Keep the header. Error pages use the top-nav-only app shell, so people can navigate away without the back button.
- Plain language, no blame: say what happened, what is safe, and what to do next. No status codes as the headline, no jokes, no "Oops".
- 404: a search box plus the way home. 403: who you're signed in as, who can grant access, "Request access" and "Switch account". 500: "Try again", the status page, and a copyable reference ID. Offline: what is saved locally and that it will sync on its own.
- Correct HTTP status and a matching <title> ("Page not found — Fleetline"); the result title is the page's only h1 .
- Planned downtime is not a 500: use the service-unavailable pattern with the return time.

## Anatomy

- Header — header.top-nav inside .app-shell--top-nav-only
- Main — main#main.app-shell__main.error-page (centres the panel vertically)
- Result panel — .result.result--page + tone ( --error , --warning , --no-permission )
- Title — h1.result__title ; description; reference ID .result__reference (500)
- Search (404) — search.search.error-page__search
- Actions — .result__actions ; technical details details.result__details (500, optional)

## Examples

### error-page · variant:404

```html
<p class="ds-demo__label">variant:404 — &lt;title&gt;Page not found — Fleetline&lt;/title&gt;</p>
            <div style="--app-shell-min-block-size: 100%; block-size: 34rem; overflow: auto; border: var(--border-width-thin) solid var(--color-border-default); border-radius: var(--radius-md); background: var(--color-bg-canvas);">
              <div class="app-shell app-shell--top-nav-only">
                <header class="top-nav app-shell__header">
                  <div class="top-nav__bar">
                    <button type="button" class="btn btn--ghost top-nav__toggle" aria-controls="e404-panel"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-menu"></use></svg><span class="btn__label">Menu</span></button>
                    <a class="top-nav__brand" href="#dispatch"><svg class="top-nav__logo" aria-hidden="true" focusable="false"><use href="#icon-truck"></use></svg>Fleetline</a>
                    <div class="top-nav__panel" id="e404-panel">
                      <nav class="top-nav__nav" aria-label="Main (404 example)"><ul class="top-nav__list"><li><a class="top-nav__link" href="#dispatch">Dispatch</a></li><li><a class="top-nav__link" href="#vehicles">Vehicles</a></li><li><a class="top-nav__link" href="#work-orders" aria-current="page">Work orders</a></li><li><a class="top-nav__link" href="#reports">Reports</a></li></ul></nav>
                    </div>
                  </div>
                </header>
                <div class="app-shell__body">
                  <div class="app-shell__main error-page" id="e404-main" tabindex="-1">
                    <section class="result result--page" aria-labelledby="e404-t">
                      <span class="result__icon" aria-hidden="true"><svg focusable="false"><use href="#icon-file-question"></use></svg></span>
                      <h4 class="result__title" id="e404-t" tabindex="-1">We can’t find that page</h4>
                      <p class="result__description">The work order may have been archived, or the link has a typo. Search for it by number or plate.</p>
                      <search class="search error-page__search">
                        <form class="search__form" action="#search" method="get">
                          <label class="label" for="e404-q">Search vehicles and work orders</label>
                          <div class="input input--affixed search__box">
                            <svg class="search__icon" aria-hidden="true" focusable="false"><use href="#icon-search"></use></svg>
                            <input class="input__control search__control" id="e404-q" name="q" type="search" placeholder="Plate, VIN or WO number" autocomplete="off" spellcheck="false">
                            <span class="search__spinner" aria-hidden="true"></span>
                            <button type="button" class="search__clear" aria-label="Clear search" hidden><svg class="icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button>
                          </div>
                          <p class="search__status sr-only" role="status"></p>
                        </form>
                      </search>
                      <div class="result__actions">
                        <a class="btn btn--secondary" href="#dispatch">Go to dispatch board</a>
                      </div>
                    </section>
                  </div>
                </div>
              </div>
            </div>
            <p>Not found: plain words, no blame, a search box and the way home. Respond with HTTP 404.</p>
```

### error-page · variant:403

```html
<p class="ds-demo__label">variant:403 — &lt;title&gt;No access — Fleetline&lt;/title&gt;</p>
            <div style="--app-shell-min-block-size: 100%; block-size: 34rem; overflow: auto; border: var(--border-width-thin) solid var(--color-border-default); border-radius: var(--radius-md); background: var(--color-bg-canvas);">
              <div class="app-shell app-shell--top-nav-only">
                <header class="top-nav app-shell__header">
                  <div class="top-nav__bar">
                    <button type="button" class="btn btn--ghost top-nav__toggle" aria-controls="e403-panel"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-menu"></use></svg><span class="btn__label">Menu</span></button>
                    <a class="top-nav__brand" href="#dispatch"><svg class="top-nav__logo" aria-hidden="true" focusable="false"><use href="#icon-truck"></use></svg>Fleetline</a>
                    <div class="top-nav__panel" id="e403-panel">
                      <nav class="top-nav__nav" aria-label="Main (403 example)"><ul class="top-nav__list"><li><a class="top-nav__link" href="#dispatch">Dispatch</a></li><li><a class="top-nav__link" href="#vehicles">Vehicles</a></li><li><a class="top-nav__link" href="#work-orders">Work orders</a></li><li><a class="top-nav__link" href="#reports" aria-current="page">Reports</a></li></ul></nav>
                    </div>
                  </div>
                </header>
                <div class="app-shell__body">
                  <div class="app-shell__main error-page" id="e403-main" tabindex="-1">
                    <section class="result result--page result--no-permission" aria-labelledby="e403-t">
                      <span class="result__icon" aria-hidden="true"><svg focusable="false"><use href="#icon-lock"></use></svg></span>
                      <h4 class="result__title" id="e403-t" tabindex="-1">You don’t have access to Harbour Road reports</h4>
                      <p class="result__description">You’re signed in as Rosa Méndez (North Yard dispatch). Reports for other depots are limited to their managers. Priya Shah, fleet admin, can give you access.</p>
                      <div class="result__actions">
                        <button type="button" class="btn btn--primary">Request access</button>
                        <a class="btn btn--ghost" href="#switch-account">Switch account</a>
                      </div>
                    </section>
                  </div>
                </div>
              </div>
            </div>
            <p>No access: say who you're signed in as, who can grant access, and offer to switch account. HTTP 403.</p>
```

### error-page · variant:500

```html
<p class="ds-demo__label">variant:500 — &lt;title&gt;Something went wrong — Fleetline&lt;/title&gt;</p>
            <div style="--app-shell-min-block-size: 100%; block-size: 34rem; overflow: auto; border: var(--border-width-thin) solid var(--color-border-default); border-radius: var(--radius-md); background: var(--color-bg-canvas);">
              <div class="app-shell app-shell--top-nav-only">
                <header class="top-nav app-shell__header">
                  <div class="top-nav__bar">
                    <button type="button" class="btn btn--ghost top-nav__toggle" aria-controls="e500-panel"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-menu"></use></svg><span class="btn__label">Menu</span></button>
                    <a class="top-nav__brand" href="#dispatch"><svg class="top-nav__logo" aria-hidden="true" focusable="false"><use href="#icon-truck"></use></svg>Fleetline</a>
                    <div class="top-nav__panel" id="e500-panel">
                      <nav class="top-nav__nav" aria-label="Main (500 example)"><ul class="top-nav__list"><li><a class="top-nav__link" href="#dispatch" aria-current="page">Dispatch</a></li><li><a class="top-nav__link" href="#vehicles">Vehicles</a></li><li><a class="top-nav__link" href="#work-orders">Work orders</a></li><li><a class="top-nav__link" href="#reports">Reports</a></li></ul></nav>
                    </div>
                  </div>
                </header>
                <div class="app-shell__body">
                  <div class="app-shell__main error-page" id="e500-main" tabindex="-1">
                    <section class="result result--page result--error" aria-labelledby="e500-t">
                      <span class="result__icon" aria-hidden="true"><svg focusable="false"><use href="#icon-circle-x"></use></svg></span>
                      <h4 class="result__title" id="e500-t" tabindex="-1">Something went wrong on our side</h4>
                      <p class="result__description">We couldn’t load the dispatch board. Nothing you saved is lost. Try again in a minute; if it keeps happening, give support this reference: <code class="result__reference">ERR-20261008-4QX7</code></p>
                      <div class="result__actions">
                        <a class="btn btn--primary" href="#dispatch"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-rotate-cw"></use></svg><span class="btn__label">Try again</span></a>
                        <a class="btn btn--ghost" href="#status">Check service status</a>
                      </div>
                      <details class="result__details">
                        <summary>Technical details</summary>
                        <dl>
                          <dt>Reference</dt><dd>ERR-20261008-4QX7</dd>
                          <dt>Time</dt><dd><time datetime="2026-10-08T14:32:07Z">8 Oct 2026, 14:32 UTC</time></dd>
                          <dt>Request</dt><dd>GET /dispatch/north-yard → 500</dd>
                        </dl>
                      </details>
                    </section>
                  </div>
                </div>
              </div>
            </div>
            <p>Server error: reassure about data, offer retry and the status page, and show a copyable reference ID. HTTP 500.</p>
```

### error-page · variant:offline

```html
<p class="ds-demo__label">variant:offline — &lt;title&gt;You're offline — Fleetline&lt;/title&gt;</p>
            <div style="--app-shell-min-block-size: 100%; block-size: 34rem; overflow: auto; border: var(--border-width-thin) solid var(--color-border-default); border-radius: var(--radius-md); background: var(--color-bg-canvas);">
              <div class="app-shell app-shell--top-nav-only">
                <header class="top-nav app-shell__header">
                  <div class="top-nav__bar">
                    <button type="button" class="btn btn--ghost top-nav__toggle" aria-controls="eoff-panel"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-menu"></use></svg><span class="btn__label">Menu</span></button>
                    <a class="top-nav__brand" href="#dispatch"><svg class="top-nav__logo" aria-hidden="true" focusable="false"><use href="#icon-truck"></use></svg>Fleetline</a>
                    <div class="top-nav__panel" id="eoff-panel">
                      <nav class="top-nav__nav" aria-label="Main (offline example)"><ul class="top-nav__list"><li><a class="top-nav__link" href="#dispatch">Dispatch</a></li><li><a class="top-nav__link" href="#vehicles">Vehicles</a></li><li><a class="top-nav__link" href="#work-orders" aria-current="page">Work orders</a></li><li><a class="top-nav__link" href="#reports">Reports</a></li></ul></nav>
                    </div>
                  </div>
                </header>
                <div class="app-shell__body">
                  <div class="app-shell__main error-page" id="eoff-main" tabindex="-1">
                    <section class="result result--page result--warning" aria-labelledby="eoff-t">
                      <span class="result__icon" aria-hidden="true"><svg focusable="false"><use href="#icon-wifi-off"></use></svg></span>
                      <h4 class="result__title" id="eoff-t" tabindex="-1">You’re offline</h4>
                      <p class="result__description">This tablet can’t reach Fleetline. 2 service logs are saved on it and will send on their own when the connection is back.</p>
                      <div class="result__actions">
                        <button type="button" class="btn btn--primary"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-rotate-cw"></use></svg><span class="btn__label">Try again</span></button>
                        <a class="btn btn--ghost" href="#saved-logs">View saved service logs</a>
                      </div>
                    </section>
                  </div>
                </div>
              </div>
            </div>
            <p>Offline (service worker fallback on tablets): say what is safe locally and that it will sync without action.</p>
```

## API

Hook | Values | Purpose
.error-page | block, on .app-shell__main | Centres the result panel in the available height
.error-page__search | part, on search.search | Full-width search inside the centred panel (404)
.result--page + tone | component modifiers | 404 info (default) · 403 --no-permission · 500 --error · offline --warning

## Do and don't

Do say what is safe ("Nothing you saved is lost") and give a reference ID support can look up. Don't strip the header or show a raw stack trace; technical details go in a collapsed details .

## Accessibility

Announcement and focus
Situation | Behavior
Full page load (server error page) | The <title> is announced; the h1 is the first heading in main
Client-side route fails | Update document.title , then move focus to the h1 ( tabindex="-1" ) so the change is announced
Connection drops | Show the offline page (or an inline banner) and announce it once through role="status" ; don't trap focus
Reference ID | Plain text, selectable with one click ( user-select: all ), readable by screen readers character by character
Tone comes from the icon and the title words, never color alone. "Try again" for a page load is a link to the same URL (works without JavaScript); offline retry is a button because it only re-checks the connection.

## Tokens

Custom property | Purpose
--size-container-sm | Max width of the 404 search
--color-feedback-danger-* , --color-feedback-warning-* , --color-bg-muted | Icon disc tones via the result panel
--space-16 | Page-level padding of .result--page
