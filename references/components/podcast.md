# Podcast components & pages — specs

Scope `podcast` (enable with `ds init --scopes product,podcast`; it adds `playback` automatically). Components live in `components/<file>.html` (category **Podcast**); full pages in `patterns/<file>.html` (category **Podcast Pages**). Podcast components compose the `playback` controls by id (`play-toggle`, `seek-bar`, `volume-control`, `time-display`, `playback-speed`, `sleep-timer`, `transcript-panel`, `media-queue`, `mini-player`, `cast-button`) and product components (`button-primary`, `toggle-button`, `progress-bar`, `badge`, `modal`, `popover`, `tabs`, `carousel`, `sortable-list`, `skeleton`, `empty-state`, `toast`) — wrap them, never re-style or respecify them.

## Contents
1. Rules for every podcast surface
2. Player: podcast-player
3. Episodes: episode-row, download-button, episode-notes
4. Shows: show-card, show-header
5. Sharing: clip-share
6. Pages

## 1. Rules for every podcast surface
Sources are named as rules: Podcasting 2.0 namespace (`podcast:chapters`, `podcast:transcript`), WCAG 1.2.1, 1.4.1, 2.2.2, 2.5.3, 2.5.8 and 4.1.3, Media Session API (`seekbackward`, `seekforward`), schema.org `PodcastEpisode` JSON-LD, `prefers-reduced-motion`.

- **Spoken word needs a transcript.** Audio-only content needs a text alternative (WCAG 1.2.1). When the feed has a `podcast:transcript` tag (VTT, SRT or HTML) the episode offers `transcript-panel`; when it has none, say "No transcript available" instead of hiding the control.
- **Skip intervals are first-class.** Media Session `seekbackward` and `seekforward` handlers use the same intervals as the on-screen buttons (default 15 s back, 30 s forward, configurable); `previoustrack`/`nexttrack` go to adjacent queue items. Guard with `'mediaSession' in navigator`, and set metadata (title, show as artist, show art) on every episode change.
- **Chapters come from the feed.** Read `podcast:chapters` JSON (title, start time, optional `img` and `url`) and show them as ticks on `seek-bar` variant chapters plus a list in `episode-notes`. The current chapter title is text near the bar, updated without per-change announcement.
- **Resume where you left off.** Store position per episode; reopening resumes there. Played at 95% or more (or the final seconds) counts as played; offer "Mark as played" and "Mark as unplayed" as buttons.
- **Status is text, not color.** Unplayed, in progress, played and downloaded each show a word or icon-plus-text (WCAG 1.4.1); in-progress shows "{n} min left" next to a `progress-bar` whose `aria-label` repeats it.
- **One toggle pattern, Label in Name (WCAG 2.5.3).** Icon-only toggles keep a stable accessible name ("Add {title} to queue") and flip `aria-pressed`. Text-labelled toggles (follow) flip the visible label and the accessible name together ("Follow" / "Following") and do not use `aria-pressed`, as `subscribe-button` does in video.md and `artist-header` in music.md. A button with a constant visible label may use `aria-pressed`. The accessible name always contains the visible text.
- **Downloads report progress and failure.** The button is icon-only with a stable action name; progress, "Downloaded", "Download failed" and size are adjacent text or a `progress-bar` outside the button, so Label in Name holds. Downloads are cancelable while running. A polite `role="status"` summary announces start, completion and failure once per episode, never per percent (WCAG 4.1.3). Offline mode lists downloaded episodes with text.
- **Show notes are untrusted HTML.** Sanitize feed content (allow paragraphs, lists, links, emphasis); links open normally and external ones say so in text. Timestamps in the notes (`12:34`) become buttons that seek the player, not links to `#`.
- **Sleep timer and speed persist per show.** Playback speed (`playback-speed`) is remembered per show; `sleep-timer` offers "End of episode" and fixed durations, with the remaining time as text and a final fade, not an abrupt stop.
- **Structured data.** Episode pages emit `PodcastEpisode` JSON-LD (name, description, datePublished, duration as ISO 8601, `partOfSeries` as `PodcastSeries`, `associatedMedia` as `AudioObject`) alongside the visible metadata.
- **Targets and touch.** 44 px targets in player and rows on touch (24 px minimum, WCAG 2.5.8); swipe gestures (swipe to queue, to download) have visible button equivalents.
- **Loading and failure.** Lists use `skeleton` with `aria-busy="true"` and a polite "Loading episodes" status. A failed stream shows "Can't play this episode" with Retry; a feed error shows the last cached list with "Couldn't refresh".
- **RTL and logical properties.** Skip buttons keep media order (back, play, forward) but their arrows follow the standard media convention; progress fill and text follow the logical direction; times stay LTR digits.
- **Tokens**: composes `color.media.*` from `playback` and product tokens only; no new tokens.
- **vs.** `podcast-player` versus music `now-playing-bar`: the podcast player has skip intervals, chapters, speed and sleep timer by default, while the music bar centers on previous/next, shuffle and repeat. `episode-row` versus music `track-row`: an episode row is a long-form `li` with date, description, time left, status and download, not a table row with an index and duration; `show-card` is the cover card for a series (compare music `artwork-card`); `download-button` is a stateful `button`, `toggle-button` is a plain binary toggle.

## 2. Player

### podcast-player
- `<section aria-label="Podcast player">` with episode art and title (link to the episode page) and show name (link to the show), `seek-bar` with `time-display`, "Back 15 seconds" and "Forward 30 seconds" buttons around `play-toggle`, `playback-speed`, `sleep-timer`, `cast-button` and a queue button. Composes playback components by id.
- `variant:full`: all controls, large art, chapter list and a transcript toggle (`aria-pressed`, constant label "Transcript"). `variant:compact`: the `mini-player` composition with art, title, `play-toggle` and a thin progress indicator; the title area opens the full player.
- `variant:skip-15-30`: skip buttons named with their interval ("Back 15 seconds", "Forward 30 seconds"), icon plus the number as visible text so the name contains it. Keys: J back 15 s and L forward 30 s (the player's configured skip intervals, rebinding the playback J/L default); Left/Right arrows stay 5 s; when focus is not in a field, via `media.js`.
- `variant:chapter-art`: artwork swaps to the current chapter's `img` and the chapter title shows as text; the art change is not announced and has `alt=""` because the title is adjacent text. Under reduced motion the swap is a cut, not a cross-fade.
- Live region: the shared status announces "Now playing: {title}" once, politely. Chapter changes are visual only. Failure: "Can't play this episode" with Retry; offline with no download says so.
- Keyboard: Tab order follows visual order; Space on `play-toggle`; speed and sleep timer open as `popover` menus that Esc closes. RTL: layout mirrors, times stay LTR.

## 3. Episodes

### episode-row
- An `<li>` (in a `ul` or `ol` list, never a `listbox`) with show art (optional), `<h3>` title link, date as `<time datetime>`, a two-line description, duration or time left, a `progress-bar` when in progress, a play `<button aria-label="Play {title}">` and `download-button` (icon-only, status text beside it); a "More actions" popover holds queue, mark played and share.
- `state:unplayed`: a "New" `badge` (text) before the title. `state:in-progress`: "{n} min left" with progress; play button name "Resume {title}". `state:played`: "Played" text with a check, title in a lower-emphasis style that still passes 4.5:1. `state:downloaded`: "Downloaded" text with icon beside the duration.
- `variant:compact`: one line (title, duration), no description, 44 px target on coarse pointers; used in queues and show lists with many items.
- Keyboard: Tab to the title link, play button, download button and more menu; the row itself is not a button, so there is no Enter-on-row action (unlike music `track-row`). The play button is visible on focus. A currently playing row has `aria-current="true"` and the text "Now playing".
- Failure: a download or playback error replaces the duration with text and Retry. RTL: media and text mirror, dates localised.

### download-button
- An icon-only `<button>` (icon button variant) with no visible text, so its accessible name is the action plus episode and may change with state (WCAG 2.5.3 is satisfied because there is no visible label to contradict). Status text ("45 MB", "{n}%", "Downloaded", "Download failed") sits outside the button as adjacent text, linked by `aria-describedby` where useful, never inside it. If a visible label is ever added inside the button, the accessible name must contain it exactly.
- `state:idle`: download icon, name "Download {title}", size as adjacent text. `state:downloading`: cancel (X) icon, name "Cancel download of {title}", with a `progress-bar` (`aria-label="Downloading {title}"`) and "{n}%" as text next to the button, not inside it. `state:downloaded`: check icon, name "Remove download of {title}" (confirm or Undo `toast`), with "Downloaded" as adjacent text.
- `state:error`: warning icon, name "Retry download of {title}", with "Download failed" as adjacent text (and a reason such as no storage). On a metered network, ask before continuing with text. The icon shape changes per state, not only color (WCAG 1.4.1).
- A polite `role="status"` summary announces "Downloading {title}", "Downloaded {title}" and "Download failed" once each; percent changes are not announced. Reduced motion: progress is a static bar update, no spinner animation.

### episode-notes
- `<section aria-label="Episode notes">` holding sanitized description HTML, optionally a chapters `<ol>` and a links `<ul>`; headings continue the page outline.
- `variant:timestamps-seek`: timestamps in the notes are `<button>` elements with the visible time ("12:34") and the name "Play from 12:34", which call the player's seek and move focus nowhere (the player announces position through `aria-valuetext`). `variant:chapters`: an `<ol>` of chapter buttons (start time, title, optional thumbnail with `alt=""`), the current one marked `aria-current="true"` plus a "Now playing" text; selecting seeks to the start.
- `variant:links`: a "Links mentioned" `<ul>`; external links carry visible "(opens in new tab)" text or an icon with an accessible name when `target="_blank"`. Sponsor links say "Sponsor" in text.
- "Show more" collapses long notes via a `button[aria-expanded]` controlling the region; collapsed content is not clipped from the accessibility tree misleadingly (use `hidden` or line-clamp with the full text reachable). Empty notes show "No show notes for this episode".

## 4. Shows

### show-card
- `<article>` with square cover (`alt=""` when the title is adjacent), `<h3>` title link (the stretched primary link), publisher text and optional episode count or "New episode" text. No nested play button unless it has its own name ("Play latest episode of {show}") and is not inside the link.
- `variant:grid`: cover over the text, used in shelves and search. `variant:list`: cover at the start with title, publisher and a two-line description, used in the library.
- Keyboard: one tab stop on the link (plus the optional play button). Placeholder with initials when the cover fails. Hover lift off under reduced motion. RTL: text aligns to the logical start.

### show-header
- `<header>` with cover, `<h1>` show title, publisher, category links, a follow button, a "More" menu and optionally rating and RSS link. Cover is decorative if the title is adjacent.
- `state:following`: the visible label and accessible name flip together from "Follow" to "Following" with a check icon, no `aria-pressed`, as `subscribe-button` in video.md; the show is named by context via `aria-describedby` pointing to the `<h1>`. A notifications bell next to it is a separate icon `toggle-button` with the stable name "New episode notifications for {show}" and `aria-pressed`.
- `variant:with-rating`: rating as text "4.7 out of 5, 12K ratings" (stars `aria-hidden` or an `img` with that name), never stars alone. `variant:rss-link`: a link "RSS feed" (visible text, copyable URL shown on activation with a copy button and a polite "Feed link copied" status).
- Mobile: cover shrinks, actions wrap below the title. Failure to follow reverts the label with "Couldn't follow" in the status.

## 5. Sharing

### clip-share
- A `<dialog>` (modal component, `aria-labelledby` the heading "Share") with a link-type choice, a preview, a copy button and share targets as buttons or links. Opened from a "Share" button, which receives focus again on close.
- `variant:at-timestamp`: a checkbox "Start at 12:34" (default checked) whose label shows the current time; the generated URL appends the time and the preview text states it. `variant:clip-range`: two time inputs (start, end, `input[type=text]` with `inputmode="numeric"` and pattern, or a dual range pair with `aria-valuetext`) with a maximum length (for example 60 s) stated in text, a preview button that plays the range and a Create clip button.
- Validation: end after start, within the episode and under the maximum, errors linked by `aria-describedby` and a summary on submit. Copy gives a polite "Link copied" status; creating a clip shows progress text and a result link, with failure kept in the dialog with Retry.
- Keyboard: focus moves into the dialog, Tab is trapped, Esc closes. Shared pages carry `PodcastEpisode` JSON-LD and an Open Graph preview; the clip page starts paused at the start time (no autoplay with sound).

## 6. Pages

### podcast-home
- Composition: app shell with `podcast-player` variant compact (as the persistent `mini-player`); `<main>` with `<h1>` "Home", a "Continue listening" shelf of `episode-row` variant compact, "New episodes" `episode-row` list and show shelves of `show-card` (each a `<section aria-labelledby>` with a "Show all" link, using `carousel` with scroll buttons and no autoplay).
- `variant:shelves`: continue listening, new episodes, popular, by category. `state:loading`: `skeleton` rows and cards with `aria-busy="true"` and the polite "Loading" status. Mobile: bottom nav, shelves scroll with snap, the player sits above the nav and the last item has bottom padding equal to its height.

### show-page
- Composition: `show-header`, then `tabs` (Episodes, About) with a sort button (Newest, Oldest) and `episode-row` list; "Load more" button rather than infinite scroll, with focus moving to the first new row.
- `variant:episodes`: the episodes panel selected, with a "Download all new" action using `download-button`. `variant:about`: description text, categories, host and publisher, links, rating and RSS (`show-header` details), and language; nothing is hidden behind hover.
- Mobile: header stacked, tabs full width. An empty show says "No episodes yet" with `empty-state`.

### episode-page
- Composition: `<main>` with the show link above the `<h1>` episode title, date, duration, a Play button (`button-primary`), `download-button`, `clip-share` trigger, `podcast-player` variant full, `episode-notes` (chapters, links) and "More from this show" as `episode-row` list. Emits `PodcastEpisode` JSON-LD.
- `variant:default`: notes below the player. `variant:with-transcript`: `transcript-panel` beside the notes (a tab on narrow screens) with speaker names, timestamps that seek and a search field; auto-follow is pausable (WCAG 2.2.2) and the panel has the constant label "Follow along" with `aria-pressed`. When the feed has no transcript, the panel says so.
- Mobile: player first, notes and transcript as tabs.

### podcast-queue
- Composition: heading "Up next", the now-playing episode, then a `ul` using `sortable-list` of `episode-row` variant compact with move up/down buttons, remove buttons, and "Clear queue" (with confirm or Undo `toast`). Reuses `media-queue` behavior from `playback`; not a `listbox`.
- `state:with-items`: total time left as text, polite announcement "{title} moved to position 3 of 12", "Play next" and "Add to queue" results land here. `state:empty`: `empty-state` "Your queue is empty" with a Browse link.
- Mobile: swipe to remove has a button equivalent; drag handles are at least 44 px.

### podcast-landing
- Composition (marketing scope, enabled alongside it): `hero` (with a muted preview of `show-card`s or a short `podcast-player` demo, no autoplay with sound), `feature-split` (skip intervals and chapters, downloads and offline), `testimonials`, `pricing-table`, `faq`, `cta-band`, `site-footer`, in that order.
- `variant:default`: the sections above in order. Any audio preview is user-started, has a pause control and shows the episode title as text.
