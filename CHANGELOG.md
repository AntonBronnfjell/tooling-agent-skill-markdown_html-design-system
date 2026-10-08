# Changelog

All notable changes to this skill. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [Semantic Versioning](https://semver.org/). The version lives in `.claude-plugin/plugin.json` (and the Cursor/Codex manifests); plugin users only receive updates when it changes.

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
- **References:** decision guide, tokens, component contract, CSS architecture, conventions, motion, content design, performance, testing (incl. visual regression), packaging, governance (incl. accessibility law), Storybook for every stack, email build, companion skills.
