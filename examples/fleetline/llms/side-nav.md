# Side Nav

Category: Navigation · page `components/side-nav.html` · CSS `css/components/side-nav.css` · JS `js/side-nav.js` (export `init(root)`)

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `side-nav` — Sidebar Navigation | core | ready · stable | state:expanded state:collapsed variant:nested state:current |

## Usage

Use the side nav for the pages inside one area of Fleetline when there are more than five (the workshop: work orders, inspections, parts, vehicles, mechanics). For the 4–6 top-level areas use the top nav.
- Group links into titled sections; nest at most two levels with a disclosure ( <details> ).
- Labels are nouns for places, ≤ 3 words. Counts say what they count in nearby text or the page ("4" inspections due today).
- The collapsed rail keeps every destination reachable by icon and tooltip; use it on narrow desktops, not on phones (use the top-nav panel there).

## Anatomy

- Collapse button — .side-nav__collapse ( aria-expanded )
- Section heading — .side-nav__heading
- Link — a.side-nav__link with icon, label, optional count
- Nested group — details.side-nav__group + summary.side-nav__summary + chevron
- Current indicator — inline-start bar, selected fill, semibold ( aria-current="page" )

## Examples

### side-nav · state:expanded variant:nested state:current

```html
<nav class="side-nav" aria-label="Workshop (live example)" data-persist="fleetline-docs-side-nav">
              <div class="side-nav__header"><button type="button" class="icon-btn icon-btn--sm side-nav__collapse" aria-expanded="true" aria-label="Collapse navigation"><svg class="icon-btn__icon side-nav__collapse-icon" aria-hidden="true" focusable="false"><use href="#icon-panel-left-close"></use></svg></button></div>
              <div class="side-nav__section">
                <h4 class="side-nav__heading" id="sn1-h1">Workshop</h4>
                <ul class="side-nav__list" aria-labelledby="sn1-h1">
                  <li><a class="side-nav__link" href="#overview"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-layout-dashboard"></use></svg><span class="side-nav__label">Overview</span></a></li>
                  <li><details class="side-nav__group" open><summary class="side-nav__link side-nav__summary"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-clipboard-list"></use></svg><span class="side-nav__label">Work orders</span><svg class="side-nav__chevron" aria-hidden="true" focusable="false"><use href="#icon-chevron-down"></use></svg></summary>
                    <ul class="side-nav__list side-nav__list--nested"><li><a class="side-nav__link" href="#wo-open" aria-current="page"><span class="side-nav__label">Open work orders</span></a></li><li><a class="side-nav__link" href="#wo-parts"><span class="side-nav__label">Waiting for parts</span></a></li><li><a class="side-nav__link" href="#wo-done"><span class="side-nav__label">Completed</span></a></li></ul></details></li>
                  <li><a class="side-nav__link" href="#inspections"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-wrench"></use></svg><span class="side-nav__label">Inspections</span><span class="side-nav__count">4</span></a></li>
                  <li><a class="side-nav__link" href="#parts"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-package"></use></svg><span class="side-nav__label">Parts inventory</span></a></li>
                </ul>
              </div>
              <div class="side-nav__section">
                <h4 class="side-nav__heading" id="sn1-h2">Fleet</h4>
                <ul class="side-nav__list" aria-labelledby="sn1-h2">
                  <li><a class="side-nav__link" href="#vehicles"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-truck"></use></svg><span class="side-nav__label">Vehicles</span><span class="side-nav__count">128</span></a></li>
                  <li><a class="side-nav__link" href="#depots"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-map-pin"></use></svg><span class="side-nav__label">Depots</span></a></li>
                  <li><a class="side-nav__link" href="#mechanics"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-users"></use></svg><span class="side-nav__label">Mechanics</span></a></li>
                  <li><a class="side-nav__link" href="#calendar"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-calendar"></use></svg><span class="side-nav__label">Service calendar</span></a></li>
                </ul>
              </div>
            </nav>
            <p>Live: the collapse button switches to the icon rail and remembers the choice.</p>
```

### side-nav · state:collapsed

```html
<nav class="side-nav" aria-label="Workshop (collapsed example)" data-collapsed>
              <div class="side-nav__header"><button type="button" class="icon-btn icon-btn--sm side-nav__collapse" aria-expanded="false" aria-label="Expand navigation"><svg class="icon-btn__icon side-nav__collapse-icon" aria-hidden="true" focusable="false"><use href="#icon-panel-left-close"></use></svg></button></div>
              <div class="side-nav__section">
                <h4 class="side-nav__heading" id="sn2-h1">Workshop</h4>
                <ul class="side-nav__list" aria-labelledby="sn2-h1">
                  <li><a class="side-nav__link" href="#overview"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-layout-dashboard"></use></svg><span class="side-nav__label">Overview</span></a></li>
                  <li><details class="side-nav__group" open><summary class="side-nav__link side-nav__summary"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-clipboard-list"></use></svg><span class="side-nav__label">Work orders</span><svg class="side-nav__chevron" aria-hidden="true" focusable="false"><use href="#icon-chevron-down"></use></svg></summary>
                    <ul class="side-nav__list side-nav__list--nested"><li><a class="side-nav__link" href="#wo-open" aria-current="page"><span class="side-nav__label">Open work orders</span></a></li><li><a class="side-nav__link" href="#wo-parts"><span class="side-nav__label">Waiting for parts</span></a></li><li><a class="side-nav__link" href="#wo-done"><span class="side-nav__label">Completed</span></a></li></ul></details></li>
                  <li><a class="side-nav__link" href="#inspections"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-wrench"></use></svg><span class="side-nav__label">Inspections</span><span class="side-nav__count">4</span></a></li>
                  <li><a class="side-nav__link" href="#parts"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-package"></use></svg><span class="side-nav__label">Parts inventory</span></a></li>
                </ul>
              </div>
              <div class="side-nav__section">
                <h4 class="side-nav__heading" id="sn2-h2">Fleet</h4>
                <ul class="side-nav__list" aria-labelledby="sn2-h2">
                  <li><a class="side-nav__link" href="#vehicles"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-truck"></use></svg><span class="side-nav__label">Vehicles</span><span class="side-nav__count">128</span></a></li>
                  <li><a class="side-nav__link" href="#depots"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-map-pin"></use></svg><span class="side-nav__label">Depots</span></a></li>
                  <li><a class="side-nav__link" href="#mechanics"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-users"></use></svg><span class="side-nav__label">Mechanics</span></a></li>
                  <li><a class="side-nav__link" href="#calendar"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-calendar"></use></svg><span class="side-nav__label">Service calendar</span></a></li>
                </ul>
              </div>
            </nav>
            <p>Icon rail: names stay in the accessibility tree; hovering shows them as tooltips.</p>
```

### side-nav · state:hover state:focus-visible

```html
<nav class="side-nav" aria-label="Link states example"><ul class="side-nav__list"><li><a class="side-nav__link is-hover" href="#vehicles"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-truck"></use></svg><span class="side-nav__label">Vehicles (hover)</span></a></li><li><a class="side-nav__link is-focus-visible" href="#depots"><svg class="side-nav__icon" aria-hidden="true" focusable="false"><use href="#icon-map-pin"></use></svg><span class="side-nav__label">Depots (focus)</span></a></li></ul></nav>
```

## API

Hook | Values | Purpose
.side-nav | block class | <nav aria-label> sidebar
[data-collapsed] | attribute (set by JS) | Icon rail
data-persist | attribute | localStorage key for the collapse state
.side-nav__header | __collapse | __section | __heading | __list | __list--nested | __link | __icon | __label | __count | __group | __summary | __chevron | parts | See anatomy
aria-current="page" | attribute | Current page
aria-expanded (collapse button) | attribute | Expanded / collapsed

## Do and don't

Workshop → Work orders → Open work orders
Do keep nesting to two levels and mark the current page.
Fleet → Vans → Electric → North Yard → KX-219
Don't use the side nav as a data tree — that's a tree view or a filtered table.

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Moves through the collapse button, links and group summaries
Enter | Follows a link
Enter / Space (summary) | Expands / collapses a nested group
Enter / Space (collapse) | Switches between full and icon rail
- Landmark: <nav> with a unique aria-label ("Workshop"), different from the top nav's "Main".
- Collapsed rail: labels are clipped, not removed, so link names don't change; js/side-nav.js adds title tooltips.
- Current page: bar + fill + weight. A group containing the current page shows its summary in bold.
- Forced colors: the current bar uses Highlight .

## Tokens

Custom property | Purpose
--color-bg-surface , --color-border-default | Panel
--color-selected-bg | -fg | -border | Current link
--color-action-ghost-bg-hover | Hover
--size-control-md | -sm | Link height (comfortable / compact)
--color-bg-muted | Count pill
--motion-duration-base | Collapse width transition (off with reduced motion)
