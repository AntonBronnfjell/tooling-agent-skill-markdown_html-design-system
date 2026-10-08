# Layout patterns (macro-components) — specs

Files in `patterns/`: `app-shell`, `form-layout`, `dashboard`, `empty-state`, `error-page`, `auth`, `settings`, `list-detail`, `detail-page`, `wizard`, `onboarding`.

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
