# Calendar components & pages — specs

Scope `calendar` (enable with `ds.py init --scopes product,calendar` or add `"calendar"` to `ds.config.json → scopes` and run `ds.py init <dir> --force` to copy scope tokens). Components live in `components/<file>.html` (category **Calendar**); full pages in `patterns/<file>.html` (category **Calendar Pages**). Calendar components compose product components (`date-field`, `time-picker`, `calendar`, `combobox`, `modal`, `popover`, `badge`, `button-primary`, `segmented-control`) — wrap them, never re-style them. Component ids are `calendar-month`, `calendar-week` and so on; they do not collide with the product component `calendar` (a date picker whose file is `date-picker`).

## Contents
1. Rules for every calendar surface
2. Views: calendar-month, calendar-week, calendar-day, calendar-agenda
3. Events: event-chip, event-editor
4. Scheduling: time-slot-picker, recurrence-picker, availability-editor, timezone-select
5. Resources: resource-scheduler
6. Pages: calendar-page, booking-page, availability-page, event-detail-page

## 1. Rules for every calendar surface
Sources: ARIA APG (grid and date picker patterns), RFC 5545 (iCalendar RRULE), ECMA-402 `Intl.DateTimeFormat` with IANA time zones, WCAG 2.2 (1.4.1, 2.1.1, 2.5.7, 2.5.8, 3.3.x).

- **Month and time views are a grid; the agenda is a list** (ARIA APG grid). A month is `role="grid"` on a `table` with `role="row"`/`gridcell` and one roving tab stop (`tabindex="0"` on the focused day, `-1` on the rest). Day-cell keys follow the APG date-grid model: Left/Right previous/next day, Up/Down previous/next week, Home/End first/last day of the week, PageUp/PageDown previous/next month, Shift+PageUp/Shift+PageDown previous/next year. Focus wraps across month boundaries by re-rendering the grid, then restoring focus to the same day number.
- **Events inside a cell never create nested tab stops.** A day cell is the only grid tab stop. Enter or Space on any day cell selects that day (`aria-selected`) and updates the side panel, whether or not it has events. To reach the events, press F2, or press Enter on a day that is already selected and has events (Down Arrow is not used: the APG date grid reserves it for next week). Focus then moves into that day's events, a `ul` of `event-chip` buttons with their own Tab/Up/Down order; Escape returns focus to the day cell. Pointer users click a chip or the day directly. The cell's accessible name states the count and the key ("Tuesday 14 October, 3 events, selected. Press Enter or F2 for events"), and an announcement of the count follows each selection.
- **Dates and times use `Intl.DateTimeFormat`, never string concatenation.** Format with the user's locale, an explicit `timeZone` (an IANA name such as `America/Mexico_City`, never a fixed offset or "EST"), and `hour12`/`hourCycle` from the locale. Machine values are `<time datetime="2026-10-17T14:00:00-06:00">`. First day of the week and weekend days come from `Intl.Locale.prototype.getWeekInfo()` (or `weekInfo` in older engines), with a documented fallback and a user setting.
- **Store UTC instants plus the event's zone.** A timed event is an instant and a zone name; a recurring series is a local wall time plus a zone, expanded per occurrence so daylight-saving shifts keep "9:00 every Monday" at 9:00. All-day events are a date, not an instant, and never shift when the viewer changes zones.
- **The zone in use is always stated.** Any surface that shows times for another audience (booking, availability, invitations) shows the zone name next to the time ("2:00 PM Mexico City time (GMT-6)") using `timeZoneName: "short"` or `"long"`, and offers `timezone-select`.
- **Color is never the only signal** (WCAG 1.4.1). An event's category appears as its color plus the category name as text (in the chip, or in the chip's accessible name and a legend). Status (tentative, declined, cancelled) is text plus an icon plus a non-color style (dashed border, strikethrough), never opacity alone.
- **All-day and timed are distinct everywhere.** All-day events sit in their own row or a "All day" label; timed events show start–end and duration. Spoken form: "Design review, 2:00 PM to 3:30 PM" versus "Conference, all day, 14 to 16 October".
- **Every drag has a non-drag alternative** (WCAG 2.5.7). Moving or resizing an event by dragging is always also possible via a "Move…" action (a `modal` dialog with `date-field` and `time-picker`) or keyboard commands. Pointer dragging is an enhancement, never the only path.
- **Today and the current time are marked in text too.** Today's cell has `aria-current="date"` and a visible marker; the now line has a visually-hidden "Now, 2:47 PM". Selected cells use `aria-selected="true"` plus a non-color indicator.
- **Announce view changes politely.** One `role="status"` region announces "October 2026", "Week of 12 October 2026" and "3 events" after navigation. Never `aria-live` on the grid itself.
- **Respect motion and density.** View transitions and the now-line animation are removed under `prefers-reduced-motion`; the now line updates once a minute. Time-grid hour height is a token; touch targets are at least 24 px (WCAG 2.5.8) and chips in dense views expose a larger tap area or open the day.
- **Conflicts are warnings, not blocks.** Overlap and working-hours conflicts are shown with text and a one-click "View conflicting event"; save stays available unless the product forbids double booking.
- **Tokens**: composes product tokens only. Event categories use `dataviz.categorical.1` to `dataviz.categorical.8` (the color-blind-safe Okabe-Ito set) as an accent, a left bar and a swatch, always beside the category name; the chip text uses `color.text.default` on `color.bg.surface`, so contrast never depends on the category color. Today and selection use `color.action.primary.bg`; conflict and invalid use `color.feedback.warning.*` and `color.feedback.danger.*`. The category name or abbreviation text carries the meaning, so swatch contrast (3:1 as a UI graphic) is required only where the swatch is the sole non-text cue; the default `#e69f00`/`#56b4e9` fail 3:1 on white, so choose darker categorical values for those cases. No new token template.
- **vs.** `calendar` (product, file `date-picker`) selects a date inside a field and has no events; `calendar-month` lays out events and is the page-level view. `date-field` and `time-picker` are the inputs inside `event-editor`; `timeline` and `data-table` show dated records without calendar semantics. `calendar-agenda` is the recommended small-screen and screen-reader-first view.

## 2. Views

### calendar-month
- Markup: `<table role="grid" aria-labelledby="month-title">` with a `<caption>`-equivalent `<h2 id="month-title">October 2026</h2>`, `thead` of `<th abbr="Monday" scope="col">Mon</th>`, and 5–6 week rows of `td role="gridcell"` containing a day button-like `<time datetime>` number and an events `ul`. Previous/next/today are `button`s above the grid (names "Previous month", "Next month", "Today").
- Keyboard: exactly the APG date-grid keys in §1 (arrows, Home/End, PageUp/PageDown, Shift+PageUp/PageDown); Enter or Space on any day selects it and updates the selected-day panel (selection always happens first; when quick-create is enabled, a second Enter or Space on the already-selected empty day, or F2, opens `event-editor` `variant:quick`); F2, or Enter on an already-selected day with events, moves focus into its event list; Escape returns to the day cell. A `role="status"` says "14 October selected, 3 events". Tab leaves the grid.
- `state:today`: the current date has `aria-current="date"`, a filled number badge and the hidden text "Today". It stays distinguishable in forced-colors via an outline.
- `state:selected-day`: `aria-selected="true"`, a border plus a check or bold number, and the day's events shown in a side panel or the agenda below.
- `variant:overflow-more`: show up to 3 chips (fewer in narrow cells); extra events collapse into a "+3 more" button whose name is "Show 3 more events on 14 October". It opens a `popover`/`modal` listing the day's events (focus moves into the list, Escape closes and returns focus to the button). Days outside the current month are visibly muted and labelled with their month.
- Reduced motion: month changes swap without sliding. RTL: the grid mirrors and Left/Right keys swap meaning with writing direction (Left = next day in RTL).

### calendar-week
- Markup: `table role="grid"`: header row of day names and dates (`th scope="col"`), an "All day" row, and 30- or 60-minute rows as `th scope="row"` with `<time>` hour labels (visible every hour, one row per slot). Events are absolutely positioned `event-chip` buttons inside the day column; they appear in DOM order by start time so reading order matches.
- Keyboard: the grid's tab stop is a slot cell. Arrows move by slot (Up/Down) and day (Left/Right); PageUp/PageDown move a week; Home/End the first/last day of the week; Enter or Space selects the slot (always, with or without events). F2, or Enter on an already-selected slot with events, enters its event list (same model as `calendar-month`); Escape returns to the slot. On an empty slot, Enter or Space selects it and a second Enter (or Space) on the already-selected empty slot opens `event-editor` `variant:quick` with that time prefilled; F2 also opens it. An event chip focused in the list: Enter opens it, Shift+F10/context menu offers "Move…" and "Delete".
- `variant:time-grid`: the default 24-hour (or working-hours) grid with scrolling that lands on the working day start; sticky day headers; hours use `Intl.DateTimeFormat` with the locale's cycle.
- `state:now-line`: a 2 px line across today's column at the current time, with a dot and a visually-hidden "Now, 2:47 PM". Position updates every minute; no animation.
- `variant:overlapping`: overlapping events sit side by side in equal-width lanes (up to 4, then a "+N" chip); each lane keeps full text (title truncates with a title attribute and full accessible name). Lane order is stable and follows start time, then duration.
- Mobile: show 3 days, or switch to `calendar-day`; horizontal swipe is optional and has Previous/Next buttons.

### calendar-day
- Markup: the `calendar-week` grid with a single day column; a day header with the date and an "All day" strip.
- `variant:time-grid`: same slot and keyboard model as `calendar-week`, with wider chips that show time, title, location and category name.
- `variant:resources`: one column per resource (person, room), headers are `th scope="col"` with the resource name; keys: Left/Right move between resource columns, Up/Down between slots. Compose with `resource-scheduler` when the data is rooms or people across many days. Filter or pick resources with `combobox` (multi-select) and persist the selection.
- A day with no events shows "No events" in the grid's top row for screen readers, not only blank space.

### calendar-agenda
- Markup: a `ul`/`ol` of day groups; each day is `<h3><time datetime="2026-10-14">Tuesday 14 October</time></h3>` followed by a `ul` of rows. A row: time range (or "All day"), `event-chip` button with title, location, category name. It needs no grid keys: standard Tab order through the event buttons; groups are skipped by headings (heading navigation).
- `variant:grouped-by-day`: sticky day headings, "Today" label on today's group, past days collapsed under "Earlier" with a toggle button (`aria-expanded`). Range changes with "Load earlier" / "Load later" buttons (not infinite scroll without a button).
- `state:empty`: "No events in this period" with a primary "Create event" button and a link to change the range; hidden days with no events are simply omitted.
- Also the recommended view on small screens and the target of "Skip to agenda" links from the grid views. RTL: logical alignment only.

## 3. Events

### event-chip
- Markup: `<button type="button" class="event-chip" data-category="3">` containing a category swatch (`dataviz.categorical.N`, 3:1 against the surface), `<time>` start time, the title, and the category name as visible text (full text in lists and the agenda). In dense month cells the name collapses to a visible non-color cue inside the chip: the category's 1-3 letter abbreviation ("PRD" for Product) or a distinct shape or pattern per category (circle, square, triangle, diamond and so on, matching the swatch), documented in the legend beside the full names; the legend never carries the only cue. The full name stays in the accessible name and in the detail popover. Accessible name: "Design review, 2:00 PM to 3:30 PM, Product category, tentative".
- `state:default`: solid left bar plus tinted background; focus ring 3:1; hover shows a tooltip-free expansion only via the detail popover.
- `state:tentative`: dashed border, a "Tentative" text label (or "?" icon with visually-hidden text), name includes "tentative".
- `state:declined`: strikethrough title, icon plus text "Declined"; stays focusable and readable (contrast 4.5:1 maintained; never fade the text below that).
- `state:cancelled`: strikethrough title, "Cancelled" label, and the slot is released in availability; shown in agenda and detail but may be hidden in dense grids via a filter that states how many are hidden.
- `variant:all-day`: full-width bar spanning days, "All day" label instead of a time, continuing arrows when it crosses the visible edge ("Continues from 12 October" in the name). Multi-day events show the date range text.
- Time formatting: `Intl.DateTimeFormat(locale, { hour: "numeric", minute: "2-digit", timeZone })` with the event's zone, stating the zone in the name when it differs from the viewer's ("2:00 PM Berlin time"). Enter or click opens the event detail `popover` (a `dialog` for full details on touch); the chip never nests other interactive controls.
- RTL: bar and arrows flip logically. Forced-colors: swatch becomes a border with the category text.

### event-editor
- Markup: `<dialog>` (or inline panel) with a `form`: title (`input`, required), `date-field` start/end, `time-picker` start/end (hidden by an "All day" checkbox), `timezone-select` (collapsed behind "Time zone" link unless it differs), `recurrence-picker`, location, attendees (`combobox`, multi-value tokens), category (a `select` or radio group showing swatch plus name), description. Primary "Save", secondary "Cancel", destructive "Delete" with confirmation.
- `variant:quick`: a small `popover`/dialog with title, date, time and "More options" link that opens `variant:full`, carrying values. Focus starts on the title; Escape closes without saving only if clean, else asks to discard.
- `variant:full`: all fields; end time defaults to start + 30 or 60 min and stays at the same duration when the start changes; end before start is invalid. Editing a recurring event first asks "This event / This and following / All events" (radio group) before saving.
- `state:conflict`: a `role="status"` warning above the actions: "This overlaps Team sync, 2:30 PM to 3:00 PM" with a link "View conflicting event"; Save stays enabled, label "Save anyway" when the product blocks double booking only softly.
- `state:invalid`: inline messages on blur, summary via `error-summary` on submit ("End time must be after start time"); `aria-invalid` and `aria-describedby`; focus moves to the summary.
- Dates and times are entered with native-first `date-field` / `time-picker`; the editor shows the zone and the resolved local time of the other zone when different. Destructive actions are never the default focus.

## 4. Scheduling

### time-slot-picker
- Markup: `<fieldset>` with `<legend>Select a time on Tuesday 14 October</legend>`, slots as `input[type=radio]` styled as buttons with `<label><time datetime>9:00 AM</time></label>`; "Previous day" and "Next day" plain buttons and a `date-field` or mini month (product `calendar`) to jump. Selected slot: `:checked` plus check icon.
- `variant:by-day`: slots for one day at a time; a week strip of day buttons shows availability counts as text ("14 Oct, 6 slots"); days without slots are `aria-disabled` links to the next available day ("Next available: Thursday 16 October").
- `state:no-slots`: "No times available on this day" with a button "See next available" and an "Email me when a slot opens" option; never an empty list.
- `variant:timezone-switch`: "Times shown in Mexico City time (GMT-6)" with a "Change" button that opens `timezone-select`; switching re-renders slots with `Intl.DateTimeFormat(locale, { timeZone })` and announces "Times updated to Berlin time" via `role="status"`. The previously selected slot is kept by instant and re-labeled.
- Slot arrow keys follow native radio-group behavior (Up/Down or Left/Right move and select); Tab enters and leaves the group. Taken slots are removed, or kept disabled with "Unavailable" text when the layout would shift.
- Mobile: single column of full-width slots, 44 px tall.

### recurrence-picker
- Markup: a `select` of presets ("Does not repeat", "Every day", "Every week on Tuesday", "Every month on the 14th", "Every year on 14 October", "Every weekday (Mon–Fri)", "Custom…") whose labels are generated from the event date; choosing Custom reveals the builder inline.
- `variant:presets`: the preset list; the chosen value serializes to an RRULE (RFC 5545), for example `FREQ=WEEKLY;BYDAY=TU`.
- `variant:custom-rrule`: interval number input ("Repeat every [2] weeks"), unit `select` (day/week/month/year), weekday toggle buttons as a `fieldset` of checkboxes (names "Monday" and so on), month mode radio ("On day 14" / "On the second Tuesday"), end radio group (Never / On `date-field` / After N occurrences) mapping to `UNTIL`, `COUNT` and `INTERVAL`, `BYDAY`, `BYMONTHDAY`, `BYSETPOS`.
- A live plain-language summary (`role="status"`, "Repeats every 2 weeks on Tuesday and Thursday, until 20 Dec 2026") and the next three occurrences as a list. Invalid combinations (UNTIL before start, COUNT 0) get inline errors. `UNTIL` is in UTC when the event is timed; DST rules documented: the series stays at the local wall time in its zone.
- Occurrences beyond 730 are not expanded in the UI; the RRULE is the source of truth, and exceptions (`EXDATE`) are listed with "Skip this date" and Undo.

### availability-editor
- Markup: a `fieldset` per weekday: a checkbox "Monday" (available or not) and, when on, a list of time ranges, each with two `time-picker`s ("Monday range 1 start", "end"), a "Remove range" button, and an "Add range" button; "Copy times to…" opens a popover of weekday checkboxes. The time zone is stated at the top with `timezone-select`.
- `variant:weekly-hours`: defaults 9:00–17:00 Monday to Friday; overlap and end-before-start ranges show inline errors; unavailable days read "Unavailable" as text.
- `variant:date-overrides`: a list of specific dates ("Mon 27 Oct: Unavailable", "Fri 31 Oct: 10:00 AM–2:00 PM") with an "Add date override" button that opens a `modal` containing the product `calendar` to pick dates (multi-select) plus hours or "Mark unavailable"; each override has an Edit and a Delete button with Undo. Overrides take precedence over weekly hours; the summary says so.
- Save is explicit with a dirty indicator; a live `role="status"` confirms "Availability saved".

### timezone-select
- Markup: product `combobox` (editable, `aria-autocomplete="list"`, listbox of options "Mexico City (GMT-6)", "Berlin (GMT+1)") over the IANA list (`Intl.supportedValuesOf("timeZone")` where available, else a bundled list). Each option shows city, offset and current local time computed with `Intl.DateTimeFormat(locale, { timeZone, timeStyle: "short", timeZoneName: "short" })`. Options contain text only (listbox options have no interactive children).
- `variant:search`: type to filter by city, country or zone abbreviation ("CST", "Berlin"); a no-results message "No time zones match" in the combobox status; Escape closes the list.
- `variant:detected`: pre-selects `Intl.DateTimeFormat().resolvedOptions().timeZone`, labelled "Detected: Mexico City (GMT-6)" with a "Not right? Change" affordance; detection is a suggestion, never silently applied to someone else's availability.
- Display name uses the IANA id as value and a friendly label; the offset reflects the date being scheduled (DST-aware), not today's. Keyboard per APG combobox (Down opens, Up/Down move, Enter selects).

## 5. Resources

### resource-scheduler
- Markup: `table role="grid"`: rows are resources (`th scope="row"`: room or person with capacity or role text), columns are time spans (hours for a day, days for a week); bookings are `event-chip` buttons inside cells; the grid's one tab stop is a cell, keys as in `calendar-week` with Left/Right along time and Up/Down across resources; Enter or Space selects a cell; F2, or Enter on an already-selected cell with bookings, enters its bookings and Escape returns; on a selected free cell a second Enter or F2 opens the quick editor. Resource filters use `combobox`; the view range uses `segmented-control` (Day/Week).
- `variant:rooms`: rows are rooms with capacity ("Boardroom, 12 seats") and equipment text; free/busy shown with fill plus text ("Free"/"Busy" in the cell name); booking a free cell (select it, then a second Enter or F2) opens `event-editor` `variant:quick` for that room and time.
- `variant:people`: rows are people with their time zone shown ("Ana, Berlin"); working hours are shaded with a pattern (not color alone) and off-hours bookings get an "Outside working hours" label.
- `state:drag-reschedule`: pointer dragging a booking shows a ghost, snaps to a slot grid (15 minutes), highlights valid cells with a pattern and shows the new time text in a tooltip-free status; dropping into a conflict is rejected with a message. Non-drag alternatives (WCAG 2.5.7): every booking has "Move…" (`modal` with `date-field`, `time-picker`, and resource `select`), and the keyboard move mode: press M on a focused booking, move with arrow keys (a `role="status"` says "Moving: Boardroom, 3:00 PM"), Enter confirms, Escape cancels. Resize is likewise a keyboard mode or "Change end time" in the Move dialog.
- Moves are optimistic with an Undo toast and a polite announcement ("Moved Design review to Boardroom, 3:00 PM"); failures revert and say why. Touch: long-press starts a drag only after the item is selected; scrolling must still work (touch-action rules), and the Move dialog is always reachable.
- Reduced motion: no animated snapping. Large datasets virtualize rows with `aria-rowcount`/`aria-rowindex`.

## 6. Pages (patterns/)
Realistic data: a mixed calendar with several categories (each with a named legend), all-day and multi-day events, a recurring series, events in two time zones, light and dark.

### calendar-page
- Composition: header → `<main>` with `<h1>` "Calendar", toolbar (Today, Previous, Next, current range heading, a `segmented-control` view switcher for Month/Week/Day/Agenda, "Create" `button-primary`), a left rail with the product `calendar` mini-month and a category legend (checkbox filters, swatch plus name), then the active view and a polite `role="status"` for range changes.
- `variant:month`: `calendar-month` with the selected-day panel; `variant:week`: `calendar-week` with now line; `variant:day`: `calendar-day`; `variant:agenda`: `calendar-agenda`.
- `variant:mobile`: the rail collapses into a drawer, month view shows dots-plus-count per day (with the count in the name) and the selected day's agenda below; a floating "Create" button respects safe-area; the view switcher becomes a menu button.
- The view and date live in the URL (`?view=week&date=2026-10-12`); the zone is stated in the toolbar.

### booking-page
- Composition: `<main>` split: host summary (name, meeting title, duration, location, description) · the step. Public, no sign-in.
- `state:select-slot`: `time-slot-picker` with the date picker and `timezone-select`, "Next" enabled after a slot is chosen (or selecting a slot advances).
- `state:details`: the chosen slot summarized with a "Change" link, form (name, email, notes, optional guests) with inline validation and a primary "Confirm booking".
- `state:confirmed`: `<h1>` "You are booked", date and time with the zone, "Add to calendar" (an `.ics` download per RFC 5545 plus Google/Outlook links), "Reschedule" and "Cancel" links, and a confirmation email note. Focus moves to the heading.
- `state:no-availability`: "No times available right now" with the host's next availability date if known, an "Email me when a slot opens" form and a contact link.
- Mobile: single column; the summary collapses into a header line.

### availability-page
- Composition: header → `<main>` `<h1>` "Availability", `timezone-select`, `availability-editor` in `variant:weekly-hours` then `variant:date-overrides`, an upcoming-preview list, "Save changes".
- `variant:default`: shows both sections, a summary ("Available 20 h per week") and a link to the public booking page.
- Mobile: weekdays stack; add-range and override actions stay full-width buttons.

### event-detail-page
- Composition: header → `<main>` `<h1>` title, `event-chip` metadata line, date and time with the zone (and the viewer's local time when different), location (map link or join link), description, attendee list (`ul` with response text per person: Accepted, Declined, Tentative, Awaiting), series info from `recurrence-picker` summary.
- `variant:organizer`: Edit (`event-editor`), Delete (confirmation, with "this event / series" choice), "Add attendees", response counts and a "Send update" action.
- `variant:guest-rsvp`: a `fieldset` of "Accept", "Tentative", "Decline" radio buttons (with the current response preselected) and a note field; a `role="status"` confirms "Response saved"; "Propose new time" opens the slot picker.
- Mobile: actions become a sticky bottom bar; the attendee list is collapsed behind a "Show attendees (12)" button.

## Sources
- WAI-ARIA APG — Grid pattern: https://www.w3.org/WAI/ARIA/apg/patterns/grid/
- WAI-ARIA APG — Date picker dialog example (date grid keys): https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/examples/datepicker-dialog/
- WAI-ARIA APG — Combobox, Radio group: https://www.w3.org/WAI/ARIA/apg/patterns/
- RFC 5545 — iCalendar (RRULE, EXDATE, VEVENT): https://www.rfc-editor.org/rfc/rfc5545
- MDN — Intl.DateTimeFormat: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat
- MDN — Intl.supportedValuesOf, Intl.Locale weekInfo: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl
- IANA Time Zone Database: https://www.iana.org/time-zones
- WCAG 2.2 — 2.5.7 Dragging Movements: https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html
- WCAG 2.2 — 1.4.1 Use of Color: https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html
