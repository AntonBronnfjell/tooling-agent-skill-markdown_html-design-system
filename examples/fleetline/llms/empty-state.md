# Empty State

Category: Patterns · page `patterns/empty-state.html` · CSS `css/patterns/empty-state.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `empty-state` — Empty State | core | ready · beta | variant:first-use variant:no-results variant:cleared |

## Usage

Show an empty state where a list, table or dashboard tile has nothing to show, in the same place and at about the same height as the content it stands in for. Say what the situation is, what to do next, and offer one way to do it.
- First use — nothing has been created yet. Explain what will appear here and offer the create action: "No work orders yet" + "Create work order".
- No results — a search or filter matched nothing. Repeat the query, suggest a fix and offer "Clear filters". Keep the search box and filters on screen so the query can be edited.
- Cleared — the user finished the queue. Confirm it plainly ("All caught up") and say when there will be more. No action is required; a link to the next useful place is enough.
- Title states the situation in plain words; description is one sentence; one primary action at most. No jokes in error-adjacent states, no illustrations that push the action below the fold on a tablet.
- Not for failures: if the list could not load, use the error tone of the result panel with "Try again".

## Anatomy

- Region — .empty-state (reserves the height of the missing content)
- Icon — .result__icon , decorative ( aria-hidden )
- Title — .result__title , a heading one level below the surrounding section
- Guidance — .result__description , one sentence
- Actions — .result__actions : one primary button, optional secondary link

## Examples

### empty-state · variant:first-use

```html
<p class="ds-demo__label">variant:first-use — inside a card</p>
            <section class="card" aria-labelledby="es1-card">
              <header class="card__header"><h4 class="card__title" id="es1-card">Work orders</h4><p class="card__meta">Van KX-219 · Ford Transit</p></header>
              <div class="empty-state" style="--empty-state-min-block-size: 16rem;">
                <section class="result" aria-labelledby="es1-t">
                  <span class="result__icon" aria-hidden="true"><svg focusable="false"><use href="#icon-clipboard-list"></use></svg></span>
                  <h5 class="result__title" id="es1-t">No work orders yet</h5>
                  <p class="result__description">Repairs and services for this van appear here with their status and mechanic.</p>
                  <div class="result__actions">
                    <button type="button" class="btn btn--primary"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-plus"></use></svg><span class="btn__label">Create work order</span></button>
                    <a class="btn btn--ghost" href="#import">Import from spreadsheet</a>
                  </div>
                </section>
              </div>
            </section>
```

### empty-state · variant:no-results

```html
<p class="ds-demo__label">variant:no-results — filters stay editable</p>
            <div class="empty-state__toolbar">
              <search class="search">
                <form class="search__form" action="#empty-state" method="get">
                  <label class="label" for="es2-q">Search vehicles</label>
                  <div class="input input--affixed search__box">
                    <svg class="search__icon" aria-hidden="true" focusable="false"><use href="#icon-search"></use></svg>
                    <input class="input__control search__control" id="es2-q" name="q" type="search" value="KX-99" autocomplete="off" spellcheck="false">
                    <span class="search__spinner" aria-hidden="true"></span>
                    <button type="button" class="search__clear" aria-label="Clear search" hidden><svg class="icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button>
                  </div>
                  <p class="search__status sr-only" role="status">No vehicles found</p>
                </form>
              </search>
              <div class="field">
                <label class="label" for="es2-depot">Depot</label>
                <div class="select"><select class="select__control" id="es2-depot" name="depot"><option>All depots</option><option selected>North Yard</option><option>Harbour Road</option></select></div>
              </div>
            </div>
            <div class="empty-state" style="--empty-state-min-block-size: 16rem;">
              <section class="result" aria-labelledby="es2-t">
                <span class="result__icon" aria-hidden="true"><svg focusable="false"><use href="#icon-search-x"></use></svg></span>
                <h4 class="result__title" id="es2-t">No results for ‘KX-99’</h4>
                <p class="result__description">No vehicle at North Yard matches that plate. Check the number, or search all 6 depots.</p>
                <div class="result__actions">
                  <button type="button" class="btn btn--primary">Clear filters</button>
                  <a class="btn btn--ghost" href="#vehicles">Browse all vehicles</a>
                </div>
              </section>
            </div>
```

### empty-state · variant:cleared

```html
<p class="ds-demo__label">variant:cleared — queue finished</p>
            <section class="card" aria-labelledby="es3-card">
              <header class="card__header"><h4 class="card__title" id="es3-card">Inspections due</h4><p class="card__meta">North Yard · next 7 days</p></header>
              <div class="empty-state" style="--empty-state-min-block-size: 16rem;">
                <section class="result result--success" aria-labelledby="es3-t">
                  <span class="result__icon" aria-hidden="true"><svg focusable="false"><use href="#icon-check-circle"></use></svg></span>
                  <h5 class="result__title" id="es3-t">All caught up</h5>
                  <p class="result__description">Every vehicle at North Yard has a valid inspection. The next one is due on <time datetime="2026-10-14">14 October</time>.</p>
                  <div class="result__actions">
                    <a class="btn btn--secondary" href="#calendar">Open service calendar</a>
                  </div>
                </section>
              </div>
            </section>
```

## API

Hook | Values | Purpose
.empty-state | block | Region that replaces the list/table; centres the result panel vertically
--empty-state-min-block-size | length (default 20rem) | Match the height of the content it replaces
.empty-state__toolbar | part | Search + filters row kept above a no-results state
.result / .result--success | component | Icon, title, guidance and actions (see Result panel)

## Do and don't

Do repeat the query and give the way out: "No results for ‘KX-99’" + "Clear filters". Don't show a bare "No data" or hide the filters that caused the empty result.

## Accessibility

Announcements and focus
Situation | Behavior
Page loads empty | No live region; the heading is found by heading navigation
Filter or search returns nothing | The result count is announced politely ("No vehicles found") through the search's role="status" ; focus stays in the search box
Last item in a queue is completed | Announce "All caught up" through a status message; move focus to the empty-state heading ( tabindex="-1" ) only if the focused row was removed
The icon is decorative; the title carries the meaning. The title is a real heading at the right level for its container (card title + 1).

## Tokens

Custom property | Purpose
--empty-state-min-block-size | Reserved height (pattern property)
--space-3 , --space-4 | Toolbar gaps
--color-feedback-info-* , --color-feedback-success-* | Icon disc via the result panel tones
