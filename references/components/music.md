# Music components & pages — specs

Scope `music` (enable with `ds.py init --scopes product,music`; it adds `playback` automatically). Components live in `components/<file>.html` (category **Music**); full pages in `patterns/<file>.html` (category **Music Pages**). Music components compose the `playback` controls by id (`play-toggle`, `seek-bar`, `volume-control`, `time-display`, `media-queue`, `mini-player`, `sleep-timer`, `cast-button`, `transcript-panel`, `captions-menu`) and product components (`button-primary`, `toggle-button`, `table`, `tabs`, `modal`, `popover`, `sortable-list`, `badge`, `avatar`, `skeleton`, `empty-state`, `search-input`) — wrap them, never re-style or respecify them.

## Contents
1. Rules for every music surface
2. Playback chrome: now-playing-bar, now-playing-view
3. Tracks: track-row, track-list, save-toggle
4. Browse: artwork-card, artist-header
5. Lyrics and editing: lyrics-view, playlist-editor
6. Audio settings: equalizer
7. Pages

## 1. Rules for every music surface
Sources are named as rules: Media Session API, ARIA APG `table` and `grid` patterns, WCAG 2.2.2, 1.4.1, 2.3.3, 2.5.8 and 4.1.3, `prefers-reduced-motion`.

- **Publish to the Media Session API.** On every track change set `navigator.mediaSession.metadata` (title, artist, album, `artwork` in several sizes) and handlers for `play`, `pause`, `previoustrack`, `nexttrack`, `seekto`; the UI controls and the OS controls call the same functions. Keep `playbackState` in sync and guard with `'mediaSession' in navigator`.
- **One player, one live region.** The persistent bar and the full view share state from `media.js`; the track change is announced once, politely ("Now playing: {title} by {artist}"), by the shared status region, never by each component.
- **A track list is a `table`** (ARIA APG table pattern): real `<table>`, `<th scope="col">` headers, `<th scope="row">` or a title cell per row. It becomes a `grid` only if cells hold several interactive widgets that need arrow-key navigation; otherwise Tab reaches each button. Never `listbox` (rows contain buttons).
- **Row action on Enter.** Enter or double-click on a focused row plays it; a visible play button in the first cell does the same for single-click and touch. Row actions (save, more menu) are separate buttons and never trigger the row action.
- **Explicit is text.** Explicit content is labelled with the word "Explicit" (a visible "E" glyph with `aria-label`/visually hidden text "Explicit"), never only an icon or color (WCAG 1.4.1). Unavailable tracks say "Unavailable" and are skipped by next/previous.
- **Playing is more than color.** The current track shows an animated or static equalizer icon, the text "Now playing" (visually hidden is acceptable in a table row) and `aria-current="true"`; the accent color only reinforces.
- **Synced lyrics move, so they are pausable** (WCAG 2.2.2): auto-scroll follows the playhead, stops when the user scrolls or presses "Stop following", and resumes only on request. Under `prefers-reduced-motion: reduce` the active line is highlighted without scrolling animation (WCAG 2.3.3).
- **Toggles are `aria-pressed` with a stable name.** Save, follow, shuffle and repeat keep their label ("Save {title}") and flip `aria-pressed`; the name never flips together with the state (double negation).
- **Artwork is decorative or labelled once.** In a card the image has `alt=""` when the title is adjacent text; the album art in the bar and view has `alt` only if it adds information. Provide a placeholder with initials/icon when art fails to load.
- **Targets and touch.** 44 px targets in bars and rows on touch (24 px minimum, WCAG 2.5.8); swipe gestures have button equivalents; the bar never covers the last row (bottom padding equals bar height).
- **Loading and failure.** Lists show `skeleton` rows with `aria-busy="true"` on the table and a polite "Loading tracks" status; a failed stream shows "Can't play this track" with Retry and skips after a limit. Offline shows downloaded items only, with text.
- **RTL and logical properties.** Controls keep media-standard order (previous, play, next) as in `playback`; text and progress fill follow the logical direction; track times stay LTR digits.
- **Tokens**: composes `color.media.*` from `playback` and product tokens only; no new tokens.
- **vs.** `artwork-card` is a media cover card with a play overlay for albums, playlists and artists; `card` is a generic container, and `video-card` is a thumbnail with duration for video. `save-toggle` is a specialised `toggle-button` (`aria-pressed`) with a save/unsave name and heart or plus icon; use `toggle-button` for other binary actions. `track-list` is a table of songs; `media-queue` (playback) is the reorderable upcoming list inside the player; `data-table` is generic tabular data.

## 2. Playback chrome

### now-playing-bar
- `<section aria-label="Now playing">` fixed to the bottom: artwork and title/artist (link to album and artist) on the start, `play-toggle` with previous/next and `seek-bar` in the center, `volume-control`, queue and lyrics toggle buttons (`aria-pressed`) and `cast-button` on the end. Composes playback components by id.
- `state:playing`: the toggle name is "Pause", title announced once politely on change. `state:paused`: name "Play". `state:empty`: "Nothing playing" with controls disabled (native `disabled`).
- `variant:mobile`: compact bar with art, title, play-toggle and a thin progress indicator; tapping the title area opens `now-playing-view`; it is the `mini-player` composition, with next as a secondary button.
- Keyboard: Tab order follows visual order; Space on the toggle; media.js shortcuts apply when focus is not in a field. The bar is reachable by a "Skip to player" link.
- Media Session handlers are registered here. Reduced motion: no marquee scrolling title; long titles truncate with the full text in the accessible name. RTL: layout mirrors.

### now-playing-view
- `<dialog>` (modal, full-screen) or a route with `<main>`; large artwork, title, artist, `seek-bar`, controls, `save-toggle`, and `<div role="tablist">` (`tabs` component) with panels "Now playing", "Lyrics" (`lyrics-view`) and "Queue" (`media-queue`).
- `variant:full-screen`: art left, tabs right on wide screens; Esc closes and returns focus to the opener. `variant:lyrics-tab` shows `lyrics-view` selected; `variant:queue-tab` shows `media-queue` with move buttons.
- `variant:mobile`: art on top, tabs as a bottom segmented tablist; swipe down to close has a visible Close button as alternative.
- Dynamic background from artwork is decorative and any text on it meets 4.5:1 via a scrim; with reduced motion the background does not animate.

## 3. Tracks

### track-row
- A `<tr>` inside `track-list` with cells: index or play button, title with artist, album (optional), duration (`<time>`), actions (`save-toggle`, "More actions" popover menu). Outside a table it renders as `<li>` with the same content.
- `state:default`: index shown, play button revealed on hover and focus. `state:playing`: equalizer icon replaces the index, `aria-current="true"`, text "Now playing" (visually hidden). `state:unavailable`: dimmed with "Unavailable" text, play button `aria-disabled`, skipped in queue.
- `variant:explicit`: "Explicit" label before the artist. `variant:with-album`: album link column (hidden on narrow screens, appended under the artist). `variant:compact`: single-line, 40 px rows with 44 px touch targets on coarse pointers.
- Enter on the row plays; Space is not bound on the row. The title is the row header. Failure: playback error replaces the duration with "Couldn't play" and Retry.

### track-list
- `<table>` with a visible or visually hidden `<caption>` and `<thead>` (#, Title, Album, Duration); optional sortable headers use `<button>` inside `th` with `aria-sort`. Composes `table` and `track-row`.
- `variant:album`: no artwork column, disc index; `variant:playlist`: adds album, date-added and a drag/move column; `variant:search`: compact rows with the artist and artwork thumbnail. `state:loading`: `aria-busy="true"`, skeleton rows, polite "Loading tracks" status.
- Keyboard: Tab to the first row's controls, Enter plays the focused row; if the grid pattern is used, arrows move between cells, Home/End and Ctrl+Home/End jump, and one tab stop enters the grid.
- Long lists virtualise with `aria-rowcount`/`aria-rowindex`. Empty list shows `empty-state`. RTL: columns mirror, durations align to the logical end.

### save-toggle
- A `<button aria-pressed>` (composes `toggle-button`) with heart or plus icon and an accessible name that does not change: "Save {title} to Your Library" (the pressed state carries saved/unsaved).
- `state:unsaved`: outline icon, `aria-pressed="false"`. `state:saved`: filled icon and check, `aria-pressed="true"`; the icon shape differs, not only the color (WCAG 1.4.1).
- Toggling is optimistic with a polite status "Saved to Your Library" / "Removed from Your Library" and an Undo in the toast; on failure it reverts with "Couldn't save". Reduced motion: no pop animation. Target 44 px on touch.

## 4. Browse

### artwork-card
- `<article>` with cover art (fixed aspect ratio), a title link (the card's primary link, stretched with a pseudo-element), subtitle text and a separate play `<button aria-label="Play {title}">` overlay. The overlay is in the tab order and visible on focus, not only on hover.
- `variant:album`: square art, subtitle "Year · Artist". `variant:playlist`: subtitle owner or description. `variant:artist-round`: circular art (`border-radius: 50%`) with "Artist" text label. `state:playing`: overlay shows Pause, an equalizer icon and the text "Playing".
- Keyboard: Tab reaches the link, then the play button; Enter activates each. Do not nest the button inside the link. Hover lift is disabled under reduced motion; art failure shows a placeholder. RTL: text aligns to the logical start.

### artist-header
- `<header>` with `<h1>` artist name, monthly listeners as text, a Play button (`button-primary`), a follow `toggle-button` and a "More" menu. Background image is decorative with a scrim for 4.5:1 text.
- `variant:hero`: large banner with the name over the image. `state:following`: the button reads "Following" with a check and `aria-pressed="true"` (stable name "Follow {artist}" in the accessible name). `variant:verified`: a badge with the text "Verified artist" (icon plus text, or an icon with an accessible name), never only a blue tick.
- Mobile: banner shrinks, actions wrap below the name.

## 5. Lyrics and editing

### lyrics-view
- `<section aria-label="Lyrics">` with lines as `<p>` (or `<ol>` of `<li>` for synced); the active line has `aria-current="true"` and a visual emphasis plus larger weight, not only color. A "Stop following" / "Follow lyrics" button (`aria-pressed`) controls auto-scroll.
- `variant:synced`: lines carry start times; clicking a line seeks (it is a `<button>` styled as text). Auto-scroll pauses when the user scrolls manually or tabs into the lyrics (WCAG 2.2.2). `variant:static`: plain text, no seeking, no scrolling.
- `state:unavailable`: "Lyrics aren't available for this song" with a link to provide feedback. `state:reduced-motion`: the active line changes by highlight without smooth scrolling, scrolling by line jumps only on request.
- Active line changes are not announced (the song is the live content); the `transcript-panel` is the accessible equivalent for speech. Source credit ("Lyrics by {provider}") is text. RTL: `dir="auto"` per line.

### playlist-editor
- A `<form>` in a `modal` (composing `modal` and `fieldset`) or inline page: name input, description textarea, cover image control (file input with Change and Remove buttons), a track list as `ul` using `sortable-list` with move up/down buttons, and Save/Cancel.
- `state:editing`: fields editable, Save enabled when dirty, unsaved-changes confirmation on Cancel. `variant:reorder`: `sortable-list` with drag handles plus "Move up" / "Move down" buttons, polite announcement "{title} moved to position 3 of 12"; not a `listbox`. `variant:cover-description`: cover upload with alt guidance, description with a visible counter ("120 of 300").
- Remove track uses confirm or Undo. Validation: name required, error text linked by `aria-describedby`. Failure on save keeps the form open with an error summary.

## 6. Audio settings

### equalizer
- `<fieldset><legend>Equalizer</legend>` with an on/off switch, a preset `<select>` and a row of band sliders (`input[type=range]`, vertical via CSS `writing-mode`/`direction`, not rotated transforms), each with `aria-label="60 Hz"` and `aria-valuetext="+3 dB"`.
- `variant:presets`: the select lists Flat, Bass boost, Vocal and Custom; picking one sets the sliders and a changed band switches the select to Custom. `variant:bands`: five to ten bands with a visible dB value as text under each and a Reset button. `state:off`: sliders `disabled`, preset greyed, text "Equalizer off".
- Keyboard: Tab between sliders, arrows step 1 dB, PageUp/PageDown 3 dB, Home/End min/max. The curve graph is decorative (`aria-hidden`) with the values available as text. Changes apply live without announcement per step. Warn in text if boosting risks clipping.

## 7. Pages

### music-home
- Composition: app shell with `now-playing-bar`; `<main>` with greeting `<h1>`, quick-access `artwork-card` grid and shelves (`<section aria-labelledby>`, each a heading with "Show all" link and a horizontally scrollable row of `artwork-card`, using a `carousel` with scroll buttons and no autoplay).
- `variant:shelves`: recent, made-for-you, new releases. `state:loading`: `skeleton` cards with `aria-busy` and polite status.
- Mobile: bottom nav, shelves scroll horizontally with snap; the bar sits above the nav.

### album-page
- Composition: header (artwork, `<h1>` title, artist link, year, track count, duration), actions (play with `button-primary`, shuffle, `save-toggle`, more menu), `track-list` variant album.
- `variant:default`: one list. `variant:multi-disc`: one table per disc with `<h2>Disc 2</h2>` and continuing numbering. Footer with copyright and label as text. Mobile: stacked header, rows compact.

### playlist-page
- Composition: header with cover, name, description, owner and stats, actions, and `track-list` variant playlist.
- `variant:own`: Edit (opens `playlist-editor`), reorder and remove actions. `variant:followed`: Follow `save-toggle`, no editing. `state:empty`: `empty-state` "Let's find something for your playlist" with a search field.

### artist-page
- Composition: `artist-header`, "Popular" `track-list` (five rows with "Show more" button toggling `aria-expanded`), discography shelves of `artwork-card`, "Appears on" and related artists.
- `variant:popular`: top tracks first. `variant:discography`: tabs (Albums, Singles, EPs) as `tabs`, sorted by date with a view toggle.

### music-library
- Composition: heading, filter chips (a `role="toolbar"` of `<button aria-pressed>` toggles, one pressed at a time with a check), sort menu, view toggle and the collection.
- `variant:grid`: `artwork-card` grid. `variant:list`: compact rows with art, name, type and date. `state:empty`: `empty-state` "Save music you like to see it here" with a Browse link.

### music-search
- Composition: `search-input` (role search landmark), results regions announced by a polite count status ("24 results"), top result as a large `artwork-card`, then Songs (`track-list` variant search), Artists, Albums and Playlists sections.
- `variant:top-result`: top result plus four songs side by side on wide screens. `state:no-results`: "No results for '{query}'" with tips and a clear button. Results update on submit or after a debounce; focus stays in the input.

### music-landing
- Composition (marketing scope, enabled alongside it): `hero` (with a muted preview of `artwork-card`s or a short `now-playing-bar` demo, no autoplay with sound), `feature-split`, `testimonials`, `pricing-table`, `faq`, `cta-band`, `site-footer`, in that order.
- `variant:default`: the sections above in order. Any audio preview is user-started with a pause control and a visible track name.
