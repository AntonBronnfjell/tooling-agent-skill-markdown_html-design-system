# AI & chat components — specs

Scope `ai` (enable with `ds.py init --scopes product,ai` or add `"ai"` to `ds.config.json → scopes`). Components live in `components/<file>.html` (category **AI & Chat**); full layouts in `patterns/<file>.html` (category **AI Patterns**). AI components compose product components — button, icon-button, copy-button, badge, popover, tooltip, details/accordion, tabs, drawer, meter, alert, avatar, `composer` — never restyle them; add AI tokens (`--color-ai-*`) only where content must read as AI.

Practice distilled from Vercel AI Elements, assistant-ui, CopilotKit, PatternFly Chatbot, Carbon for AI, Cloudscape GenAI patterns, OpenAI Apps SDK UI guidelines, MCP Apps (SEP-1865) and Microsoft's HAX guidelines (cited as **HAX G1–G18**). See `sources.md`.

## Contents
1. Rules for every AI surface
2. Conversation: conversation, chat-message, streaming-response, generating-indicator, code-block
3. Model transparency: reasoning, agent-plan, tool-call, sources, inline-citation, ai-label, ai-disclaimer
4. Control: approval-card, message-actions, response-feedback
5. Input: prompt-input, model-picker, context-chips, suggestion-chips, voice-input, usage-meter
6. Containers & navigation: ai-empty-state, conversation-list, artifact-panel, app-widget, ai-status-banner
7. Pages

## 1. Rules for every AI surface

**Accessibility of streaming (the hard part)**
- The conversation is `role="log"` (implicit `aria-live="polite"`), but **the streaming message body is never itself the announcement target** — token-by-token DOM writes either re-announce everything (`aria-atomic="true"`) or get dropped by screen readers. Instead:
  - A single shared visually-hidden announcer (`js/lib/live-region.js`, polite) receives **whole sentences or paragraphs**, flushed on sentence end (`.`, `?`, `!`, line break, end of list item/code block) and no more often than `--motion-ai-announce-throttle` (≈1.5 s). Code blocks and tables are announced as "Code block, Python, 14 lines" / "Table, 4 columns", not read out.
  - Mark the streaming `<article>` with `aria-busy="true"`; flip to `false` on completion and announce **"Response complete"** (or "Response stopped" / "Response failed") once.
  - Offer a user setting *Read responses aloud as they stream: on / status only*. Default: sentence announcements on. *(Uncertain — practitioners disagree; some recommend status-only announcements plus reading the finished message. Test with NVDA, JAWS, VoiceOver.)*
- **Focus stays in the prompt input** after sending and while streaming. Never move focus into the response. New content never steals focus or scroll position.
- **Stop is always reachable**: while generating, the submit button becomes **Stop** (same position, `aria-label="Stop generating"`), and **Esc** in the prompt input (or anywhere in the conversation, when no overlay is open) stops. Stopping keeps the partial output, labelled "Stopped".
- Processing is perceivable without vision: `generating-indicator` is `role="status"` with text ("Generating a response"), not just an animation.
- Keyboard: everything in a message (actions, citations, code copy, tool disclosures) is reachable in DOM order; message action toolbars are always in the tab order (visible on focus, not hover-only).

**Labelling AI content (HAX G1, G2, G11; Carbon for AI)**
- Anything produced by a model is identifiable as AI by text — sender name ("Assistant", product name) or an `ai-label` — not only by color, gradient or sparkle icon.
- Set expectations: what the assistant can do and how well (empty state + `ai-disclaimer`); explain on demand (`ai-label` popover, `reasoning`, `sources`).
- When a user edits AI-filled content, it stops being labelled AI and offers **Revert to AI** (Carbon pattern).

**Citations & grounding**
- Citations are real `<a href>` links to the actual source, never decorative numbers. Every inline number maps to an item in `sources`. If a source can't be opened (private doc, deleted), show it as text with "Unavailable", don't fake a link. Links to external sites state the domain.

**Motion**
- Shimmer, caret blink, pulsing avatars and gradients are decorative and **stop under `prefers-reduced-motion`** (static "Generating…" text, solid caret or none). Streaming text should append without animating layout; don't animate height of the growing message. Auto-scroll uses `behavior: "auto"` under reduced motion.

**Latency states (Cloudscape)**
- Two phases: **processing** (nothing to show yet → `generating-indicator`) and **generating** (content arriving → `streaming-response` with caret). Don't show a loading state for waits under ~1 s (`--motion-ai-loading-delay`) to avoid flicker. After ~8 s (`--motion-ai-long-wait`) add elapsed time and a reason if known ("Searching 12 sources… 14 s"). Copy pattern: "Generating a response", "Searching the web", "Reading report.pdf" — verb + object, no trailing punctuation.

**Errors & retry**
- Every failure says what happened and what to do: rate limit (with reset time), network (retry; draft kept), server/model error (retry, maybe another model), content filtered (rephrase; don't shame), context too long (start new chat / summarize), partial response (Continue). Failed sends keep the user's text in the input. See `ai-status-banner`.

**Human control (HAX G8, G9, G16, G17)**
- Easy dismissal and correction: stop, regenerate, edit prompt, revert. Consequential actions by an agent require `approval-card` with clear scope and reversibility. Provide global controls (memory on/off, data-use settings) and link to them from the disclaimer.

**Content safety**
- Render model output as **untrusted**: markdown → sanitized HTML (no raw HTML/script, no `javascript:` URLs, `rel="noopener noreferrer"` + `target` policy on links, images from allowlisted hosts or proxied). Tool/app UIs run in sandboxed iframes (`app-widget`). Never auto-execute generated code; Run is an explicit action, sandboxed.
- Show filtered/blocked content as a neutral notice, not an error splash.

**Privacy**
- Show what context is sent (`context-chips`: files, page, selection) before sending; let users remove it. Disclose data use and retention in the first-run disclaimer and feedback form ("Your conversation will be shared with reviewers"). Don't put prompts or content in analytics hooks (`data-track` carries action names only).

**Layout & i18n**
- Conversation column max `--size-ai-message-max-inline` (~48rem) for readable measure; prompt input pinned to the bottom of the conversation region with `scroll-padding-bottom` equal to its height so focused items aren't hidden. Logical properties throughout: user messages align to inline-end (mirror in RTL). Model output may be in a different language than the UI — set `lang` on the message if known, and `dir="auto"` on user and assistant content.

## 2. Conversation

### conversation
- Anatomy: scroll container `<section role="log" aria-label="Conversation with Assistant">` → optional "Load earlier messages" button / sentinel at the top → `<ol>` of turns (or a sequence of `<article>`) → optional day dividers (`<li role="separator">` with text, or an `<h2 class="sr-only">` per day) → bottom sentinel → floating **Jump to latest** button.
- **Scroll anchoring:** stick to bottom while the user is at the bottom (IntersectionObserver on the bottom sentinel, not scroll math on every token). When the user scrolls up, stop auto-scrolling, show "Jump to latest" (with "New response" badge if content arrived), and keep their position — use `overflow-anchor: auto` on content and `overflow-anchor: none` on the sentinel; when prepending history, preserve `scrollTop` by delta. Sending a message always scrolls to the new user message.
- Jump to latest: `<button>` with visible text or `aria-label="Jump to latest message"`; activating scrolls to bottom and does **not** move focus into the log (focus stays where it was, typically the input). Hidden (not just transparent) when at bottom.
- States: default, scrolled-up with new content, loading history (skeleton rows at top, `aria-busy` on the log), streaming, error loading history (inline retry).
- Keyboard: the log scroll region is focusable (`tabindex="0"`) only if it has no focusable children; PageUp/PageDown work natively. Optional: Alt+↑/↓ moves between messages (document if added).
- Tokens: `--size-ai-message-max-inline`, `--color-bg-canvas`, `--space-*` for turn gap.
- Pitfalls: `aria-live="assertive"` on the log; `scroll-behavior: smooth` on every token (janky, motion-sick); auto-scrolling while the user is reading; virtualizing without keeping messages in DOM for find-in-page (if virtualized, document the tradeoff).

### chat-message
- Anatomy: `<article aria-labelledby="msg-12-author">` → header (avatar `alt=""` since name is adjacent, author name as a heading — `<h3>` or `sr-only` heading per turn helps screen-reader heading navigation —, `<time datetime>`) → content (user: plain text with preserved line breaks; assistant: `streaming-response`) → attachments (`context-chips`, read-only) → footer (`message-actions`, status).
- Variants: **user** (bubble at inline-end, `--color-ai-user-bubble-bg`, `--radius-ai-bubble`), **assistant** (full-width, no bubble, optional AI label/avatar), **system** (centered small muted text: "Model changed to X", "Conversation shared" — not a bubble), **error** (feedback-danger tokens + icon + text + Retry). With avatar / compact (no avatars, tighter gaps).
- States: pending-send (muted + "Sending…"), failed-send ("Not sent. Retry" button, text preserved), streaming, complete, stopped.
- Pitfalls: distinguishing speakers by color/side only; rendering user text as markdown/HTML (XSS + surprising formatting); timestamps without `datetime`.

### streaming-response
- Anatomy: `.prose` container rendered from sanitized markdown → blocks (p, lists, tables in a scrollable labelled region, `code-block`, images with alt from model or "Generated image") → caret (`::after` pseudo, `--color-ai-caret`, `aria-hidden`) at the end while streaming.
- Behavior: render incrementally but **commit block-by-block**: keep the unfinished block (partial markdown like an open code fence or half table) in a provisional state so layout doesn't flip; highlight code once the fence closes. Reserve no fake height. Links become clickable only once complete (avoid clicking half-written URLs).
- States: streaming (`aria-busy="true"`, caret), complete (caret removed, announce "Response complete"), stopped (keep text, append muted "Stopped" note + Continue/Regenerate), interrupted (network drop: "Response interrupted" + Retry/Continue).
- A11y: see §1 announcer rules. Headings inside model output start at the level below the message heading (shift `#` → `h4` if message heading is `h3`).
- Tokens: typography body/code, `--color-ai-caret`, `--motion-ai-caret-blink`.
- Pitfalls: `innerHTML` with unsanitized output; re-rendering the whole message each token (kills selection and screen-reader position — append/patch instead); blinking caret under reduced motion.

### generating-indicator
- Anatomy: `<div role="status">` → optional AI avatar/glyph → label text ("Thinking", "Generating a response", "Searching the web") → optional elapsed time → optional Stop (usually lives in prompt-input).
- Variants: shimmer-text (label with a moving gradient highlight via `background-clip: text`; base and highlight both ≥4.5:1 — `--color-ai-shimmer-base` / `-highlight`), dots (three dots, `aria-hidden`, label sr-only), avatar-pulse.
- States: processing (no content yet), generating (inline with streaming content — usually only the caret, indicator hidden), long-wait ("Still working… 24 s", with what it's doing if known), reduced-motion (static text).
- Appears after `--motion-ai-loading-delay`; status text announced once per change, not per second.
- Pitfalls: spinner with no text; ticking elapsed seconds inside the live region (announce only at changes in phase).

### code-block
- Anatomy: `<figure>` → `<figcaption>` (language + filename) and toolbar (Copy — reuse `copy-button`; optional Run / Apply / Insert / Download; wrap toggle) → `<pre tabindex="0" aria-label="Python code">` → `<code>` → optional output region (`<output>` or `<pre>` labelled "Output") for run results.
- States: streaming (no highlight, Copy disabled until fence closes — or copies partial with label "Copy partial"), copied ("Copied" for ~2 s, announced via live region), running (`aria-busy`, Stop), run-error (output in danger style), long-scroll (max block size then scroll; focusable region), wrapped.
- Run executes only on explicit click, in a sandbox, and states where ("Runs in browser sandbox"). Diff variant (+/- lines) uses text markers, not color only.
- Tokens: `typography.code`, `--color-bg-subtle`, `--radius-md`.
- Pitfalls: Copy that copies line numbers; horizontal scroll without a focusable region; highlighting libraries re-tokenizing the whole block each token.

## 3. Model transparency

### reasoning
- Anatomy: `<details>` → `<summary>` ("Thinking…" while active; "Thought for 12 s" after; chevron) → reasoning summary text (muted, smaller).
- Behavior: open while thinking (optional), auto-collapse when the answer starts streaming — but **never collapse if the user opened it manually**. Do not announce reasoning text through the live region; announce "Thinking" and "Done thinking" only.
- Variants: with duration, summary-only (when the provider only exposes summaries — label it "Reasoning summary", don't imply it's the full chain).
- Pitfalls: presenting reasoning as authoritative explanation (it may not reflect the real computation — keep `ai-label` popover as the explanation surface); huge unscrolled reasoning dumps.

### agent-plan
- Anatomy: header ("Plan · 3 of 5 done", optional collapse) → `<ol>` of steps → each `<li>`: status icon (`aria-hidden`) + **status text** (sr-only or visible: "Done", "In progress", "Failed", "Skipped") + title + optional details/substeps (`<details>`) + duration.
- States per step: pending, in-progress (spinner/shimmer, `aria-current="step"`), done, failed (reason + Retry step), skipped (reason). Collapsed-summary shows only the current step.
- Announce step transitions via the shared announcer, throttled ("Step 3 of 5: Updating tests").
- Plans proposed **before** execution can be editable (reorder/remove/approve) → hand off to `approval-card`.
- Tokens: `--color-ai-tool-*` status colors.

### tool-call
- Anatomy: `<details>` card → `<summary>`: tool icon, human-readable name ("Searched the web", "Read calendar"), key argument preview ("query: 'Q3 revenue'"), status badge (text), duration → body: **Input** (`<dl>` or pretty JSON in `code-block`), **Output** (rendered result, truncated with "Show all"), error message.
- States: pending (queued), running (`aria-busy`, shimmer on name, Cancel if supported), success, error (danger badge, error text, Retry), cancelled; streaming-input (arguments arriving — AI Elements calls these `input-streaming` → `input-available` → `output-available` / `output-error`), approval-required (renders `approval-card` inside).
- Collapsed by default when successful; expanded on error. Raw JSON is secondary — show a readable summary first.
- Pitfalls: leaking secrets/tokens in displayed inputs (mask fields marked sensitive); status by color only; dozens of cards for one turn (group consecutive calls: "Used 6 tools" disclosure).

### sources
- Anatomy: `<details>` → `<summary>` "Used 5 sources" (+ stacked favicons, `aria-hidden`) → `<ol>` (numbers match inline citations) → each item: `<a href>` title, domain, optional date and snippet.
- Variants: collapsed count, list, cards (horizontal scroll row → focusable labelled region), unavailable source (text, "Unavailable" badge).
- Pitfalls: numbering mismatch with inline citations; favicons as the only identifier; linking to search results instead of the cited page.

### inline-citation
- Anatomy: `<sup><a href="#src-2" aria-label="Source 2: Annual report 2025 (example.com)" aria-describedby="cite-2-preview">2</a></sup>` → preview card (popover `hint`/hover-card: title, domain, quoted passage). Clicking goes to the source (external) or scrolls to the source list entry — pick one per product and document it.
- Variants: numbered, multiple (`[1, 3]` as separate links), quote-highlight (the supporting span gets a subtle underline/background and the citation label).
- Keyboard: Tab focuses the link and shows the preview; Esc hides the preview. Target ≥24×24 via padding (superscript numbers are tiny).
- Pitfalls: preview only on hover; numbers that are not links.

### ai-label
- Anatomy: `<button class="ai-label" aria-label="AI-generated — show details" popovertarget="ai-explain-1">` with visible "AI" text (and optional sparkle `aria-hidden`) → explainability popover (toggletip: opens on click, stays until dismissed) with sections: **Overview** (what was generated and from what), **Supporting details** (model name/version, confidence if meaningful, date), **Artifacts & resources** (sources, data used), **Actions** (View details, Give feedback, Revert to AI / Turn off suggestions). Section order follows Carbon's popover template.
- Variants: default (on containers: upper inline-end corner, not flush), inline (sized to adjacent text), with-text ("AI generated"), sizes sm/md aligned to icon/control sizes; edited-revert (after user edits, label is replaced by a "Revert to AI" button with an undo icon and accessible name).
- AI containers may use `--color-ai-surface`, `--color-ai-border`, `--shadow-ai-glow` — subtle; removed in forced-colors/high-contrast (border remains).
- Pitfalls: label that isn't interactive but looks like it (be a button, or be plain text — not a span with hover); hiding confidence numbers behind the gradient; labelling everything AI (label at the scope that's actually AI: field, row, section).

### ai-disclaimer
- Variants: **footnote** — one short `<p class="small">` under the prompt input: "AI can make mistakes. Check important info." + link ("Learn more" with accessible name "Learn more about AI accuracy"); **inline-notice** — callout in a page/region where AI output is consumed (reports); **first-run-dialog** — `<dialog>` on first use: what it does, limits, data use & retention, link to settings; one primary "Got it", persisted.
- Pitfalls: walls of legal text in the composer; dismissible footnote (it's not a banner); color-only disclaimers.

## 4. Control

### approval-card
- Anatomy: `<form>` region with heading ("Approve action?") → **what**: plain-language action ("Send email to 3 recipients", "Delete 14 files in /reports") → **details**: target, parameters (diff/preview, recipients list, amount) → **scope** `<fieldset>` radio: "Only this time" (default) / "For this conversation" / "Always for this tool" (enterprise) → **reversibility** text ("Can be undone for 30 days" / "Cannot be undone") → actions: **Approve** (primary; danger style when irreversible), **Deny** (secondary, equal size), **Edit** (opens editable fields inline, then "Approve with changes") → optional deny reason ("Tell the assistant what to do instead").
- States: awaiting (the run is paused; generating indicator says "Waiting for your approval"; focus is **not** stolen — announce "Approval needed" politely and make the card reachable via a "Review request" link in the status area), approved (collapsed record: "Approved by you · 10:42 · once"), denied (record + reason), expired ("Request expired" — actions disabled, Re-run), batch (approve/deny each or all).
- Keyboard: standard form; Enter does **not** approve implicitly (approve button is not the form's default when irreversible — use `type="button"` + explicit click). Irreversible approvals may require typing a confirmation or a second click with changed label.
- Tokens: `--color-ai-approval-bg|border`, `--color-ai-approval-destructive-border`.
- Pitfalls: vague verbs ("Proceed?"); default-checked "Always allow"; approve button where deny is visually de-emphasized; auto-approving after a timeout. (Patterns: AI Elements Confirmation, CopilotKit human-in-the-loop, MCP Apps host approval of UI-initiated tool calls.)

### message-actions
- Anatomy: `<div role="toolbar" aria-label="Message actions" aria-orientation="horizontal">` with icon-buttons (each has `aria-label` + tooltip): Copy, Regenerate (assistant) / Edit (user), Good response / Bad response (`aria-pressed` toggles, mutually exclusive), Read aloud (optional), Share, More (menu: Branch from here, Report). Branch nav: `‹ 2 / 3 ›` = buttons "Previous response"/"Next response" + text "Response 2 of 3" (`aria-live` off; the change of content announces via the message).
- Roving tabindex per APG toolbar (one Tab stop; ←/→ move). Visible on hover **and** focus-within, always visible on touch and on the latest message.
- States: copied (icon swap + "Copied" announced), regenerating (Regenerate disabled, message becomes streaming; old version kept as branch), feedback-up/down (pressed; down opens `response-feedback`).
- Edit (user message): turns the bubble into an inline textarea with Cancel / Send (Esc cancels); sending creates a new branch.
- Pitfalls: hover-only toolbars; thumbs that only change color; regenerate that destroys the previous answer.

### response-feedback
- Anatomy: inline panel under the message (or `<dialog>` variant) → heading "What went wrong?" (or "What did you like?") → `<fieldset>` of reason toggles/checkboxes (Inaccurate, Not helpful, Didn't follow instructions, Harmful or unsafe, Out of date, Other) → optional `<textarea>` comment → data notice ("Submitting shares this conversation with our team to improve the product. Learn more") → Submit / Cancel.
- States: reasons-open, submitted (replace with "Thanks for your feedback" `role="status"`, focus moves to it or back to the thumbs button), with-comment, error (keep input).
- HAX G15 (granular feedback): reasons are specific; feedback is optional and never blocks continuing.
- Pitfalls: modal for every thumbs-down; sharing data without saying so.

## 5. Input

### prompt-input
- **Builds on `composer` (forms.md)** — reuse its auto-grow textarea, attachment input, error-with-retry and counter behaviors. AI-specific differences:
  - **Enter sends, Shift+Enter inserts a newline** (chat convention — this inverts composer's default; document it near the field via `aria-describedby` hint, and respect IME composition: don't send while `isComposing`).
  - Submit ↔ **Stop** swap while generating (same slot, same size, `aria-label` changes; Esc also stops). The textarea stays editable while generating so users can draft the next prompt; submit is disabled until stopped/done (or queues — say so).
  - Toolbar row: attach (`input[type=file]`), tools/mode menu (menu-button: Web search, Deep research, Image — as `menuitemcheckbox`), `model-picker`, `voice-input`, `usage-meter` (context variant), submit/stop.
  - Context row above the textarea: `context-chips`.
  - Label: visible or `sr-only` `<label>` ("Message Assistant"); placeholder is an example, not the label.
- States: empty (submit disabled with `aria-disabled` + tooltip "Type a message"), filled, generating, with attachments (uploading blocks send until done, or sends when ready — show it), rate-limited (input enabled for drafting, send disabled, `ai-status-banner` above with reset time), disabled (e.g. read-only shared chat — explain why).
- Height: grows to `--size-ai-prompt-max-block`, then scrolls. Pinned at bottom; on mobile respects the virtual keyboard (`interactive-widget=resizes-content` viewport meta, or `visualViewport`) and safe-area insets.
- Pitfalls: losing the draft on error or navigation (persist per conversation); sending on Enter during IME composition; stop button that moves.

### model-picker
- Native `<select>` (customizable select where supported) labelled "Model", or a button + popover listbox (APG listbox) when options need descriptions ("Fast · good for everyday tasks", relative cost). Unavailable options are `disabled` with reason text ("Requires Pro"). Changing model mid-conversation inserts a `system` message ("Switched to X").
- Pitfalls: model names only (users don't know them) — add one-line purpose; hidden cost differences.

### context-chips
- Anatomy: `<ul aria-label="Attached context">` → chip `<li>`: icon/thumbnail (`alt` for images), name (truncate middle: "quarterly-re…port.pdf", full name in `title` and accessible name), meta (size, pages, "Selection, 120 words", "Current page"), remove `<button aria-label="Remove quarterly-report.pdf">`.
- States: uploading (`<progress>` inside chip, Cancel), error ("Too large — max 20 MB", danger style, Retry/Remove), removable, overflow ("+3 more" disclosure). Page-context/selection chips can be toggled off (`aria-pressed`) rather than removed.
- Announce add/remove/upload-complete via the shared announcer. After removing, focus moves to the next chip or the input.

### suggestion-chips
- Anatomy: `<ul aria-label="Suggested prompts">` of `<button>`s (chips, `--radius-ai-chip`) or starter cards (icon + title + one-line description).
- Behavior: follow-up chips **send** immediately; starter cards **insert** into the input for editing (pick per product; label behavior consistently). Chips disappear once the user sends something else; a horizontal scroll row is a focusable labelled region with visible overflow cue.
- Keep to ~3–4 follow-ups, ≤ ~60 characters each.

### voice-input
- Anatomy: mic toggle `<button aria-pressed="false" aria-label="Start voice input">` → listening state (label "Stop voice input", level meter `aria-hidden`, "Listening" `role="status"`), live transcript written into the textarea (editable before send), optional push-to-talk (hold Space when button focused; always also a click toggle).
- States: idle, listening, processing ("Transcribing"), permission-denied ("Microphone blocked. Allow access in browser settings" + help link), error/unsupported (button hidden or disabled with reason).
- Privacy: clear recording indicator while mic is open; stop on blur/route change.

### usage-meter
- Native `<meter min max low high optimum value>` + text ("62% of context used · 81k / 128k tokens", "$0.42 this conversation", "18 of 25 messages left today"). Details popover breaks down usage (system, files, conversation). Thresholds: near-limit (warning text + suggestion "Start a new chat to keep responses accurate"), over-limit (danger + action).
- Compact variant in prompt-input: small ring/bar + percentage; accessible name includes the full text.
- Pitfalls: color-only thresholds; ticking counts in a live region.

## 6. Containers & navigation

### ai-empty-state
- Anatomy: `<section aria-labelledby>` → AI glyph (decorative, may use `--gradient-ai`) → `<h1>`/`<h2>` greeting ("How can I help with your projects?") → capabilities & limits list (HAX G1/G2: "Can: summarize docs, draft emails. Can't: access your email.") → `suggestion-chips` starter cards → `ai-disclaimer` footnote.
- Variants: greeting-with-starters, capabilities, scoped-assistant (copilot in an app: starters derived from current page), first-run (adds data-use notice).
- Focus lands in the prompt input, not on starters.

### conversation-list
- Anatomy: `<nav aria-label="Chat history">` → New chat button → search (`search-input`) → groups with headings (Pinned, Today, Yesterday, Previous 7 days, Older) → `<ul>` of `<a href aria-current="page">` titles (truncate, full title in accessible name) → per-item More menu (Rename, Pin, Share, Delete).
- States: default, current, renaming (inline-edit; Enter saves, Esc cancels, focus returns to the link), deleting (`alert-dialog` confirm or undo toast), empty ("No conversations yet"), loading (skeletons), search no-results.
- Mobile: lives in a drawer opened from the header.
- Pitfalls: items as buttons (use links so they open in new tabs/are shareable); titles auto-generated mid-stream causing jumpy list.

### artifact-panel
- Anatomy: `<aside aria-labelledby="artifact-title">` → header (title, type badge, version selector "v3 of 3", Copy, Download, Open full screen, Close) → `tabs` (Preview / Code) → body (`code-block`, rendered doc, or sandboxed `<iframe sandbox title="Preview of …">`).
- Variants: side-panel (resizable split; splitter is `role="separator"` with `aria-valuenow`, arrow keys resize), fullscreen (`<dialog>`), mobile-sheet (drawer/bottom-sheet), closed-chip (in the message: a card "Quarterly report — Document · Open" that reopens the panel).
- States: streaming (content builds in place; `aria-busy`), version-history (previous versions readonly with "Restore"), error.
- Opening the panel doesn't steal focus from the input when it opens automatically; opening by user click moves focus to the panel heading; Close returns focus to the trigger.

### app-widget (MCP Apps / Apps SDK shell)
- Anatomy: `<section aria-label="<App name>: <widget title>">` → attribution header (app icon, app name, "Interactive app" label) → `<iframe sandbox="allow-scripts allow-forms" title="…">` (no `allow-same-origin` with untrusted content; CSP limited to the domains the resource declares — MCP Apps `connectDomains`/`resourceDomains`/`frameDomains`; host must not allow undeclared domains) → host controls (Expand to fullscreen, Close PiP).
- Display modes (MCP Apps: `inline` | `fullscreen` | `pip`; Apps SDK adds inline carousel):
  - **inline-card:** single purpose; ≤ 2 actions; no nested scrolling, no deep navigation, no duplicated composer. Height is content-driven (iframe resizes on the app's size-changed notification), with a max before "Expand".
  - **carousel:** 3–8 similar items, each ≤ 3 lines of text and ≤ 1 CTA; prev/next buttons + "2 of 6"; follows `carousel` spec.
  - **fullscreen:** `<dialog>`; the host composer remains available; Esc/close returns to the chat and focus to the trigger.
  - **pip:** floating, non-modal, for ongoing sessions; closes automatically when the session ends; always has a close button.
- Theming: pass the host's theme and tokens to the app (MCP Apps host context `theme` + `styles` CSS variables such as `--color-background-primary`, `--color-text-primary`, `--font-sans`); map our semantic tokens onto those names in the host adapter. Apps should inherit system fonts; brand accents only on logo/primary button (Apps SDK guidance).
- States: loading (skeleton at the declared/last height), error ("Couldn't load <App>" + Retry, text fallback of the tool result), awaiting-approval (UI-initiated tool calls may require host approval → `approval-card` outside the iframe, never inside it — the iframe can't be trusted to render consent).
- Pitfalls: letting the iframe draw its own fake "approve" buttons for host-level permissions; unlabelled iframes; focus traps inside inline widgets.

### ai-status-banner
- Placement: directly above the prompt input (affects sending) or inline in the failed message (affects that turn).
- Variants & copy: **rate-limited** — "You've reached the message limit. Resets at 3:00 PM." (+ `<time>`, optional Upgrade), `role="status"`; **network-error** — "Connection lost. Your message wasn't sent." + Retry, `role="alert"`; **server-error** — "The model is unavailable right now." + Retry / Try another model; **content-filtered** — "This request can't be completed under our usage policy." + Learn more (neutral tone); **context-limit** — "This conversation is too long." + Start new chat / Summarize and continue; **partial-response** — "The response was cut off." + Continue.
- States: retrying (`aria-busy`, button disabled "Retrying…"), auto-retry with backoff shows countdown text (not announced each second).
- Pitfalls: generic "Something went wrong"; assertive alerts for non-urgent limits; losing the user's prompt.

## 7. Pages (patterns/)

Each page is a realistic composition with real copy, demoed in light/dark, mobile/desktop, with keyboard walkthrough documented (send → stop with Esc → jump to latest → message actions → citations).

| Page | Composition |
|---|---|
| **chat-app** | `app-shell` variant: header (title, model-picker, share, user menu) → `conversation-list` in a side nav (drawer on mobile) → `<main>`: `ai-empty-state` or `conversation` (chat-message ×n, streaming-response, reasoning, tool-call, sources, message-actions, suggestion-chips) → sticky `prompt-input` (context-chips, usage-meter) + `ai-disclaimer` footnote → optional `artifact-panel` as a resizable inline-end split. Landmarks: header, nav "Chat history", main, aside "Artifact". |
| **copilot-panel** | Existing product screen (e.g. dashboard or form) + `<aside aria-label="Copilot">` docked at inline-end (`--size-ai-copilot-panel-inline`), toggled by a header button (`aria-expanded`, shortcut documented e.g. ⌘I). Panel: header (title, new chat, close) → `ai-empty-state` (scoped starters from page) → conversation → prompt-input with page-context and selection chips. AI-filled fields in the page get `ai-label` + Revert to AI; agent edits to the page go through `approval-card` or an inline diff with Apply/Discard. Variants: docked (page reflows, non-modal), overlay (floating, non-modal, `popover`), mobile-sheet (modal `<dialog>`). |
| **agent-run** | Header: run title, status badge, elapsed time, cost (`usage-meter`), Stop / Resume / Re-run. Main: `agent-plan` summary → timeline `<ol>` of steps (reasoning, tool-call cards, approval-card when paused, artifacts) with timestamps and durations; step-detail in an inline-end `<aside>` (inputs, outputs, logs in `code-block`, errors). Filters (status, tool) and "Jump to current step". States: running (throttled step announcements), awaiting-approval (banner + "Review request" link), completed (summary + outputs), failed (failed step expanded, Retry from step). |

## Sources

Fetched and read:
- Vercel AI Elements: https://elements.ai-sdk.dev/ (component inventory; Tool states input-streaming / input-available / output-available / output-error; Confirmation, Reasoning, Chain of Thought, Plan, Task, Queue, Sources, Inline Citation, Context, Model Selector, Shimmer, Artifact, Speech Input)
- Carbon for AI overview: https://carbondesignsystem.com/guidelines/carbon-for-ai/ (light/glow/gradient treatment, revert to AI, explainability)
- Carbon AI label usage: https://carbondesignsystem.com/components/ai-label/usage/ (variants, sizes, placement, explainability popover sections, revert; formerly "AI slug")
- Cloudscape GenAI loading states: https://cloudscape.design/patterns/genai/genai-loading-states/ (processing vs generating, avoid <1s loaders, "Generating a response" copy pattern)
- OpenAI Apps SDK UI guidelines: https://developers.openai.com/apps-sdk/concepts/ui-guidelines (inline card <=2 actions, no nested scroll; carousel 3-8 items; fullscreen with system composer; PiP; system fonts/colors)
- MCP Apps SEP-1865: https://modelcontextprotocol.net/seps/1865-mcp-apps-interactive-user-interfaces-for-mcp
- MCP Apps draft spec: https://github.com/modelcontextprotocol/ext-apps/blob/main/specification/draft/apps.mdx (display modes inline/fullscreen/pip, host context theme/styles CSS variables, size-changed notifications, CSP connectDomains/resourceDomains/frameDomains, tool visibility)
- MCP Apps announcement: https://blog.modelcontextprotocol.io/posts/2025-11-21-mcp-apps/
- assistant-ui docs: https://www.assistant-ui.com/docs (index only; primitives Thread, ThreadList, Composer, ActionBar, BranchPicker taken from general knowledge — verify)

Found via search (titles/snippets only; details from prior knowledge — verify before citing):
- PatternFly Chatbot design guidelines: https://www.patternfly.org/patternfly-ai/chatbot/overview/design-guidelines (display modes overlay/docked/fullscreen/embedded; fetch returned 404 at time of research)
- PatternFly Chatbot messages: https://www.patternfly.org/patternfly-ai/chatbot/chatbot-messages
- PatternFly conversation history: https://patternfly.org/patternfly-ai/chatbot/chatbot-conversation-history
- CopilotKit useHumanInTheLoop: https://docs.copilotkit.ai/reference/hooks/useHumanInTheLoop
- Cloudscape GenAI patterns index: https://cloudscape.design/gen-ai/patterns/ (also /thinking/, /progressive-steps/, /response-regeneration/)
- Microsoft HAX Guidelines for Human-AI Interaction (18 guidelines): https://www.microsoft.com/en-us/research/publication/guidelines-for-human-ai-interaction/ and HAX Toolkit https://www.microsoft.com/en-us/haxtoolkit/
- Streaming + screen readers:
  - https://tianpan.co/blog/2026/04/17/ai-accessibility-streaming-screen-readers
  - https://azukiazusa.dev/en/blog/accessible-streaming-chat-ui
  - https://jira.atlassian.com/browse/ROVO-978 (real-world bug: streamed content not announced)
- WAI-ARIA log role: https://www.w3.org/TR/wai-aria-1.2/#log
- DTCG format 2025.10 (color object form, gradient type): https://www.designtokens.org/tr/2025.10/format/
