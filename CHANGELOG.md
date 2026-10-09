# Changelog

All notable changes to this skill. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [Semantic Versioning](https://semver.org/). The version lives in `.claude-plugin/plugin.json` (and the Cursor/Codex manifests); plugin users only receive updates when it changes.

## [1.1.0] - 2026-10-08

### Added
- **Mobile migration** (`references/mobile.md`): `ds.py mobile spec` (tokens per theme with absolute type metrics, shadows and motion; Playwright-measured boxes of every demo at 390 px; @3x reference PNGs), `mobile scaffold` (SwiftUI, Jetpack Compose, Flutter, React Native themes + 10 core components + snapshot tests + `FIDELITY.md`; .NET MAUI resources; `web-mobile.css` for Ionic/Capacitor/PWA), `mobile verify` (stdlib PNG decoder, OKLab ΔE diff, size check, diff images, report, exit 1 on drift; optional numeric comparison), `mobile lint` (raw colors, magic numbers, fixed fonts, hover, small touch targets, foreign icons). Measured values are snapped to the token that has them, and colors the web paints with another token follow the web.
- The PostToolUse hook lints Swift, Kotlin, Dart and TS/TSX edits in apps scaffolded with `--out` (`.ds-mobile.json` marker).
- **Icons** (`references/icons.md`): `icons-add` (Lucide, Tabler, Phosphor, Heroicons, Material Symbols from jsDelivr at a pinned version, license recorded, unsafe SVG refused, mirror via `DS_ICON_CDN`), `icons-style` (measured style contract, or derived from tokens), `icons-lint` (viewBox, paint, stroke, caps/joins, live area, forbidden elements, complexity) for icons drawn from scratch, and `icons --platforms` for SwiftUI asset catalogs + `DSIcon`, Compose `ImageVector`s + VectorDrawables, Flutter `DsIcon`, React Native `DsIcon`.
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
