# Changelog

All notable changes to this skill. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [Semantic Versioning](https://semver.org/). The version lives in `.claude-plugin/plugin.json` (and the Cursor/Codex manifests); plugin users only receive updates when it changes.

## [Unreleased]

### Added
- **Snapshot tests for the gesture components** (mobile scope). They use the same `<file>--<demo>--<theme>` names as the web references, and cover the resting states the design system draws itself: `swipe-pager` and `zoomable-image` on all four targets; the `action-sheet` list on Compose, Flutter and React Native; the `swipe-actions` full-swipe background and the non-modal `detent-sheet` peek on Compose and Flutter. System-drawn sheets, dialogs and iOS swipe buttons are left to the platform. `FIDELITY.md` lists what each target covers.
- New reusable pieces the snapshots render: `DsSwipeBackground` and `DsActionList` (Compose, Flutter), `DsActionList` (React Native).

### Changed
- SwiftUI `DSZoomableImage` takes any view: `DSZoomableImage(label:) { Image("photo").resizable().scaledToFit() }` (was `DSZoomableImage(_ image: Image, label:)`).
- Flutter non-modal `DsDetentSheet` sizes its peek from its own height, not the screen's, so it works inside any layout.

## [1.4.0] - 2026-10-23

### Added
- **`mobile` scope** (opt-in, `ds init --scopes product,mobile`): 7 touch and drag components in a new **Mobile & Gestures** category. `swipe-actions` and `action-sheet` (core); `pull-to-refresh`, `detent-sheet` (snap heights with a working handle), `swipe-pager` and `collapsing-app-bar` (standard); `zoomable-image` (enterprise). Manifest now has 539 components, 42 categories and 19 scopes. Specs in `references/components/mobile.md`, including a **gesture contract** for every scope: a visible non-drag path for each gesture (WCAG 2.5.1, 2.5.7), act on release, scroll snap before script, `touch-action` per axis, keyboard parity, reduced motion, RTL.
- **Scope tokens** `size.sheet.peek` (96 px) and `size.swipe-action` (80 px), shared by web CSS and the native scaffold.
- **Native gesture wrappers:** with the `mobile` scope on, `ds mobile scaffold` also writes `DSGestures.swift`, `DsGestures.kt`, `ds_gestures.dart` and `DsGestures.tsx`. They wrap each platform's own components (`.swipeActions`, `.presentationDetents`, `SwipeToDismissBox`, `PullToRefreshBox`, `Dismissible`, `DraggableScrollableSheet`, `RefreshControl`, …) with tokens and a non-drag path. React Native uses core APIs only. `FIDELITY.md` lists what each file wraps; CI compiles them on all four targets.
- `references/mobile.md`: the web-to-native table maps every gesture component to its platform built-in.

### Changed
- `bottom-sheet`, `sortable-list` and messaging swipe rows point to the new components and gesture rules (text only; no new demos for existing systems).

## [1.3.1] - 2026-10-21

### Changed
- **`ds` is the command everywhere:** help (`usage: ds …`), messages, generated file headers, SKILL.md, README, references and plugin commands say `ds <command>`. `python3 <skill-dir>/scripts/ds.py` is the fallback when `ds` isn't installed, can't run, or is an older install. SKILL.md tells agents when to switch. Hooks, CI templates and generated package scripts still call the script by path, because they run where `ds` may not be on PATH.

## [1.3.0] - 2026-10-21

### Added
- **Homebrew:** `brew install AntonBronnfjell/tap/html-design-system` installs the `ds` command. The `homebrew` workflow points the tap's formula at each published release, and the tap's CI installs and tests it.
- **`ds` command:** user-level installs put a launcher at `~/.local/bin/ds` (`ds.cmd` on Windows) that runs the installed `scripts/ds.py`, so `ds build ./design-system` works from anywhere. The installer warns when `~/.local/bin` isn't on PATH or another `ds` comes first, never overwrites a `ds` it didn't create, and `--uninstall` removes it. Skip it with `--no-cli`.

## [1.2.0] - 2026-10-17

### Added
- **13 new opt-in scopes** (manifest now 532 components in 41 categories, 3 tiers and 18 scopes; 340 components in opt-in scopes, 192 in `product`): `playback` 11 (base for media, added automatically), `video` 16, `live` 12, `music` 17, `podcast` 12, `reading` 21, `messaging` 28, `billing` 19, `analytics` 17, `erp` 16, `calendar` 15, `maps` 13, `social` 17. Each has a spec in `references/components/<scope>.md`.
- **Scope dependencies:** `scope_requires` in the manifest (`video`, `music`, `podcast`, `reading`, `messaging` require `playback`; `live` requires `video`), resolved by `expand_scopes()` in `ds.py`.
- **`requires_scopes` gating:** landing pages of consumer scopes (video, live, music, podcast, reading, messaging, social) carry `requires_scopes: [marketing]` and are only planned when `marketing` is on.
- **Product additions** (`product` 180 to 192): settings suite (profile, account, security, notifications, privacy, appearance, sessions, connected apps, data), `notification-inbox`, `preference-matrix`, `notification-permission-prompt`. Tiers across app UI: core 68, standard 78, enterprise 46.
- **Upgrade note:** existing standard/enterprise systems gain 8/12 new uncovered product pages (settings suite and related); `ds.py plan` lists them. After adding scopes by hand to `ds.config.json`, run `ds.py init <dir> --force` to copy scope tokens; `ds.py check` warns when they are missing.
- Plugin eval case 4 (podcast app with marketing site: scopes, auto-added playback, build plan).

### Changed
- `ds.py init --scopes` help lists the manifest's scopes.
- `test_all_scopes` covers every scope; the manifest component floor is raised to 532.
- README, SKILL.md, plugin manifests and builder brief updated for the new counts and scopes.

### Fixed
- `ds.py` category titles fall back to manifest names, so Storybook works for the new categories.
- Skill hooks no longer fail when `CLAUDE_SKILL_DIR` is unset (plugin installs, other tools): they fall back to `CLAUDE_PLUGIN_ROOT`, then `~/.claude/skills/html-design-system`, and exit quietly if `ds.py` is not found. Before, the missing path made python exit 2, which Claude Code treats as a blocking hook error (a Stop hook could keep the session from ending).

## [1.1.0] - 2026-10-08

### Added
- **Mobile migration** (`references/mobile.md`): `ds.py mobile spec` (tokens per theme with absolute type metrics, shadows and motion; Playwright-measured boxes of every demo at 390 px; @3x reference PNGs), `mobile scaffold` (SwiftUI, Jetpack Compose, Flutter, React Native themes + 10 core components + snapshot tests + `FIDELITY.md`; .NET MAUI resources; `web-mobile.css` for Ionic/Capacitor/PWA), `mobile verify` (stdlib PNG decoder, OKLab ΔE diff, size check, diff images, report, exit 1 on drift; optional numeric comparison), `mobile lint` (raw colors, magic numbers, fixed fonts, hover, small touch targets, foreign icons). Measured values are snapped to the token that has them, and colors the web paints with another token follow the web.
- The PostToolUse hook lints Swift, Kotlin, Dart and TS/TSX edits in apps scaffolded with `--out` (`.ds-mobile.json` marker).
- **Icons** (`references/icons.md`): `icons-add` (Lucide, Tabler, Phosphor, Heroicons, Material Symbols from jsDelivr at a pinned version, license recorded, unsafe SVG refused, mirror via `DS_ICON_CDN`), `icons-style` (measured style contract, or derived from tokens), `icons-lint` (viewBox, paint, stroke, caps/joins, live area, forbidden elements, complexity) for icons drawn from scratch, and `icons --platforms` for SwiftUI asset catalogs + `DSIcon`, Compose `ImageVector`s + VectorDrawables, Flutter `DsIcon`, React Native `DsIcon`.
- Plugin commands `/html-design-system:mobile` and `/html-design-system:icons`; plugin descriptions and keywords cover mobile and icons.
- Docs: `references/mobile.md`, `references/icons.md`; mobile/icon sections in the README, SKILL.md, testing, builder brief, adapters, imagery, companion skills, CONTRIBUTING and the Fleetline example.
- CI job that compiles the generated code on real SDKs: Swift against the iOS SDK, Compose with Gradle, Flutter analyze + golden run, React Native `tsc --strict`.

## [1.0.0] - 2026-10-08

First tagged release.

### Added
- **Skill:** discover → decide (extend / adopt / new) → tokens → plan → build → verify → ship workflow; scoped Claude Code hooks (post-edit lint, stop gate during build); works in Claude Code, Codex, Cursor, Copilot, Gemini CLI, Windsurf, Cline, Kiro, Roo, OpenCode, Amp, Goose, Junie, Continue.
- **Manifest:** 306 components in 16 categories, 3 tiers and 5 scopes (`product` + opt-in `marketing`, `ai`, `commerce`, `email`), each with required variants/states, ARIA pattern and native element, and a spec in `references/components/`.
- **Tokens:** DTCG 2025.10 with color objects (sRGB, OKLCH, Display P3, …), resolver file, light/dark/high-contrast themes, subtree themes, density, elevation pairs, state layers; contrast checked from color components in every theme; `migrate-colors` for legacy hex tokens.
- **ds.py (stdlib):** `detect`, `audit`, `init`, `build`, `check`, `coverage`, `plan`, `phase`, `status`, `sync`, `serve`, `storybook` (html or server renderer), `design-md` (Google DESIGN.md format + ACCESSIBILITY.md), `llms`, `mcp`, `email`, `package`, `ci`, `migrate-colors`, `palette`, `scale`, `export` (Tailwind, shadcn, Figma, iOS, Android, Compose, Flutter), `icons`, `taste`.
- **Existing projects:** stack detection for 18 frameworks and monorepos, ownership ledger (never overwrites files it didn't create or that you edited), `--dry-run`, `--force-all`, sync into the app's conventional folders, Storybook composition and GitLab include snippets instead of editing project files.
- **Agents:** generated `llms.txt`, per-component Markdown, `dist/ds-index.json` and a stdlib MCP server.
- **Packaging:** Claude Code plugin + marketplace, Cursor and Codex plugin manifests, cross-agent installer (`install.py`/`.sh`/`.ps1`), MIT license.
- **Quality:** stdlib unit tests with golden outputs, CI for Python 3.8–3.14 on Linux/macOS/Windows with `claude plugin validate`, plugin eval cases.
- **Example:** `examples/fleetline`, a complete core-tier system (68/68) built with the skill and published to GitHub Pages with Storybook (311 stories). It passes `check --strict`, `taste --strict` and the DESIGN.md lint; axe and keyboard checks pass on 211/212 page × theme combinations.
- **Shared JS** for generated systems: `js/lib/invokers.js` (fallback for `commandfor`/`command`), plus `ds:themechange` events between the docs toolbar and `theme.js`. A `size.sticky-offset` token drives `scroll-padding` so focused elements aren't hidden under sticky headers.
- **Component contract:**
  - readable hint text under disabled controls;
  - selected fills recolor all their descendant text;
  - links inside tinted fills follow the fill's text color;
  - unique landmark labels on docs pages;
  - frozen demo states don't animate.
  - The error summary moved to core, because the core form-layout pattern depends on it.
- **References:** decision guide, tokens, component contract, CSS architecture, conventions, motion, content design, performance, testing (incl. visual regression), packaging, governance (incl. accessibility law), Storybook for every stack, email build, companion skills.
