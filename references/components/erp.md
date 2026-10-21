# ERP components & pages — specs

Scope `erp` (enable with `ds init --scopes product,erp` or add `"erp"` to `ds.config.json → scopes`). Components live in `components/<file>.html` (category **ERP**); full pages in `patterns/<file>.html` (category **ERP Pages**). ERP components compose product components (`data-table`, `combobox`, `stepper`, `timeline`, `file-upload`, `saved-filters`, `modal`, `error-summary`, `button-primary`) — wrap them, never re-style them.

## Contents
1. Rules for every ERP surface
2. Record: record-header, status-workflow, approval-panel, audit-log
3. Lines and lookup: line-item-editor, master-data-lookup
4. Inventory and output: inventory-level, print-layout
5. Bulk operations: batch-edit, import-wizard
6. Pages: record-list-page, record-form-page, purchase-order-page, inventory-page, approvals-inbox, import-page

## 1. Rules for every ERP surface
Sources: SAP Fiori and Oracle Redwood object-page conventions (cited as precedent for the header-plus-sections record layout and action placement), ARIA APG grid pattern, CSS Paged Media (`@page`), WCAG 2.2 (1.4.1, 2.5.8, 3.3.1, 3.3.3, 3.3.4).

- **Object-page layout is the precedent.** A record shows a header (title, key facts, status, primary actions), then sections or tabs, then lines (SAP Fiori object page, Oracle Redwood record pages). There is one `button-primary`; the rest are secondary or in a menu.
- **Status is text plus icon, never color alone** (WCAG 1.4.1). "Approved" has a check icon and the word; color only reinforces.
- **Transitions are buttons named by the action** ("Submit for approval", "Approve", "Post to ledger"), not by the target status. Only transitions valid for the current status and the user's permission are shown; a missing one may be explained in text ("Approval requires the finance role").
- **Legal and financial submissions get a review step** (WCAG 3.3.4 Error Prevention): irreversible actions (posting, approving a payment, deleting, applying a batch) are reversible, checked, or confirmed. Confirmation uses `modal` with a summary of what will change and a button naming the action; Cancel is the initial focus.
- **Validate where it happens.** Cell and field errors are inline (`aria-invalid="true"` + `aria-describedby` to the message) after commit or blur; on save, an `error-summary` lists every problem with links to the cell or field (WCAG 3.3.1, 3.3.3). Messages say how to fix.
- **Money and quantities**: format with `Intl.NumberFormat(locale, {style:'currency', currency})`, never string concatenation; respect minor units (JPY 0, KWD 3). Numbers are end-aligned (`text-align: end`) with `font-variant-numeric: tabular-nums`. The unit of measure is in the column header or beside the number.
- **Keyboard first.** Back-office users enter data for hours: every action has a keyboard path, no hover-only controls, visible focus, tab order follows reading order. Shortcuts are documented and never override screen-reader or browser keys.
- **Protect unsaved work.** A dirty record shows "Unsaved changes" text, warns on navigation (`beforeunload` plus an in-app prompt via `modal`), and prev/next asks to save or discard first.
- **Locked and read-only are explained.** A locked record says who holds the lock and since when; controls become text or `readonly`, not just greyed out.
- **Concurrent edits**: save with a version; on conflict show what changed (as in `audit-log` `variant:field-changes`) and offer reload or overwrite, never silent last-write-wins.
- **Announce, don't spam.** Totals, row counts and progress go to one polite `role="status"` region after a commit or on a throttle, never per keystroke. A blocking error uses `role="alert"` once.
- **Dense by choice.** Density is a user setting (comfortable/compact) that changes spacing only; target size stays at least 24x24 CSS px (WCAG 2.5.8).
- **Print is a feature.** Documents have a dedicated print stylesheet (`print-layout`); no interactive chrome prints.
- **Tokens**: composes product tokens only (`color.text.default`, `color.text.muted`, `color.feedback.<tone>.{bg,fg,border,icon}`, `color.bg.surface`); no scope token template.
- **vs.**
  - `line-item-editor` vs `data-table`: use `data-table` to browse, sort and select read-mostly rows; use `line-item-editor` when cells are edited in place and the lines produce totals.
  - `status-workflow` vs `stepper`: `stepper` guides the user through steps they complete in one session; `status-workflow` is the persistent lifecycle state of a record, with permission-gated transitions that may span days and people.
  - `master-data-lookup` vs `combobox`: `combobox` picks from a short list of labels; `master-data-lookup` searches a large reference table (items, vendors, accounts) by code or name, shows several columns, and may offer create-new.

## 2. Record

### record-header
- Markup: `<header>` inside `<main>` with `<h1>` (record title, e.g. "Purchase order PO-10482"), a `<dl>` of key facts (vendor, total, date), the status text from `status-workflow`, and a group of buttons. Not a landmark of its own.
- `variant:status-actions`: status text plus icon beside the title; primary transition as `button-primary` named by action; other actions in an "Actions" menu button.
- `variant:prev-next`: "Previous record" and "Next record" buttons with position text "3 of 48" in a polite status. Arrow icons are `aria-hidden`; names are the full phrases. When dirty, asks to save or discard first.
- `state:locked`: lock icon plus text "Locked by Dana Ruiz since 14:05"; edit actions removed; "Request access" button if permitted.
- Mobile: title and status stack; secondary facts collapse into a "Details" disclosure; actions become the menu button plus one primary.
- RTL: logical properties; prev/next icons mirror. Long titles wrap; the record number is never truncated.

### status-workflow
- Markup: `<ol>` of statuses (text plus icon each) with `aria-current="step"` on the current one, followed by a group of transition `<button>`s. Differs from `stepper`: it shows lifecycle, not wizard progress.
- Demos: `state:draft` (action "Submit for approval"), `state:submitted` ("Awaiting approval from Finance"; actions "Approve", "Reject", "Recall"), `state:approved` ("Post to ledger"), `state:posted` (terminal; no forward action, "Reverse entry" if allowed), `state:rejected` (reason with who and when; "Revise and resubmit").
- Each status has a visible text name and a distinct icon shape (not just color); the current one is also exposed via `aria-current`.
- Irreversible transitions (posting): the button opens a `modal` review step (summary of totals, accounts and period) with a confirm button "Post to ledger" and Cancel (WCAG 3.3.4). After success, the status changes and a polite status message states the new status.
- Failures: a transition refused by the server shows `error-summary` with the reasons ("Line 3 has no cost center"); the status does not change.
- Reduced motion: no animated status transitions. RTL mirrors the order.

### approval-panel
- Markup: `<section aria-labelledby>` "Approval" with request summary, then a decision form: "Approve" and "Reject" buttons and a required comment `<textarea>` for rejection (inline error if empty).
- `state:pending` (waiting on you or on someone, stated in text), `state:approved` and `state:rejected` (decision, who, when, comment as text plus icon).
- `variant:chain`: ordered `<ol>` of approvers with each step's status text ("Step 2 of 3: Maria Gomez, pending"); history composes `timeline`.
- `variant:delegated`: text "Delegated to Sam Lee by Maria Gomez until 24 Oct"; the delegator stays visible in the audit trail.
- Approving a payment asks for confirmation as in `status-workflow`. The decision is announced once via `role="status"`.
- Mobile: buttons full width; comment field comes first for reject.

### audit-log
- Markup: `<table>` with `<caption>`, columns When (`<time datetime>`), Who, Action, Details; newest first with `aria-sort` stated. Dates show absolute time with timezone.
- `variant:field-changes`: Details is a `<dl>` of changed fields as "Quantity: 10 → 12" with visually hidden "from" and "to"; long values are truncated with a disclosure, never silently cut.
- `variant:filters`: filter by user, action, field and date range via `saved-filters` and form controls; result count in a polite status.
- `state:empty`: "No changes recorded for this record"; when filtered, a "Clear filters" button.
- Append-only: no edit or delete controls. System actions name the system ("Integration: SAP sync").
- Mobile: rows become cards with the same `<dl>` structure.

## 3. Lines and lookup

### line-item-editor
- Markup: ARIA APG **grid** on `<table role="grid">` with `<caption>`, column headers (`<th scope="col">`), `aria-rowcount`/`aria-colcount` if virtualized, and `aria-readonly` on read-only cells. Roving tabindex: exactly one cell (or its widget) has `tabindex="0"`. The grid is one Tab stop and Tab leaves the grid; Tab never walks cell to cell.
- Navigation mode keys: arrows move one cell; Home/End go to first/last cell in the row; Ctrl+Home / Ctrl+End to first/last cell of the grid; Page Up/Page Down move by a screenful. No wrap at edges.
- Edit mode: Enter or F2 starts editing the focused cell (the input takes focus, caret at end); typing a printable character replaces the value and starts editing (spreadsheet-like); Enter commits and moves down; Escape cancels, restores the previous value and returns to navigation mode on the same cell. Arrow keys inside an input move the caret, not cells. Tab while editing commits and leaves the grid.
- Demos: `state:default` (navigation mode, focus ring on the cell), `state:editing-cell` (cell holds a labelled `<input>` named like "Quantity, row 2"), `state:invalid-cell` (`aria-invalid="true"`, `aria-describedby` pointing to a message with icon plus text; validated on commit, never per keystroke), `variant:totals` (`<tfoot>` with subtotal, tax, grand total), `variant:add-row` ("Add line" button below the grid; the new row's first cell gets focus and a polite status says "Line 4 added").
- Per-cell errors say how to fix ("Quantity must be 1 or more"). On save, `error-summary` links jump to the cell, which scrolls into view and takes focus. The invalid cell keeps the entered value.
- Totals: recomputed on commit, formatted with `Intl.NumberFormat` currency, `tabular-nums`, end-aligned; announced once via a polite `role="status"` ("Total $1,240.00") after commit, not on each keystroke. No `aria-live` on the totals cells themselves.
- Row actions (remove, duplicate) are buttons with row-specific names ("Remove line 2: Widget"); removal offers Undo. Row selection uses checkboxes in the first column.
- Lookup cells embed `master-data-lookup`; choice cells use a native `select` or `combobox`. Pasting multi-row data from a spreadsheet fills cells and validates each.
- Reduced motion: no row add/remove animation. RTL: Left/Right arrows follow visual order. Mobile: grid scrolls horizontally with a sticky first column, or becomes one card per line with the same fields.
- Failure: save conflict or server error shows `role="alert"` once and keeps edits.

### master-data-lookup
- Markup: `<input role="combobox" aria-expanded aria-controls aria-autocomplete="list" aria-haspopup="grid" aria-activedescendant>` with a visible `<label>`. Because results have several columns (code, name, extra), the popup is `role="grid"` (APG combobox with grid popup), not a `listbox`, so columns are announced. The popup is a `[popover]` anchored to the input.
- Focus model: DOM focus always stays on the input, so typing keeps filtering. `aria-activedescendant` on the combobox points at the active gridcell (set to empty when none is active). Down opens the popup (activating the first row) or moves to the next row; Up moves to the previous row; Right and Left move between cells of the active row (RTL swaps them). Enter accepts the active row. Escape closes the popup and keeps the typed text (a second Escape clears it). Typing, Backspace, Home and End act on the input text.
- Tab with the popup open closes it. If a row is active, Tab accepts that row and moves on; if no row is active, the typed text is kept and validated on blur (the field is invalid until a record is picked). Shift+Tab behaves the same.
- `variant:code-name-columns`: rows show code and name (e.g. "10042 — Hex bolt M8"); the input shows "10042 Hex bolt M8" once selected; matched text is highlighted with `<mark>` and is never the only cue.
- `state:no-match`: the grid has no data rows; a polite status says "No match for 'xyz'" and, if allowed, the single row is the create-new row. Never an empty popup. Free text is not accepted silently; the field stays invalid until a record is picked.
- `variant:create-new`: "Create vendor 'Acme'" is the final grid row, one `gridcell` spanning the columns (`aria-colspan`), reachable with Down like any row and the active-descendant target; Enter creates (no nested button, since a button is not a valid grid child). It opens a `modal` with a short form; on success the new record is selected and a status announces it.
- The result count is announced politely ("5 results"). The popup never opens on focus alone (WCAG 3.2.1); filtering is debounced about 250 ms.
- A "Browse all" button sits outside the popup, beside the input, and opens an advanced search `modal` with filters for large tables.
- Loading: `aria-busy` on the popup with "Searching" text. Failure: a polite status "Could not load results" and a Retry button beside the input (not in the grid).

## 4. Inventory and output

### inventory-level
- Markup: quantity as `<data value>` with unit ("128 pcs"), status text plus icon, optional `<meter>` for stock against the reorder point (with the value in text beside it).
- `state:in-stock` ("In stock"), `state:low` ("Low: below reorder point of 50"; warning icon), `state:out` ("Out of stock"; error icon; backorder date if known).
- `variant:by-location`: `<table>` with `<caption>`: Location, On hand, Reserved, Available; totals row; locations with low stock are marked in text.
- Available is on hand minus reserved, shown explicitly; numbers `tabular-nums`, end-aligned. Updates after a stock movement are announced via polite status only when the user caused them.
- Mobile: locations become a `<dl>` list.

### print-layout
- Markup: `<article class="print-doc">` with document header (company, number, date), addresses, lines `<table>` with `<thead>` repeating on each page (`display: table-header-group`), totals, terms and footer.
- Stylesheet: `@page { size: A4; margin: 15mm 12mm; }` (Letter for US locales), named pages where needed; `@media print` hides all interactive chrome (`nav`, buttons, filters, toasts, `[data-no-print]`), resets backgrounds to white, uses black text, and expands external link URLs (`a[href^="http"]::after { content: " (" attr(href) ")"; }`).
- Page breaks: `break-inside: avoid` on rows, totals and signature blocks; `break-after: page` between documents; orphans/widows set. Page numbers use `@page { @bottom-center { content: "Page " counter(page) " of " counter(pages); } }` where supported, with a fallback footer.
- `variant:invoice`: invoice number, due date, tax breakdown, payment instructions, legal and tax IDs. `variant:purchase-order`: PO number, vendor and ship-to blocks, requested delivery, terms, approval signature area.
- The Print button on the record is a normal `button` calling `window.print()`; the screen preview uses the same CSS in a paper-sized frame.
- Money is formatted for the document locale and currency; font size at least 9 pt. Color is never the only signal, since printing may be monochrome.

## 5. Bulk operations

### batch-edit
- Markup: a `modal` (`dialog`) opened from the selection toolbar button "Edit 24 selected", with a field chooser, a new-value control, and a preview `<table>` of before/after per record (paged if large).
- `state:preview`: shows what will change and how many records are affected; the button "Apply to 24 records" names the action; records to be skipped are listed with reasons. This is the required review step (WCAG 3.3.4).
- `state:applying`: `<progress>` with text "Applying 12 of 24"; the dialog stays open, Cancel stops the remaining records; one polite status per about 10% or 5 s, not per record.
- `state:partial-failure`: summary "21 updated, 3 failed" as `role="alert"` once; a failures table with record, reason, a "Retry failed" button and a "Download failure report" link. Successful changes are not rolled back silently, and the text says so.
- Focus returns to the toolbar trigger on close. Mobile and RTL: full-screen dialog, logical properties.

### import-wizard
- Markup: steps as `stepper` (ordered list with `aria-current="step"`), each step with a heading; Back and Next buttons; `file-upload` for the source file with accepted types and size stated.
- `state:mapping`: `<table>` of source columns to target fields with a native `select` per row (label includes the source column name); auto-matches show "Matched by name"; required target fields without a source are listed.
- `state:validation-report`: counts (valid, warnings, errors) as text plus icons; errors table with row, column, message and fix hint; `error-summary` at top; downloadable error file. Blocking errors disable nothing silently: "Continue" is explained by text.
- `state:dry-run`: "Nothing has been saved yet." Shows what would be created, updated or skipped. The final button "Import 1,204 records" is the review step (WCAG 3.3.4).
- `state:imported`: result summary with created, updated and skipped counts, links to the imported list and the log; announced once via status.
- Long runs show `<progress>` and survive navigation (job id) with a link back. Failure: unreadable file or wrong encoding gets a specific message.

## 6. Pages

### record-list-page
- Composition: `<main>` with `<h1>` and primary "New record" button, `saved-filters` toolbar, `data-table` (sortable, selectable) with a record link in the first column, pagination, and a bulk-action toolbar when rows are selected.
- `variant:dense`: compact row height; target size still at least 24 px; the density toggle is a button with `aria-pressed` and a constant label "Compact rows".
- `variant:saved-views`: saved view selector (named filters and columns), "Save current view" and a text indicator "Modified" when it differs from the saved one.
- `state:empty`: explains why ("No purchase orders yet" or "No results for these filters") with "New record" or "Clear filters".
- Mobile: columns collapse to key fields in cards; filters open in a `modal` or drawer.

### record-form-page
- Composition: `<main>`, `record-header`, tabs (General, Lines, Attachments, History) where Lines hosts `line-item-editor` and History hosts `audit-log`; Save and Cancel in a sticky action bar; `error-summary` on a failed save.
- `variant:header-tabs-lines`: header facts, tabbed sections, lines grid with totals below it.
- `state:dirty`: "Unsaved changes" text in the action bar; leaving prompts via `modal`; on a failed save, focus moves to the `error-summary`.
- `state:readonly`: fields shown as text with labels (`<dl>`) rather than disabled inputs; the reason is shown ("Posted records cannot be edited"); "Edit" only if allowed.
- Mobile: tabs scroll horizontally or become accordions; the action bar sticks to the bottom.

### purchase-order-page
- Composition: `record-form-page` structure with vendor via `master-data-lookup`, lines via `line-item-editor` (`variant:totals`), `status-workflow` in the header, `approval-panel`, `audit-log`, and a Print action using `print-layout` `variant:purchase-order`.
- `variant:draft`: editable; action "Submit for approval"; validation summary before submit.
- `variant:approved`: lines read-only, status shows approved, actions "Send to vendor" and "Print"; the approval chain is shown.
- Mobile: lines render as cards; totals stay visible below.

### inventory-page
- Composition: `<main>` with `<h1>`, filters and a view switch.
- `variant:stock-list`: `data-table` of items with `inventory-level` status text, location filter, low-stock filter and export.
- `variant:item-detail`: `record-header`, `inventory-level` `variant:by-location`, movement history via `timeline`, and "Adjust stock" opening a `modal` with a required reason and a review step.
- Mobile: list becomes cards; detail sections stack.

### approvals-inbox
- Composition: `<main>`, `<h1>` "Approvals", filter tabs (Pending, Delegated, Decided), items as a `ul` each with summary, requester, amount, age, inline "Approve" and "Reject" buttons (names include the item, e.g. "Approve PO-10482") and a link to open the record.
- `state:with-items`: count in the heading and a polite status; after a decision the row is removed with an Undo status and focus moves to the next item.
- `state:empty`: "You're all caught up. No approvals waiting." with a link to decided items.
- Bulk approve requires a review step. Mobile: buttons stay visible, no swipe-only actions.

### import-page
- Composition: `<main>` with `<h1>` "Import purchase orders", intro with a template download link, and the `import-wizard` in its steps.
- `variant:default`: starts at upload; prior imports in a `data-table` below with status text and a link to each log.
- Mobile: wizard steps stack; the mapping table becomes a list of labelled selects.
