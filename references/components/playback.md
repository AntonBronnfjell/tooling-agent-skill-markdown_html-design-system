# Playback components — specs

Scope `playback` is a **base scope**: you rarely enable it by hand. `ds.py init --scopes product,video` (or `live`, `music`, `podcast`, `reading`, `messaging`) adds it automatically, and `ds.config.json → scopes` is expanded the same way on load for components. Scope tokens are copied only by `init`: after adding scopes to `ds.config.json` by hand, run `ds.py init <dir> --force` (not `--adopt`, which exits when `ds.config.json` exists) to copy `tokens/scopes/playback.json` and its themes. Components live in `components/<file>.html` (category **Playback**); there are no pages. Playback components compose product components (button, slider, popover menu, sortable-list, tooltip) — wrap them, never re-style them.

## Contents
1. Rules for every playback surface (including `js/lib/media.js`)
2. Transport: play-toggle, seek-bar, volume-control, time-display, playback-speed
3. Text tracks: captions-menu, transcript-panel
4. Queue & presence: media-queue, mini-player
5. Utilities: sleep-timer, cast-button

## 1. Rules for every playback surface
Sources are named as rules, not numbers: WCAG 2.2, WebVTT, Media Session API, Remote Playback API, FCC caption display settings, ARIA APG.

- **Captions and transcripts are first-class** (WCAG 2.2 1.2.2 captions for prerecorded media, 1.2.4 live captions, 1.2.5 audio description). Every player exposes a captions control; audio-only media offers a transcript. Caption preference persists and is applied on load.
- **Caption styling is a user setting** (FCC caption display rules as precedent): size, text color, background color/opacity, edge style and font family are user-controlled and never overridden by the author. Captions render as WebVTT cues (`<track kind="captions">`) over `color.media.scrim`; cue text meets 4.5:1.
- **Nothing moving without a way to stop it** (WCAG 2.2 2.2.2 pause, stop, hide): any auto-updating or auto-playing element has a visible pause control.
- **Audio never starts on its own** (WCAG 2.2 1.4.2 audio control): no autoplay with sound for more than 3 s without a visible pause/mute control; autoplay, when allowed, starts muted.
- **Seek bar is a native range slider** (ARIA APG slider): `input[type=range]` with `aria-valuetext` like "1:23 of 4:56"; Arrow keys step 5 s (the markup says `step="1"`, so a `keydown` handler steps 5 s and calls `preventDefault`), PageUp/PageDown 10%, Home/End jump to ends.
- **Speed and caption pickers are menu buttons** (ARIA APG menu button): a `button` with `aria-haspopup`/`aria-expanded` opening a `[popover]` menu; the button's name carries the current value ("Playback speed, 1.5x").
- **Transport buttons change their name, not `aria-pressed`.** "Play" becomes "Pause"; "Mute" becomes "Unmute". The icon swap is paired with the name swap.
- **Keyboard map** (`js/lib/media.js`, active when the player or its container has focus): Space or K play/pause; Left / Right arrows seek 5 s everywhere; J / L skip back/forward by the player's configured skip intervals (default 10 s; podcast and audiobook players rebind them to their 15 s back / 30 s forward buttons); M mute; C captions; F fullscreen. Shortcuts never fire while typing in an input, and never capture Space on a focused button.
- **Media Session API.** `js/lib/media.js` sets `navigator.mediaSession.metadata` (title, artist/channel, album, artwork sizes 96-512) and registers `play`, `pause`, `seekbackward`, `seekforward`, `previoustrack`, `nexttrack`, `seekto`, and keeps `playbackState` and `setPositionState` current, so lock-screen and headset controls work.
- **One polite live region.** `media.js` announces through `js/lib/live-region.js` (one polite region per page, never its own `role="status"`): state changes ("Paused", "Captions on", "Speed 1.5x", "Buffering"). Time ticks are never announced; `aria-live` is never put on the time or the seek bar.
- **Remote playback is feature-detected** (Remote Playback API; AirPlay via `webkitShowPlaybackTargetPicker`): `cast-button` is hidden or `state:unavailable` when no target exists, never a dead button.
- **Reduced motion and no motion-only cues.** Buffering spinner, hover previews and expand animations respect `prefers-reduced-motion`; live, buffering and error states always have text, not only color (WCAG 1.4.1).
- **Touch targets** are at least 44 px (24 px WCAG 2.5.8 minimum); controls stay reachable with one thumb in the mini-player.
- **Tokens.** `color.media.surface` (always dark), `scrim`, `fg`, `track.rail|buffered|played`, `live`, `live-fg` (text on the LIVE badge), `focus`. Contrast pairs: fg on surface 4.5, fg on scrim 4.5 (captions), live-fg on live 4.5, live on surface 3, played on rail 3, played on buffered 3, fg (thumb) on buffered 3, focus on surface 3. The surface stays dark in every theme; buffered sits between rail and played; high-contrast raises focus and separation.
- **vs.** `media-stage` (product) is a static hero surface, not a player. `video-section` (marketing) is a page section; when interactive it embeds `video-player`. Players built on this scope (video, music, podcast) compose these controls rather than redefining them.

## 2. Transport

### play-toggle
- `<button type="button">` with an icon plus visually-hidden text; the name flips between "Play" and "Pause" (never `aria-pressed`).
- `state:play`: shows the play glyph, name "Play". `state:pause`: pause glyph, name "Pause".
- `state:loading`: spinner, name "Loading", `aria-disabled="true"` but focusable; the live region announces "Buffering".
- `state:replay`: replay glyph at end of media, name "Replay"; activating seeks to 0 and plays.
- Keyboard: Space/Enter on the button, K from the player. Reduced motion: spinner becomes a static glyph with text. RTL: play triangle mirrors with `[dir=rtl]`.

### seek-bar
- `<input type="range" min="0" max="duration" step="1">` with `aria-valuetext` "1:23 of 4:56"; buffered and played ranges are drawn with `color.media.track.*` behind the native thumb.
- `state:default`: played fill plus thumb. `state:buffering`: buffered range stalls, a text "Buffering" appears with the spinner, and the thumb stays operable.
- `variant:chapters`: ticks at chapter starts; the chapter title is part of the value text ("Intro, 0:42 of 4:56").
- `variant:hover-preview`: a time (and optional thumbnail) tooltip on hover and keyboard focus; thumbnails are decorative, the time text is the content.
- `state:live-edge`: for live streams; shows a "LIVE" button to jump to the edge, and valuetext "Live" or "30 seconds behind live".
- `state:disabled`: native `disabled` on the range plus adjacent visible reason text ("Seeking unavailable"), not `title` only.
- Keyboard: Arrows 5 s, PageUp/PageDown 10%, Home/End. The bar is mirrored under `[dir=rtl]` for the visual fill, but the time order remains logical. Failure state: unknown duration shows the elapsed time only and a non-seekable state.

### volume-control
- Mute `<button>` (name "Mute" / "Unmute") followed by `<input type="range" min="0" max="1" step="0.05">` labelled "Volume", `aria-valuetext` "70 percent".
- `state:default`: slider visible beside the button at desktop widths. `state:muted`: icon and text show muted; the slider keeps its remembered value and restores on unmute.
- `variant:vertical-popover`: the slider sits in a `[popover]` above the button for narrow bars; opens on focus, hover or click, closes on Escape and returns focus to the button.
- Keyboard: Up/Down 5%, M mutes. On iOS volume is hardware-only, so hide the slider and keep the mute button when `volume` is not settable.

### time-display
- `<time datetime="PT1M23S">` elements; separators are plain text ("1:23 / 4:56").
- `variant:elapsed-duration`: "1:23 / 4:56". `variant:remaining`: "-3:33". `variant:live`: "LIVE" text plus a dot, optionally "-0:30" behind live (never color-only).
- `font-variant-numeric: tabular-nums` so width does not jitter; format with hours only when needed.
- Not a live region: never announced per tick (the seek bar's `aria-valuetext` carries the time on demand). Tap toggles elapsed/remaining when the product allows.

### playback-speed
- A menu button "Playback speed, 1x" opening a `[popover]` menu with `menuitemradio` entries 0.5, 0.75, 1, 1.25, 1.5, 2, 3x; the current value is in the button name.
- `variant:menu`: the menu above. `variant:stepper`: minus/plus buttons that step 0.25 within 0.5-3x, with the current value displayed between them as text.
- Setting `preservesPitch` stays true. Speed applies instantly and is announced once via the live region ("Speed 1.5x"). Persists per product (or per show for podcasts).
- Keyboard: arrows move in the menu, Enter selects, Escape closes; shortcuts Shift+. and Shift+, step speed when the product enables them.

## 3. Text tracks

### captions-menu
- Menu button "Captions" (state in the name: "Captions, off" or "Captions, English") opening a `[popover]` menu of `menuitemradio` tracks plus "Caption style…".
- `state:off`: "Off" is checked, button shows an unfilled glyph plus text. `state:on`: a track is checked; the glyph shows an underline or fill (not color alone).
- `variant:tracks`: one entry per `<track kind="captions|subtitles">` by `label` and `srclang`; auto-generated captions are labelled "(auto-generated)". Descriptions tracks (1.2.5) are listed separately.
- `variant:caption-style`: size (50-200%), text color, background color and opacity, edge style and font family, with a live preview line on `color.media.scrim`. This is a user setting persisted across sessions (FCC-style).
- Keyboard: C toggles on/off from the player; arrows and Enter in the menu. Respect OS caption preferences when `prefers-captions`-style settings exist; RTL cues use `dir` from the WebVTT cue.

### transcript-panel
- A `section` labelled "Transcript" containing an `<ol>` of cues, each a `<button>` with a `<time>` and text (or a link when the product uses text links).
- `state:synced`: the active cue has `aria-current="true"` plus a visible marker; the panel scrolls to keep it in view.
- `variant:search`: a search field filters/highlights matches; match count is announced politely ("3 matches").
- `variant:click-to-seek`: activating a cue seeks to its start time and keeps focus on the cue.
- `state:auto-scroll-paused`: scrolling manually or moving focus pauses auto-scroll and shows a "Jump to current" button (WCAG 2.2.2). Never steals focus.
- Reduced motion: scroll jumps instantly. Includes speaker labels and `[inaudible]` conventions.

## 4. Queue & presence

### media-queue
- A plain list (`<ol>`, implicit `list` role, not a listbox, since items hold buttons and menus) of items (artwork, title, creator, duration) inside a labelled region "Queue"; the playing item has `aria-current="true"` and a "Now playing" text label with an equalizer glyph that is static under reduced motion.
- `state:now-playing`: current item pinned at the top. `state:empty`: "Nothing queued" with an action to browse.
- `variant:reorder`: composes `sortable-list` (drag handle plus keyboard Up/Down move buttons, live announcement "Moved to position 3 of 8"); remove has Undo.
- `variant:up-next`: compact view showing the next 1-3 items with "Play next"/"Add to queue" in the item menu.

### mini-player
- A `<aside aria-label="Mini player">` holding the play-toggle, title, optional skip and a thin progress `<progress>`; activating the title region expands it.
- `variant:bottom-bar`: fixed to the block-end edge with safe-area inset; content above must reserve padding. `variant:floating`: a small draggable (keyboard-movable) overlay that can dock to corners.
- `state:expanded`: expands to the full player (a `dialog` on mobile); focus moves in and Escape or the collapse button returns it.
- Keeps playing across navigation; closing it stops playback after an explicit "Close" (name states "Close player"). Reduced motion: no slide, cross-fade only.

## 5. Utilities

### sleep-timer
- A menu button "Sleep timer" opening a `[popover]` menu: Off, 5, 10, 15, 30, 45, 60 minutes, "End of chapter/episode".
- `variant:minutes`: counts down; `variant:end-of-chapter`: stops at the next chapter boundary.
- `state:active`: the button name includes the remainder ("Sleep timer, 12 minutes left") and a visible badge; the final 30 seconds fade volume. Announce set and cancel via the live region only, not each minute.
- Failure: if the chapter list is missing, the end-of-chapter option is hidden.

### cast-button
- A `<button>` named "Cast to device" using the Remote Playback API (`video.remote.prompt()`), or `webkitShowPlaybackTargetPicker` for AirPlay; availability via `remote.watchAvailability`.
- `state:available`: normal. `state:connecting`: spinner with text "Connecting to Living Room TV". `state:connected`: the name becomes "Casting to Living Room TV. Stop casting", with a visible text label.
- `state:unavailable`: hidden by default, or disabled with explanation when the product wants the affordance visible.
- Local controls keep working while connected (they drive the remote session); failures announce "Couldn't connect" and return to `state:available`.
