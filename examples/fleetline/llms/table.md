# Table

Category: Data Display · page `components/table.html` · CSS `css/components/table.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `table` — Table (basic) | core | ready · stable | variant:default variant:striped variant:compact variant:with-caption |

## Usage

Use a table to compare records across the same columns: work orders, service intervals, parts costs. Use a list group when each row is one item with a title and a few details, and a description list for the fields of a single vehicle.
- Default — row dividers only; fits most screens.
- Striped — wide tables with 6+ columns where the eye loses the row.
- Compact — dispatcher desktop views with many rows; never on tablet screens mechanics use with gloves.
- Bordered — dense numeric grids (cost breakdowns) where cells must read as separate.
Content: column headers are nouns in sentence case with the unit in brackets ("Labour (h)", "Parts (€)"). Format numbers with the locale ( Intl.NumberFormat ); show "0.00", not an empty cell, when the value is zero, and "—" with .sr-only "Not recorded" when it is unknown. Sorting, selection and pagination belong to the data table.

## Anatomy

- Scroll wrapper — .table-wrap , role="region" , tabindex="0" , labelled by the caption
- Caption — <caption> , visible ( .table__caption ) or .sr-only
- Column headers — <th scope="col"> in <thead>
- Row header — <th scope="row"> , the identifying cell (work order number)
- Data cells — <td> ; numeric ones get .table__num
- Secondary line (optional) — .table__secondary inside a cell

## Examples

### table · variant:default

```html
<div class="table-wrap" role="region" aria-labelledby="t-default" tabindex="0">
              <table class="table">
                <caption id="t-default" class="sr-only">Open work orders</caption>
                <thead>
                  <tr><th scope="col">Work order</th><th scope="col">Vehicle</th><th scope="col">Mechanic</th><th scope="col" class="table__num">Labour (h)</th><th scope="col" class="table__num">Parts (€)</th></tr>
                </thead>
                <tbody>
                  <tr><th scope="row">WO-4182</th><td>Van KX-219<span class="table__secondary">Ford Transit, 84,212 km</span></td><td>Marta Quintero</td><td class="table__num">3.5</td><td class="table__num">412.80</td></tr>
                  <tr><th scope="row">WO-4185</th><td>Truck TR-077<span class="table__secondary">Volvo FH, 312,940 km</span></td><td>Idris Okafor</td><td class="table__num">11.0</td><td class="table__num">2,940.00</td></tr>
                  <tr><th scope="row">WO-4191</th><td>Van KX-224<span class="table__secondary">Mercedes Sprinter, 51,006 km</span></td><td>Lena Brandt</td><td class="table__num">1.25</td><td class="table__num">68.40</td></tr>
                  <tr><th scope="row">WO-4193</th><td>Pickup PU-012<span class="table__secondary">Toyota Hilux, 140,377 km</span></td><td>Marta Quintero</td><td class="table__num">0.75</td><td class="table__num">0.00</td></tr>
                </tbody>
              </table>
            </div>
```

### table · variant:striped

```html
<div class="table-wrap" role="region" aria-labelledby="t-striped" tabindex="0">
              <table class="table table--striped">
                <caption id="t-striped" class="sr-only">Open work orders, depot north</caption>
                <thead>
                  <tr><th scope="col">Work order</th><th scope="col">Vehicle</th><th scope="col">Mechanic</th><th scope="col" class="table__num">Labour (h)</th><th scope="col" class="table__num">Parts (€)</th></tr>
                </thead>
                <tbody>
                  <tr><th scope="row">WO-4182</th><td>Van KX-219<span class="table__secondary">Ford Transit, 84,212 km</span></td><td>Marta Quintero</td><td class="table__num">3.5</td><td class="table__num">412.80</td></tr>
                  <tr><th scope="row">WO-4185</th><td>Truck TR-077<span class="table__secondary">Volvo FH, 312,940 km</span></td><td>Idris Okafor</td><td class="table__num">11.0</td><td class="table__num">2,940.00</td></tr>
                  <tr><th scope="row">WO-4191</th><td>Van KX-224<span class="table__secondary">Mercedes Sprinter, 51,006 km</span></td><td>Lena Brandt</td><td class="table__num">1.25</td><td class="table__num">68.40</td></tr>
                  <tr><th scope="row">WO-4193</th><td>Pickup PU-012<span class="table__secondary">Toyota Hilux, 140,377 km</span></td><td>Marta Quintero</td><td class="table__num">0.75</td><td class="table__num">0.00</td></tr>
                </tbody>
              </table>
            </div>
```

### table · variant:compact

```html
<div class="table-wrap" role="region" aria-labelledby="t-compact" tabindex="0">
              <table class="table table--compact">
                <caption id="t-compact" class="sr-only">Open work orders (compact)</caption>
                <thead>
                  <tr><th scope="col">Work order</th><th scope="col">Vehicle</th><th scope="col">Mechanic</th><th scope="col" class="table__num">Labour (h)</th><th scope="col" class="table__num">Parts (€)</th></tr>
                </thead>
                <tbody>
                  <tr><th scope="row">WO-4182</th><td>Van KX-219<span class="table__secondary">Ford Transit, 84,212 km</span></td><td>Marta Quintero</td><td class="table__num">3.5</td><td class="table__num">412.80</td></tr>
                  <tr><th scope="row">WO-4185</th><td>Truck TR-077<span class="table__secondary">Volvo FH, 312,940 km</span></td><td>Idris Okafor</td><td class="table__num">11.0</td><td class="table__num">2,940.00</td></tr>
                  <tr><th scope="row">WO-4191</th><td>Van KX-224<span class="table__secondary">Mercedes Sprinter, 51,006 km</span></td><td>Lena Brandt</td><td class="table__num">1.25</td><td class="table__num">68.40</td></tr>
                  <tr><th scope="row">WO-4193</th><td>Pickup PU-012<span class="table__secondary">Toyota Hilux, 140,377 km</span></td><td>Marta Quintero</td><td class="table__num">0.75</td><td class="table__num">0.00</td></tr>
                </tbody>
              </table>
            </div>
```

### table · variant:with-caption

```html
<div class="table-wrap" role="region" aria-labelledby="t-caption" tabindex="0">
              <table class="table table--bordered">
                <caption id="t-caption" class="table__caption">Open work orders — week 41</caption>
                <thead>
                  <tr><th scope="col">Work order</th><th scope="col">Vehicle</th><th scope="col">Mechanic</th><th scope="col" class="table__num">Labour (h)</th><th scope="col" class="table__num">Parts (€)</th></tr>
                </thead>
                <tbody>
                  <tr><th scope="row">WO-4182</th><td>Van KX-219<span class="table__secondary">Ford Transit, 84,212 km</span></td><td>Marta Quintero</td><td class="table__num">3.5</td><td class="table__num">412.80</td></tr>
                  <tr><th scope="row">WO-4185</th><td>Truck TR-077<span class="table__secondary">Volvo FH, 312,940 km</span></td><td>Idris Okafor</td><td class="table__num">11.0</td><td class="table__num">2,940.00</td></tr>
                  <tr><th scope="row">WO-4191</th><td>Van KX-224<span class="table__secondary">Mercedes Sprinter, 51,006 km</span></td><td>Lena Brandt</td><td class="table__num">1.25</td><td class="table__num">68.40</td></tr>
                  <tr><th scope="row">WO-4193</th><td>Pickup PU-012<span class="table__secondary">Toyota Hilux, 140,377 km</span></td><td>Marta Quintero</td><td class="table__num">0.75</td><td class="table__num">0.00</td></tr>
                </tbody>
              </table>
            </div>
```

## API

Hook | Values | Purpose
.table | block class | Base table: full width, row dividers
.table--striped | --compact | --bordered | modifier class | Zebra rows, tighter cells, cell borders
.table-wrap | wrapper class | Horizontal scroll container; add role="region" tabindex="0" aria-labelledby
.table__caption | part class | Visible caption style (or use .sr-only )
.table__num | part class | End-aligned, tabular numerals; put it on the header too
.table__secondary | part class | Muted second line in a cell
[data-density="compact"] | ancestor attribute | Same as .table--compact

## Do and don't

Header "Parts (€)", value 2,940.00 end-aligned.
Do put units in the header and align numbers on the decimal side.
Header "Parts", value €2940 start-aligned.
Don’t repeat units in every cell or start-align numbers.
<th scope="row">WO-4182</th>
Do mark the identifying cell of each row as a row header.
<div class="row"> grids pretending to be tables.
Don’t build tables from divs; screen readers lose row and column context.

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Moves focus to the scroll wrapper when the table overflows
← / → | Scrolls the focused wrapper horizontally
- Role: native <table> . Screen readers announce "table, Open work orders, 5 columns, 5 rows" and read the header with each cell.
- Every table has a <caption> ; hide it with .sr-only only when a visible heading right above says the same.
- scope="col" and scope="row" on headers. Don't use role="grid" unless cells are interactive with arrow-key navigation.
- The scroll wrapper is focusable so keyboard users can reach overflowing columns; its name comes from the caption.
- Forced colors: all cell borders switch to CanvasText ; stripes are dropped.

## Tokens

Custom property | Purpose
--density-comfortable-cell-padding-y / --density-compact-cell-padding-y | Row height per density
--space-3 | -4 | Cell inline padding
--color-border-default | -strong | Row dividers, header underline
--color-bg-subtle | Header fill and stripes
--color-text-default | -muted | Cell text, secondary line
--font-size-sm | -xs | -md | Cell, secondary line, caption
--focus-ring-* | Focus ring on the scroll wrapper
