# Scope expansion: media, reading, messaging, billing, analytics, ERP, calendar, maps, social, account settings

Date: 2026-10-17 · Status: draft for review · Target release: 1.2.0

## 1. Goal

Add opt-in coverage for products the manifest can't describe today: video, livestreaming, music and podcasts, book and article reading, person-to-person messaging (DMs, channels, calls, support widget), billing and payments, reports and metrics, ERP, calendar and scheduling, maps, and social profiles. Also add a full account-settings suite and notification preferences to `product`, plus a landing page for each consumer scope.

**Non-goals for this release:** mobile scaffold components (the 10 core components stay as they are), the Fleetline example, and splitting the manifest file. Each one waits for a concrete need.

## 2. Decisions (from brainstorming)

| # | Decision | Rationale |
|---|---|---|
| D1 | Approach A, data-first: manifest entries + one reference doc per scope + token templates only where needed. About 15 lines of `ds.py` | Scopes are already data-driven (`components()`, `page_dir`, `templates/scopes/<scope>/`). No consumer format breaks |
| D2 | Four media scopes (`video`, `live`, `music`, `podcast`) on top of a hidden base scope `playback` | Each product type stays opt-in, and the player core is written once |
| D3 | `scope_requires` map: picking a scope pulls in its base scopes | A podcast-only system still gets the transport controls |
| D4 | Per-component `requires_scopes`: landing pages build only when `marketing` is on too | Avoids building a marketing surface for an internal app |
| D5 | One spec, implemented in waves (one scope per commit) | All scopes have the same shape; separate specs would be ceremony |
| D6 | Messaging covers DMs + groups, channels, calls and the support widget, gated by tier | User picked all four depths |
| D7 | Reading covers ebook, audiobook, comics/manga and long-form articles | User picked all four formats |
| D8 | Landing pages only for consumer scopes (video, live, music, podcast, reading, messaging, social) | B2B scopes (billing, analytics, ERP, calendar, maps) use `landing-page variant:saas` and `pricing-page`, which already exist |

## 3. Infrastructure

### 3.1 Manifest (`assets/manifest.json`)

- `scopes`: add these keys, using the existing format (string description): `playback`, `video`, `live`, `music`, `podcast`, `reading`, `messaging`, `billing`, `analytics`, `erp`, `calendar`, `maps`, `social`. The `playback` description starts "Base scope (added automatically by video/live/music/podcast/reading/messaging)".
- New top-level key:
  ```json
  "scope_requires": {
    "video": ["playback"], "live": ["video"], "music": ["playback"], "podcast": ["playback"],
    "reading": ["playback"], "messaging": ["playback"]
  }
  ```
  Expansion is transitive, so `live` pulls in `video` and then `playback`.
- Categories: `<scope>` (components) and `<scope>-pages` (`"page_dir": "patterns"`), same shape as `commerce` / `commerce-pages`. `playback` has components only.
- Component field `requires_scopes` (optional list). The component is skipped unless every listed scope is enabled. It is used only by the landing pages in this release.
- Component ids stay globally unique. Shared docs pages use `file` the way `calendar` already uses `date-picker`.

### 3.2 `ds.py`

1. `expand_scopes(scopes)` does a fixed-point expansion over `MANIFEST["scope_requires"]` and preserves order (requested scopes first, then the added ones).
2. `cmd_init`: call `expand_scopes` after parsing `--scopes` and before the unknown-scope check and the template copy loop. Print `scopes: product, music (+ playback)` so the addition is visible.
3. `components(cfg)`: also check `set(c.get("requires_scopes", [])) <= scopes`.
4. `load_cfg` (or `components`) expands scopes too, so an existing `ds.config.json` edited by hand to add `"music"` still gets `playback` without re-running `init`. Templates for added scopes are copied only by `init` (documented: re-run `init --adopt` to pick up scope tokens).
5. The usage string lists all scopes from the manifest instead of a hard-coded example.

### 3.3 Token templates (`assets/templates/scopes/<scope>/`)

| Scope | tokens.json | themes | contrast pairs |
|---|---|---|---|
| playback | `media.surface` (always dark), `media.scrim`, `media.track.rail|buffered|played`, `media.live` (red), `media.focus` | dark, high-contrast | caption text on scrim, live badge text, control icon on surface |
| reading | `reader.paper|sepia|night` bg/fg/link/selection, `reader.measure` (66ch), `reader.leading`, `reader.highlight.yellow|green|blue|pink` | dark, high-contrast | each reader theme fg/bg/link, highlight bg with text |
| messaging | `message.own|other` bg/fg, `presence.online|away|busy|offline` | dark, high-contrast | own/other bubble text |
| maps | `map.pin.default|selected|visited`, `map.route`, `map.cluster` | dark | pin label on pin |
| analytics | `metric.delta.up|down|flat` (reuses the dataviz palette from `references/imagery.md`) | dark, high-contrast | delta text on surface |
| others | none (they compose product tokens) | | |

Delta and presence colors always ship with text or icon, never color alone (contract §5).

### 3.4 Reference docs

One `references/components/<scope>.md` per scope with the `commerce.md` skeleton: header (how to enable it, where the files live, which product components it composes), Contents, §1 rules for every surface (sourced), one section per group, then Pages. SKILL.md "References" and `references/builder-brief.md` list the new files. `references/companion-skills.md` stays as is.

Sources to cite in the rules (as rules, not numbers): WCAG 2.2 (1.2.x media, 2.2.2 pause/stop/hide, 2.3.3 animation, 1.4.12 text spacing), Media Session API, Remote Playback API, WebVTT, EPUB 3 + Media Overlays, Readium CSS user settings, CSS Custom Highlight API, ARIA APG (`log`, `feed`, `grid`, `combobox`, `dialog`), Web Share API, Notifications API permission UX (soft ask first), Geolocation permission UX, RFC 5545 RRULE, Baymard / GOV.UK for billing forms, FTC "click to cancel" honesty rules (cite as a rule).

### 3.5 Tests (`tests/test_ds.py`)

- `scope_requires` keys and values are known scopes; the graph has no cycles.
- `init --scopes product,live` stores `product, live, video, playback`.
- `requires_scopes`: `video-landing` isn't listed by `components()` without `marketing` and is listed with it.
- Every non-`product` scope with at least one category has `references/components/<scope>.md`.
- Every manifest id is unique (existing test, if one exists; add it if not).
- Golden files are updated only where `index.html` / status output changes.

## 4. Catalog

Format: `id` (tier) — demos — notes. Tiers: c = core, s = standard, e = enterprise. Each entry also gets `aria`, `native` and `desc` in the manifest (specified in the reference doc). Demos marked `…` inherit the obvious `state:loading`/`state:error` where the component fetches data.

### 4.1 `playback` (base, components only)
- `play-toggle` (c): state:play, state:pause, state:loading, state:replay. `button` with a changing accessible name, not `aria-pressed`.
- `seek-bar` (c): state:default, state:buffering, variant:chapters, variant:hover-preview, state:live-edge, state:disabled. `input[type=range]` with `aria-valuetext` "1:23 of 4:56".
- `volume-control` (c): state:default, state:muted, variant:vertical-popover.
- `time-display` (c): variant:elapsed-duration, variant:remaining, variant:live.
- `playback-speed` (c): variant:menu, variant:stepper. Range 0.5 to 3×, current value in the name.
- `captions-menu` (s): state:off, state:on, variant:tracks, variant:caption-style. Caption style covers size, background and font (FCC-style user settings).
- `transcript-panel` (s): state:synced, variant:search, variant:click-to-seek, state:auto-scroll-paused.
- `media-queue` (s): state:now-playing, state:empty, variant:reorder (composes `sortable-list`), variant:up-next.
- `mini-player` (s): variant:bottom-bar, variant:floating, state:expanded.
- `sleep-timer` (e): variant:minutes, variant:end-of-chapter, state:active.
- `cast-button` (e): state:available, state:connecting, state:connected, state:unavailable. Remote Playback API / AirPlay.
- Shared behavior `js/lib/media.js`: Media Session metadata/actions, keyboard map (Space/K, J/L, ←/→, M, C, F), one live region for state changes. Documented in `playback.md` §1, not a manifest entry.

### 4.2 `video` (requires playback)
Components:
- `video-player` (c): variant:inline, variant:theater, variant:fullscreen, variant:with-chapters, state:loading, state:buffering, state:error, state:ended. Composes the playback controls. No autoplay with sound; captions on by preference.
- `video-card` (c): variant:grid, variant:list, variant:compact, state:watched-progress, state:loading.
- `video-end-screen` (s): state:countdown, state:cancelled, variant:suggestions. Autoplay countdown is cancelable and never starts under reduced motion without a visible control.
- `video-quality-menu` (s): variant:auto, variant:manual, state:data-saver.
- `playlist-panel` (s): state:current-item, variant:collapsible, variant:shuffle-loop.
- `creator-header` (s): variant:banner, variant:compact, state:subscribed.
- `subscribe-button` (c): state:subscribe, state:subscribed, variant:with-notifications-bell.
- `content-warning` (s): variant:age-gate, variant:sensitive, state:revealed.
- `video-upload` (e): state:uploading, state:processing, state:ready, state:failed, variant:metadata-form, variant:thumbnail-picker.

Pages (`video-pages`):
- `watch-page` (c): variant:default, variant:theater, variant:with-playlist, variant:mobile.
- `video-home` (c): variant:grid, variant:category-chips, state:loading.
- `channel-page` (s): variant:videos, variant:about, state:empty.
- `video-library` (s): variant:history, variant:watch-later, state:empty.
- `video-search-results` (s): variant:filters, state:no-results.
- `video-studio` (e): variant:content-list, variant:edit-video.
- `video-landing` (s, requires marketing): variant:default, variant:with-pricing.

### 4.3 `live` (requires video)
Components:
- `live-badge` (c): state:live, state:starting-soon, state:ended, state:offline, variant:with-viewers. The word LIVE is always present.
- `live-player` (c): state:live-edge, state:behind-live (shows "Go live"), state:reconnecting, state:offline, variant:dvr, variant:latency-indicator.
- `live-chat` (c): state:default, state:paused-scroll (shows "N new messages"), variant:pinned, variant:slow-mode, variant:members-only, variant:moderation, state:collapsed. Uses `role=log` with announcements throttled or opt-in.
- `live-reactions` (s): state:default, state:reduced-motion. Reduced motion gives a static count.
- `stream-schedule` (s): variant:week, variant:list, state:reminder-set, state:empty.
- `live-poll` (e): state:open, state:voted, state:closed-results.
- `tip-message` (e): variant:tiers, state:pinned. Paid chat highlight; amount shown as text.
- `go-live-panel` (e): state:preview, state:live, state:health-warning, variant:stream-key. Stream key masked, with a copy button.

Pages (`live-pages`):
- `live-page` (c): variant:with-chat, variant:theater, variant:mobile-overlay-chat, state:offline.
- `live-directory` (s): variant:grid, variant:category, state:empty.
- `live-studio` (e): variant:dashboard.
- `live-landing` (s, requires marketing).

### 4.4 `music` (requires playback)
Components:
- `now-playing-bar` (c): state:playing, state:paused, state:empty, variant:mobile. Persistent bar with art, title, controls, seek, volume, and queue/lyrics toggles.
- `track-row` (c): state:default, state:playing, state:unavailable, variant:explicit, variant:with-album, variant:compact.
- `track-list` (c): variant:album, variant:playlist, variant:search, state:loading. `table` semantics; row action on Enter.
- `artwork-card` (c): variant:album, variant:playlist, variant:artist-round, state:playing. Play overlay reachable by keyboard.
- `save-toggle` (c): state:saved, state:unsaved. `aria-pressed` heart or plus.
- `artist-header` (s): variant:hero, state:following, variant:verified.
- `lyrics-view` (s): variant:synced, variant:static, state:unavailable, state:reduced-motion.
- `now-playing-view` (s): variant:full-screen, variant:lyrics-tab, variant:queue-tab, variant:mobile.
- `playlist-editor` (s): state:editing, variant:reorder, variant:cover-description.
- `equalizer` (e): variant:presets, variant:bands, state:off.

Pages (`music-pages`):
- `music-home` (c): variant:shelves, state:loading.
- `album-page` (c): variant:default, variant:multi-disc.
- `playlist-page` (c): variant:own, variant:followed, state:empty.
- `artist-page` (s): variant:popular, variant:discography.
- `music-library` (s): variant:grid, variant:list, state:empty.
- `music-search` (s): variant:top-result, state:no-results.
- `music-landing` (s, requires marketing).

### 4.5 `podcast` (requires playback)
Components:
- `podcast-player` (c): variant:full, variant:compact, variant:skip-15-30, variant:chapter-art.
- `episode-row` (c): state:unplayed, state:in-progress, state:played, state:downloaded, variant:compact.
- `show-card` (c): variant:grid, variant:list.
- `show-header` (s): state:following, variant:with-rating, variant:rss-link.
- `episode-notes` (s): variant:timestamps-seek, variant:chapters, variant:links.
- `download-button` (s): state:idle, state:downloading, state:downloaded, state:error.
- `clip-share` (e): variant:at-timestamp, variant:clip-range.

Pages (`podcast-pages`):
- `podcast-home` (c): variant:shelves, state:loading.
- `show-page` (c): variant:episodes, variant:about.
- `episode-page` (c): variant:default, variant:with-transcript.
- `podcast-queue` (s): state:with-items, state:empty.
- `podcast-landing` (s, requires marketing).

### 4.6 `reading` (requires playback)
Components:
- `reader-viewport` (c): variant:paged, variant:scroll, variant:two-column, variant:rtl, variant:vertical-writing, state:loading. Uses `writing-mode` and logical properties.
- `reader-toolbar` (c): state:visible, state:auto-hidden, variant:mobile.
- `reader-settings` (c): variant:typography, variant:theme, variant:layout. Font, size, leading, margins, paper/sepia/night, paged/scroll, justify; saved per user (Readium CSS settings).
- `reader-toc` (c): state:current-chapter, variant:nested.
- `reading-progress` (c): variant:percent, variant:location, variant:time-left, variant:jump-slider.
- `book-card` (c): variant:grid, variant:list, state:in-progress, state:finished, variant:format-badges.
- `highlight-menu` (s): state:open, variant:colors-labelled, variant:note, variant:define. CSS Custom Highlight API; colors carry names.
- `notes-panel` (s): variant:highlights, variant:notes, variant:export, state:empty.
- `bookmark-toggle` (s): state:set, state:unset.
- `in-book-search` (s): state:results, state:no-results.
- `bookshelf` (s): variant:collections, variant:sort, state:empty.
- `audiobook-player` (s): variant:chapters, variant:follow-along, state:sleep-timer. Follow-along uses EPUB Media Overlays to highlight the current sentence.
- `comic-viewer` (s): variant:single, variant:spread, variant:rtl-manga, variant:webtoon-scroll, variant:fit-width, state:zoomed.
- `article-reader` (s): variant:default, variant:reading-time, variant:with-tts.
- `dictionary-popover` (e): state:found, state:not-found.
- `tts-control` (e): state:speaking, state:paused, variant:voice-rate, variant:word-highlight. `speechSynthesis`.

Pages (`reading-pages`):
- `library-page` (c): variant:shelves, variant:continue-reading, state:empty.
- `book-detail-page` (c): variant:ebook, variant:audiobook, variant:series.
- `reader-page` (c): variant:paged, variant:scroll, variant:comic, variant:audiobook.
- `read-later-page` (s): variant:list, state:empty.
- `reading-landing` (s, requires marketing).

### 4.7 `messaging` (requires playback, for voice notes and call media)
Components, DMs and groups:
- `message-bubble` (c): variant:own, variant:other, variant:grouped-first|middle|last, variant:with-avatar, variant:reply-quote, state:sending, state:sent, state:delivered, state:read, state:failed-retry, state:edited, state:deleted. Separate from `ai` `chat-message`; sender is conveyed by text, not just alignment.
- `message-thread` (c): variant:day-dividers, state:unread-divider, state:jump-to-latest, state:loading-older, state:empty. Uses `role=log`.
- `conversation-row` (c): state:unread, state:muted, state:pinned, state:typing, variant:group.
- `presence-indicator` (c): state:online, state:away, state:busy, state:offline. Has a text alternative.
- `typing-indicator` (c): state:one, state:several, state:reduced-motion. Announcements throttled.
- `attachment-preview` (c): variant:image, variant:file, variant:video, state:uploading, state:failed.
- `message-reactions` (s): state:default, state:own-reacted, variant:picker-open. Chips with `aria-pressed` and a count.
- `emoji-picker` (s): variant:search, variant:skin-tone, variant:recent. Grid pattern.
- `voice-note` (s): state:recording, state:permission-denied, state:recorded, state:playing.
- `mention-autocomplete` (s): state:open, state:no-match. Combobox inside `composer`.
- `read-receipts` (s): variant:dm, variant:group-avatars.
- `message-search` (s): state:results, state:no-results, variant:filters.

Components, channels:
- `channel-list` (s): state:unread, state:mention, variant:private, variant:muted, variant:sections.
- `channel-header` (s): variant:topic, variant:members, variant:call-actions.
- `thread-panel` (s): state:open, state:empty.
- `member-list` (s): variant:by-role, variant:with-presence.
- `pinned-messages` (e): state:with-items, state:empty.

Components, calls:
- `call-controls` (e): state:in-call, state:muted, state:camera-off, state:sharing, variant:mobile. "Leave" uses the danger style.
- `participant-tile` (e): state:speaking, state:muted, state:camera-off, state:hand-raised, state:poor-connection. Speaking is shown by border and text, not color alone.
- `incoming-call` (e): state:ringing, state:missed. Uses `role=alertdialog`.
- `device-check` (e): state:preview, state:permission-denied, state:no-devices.

Components, support:
- `support-launcher` (s): state:closed, state:unread, state:open.
- `support-panel` (s): state:bot, state:agent-handoff, state:offline-form, state:csat, variant:reply-time.

Pages (`messaging-pages`):
- `inbox-page` (c): variant:two-pane, variant:mobile-list, state:no-selection, state:empty.
- `workspace-page` (s): variant:three-pane, variant:with-thread.
- `call-page` (e): variant:grid, variant:speaker, variant:screen-share.
- `support-widget-page` (s): variant:on-marketing-page, variant:in-app.
- `messaging-landing` (s, requires marketing).

### 4.8 `billing`
Components (composes `payment-card-entry`, `data-table`, `meter`, `alert`):
- `current-plan` (c): state:active, state:trial, state:past-due, state:cancelled-until.
- `plan-picker` (c): variant:monthly-annual, state:proration-preview, state:downgrade-warning.
- `payment-method-list` (c): state:default, state:expired, state:empty, variant:add.
- `add-payment-method` (c): variant:card, variant:bank-debit-mandate, variant:wallet.
- `invoice-list` (c): state:paid, state:open, state:overdue, state:void, state:empty.
- `invoice-detail` (s): variant:line-items-tax, state:pay-now.
- `billing-usage` (s): state:under, state:near-limit, state:over. Different from the `ai` `usage-meter`, which measures tokens.
- `billing-alert` (s): variant:payment-failed, variant:card-expiring, variant:trial-ending.
- `cancel-flow` (s): state:reason, state:offer, state:confirm, state:done. Cancelling takes no more steps than signing up, with no confirmshaming.
- `transaction-list` (s): variant:filters, variant:export, state:pending, state:refunded.
- `payout-summary` (e): variant:balance, variant:schedule, state:on-hold.
- `wallet-balance` (e): variant:credits, state:top-up.
- `tax-info-form` (e): variant:vat-id, state:invalid, state:verified.
- `refund-dialog` (e): variant:full, variant:partial.

Pages (`billing-pages`):
- `billing-page` (c): variant:overview, state:past-due.
- `plans-page` (c): variant:in-app, state:current-highlighted.
- `invoice-page` (s): variant:printable.
- `transactions-page` (s): state:empty.
- `payouts-page` (e): variant:history.

### 4.9 `analytics`
Components (composes `stat`, `chart-*`, `data-table`, `date-range-picker`):
- `analytics-filter-bar` (c): variant:date-presets, variant:compare-to, variant:segments, state:applied.
- `report-table` (c): variant:totals-row, variant:drill-down, state:loading, state:no-data.
- `export-menu` (c): variant:csv-xlsx-pdf, state:preparing, state:ready.
- `data-freshness` (c): state:fresh, state:stale, state:refreshing.
- `metric-definition` (s): variant:hover-card, variant:glossary.
- `scorecard` (s): variant:target, variant:vs-previous, state:missed. Composes `stat`.
- `funnel-chart` (s): variant:steps, variant:with-dropoff, state:loading.
- `cohort-table` (e): variant:retention, state:loading. A heatmap that always shows the numbers.
- `pivot-table` (e): variant:row-col-groups, state:empty.
- `report-builder` (e): state:empty, state:configured, variant:chart-type.
- `scheduled-report` (e): variant:schedule-form, state:active, state:paused.
- `chart-annotation` (e): variant:event-marker, state:editing.
- `alert-rule` (e): variant:threshold, state:triggered.

Pages (`analytics-pages`):
- `analytics-overview` (c): variant:kpi-row-charts, state:loading.
- `report-page` (c): variant:chart-table, variant:shared-readonly.
- `reports-library` (s): variant:list, state:empty.
- `report-builder-page` (e): variant:default.

### 4.10 `erp`
Components (composes `data-table`, `combobox`, `stepper`, `timeline`, `file-upload`, `saved-filters`):
- `record-header` (c): variant:status-actions, variant:prev-next, state:locked.
- `line-item-editor` (c): state:default, state:editing-cell, state:invalid-cell, variant:totals, variant:add-row. Grid pattern; keyboard behaves like a spreadsheet.
- `status-workflow` (c): state:draft, state:submitted, state:approved, state:posted, state:rejected.
- `master-data-lookup` (c): variant:code-name-columns, state:no-match, variant:create-new.
- `approval-panel` (s): state:pending, state:approved, state:rejected, variant:chain, variant:delegated.
- `audit-log` (s): variant:field-changes, variant:filters, state:empty.
- `inventory-level` (s): state:in-stock, state:low, state:out, variant:by-location.
- `print-layout` (s): variant:invoice, variant:purchase-order. `@page` rules plus a print stylesheet.
- `batch-edit` (e): state:preview, state:applying, state:partial-failure.
- `import-wizard` (e): state:mapping, state:validation-report, state:dry-run, state:imported.

Pages (`erp-pages`):
- `record-list-page` (c): variant:dense, variant:saved-views, state:empty.
- `record-form-page` (c): variant:header-tabs-lines, state:dirty, state:readonly.
- `purchase-order-page` (s): variant:draft, variant:approved.
- `inventory-page` (s): variant:stock-list, variant:item-detail.
- `approvals-inbox` (s): state:with-items, state:empty.
- `import-page` (e): variant:default.

### 4.11 `calendar`
Components (composes `date-field`, `time-picker`, `calendar`, `combobox`):
- `calendar-month` (c): state:today, state:selected-day, variant:overflow-more.
- `calendar-week` (c): variant:time-grid, state:now-line, variant:overlapping.
- `calendar-day` (s): variant:time-grid, variant:resources.
- `calendar-agenda` (c): variant:grouped-by-day, state:empty.
- `event-chip` (c): state:default, state:tentative, state:declined, state:cancelled, variant:all-day. The category name appears with its color.
- `event-editor` (c): variant:quick, variant:full, state:conflict, state:invalid.
- `time-slot-picker` (c): variant:by-day, state:no-slots, variant:timezone-switch.
- `recurrence-picker` (s): variant:presets, variant:custom-rrule.
- `availability-editor` (s): variant:weekly-hours, variant:date-overrides.
- `timezone-select` (s): variant:search, variant:detected.
- `resource-scheduler` (e): variant:rooms, variant:people, state:drag-reschedule.

Pages (`calendar-pages`):
- `calendar-page` (c): variant:month, variant:week, variant:day, variant:agenda, variant:mobile.
- `booking-page` (c): state:select-slot, state:details, state:confirmed, state:no-availability.
- `availability-page` (s): variant:default.
- `event-detail-page` (s): variant:organizer, variant:guest-rsvp.

### 4.12 `maps`
Components (provider-agnostic: MapLibre, Leaflet, Google, Mapbox; the docs explain how to wrap each):
- `map-container` (c): state:loading, state:error, state:static-fallback, variant:with-attribution. Labelled region, keyboard pan/zoom, no scroll hijack (two-finger or Ctrl to zoom), and a list as text alternative.
- `map-marker` (c): state:default, state:selected, state:visited, variant:with-label. `button` semantics.
- `map-popup` (c): state:open, variant:card.
- `map-controls` (c): variant:zoom, variant:locate, variant:layers, variant:fullscreen.
- `location-search` (c): state:suggestions, state:no-results.
- `location-picker` (s): state:drop-pin, state:locating, state:permission-denied, state:selected.
- `marker-cluster` (s): state:collapsed, state:expanded.
- `map-list-sync` (s): variant:split, variant:mobile-toggle, state:hover-sync.
- `directions-panel` (e): variant:modes, variant:steps, state:no-route.
- `area-selector` (e): variant:radius, variant:polygon.

Pages (`maps-pages`):
- `store-locator` (c): variant:split, variant:mobile, state:no-results.
- `map-search-page` (s): variant:search-as-move, state:loading.
- `directions-page` (e): variant:default.

### 4.13 `social`
Components (composes `post-card`, `feed`, `comment-thread`, `avatar`, `composer`):
- `profile-header` (c): variant:own, variant:other, state:private, state:blocked, variant:verified. "Verified" is in the accessible name.
- `follow-button` (c): state:follow, state:following, state:requested, state:follows-you. Unfollow goes through a menu or confirm, never a hover-only label swap.
- `user-row` (c): variant:with-follow, variant:compact.
- `reaction-bar` (c): state:default, state:liked, state:saved, variant:counts.
- `post-composer` (c): state:empty, state:with-media, state:over-limit, variant:audience. Composes `composer`.
- `share-sheet` (s): variant:web-share, variant:fallback-copy-link.
- `stories-tray` (s): state:unseen, state:seen. Ring plus text state, not color alone.
- `story-viewer` (s): state:playing, state:paused, state:reduced-motion, variant:reply. Pauses on hold or focus; has keyboard next/prev.
- `people-suggestions` (s): variant:carousel, variant:list, state:empty.
- `report-dialog` (s): state:reasons, state:submitted, variant:with-block.
- `block-mute-menu` (s): variant:mute, variant:block, state:confirm.

Pages (`social-pages`):
- `profile-page` (c): variant:posts, variant:media, state:private, state:empty.
- `home-feed-page` (c): variant:following, variant:for-you, state:loading.
- `post-detail-page` (s): variant:with-replies.
- `followers-page` (s): variant:followers, variant:following, state:empty.
- `explore-page` (s): variant:trending, variant:search.
- `social-landing` (s, requires marketing).

### 4.14 `product` additions
Patterns category (`patterns`), one docs page each. The existing `settings` pattern becomes the shell they share:
- `settings-profile` (s): variant:default, variant:avatar-upload, state:saving, state:invalid.
- `settings-account` (s): variant:email-change-verify, variant:username, variant:language-region-timezone.
- `settings-security` (s): variant:password, variant:2fa-setup, variant:passkeys, variant:recovery-codes, state:2fa-enabled.
- `settings-notifications` (s): variant:channel-matrix, variant:quiet-hours, variant:digest. Composes `preference-matrix`.
- `settings-privacy` (s): variant:visibility, variant:blocked-users, variant:data-sharing.
- `settings-appearance` (s): variant:theme, variant:density, variant:motion, variant:text-size. Wired to `js/theme.js`.
- `settings-sessions` (e): variant:devices, state:sign-out-others.
- `settings-connected-apps` (e): variant:oauth-apps, variant:api-tokens, state:empty.
- `settings-data` (e): variant:export, variant:delete-account. Reuses `delete-with-confirmation` type-to-confirm.
- `notification-inbox` (e): variant:all, variant:unread, variant:mentions, state:empty, variant:bulk-mark-read. Full page; `notification-center` stays the popover.

Forms and feedback categories:
- `preference-matrix` (s, forms): variant:switches, variant:checkboxes, state:all-off. Table of event × channel (email, push, in-app, SMS) with row and column headers.
- `notification-permission-prompt` (s, feedback): state:soft-ask, state:granted, state:denied-help, state:unsupported. The native prompt only appears after a user action.

## 5. Implementation waves

Each wave is one commit and leaves the repo green (`python3 -m unittest discover tests`, `ds.py init <tmp> --scopes product,<scope>,marketing --tier enterprise --dry-run`, `ds.py coverage`, `ds.py plan`).

| Wave | Content |
|---|---|
| W0 | `ds.py` `expand_scopes` + `requires_scopes` + tests; `playback` scope (manifest, `playback.md`, token template) |
| W1 | `video` + `live` |
| W2 | `music` + `podcast` |
| W3 | `reading` |
| W4 | `messaging` |
| W5 | product additions (settings suite, notifications) and the `patterns.md` / `forms.md` / `overlays-feedback.md` sections |
| W6 | `billing` |
| W7 | `analytics` |
| W8 | `erp` |
| W9 | `calendar` + `maps` |
| W10 | `social` |
| W11 | Counts regenerated across SKILL.md, README, `.claude-plugin/*`, `.codex-plugin/plugin.json`, `.cursor-plugin/plugin.json`; SKILL.md Phase 1 scope guidance and References list; `builder-brief.md`; CHANGELOG 1.2.0; one eval in `evals/evals.json` (a "podcast app" prompt should pick `podcast` and get `playback`) |

Waves W1 to W10 are independent once W0 lands, so they can run as parallel subagents (one per wave, with the manifest merged serially to avoid JSON conflicts).

## 6. Risks

- **Manifest size** (~127 KB to ~260 KB): reviewable per wave. Split it (approach B) if a single-file diff becomes unworkable.
- **Overlap with existing components** (`chat-message` vs `message-bubble`, `usage-meter` vs `billing-usage`, `stat` vs `scorecard`): each reference doc has a "vs." line saying when to use which.
- **Enterprise tier with every scope** is about 530 components (306 + 226). The plan output already groups by file, and builder subagents fan out per category, so the size is fine.
- **Third-party surfaces** (map tiles, payment iframes, DRM video): the docs state what the system can't guarantee, the same way `commerce.md` does for hosted card fields.
