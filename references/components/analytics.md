# Analytics components & pages — specs

Scope `analytics` (enable with `ds init --scopes product,analytics` or, in an existing system, add `"analytics"` to `ds.config.json → scopes` and run `ds init <dir> --force` to copy scope tokens; hand-editing alone plans components but copies no tokens). It has no required scopes. Components live in `components/<file>.html` (category **Analytics**); full pages in `patterns/<file>.html` (category **Analytics Pages**). Analytics components compose product components — `stat`, `chart-container`, `chart-legend`, `chart-tooltip`, `chart-axis`, `sparkline`, `data-table`, `date-range-picker`, `saved-filters`, `hover-card`, `menu-button`, `badge`, `empty-state`, `skeleton` — wrap them, never re-style them. This scope ships no landing page; B2B marketing uses `landing-page variant:saas`.

## Contents
1. Rules for every analytics surface
2. Filtering & output: analytics-filter-bar, report-table, export-menu, data-freshness
3. Meaning: metric-definition, scorecard
4. Analysis views: funnel-chart, cohort-table, pivot-table
5. Authoring & monitoring: report-builder, scheduled-report, chart-annotation, alert-rule
6. Pages

## 1. Rules for every analytics surface
Sources: WCAG 1.1.1 (non-text content), 1.4.1 (use of color), 1.4.11 (non-text contrast), ARIA APG grid and table patterns, `Intl.NumberFormat` and `Intl.DateTimeFormat`, and the dataviz palette in `references/imagery.md` (`dataviz.categorical.1…8`, sequential, diverging). Cite rules, not statistics.

- **Every chart has a table or text alternative.** The underlying data is a real `<table>` (in a `<details>` "Show data table" or a toggle) and the SVG carries `role="img"`, a takeaway in `aria-label` and `aria-describedby` to a longer summary (WCAG 1.1.1). Compose `chart-container`; do not respecify its parts.
- **Never color alone.** Series, deltas, heatmap cells, status and missed targets carry a second channel: direct label, marker shape, dash pattern, arrow icon, sign or text (WCAG 1.4.1). Series use the dataviz palette in fixed order and each mark meets 3:1 against `color.bg.surface` (WCAG 1.4.11).
- **Deltas are arrow + signed number + text.** A delta reads "▲ +12% vs last month" with the arrow as an `aria-hidden` icon and visually-hidden words ("up 12 percent compared with last month"). Color from `color.metric.delta.up|down|flat` only reinforces it. Use a real minus (U+2212) and `Intl.NumberFormat` with `signDisplay: 'always'`.
- **Direction is not sentiment.** Up is not always good: cost, churn, latency and error rate going up is bad. The metric definition declares its positive direction (`higher-is-better`, `lower-is-better` or `neutral`) and the delta tone is derived from that, not from the sign. A neutral metric (traffic mix) uses the `flat` token for both directions. The text still says "up" or "down" so meaning never depends on tone. Token mapping: `metric.delta.up|down|flat` name the tone (favorable, unfavorable, neutral), not the arrow. Pick the token from the metric's declared positive direction and keep the arrow and sign from the actual change; e.g. a lower-is-better cost metric that rises shows ▲ +12% in `color.metric.delta.down`.
- **Numbers are formatted by locale.** `Intl.NumberFormat(locale, {notation: 'compact'})` for large values in tiles and axes ("1.2M"), full values in tables and in an accessible name or adjacent hidden text, `tabular-nums` and end alignment in columns, `style: 'percent'` for rates, an explicit currency. Never concatenate symbols or hand-build separators.
- **Time zones and ranges are stated.** Every date filter and every "as of" time shows its time zone ("Oct 1 – Oct 31, 2026, UTC" or the account zone) and whether the end date is inclusive; comparison ranges are written out ("vs Sep 1 – Sep 30"). Render with `Intl.DateTimeFormat` inside `<time datetime>`. Presets such as "Last 7 days" show the resolved dates beside them.
- **Filters apply on an explicit action or after a short debounce**, never on focus (WCAG 3.2.2). Applied filters are visible as removable text chips and as a sentence in the report header and in exports, so a screenshot or export is self-describing.
- **Loading and empty states explain themselves.** `skeleton` keeps layout and never replaces text a screen reader needs; `no-data` says why (no events in range, filter too narrow, data not yet collected) and offers one next action. A missing value is "No data", never `0`; zero and null are distinct.
- **State freshness.** Every report shows when its data was last updated (`data-freshness`). Stale or partial data is flagged in text, not only with a tone, and totals computed from partial data say so.
- **One polite announcement per update.** Applying filters, finishing an export or a refresh announces once through a single `role="status"` region (`js/lib/live-region.js`), for example "Report updated: 1,204 rows, Oct 1 – Oct 31 UTC". No `aria-live` on tiles, chart marks or table cells.
- **Sampling, estimates and definitions are disclosed.** Estimated or sampled figures are marked in text ("Estimated"), and each metric links to its `metric-definition` so two reports that disagree can be reconciled.
- **Privacy in exports and shares.** Exports and shared read-only views respect the viewer's data permissions, suppress small cohorts below a documented threshold, and never embed unmasked personal data in a filename or URL.
- **Reduced motion and forced colors.** Chart entry animation and number count-up are off under `prefers-reduced-motion`; in forced-colors mode lines use `CanvasText` and fills fall back to patterns.
- **Tokens**: `color.metric.delta.up|down|flat` (favorable, unfavorable, neutral tone; see the token mapping in the direction rule) alias `color.feedback.success.fg`, `color.feedback.danger.fg` and `color.text.muted`. Each is contrast-pair-checked against `color.bg.surface` at 4.5:1; because the aliases already adapt per theme, the scope ships no `themes/` overrides. The `$description` of each token says "always paired with an arrow icon and a signed number". Everything else composes product tokens and `dataviz.*`.
- **vs.**: `scorecard` vs product `stat`: `stat` already does value, trend and sparkline; use `scorecard` when a target or a previous-period comparison is part of the point (it composes `stat`). `report-table` vs `data-table`: `data-table` is the general interactive grid; `report-table` is a read-only, caption-led table with totals, drill-down and report states, built on it. `pivot-table` vs `report-table`: pivot groups on both axes and recomputes totals; report-table has one row dimension. `cohort-table` vs a chart heatmap: cohort-table is a table first and always prints the numbers.

## 2. Filtering & output

### analytics-filter-bar
- Markup: `<form aria-label="Report filters">` (a form landmark, not `role="search"`, since these are filters rather than a search box) with `<fieldset>`s (date range via `date-range-picker`, segments via `select`/`combobox`) and an "Apply" `button-primary`. Applied filters render as a `<ul>` of chips, each a text "Remove filter: Country is Germany" button.
- `variant:date-presets`: preset buttons in a labelled group (Today, Last 7 days, Last 30 days, This quarter, Custom) as `aria-pressed` toggles in one group; the resolved dates and time zone sit beside the presets ("Oct 11 – Oct 17, UTC"). "Custom" opens `date-range-picker`.
- `variant:compare-to`: a `select` "Compare to" (Previous period, Same period last year, None) plus a visible sentence of the comparison dates. Compare-to is disabled with an explanation when it would overlap the main range.
- `variant:segments`: segment chooser via `combobox` multi-select with a count in text ("3 segments"); segments never rely on color swatches alone, each has a name.
- `state:applied`: chips are shown, an "N filters applied" count and a "Clear all" button exist; applying announces once ("Filters applied: 3. 1,204 rows"). Keyboard: Tab order is range, compare, segments, Apply; Enter in a field submits; Esc in a popover returns focus to its trigger. Never apply on focus.
- RTL: bar mirrors with logical properties; dates via `Intl.DateTimeFormat`. Mobile: collapses into a "Filters (3)" button opening a `drawer` with the same form; Apply is sticky.

### report-table
- Markup: native `<table>` with `<caption>` stating title, applied filters and as-of ("Revenue by region, Oct 1 – Oct 31 UTC"), `<th scope="col|row">`, `<tfoot>` for totals. Numeric columns end-aligned with `tabular-nums`; units in the header, not each cell. Composes `data-table` (sorting, sticky header, density); it is read-only and not a `grid` unless cells are editable.
- `variant:totals-row`: totals in `<tfoot>` with a row header "Total"; if rows are paginated the total says whether it covers all rows or this page ("Total, all 1,204 rows").
- `variant:drill-down`: the row header is a link to the detail report keeping filters ("Germany, view cities"), or an expandable row via a `<button aria-expanded aria-controls>` with child rows inserted after it. Level is stated in the accessible name, not only by indentation.
- `state:loading`: `aria-busy="true"` on the table wrapper, skeleton rows aria-hidden, one polite "Loading report" status; the caption and column headers stay.
- `state:no-data`: one row spanning columns inside the table body with the reason and a next action ("No orders from Oct 1 to Oct 7 for this segment. Widen the date range"). Cells with unknown values show "No data" (visually "—" with hidden text), never `0`.
- Sort changes announce once ("Sorted by revenue, descending") and use `aria-sort` on the header. Wide tables scroll in a focusable region labelled by the caption; first column sticky. Mobile: keep the table scrollable, never stack losing column headers. Reduced motion: no row transitions.

### export-menu
- Markup: a `menu-button` whose popover is `role="menu"` of `menuitem`s ("Export CSV", "Export XLSX", "Export PDF"); the trigger is "Export" with `aria-haspopup="menu"`. Items state what is exported: "CSV, 1,204 rows, current filters".
- `variant:csv-xlsx-pdf`: each format has one line of help in the item description (CSV raw values for analysis, XLSX with formatting, PDF as shown). Exports honor applied filters and say so; a "Include all rows" choice is a separate labelled option, not a hidden default.
- `state:preparing`: the trigger stays enabled elsewhere but the chosen item is replaced by "Preparing CSV…" text with a `progress-bar` (indeterminate if unknown); long jobs continue in the background with an email or a notification, and the user may leave the page. Announce once, "Preparing export".
- `state:ready`: a "Download CSV (1.2 MB)" link plus the file name; announce "Export ready"; failure says why and offers Retry. Links expire: say when ("available for 24 hours").
- Keyboard: Enter/Space opens and focus goes to the first item; ↑/↓ move, Home/End jump, Esc closes and returns focus to the trigger, Tab closes. Never open on hover or focus. CSV exports use raw, locale-neutral values (ISO dates, dot decimals, no currency symbols) and the menu item says so.

### data-freshness
- Markup: `<p>` with an icon, a text status and `<time datetime>` ("Updated 5 minutes ago, Oct 17, 09:55 UTC"). Relative text updates on the shared interval from `formatters` and is never a live region; the absolute time and zone are always available in the DOM and on focus/hover via a `tooltip`.
- `state:fresh`: "Updated 5 minutes ago". `state:stale`: warning tone + "Stale" word + age and cause ("Last updated 3 days ago. Source sync failed") with a fix or contact action; consumers of exported data see the same text in the file header.
- `state:refreshing`: "Refreshing…" with a spinner (static icon under reduced motion), `aria-busy` on the refreshed region and one polite status on completion ("Data updated 09:58 UTC"). The refresh button is a real `button` that disables while running and says why.
- Place next to the report title, not hidden in a footer. A schedule is documented ("Updates hourly") so users know what "fresh" means. RTL: icon leads with logical order.

## 3. Meaning

### metric-definition
- Content: name, plain-language definition, formula (as text, with `<code>` or MathML when needed), data source, owner, refresh cadence, positive direction (higher-is-better, lower-is-better, neutral) and caveats. The definition is also the source of truth for delta tone (see rules).
- `variant:hover-card`: an info `button` with a name ("About metric: Churn rate") opening a non-modal `hover-card`/`popover`. Opens on click or Enter/Space, and on hover with a delay, never on focus alone (WCAG 3.2.1); dismissible with Esc and hoverable (WCAG 1.4.13); focus stays on the trigger unless the card contains a link, in which case Tab moves into it.
- `variant:glossary`: a `<dl>` of terms sorted A–Z with in-page search and anchors (`#churn-rate`), each `<dt id>`; report headers link to the term. The glossary is the canonical page and the hover card repeats the same text from one source.
- Failure: a missing definition shows "No definition yet" with an owner contact, never an empty card. Mobile: card becomes a `drawer` or inline `disclosure`. RTL: formulas stay LTR (`dir="ltr"` on `<code>`).

### scorecard
- Composes product `stat` (value, label, trend, optional `sparkline`) and adds one comparison. `<section aria-labelledby>` per tile or a `<ul>` of tiles; the label is the metric name (a link to its `report-page` when drill-down exists), the value is `Intl.NumberFormat` compact with the full value in hidden text.
- `variant:target`: shows target and attainment as text ("62% of the 80,000 target") with the native `<meter>` (min, max, value) or `progress-bar`, labelled and with the same figures in text. Met, near and behind states are words ("On track", "Behind"), not only tone.
- `variant:vs-previous`: delta against the previous period as arrow + signed number + words ("▲ +12% vs Sep 2026"); tone token chosen by the token mapping in rules (favorable = `metric.delta.up`, unfavorable = `metric.delta.down`, neutral = `flat`), arrow and sign from the actual change; a cost that rose shows ▲ +12% in `metric.delta.down`.
- `state:missed`: states the shortfall and by how much ("Missed target by 4,200, −5%") with an icon and warning/danger text; does not use red fill alone. If both a target and a previous period are shown, the target line comes first.
- Not a live region; refreshed values announce through the page's single status message. Mobile: tiles in a one- or two-column grid, order preserved. Reduced motion: no count-up.

## 4. Analysis views

### funnel-chart
- Composes `chart-container`. Steps ordered top to bottom (or left to right) with each step's name, count and percent of the first step in text beside the bar; the bar length is a second channel to the numbers (not the only one). Table alternative lists step, count, conversion from previous and from start.
- `variant:steps`: single series, one color (`dataviz.categorical.1`); bars end-aligned left, never a pyramid that distorts area.
- `variant:with-dropoff`: between steps a text row "−38%, 1,240 left" with a down arrow; drop-off tone is neutral (a funnel always drops) and reserves warning/danger for an abnormal drop defined by the metric.
- `state:loading`: skeleton bars with aria-hidden, one polite status; step names stay visible. Empty steps show "0" only when zero was measured, otherwise "No data".
- Keyboard: steps are focusable only if they drill down (link per step); otherwise static text. Tooltips follow `chart-tooltip` rules. Mobile: vertical bars full width with the numbers inline, never hidden behind hover.

### cohort-table
- Markup: native `<table>` with `<caption>` ("Weekly retention by signup cohort"), row headers = cohort (date + size), column headers = period offset ("Week 0, Week 1, …"). Every cell prints its value ("42%"); the shade comes from a sequential ramp (`dataviz.sequential.1…5`) and is redundant with the number. Text on each cell is pair-checked against its shade at 4.5:1 (choose dark or light text per step).
- `variant:retention`: the first column (Week 0) is 100% and may be de-emphasized; incomplete periods are empty cells with "Not yet" text and a hatched pattern, not zero. A legend states the ramp's low and high values in numbers, not just a gradient.
- `state:loading`: `aria-busy`, skeleton cells aria-hidden, header and row labels kept.
- Keyboard: a read-only table needs none; if cells drill down, each cell value is a link and the table is not a `grid`. Large tables scroll in a labelled focusable region with sticky first column. Show the unit ("% of cohort") in the caption; support a toggle between percent and absolute counts. Forced colors: pattern fills replace shades; the numbers remain.

### pivot-table
- Markup: `<table>` with grouped `<th scope="colgroup|rowgroup|col|row">`, `<caption>`, subtotals and a grand total in rows/columns with their own headers. Use ARIA APG grid (`role="grid"`, roving tabindex, arrow keys, Home/End, Ctrl+Home/End, PageUp/PageDown) only when cells are interactive (drill, editing, selection); a read-only pivot stays a static table and keeps normal browsing semantics.
- `variant:row-col-groups`: row groups collapse with `button aria-expanded` and column groups span with `colspan` and `scope="colgroup"`; the group name is part of each cell's header association. Totals labelled "Subtotal: Europe" and "Grand total". Number columns end-aligned, `tabular-nums`, locale format; null shows "—" with hidden "No data".
- `state:empty`: explains that no dimensions or no rows are chosen and offers "Add a row field" (links to `report-builder`). Row, column and value fields are changed in the builder form, not by drag only; a drag path needs a non-drag alternative as in `sortable-list` (WCAG 2.5.7).
- Announce changes of grouping once ("Grouped by region, then country. 24 rows"). Sticky row and column headers for scroll. Mobile: horizontal scroll with sticky row headers; never collapse to cards that lose the second dimension. RTL: logical alignment; totals column on the inline-end.

## 5. Authoring & monitoring

### report-builder
- Markup: `<form>` of `<fieldset>`s: Metrics, Dimensions, Filters, Chart type, plus a live preview region (`chart-container` + table alternative). Multi-pick through `combobox` or `checkbox` groups; ordering of selected fields via `sortable-list` (`ul` with move buttons), not `listbox`.
- `state:empty`: nothing selected; the preview explains what to pick first ("Choose at least one metric") with a button, and the preview is not an empty chart frame.
- `state:configured`: summary sentence of the report ("Revenue and orders by region, Oct 1 – Oct 31 UTC, 2 filters"); save, schedule (`scheduled-report`) and export (`export-menu`) actions enabled. Preview updates after Apply or a short debounce and announces once; invalid combinations (a metric with an incompatible dimension) are prevented with a text explanation, not silently dropped.
- `variant:chart-type`: a `radiogroup` (`segmented-control`) of Table, Line, Bar, Funnel, Cohort, each with an icon and text label; only compatible types are enabled, disabled ones say why. Switching type keeps selections.
- Keyboard: standard form order; arrow keys in the radiogroup; no field is drag-only. Unsaved changes are protected by a leave warning. Mobile: preview below the form with a sticky "Update preview" button.

### scheduled-report
- Markup: `<form>` with frequency (`radiogroup`: Daily, Weekly, Monthly), time (`time-picker`), **time zone `select` always visible and defaulted to the viewer's with its name spelled out**, recipients (`tag-input` with email validation), format (CSV, XLSX, PDF) and a message. The sentence at the end restates it ("Every Monday at 08:00 Europe/Berlin to 3 people as PDF").
- `variant:schedule-form`: validation on blur with text; DST edge cases explained ("Runs at 02:30 may be skipped on March 29; it runs at 03:00 that day"); a "Send test" button states who receives it.
- `state:active`: a `switch` "Schedule enabled" (constant visible label + role=switch) beside the next run as `<time>` with zone and last run result ("Last sent Oct 10, 08:00 UTC, delivered to 3").
- `state:paused`: switch off, status text "Paused" (never tone alone), next run "—" with the reason (paused by you, or by failed delivery) and "Resume" via the same switch. Delivery failures are listed with cause and a retry.
- Announce save and toggle results once; recipients are validated and removable with a text "Remove ana@example.com" button; external recipients are flagged in text where policy requires it. Mobile: stacked fields, sticky Save.

### chart-annotation
- Markup: markers on the time axis are `<button>`s (focusable, in time order, roving tabindex if many) with a name ("Annotation Oct 8: Pricing change"), a shape marker (not color only), and a `popover` showing date, author and text. Every annotation also appears in the chart's table alternative as a column or a following list, so the information is not pointer-only.
- `variant:event-marker`: vertical line or flag with a short label, at most one visible label per cluster ("3 events" expands to a list); events keep stable shapes across charts on the page. Tooltips follow `chart-tooltip` rules (Esc dismiss, hoverable).
- `state:editing`: "Add annotation" opens a labelled form (`modal` or inline: date, text up to a limit, visibility); editing and delete are in the popover ("Edit annotation", "Delete annotation" with confirmation naming the date). Keyboard: Enter opens a marker, Esc closes and returns focus to it; moving a marker uses a date field, not drag only (WCAG 2.5.7).
- Announce create, update and delete once ("Annotation added on Oct 8"). Permissions: read-only viewers see annotations but no edit controls. Mobile: markers open a `drawer` with the list.

### alert-rule
- Markup: `<form>` stating the rule in a sentence ("Alert when Error rate is above 2% for 15 minutes"): metric (`select`), condition (`select`: above, below, changes by), threshold (`input` with unit), window, evaluation frequency, recipients and channels (checkbox group), severity (`select`, with text labels), and `switch` "Rule enabled".
- `variant:threshold`: threshold and window are number fields with units and validation on blur; a preview mini chart (`chart-container` with the threshold as a labelled line, dashed, plus table alternative) shows where past data would have triggered. The threshold line is labelled in text, not only by color.
- `state:triggered`: a `badge` "Triggered" with an icon, the current value, the threshold, since when (`<time>` with zone) and the next action (Acknowledge, Mute for…, Open report). Announce a newly triggered rule once via the page's status region or `alert` if this page caused it; persistent triggers are not re-announced. Acknowledgement records who and when.
- Direction is not sentiment: "above" is the user's chosen condition and is never colored good or bad in the form. Muting states its end time. Delivery tests ("Send test alert") say who receives it. Mobile: stacked form with the summary sentence sticky above Save.

## 6. Pages

### analytics-overview
- Composition: app shell → `<h1>` (dashboard name) with `data-freshness` → `analytics-filter-bar` → a `<ul>` of `scorecard` tiles (KPI row) → two to four `chart-container` cards, each with its title, table alternative and an "Open report" link → optional `report-table` of top items. Filters apply to every card and the applied-filters sentence leads the page.
- `variant:kpi-row-charts`: the KPI row (4–6 tiles with sparklines and deltas) sits above a grid of charts; chart order is by importance, not by data size, and every card has a heading in the page outline.
- `state:loading`: `skeleton` tiles and chart frames keep layout; filter bar and headings are real; one polite "Loading dashboard" status then "Dashboard updated". Cards load independently and a failed card shows its own error with Retry without blocking others.
- Mobile: filter bar collapses to a "Filters (n)" `drawer`; scorecards in a two-column grid, charts stacked full width, tables scroll horizontally; deltas keep their text.

### report-page
- Composition: app shell → breadcrumb → `<h1>` report name → `data-freshness` · `export-menu` · share/schedule actions → `analytics-filter-bar` → primary `chart-container` → `report-table` of the same data with totals; `metric-definition` links in the column headers and chart title.
- `variant:chart-table`: the chart and table share filters and the table is the accessible source of truth for the chart; the table is visible by default for analysts and collapsible under the chart for casual viewers, never absent.
- `variant:shared-readonly`: a banner states "Shared by Ana, view only, filters fixed to Oct 1 – Oct 31 UTC"; the filter bar becomes plain text, edit/schedule controls are removed (not disabled), export obeys the sharer's permissions and the link's expiry is stated.
- Mobile: chart first, then the table in a scroll region; actions in an overflow `menu-button`; the report title and freshness stay at top.

### reports-library
- Composition: app shell → `<h1>` Reports → "New report" button-primary → search and filters (owner, type, scheduled) → a `<ul>` or table of reports: name (link), owner, last run (`<time>` with zone), schedule state text, and a row `overflow-menu` (Open, Duplicate, Schedule, Delete with confirmation).
- `variant:list`: sortable by name and last run with `aria-sort`; the result count announces once after search ("12 reports"). Scheduled reports show "Scheduled: Weekly" text and "Paused" where applicable.
- `state:empty`: `empty-state` ("No reports yet. Create your first report") with a primary "New report" and a link to templates; a search with no matches says so and offers clearing filters, which differs from the true-empty state.
- Mobile: rows become cards with name, owner and last run; the overflow menu stays reachable at target size.

### report-builder-page
- Composition: app shell → `<h1>` "New report" or the report name → `report-builder` (form on the inline-start, live preview on the inline-end) → action bar: Save, Schedule (`scheduled-report` in a `modal`/`drawer`), Export (`export-menu`), Cancel. `data-freshness` sits above the preview.
- `variant:default`: preview shows the chart and its table alternative; unsaved changes are flagged in text and protected on navigation. Saving announces once ("Report saved") and moves focus to the heading or the success message without losing the form's position.
- Failure: a preview error is shown inside the preview with cause and Retry; the form stays editable. Permissions: users without edit rights get the read-only `report-page` instead.
- Mobile: single column, form then preview, sticky action bar (Save plus an overflow for the rest).
