# Video components & pages — specs

Scope `video` (enable with `ds init --scopes product,video`; it adds `playback` automatically). Components live in `components/<file>.html` (category **Video**); full pages in `patterns/<file>.html` (category **Video Pages**). Video components compose the `playback` controls (play-toggle, seek-bar, volume-control, time-display, playback-speed, captions-menu, transcript-panel, media-queue, mini-player, cast-button) and product components (button, badge, tabs, table, progress, dialog, popover menu) — wrap them, never re-style or respecify them.

## Contents
1. Rules for every video surface
2. Player: video-player, video-quality-menu, video-end-screen, playlist-panel
3. Browse: video-card
4. Creator: creator-header, subscribe-button, video-upload
5. Safety: content-warning
6. Pages

## 1. Rules for every video surface
Sources are named as rules: WCAG 2.2, `prefers-reduced-motion`, browser autoplay policies, HTML `loading`/`fetchpriority`, schema.org `VideoObject`.

- **Captions, transcripts and audio description** (WCAG 1.2.1 to 1.2.5): every video has `<track kind="captions">`, a transcript where it helps, and an audio-description track or alternative for prerecorded video with visual-only information. Captions are on by stored preference.
- **No autoplay with sound** (browser autoplay policies, WCAG 1.4.2): autoplay, when used, starts muted with a visible unmute control; a click or tap is the only thing that starts audio. Never autoplay on a page the viewer did not open for that video.
- **Pause, stop, hide** (WCAG 2.2.2): any moving preview (hover preview, looping thumbnail, autoplay countdown) has a visible pause or cancel control and stops under `prefers-reduced-motion: reduce`, falling back to a still thumbnail.
- **Playback controls are the playback scope's.** `video-player` places `play-toggle`, `seek-bar`, `volume-control`, `time-display`, `playback-speed`, `captions-menu` and `cast-button` by id and uses `js/lib/media.js` for the keyboard map, Media Session and live region. Do not redefine them.
- **Thumbnails are images with sizes.** Cards use explicit `width`/`height` or `aspect-ratio`, `loading="lazy"` below the first row, and `fetchpriority="high"` only on the watch-page poster (LCP). Thumbnail `alt` is empty when the title text repeats it.
- **Duration and progress are text too** (WCAG 1.4.1): duration is a `<time>` badge ("12:34"); watched progress is a bar plus "Watched 40%" or "5 min left" in the accessible name.
- **Structured data**: watch pages emit `VideoObject` JSON-LD (name, description, thumbnailUrl, uploadDate, duration as ISO 8601, contentUrl or embedUrl, `hasPart` Clip for chapters).
- **Errors and loading are visible text**: loading, buffering and error states have text and an icon, never color only; errors offer Retry and say what happened ("This video can't be played. Check your connection.").
- **Reduced data**: the quality menu honors `navigator.connection.saveData`; data-saver lowers the default resolution and disables preview loops.
- **Subscribe and toggles use state names.** The button name flips ("Subscribe" to "Subscribed"); `aria-pressed` is used only when the label is constant.
- **Age and sensitive gating is server-enforced**: the gate hides the media element (not just overlays it), the client check is a convenience, and the choice persists per policy.
- **Touch and RTL**: 44 px targets (24 px minimum, WCAG 2.5.8); layouts use logical properties; seek fill mirrors under `[dir=rtl]`, time order stays logical.
- **Tokens**: composes `color.media.*` from `playback` and product tokens only; no new tokens.
- **vs.** `video-card` is a media thumbnail card for browsing; `post-card` (social) is a feed item with author and body text. `creator-header` is a channel identity header with subscribe; messaging `channel-header` is a chat-room title bar with members and actions. `video-section` (marketing) is a page section; when interactive it embeds `video-player`.

## 2. Player

### video-player
- `<div role="region" aria-label="Video player: {title}">` wrapping a native `<video>` with `<track>` elements and the playback controls bar; no `controls` attribute once the custom bar is active, but with it as the no-JS fallback.
- `variant:inline`: fits the content column at 16:9. `variant:theater`: full-width, capped height, page chrome dimmed. `variant:fullscreen`: Fullscreen API on the container (not the video) so custom controls and captions stay; Escape exits and focus returns to the toggle.
- `variant:with-chapters`: seek-bar chapter ticks and a chapter list; current chapter title shows in the control bar.
- `state:loading`: poster plus spinner and "Loading". `state:buffering`: spinner and text "Buffering", controls stay operable. `state:error`: poster, message, Retry button (focused), live region announces the error. `state:ended`: shows `video-end-screen` and a "Replay" play-toggle.
- Keyboard: media.js map (Space/K, J/L, arrows, M, C, F) when the player has focus; controls follow the toolbar tab order; Esc closes menus first. Controls auto-hide only after pointer inactivity and always reappear on keyboard focus.
- Reduced motion: no controls fade or hover-preview animation; buffering spinner is a static glyph with text. RTL: control order mirrors; time stays logical.

### video-quality-menu
- Menu button "Quality, Auto (720p)" opening a `[popover]` menu with `menuitemradio` items.
- `variant:auto`: Auto is selected and the label shows the current resolution. `variant:manual`: a fixed level is checked ("1080p"); high levels carry "HD"/"4K" text. `state:data-saver`: a checked "Data saver" item caps resolution, and an inline note says why.
- Arrow keys move, Enter/Space select and close, Escape closes and returns focus. The change is announced politely ("Quality 1080p"). Failure: an unavailable level is `aria-disabled` with a reason.

### video-end-screen
- `<section aria-label="Up next">` over the player at `ended`, with a suggestions grid of `video-card` (compact) and replay button.
- `state:countdown`: "Up next in 5" with a visible Cancel button; the number is text, a progress ring is decorative. `state:cancelled`: countdown gone, "Autoplay cancelled" and a manual "Play next" button. `variant:suggestions`: grid only, no autoplay.
- Under `prefers-reduced-motion` the countdown does not start by itself unless a visible Cancel/Pause control is present; the ring does not animate. The first focus goes to Cancel; Escape cancels. The countdown is announced once, not per tick.

### playlist-panel
- `<section aria-labelledby>` with heading (playlist title, "3 / 12") and `<ol>` of rows (thumbnail, title, channel, duration); each row is a link. No listbox role.
- `state:current-item`: the row has `aria-current="true"` plus a "Now playing" label and is scrolled into view on open. `variant:collapsible`: heading is a disclosure button (`aria-expanded`) that collapses the list. `variant:shuffle-loop`: Shuffle and Loop are toggle buttons with `aria-pressed` (constant labels), loop cycles off/all/one with the state in text.
- Reordering, when allowed, is `sortable-list` move buttons. Keyboard: Tab through rows, Enter plays. Failure: unavailable items show "Unavailable" text and are skipped.

## 3. Browse

### video-card
- `<article>` with a link wrapping the thumbnail and title (one tab stop), channel name as a separate link, metadata "1.2M views · 3 days ago", and a duration `<time>` badge over the thumbnail.
- `variant:grid`: stacked thumbnail over text. `variant:list`: thumbnail beside title, channel and description. `variant:compact`: small thumbnail and two lines, for sidebars and the end screen.
- `state:watched-progress`: a bar under the thumbnail plus "Watched" text in the accessible name. `state:loading`: skeleton with fixed aspect ratio, `aria-busy`.
- Hover preview (optional) is muted, starts after a delay, is absent under reduced motion and data-saver, and has no sound. Thumbnails lazy-load below the first row.
- RTL: text alignment and the badge corner use logical insets. Failure: a missing thumbnail shows a neutral placeholder, not a broken image.

## 4. Creator

### creator-header
- `<header>` with avatar (`alt` empty when the name is adjacent), `<h1>` name (a verified badge has text), handle, subscriber and video counts, and the `subscribe-button`.
- `variant:banner`: wide banner image behind or above the identity; decorative, text never sits on it without a scrim at 4.5:1. `variant:compact`: single row used atop the watch page. `state:subscribed`: the button shows Subscribed and the bell menu.
- Mobile stacks avatar over text; the description truncates with a "More" disclosure.

### subscribe-button
- `<button type="button">` whose name flips "Subscribe" / "Subscribed" (not `aria-pressed`); the subscriber count lives outside the name.
- `state:subscribe`: primary style. `state:subscribed`: secondary style with check icon and text; activating opens a menu to unsubscribe, with confirmation. `variant:with-notifications-bell`: an adjacent menu button "Notifications, Personalized" with `menuitemradio` All/Personalized/None.
- Optimistic update with rollback and a polite announcement ("Subscribed to {name}"); a signed-out click goes to sign-in and returns. Busy: `aria-disabled` with text, still focusable.

### video-upload
- A native `<input type="file" accept="video/*">` in a drop zone that is not the only path; progress uses `<progress>` with text "Uploading 42% of 1.2 GB".
- `state:uploading`: progress, speed text, Cancel button. `state:processing`: indeterminate progress with "Processing, you can leave this page" and an HD processing note. `state:ready`: a success `alert` with link and Publish button. `state:failed`: reason and Retry, nothing lost.
- `variant:metadata-form`: title, description, visibility radiogroup, audience (made-for-kids) radiogroup, captions upload; inline validation per product forms. `variant:thumbnail-picker`: a `radiogroup` of generated frames plus a custom upload, selected state has a check and text.
- Status changes go through one polite live region; leaving mid-upload triggers a `beforeunload` warning.

## 5. Safety

### content-warning
- `<section role="group" aria-labelledby>` replacing the media area, with a heading, reason text and buttons; the media is not in the DOM or is `inert` until confirmed.
- `variant:age-gate`: asks the viewer to confirm an age or sign in; a date field is native `input[type=date]` or three labelled selects, and refusal leads to a back link. `variant:sensitive`: "This video may contain sensitive content" with "Show" and "Go back". `state:revealed`: the content shows with a "Warning shown earlier" note and a way to hide again.
- First focus goes to the primary action; Escape does not dismiss. Never color-only; the reason is always text.

## 6. Pages

### watch-page
- Composition: `video-player` in the main column, title `<h1>`, `creator-header` (compact) with `subscribe-button`, description disclosure, comments, and a related column of `video-card` (compact). Emits `VideoObject` JSON-LD; the poster has `fetchpriority="high"`.
- `variant:default`: two columns. `variant:theater`: player spans full width, content below. `variant:with-playlist`: `playlist-panel` above the related list. `variant:mobile`: player pinned at the top, content scrolls beneath, related and comments in tabs, `mini-player` when scrolled away or navigating.

### video-home
- Composition: optional `tag` chip row (category filter) above a responsive grid of `video-card`. The chips are a `role="group"` with an `aria-label` of `<button aria-pressed>` (one pressed at a time).
- `variant:grid`: 1 to 4 columns. `variant:category-chips`: horizontally scrolling chips, the selected chip with `aria-pressed` and a check; scrolling has buttons, not just swipe. `state:loading`: skeleton cards with `aria-busy`. First row eager, the rest lazy.

### channel-page
- Composition: `creator-header` (banner) plus `tabs` (Videos, Playlists, About).
- `variant:videos`: sort control and card grid. `variant:about`: description, links, join date, stats. `state:empty`: "No videos yet" with an action for the owner.

### video-library
- Composition: sidebar or tabs (History, Watch later), list of `video-card` (list) with watched progress and remove buttons.
- `variant:history`: grouped by day with a Clear history button (confirmation) and a pause-history toggle. `variant:watch-later`: reorderable by move buttons, with Play all. `state:empty`: explains and links to Home.

### video-search-results
- Composition: search `<form role="search">`, result count in a polite live region, filter panel (duration, upload date, type, features) and `video-card` (list) results.
- `variant:filters`: filters as a disclosure on mobile with applied chips. `state:no-results`: states the query, suggests fewer filters or other spelling, and offers popular videos.

### video-studio
- Composition: app shell with left nav, page header and either a `table` or an edit form.
- `variant:content-list`: table (thumbnail, title, visibility, date, views) with bulk select and filters; row actions in a menu. `variant:edit-video`: the `video-upload` metadata-form and thumbnail-picker, a preview `video-player`, and a sticky Save bar with unsaved-changes warning.

### video-landing
- Composition (marketing scope, enabled alongside it): `hero` (with a muted, user-startable `video-player` or `video-section`), `feature-split`, `testimonials`, `pricing-table`, `faq`, `cta-band`, `site-footer`, in that order.
- `variant:default`: hero, feature-split, testimonials, faq, cta-band, site-footer (pricing-table omitted). `variant:with-pricing`: all seven sections. The hero video never autoplays with sound and has a pause control, a transcript link and captions.
