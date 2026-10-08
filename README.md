# html-design-system

Agent skill (Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI, Windsurf, Cline, Kiro, Roo, OpenCode, …) that decides **which** design system a product needs (extend what exists, adopt a reference system such as Carbon / Material 3 / Fluent 2 / Polaris, or create a new direction) and then builds a **complete** HTML/CSS design system: DTCG tokens with light / dark / high-contrast themes and all 130 components of the enterprise taxonomy, each with every state, WCAG 2.2 AA accessibility and a docs page.

Completeness is enforced by tooling, not memory: a machine-readable manifest, a stdlib-only CLI, and hooks that lint every edit and refuse to stop while the build is incomplete.

## Layout

```
./  (repo root = skill root)
├── SKILL.md                     workflow (discover → decide → tokens → plan → build → verify → ship) + hooks
├── assets/
│   ├── manifest.json            130 components · 8 categories · tiers core/standard/enterprise
│   └── templates/               DTCG tokens, themes, config, base.css, docs chrome, page template
├── scripts/ds.py                init · audit · build · check · coverage · plan · phase · status · hook entry points
├── hooks/settings.example.json  manual Claude hook snippet (the installer's --claude-hooks does this for you)
├── install.py / .sh / .ps1      cross-agent installer
└── references/                  decision guide, tokens, component contract, per-category specs, companions, governance
```

## Install (any agent)

Requires Python 3.8+ (the skill's own scripts use it too). From a clone (`git clone https://github.com/AntonBronnfjell/tooling-agent-skill-markdown_html-design-system.git`):

```bash
./install.sh                    # macOS / Linux — auto-detects installed agents
.\install.ps1                   # Windows PowerShell
python3 install.py --list       # see every supported agent, its path and status
```

| Option | Effect |
|---|---|
| `--tools all` / `--tools claude,cursor,kiro` | all known agents / a specific set (default `auto` = detected ones) |
| `--project <dir>` | install into a repo (`.claude/skills`, `.agents/skills`, …) so the team gets it on clone |
| `--link` | dev mode: Claude Code symlinks to this repo, so edits are live |
| `--claude-hooks` | also register the lint/coverage hooks in Claude `settings.json` (always-on; see below) |
| `--uninstall` | remove everything the installer created (only its own files and hooks) |
| `--dry-run` | preview |

Without cloning:

```bash
curl -fsSL https://raw.githubusercontent.com/AntonBronnfjell/tooling-agent-skill-markdown_html-design-system/main/install.sh | sh -s -- --tools all
```

```powershell
irm https://raw.githubusercontent.com/AntonBronnfjell/tooling-agent-skill-markdown_html-design-system/main/install.ps1 | iex
```

### Where it goes

| Agent | User-level location | Project-level | Notes |
|---|---|---|---|
| Claude Code | `~/.claude/skills/html-design-system` | `.claude/skills/` | Full SKILL.md: scoped hooks, `argument-hint`, live status |
| Codex, Cursor, Gemini CLI, GitHub Copilot, Windsurf/Devin, OpenCode, Amp, Goose, Junie | `~/.agents/skills/html-design-system` (shared standard) | `.agents/skills/` (Copilot, Cline, OpenCode, Amp, Goose also read project `.claude/skills/`) | Portable SKILL.md: Claude-only frontmatter keys removed for strict agentskills.io validators |
| Kiro · Roo Code · Cline | `~/.kiro/skills` · `~/.roo/skills` · `~/.cline/skills` | `.kiro/` · `.roo/` · `.cline/skills` | Symlink to the shared copy (copy on Windows without Developer Mode) |
| Continue | `~/.continue/rules/html-design-system.md` | `.continue/rules/` | Rule that points the agent at the skill |
| Aider | — | — | No skill support: installer prints the `read:` line for `.aider.conf.yml` |

Agents that read `~/.agents/skills` don't get a second copy in their own folder by default, which would list the skill twice. You can force one with `--tools cursor,copilot,gemini,windsurf,devin,opencode,junie,codex`.

### Hooks

- **Claude Code:** the hooks are declared in SKILL.md and run only while the skill is active.
- **Always-on hooks:** `--claude-hooks` adds them to `~/.claude/settings.json`, or to the project's settings with `--project`. Don't combine it with the skill-scoped hooks unless you're fine with each check running twice while the skill is active.
- **Gating:** both hooks stay silent outside a design system (no `ds.config.json`). The Stop gate only acts during the `build` phase. Soften it with `"gate": "warn"` or `"off"` in `ds.config.json`.
- **Other agents:** their hook formats differ and aren't installed. SKILL.md tells those agents to run `ds.py check` after each file and `ds.py coverage` before ending a turn. `hooks/settings.example.json` is a manual Claude snippet.

## Companion skills

Uses `/graphify` (existing-code discovery, final component↔token map), `/ui-ux-pro-max` (style, palette, fonts, UX rules), `/plan` (approval before building), `/ponytail` (native-first, minimal implementation), `/ui-styling` (Tailwind / shadcn adapters). All optional with documented fallbacks — see `references/companion-skills.md`.

## CLI quick reference

```bash
DS="python3 scripts/ds.py"
$DS audit ./src                         # what de-facto design system exists?
$DS init ./design-system --name Acme --tier enterprise
$DS build ./design-system               # tokens.css, ds.css, index.html
$DS check ./design-system --strict      # tokens, contrast (all themes), lint, coverage
$DS plan ./design-system                # what's left, grouped by file
```
