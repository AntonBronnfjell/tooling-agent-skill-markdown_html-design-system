# Navigation & orientation — specs

Files: `top-nav`, `side-nav`, `app-rail`, `bottom-nav`, `breadcrumbs`, `tabs`, `pagination`, `stepper`, `command-palette`, `skip-link`, `tree-view`, `carousel` (dot indicator), `back-to-top`, `toc`, `page-header`, `footer`.

Common rule: the current location uses `aria-current="page"` (or `"step"`, `"location"`) **and** a non-color cue (bar, weight, icon).

## top-nav
- `<header>` (banner) → logo link (home), `<nav aria-label="Main">` list, search, utility icons (notifications with badge count in the accessible name: "Notifications, 3 unread"), profile menu (menu button).
- Mobile: collapse into a disclosure / drawer triggered by a "Menu" button with `aria-expanded`; don't hide primary actions behind it if there are ≤ 4.
- Sticky variant: account for it in `scroll-padding-top` so focused elements aren't hidden (WCAG 2.4.11).

## side-nav
- `<nav aria-label="…">` + list; sections with headings; nested groups via `<details>` or disclosure buttons (`aria-expanded`). Collapsed (icons only) variant keeps names via tooltips + `aria-label`; collapse state persisted. Max 2 nesting levels.

## app-rail (enterprise)
- 56–80px vertical bar of icon + short label items for top-level apps/modules; badges; current item indicator. Pairs with side-nav for secondary navigation.

## bottom-nav (enterprise)
- Mobile only, 3–5 destinations, icon + label always (no icon-only), safe-area padding, hides on desktop breakpoints.

## breadcrumbs
- `<nav aria-label="Breadcrumb"><ol>` with separators generated via CSS (not in the accessible text); last item is `aria-current="page"` (not a link). Collapse middle items into an overflow menu when > 4; mobile shows only "← Parent".

## tabs
- APG tabs: `role="tablist"` (+ `aria-label`), `role="tab" aria-selected aria-controls`, `role="tabpanel" aria-labelledby tabindex="0"`. Arrow keys move, Home/End; automatic activation for cheap panels, manual (Enter) for expensive ones. Variants: underline, contained/pill; overflow → scroll with fade or "More" menu; disabled tab. Tabs that change the URL are navigation — use links + `aria-current` instead.

## pagination
- `<nav aria-label="Pagination">` with links (Previous, numbers, ellipsis, Next); current `aria-current="page"`; disabled prev on first page rendered as non-link text. Compact variant ("Page 3 of 12" + prev/next); page-size select and "Showing 21–40 of 312" for data tables. Prefer "Load more" for feeds.

## stepper
- `<ol>` of steps with status text visually hidden ("Completed", "Current", "Not started", "Error") + icons; current `aria-current="step"`. Horizontal → vertical on mobile. Completed steps may be links back.

## command-palette (enterprise)
- `<dialog>` opened by ⌘K/Ctrl+K (and a visible button); combobox input filtering grouped `listbox` results (recent, pages, actions), each with icon + shortcut hint; Enter executes, Esc closes and returns focus. No results state with suggestion.

## skip-link
- First focusable element: `<a class="sr-only sr-only--focusable" href="#main">Skip to main content</a>`; target `<main id="main" tabindex="-1">`. Multiple skip links allowed (to search, to nav).

## tree-view (enterprise)
- APG treeview: `role="tree"`, `treeitem` with `aria-expanded` / `aria-level` / `aria-selected`, `group` for children. Keys: ↑/↓ move, → expand/enter child, ← collapse/parent, Home/End, typeahead, `*` expands siblings. Indent via `--tree-indent` × level; chevrons mirror in RTL.

## dot-indicator (in `carousel`)
- Buttons labeled "Slide 3 of 5", current with `aria-current="true"`; ≥ 24px hit area even if the dot is 8px.

## back-to-top
- Appears after ~2 viewport heights of scroll; `<a href="#top">` (works without JS) labeled "Back to top"; moves focus to the top target; doesn't overlap FAB/toasts.

## toc (in-page nav)
- `<nav aria-label="On this page">` list of anchors; scroll-spy via IntersectionObserver sets `aria-current="location"`; sticky on desktop, collapsible (`<details>`) on mobile.

## page-header
- `<header>` inside main: breadcrumbs, H1 title, meta (status badge, owner, updated time), primary/secondary actions (overflow into menu on small screens), optional tabs underneath. One H1 per page.

## footer
- `<footer>` (contentinfo at page level): link columns with headings, legal, language selector, social links (icon-only need labels). Simple and multi-column variants.

## section-header
- Heading block that opens a page section: optional overline (small caps label, `text-overline`), heading at the right semantic level, description (≤ 2 lines, `--size-measure`), trailing action (link or button). Centered variant for marketing/landing sections. The overline is not part of the heading's accessible name unless intended — place it before the heading as a `<p>`.

## bottom-nav (now standard tier)
- Core for mobile-first products: show it below the `lg` breakpoint and swap to side-nav/top-nav above it inside the app shell (one nav visible at a time, same destinations, same `aria-current`).

Files added: `app-switcher`, `menubar`.

## app-switcher (enterprise)
- Header button (grid icon + accessible name "Switch app" / "Products") with `aria-expanded aria-controls` opening a `[popover]` containing `<nav aria-label="Apps">` with a list of links (icon + name + short description). It's **disclosure navigation**, not `role="menu"` — Tab moves through links, Esc closes and returns focus.
- Current app marked `aria-current="page"` + visual indicator; optional "Recent" group and "All apps" link. Grid layout 3 columns; list on narrow.
- Pitfalls: icon-only tiles without names; mixing actions (sign out) into the switcher.

## menubar (enterprise)
- Only for desktop-like editor products (document/IDE tools). Website navigation is **never** a menubar (use nav + links/disclosure).
- APG Menubar: `role="menubar"` (one Tab stop, roving focus), items `role="menuitem" aria-haspopup="menu" aria-expanded`; ←/→ move across the bar (and switch open menus), ↓/Enter/Space open and focus first item, ↑ opens to last, Esc closes to the bar item, Tab leaves the menubar and closes menus, typeahead. Menus follow the menu spec (checkable items, submenus, shortcut `kbd`).
- Mirror shortcuts as real keyboard shortcuts; show them right-aligned. Collapse to a single "Menu" button on narrow screens.
