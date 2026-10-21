# Social components & pages — specs

Scope `social` (enable with `ds init --scopes product,social`; it has no required scopes, add `marketing` for `social-landing`). Components live in `components/<file>.html` (category **Social**); full pages in `patterns/<file>.html` (category **Social Pages**). Social components compose product components — `post-card`, `feed`, `comment-thread`, `avatar`, `composer`, `modal`, `menu-button`, `carousel`, `button-primary`, `button-secondary`, `button-destructive`, `badge`, `tabs`, `tooltip`, `textarea`, `radio-group`, `switch`, `alert-dialog`, `toast`, `empty-state`, `skeleton` — wrap them, never re-style them.

## Contents
1. Rules for every social surface
2. Profiles and people: profile-header, follow-button, user-row, people-suggestions
3. Posts: reaction-bar, post-composer, share-sheet
4. Stories: stories-tray, story-viewer
5. Safety: report-dialog, block-mute-menu
6. Pages

## 1. Rules for every social surface
Sources: WCAG 2.2 (2.2.2 Pause, Stop, Hide; 2.5.3 Label in Name; 2.5.8 Target Size; 1.4.1 Use of Color), the ARIA Authoring Practices `feed` pattern, the Web Share API, and platform safety guidance (report and block always within reach).

- **Report and block are reachable from every post and profile.** Every `post-card` and every `profile-header` carries a "More actions" `menu-button` with Report, Mute and Block (`block-mute-menu`). Safety actions are never hidden behind a hover, a long press only, or a settings page.
- **Safety flows never shame.** Block, mute and report confirmations use neutral copy that states what will happen ("They won't be able to see your posts or find your profile"); no guilt, urgency or "Are you sure you want to abandon…" wording. Cancel and Confirm have equal visual weight and plain names.
- **Blocked and private states have explicit copy.** A blocked profile says "You blocked this account" with an "Unblock" action; if the viewer is blocked, the copy says only what is necessary and does not reveal more than the platform's policy. A private profile says "This account is private" and offers "Request to follow". The state is text, never only a lock icon or blur.
- **Auto-advance and motion must be pausable (WCAG 2.2.2).** Stories and carousels that move for more than 5 seconds provide a pause control, pause on hold, focus and hover, and do not auto-advance under `prefers-reduced-motion: reduce`.
- **Toggle pattern follows Label in Name (WCAG 2.5.3).** Text-labelled toggles (`follow-button`) flip the visible label and the accessible name together ("Follow" / "Following") and do not use `aria-pressed`, as video `subscribe-button` and music `artist-header` do. Icon-only toggles (like, save) keep a stable name ("Like", "Save") and flip `aria-pressed`. Never a flipping label with `aria-pressed`.
- **State is never color alone (WCAG 1.4.1).** Unseen story, liked, saved, verified, requested and muted states always have text or an icon with a name besides color or a ring.
- **Feeds follow the APG `feed` pattern.** Posts are `article` elements in a `role="feed"` with `aria-busy` while loading more, `aria-labelledby`, `aria-posinset` and `aria-setsize` where the total is known (`-1` otherwise); Page Up/Page Down move between articles. Infinite scroll always has a "Load more" button fallback and keeps the footer reachable.
- **Target size (WCAG 2.5.8).** Every action, including icon buttons in the reaction bar and the story close button, is at least 24 by 24 CSS px with spacing, 44 px on touch; counts are text beside the button.
- **Counts are text, announced once.** "128 likes" is visible text next to the button; updates after a tap are announced through one polite live region ("Liked. 129 likes"), never by `aria-live` on the count. Abbreviated counts ("1.2K") expose the full number in visually-hidden text.
- **Share with a fallback.** `navigator.share` runs only from a user gesture, after `navigator.canShare` feature detection; when unavailable or rejected (`AbortError` is not an error) the sheet offers Copy link plus explicit targets.
- **User content is untrusted.** Names, bios and posts are escaped; `rel="ugc nofollow noopener"` on user links; mentions and hashtags are links with text; images need author-provided `alt` with a prompt to add it.
- **Language and direction.** User content carries `lang` and `dir="auto"`; layout uses logical properties so profiles and feeds mirror in RTL.
- **Tokens**: composes product tokens only (`color.text.*`, `color.bg.surface`, `color.feedback.<tone>.*`, `color.action.*`); no scope template.
- **vs.** `post-composer` is the social post form with media, limit and audience; product `composer` is the generic message-style input it composes. `reaction-bar` is the like, reply, share and save row on a feed post; messaging `message-reactions` are emoji chips on a chat message. `profile-header` is a person's profile with follow, counts and safety actions; video `creator-header` is a channel's branding with subscribe, and messaging `channel-header` is a chat room title bar. `user-row` is one person in a list; `people-suggestions` is a curated block of them.

## 2. Profiles and people

### profile-header
- Markup: `<header>` with `avatar` (large, with `alt` or decorative when the name follows), the display name in the page `<h1>`, handle as text (`@ana`), bio, links, counts as a `<dl>` or inline list ("1,204 followers", "310 following", "86 posts"; the first two are links to `followers-page`), a `follow-button` or "Edit profile", and a "More actions" `menu-button` for Report, Mute and Block.
- `variant:own`: "Edit profile" and "Share profile" replace follow; the safety menu is replaced by settings. `variant:other`: `follow-button`, "Message" (when messaging is enabled) and the safety menu.
- `variant:verified`: a badge with the visible text "Verified" or an icon with an accessible name, and the heading's accessible name includes it ("Ana Ruiz, Verified account") through visually-hidden text, never a blue tick alone.
- `state:private`: copy "This account is private. Follow to see their posts." plus "Request to follow"; counts of posts may show but the content area is replaced by that message, not by blurred posts.
- `state:blocked`: "You blocked this account" with an "Unblock" button; follow, message and counts are removed, the safety menu stays so the viewer can unblock or report.
- Keyboard: Tab order is name, follow, menu, then counts. Reduced motion: no banner parallax. RTL: logical alignment. Failure: counts that fail to load show "—" with a retry, not 0.

### follow-button
- Markup: `<button type="button">` (wrap `button-primary` for Follow, `button-secondary` for Following). The visible label and accessible name flip together: "Follow" then "Following"; no `aria-pressed`. The person is identified by context with `aria-describedby` pointing to the name element; if the name is extended ("Follow Ana Ruiz"), it must still contain the visible text ("Follow").
- `state:follow`: primary style, label "Follow". `state:following`: secondary style, label "Following" with a check icon; activating it never unfollows on a single hover or click-through accident: it opens a `menu-button` menu (Unfollow, Mute, Add to close friends) or a confirm for private accounts ("Unfollow Ana? You'll need to request again").
- `state:requested`: label "Requested" as text with a clock icon; activating it offers "Cancel request". `state:follows-you`: a separate text badge "Follows you" beside the button, not in the button name and not a color change.
- Never swap the label on hover ("Following" to "Unfollow") because hover has no keyboard or touch equivalent. Optimistic update with rollback and a toast ("Couldn't follow. Try again.") on failure; the result is announced through one polite status ("Following Ana Ruiz").
- Keyboard: Enter and Space. Target at least 44 px on touch. RTL: icon is placed with logical margin.

### user-row
- Markup: `<li>` in a `<ul>`: `avatar`, name link, handle text, optional one-line context ("Followed by Sam and 3 others") and a `follow-button`. The row name link is the primary target; the button is a separate control, never nested in the link.
- `variant:with-follow`: the `follow-button` sits at the inline end; at narrow widths the context line wraps and the button stays visible. `variant:compact`: smaller avatar and no bio for dense lists (mentions, likers dialogs); the target size is still 24 px or more.
- Verified and private states follow `profile-header` (text or named icon). Keyboard: Tab goes name link then button. Loading: `skeleton`. RTL: logical alignment. Failure: row-level inline retry on follow failure.

### people-suggestions
- Markup: a labelled `<section>` with `<h2>` "Suggested for you" containing a `ul` of `user-row` or cards with a visible reason ("Followed by Sam", "Based on people you follow"), a `follow-button` and a Dismiss button ("Dismiss Ana Ruiz"). A "Why am I seeing this?" link explains the signals.
- `variant:carousel`: wraps product `carousel` with Previous and Next buttons, scroll-snap, no auto-advance, and a visible "See all" link; every card is reachable by keyboard without the arrows. `variant:list`: a plain vertical list of `user-row variant:with-follow`. When placed inside a `feed` (as on `home-feed-page`) the block is an `<article aria-label="Suggested people">` counted in `aria-setsize` and `aria-posinset`, not a bare section; outside a feed it is the labelled `<section>`.
- `state:empty`: `empty-state` "No suggestions right now" with "Find people" linking to `explore-page`; never an empty gap. Dismissing removes the item and moves focus to the next one, announcing "Suggestion dismissed".
- Failure: the section hides itself rather than showing an error. Reduced motion: scroll without smooth animation. Never pre-follow anyone or use contact-import data without explicit consent.

## 3. Posts

### reaction-bar
- Markup: a plain group (`<div role="group" aria-label="Post actions">`) of buttons, not a toolbar, so no roving tabindex is required: Like, Reply, Share and Save, plus counts as text beside each button.
- `state:default`: all off. `state:liked`: Like is `aria-pressed="true"` with a filled heart and the count increments; the name is stable ("Like"). `state:saved`: Save is `aria-pressed="true"` with a filled icon; the name is stable ("Save"). Reply is a link or button to the thread; Share opens `share-sheet`.
- `variant:counts`: counts are visible text ("128 likes" or the number next to the icon with a visually-hidden unit), abbreviated above 10,000 with the exact value in hidden text; the count is not inside the button name unless it is visible there.
- Optimistic toggles with rollback, announced once through a polite status ("Liked"). Double-tap-to-like is an extra, never the only way. Keyboard: Tab through four buttons; Enter and Space activate. Target 44 px on touch.
- Differs from messaging `message-reactions` (emoji chips on a chat message). RTL: order mirrors. Failure: toast and rollback.

### post-composer
- Markup: a `<form>` wrapping product `composer` with a labelled `textarea` ("Post text"), an attach-media button, an audience control and a Post button (`button-primary`). Works without JS by posting the form.
- `state:empty`: placeholder "What's happening?" is not the label (a real label exists, visible or visually hidden); Post is enabled with a validation message on empty submit rather than silently disabled (or disabled with the reason as text).
- `state:with-media`: thumbnails in a list with an "Add description" field per image (alt text), Remove buttons named "Remove photo 1" and a progress indicator for uploads (`progress-bar`).
- `state:over-limit`: a character counter as text ("12 characters over the limit"), exposed with `aria-describedby`; the count is announced politely at thresholds (for example at 20 remaining and at over-limit), not per keystroke. The overflow text is marked with a non-color cue, and Post is blocked with the reason as an error.
- `variant:audience`: a `radio-group` in a `menu-button` or modal ("Everyone", "Followers", "Close friends") with a description of each; the current audience is visible text on the trigger ("Audience: Followers") and its accessible name includes that text.
- Keyboard: Ctrl or Cmd+Enter posts as an optional shortcut, documented; Esc with a draft asks to save or discard in an `alert-dialog` with neutral copy. Drafts are kept on accidental close. Failure: keep the text and offer retry.

### share-sheet
- Markup: `<dialog>` (wrap `modal`, or a bottom sheet on mobile) titled "Share post" with the post URL in a read-only `text-field`, a "Copy link" button, and targets as links (Messages, Email, and configured networks) that open in a new context with `rel="noopener"`.
- `variant:web-share`: where `navigator.canShare({url})` is true, the Share button calls `navigator.share({title, text, url})` straight from the click handler and the native sheet replaces the dialog; a user cancel (`AbortError`) is silent.
- `variant:fallback-copy-link`: when Web Share is unavailable, the dialog is shown with "Copy link" using `navigator.clipboard.writeText`; success is announced ("Link copied") through a polite status and the button text stays "Copy link" with the confirmation next to it. If clipboard permission fails, the input text is pre-selected for manual copy.
- Keyboard: focus moves to the dialog heading or first control; Esc closes and returns focus to the Share button. Private accounts' posts show "Only followers can see this post" before sharing a link. RTL: URL stays `dir="ltr"`.

## 4. Stories

### stories-tray
- Markup: a `<ul>` (or `carousel`) of items, each a link or button with the avatar inside a ring and the name below ("Ana Ruiz"). The accessible name carries the state: "Ana Ruiz, unseen story" or "Ana Ruiz, seen"; the first item is "Your story" with an "Add story" affordance named separately.
- `state:unseen`: gradient or accent ring at 3:1 against the background plus a visible text cue (a small "New" badge or the name in bold with the hidden state text), not color alone. `state:seen`: muted ring, name in regular weight, and the state text in the name. Unseen items sort first.
- Scrolling: arrows on pointer devices as buttons, scroll-snap, no auto-scroll. Keyboard: Tab through items; Enter opens `story-viewer`. Loading: `skeleton` circles. RTL: starts at the inline start. Failure: tray hides with no error.

### story-viewer
- Markup: a full-screen `<dialog>` with a progress area (one segment per story item in an `ol`, the current one `aria-current="step"`), the author `user-row variant:compact`, the media with `alt` or a caption, a Pause/Play button, Close, Previous and Next buttons, and the optional reply form. Segment progress also has text: "Story 2 of 5" visible or visually hidden, not segment color only.
- `state:playing`: items advance after 5 seconds (images) or at the video end. Under WCAG 2.2.2 a visible Pause button is always present; auto-advance also pauses on pointer hold (press and hold), on hover, and while any control or the reply field has focus, and resumes on release or blur.
- `state:paused`: the control flips its visible label and accessible name together from "Pause" to "Play" (icon plus text, no `aria-pressed`) and the current segment stops filling. `state:reduced-motion`: `prefers-reduced-motion: reduce` means no auto-advance and no progress animation; the user moves with Next and Previous, and video does not autoplay.
- `variant:reply`: a `<form>` with a labelled field ("Reply to Ana") and Send, plus quick emoji buttons; focusing the field pauses the story; sent state is announced ("Reply sent").
- Keyboard: Left and Right arrows (previous and next item) and Space (toggle pause) are shortcuts that apply only when focus is on the dialog itself or the media or progress area; they never fire in the reply field (arrows move the caret, Space types) or on a focused button, where native Enter and Space activation of Pause, Previous, Next and Close is left alone so nothing double-fires. Esc closes and returns focus to the tray item, Tab is trapped inside the dialog. Tap zones on touch are supplements to the buttons, never the only way. Captions are available for video and are on by default when the user has enabled captions in the product.
- Safety: the viewer's header has the "More actions" menu (Report, Mute, Block) reachable with the keyboard. Failure: a media error shows "Couldn't load this story" with a Next button.

## 5. Safety

### report-dialog
- Markup: `<dialog>` (wrap `modal`) with `<h2>` "Report post" (or account, or comment) and a stepped flow. Opened from the `block-mute-menu` or a post's "More actions" menu, and from every profile, post and comment.
- `state:reasons`: a `fieldset` with `<legend>` "Why are you reporting this?" and radios (Spam, Harassment, Hate, Self-harm, Misinformation, Something else), each with a one-line explanation; "Something else" reveals an optional labelled textarea. Next is enabled once a reason is chosen (or shows an error "Select a reason"). Self-harm shows support resources before or after submit.
- `state:submitted`: "Thanks, we've received your report" with what happens next (review timeline stated honestly, no promises about outcome), a "Done" button and, where relevant, the block and mute options. Focus moves to the confirmation heading; announced politely.
- `variant:with-block`: after the report, an unchecked-by-default offer "Also block @ana" as a `checkbox` or a button; never pre-checked, never required, and skipping has equal prominence. Copy never discourages reporting or uses guilt.
- Keyboard: Esc cancels at any step with no data loss warning needed before the first choice; focus returns to the opener. Reports are confidential ("They won't be told who reported them"). Failure: keep the choices and offer retry; reports are never silently dropped.

### block-mute-menu
- Markup: `menu-button` with a `[popover]` `role="menu"` of `menuitem`s: Mute, Block, Report; the trigger is named "More actions for Ana Ruiz". The menu is available on `profile-header`, `post-card`, comments and `story-viewer`. Opening is by activation only, never on focus (WCAG 3.2.1).
- `variant:mute`: "Mute @ana" explains "You won't see their posts. They won't be told." and lists granularity (posts, stories) as `menuitemcheckbox` items in a menu or `switch` controls in a follow-up dialog. Unmute is available in the same place and in settings. `variant:block`: "Block @ana" explains the effects in plain words.
- `state:confirm`: an `alert-dialog` with the title "Block Ana Ruiz?", a description of the effects, and two equal buttons "Block" (`button-destructive`) and "Cancel". Copy is neutral: no "Are you sure you want to lose a friend?" Confirmation is shown for block, not for mute (reversible and low-risk). The result is a toast with "Undo" and a status announcement ("Blocked Ana Ruiz").
- Keyboard: Arrow keys move through items, Home and End jump, Esc closes and returns focus to the trigger, type-ahead optional. Failure: toast with retry. Blocking also removes the follow relationship in both directions and hides the account's content on every surface at once.

## 6. Pages

### profile-page
- Composition: `<main>` with the `profile-header` (`<h1>`), a `tabs` row (Posts, Media, Replies, Likes where allowed) and a `feed` of `post-card`s or a media grid. Each post and the header carry the `block-mute-menu`.
- `variant:posts`: the feed in chronological order with `reaction-bar` on each. `variant:media`: a grid of images and video poster links, each with `alt` and an aria label of the post; opens `lightbox` or the post detail.
- `state:private`: the header copy and "Request to follow" replace the content area; tabs are hidden. `state:empty`: `empty-state` "No posts yet" (own profile adds "Create your first post" with `post-composer`).
- Mobile: header stacks, counts in a row, tabs scroll horizontally with visible scroll cues, the safety menu remains in the header.

### home-feed-page
- Composition: `<main>` with `<h1>` (visually hidden "Home"), `stories-tray`, `post-composer`, a tab group (Following, For you) and the `feed` of `post-card`s with `reaction-bar`; `people-suggestions` inserted after the first screenful as an `<article aria-label="Suggested people">` inside the feed (APG `feed` children must be articles), counted in `aria-setsize` and `aria-posinset` like any post.
- `variant:following`: chronological posts from followed accounts, with a "New posts" button instead of automatically shifting the list. `variant:for-you`: ranked posts with a "Why am I seeing this?" per post and a control to see less of a topic; the tab's name states the order.
- `state:loading`: `skeleton` post cards and `aria-busy="true"` on the feed; the feed keeps existing posts while loading more; a "Load more" button is the fallback to infinite scroll; a polite status announces "10 more posts loaded".
- Mobile: single column, the composer collapses to a button opening a full-screen `post-composer`, tab bar remains reachable, no scroll hijack.

### post-detail-page
- Composition: `<main>` with a back link, the `post-card` (expanded, `<h1>` is the author and a short excerpt), `reaction-bar`, a reply `post-composer` (compact) and a `comment-thread` of replies with nested levels and "Show more replies" buttons.
- `variant:with-replies`: threaded replies sorted with a Sort control (Top, Newest), each reply with its own `reaction-bar` and `block-mute-menu`; a deleted or blocked parent shows "This post is unavailable" without breaking the thread.
- Mobile: composer is a sticky bar above the safe area; nested indentation is capped at three levels with "Continue thread" links.

### followers-page
- Composition: `<main>` with `<h1>` ("Ana Ruiz" with "Followers" in a `tabs` row of Followers and Following), a `search-input` ("Search followers") and a `ul` of `user-row variant:with-follow`.
- `variant:followers` and `variant:following`: the same layout, tab selected with `aria-selected`; in Following, the button reads "Following" and unfollow goes through a menu or confirm; a "Remove follower" action lives in each follower row's menu. Long lists use "Load more" with a status.
- `state:empty`: `empty-state` ("No followers yet" or "Not following anyone yet") with a link to `explore-page`. Private accounts you do not follow show the private copy instead of the list.
- Mobile: full-width rows, 44 px targets, sticky search.

### explore-page
- Composition: `<main>` with `<h1>` "Explore", a `search-input` with suggestions, `tabs` (For you, Trending, People, Topics), trending topics as a `ol` of links with post counts as text, and `people-suggestions` and posts below.
- `variant:trending`: ranked topics ("1. #design, 12K posts") and trending posts in a `feed`; ranking is explained ("Trending in your region") and rank is text, not only position.
- `variant:search`: query results grouped by People, Posts and Topics with a count and a polite status ("24 results for design"); recent searches are listed with a Clear button; the empty result is an `empty-state` with suggestions.
- Mobile: search is sticky at the top, tabs scroll horizontally, results are one column.

### social-landing
- Composition (marketing scope, enabled alongside it): `marketing-header`, `hero` (a short product preview with a muted looping demo that has a pause control), `feature-split` (communities, stories, safety), `testimonials`, `pricing-table` when there is a paid tier, `faq` (including privacy and safety), `cta-band`, `site-footer`, in that order. Safety and moderation tools are a named feature, not fine print.
- `variant:default`: the sections above in order; the preview shows sample content only and never real users' data. Mobile: sections stack with a sticky "Join" button that does not cover the footer links.
