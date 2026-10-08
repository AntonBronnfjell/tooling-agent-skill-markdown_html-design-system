# Layout patterns (macro-components) — specs

Files in `patterns/`: `app-shell`, `form-layout`, `dashboard`, `empty-state`, `error-page`, `auth`, `settings`, `list-detail`, `detail-page`, `wizard`, `onboarding`.

## Contents
- app-shell
- form-layout
- dashboard
- empty-state
- error-page
- auth
- settings
- list-detail
- detail-page
- wizard (enterprise)
- onboarding (enterprise)
- feed (enterprise)
- Real-screen demos
- start-page
- question-page (one thing per page)
- check-answers
- confirmation-page
- task-list-page
- step-by-step-navigation
- service-unavailable
- session-timeout
- exit-page-quickly
- address-entry
- name-entry
- phone-entry
- payment-card-entry
- unsaved-changes
- create-resource (enterprise)
- delete-with-confirmation (enterprise)
- saved-filters (enterprise)


Patterns are **compositions of existing components only** — if a pattern needs new styling, that's a missing component or token; add it there, not in the pattern CSS. Pattern pages are full-page demos; each still has the five `data-doc` sections. Build them last; they're the integration test of the whole system.

## app-shell
- Landmarks: skip link → `<header>` (top-nav) → `<nav>` (side-nav / app-rail) → `<main id="main">` → optional `<aside>` → `<footer>`. CSS grid with named areas: `"header header" "nav main"`; side-nav collapses to drawer below lg; mobile variant uses bottom-nav or top menu. Main scrolls independently only if necessary (prefer document scroll — better for zoom and mobile). Demo all three variants.

## form-layout
- Single column by default (fastest to complete); two-column only for short related fields (city/postcode) on ≥ md. Sections with headings + descriptions (fieldset where grouping is semantic). Action bar: primary at inline-start for linear forms (or inline-end in dialogs — pick one, ADR it), sticky on long forms. Invalid state demo: error summary at top + inline errors. Label-above alignment.

## dashboard
- Page header (title, date range picker, actions) → KPI row (stat cards, auto-fit grid) → mixed tiles (charts, data table, lists) on a 12-col grid with spans; tiles are cards with title + menu; loading state shows skeletons per tile (no full-page spinner). Responsive: tiles reflow to single column.

## empty-state
- Illustration/icon (decorative), title stating the situation, one sentence of guidance, one primary action (+ optional secondary link). Variants: first use ("Create your first project"), no results ("No results for 'x'" + clear filters), cleared ("All caught up"). Used inside tables, lists, pages.

## error-page
- 404 (not found: search + home link), 403 (no access: request access / switch account), 500 (something went wrong: retry, status page link, error reference ID), offline. Keep header/nav so users can recover; plain language, no blame; correct `<title>`.

## auth
- Sign in, sign up, forgot/reset password: centered card on canvas, logo, H1, form with correct `autocomplete` (username, current-password, new-password, one-time-code), password reveal, error summary for failed sign-in (generic "Email or password is incorrect"), SSO buttons, links between flows. Never disable paste.

## settings
- Side-nav (or tabs) of sections + content column; each section a form card. Choose and document a save model: immediate (switches, with toast) vs explicit Save per section (with unsaved-changes guard). Danger zone section at bottom with destructive actions + alert dialog.

## list-detail
- Collection page: page header with primary create action, filter bar (search input, filter chips/selects, "Clear all", result count), list or data table, pagination, bulk actions on selection, faceted filters in a drawer on mobile. No-results state demo.

## detail-page
- Record view: page header (breadcrumbs, title, status badge, actions), tabs (Overview, Activity, Settings), description list of fields, related lists, timeline/activity, optional side panel with metadata.

## wizard (enterprise)
- Stepper + one step per page/panel, Back/Next/Cancel, per-step validation, review step summarizing answers with "Change" links, completion confirmation. Preserve entered data when navigating back.

## onboarding (enterprise)
- Welcome screen + setup checklist (progress, items linking to tasks, dismiss when done) and optional coachmarks for key UI. Skippable; resumable.

## feed (enterprise)
- APG feed pattern: container `role="feed" aria-busy` while loading, each item `<article aria-posinset aria-setsize="-1" aria-labelledby>` (post-card). Page Down/Up move between articles. Load more via a visible "Load more" button (infinite scroll may trigger it, but the button stays for keyboard users). "New posts" notice is a button at the top that inserts items and moves focus — never shift content under the reader. Empty and loading states.

## Real-screen demos
- Besides per-pattern demos, add at least one full screen per product surface (e.g. "Dashboard — populated", "Settings — dirty form") composed only from system components. They're the integration test that reveals missing tokens and spacing gaps; Storybook renders patterns full-screen.

Files added in `patterns/`: `start-page`, `question-page`, `check-answers`, `confirmation-page`, `task-list-page`, `step-by-step-navigation`, `service-unavailable`, `session-timeout`, `exit-page-quickly`, `address-entry`, `name-entry`, `phone-entry`, `payment-card-entry`, `unsaved-changes`, `create-resource`, `delete-with-confirmation`, `saved-filters`.

Transactional patterns below follow GOV.UK Design System research; they generalize well to any form-heavy product.

## start-page
- H1 = the task in verb form ("Apply for a parking permit"), short list of what you can do, what you'll need ("before you start" list), how long it takes, one primary "Start now" link styled as a start button (`<a class="btn btn--start" href>` — it navigates, so it stays a link). Sign-in variant offers "Continue a saved application". No form fields on this page.

## question-page (one thing per page)
- One question per page: for a single field the `<label>` **is** the `<h1>` (`<h1><label for>…</label></h1>`); for a group the `<legend>` wraps the `<h1>`. Hint text below. "Continue" submit, "Back" link above the content (not browser-only back).
- Errors: error summary + inline error + `Error:` prefix in `<title>`. Preserve answers when going back. Branching questions are fine — the check-answers page shows the final path.

## check-answers
- Summary list (`<dl>` rows: question `dt`, answer `dd`, action `dd` with "Change<span class="sr-only"> name</span>" link) grouped by section with `h2`s. Change links return to the question then back to check-answers (not through the whole flow).
- Declaration text (if legal) above the final "Accept and send" button. Incomplete state blocks submission and links to missing answers.

## confirmation-page
- `result-panel` (success) with H1 ("Application complete") and the reference number in large, copyable text; "What happens next" section; contact info; feedback link. Don't put the only copy of important info in a toast. Pending variant: "We've received your application" when processing is async.

## task-list-page
- H1, completion summary ("You have completed 3 of 7 sections"), `<ol>` of sections, each with task links and a status **as text** (`Completed`, `In progress`, `Not yet started`, `Cannot start yet`) styled as tags — status in the link's accessible name via `aria-describedby`. "Cannot start yet" tasks are not links. Submit available only when all complete (or route to check-answers).

## step-by-step-navigation
- For journeys spanning pages/services ("Learn to drive"): numbered `<ol>` of steps (with "and"/"or" connectors for parallel steps), each step a disclosure (`<details>` or button `aria-expanded`) listing links; "Show all steps" toggle. Current step/page highlighted with `aria-current` + text "You are here". Sidebar variant on content pages, full variant on the hub page. Distinct from `stepper` (single in-page process).

## service-unavailable
- Planned (with return date/time in `<time>`, saved data reassurance), unplanned (apologize, what to do instead, phone/alternative channel), closed permanently (where to go now). HTTP 503 with `Retry-After` for planned. Keep header/footer; no "try again" loop button pretending to work. Different from `error-page` 500 (unexpected failure for one request).

## session-timeout
- WCAG 2.2.1: warn at least 2 minutes before expiry with an `alertdialog` (`<dialog role="alertdialog">`, `showModal`): "You'll be signed out in 2 minutes", primary "Stay signed in" (extends session, returns focus to where the user was), secondary "Sign out". Countdown text updates visually every second but is announced **only** at coarse intervals (e.g. each minute) via the dialog's description, not a per-second live region.
- On expiry: navigate to a "You have been signed out" page explaining unsaved data status and a sign-in link back to the same place. Preserve in-progress form data server-side where possible.

## exit-page-quickly
- For sensitive services (domestic abuse): sticky button-styled **link** "Exit this page" (`href` to a neutral site, e.g. weather/search) at the top of every page; on activation, JS also replaces history (`location.replace`) and blanks the page immediately (overlay) before navigating; keyboard shortcut Shift pressed 3 times, explained in visually hidden + visible text.
- Interstitial pages explain the feature and that it doesn't clear browser history (link to guidance). Works without JS (plain link). Visual: high-emphasis but not an error color; doesn't cover content at 320px.

## address-entry
- Default multi-field: Address line 1, line 2 (optional), Town or city, County (optional), Postcode — with `autocomplete="address-line1|address-line2|address-level2|address-level1|postal-code"` and fixed widths (postcode `width-10ch`). Single `<fieldset>` + legend.
- Lookup variant: postcode → "Find address" → `<select>` of results (with count) + "I can't find the address in the list" → manual fields (always available). International: country `<select>` first (`autocomplete="country"`), then free-text lines + optional region/postal code — never require a postcode or state globally.

## name-entry
- Prefer one "Full name" field (`autocomplete="name"`, `spellcheck="false"`, width `width-20ch`); if you must split, use "Given names"/"Family name" (not first/last) with `given-name`/`family-name`. Accept any characters (apostrophes, hyphens, spaces, diacritics, non-Latin scripts), lengths up to ≥ 100; don't require a title; mononyms allowed.

## phone-entry
- `type="tel" autocomplete="tel"`, width `width-20ch`, accept spaces, brackets, dashes and `+`; normalize server-side (E.164). International: explain "include the country code" in hint text, or a separate country-code `<select>` only if the backend requires it. Never mask to a fixed national format. Say why you need it and whether you'll call or text.

## payment-card-entry
- Fields in one `fieldset`: Card number (`inputmode="numeric" autocomplete="cc-number"`, allow spaces, format in groups on blur, detect brand and show it as text + logo), Expiry (`cc-exp` single MM/YY field or month/year via date-field month-year), Security code (`cc-csc`, width `width-4ch`, hint where to find it), Name on card (`cc-name`). Luhn check on submit, not keystroke.
- Never disable paste or autofill; error messages specific ("Card number is too short"). In practice embed the PSP's hosted fields (Stripe, Adyen, GOV.UK Pay) for PCI scope — style them with the same tokens and ensure their iframes expose labels *(uncertain: hosted-field a11y varies by provider; test with a screen reader)*.

## unsaved-changes
- Track dirty state by comparing current `FormData` with the initial snapshot (not "any input event"). In-app navigation: intercept links/router (Navigation API `navigate` event — Baseline newly available 2026-01 — or the router guard) and show an `alertdialog`: "You have unsaved changes" — "Save and leave" / "Discard changes" / "Keep editing" (initial focus on Keep editing). Browser close/reload: `beforeunload` with `preventDefault()` only while dirty (custom text isn't shown by browsers). Remove the listener when clean — it disables bfcache.
- Optional dirty indicator ("Unsaved changes" text near Save). Prefer autosave drafts where feasible.

## create-resource (enterprise)
- Single-page: page header "Create project", form-layout sections, primary "Create project" (verb + noun) + Cancel (returns to the list, guarded by unsaved-changes). Multi-page: `wizard` with review step (check-answers), each step URL-addressable. Success: redirect to the new resource's detail page with a success toast/alert ("Project created") — not back to an empty form. Server errors keep data and show the error summary.
- Defaults pre-filled; optional fields collapsed under "Advanced settings" (disclosure).

## delete-with-confirmation (enterprise)
- Decide by reversibility: reversible → delete immediately + "Undo" toast (or soft-delete/trash); irreversible single item → `alertdialog` naming the item and consequence ("Delete 'Q3 report'? This can't be undone."), destructive button labelled with the action; irreversible **high-impact** (repos, workspaces, accounts) → type-to-confirm: a text field "Type <strong>acme-prod</strong> to confirm" enabling the destructive button only on exact match (case-sensitive, paste allowed), label associated, mismatch hint not an error until submit.
- Bulk deletes state the count ("Delete 12 files?"). After delete: move focus to a sensible place (next row, list heading) and announce via toast/status.

## saved-filters (enterprise)
- Collection pages with complex filters: a view switcher (`select` or menu button "View: My open tickets") listing default, personal and shared views; "Save view" opens a dialog (name, visibility: only me / team) saving filters + sort + columns + density. Modified state: "Unsaved changes" tag with "Save" / "Save as new" / "Reset".
- URL holds the active filter state (shareable, back button works); saved views are named pointers to that state. Manage views (rename, delete with confirm, set default). Empty state: no saved views explains how to create one.
