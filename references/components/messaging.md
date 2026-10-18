# Messaging components & pages — specs

Scope `messaging` (enable with `ds.py init --scopes product,messaging`; it adds `playback` automatically, add `marketing` for `messaging-landing`). Components live in `components/<file>.html` (category **Messaging**); full pages in `patterns/<file>.html` (category **Messaging Pages**). Messaging components compose product components (`button-primary`, `button-destructive`, `avatar`, `badge`, `modal`, `popover`, `overflow-menu`, `tabs`, `composer`, `file-upload`, `progress-bar`, `empty-state`, `skeleton`, `toast`, `text-field`) and the `playback` controls by id (`play-toggle`, `seek-bar`, `time-display`, `playback-speed`) — wrap them, never re-style them.

## Contents
1. Rules for every messaging surface
2. Direct and group messages: message-bubble, message-thread, conversation-row, presence-indicator, typing-indicator, attachment-preview, message-reactions, emoji-picker, voice-note, mention-autocomplete, read-receipts, message-search
3. Channels: channel-list, channel-header, thread-panel, member-list, pinned-messages
4. Calls: call-controls, participant-tile, incoming-call, device-check
5. Support: support-launcher, support-panel
6. Pages

## 1. Rules for every messaging surface
Sources are named as rules, not numbers: ARIA APG (`log`, `grid`, `combobox`, `alertdialog`), WCAG 2.2 (4.1.3 status messages, 1.4.1 use of color, 2.2.2 pause stop hide, 2.5.8 target size, 1.4.11 non-text contrast, 2.5.3 label in name), `getUserMedia` / `MediaDevices` permission UX.

- **Sender is conveyed by text.** Own and other bubbles differ by alignment and color, but every `message-bubble` also carries the sender in text: a visually hidden "You said" / "Ana said" before the body, or a visible name above the first bubble of a group. Alignment and color alone are never the signal (WCAG 1.4.1). Time, edited and delivery state are text too.
- **Native first.** Messages are `<li>` items of an `ol`; the composer is a `<form>` with a `textarea`; reactions and call controls are `<button>`; the incoming call is a `<dialog>`; the member list and channel list are `ul`. Roles are added only where no element exists (`log`, `grid`, `combobox`, `alertdialog`).
- **A log announces everything, so throttle it** (ARIA APG `log`: implicit `aria-live="polite"`; WCAG 4.1.3 status messages). `message-thread` is `role="log"` with `aria-live="off"` so new messages are not read one by one, plus one batched `role="status"` summary beside it ("3 new messages from Ana", at most once every few seconds, merged). Mentions of the viewer and failed sends are announced immediately through a separate `role="alert"`/status. A user switch "Announce every message" restores full reading. `live-chat` (live scope) is a broadcast stream with the same throttling; this thread is a conversation.
- **Typing and receipts are quiet** (WCAG 4.1.3). Typing is one polite status ("Ana is typing", "Ana and 2 others are typing"), debounced, set on start and cleared on stop (never repeated per keystroke); read receipts update text in place without announcing, except the latest own message's state change summarised in the same batched status.
- **Typing animation is not essential motion** (WCAG 2.2.2, `prefers-reduced-motion`). Dots stop pulsing under reduced motion (static "..." with the text), and any animation that runs more than 5 s has a way to stop. Message entry animations become instant.
- **Presence is never color alone** (WCAG 1.4.1, 1.4.11). `presence-indicator` is a dot of `color.presence.*` (at least 3:1 against `color.bg.surface` in every theme) with a different shape or glyph per state (filled, half, minus, hollow) and a text alternative (visible label or visually hidden "Online").
- **Message state is explicit.** `sending` (spinner icon + "Sending"), `sent`, `delivered`, `read`, `failed-retry` ("Not sent" with Retry button), `edited` ("Edited"), `deleted` ("This message was deleted", content removed from the DOM). Optimistic sends keep their place; retry never reorders.
- **Scroll position is respected.** The thread follows the newest message only while the user is within a threshold of the end; otherwise a "Jump to latest" button with the unread count appears and focus is never moved. Loading older messages preserves the scroll anchor (`overflow-anchor`, or manual restore) so the view does not jump.
- **Composer keys.** Enter sends, Shift+Enter inserts a newline (Ctrl/Cmd+Enter configurable on touch); IME composition (`isComposing`) never sends. Drafts persist per conversation. Pasted and dropped files become `attachment-preview` items before send.
- **Calls need explicit consent and recovery.** The camera and microphone are requested only after a user action, preceded by `device-check`, with plain-language denied and no-device states and a recovery path ("Allow in browser settings"). Join is muted by default when the user has not chosen otherwise. Media is stopped (`track.stop()`) when leaving a call or closing the check.
- **Call controls are big and labelled** (WCAG 2.5.8 target size, minimum 24 px; use 44 px for touch). Mute and camera are toggles with a stable name and `aria-pressed` (icon only: "Microphone", "Camera"); "Leave" uses `button-destructive`, is separated from the toggles and never adjacent to Mute without spacing. Hardware and keyboard shortcuts (M, V) are listed and rebindable.
- **Incoming calls interrupt, so they are accountable.** `incoming-call` is an `alertdialog` that takes focus, names the caller, has Accept and Decline buttons, rings only with sound the user enabled, auto-stops after a timeout, and leaves a "Missed call" row in the thread.
- **User content is untrusted.** Messages render as text; links get `rel="noopener nofollow ugc"`, previews are fetched server side, and each message has `dir="auto"`. Emoji have names ("Thumbs up") for search and AT.
- **Touch and RTL.** Targets at least 44 px on touch; swipe actions on `conversation-row` always have a menu equivalent. Use logical properties; own bubbles align to `inline-end` and flip in RTL.
- **Tokens.** `color.message.own.bg|fg`, `color.message.other.bg|fg`, `color.presence.online|away|busy|offline`, `size.message.max-width` (68ch). Contrast pairs (light, dark, high-contrast): each bubble `fg` on its own `bg` at 4.5, each presence color on `color.bg.surface` at 3. Everything that appears on a bubble (text, links, reply quote, timestamp, edited label, reaction counts) uses the bubble `fg` token or a documented lighter variant that is pair-checked; never the page text color. Bubbles do not need to meet 3:1 against the surface because the text, the sender label and the tail or border carry the boundary; in high-contrast the other bubble gets a 1 px `color.border` outline. Dark and high-contrast themes override all of them.
- **vs.** `message-bubble` is a person-to-person message; ai `chat-message` is an assistant turn with sources, tools and streaming, and product `comment-thread` is document discussion with resolve states, not live chat. `message-thread` is a conversation log; `live-chat` is a broadcast audience stream. `channel-header` is the header of a channel or DM; video `creator-header` is a channel's public branding with subscribe. `support-panel` is a customer-to-agent chat widget with handoff and CSAT; ai `copilot-panel` is an assistant docked in the app. `thread-panel` is the replies side panel of one message; `message-thread` is the main conversation.

## 2. Direct and group messages

### message-bubble
- Markup: `<li>` containing `<article>` (or a `div`) with a visually hidden "You said" / "{Name} said", the text, then a `<footer>` with `<time datetime>` and state text. Avatars are `avatar`; the group sender name sits above the first bubble.
- `variant:own` (inline-end, `color.message.own`) and `variant:other` (inline-start, `color.message.other`), both with `max-width: size.message.max-width`. `variant:grouped-first`, `variant:grouped-middle`, `variant:grouped-last`: consecutive messages from one sender within a few minutes; first shows name and avatar space, corners tighten between, last shows time and avatar. Grouping is purely visual; the hidden sender text stays on every bubble.
- `variant:with-avatar`: `avatar` beside the last bubble of a group (empty `alt`; the name is in the text). `variant:reply-quote`: a `<blockquote>` "Replying to Ana" with a 2-line excerpt that is a link to the original (a button focusing it), in the bubble fg color.
- `state:sending` (clock icon + "Sending"), `state:sent`, `state:delivered`, `state:read` (check glyphs with text "Sent", "Delivered", "Read", never ticks alone), `state:failed-retry` ("Not sent" in `color.text.danger` with an error icon and a Retry button; Delete is a menu item), `state:edited` ("Edited" next to the time), `state:deleted` (italic "This message was deleted", reactions and quote removed).
- Keyboard: the bubble is not a tab stop; per-message actions (React, Reply, More menu) are buttons in a toolbar-like group revealed on hover or focus-within and always reachable by Tab. Long press opens the same menu on touch.
- Failure and edge cases: very long unbroken strings wrap (`overflow-wrap: anywhere`); never fix heights (WCAG 1.4.12). Contrast: all text on the bubble uses `color.message.*.fg`. Reduced motion: no pop-in. RTL: bubble tail and alignment flip.

### message-thread
- Markup: `<section aria-label="Conversation with Ana">` containing `<ol role="log" aria-live="off" aria-relevant="additions">` of messages, a sibling `<p role="status">` for the batched announcement, a "Jump to latest" button and the `composer`. The log is a focusable scroll region (`tabindex="0"`) only if it can scroll; Page Up/Down and Home/End scroll it.
- `variant:day-dividers`: `<li>` rows containing a `<time>` (or an `<h3>`) "Today", "Yesterday", "Mon 12 Oct", sticky while scrolling; they are text, not only a line.
- `state:unread-divider`: "3 unread messages" line (text, a New marker, not color alone) with the first unread message focusable via the "Jump to unread" button; cleared after the user has read to the end.
- `state:jump-to-latest`: shown when scrolled up; button "Jump to latest, 4 new" (the visible text is contained in the name); activating scrolls to the end and moves focus to the composer.
- `state:loading-older`: `skeleton` bubbles at the top, `aria-busy="true"` on the log, status "Loading earlier messages"; reaching the top triggers loading with a scroll-anchor so the view does not jump; failure shows "Couldn't load earlier messages" with Retry.
- `state:empty`: `empty-state` "Say hello to Ana" with the composer focused.
- Throttling (see rules): the log is `aria-live="off"`; the status batches. DOM is virtualised for long histories with the visible window kept in the accessibility tree and `aria-setsize`/`aria-posinset` only if the list is virtualised. RTL: `dir="auto"` per message.

### conversation-row
- Markup: `<li>` with one `<a>` (the whole row is the link) containing `avatar` (with `presence-indicator`), name, last-message preview (one line, truncated with `text-overflow`), time and badges; the accessible name is built as "Ana Silva, unread 3, last message …, 10:42".
- `state:unread`: bold name and a count `badge` with text ("3 unread" visually hidden prefix); `state:muted`: bell-off icon with "Muted" text for AT and no count color; `state:pinned`: pin icon + "Pinned"; `state:typing`: preview replaced by "Ana is typing…" (no announcement from the row, the thread owns it).
- `variant:group`: stacked or collage avatar, sender prefix in the preview ("Ben: Sounds good"), member count in the label.
- Current conversation uses `aria-current="page"`. Keyboard: Tab through rows, Enter opens; a context menu (Mute, Pin, Mark unread, Archive) is an `overflow-menu` per row, and swipe actions on touch have the same `overflow-menu`. Reduced motion: swipe reveal without spring.

### presence-indicator
- Markup: `<span>` with a dot (`aria-hidden="true"`) and either a visible label or a visually hidden label ("Online"). On an `avatar` badge position, the text is attached to the row name via `aria-describedby` or the hidden text, not a lone `aria-label` on a `span`.
- `state:online` (filled circle, `color.presence.online`), `state:away` (clock or half-filled glyph, "Away"), `state:busy` (minus or dash glyph, "Busy, do not disturb"), `state:offline` (hollow circle, "Offline"). Each differs by shape and text as well as color; all dots are at least 3:1 against `color.bg.surface`.
- Last-seen text ("Active 5 min ago") is shown in the header or on hover/focus, never only in a tooltip. Status changes are not announced. High-contrast: dot gets an outline.

### typing-indicator
- Markup: `<p role="status">` (or a visible text node inside the thread's status region) with three dots (`aria-hidden`) and text "Ana is typing…".
- `state:one`: "Ana is typing"; `state:several`: "Ana and Ben are typing", then "Several people are typing" past three. `state:reduced-motion`: dots static, no pulsing (`prefers-reduced-motion: reduce`); the text stays.
- Announcements throttled: a typing event sets the status once per typing burst, expires after about 5 s without events, and is cleared on send; no announcement per keystroke or per user change within 3 s. The sender's own typing is never shown.
- Place it above the composer, in layout space reserved so nothing shifts. Failure: if the connection drops the indicator is removed.

### attachment-preview
- Markup: `<figure>` with the media or file icon and `<figcaption>` (name, type, size). `variant:image`: `<img alt="…">` (the sender's description or the file name) that opens `lightbox`; `variant:file`: icon, name as a download `<a download>`, size ("PDF, 2.3 MB"); `variant:video`: `<video controls preload="metadata" poster>` with a play button over the poster named "Play video {name}", captions when provided.
- `state:uploading`: `progress-bar` (`role="progressbar"` with value, text "Uploading 45%"), a Cancel button named "Cancel upload of {name}". `state:failed`: error icon, "Upload failed", Retry and Remove buttons.
- In the composer each attachment has a Remove button ("Remove {name}"). Compose `file-upload` for picking and drop targets. Limits and types are stated up front ("Up to 25 MB"); rejected files explain why. Reduced motion: progress without animation.

### message-reactions
- Markup: a plain group `<div role="group" aria-label="Reactions">` of `<button aria-pressed>` chips (emoji + count) followed by an "Add reaction" icon button that opens `emoji-picker` in a `popover`. Not a `toolbar`, so Tab reaches each chip (no roving tabindex).
- The chip's name is stable and carries the count: "Thumbs up, 3 reactions, you reacted" via `aria-label` that contains the visible emoji name/count text. `state:default`: unpressed chips; `state:own-reacted`: `aria-pressed="true"` with filled border plus a check glyph (not color alone). `variant:picker-open`: picker open, focus inside.
- Tooltip or press-and-hold shows who reacted (text list in a popover, keyboard reachable, not hover-only). Count changes from others update in place without announcing. Reduced motion: no pop animation.

### emoji-picker
- Markup: a `popover` with a search `input[type=search]`, category `tabs`, and the emoji as an APG `grid` (`role="grid"` with `role="row"`/`gridcell`, one tab stop, arrow keys move by cell, Home/End row start/end, Ctrl+Home/End first/last, Page Up/Down by category); each cell is a button named by the emoji name ("Grinning face").
- `variant:search`: filter by name and keyword; results count in a polite status ("12 results"), "No emoji found" empty text. `variant:skin-tone`: a menu of tone choices (a labelled `radiogroup` or `overflow-menu`) applied to supporting emoji, saved per user. `variant:recent`: a "Recently used" row first, capped, clearable.
- Esc closes and returns focus to the trigger; selecting inserts the emoji and keeps the picker open with Shift held, otherwise closes. Never opens on focus alone. Emoji render with a font fallback and each glyph has its text name for AT. Reduced motion: no skin-tone slide.

### voice-note
- Markup: a `<button>` "Record voice message" in the `composer`; recording UI replaces the input with a timer (`time-display`), a level meter, "Cancel" and "Send" buttons. Recorded notes play with `play-toggle`, `seek-bar` (waveform is decorative; `input[type=range]` carries `aria-valuetext`), `time-display` and `playback-speed` (1x, 1.5x, 2x).
- `state:recording`: permission already granted, "Recording 0:12" (timer updates visually; announced once on start and at stop, not each second), pulsing dot stops under reduced motion; Stop/Cancel/Send reachable, Esc cancels with a confirm if over a few seconds. `state:permission-denied`: "Microphone access is blocked" with steps to allow it and a Retry; text input stays usable.
- `state:recorded`: preview with play, a Delete button and Send; `state:playing`: play-toggle becomes Pause (stable name "Play voice message" + `aria-pressed`, or flip name and label together), progress through `seek-bar`, one note plays at a time and the next unplayed note may auto-continue only if the user opted in. Transcript offered via `transcript-panel` where available.
- The microphone is requested on the click of Record, never on load, and released when recording stops (`MediaRecorder` and `track.stop()`). Maximum length stated.

### mention-autocomplete
- Markup: inside `composer`, the `textarea` is the APG `combobox` (`aria-autocomplete="list"`, `aria-expanded`, `aria-controls`, `aria-activedescendant`) with a `[popover]` `listbox` of people (`avatar`, name, handle, presence as text); options contain no interactive descendants.
- `state:open`: opens after typing `@` plus 0-n characters; Down/Up move the active option, Enter or Tab inserts "@Ana Silva" as an atomic mention, Esc closes and keeps the typed text; the highlighted option is conveyed by `aria-selected` plus a visible mark. Result count in a polite status ("5 suggestions").
- `state:no-match`: "No one matches @xyz" shown as text in the popup, Enter inserts plain text. Never opens on focus alone. The listbox is not opened while IME composition is in progress. Inserted mentions are exposed as text in the message and notify the user (announced to them as a mention, always).

### read-receipts
- Markup: `<p>` or `<span role="status">` under the last own message: `variant:dm`: text "Seen 10:42" (or "Delivered") with a small check glyph, never glyph alone; `variant:group-avatars`: up to 5 small `avatar`s of readers with "+3" and a button "Seen by 8" that opens a `popover` listing readers and times.
- The avatars are decorative (`alt=""`) with the summary text in the button name. Updates change text in place and are not announced individually; the thread's batched status may say "Ana read your message". Privacy: a setting turns receipts off, and the UI states when receipts are hidden ("Read receipts are off").

### message-search
- Markup: `<search>` (or `<form role="search">`) with `input[type=search]` named "Search messages", results as `<ul>` of rows (sender, snippet with `<mark>` matches, conversation, date) that are links jumping to the message in context.
- `state:results`: result count in a status ("24 results for \"budget\""); matches use `<mark>` plus bold, not color alone. `state:no-results`: "No messages match \"budget\"" with suggestions (clear filters, check spelling). `variant:filters`: filter chips as `<button aria-pressed>` or a `popover` form (From, In, Date, Has attachment), active filters shown as removable chips with named remove buttons.
- Keyboard: `/` or Ctrl+K focuses search when no input is focused; Esc clears, then closes; Down moves to results. Search is debounced; loading uses `aria-busy` and a "Searching…" status; errors offer Retry. Deleted and edited messages follow server state.

## 3. Channels

### channel-list
- Markup: `<nav aria-label="Channels">` with grouped `ul`s (`variant:sections`: Starred, Channels, Direct messages as disclosure `<details>` or headings with `aria-expanded` toggles); each row is a link with `#` or lock icon and name.
- `state:unread`: bold name and a "Unread" visually hidden text; `state:mention`: a badge with the count and text ("2 mentions") that outranks plain unread; `variant:private`: lock icon + visually hidden "Private channel"; `variant:muted`: dimmed name (still 4.5:1) and "Muted" text, no badge color.
- Current channel `aria-current="page"`. Keyboard: Tab through, Enter opens; Alt+Up/Down moves to previous/next unread channel (documented). Create-channel and browse are `button-primary` / links at the end of each section.

### channel-header
- Markup: `<header>` with channel name `<h1>` (or `<h2>` in a pane), a topic line, member count button, and actions. Differs from video `creator-header` (public branding and subscribe).
- `variant:topic`: topic text truncated to one line with a "Edit topic" button for permitted users, full text in a `popover`. `variant:members`: avatar stack with a button "12 members" opening `member-list` in `thread-panel` area or `modal`. `variant:call-actions`: "Start call" and "Start video call" icon buttons with stable names, disabled with an explanation when a call is in progress ("Join call").
- Names and topics wrap, never clip at 200% zoom. The header collapses to a back button + name on mobile. RTL: icons that imply direction mirror.

### thread-panel
- Markup: `<aside aria-label="Thread">` (complementary) with a header (title "Thread", Close button), the parent `message-bubble`, a reply count "4 replies" heading and an `ol` of replies, and a `composer`. The reply list is a `role="log"` with the same throttling as `message-thread`.
- `state:open`: panel shown beside (desktop) or over (mobile, as a full-screen route) the thread, focus moves to the panel heading and returns to the "N replies" link on close with Esc. `state:empty`: "No replies yet" with the composer focused.
- Replies also can be shown in the channel ("Also send to #channel" checkbox). Reduced motion: slide becomes a cut.

### member-list
- Markup: `<section aria-label="Members">` with headings (`variant:by-role`: Owners, Admins, Members with counts) and `ul` rows of `avatar`, name, role text and an actions menu; a filter `text-field` for large lists.
- `variant:with-presence`: each row has `presence-indicator` with text; online members sort first. Role is text, not a badge color. Virtualise big lists; the count is stated ("128 members"). Keyboard: Tab through rows; actions are an `overflow-menu` per row ("Actions for Ana"). Remove/ban need `modal` confirmation.

### pinned-messages
- Markup: `<section aria-label="Pinned messages">` with a heading showing the count and a `ul` of compact message cards (sender, time, 2-line text) each with a "Jump to message" link and, for permitted users, an "Unpin" button named with the sender.
- `state:with-items`: ordered newest-pinned first, with "Pinned by {name}"; `state:empty`: `empty-state` "No pinned messages. Pin important messages so everyone can find them." Pin and unpin results go through `toast`; pinning is limited and says so ("Up to 50 pins").

## 4. Calls

### call-controls
- Markup: a plain group `<div role="group" aria-label="Call controls">` of buttons: Microphone, Camera, Share screen, Raise hand, Chat, More, then a separated "Leave" (`button-destructive`). Not `role="toolbar"`, so each control is a Tab stop (or, if using `toolbar`, implement roving tabindex with arrows). Targets 44 px; at least 24 px with spacing in dense desktop (WCAG 2.5.8).
- Toggles keep stable icon-only names with `aria-pressed`: Microphone, Camera, Share screen, Raise hand (pressed means the feature is on or active). Visible text beside the icon states the condition, so color and icon are never the only signal. `state:in-call`: all controls available and the elapsed time shown through `time-display`. `state:muted`: Microphone `aria-pressed="false"`, slashed-mic icon and visible text "Muted". `state:camera-off`: Camera `aria-pressed="false"` with "Camera off" text. `state:sharing`: Share screen `aria-pressed="true"` and a banner "You are sharing your screen" with a "Stop sharing" button.
- `variant:mobile`: bottom bar with the main four controls and a More menu; safe-area insets; Leave stays visible. Shortcuts: M mute, V camera, Esc never leaves. Mute/camera changes are announced once through a polite status ("Microphone muted"). Leave asks confirmation only when sharing or hosting. Reduced motion: no hover grow.

### participant-tile
- Markup: `<figure aria-label="Ana Silva">` with `<video autoplay playsinline muted>` (remote audio plays through a separate element) or an `avatar` when the camera is off; `<figcaption>` shows the name and status text/icons.
- `state:speaking`: 3 px outline plus a "Speaking" text label or sound-wave icon with text for AT, not color alone (and not announced per speaker change; an optional "Active speaker" status is throttled). `state:muted`: mic-off icon with "Muted" text. `state:camera-off`: avatar with name. `state:hand-raised`: hand icon with "Hand raised". `state:poor-connection`: icon with "Poor connection" text and, if needed, video drops to audio first.
- Video has no autoplay audio; local preview is muted and mirrored only visually. Tiles are not tab stops unless they have a menu (pin, mute locally); then a button per tile. Names truncate with `title` fallback and are still in the DOM. Reduced motion: no tile animation on speaker change.

### incoming-call
- Markup: `<dialog role="alertdialog" aria-labelledby aria-describedby>` shown with `showModal()`: title "Ana Silva is calling", description "Video call", `avatar`, `button-primary` "Accept" and `button-destructive` "Decline" (plus "Accept with audio only"). Initial focus goes to the dialog title (an interruption must not be accepted by a stray Enter), then Tab order is Accept, Decline. Focus is trapped and returns to the previously focused element on close (APG `alertdialog`).
- `state:ringing`: ring sound only if enabled and never autoplaying before the user has interacted with the app; a visual pulse stops under reduced motion; times out after ~30 s into missed. `state:missed`: non-modal row/toast "Missed call from Ana, 10:42" with "Call back" and a persisted entry in the thread; the call history keeps it.
- On mobile, native call UI may be used where available. Do-not-disturb suppresses sound and shows a quiet banner. Esc declines.

### device-check
- Markup: a `modal` (or page section) "Check your camera and microphone" with a `<video>` preview (muted), `<select>` for camera, microphone and speaker (`setSinkId` when supported) each with a label, an input-level `<meter>` for the mic with a text value, a "Test speakers" button and the primary "Join call" button.
- `state:preview`: devices listed and preview running; label of each device is shown only after permission. `state:permission-denied`: "Camera and microphone are blocked" with browser-specific steps and a Try again button; joining without devices is allowed ("Join without camera"). `state:no-devices`: "No camera found" / "No microphone found" with a plug-in hint and listen for `devicechange`.
- `getUserMedia` is called only after clicking "Allow" or "Check devices", not on load; on close the tracks are stopped. Preview mirrored visually only. Errors (NotAllowedError, NotFoundError, NotReadableError) map to specific messages. Level meter is also text ("Speaking level: good"), not color alone.

## 5. Support

### support-launcher
- Markup: a fixed `<button aria-expanded aria-controls>` named "Chat with support" (icon plus label, or icon with stable name), placed bottom-inline-end and not covering page content or the cookie banner; safe-area aware.
- `state:closed`: icon (and short label on desktop). `state:unread`: a badge with the count and visually hidden text "2 unread messages" and a polite status once when a new message arrives. `state:open`: pressed/expanded, icon becomes a close chevron with the name staying "Chat with support" (`aria-expanded` carries state). Hidden in print. Reduced motion: no bounce.
- Never opens automatically on focus; proactive greetings are a dismissible bubble that does not move focus.

### support-panel
- Markup: `<section role="dialog" aria-modal="false" aria-label="Support chat">` as a non-modal floating panel (or `modal` on mobile with a trap); contains a header (agent name, status, minimise, close), a `message-thread`, and a `composer`. Esc minimises and returns focus to `support-launcher`. Different from ai `copilot-panel` (assistant in the app); this is customer-to-company chat.
- `state:bot`: a bot is labelled "Automated assistant" in text, quick-reply buttons are a group of `<button>`s, and "Talk to a person" is always available. `state:agent-handoff`: "Connecting you to an agent… about 2 min" in a status, the transcript carries over, and the agent's name appears when joined. `state:offline-form`: out of hours, an inline form (email, message) with labels, validation and a confirmation. `state:csat`: "How was your chat?" with a `radiogroup` of ratings that have text labels (not only stars/emoji) and an optional comment.
- `variant:reply-time`: "Usually replies in a few minutes" as text near the header. Transcript email/download offered at the end. Attachments reuse `attachment-preview`. Focus stays in the composer after send. Messages from the agent use the same throttled log rules.

## 6. Pages

### inbox-page
- Composition: `<main>` with a `<nav aria-label="Conversations">` (search via `message-search`, `conversation-row` list) and the conversation pane (`channel-header` or a compact header, `message-thread`, `composer`). Landmarks: one `main`; the list is a `nav`; the conversation is a `section`.
- `variant:two-pane`: list left (about 360 px), thread right, both independently scrollable; the selected row is `aria-current`. `variant:mobile-list`: the list full screen; opening a row navigates to the thread with a Back button, and focus moves to the thread heading; the browser Back closes the thread.
- `state:no-selection`: `empty-state` "Select a conversation" in the pane. `state:empty`: no conversations, `empty-state` with a "New message" `button-primary`. Reduced motion: pane transitions are cuts.

### workspace-page
- Composition: `<main>` with `channel-list` (left, with workspace switcher and search), the active channel (`channel-header`, `message-thread`, `composer`) and `member-list` or `thread-panel` at the right.
- `variant:three-pane`: channels, thread, members; below a breakpoint the members pane is a `modal` from the header button. `variant:with-thread`: `thread-panel` replaces the members pane; below the breakpoint it is a full-screen route. `pinned-messages` opens from the header.
- Keyboard: Ctrl+K jumps to a channel or person (search), Alt+Up/Down moves between unread channels; skip links to channels, conversation and composer are provided.

### call-page
- Composition: `<main>` with the participant area and `call-controls` at the bottom; a side panel (chat as `thread-panel`, people as `member-list`) opens from the controls; before joining, `device-check`.
- `variant:grid`: equal `participant-tile`s in a responsive grid (up to 9 visible, "+4" overflow button listing the rest). `variant:speaker`: the active speaker large with a filmstrip; a pin keeps a person large. `variant:screen-share`: the shared screen large, participants in a filmstrip, banner "Ana is sharing their screen" and a Stop sharing button for the presenter; the shared surface has a text alternative of the sharer's name.
- Incoming calls use `incoming-call`; the page shows an elapsed timer and connection status (`role="status"`). Leaving returns to the inbox. Reduced motion: layout changes cut instantly.

### support-widget-page
- Composition: a host page plus `support-launcher` and `support-panel`; the page content is unchanged.
- `variant:on-marketing-page`: shown over a public page (for example a `landing-page`), anonymous visitors, pre-chat form for name and email, and the panel avoids covering the cookie banner or footer links. `variant:in-app`: signed-in user with account context ("Chatting as ana@example.com"), previous conversations list, and attachments from the app.
- Mobile: the launcher stays 44 px and the open panel becomes a full-screen `modal`. The widget is lazy loaded after interaction or idle and never blocks the host page's focus order.

### messaging-landing
- Composition (requires `marketing`): `marketing-header`, `hero` (headline, "Get started" `button-primary` and demo, a product screenshot of the inbox with real text), `logo-cloud`, `feature-split` (channels and threads), `feature-split` (calls and voice notes), `feature-grid` (security, search, integrations, mobile), `testimonials`, `pricing-table`, `faq`, `cta-band`, `site-footer`.
- `variant:default`: the sequence above. Product imagery has `alt` text describing the UI, any chat-bubble illustration shows sender by text, and animated demos pause (WCAG 2.2.2) and are static under reduced motion.
