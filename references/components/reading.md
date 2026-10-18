# Reading components & pages — specs

Scope `reading` (enable with `ds.py init --scopes product,reading`; it adds `playback` automatically). Components live in `components/<file>.html` (category **Reading**); full pages in `patterns/<file>.html` (category **Reading Pages**). Reading components compose product components (`button-primary`, `modal`, `popover`, `tabs`, `slider`, `progress-bar`, `sortable-list`, `empty-state`, `skeleton`, `toast`) and the `playback` controls by id (`play-toggle`, `seek-bar`, `time-display`, `playback-speed`, `sleep-timer`, `transcript-panel`) — wrap them, never re-style them.

## Contents
1. Rules for every reading surface
2. Reading surface: reader-viewport, reader-toolbar, reader-settings, reader-toc, reading-progress
3. Annotation: highlight-menu, notes-panel, bookmark-toggle, in-book-search, dictionary-popover
4. Library: book-card, bookshelf
5. Other formats: audiobook-player, comic-viewer, article-reader, tts-control
6. Pages

## 1. Rules for every reading surface
Sources are named as rules, not numbers: EPUB 3.3, EPUB Media Overlays, Readium CSS user settings, CSS `writing-mode` and logical properties, CSS Custom Highlight API, WCAG 2.2 (1.4.8 visual presentation, 1.4.12 text spacing, 1.4.1 use of color), Web Speech API (`speechSynthesis`), ARIA APG.

- **The reader controls the presentation** (WCAG 1.4.8 visual presentation; Readium CSS user settings): font family, size, line height, margins, paragraph and letter spacing, justification, and the paper/sepia/night colors are user settings, applied through CSS custom properties on the viewport and never overridden by book styles. Settings persist per user (and per book when the user chooses).
- **Reader themes are independent of the app theme.** Paper, sepia and night are chosen in `reader-settings` and live in `tokens.json`; the app's light/dark/high-contrast theme only changes the chrome around the page (and the highlight colors, see Tokens). The default is "match the app" until the user picks one.
- **Comfortable measure by default** (WCAG 1.4.8: lines of 80 characters or fewer): `size.reader.measure` (66ch) caps the line in `scroll` and `paged` layouts, centred; `size.reader.leading` (1.6) is the default line height. Text must survive the WCAG 1.4.12 text-spacing overrides (line height 1.5, paragraph spacing 2x, letter spacing 0.12em, word spacing 0.16em) with no clipped or overlapping text, so never fix heights on text blocks.
- **Logical properties and `writing-mode` everywhere.** Layout uses `margin-inline`, `padding-block`, `inset-inline-start` and `text-align: start`, so `dir="rtl"` and `writing-mode: vertical-rl` (CJK, EPUB `page-progression-direction`) flip without a second stylesheet. Page-turn direction, the progress bar fill and the TOC follow the writing direction.
- **Text stays text.** Book content is real selectable DOM text (EPUB XHTML or sanitized HTML), not canvas or images, so screen readers, find, translation and selection work. Images carry the author's `alt`; decorative ones `alt=""`.
- **Paged mode is still navigable by keyboard and AT.** Page turn is Right/Left (mirrored in RTL), PageDown/PageUp or Space/Shift+Space, plus tap zones and visible Previous/Next buttons; the screen-reader reading order is the whole chapter, and the visible page is announced through one polite `role="status"` ("Page 12 of 240", "Chapter 3: The Road"), throttled to once per turn.
- **Highlights use the CSS Custom Highlight API** (`CSS.highlights`, `::highlight()`): ranges are registered as `Highlight` objects without wrapping text in spans, so the DOM and selection are untouched. Where the API is missing, fall back to wrapped `<mark>` elements. Highlight colors carry names ("Yellow", "Green", "Blue", "Pink"), and a highlighted passage also has an underline or `<mark>` semantics plus a text entry in `notes-panel` (WCAG 1.4.1: color is never the only signal).
- **Chrome never traps or hides the text.** Auto-hiding toolbars (reduced after a few seconds) return on tap, any key, pointer move or when anything inside receives focus, and never hide while a control is focused (WCAG 2.2.1/2.4.11: focused controls are not obscured). Reduced motion turns page-turn animation into a cut.
- **Position is a first-class, resumable value.** Progress uses an EPUB CFI (or an equivalent stable locator) saved on every page turn and chapter change, synced across devices, and restored on open with "Continue from page 87?" when another device is ahead; the visible progress is derived from locations, not scroll pixels.
- **Reading time is an estimate and says so**: "About 12 min left" (a stated words-per-minute, user-adjustable), computed from remaining words in the chapter or book.
- **Audio follows playback.** Audiobooks and TTS reuse `js/lib/media.js` and the `playback` keyboard map (Space/K play-pause, J/L 10 s, Left/Right 5 s, M, C, F), Media Session metadata and the single polite live region. Nothing speaks on its own (WCAG 1.4.2).
- **Speech is feature-detected** (Web Speech API): `speechSynthesis.getVoices()` can be empty or arrive late (`voiceschanged`), so `tts-control` shows "Text-to-speech isn't available on this device" rather than a dead button, and falls back to the reader's own screen reader.
- **Touch targets** are at least 44 px; page-turn zones never cover links or selection handles, and system gestures (edge swipe back) are not used for page turns.
- **Tokens.** `color.reader.paper|sepia|night.bg|fg|link|selection`, `color.reader.highlight.yellow|green|blue|pink`, `size.reader.measure` (66ch), `size.reader.leading` (1.6). Contrast pairs (all themes): each `fg` on `bg` 4.5, each `link` on `bg` 4.5, each `fg` on `selection` 4.5, and `paper.fg` on each highlight 4.5. `themes/dark.json` overrides only the four highlight colors; `themes/high-contrast.json` maps paper to pure black on white.
- **vs.** `article-reader` is a reading mode for long-form articles with reader controls; `prose` (product typography) styles authored content in a page and `blog-article` (marketing) is a public post page, and neither has reader settings or progress. `comic-viewer` shows paged image sequences with fit and zoom; `lightbox` is a modal for opening one image from a gallery. `audiobook-player` composes `playback` controls; it does not redefine them.

## 2. Reading surface

### reader-viewport
- Markup: `<section aria-label="Book text" tabindex="0">` (a labelled `section` is already a region) containing the chapter as an `<article>`; chapter changes move focus to the chapter `<h1>` (`tabindex="-1"`).
- `variant:paged`: CSS columns or paginated slices, one page at a time, page turn by keys, tap zones and buttons; no horizontal scrollbar. `variant:scroll`: continuous vertical scroll with the measure cap; position saved on scroll end.
- `variant:two-column`: two pages side by side from a width threshold (about 900 px) and single column below; a spread never splits a figure.
- `variant:rtl`: `dir="rtl"`, page turn and progress mirror. `variant:vertical-writing`: `writing-mode: vertical-rl`, lines flow right to left, paging moves along the inline axis and scrolling is horizontal; `text-orientation: mixed`, upright Latin runs only when the book requests it.
- `state:loading`: `skeleton` lines, `aria-busy="true"`, status "Loading chapter 3"; failure shows "Couldn't load this chapter" with a Retry button and keeps the toolbar.
- Keyboard: Right/Left (mirrored in RTL), PageDown/PageUp, Space/Shift+Space, Home/End for chapter start/end; shortcuts never fire while typing in `in-book-search` or a note field. Reduced motion: no slide or curl animation.

### reader-toolbar
- Markup: a `<header>` with a Back link, book title, and a group of icon buttons (Contents, Search, Settings, Bookmark) with stable names; a bottom bar with `reading-progress`. Plain group of buttons, no `role="toolbar"`, so Tab reaches each (no roving tabindex).
- `state:visible`: shown. `state:auto-hidden`: hidden after inactivity with `inert` removed on reveal; revealing happens on tap, any key, pointer move and focus-within, and the toolbar is never hidden while it holds focus or a menu from it is open.
- `variant:mobile`: top bar collapses to Back, Contents and a More menu (`popover` menu); safe-area insets respected; bottom bar holds progress.
- Reduced motion: fade or instant. RTL: Back arrow mirrors and button order follows `dir`.

### reader-settings
- Markup: a `modal` (`dialog`) or a bottom sheet on mobile, titled "Reading settings", with `tabs`-style sections or one scroll of `fieldset`s; changes apply live with a Reset to defaults button.
- `variant:typography`: font family (radio group: Publisher default, Serif, Sans, Dyslexia-friendly font), size (`slider` with a visible value, 80-300%), line height, paragraph and letter spacing, margins, justify toggle (a `<button aria-pressed>` or switch with the constant label "Justify text").
- `variant:theme`: radio group of Paper, Sepia, Night (each a labelled swatch showing "Aa" and the name as text, current one checked) plus "Match app theme" and a brightness slider for night.
- `variant:layout`: radio group Paged / Scroll, columns (auto / one / two), margin size, and for CJK a writing-direction choice. Settings save per user and optionally per book (Readium CSS user settings).
- Keyboard: Esc closes, focus returns to the Settings button; changes announced through the polite status only for non-visual effects ("Night theme"). Reduced motion: live preview without transitions.

### reader-toc
- Markup: `<nav aria-label="Contents">` with an `ol`; nested chapters are nested `ol`s inside disclosure (`<details>`/`summary`), links are real `<a>`/buttons that navigate the viewport.
- `state:current-chapter`: the current item has `aria-current="location"` and a visible marker (bar plus bold, not color alone); it is scrolled into view when the panel opens.
- `variant:nested`: parts, chapters and sections with expand/collapse; the branch containing the current chapter is open by default.
- Keyboard: Tab through links, Enter navigates and closes the panel on mobile, focus then moves to the chapter heading. RTL: indentation uses `padding-inline-start`.

### reading-progress
- Markup: `progress-bar` semantics (`<progress>` or `role="progressbar"` with `aria-valuenow`) for display variants; `variant:jump-slider` is a native `input[type=range]` (use `disabled`, not `aria-disabled`) with `aria-valuetext` such as "Chapter 4, 38 percent, page 112 of 295".
- `variant:percent`: "38%". `variant:location`: "Page 112 of 295" (or "Location 1,204 of 3,180" for reflowable books where pages are not stable). `variant:time-left`: "About 2 h 10 min left in book" (see estimate rule). Users cycle between them with a button whose name is "Progress display, percent" (current value in the name).
- `variant:jump-slider`: dragging previews the target chapter title in a tooltip; releasing moves, with an Undo "Back to page 112" `toast` so a stray drag is recoverable.
- Keyboard: Arrow keys step one page, PageUp/PageDown one chapter, Home/End ends. The percentage text is not a live region; position changes are covered by the viewport's one throttled status. Fill direction follows writing direction.

## 3. Annotation

### highlight-menu
- Markup: a `[popover]` `menu` (APG menu button pattern without a button: it opens on text selection finishing, never on focus alone) anchored to the selection; items are `menuitem` buttons: four color swatches named "Highlight yellow", "Highlight green", "Highlight blue", "Highlight pink", then "Add note", "Define", "Copy", "Share quote". Roving tabindex, arrows, Esc closes and returns the selection.
- `state:open`: menu shown with a visible focus ring; the selection remains highlighted. Opening happens via mouse/touch selection end or the keyboard shortcut (Shift+F10 or the Menu key) after selecting text with Shift+Arrows, so keyboard users get the same path.
- `variant:colors-labelled`: each swatch shows a visible name next to or under the color (a tooltip alone is not enough on touch), and an existing highlight is shown selected with text "Yellow, tap to remove". Names match `notes-panel` entries (WCAG 1.4.1).
- `variant:note`: "Add note" opens an inline `textarea` field with Save and Cancel, label "Note", focus moves in, Esc cancels. `variant:define`: hands the selected word to `dictionary-popover`.
- Highlights are registered with `CSS.highlights.set(name, new Highlight(...ranges))` and styled by `::highlight(reader-yellow)` using `color.reader.highlight.*` with the reader's fg; non-supporting browsers fall back to `<mark>`. Failure: "Couldn't save highlight" with Retry (kept locally first, synced later).

### notes-panel
- Markup: `<aside aria-label="Notes and highlights">` (complementary) with `tabs` (Highlights, Notes) or a filter; each entry is an `li` in a `ul` with the quote, color name as text, chapter and date, a "Go to passage" link and an Actions menu (Edit, Delete). Not a `listbox`.
- `variant:highlights`: grouped by chapter, filterable by color name. `variant:notes`: entries that have a note, note text first.
- `variant:export`: an Export button opening a menu (Markdown, Plain text, Copy to clipboard); the export contains quote, note, color name, chapter and location. A `toast` confirms "Exported 14 highlights".
- `state:empty`: `empty-state` "No highlights yet. Select text to highlight it." Deleting offers Undo via `toast`. Keyboard: Tab to the entry's link then its menu; Delete asks for no hidden shortcut.

### bookmark-toggle
- Markup: `<button type="button" aria-pressed>` with a stable accessible name "Bookmark this page" (WCAG 2.5.3: icon-only, so the name never flips; `aria-pressed` carries the state), outline vs filled icon plus the shape difference, not only fill color.
- `state:unset`: `aria-pressed="false"`. `state:set`: `aria-pressed="true"`; the polite status announces "Bookmark added" or "Bookmark removed" and a ribbon marker appears in the viewport corner with visually-hidden text "Bookmarked".
- Keyboard: Enter/Space on the button; optional shortcut B is documented and off while typing. Failure: reverts and shows "Couldn't save bookmark".

### in-book-search
- Markup: `<search>` landmark with `<input type="search">` labelled "Search in book", a Search button and a result count status; results are an `ol` of links with the snippet (match in `<mark>`) and chapter/location.
- `state:results`: "12 results" in a polite status (debounced; submit with Enter, not per keystroke); the current result is `aria-current="true"`, matches are also highlighted in the viewport with a non-color marker (underline).
- `state:no-results`: "No results for “dragon”" with a suggestion to check spelling or search all books; the status announces the same.
- Keyboard: Enter runs search and jumps to the first result, F3 or Next/Previous buttons move between matches, Esc closes and returns focus to the viewport at the active match.

### dictionary-popover
- Markup: `[popover]` with `role="dialog"` and an accessible name "Definition: {word}", anchored to the selected word; Close button, Esc closes, focus returns to the selection.
- `state:found`: headword, pronunciation (with an audio button named "Play pronunciation of {word}", user-initiated), part of speech, numbered definitions and a source link; "Add to vocabulary" is a normal button.
- `state:not-found`: "No definition found for “{word}”" with "Search the web" and "Copy" actions; offline states say "Dictionary unavailable offline".
- Content is language-tagged (`lang` on the headword and definitions). Reduced motion: no zoom-in transition.

## 4. Library

### book-card
- Markup: `<article>` with a cover `<img>` (alt is empty when the title is shown beside it, else "Cover of {title}"), title as a link `<h3><a>`, author, and a progress readout; the whole card is not a second link (one link target, `::after` stretched).
- `variant:grid`: cover-led card with title and author below. `variant:list`: row with cover, title, author, series, progress and actions.
- `state:in-progress`: `progress-bar` plus text "38% read, 2 h left"; the link goes to the saved position. `state:finished`: a check icon with the text "Finished".
- `variant:format-badges`: badges with visible text "Ebook", "Audiobook", "Comic", "PDF" (never icon-only or color-only); a card with several formats lists all of them.
- Overflow actions (Mark as finished, Remove, Download) sit in a menu button with name "Actions for {title}". Missing covers show a generated cover with the title as text. Cover images have explicit aspect ratio (2:3) and lazy loading below the first row.

### bookshelf
- Markup: `<section aria-labelledby>` per shelf with an `<h2>` and a `ul` of `book-card`; a horizontally scrolling shelf is a focusable scroll region with "Show more" and a "See all" link, not an infinite carousel.
- `variant:collections`: user collections (To read, Favorites, custom) as headers with counts; add/remove from the card menu; reorder collections with `sortable-list` (move up/down buttons).
- `variant:sort`: a menu button "Sort: Recently read" with options Title, Author, Recently read, Date added, Progress; the choice persists and is announced ("Sorted by title").
- `state:empty`: `empty-state` "Your shelf is empty" with a Browse action. Loading uses `skeleton` cards.

## 5. Other formats

### audiobook-player
- Markup: `<section aria-label="Audiobook player">` composing `play-toggle`, a `seek-bar` for the chapter (or the whole book via a toggle), `time-display`, skip back 15 s and forward 30 s buttons (names state the interval), `playback-speed`, `sleep-timer`, previous/next chapter buttons and a chapters `reader-toc`-style list. It keeps the `playback` keyboard map (Space/K, J/L 10 s, Left/Right 5 s, M); the skip buttons are the touch equivalents and may use different intervals than J/L, stated in their names.
- `variant:chapters`: a chapters `ul` with durations as text; the current chapter has `aria-current="true"` and a "Playing" label; chapter change is announced once.
- `variant:follow-along`: the text pane highlights the current sentence from EPUB Media Overlays (SMIL `par` elements linking text ids to audio clips); the highlight is paired with an underline, the pane auto-scrolls and has a "Follow along" pause (the constant label with `aria-pressed`, WCAG 2.2.2); a manual scroll pauses following and shows "Jump to current" button.
- `state:sleep-timer`: the `sleep-timer` countdown is visible as text ("Sleep in 14 min"), the end-of-chapter option is offered, and the final 30 s fade is gradual; "Extend" is available as a button. Media Session metadata (title, author, cover) and lock-screen skip actions are set by `js/lib/media.js`.
- Failure: "Couldn't load audio" with Retry; position syncs with the ebook edition of the same title where both are owned.

### comic-viewer
- Markup: `<section aria-label="Comic viewer">` with the page image(s) in a focusable stage, Previous/Next buttons, a page `input[type=range]` and a zoom control. Each page `<img>` has `alt` (author description, or "Page 12 of 180" at minimum); accessible comics provide panel text or a per-page transcript toggle.
- `variant:single`: one page at a time. `variant:spread`: two facing pages from a width threshold, cover alone on the first screen.
- `variant:rtl-manga`: `dir="rtl"`, Left arrow goes to the next page, the progress fills from the right, spreads order right-then-left; the toggle "Reading direction: right to left" is user-controllable.
- `variant:webtoon-scroll`: continuous vertical strip with lazy loading, reserved image heights (no layout shift) and "Next chapter" at the end. `variant:fit-width`: fit to width, height or original, selected from a menu button with the current value in its name.
- `state:zoomed`: pinch, double-click or +/- buttons; zoomed pages pan with arrow keys and drag, a visible "Reset zoom" button restores, and page-turn gestures are disabled while zoomed. Not a `lightbox`: no backdrop modal, the viewer is the page.
- Reduced motion: page turn is a cut. Preload the next two pages; errors show "Couldn't load page 12" with Retry.

### article-reader
- Markup: `<article>` with `<h1>`, byline, date, estimated reading time as text ("6 min read"), optional `<progress>`, and body in a measure-capped column using `size.reader.measure` and the user's reader settings (a compact `reader-settings`). Distinct from `prose` (product typography) and `blog-article` (marketing page).
- `variant:default`: clean extracted content (headings, figures with captions, links underlined) with a source link back to the original.
- `variant:reading-time`: reading time and a "time left" readout that updates as the user scrolls (not live-announced); the estimate states its assumed speed in the details.
- `variant:with-tts`: shows `tts-control` pinned at the bottom; the paragraph being read is outlined (not color alone) and scrolled into view.
- Failure: if extraction fails, show the original link with "Couldn't load reader view"; `lang` and `dir` come from the source.

### tts-control
- Markup: `<div role="group" aria-label="Read aloud">` with a Play/Pause button (name flips "Read aloud" / "Pause reading", no `aria-pressed`), Stop, Previous/Next paragraph, a `<select>` for voice and a native `input[type=range]` for rate with `aria-valuetext` ("1.25 times"). Built on `speechSynthesis`/`SpeechSynthesisUtterance`, one utterance per paragraph to keep controls responsive.
- `state:speaking`: the play button reads "Pause reading", status "Reading paragraph 4 of 20" (once per paragraph, not per word). `state:paused`: "Resume reading"; paused utterances are resumed or re-queued after the tab regains focus.
- `variant:voice-rate`: voice list from `getVoices()` filtered to the content `lang`, rate 0.5x-3x, pitch optional, choices persisted. Empty list: "No voices installed for this language".
- `variant:word-highlight`: uses `boundary` events (where supported) to mark the current word with the Custom Highlight API and a non-color underline; where events are not provided, highlight at paragraph level. It is a visual aid only, not announced.
- Nothing starts without a user action (WCAG 1.4.2); Esc or the Stop button always cancels, `speechSynthesis.cancel()` runs on navigation. Screen-reader users are told that their own screen reader may be better ("Read aloud is for sighted and low-vision readers; your screen reader can read this page directly").

## 6. Pages

### library-page
- Composition: app shell with `reading-progress`-aware "Continue reading" row, `bookshelf` shelves, a search field and a "Add books" action; `<h1>` "Library".
- `variant:shelves`: Reading now, Want to read, Finished, collections. `variant:continue-reading`: the most recent book large with cover, progress, time left and a Continue button (`button-primary`), then shelves. `state:empty`: `empty-state` "Your library is empty" with Browse the store and Import actions.
- Mobile: bottom nav, shelves scroll with snap and a visible "See all"; grid becomes two columns.

### book-detail-page
- Composition: `<main>` with cover, `<h1>` title, author links, rating, format switch (Ebook / Audiobook / Comic as `tabs` or links), primary action (`button-primary`: "Read sample", "Buy", "Continue"), description, details (publisher, pages, language, duration, narrator) and "More in this series" as `book-card` list. Emits `Book` JSON-LD with `workExample` per format.
- `variant:ebook`: sample and file size, supported reading modes. `variant:audiobook`: narrator, length, a sample using `audiobook-player` (user-started). `variant:series`: ordered series list with owned/unowned status in text and "Read in order" guidance.
- Mobile: cover and actions stack, the primary action is sticky at the bottom without covering the description.

### reader-page
- Composition: a full-screen `<main>` with `reader-toolbar`, `reader-viewport` (or `comic-viewer` or `audiobook-player`), `reading-progress`, and dialogs for `reader-settings`, `reader-toc`, `in-book-search` and `notes-panel`; selection opens `highlight-menu`.
- `variant:paged` and `variant:scroll`: the two reflow modes from `reader-viewport`. `variant:comic`: `comic-viewer`, toolbar with page slider and reading direction. `variant:audiobook`: `audiobook-player` with optional follow-along pane.
- Mobile: chrome auto-hides (see `reader-toolbar`), panels open as bottom sheets, the page area uses the whole viewport minus safe areas. Last position is saved on `visibilitychange` and `pagehide`.

### read-later-page
- Composition: heading "Read later", add-by-URL field, a `ul` of saved articles (title, source, reading time as text, saved date, excerpt) with Archive, Delete (Undo `toast`) and tags; opens in `article-reader`.
- `variant:list`: sort by date, source or reading time, filter by tag, and an Archived view. `state:empty`: `empty-state` "Nothing saved yet" explaining how to save an article, with a link to the browser extension or share-sheet help.
- Mobile: swipe actions have button equivalents in an item menu.

### reading-landing
- Composition (marketing scope, enabled alongside it): `hero` (with a short user-started reader preview showing paper/sepia/night, no autoplay audio), `feature-split` (customizable reading and highlights, audiobooks with follow-along, comics and manga), `testimonials`, `pricing-table`, `faq`, `cta-band`, `site-footer`, in that order.
- `variant:default`: the sections above in order. The theme preview uses real text at the three reader themes with visible theme names, so it works without color perception.
