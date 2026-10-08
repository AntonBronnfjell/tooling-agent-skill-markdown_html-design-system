---
name: html-design-system
description: >
  Decides which design system to build (extend an existing design, adopt a reference
  system like Carbon/Material/Fluent/Polaris, or create a new visual direction) and then
  builds a COMPLETE HTML/CSS design system: DTCG design tokens with light/dark/high-contrast
  themes, and all 136 enterprise components (primitives, buttons, every form control,
  navigation, data tables, overlays, feedback, layout patterns) each with every state,
  accessibility (WCAG 2.2 AA, WAI-ARIA APG), and a documentation page, plus a generated
  Storybook, DESIGN.md contract, npm packaging and CI. Uses scripts and hooks to lint,
  check contrast and track coverage so nothing is skipped. Use this skill
  whenever the user wants to create, scaffold, audit, extend, finish or document a design
  system, UI kit, component library, style guide, pattern library, Storybook or design tokens for the
  web — even if they only say "build our components", "make a UI library", "we need
  consistent UI", "turn our CSS into a system", or list components to build.
argument-hint: "[new|extend <path>|adopt <system>|audit <path>|resume] [core|standard|enterprise]"
hooks:
  PostToolUse:
    - matcher: "Write|Edit|MultiEdit"
      hooks:
        - type: command
          command: python3 "${CLAUDE_SKILL_DIR}/scripts/ds.py" hook-post-edit
  Stop:
    - hooks:
        - type: command
          command: python3 "${CLAUDE_SKILL_DIR}/scripts/ds.py" hook-stop
---

# HTML Design System

Build a complete, accessible, token-driven HTML/CSS design system — and first, decide *which* design system it should be.

**Current state:** !`python3 "${CLAUDE_SKILL_DIR}/scripts/ds.py" status 2>/dev/null || echo "status unavailable — run ds.py status manually"`
(If that line shows a raw command, your tool doesn't expand it: run `python3 <skill-dir>/scripts/ds.py status` yourself.)

**Arguments:** `$ARGUMENTS` (mode and/or tier; empty means: discover, then ask)

## Why this skill is structured the way it is

A design system fails in two ways: it looks wrong for the product (wrong *direction*), or it has holes — a missing invalid state, a modal with no focus return, a dark theme where muted text is illegible (incomplete *coverage*). The direction is a judgment call, so it gets an explicit decision phase with research companions. Coverage is mechanical, so it's enforced by a machine-readable manifest (`assets/manifest.json`, 136 components across 8 categories and 3 tiers) plus scripts and hooks that tell you exactly what's missing. Trust the tools for coverage and spend your thinking on quality.

## Toolkit

`<skill-dir>` = the directory containing this SKILL.md (Claude Code exposes it as `${CLAUDE_SKILL_DIR}`). `ds.py` = `python3 <skill-dir>/scripts/ds.py` (Python 3.8+, stdlib only):

| Command | Does |
|---|---|
| `ds.py audit <repo>` | Inventory existing colors, spacing, fonts, radii, shadows, custom properties, Tailwind usage, component files |
| `ds.py init <dir> --name N --tier T` | Scaffold the system (tokens, themes, base CSS, docs chrome, page template, config) |
| `ds.py build <dir>` | Tokens → `dist/tokens.css`; bundle `dist/ds.css`; regenerate `index.html` with coverage |
| `ds.py check <dir> [--strict]` | Token validity, required groups/themes, contrast pairs in every theme, CSS/HTML lint |
| `ds.py coverage <dir>` / `plan <dir>` | What's missing per component / ordered build queue grouped by file |
| `ds.py phase <dir> <phase>` | Record phase: discover → decide → plan → build → done |
| `ds.py serve <dir>` | Preview the docs site at http://127.0.0.1:8000 (no dependencies) |
| `ds.py storybook <dir>` | Standalone Storybook (html-vite): one story per demo, token catalog, theme/density/RTL/motion toolbar, axe on every story |
| `ds.py design-md <dir>` | `DESIGN.md` — the one-file contract (themes with resolved values, type, scales, rules, inventory, decisions) |
| `ds.py package <dir>` / `ci <dir> --provider github\|gitlab` | npm exports for CSS/tokens/js; pipeline: check → Storybook to Pages → idempotent publish |

**Hooks (active while this skill is loaded):** after every Write/Edit of a file inside a design system, `hook-post-edit` lints it, rebuilds tokens when token JSON changes, and tells you which demos/doc sections that page still lacks. When phase is `build`, `hook-stop` blocks ending the turn while components are incomplete (once per turn — if you genuinely need the user, set phase to `plan` first). To keep hooks on outside this skill, see the README's project-hook snippet.
**No hooks in your tool** (Cursor, Copilot, Gemini, Codex, …)? Do their job by hand: run `ds.py check <dir>` after each file you finish, and `ds.py coverage <dir>` before you end any turn during the build phase — if it isn't complete, keep building.

## Workflow

### Phase 0 — Discover (what exists?)
1. Read the status line above. If a system exists, `resume`: run `ds.py plan <dir>` and jump to the matching phase.
2. Look for design sources: existing CSS/Tailwind/theme files, a component folder, Figma URLs, brand guides.
   - Run `ds.py audit <repo>` on any existing UI code.
   - For a sizable codebase, run **/graphify** on the UI directory to find shared theme/component hubs and duplicates.
   - Figma link → Figma MCP `get_variable_defs` / `get_design_context`.
3. Summarize findings in 5–10 lines: what exists, how consistent it is, what's duplicated.

### Phase 1 — Decide (which design system?)
Read `references/decision-guide.md`. Choose **extend**, **adopt** (name the reference system) or **new**; hybrids allowed.
- Ask the user only what discovery couldn't answer (one AskUserQuestion round: product/users, assets, tier, extra targets). If the user asked for "complete", the tier is `enterprise`.
- For a new or re-skinned direction, invoke **/ui-ux-pro-max** and run its `--design-system` generator with the product context; deep-dive color/typography/ux domains as needed.
- `ds.py init <project>/design-system --name "<Name>" --tier <tier>`, then fill `ds.config.json` `brief`, `direction` and an ADR in `decisions`. `ds.py phase <dir> decide`.

### Phase 2 — Foundations (tokens)
Read `references/tokens.md`. Replace the neutral starter values in `tokens/primitive.json`, `semantic.json`, `themes/*.json` with the chosen direction (extend mode: map existing values; keep their old names in `$description`). Add contrast pairs for any new fg/bg combinations. Run `ds.py build` and `ds.py check` until there are no token errors. Also decide here: fonts (self-hosted, subsets — `references/packaging.md`), motion personality/bans/moments (`references/motion.md` → `ds.config.json → motion`), and the style allocation if the direction mixes looks. Wire the theme runtime (`js/theme.js`, no-flash snippet).

### Phase 3 — Plan
Run `ds.py plan <dir>` and present the plan with **/plan** (plan mode) for approval: direction summary, token highlights, tier and component count, build order, which categories go to subagents, extra targets (Tailwind/shadcn via /ui-styling, Figma). Building 100+ files without sign-off on direction is the expensive mistake to avoid. After approval: `ds.py phase <dir> build`.

### Phase 4 — Build
Read `references/component-contract.md` (Definition of Done) once, and the matching `references/components/<category>.md` before each category.
1. **Reference implementation first, in the main thread:** `typography`, `stack`, `grid`, `icon`, then `button` and `form-field` + `text-field`, then `js/lib/` shared behaviors (roving focus, dismiss, position, hotkey, live region). These set conventions (class naming, demo layout, state-freezing classes, token usage, `init(root)` modules) that every other page copies.
2. **Fan out the rest** by category with parallel subagents using `references/builder-brief.md` (one subagent per category; patterns last because they compose everything). If subagents aren't available, continue serially in plan order.
3. Native first, minimal JS — apply **/ponytail** to *how* things are built, never to *what* is built: the manifest is the requirement.
4. If `targets` includes Tailwind/shadcn, use **/ui-styling** to generate the adapter from the semantic tokens. For React/Vue/Svelte/Angular/Web Components adapters follow `component-contract.md` §7 (folder anatomy, layers, API conventions; test → component → story).
Keep going until `ds.py coverage` is complete — hook messages tell you what's left after each edit.

### Phase 5 — Verify
- `ds.py check <dir> --strict` passes (no token errors, no lint, full coverage).
- Accessibility: run /accesslint `audit_html` on pages when available; otherwise walk the contract §5 checklist for each category.
- Visual: if a browser tool exists, screenshot representative pages in light/dark/high-contrast, compact density, RTL, and 320px width.
- Optional: /ponytail-review over `css/` and `js/`.
- Automated tests per `references/testing.md`: Storybook a11y (every story), Playwright + axe over every page × theme, unit tests for framework adapters.

### Phase 6 — Document & ship
`ds.py build` (regenerates `index.html` with live coverage), `ds.py design-md` (the contract), `ds.py storybook` (the independent workbench — `references/storybook.md`), and when it will be consumed by other repos `ds.py package` + `ds.py ci` (`references/packaging.md`). Write the system `README.md`, `CHANGELOG.md` (+ migration notes), `CONTRIBUTING.md` and principles per `references/governance.md`. Optionally run **/graphify** on the design system to produce a component↔token map for the docs. Then `ds.py phase <dir> done` and report: direction + rationale, tier, coverage numbers, check results, how to consume, and known gaps.

## Output layout

```
design-system/
├── ds.config.json            brief, direction, tier, phase, ADRs, contrast pairs
├── tokens/                   primitive / semantic / component JSON, themes/, components/<file>.json
├── dist/tokens.css, ds.css   generated — never edit
├── css/base.css              reset + focus + sr-only + reduced motion
├── css/components/*.css, css/patterns/*.css
├── js/theme.js, js/lib/*.js  theme runtime + shared behaviors; js/<file>.js only where native HTML can't
├── components/*.html, patterns/*.html   one docs page per manifest file
├── docs/                     docs chrome + page template
├── index.html                generated catalog with coverage
├── DESIGN.md                 generated contract
├── dist/tokens.json, tokens.scss   build-time tokens (media queries, JS)
├── .storybook/, stories/, package.json   generated workbench (`ds.py storybook`)
└── tools/ds/                 vendored ds.py for CI (`ds.py ci`)
```

## References (read when the phase calls for it)
- `references/decision-guide.md` — extend vs adopt vs new; reference systems; brief questions; ADRs
- `references/tokens.md` — tiers, DTCG format, naming, direction → tokens, themes/density/RTL, contrast
- `references/component-contract.md` — Definition of Done: markup convention, state matrix, CSS rules, native-first JS, a11y, docs
- `references/components/{foundations,actions,forms,navigation,data-display,overlays-feedback,patterns}.md` — per-component specs
- `references/builder-brief.md` — subagent prompt for parallel category builds
- `references/companion-skills.md` — when to use /graphify, /ui-ux-pro-max, /plan, /ponytail, /ui-styling and others, with fallbacks
- `references/motion.md` — motion vocabulary, bans, reduced-motion (media query + `data-reduced-motion`)
- `references/storybook.md` — docs site, generated Storybook, framework Storybooks (React/Vue/Svelte/Angular/WC), alternatives
- `references/testing.md` — Storybook a11y, Playwright + axe per page/theme, unit tests for adapters
- `references/packaging.md` — npm exports, fonts, framework library builds, release/versioning
- `references/governance.md` — DESIGN.md, versioning, migration guides, deprecation, contribution, adapters
- `assets/manifest.json` — the full component taxonomy (id, tier, file, required demos, ARIA pattern, native element)
