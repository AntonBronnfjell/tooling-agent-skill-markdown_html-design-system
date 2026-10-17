# Live components & pages — specs

Scope `live` (enable with `ds.py init --scopes product,live`; it adds `video` and `playback` automatically). Components live in `components/<file>.html` (category **Live**); full pages in `patterns/<file>.html` (category **Live Pages**). Live components compose `video-player`, the `playback` controls (play-toggle, volume-control, time-display, captions-menu, cast-button), `color.media.live`, and product components (button, badge, tabs, progress, popover menu, fieldset) — wrap them, never re-style or respecify them.

## Contents
1. Rules for every live surface
2. Status and player: live-badge, live-player
3. Audience: live-chat, live-reactions, live-poll, tip-message
4. Schedule: stream-schedule
5. Broadcaster: go-live-panel
6. Pages

## 1. Rules for every live surface
Sources are named as rules: ARIA APG `log` role, WCAG 2.2.2, 2.3.3, 4.1.3 and 1.4.1, HLS/DASH low-latency vocabulary, `prefers-reduced-motion`.

- **LIVE is a word.** Every live status shows the text "LIVE" (or "Starting soon", "Ended", "Offline") with an icon; the red `color.media.live` dot alone never carries it (WCAG 1.4.1).
- **Live edge and DVR vocabulary** (HLS/DASH low-latency): the live edge is the newest playable segment; the DVR window is how far back the viewer can seek. Behind the live edge, the player says so in text ("30 seconds behind live") and offers "Go live".
- **Chat is a `log`** (ARIA APG `log`): `role="log"` has implicit `aria-live="polite"`; new messages append at the end, and the log is never `aria-atomic`.
- **Throttle announcements** (WCAG 4.1.3 status messages): a busy chat must not flood a screen reader. Announcements are off by default or batched ("12 new messages") at most every few seconds, with an opt-in toggle for reading every message; moderation and system notices are always announced.
- **Respect reading position.** When the viewer scrolls up, auto-scroll stops and a "N new messages" button returns to the end; never yank scroll while they read.
- **Moving content is pausable** (WCAG 2.2.2): floating reactions, fast chat scroll and tip animations can be paused or are replaced by static counts, and they stop under `prefers-reduced-motion: reduce`.
- **No flashing** (WCAG 2.3.3 animation from interactions and 2.3.1): reaction bursts and tip effects do not flash more than three times per second and are disabled by reduced motion.
- **Amounts and status are text** (WCAG 1.4.1): tip amounts, viewer counts, poll percentages and stream health are written out; color and icon only reinforce.
- **Playback controls are the playback scope's.** `live-player` composes `video-player` and the shared controls by id; it adds the live-specific parts only. `media.js` owns the single polite live region.
- **Reconnect gracefully**: a dropped stream shows "Reconnecting" with a spinner and text, retries with backoff, and moves to "Stream offline" after a limit with a Retry button; chat reconnects independently.
- **Moderation is server-enforced**: slow mode, members-only and bans are checked server-side; the client only reflects them and says why input is disabled.
- **Secrets are masked**: stream keys are hidden by default, revealed on request, copied with a button, and never put in URLs, logs or analytics.
- **Touch and RTL**: 44 px targets (24 px minimum, WCAG 2.5.8); logical properties; the chat input does not hide behind the on-screen keyboard.
- **Tokens**: composes `color.media.*` (notably `live`) from `playback` and product tokens only; no new tokens.
- **vs.** `live-chat` is a broadcast audience stream with many senders and a moderator, not a conversation; messaging `message-thread` is a person-to-person or group conversation with read state, and ai `conversation` is a single-user exchange with an assistant. `live-player` is a `video-player` for streams (live edge, DVR); use `video-player` for on-demand video. `stream-schedule` lists future streams; `live-directory` lists those on air now.

## 2. Status and player

### live-badge
- `<span>` (not interactive) with a dot icon and text, on `color.media.live` for live, neutral styles for the rest; viewer count is a separate text node.
- `state:live`: dot and "LIVE". `state:starting-soon`: clock icon and "Starting soon", optionally a `<time>` with the start. `state:ended`: "Ended" with the duration. `state:offline`: "Offline". `variant:with-viewers`: "LIVE" plus "12.4K watching" (compact number, full number in the accessible name).
- Viewer count updates are not announced; the dot pulse is decorative and stops under reduced motion. Color pairs meet 4.5:1 for text, 3:1 for the dot.
- RTL: dot and text order mirror; digits stay logical.

### live-player
- A `video-player` (`role="region"`, `aria-label="Live: {title}"`) with live controls: `live-badge`, `play-toggle`, `volume-control`, `time-display` (variant live), `captions-menu`, `cast-button`, fullscreen. The seek bar is a DVR bar only when `variant:dvr`.
- `state:live-edge`: playing at the edge; the badge says LIVE and the "Go live" button is disabled or hidden. `state:behind-live`: the badge shows "30 seconds behind live" and a focusable "Go live" button jumps to the edge.
- `state:reconnecting`: spinner and "Reconnecting", last frame dimmed, controls stay operable, announced politely once. `state:offline`: poster, "Stream offline" and a Retry button or the next scheduled time from `stream-schedule`.
- `variant:dvr`: `seek-bar` over the DVR window with valuetext "5 minutes behind live"; pausing keeps the window and shows the time behind. `variant:latency-indicator`: text "Latency 3.2 s" with a low-latency or normal-latency label, a quality hint not an alert.
- Keyboard: media.js map (Space/K, arrows, M, C, F) plus a key to jump to live; Esc closes menus first. Captions: live captions (WCAG 1.2.4) are offered where the source has them.
- Reduced motion: no pulse or fade; RTL: controls mirror, time stays logical.

## 3. Audience

### live-chat
- `<section aria-label="Live chat">` with a header (title, viewer count, collapse button), a message list `<ol role="log" aria-label="Chat messages">`, and a composer `<form>` (a text input with Send; an emoji popover menu). Each message is `<li>` with author, badge text (Mod, Member), time and text.
- `state:default`: auto-scrolling, newest at the end. `state:paused-scroll`: the viewer scrolled up; the list stops and a button "3 new messages" appears at the end and returns to it (focus not moved). `state:collapsed`: only the header, a "Show chat" button with `aria-expanded="false"`.
- `variant:pinned`: a pinned message (`<aside>` with Pin icon and "Pinned by {name}") above the log with dismiss. `variant:slow-mode`: composer shows "Slow mode: 10 s between messages" and a countdown as text; Send is `aria-disabled` until ready. `variant:members-only`: composer replaced by "Chat is for members" with a Join link. `variant:moderation`: moderators get a per-message menu (Delete, Timeout, Ban) with confirmation, deleted messages read "Message removed".
- Announcements are throttled or opt-in: the log announces batches ("12 new messages") or nothing by default; an "Announce new messages" switch turns on full reading. Mentions of the viewer and moderation notices are always announced.
- Keyboard: Tab to the composer; Shift+Tab reaches the new-messages button and message menus; Enter sends, Shift+Enter is a newline when multi-line. Messages are plain text, links get `rel="noopener nofollow ugc"`.
- Failure: a failed send stays in place with "Not sent" and Retry; disconnected shows "Chat reconnecting". The list is capped (older nodes removed) to keep the DOM small. RTL: per-message `dir="auto"`.

### live-reactions
- `<div role="group" aria-label="Reactions">` of `<button>`s, each with emoji, accessible name "Send heart reaction", and a running count as text.
- `state:default`: a click sends one reaction and a floating emoji rises over the player for about two seconds; holding does not repeat faster than a cap. `state:reduced-motion`: no floating emoji; the count updates statically with a brief non-moving highlight.
- Counts are not announced per reaction; the group may announce a summary only on request. Floating emoji are `aria-hidden` and decorative. Bursts never flash more than three times per second (WCAG 2.3.1, 2.3.3).
- Keyboard: Tab through buttons, Enter/Space sends. Failure: rate-limited buttons are `aria-disabled` with a tooltip ("Slow down"). RTL: floats from the logical end edge.

### live-poll
- `<form>` with `<fieldset><legend>` the question and native radios (or checkboxes for multi-select), a Vote button, a time-remaining text and the vote count.
- `state:open`: options selectable, countdown text "Ends in 1:30" (not announced per tick). `state:voted`: the choice is marked with a check and text "Your vote", results shown as `<progress>` or bars with percent text, with polite announcement "Vote recorded". `state:closed-results`: final results, winner labelled "Winner" with text, "Poll closed".
- Results update at most every few seconds, not announced live; a Retry shows on vote failure. Options are never color-only (percent and label always present). RTL: bars fill from the logical start.

### tip-message
- A chat `<li>` with a highlighted background, amount as text ("$5.00" with currency), author, optional message and a tier label.
- `variant:tiers`: tiers differ by label ("Gold, $20") and by border/background tone plus icon; each tier meets 4.5:1 text contrast. `state:pinned`: the message sits in the pinned slot for a duration shown as text ("Pinned for 2 min"), with a visual countdown bar as decoration.
- Amounts are always text (WCAG 1.4.1); the highlight never relies on color alone. Tips are always announced in the log (they are rare and meaningful) even when other announcements are throttled. Paid messages are still moderated and removable.
- Reduced motion: no entrance animation or pin shimmer. RTL: amount and currency order follow the locale.

## 4. Schedule

### stream-schedule
- `<section aria-labelledby>` with an `<ol>` of events; each has `<time datetime>` (with timezone shown as text), title, streamer and a "Remind me" toggle.
- `variant:week`: seven day groups (each with heading) in a grid on wide screens, stacked on mobile; today is marked with text. `variant:list`: flat chronological list with relative times ("Tomorrow, 8:00 PM").
- `state:reminder-set`: the button reads "Reminder set" with a check and `aria-pressed` is not used (the name flips); polite announcement "Reminder set for {title}". `state:empty`: "No upcoming streams" with a Follow action.
- Times are shown in the viewer's local zone with the zone named. A live event shows `live-badge` and links to the stream. Failure: reminder failure rolls back with a message.

## 5. Broadcaster

### go-live-panel
- `<section role="region" aria-label="Go live">` with a preview `<video muted>`, title and category fields, audio meters (with text dB), a stream health summary, the stream key field and a primary Go live / End stream button.
- `state:preview`: camera preview, button "Go live". `state:live`: `live-badge`, elapsed `<time>`, viewer count and a destructive "End stream" button requiring confirmation. `state:health-warning`: a polite `status` message with text and an icon ("Unstable connection: bitrate dropped to 1.2 Mbps") and a suggestion; critical loss is an `alert`.
- `variant:stream-key`: the key in `<input type="password" readonly>` with a Show/Hide toggle (`aria-pressed` with constant label "Show stream key") and a "Copy stream key" button that announces "Copied" politely; Reset key opens a confirmation dialog. The key is never in the DOM as plain text until revealed, never logged.
- Keyboard: normal form order; End stream is not adjacent to Go live without separation. Health updates throttle to a few seconds and are not announced per tick. Failure: permissions denied for camera or mic shows what to enable.

## 6. Pages

### live-page
- Composition: `live-player` with `live-badge` and title `<h1>`, a streamer header (reusing `creator-header` compact with `subscribe-button`), `live-reactions`, `live-chat`, and about/schedule tabs below. Main landmark; chat is a complementary region.
- `variant:with-chat`: player left, chat in a fixed-width right column on wide screens. `variant:theater`: player spans the width, chat below or as a collapsible panel. `variant:mobile-overlay-chat`: chat overlays the lower part of the player in landscape with transparent messages (4.5:1 on a scrim), a toggle to hide it, and full chat below the player in portrait. `state:offline`: poster, "Offline", the next entry from `stream-schedule`, and past broadcasts as `video-card`.
- Mobile keeps the player pinned and the composer above the keyboard.

### live-directory
- Composition: heading, category chips (a toolbar, single-select as `menuitemradio` or `aria-pressed` toggles per the video conventions) and a responsive grid of live stream cards (`video-card` with `live-badge` and viewer count).
- `variant:grid`: 1 to 5 columns sorted by viewers. `variant:category`: one category with a header and sort menu. `state:empty`: "No one is live in {category}" with the schedule link. Viewer counts refresh without moving the cards under the pointer (re-sort on request only).

### live-studio
- Composition: app shell with the `go-live-panel`, a `live-chat` (moderation variant), a stream health panel, `live-poll` creation and an events list.
- `variant:dashboard`: two or three columns of regions, each with a heading and landmark label; analytics tiles with text values. Collapses to tabs on mobile. Ending a stream asks for confirmation.

### live-landing
- Composition (marketing scope, enabled alongside it): `hero` (with a muted, user-startable `live-player` or `video-player` of a replay), `feature-split`, `testimonials`, `pricing-table`, `faq`, `cta-band`, `site-footer`, in that order.
- `variant:default`: the sections above in order. The hero video never autoplays with sound and has a pause control, a transcript link and captions.
