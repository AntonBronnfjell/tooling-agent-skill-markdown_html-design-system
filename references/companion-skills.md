# Companion skills & tools

This skill owns the **structure and completeness** of the system. Other installed skills supply specialist judgment. Use them at the phases below; if one isn't installed, follow the fallback — never block on a missing companion.

| Phase | Companion | What to ask it for | Fallback |
|---|---|---|---|
| 0 Discover | `ds.py detect` (built in) | Stack, monorepo, existing styles/tokens/Storybook/CI, safe location and sync targets — always first in an existing project | — |
| 0 Discover | **/graphify** | Knowledge graph of an existing codebase: god nodes (shared theme/Button/Modal files), duplicate components, which files consume which styles. Run `/graphify <repo-or-ui-dir>` then query: "which components define colors?", "what are the modal implementations?" | `ds.py audit <repo>` + grep for component files |
| 0 Discover | Figma MCP (`get_variable_defs`, `get_design_context`, `search_design_system`) | Pull existing variables/components when the user shares a Figma URL | Ask for exported tokens/screenshots |
| 1 Decide | **/ui-ux-pro-max** | Style, palette, font pairing, UX rules for the product type: `search.py "<product> <industry> <keywords>" --design-system -p "<Name>" -f markdown` (+ `--variance/--motion/--density`), then `--domain color|typography|ux` deep-dives | `decision-guide.md` tables + your own judgment; record rationale |
| 1 Decide | /frontend-design, /brand | Distinctive direction, avoid generic look; brand voice — essential for the marketing scope, where heroes and landing pages carry the brand | — |
| 2 Plan | **/plan** (plan mode) | Present the build plan (direction, tier, token decisions, file queue from `ds.py plan`, delegation strategy) for approval before writing 100+ files. Use EnterPlanMode/ExitPlanMode; the `writing-plans` skill if plan mode isn't available | Write the plan to `design-system/PLAN.md` and ask for approval |
| 3–4 Build | **/ponytail** | Native-first, no-dependency implementation: `<dialog>`, `popover`, `<details>`, native inputs, CSS over JS, one small module instead of a framework. Apply its YAGNI lens to *implementation*, never to *coverage* — the component list is the requirement | `component-contract.md` §4 |
| 3–4 Build | `ds.py export` (built in) | Tailwind v4, shadcn, Figma Variables, iOS/Android/Compose/Flutter outputs from the tokens (`adapters.md`) | — |
| 3–4 Build | **/ui-styling** | When `targets` includes Tailwind or shadcn: generate `tailwind` theme / shadcn CSS variables from `dist/tokens.css` (`tailwind_config_gen.py`), shadcn component mapping; also canvas-based visual assets | Hand-map tokens: Tailwind v4 `@theme { --color-*: var(--color-*) }` |
| 3–4 Build | /dataviz | Chart container & palette rules | `data-display.md` chart section |
| 5 Verify | /accesslint (`audit_html`, `audit_live`) | Automated WCAG audit of each page | Contract §5 checklist by reading |
| 5 Verify | /webapp-testing or browser tools | Screenshots in light/dark/RTL/compact, keyboard walkthrough | `ds.py check` + manual reasoning |
| 5 Verify | /ponytail-review | Over-engineering pass on `css/` and `js/` | — |
| 5 Verify | `ds.py taste`, `ds.py playwright` (built in) | Generic-AI-look lint; visual regression + axe + keyboard focus per page × theme | — |
| 6 Document | /graphify (again) | Graph of the generated system: components ↔ tokens ↔ JS, to spot orphan tokens and components bypassing semantic tokens; include `GRAPH_REPORT.md` in the docs | `grep -o 'var(--[a-z0-9-]*' css -r | sort | uniq -c` |
| 6 Document | design-systems:* plugin skills (governance, documentation-template, naming-convention) | Governance docs, contribution model | `governance.md` |

## Notes
- Invoke companions via the Skill tool by their exact names; scripts inside them are referenced by their own SKILL.md (e.g. ui-ux-pro-max's `scripts/search.py`). Resolve the path from that skill's base directory rather than hardcoding.
- /ponytail can conflict with "complete" if misapplied. Settle it in the plan: coverage = fixed by the manifest; *how* each component is built = as simple as the platform allows.
