# Mobile & gesture components — specs

Scope `mobile` (enable with `ds init --scopes product,mobile`). Components live in `components/<file>.html` (category **Mobile & Gestures**). They compose product components by id (`button-primary`, `button-destructive`, `icon-button`, `menu-button`, `overflow-menu`, `list-group`, `drawer`, `modal`, `tabs`, `toast`, `spinner`, `search-input`) — wrap them, never re-style them. The native port uses each platform's built-in gesture components (`references/mobile.md` §2), and `ds mobile scaffold` generates token-styled wrappers for them when this scope is on.

## Contents
1. Gesture contract (applies to every gesture in every scope)
2. Rows and actions: swipe-actions, action-sheet
3. Scroll gestures: pull-to-refresh, collapsing-app-bar
4. Sheets and pages: detent-sheet, swipe-pager
5. Media: zoomable-image
6. Sources

## 1. Gesture contract
Sources are named as rules: WCAG 2.2 (2.5.1 pointer gestures, 2.5.7 dragging movements, 2.5.2 pointer cancellation, 2.5.8 target size, 2.1.1 keyboard, 2.3.3 animation from interactions), ARIA APG (`dialog`, `tabs`, `menu button`), MDN (scroll snap, Pointer Events, `touch-action`, `overscroll-behavior`, scroll-driven animations).

- **Every gesture has a visible, single-pointer path** (WCAG 2.5.1, 2.5.7, technique G219). A swipe, drag, pinch or long press is a shortcut, never the only way: the same action is a button or a menu item that works with one tap, a mouse click and the keyboard. Swipe-only and long-press-only actions are bugs (`social.md` and `erp.md` already require this).
- **Act on release, allow cancel** (WCAG 2.5.2). Nothing fires on pointer down. Moving back past the threshold, or `pointercancel`, returns to rest without acting. Destructive full swipes either confirm or show an Undo `toast`.
- **Scroll snap first, script second.** Reveal, paging and snap heights are scroll containers with `scroll-snap-type` and `scroll-snap-align`, so momentum, rubber-banding and RTL come from the browser. Script only reads the result (`scrollend`, `IntersectionObserver`) or covers what snap can't do (drag past the last snap to dismiss, pinch). When script handles a drag: Pointer Events with `setPointerCapture`, never the HTML5 Drag and Drop API (no touch support, poor accessibility).
- **Don't steal the page scroll.** Scroll-snap containers keep the default `touch-action`: the browser already tells a horizontal swipe from a vertical scroll. A script-driven drag sets `touch-action` to the axis it leaves to the page (`pan-y` on a horizontal drag handle, `pan-x` on a vertical one, `none` only on a zoomed image). Use `overscroll-behavior: contain` on inner scrollers so they don't trigger the browser's own pull-to-refresh or back swipe. Long press selects first; a drag starts only after selection (as in `sortable-list` and `calendar` moves).
- **Keyboard parity** (WCAG 2.1.1). Each component lists its keys. Focus stays on the control that acted, or moves to a stated place; never to `body`.
- **Targets** (WCAG 2.5.8). At least 24 px, and 44 px on touch (`size.touch-target`). Revealed actions are at least `size.swipe-action` wide.
- **Reduced motion** (WCAG 2.3.3, `prefers-reduced-motion`). Snapping still works, but `scroll-behavior` is `auto`, settle and spring animations become instant, and parallax or title scaling is off.
- **RTL.** Leading and trailing follow the writing direction: the trailing swipe reveals actions on the `inline-end` side and the pager advances toward `inline-end`. Use logical properties only.
- **No haptics or sound on the web.** `navigator.vibrate` is unreliable and can't be turned off by users per site. Native apps use the platform's standard haptic for the platform component, nothing custom.
- **Tokens.** Colors come from existing roles: `feedback.danger.*` for destructive actions, `action.*` for others, `bg.surface` and `elevation.overlay` for sheets, `border.default` for the handle. This scope adds `size.sheet.peek` (96 px) and `size.swipe-action` (80 px). Durations use `motion.duration.*` and `motion.easing.*`.

## 2. Rows and actions

## swipe-actions (core)
- Markup: `<li>` with a horizontal scroll container (`overflow-x: auto; scroll-snap-type: x mandatory; overscroll-behavior-x: contain`) holding three snap children: leading actions, the row content (snap target at rest, full width), trailing actions. Actions are `<button>`s at least `size.swipe-action` wide. The row content keeps its own primary link or button.
- Fallback (`variant:menu-fallback`, always present): a "More actions" `menu-button` in the row with exactly the same actions. On pointer devices without touch (`@media (hover: hover) and (pointer: fine)`) the menu button is visible and the swipe container doesn't scroll.
- States: `state:revealed-trailing` / `state:revealed-leading` show the actions; `state:full-swipe` shows the first trailing action stretched to the full row with its label (fires on release past `--swipe-full-threshold`, about 60% of the row, via `scrollend`); `state:focus-visible` shows the row content focus ring.
- Revealed actions are `inert` until revealed so Tab doesn't land on hidden buttons. Revealing one row closes any other. Tapping the content of a revealed row closes it instead of opening the item.
- Destructive action: `button-destructive` colors (`feedback.danger.*`), label in text ("Delete"), never color or icon alone. A full swipe on a destructive action removes the row and shows an Undo `toast`, announced politely ("Message deleted. Undo").
- Native: SwiftUI `.swipeActions(edge:allowsFullSwipe:)`, Compose `SwipeToDismissBox`, Flutter `Dismissible`, React Native core `PanResponder` + `Animated`.

## action-sheet (core)
- Markup: `<dialog>` opened with `showModal()`, anchored to the bottom on narrow viewports and centered (or as a `popover` menu next to the trigger) from `md` up. A list of `<button>`s, then a visually separate Cancel button. Optional title and message (`variant:with-title`) wired with `aria-labelledby` / `aria-describedby`.
- `variant:destructive`: the destructive button uses `feedback.danger.fg` text and says what it does ("Delete conversation"); it is never the first focused button. Initial focus goes to the first non-destructive action.
- Esc, Cancel, the backdrop and a downward drag of the sheet (if implemented, via the `detent-sheet` dismiss rule) all close it. Focus returns to the trigger.
- Use a `menu-button` (product) when the options are navigation or toggles; an action sheet is for one-shot actions on one item.
- Native: SwiftUI `.confirmationDialog`, Compose `ModalBottomSheet` with a list, Flutter `showModalBottomSheet`, React Native `Modal` (or `ActionSheetIOS` on iOS).

## 3. Scroll gestures

## pull-to-refresh (standard)
- Only for an inner scroll container (feed, inbox) that has its own scroll. A full page relies on the browser's built-in pull to refresh: don't rebuild it, and don't block it with `overscroll-behavior` on `html`.
- Markup: the scroll container (`overscroll-behavior-y: contain`) starts with an indicator area above the first item, implemented as an extra snap point (`scroll-snap-type: y proximity`; content snap target at rest). Pulling past the indicator and releasing (`scrollend` at the indicator snap) starts a refresh.
- Required alternative (`variant:refresh-button`): a visible "Refresh" `icon-button` (name "Refresh") in the list header or toolbar that does the same thing.
- States: `state:idle`, `state:pulling` (arrow rotates with distance; text "Pull to refresh", then "Release to refresh"), `state:refreshing` (`spinner`, container `aria-busy="true"`, the button disabled with `aria-disabled`), `state:done` (polite `role="status"`: "Updated just now" or "3 new items"; errors use the same status and keep the old content).
- Focus doesn't move. New items are inserted above without jumping the reader's place when they have scrolled.
- Native: SwiftUI `.refreshable`, Compose `PullToRefreshBox`, Flutter `RefreshIndicator`, React Native `RefreshControl`.

## collapsing-app-bar (standard)
- Markup: `<header>` (banner landmark when it's the page header) with a large title (`h1`) and a compact bar that shows the same title in small type once scrolled. The `h1` stays one element; the compact copy is `aria-hidden`.
- Behavior: CSS scroll-driven animation (`animation-timeline: scroll()`), with `position: sticky` for the compact bar. Browsers without `animation-timeline` show the compact bar plus the large title in the content, no animation. No script needed.
- `variant:with-search`: a `search-input` under the large title that scrolls away with it and stays reachable from a search `icon-button` in the compact bar.
- Reduced motion: no scaling; the large title scrolls away normally and the compact bar appears without a transition.
- Native: SwiftUI `NavigationStack` with `.navigationBarTitleDisplayMode(.large)`, Compose `LargeTopAppBar` with `exitUntilCollapsedScrollBehavior`, Flutter `SliverAppBar` (`pinned`, `expandedHeight`), React Native `Animated` header driven by `onScroll`.

## 4. Sheets and pages

## detent-sheet (standard)
Use `drawer`'s `bottom-sheet` (product) for a simple modal panel; use `detent-sheet` when the sheet stays on screen at several heights (maps, players, filters beside a list).
- Markup: `<dialog>` whose inner scroll container is the full viewport height with snap points for each detent: peek (`size.sheet.peek` visible), half (50%), full (top inset by the safe area). `scroll-snap-type: y mandatory`; the content inside scrolls normally once at full height.
- Handle: a real `<button>` at the top ("Resize sheet"), with `aria-expanded` (false at peek, true otherwise) and a label that says the current height ("Sheet, half height"). Tap or Enter/Space cycles peek → half → full → peek. Visible handle bar is at least `size.touch-target` tall as a target.
- `variant:non-modal` (`show()`): no backdrop, page stays usable, the sheet never takes focus on open. `variant:modal` (`showModal()`): backdrop, focus moves into the sheet, Esc closes, focus returns to the trigger.
- Dismiss: dragging below peek past a small overscroll closes a modal sheet (read on `scrollend`; this is the only script beyond `showModal`). Non-modal sheets stop at peek. Every sheet also has a Close `icon-button`.
- States: `state:peek`, `state:half`, `state:full`, `state:dragging` (handle highlighted, `cursor: grabbing`), `state:focus-visible` (handle ring).
- Announce height changes made by keyboard politely only when the label change isn't enough (it usually is).
- Native: SwiftUI `.sheet` + `.presentationDetents([.height(peek), .medium, .large])` + `.presentationDragIndicator(.visible)`, Compose `BottomSheetScaffold` (non-modal) / `ModalBottomSheet`, Flutter `DraggableScrollableSheet` (`snap: true`, `snapSizes`), React Native `Modal` + `PanResponder` snapping between the same heights.

## swipe-pager (standard)
Use `carousel` (data-display) for promotional or media slides; use `swipe-pager` for full-width app sections the user switches between (tabs on a phone, onboarding steps).
- Markup: APG tabs. `role="tablist"` with `role="tab"` buttons (`variant:with-tabs`) or dot tabs labelled "Page 2 of 4" (`variant:with-dots`); panels are `role="tabpanel"` children of one horizontal scroll container (`scroll-snap-type: x mandatory`).
- Swiping changes the selected tab (`IntersectionObserver` or `scrollend` sets `aria-selected` and `tabindex`); selecting a tab scrolls its panel into view (`scrollIntoView({inline: "start"})`, `behavior: "auto"` under reduced motion). Inactive panels are `inert`.
- Keyboard: APG tabs (←/→, Home/End on the tablist). Panels never trap horizontal arrow keys.
- `::scroll-marker` / `::scroll-button()` may replace the dots and arrows where supported (Chromium); the scripted tablist stays the baseline.
- Native: SwiftUI `TabView` with `.tabViewStyle(.page)`, Compose `HorizontalPager` + tab row or indicator, Flutter `PageView` + `TabBar`, React Native `FlatList` with `pagingEnabled`.

## 5. Media

## zoomable-image (enterprise)
- Markup: `<figure>` with the `<img>` (alt kept), a `<figcaption>`, and a toolbar group of "Zoom in", "Zoom out" and "Reset zoom" `icon-button`s (`variant:with-controls`, always present on touch and pointer).
- Gestures: pinch and double tap zoom around the gesture point; one-finger drag pans only while zoomed (`touch-action: none` while zoomed, `pan-y pinch-zoom` at rest so the page scrolls). Scale is clamped (1×–4×) and pans stop at the image edges.
- Keyboard: the image wrapper is focusable (`tabindex="0"`, named by the image alt) only while zoomed; arrows pan, `+` / `-` zoom, `0` resets. Buttons announce the level politely ("200%").
- Inside `lightbox` it replaces the plain image; Esc first resets zoom, then closes.
- Native: SwiftUI `MagnificationGesture` (or `MagnifyGesture` on iOS 17+) + `DragGesture`, Compose `Modifier.transformable`, Flutter `InteractiveViewer`, React Native `ScrollView` `maximumZoomScale` on iOS; on Android the buttons are the zoom path unless the app adds `react-native-gesture-handler`.

## 6. Sources
- Apple Human Interface Guidelines: sheets (detents), action sheets, lists and tables (swipe actions), refresh content controls, navigation bars (large titles).
- Material Design 3: bottom sheets (standard and modal), lists (swipe to dismiss), pull to refresh, tabs, top app bar (large, collapsing).
- Ionic: `ion-item-sliding`, `ion-refresher`, `ion-modal` sheet breakpoints, `ion-action-sheet`.
- WCAG 2.2 Understanding 2.5.7 Dragging Movements: https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements and technique G219: https://www.w3.org/WAI/WCAG22/Techniques/general/G219
- Native-like bottom sheets with CSS scroll snap: https://dev.to/viliket/native-like-bottom-sheets-on-the-web-the-power-of-modern-css-ld6
- CSS carousels (`::scroll-marker`, `::scroll-button()`): https://developer.chrome.com/blog/carousels-with-css
