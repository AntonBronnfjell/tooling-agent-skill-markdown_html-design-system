# Tabs

Category: Navigation · page `components/tabs.html` · CSS `css/components/tabs.css` · JS `js/tabs.js` (export `init(root)`)

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `tabs` — Tabs | core | ready · stable | state:selected state:hover state:focus-visible state:disabled variant:underline variant:contained variant:overflow |

## Usage

Use tabs to switch between related views of the same object without leaving the page: a van's overview, service history and documents. Don't use tabs for steps in a sequence (stepper) or to compare content side by side.
- 2–7 tabs; labels are short nouns ("Service history"), sentence case, no verbs.
- Underline for page sections; contained for switching how the same data is shown (Map / List / Timeline).
- If each tab has its own URL, it's navigation: use links with aria-current="page" inside a <nav> (same classes).
- Counts are context, not alerts; keep them in the label's text flow.

## Anatomy

- Tab list — .tabs__list[role=tablist][aria-label]
- Tab — button.tabs__tab[role=tab] with aria-selected and aria-controls
- Count (optional) — .tabs__count
- Selected indicator — 2px bar + semibold + color
- Panel — .tabs__panel[role=tabpanel][aria-labelledby][tabindex=0]

## Examples

### tabs · variant:underline state:selected

```html
<div class="tabs tabs--underline"><div class="tabs__list" role="tablist" aria-label="Van KX-219"><button type="button" class="tabs__tab" role="tab" id="tb1-t0" aria-selected="true" aria-controls="tb1-p0">Overview</button><button type="button" class="tabs__tab" role="tab" id="tb1-t1" aria-selected="false" aria-controls="tb1-p1">Service history <span class="tabs__count">12</span></button><button type="button" class="tabs__tab" role="tab" id="tb1-t2" aria-selected="false" aria-controls="tb1-p2">Inspections</button><button type="button" class="tabs__tab" role="tab" id="tb1-t3" aria-selected="false" aria-controls="tb1-p3">Documents</button></div><div class="tabs__panel" role="tabpanel" id="tb1-p0" aria-labelledby="tb1-t0" tabindex="0"><p>Van KX-219 · Ford Transit · 84,210 km · North Yard depot.</p></div><div class="tabs__panel" role="tabpanel" id="tb1-p1" aria-labelledby="tb1-t1" tabindex="0"><p>12 completed work orders since March 2024.</p></div><div class="tabs__panel" role="tabpanel" id="tb1-p2" aria-labelledby="tb1-t2" tabindex="0"><p>Next brake inspection due 14 November.</p></div><div class="tabs__panel" role="tabpanel" id="tb1-p3" aria-labelledby="tb1-t3" tabindex="0"><p>Registration, insurance and the last emissions test.</p></div></div>
            <p>Automatic activation: arrow keys select as they move (panels are already loaded).</p>
```

### tabs · state:hover state:focus-visible

```html
<div class="tabs tabs--underline"><div class="tabs__list" role="tablist" aria-label="Tab states example"><button type="button" class="tabs__tab" role="tab" id="tb2-t0" aria-selected="true" aria-controls="tb2-p0">Overview</button><button type="button" class="tabs__tab is-hover" role="tab" id="tb2-t1" aria-selected="false" aria-controls="tb2-p1">Service history</button><button type="button" class="tabs__tab is-focus-visible" role="tab" id="tb2-t2" aria-selected="false" aria-controls="tb2-p2">Inspections</button></div><div class="tabs__panel" role="tabpanel" id="tb2-p0" aria-labelledby="tb2-t0" tabindex="0"><p>Overview for van KX-219.</p></div><div class="tabs__panel" role="tabpanel" id="tb2-p1" aria-labelledby="tb2-t1" tabindex="0"><p>Hover state.</p></div><div class="tabs__panel" role="tabpanel" id="tb2-p2" aria-labelledby="tb2-t2" tabindex="0"><p>Focus-visible state.</p></div></div>
```

### tabs · state:disabled

```html
<div class="tabs tabs--underline"><div class="tabs__list" role="tablist" aria-label="Work order WO-4182"><button type="button" class="tabs__tab" role="tab" id="tb3-t0" aria-selected="true" aria-controls="tb3-p0">Tasks</button><button type="button" class="tabs__tab" role="tab" id="tb3-t1" aria-selected="false" aria-controls="tb3-p1">Parts</button><button type="button" class="tabs__tab" role="tab" id="tb3-t2" aria-selected="false" aria-controls="tb3-p2" aria-disabled="true">Invoice</button></div><div class="tabs__panel" role="tabpanel" id="tb3-p0" aria-labelledby="tb3-t0" tabindex="0"><p>3 tasks: replace front pads, check rotors, road test.</p></div><div class="tabs__panel" role="tabpanel" id="tb3-p1" aria-labelledby="tb3-t1" tabindex="0"><p>Front brake pad set ×1, rotor ×2.</p></div><div class="tabs__panel" role="tabpanel" id="tb3-p2" aria-labelledby="tb3-t2" tabindex="0"><p>Available after the work order is closed.</p></div></div>
            <p>Disabled tabs stay focusable so people find them; explain why near the tabs: "Invoice is available after closing."</p>
```

### tabs · variant:contained

```html
<div class="tabs tabs--contained" data-activation="manual"><div class="tabs__list" role="tablist" aria-label="Dispatch board view"><button type="button" class="tabs__tab" role="tab" id="tb4-t0" aria-selected="true" aria-controls="tb4-p0">Map</button><button type="button" class="tabs__tab" role="tab" id="tb4-t1" aria-selected="false" aria-controls="tb4-p1">List</button><button type="button" class="tabs__tab" role="tab" id="tb4-t2" aria-selected="false" aria-controls="tb4-p2">Timeline</button></div><div class="tabs__panel" role="tabpanel" id="tb4-p0" aria-labelledby="tb4-t0" tabindex="0"><p>Map of 42 vans in service.</p></div><div class="tabs__panel" role="tabpanel" id="tb4-p1" aria-labelledby="tb4-t1" tabindex="0"><p>List of 42 vans in service.</p></div><div class="tabs__panel" role="tabpanel" id="tb4-p2" aria-labelledby="tb4-t2" tabindex="0"><p>Today's jobs on a timeline.</p></div></div>
            <p>Manual activation (<kbd>Enter</kbd>/<kbd>Space</kbd>) — the map is expensive to render.</p>
```

### tabs · variant:overflow

```html
<div class="tabs tabs--underline tabs--overflow" style="max-inline-size: 24rem;"><div class="tabs__list" role="tablist" aria-label="Depots"><button type="button" class="tabs__tab" role="tab" id="tb5-t0" aria-selected="true" aria-controls="tb5-p0">North Yard</button><button type="button" class="tabs__tab" role="tab" id="tb5-t1" aria-selected="false" aria-controls="tb5-p1">Harbor Road</button><button type="button" class="tabs__tab" role="tab" id="tb5-t2" aria-selected="false" aria-controls="tb5-p2">Eastgate</button><button type="button" class="tabs__tab" role="tab" id="tb5-t3" aria-selected="false" aria-controls="tb5-p3">Airport</button><button type="button" class="tabs__tab" role="tab" id="tb5-t4" aria-selected="false" aria-controls="tb5-p4">Riverside</button><button type="button" class="tabs__tab" role="tab" id="tb5-t5" aria-selected="false" aria-controls="tb5-p5">Old Town</button><button type="button" class="tabs__tab" role="tab" id="tb5-t6" aria-selected="false" aria-controls="tb5-p6">Southport</button><button type="button" class="tabs__tab" role="tab" id="tb5-t7" aria-selected="false" aria-controls="tb5-p7">Hill Street</button></div><div class="tabs__panel" role="tabpanel" id="tb5-p0" aria-labelledby="tb5-t0" tabindex="0"><p>North Yard depot: vans, mechanics and open work orders.</p></div><div class="tabs__panel" role="tabpanel" id="tb5-p1" aria-labelledby="tb5-t1" tabindex="0"><p>Harbor Road depot: vans, mechanics and open work orders.</p></div><div class="tabs__panel" role="tabpanel" id="tb5-p2" aria-labelledby="tb5-t2" tabindex="0"><p>Eastgate depot: vans, mechanics and open work orders.</p></div><div class="tabs__panel" role="tabpanel" id="tb5-p3" aria-labelledby="tb5-t3" tabindex="0"><p>Airport depot: vans, mechanics and open work orders.</p></div><div class="tabs__panel" role="tabpanel" id="tb5-p4" aria-labelledby="tb5-t4" tabindex="0"><p>Riverside depot: vans, mechanics and open work orders.</p></div><div class="tabs__panel" role="tabpanel" id="tb5-p5" aria-labelledby="tb5-t5" tabindex="0"><p>Old Town depot: vans, mechanics and open work orders.</p></div><div class="tabs__panel" role="tabpanel" id="tb5-p6" aria-labelledby="tb5-t6" tabindex="0"><p>Southport depot: vans, mechanics and open work orders.</p></div><div class="tabs__panel" role="tabpanel" id="tb5-p7" aria-labelledby="tb5-t7" tabindex="0"><p>Hill Street depot: vans, mechanics and open work orders.</p></div></div>
            <p>Too many tabs for the width: the list scrolls with snap points. Arrow keys scroll the focused tab into view.</p>
```

## API

Hook | Values | Purpose
.tabs | block class | Wrapper
.tabs--underline | --contained | modifier | Visual variant
.tabs--overflow | modifier | Room for the scrollbar when tabs overflow
data-activation="manual" | attribute | Select on Enter/Space instead of on focus
.tabs__list | __tab | __count | __icon | __panel | parts | See anatomy
aria-selected / aria-current="page" | attribute | Selected tab / current URL tab
aria-disabled="true" | attribute | Unavailable, focusable
tabs-change | event | Fired on the tablist: detail { tab, panel }

## Do and don't

Overview Service history Documents
Overview for van KX-219.
Service history for van KX-219.
Documents for van KX-219.
Do use short nouns for views of one object. 1. Check brakes 2. Check tires 3. Sign off
1. Check brakes for van KX-219.
2. Check tires for van KX-219.
3. Sign off for van KX-219.
Don't use tabs for ordered steps — use a stepper.

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Moves into the tab list (to the selected tab), then to the panel
← / → | Previous / next tab, wrapping (mirrored in RTL); selects it with automatic activation
Home / End | First / last tab
Enter / Space | Selects the focused tab (manual activation)
- Pattern: WAI-ARIA APG Tabs with roving tabindex ( js/lib/roving-focus.js ) — one Tab stop for the whole list.
- Panels have tabindex="0" so keyboard users reach text-only panels.
- Selected tab: bar, weight and color — never color alone; forced colors use Highlight .
- Screen readers announce "Service history, tab, 2 of 4, selected".

## Tokens

Custom property | Purpose
--color-text-muted | Unselected label
--color-selected-fg | -border | Selected label and bar
--color-action-ghost-bg-hover | Hover
--color-border-default | List baseline
--color-bg-subtle | -surface , --color-border-strong | Contained variant
--size-control-md | -sm | Tab heights
--color-text-disabled | Disabled tab
