# Decision guide: which design system to build

The first real decision is not colors — it's **where the design comes from**. Get this wrong and every later token is wasted. Pick exactly one mode and record it in `ds.config.json → direction`.

## Contents
1. The three modes
2. Signals to look for (Phase 0 evidence)
3. Choosing a reference system (adopt mode)
4. Creating a new visual direction (new mode)
5. Brief questions to ask the user
6. Recording the decision (ADR)

## 1. The three modes

| Mode | Use when | What you produce |
|---|---|---|
| **extend** | The product already has a de-facto design (CSS variables, Tailwind theme, Figma library, brand guide, consistent screens). | Extract and normalize existing values into tokens; fill gaps; keep the look. Never "redesign" silently. |
| **adopt** | No design yet, but the team wants proven conventions (enterprise app, gov, internal tool), or a stack is mandated (Material for Android parity, Fluent for Microsoft 365 add-ins, Carbon for IBM-ish data tools). | Re-implement a reference system's structure (token tiers, component inventory, behavior) in plain HTML/CSS with the brand's skin. |
| **new** | Greenfield product, distinctive brand matters (consumer, marketing-heavy, startup). | Fresh visual direction from `/ui-ux-pro-max`, built on the same structural rigor. |

Hybrids are fine and common: *adopt* Carbon's structure + *new* brand palette. Record both.

## 2. Signals to look for

Run these before deciding (Phase 0):

- `python3 <skill-dir>/scripts/ds.py audit <repo>` — counts distinct colors, spacings, radii, fonts, custom properties, Tailwind classes, and component-named files.
  - **< ~20 distinct colors and existing `--custom-properties`** → a system exists: *extend*.
  - **Hundreds of one-off hex values / px values** → no system: consolidate (extend with heavy cleanup) or *new*.
  - **Tailwind config / shadcn `components.json`** → extend; also emit a Tailwind adapter via `/ui-styling`.
- `/graphify <repo>` on larger codebases — find the god nodes (shared Button/Modal/theme files) and which components import which tokens. This tells you what the *real* component inventory is and what's duplicated (three different modals = consolidation target).
- Figma URL provided → use the Figma MCP (`get_variable_defs`, `get_design_context`, `search_design_system`) to pull variables and components; that's an *extend* source of truth.
- Brand guidelines PDF / logo only → *new* (or *adopt* + brand skin), seeded with the brand colors and type.

## 3. Choosing a reference system (adopt mode)

| Reference | Strong at | Pick when |
|---|---|---|
| IBM **Carbon** | Data-dense enterprise, data tables, 2x grid, themes (white/g10/g90/g100) | Admin consoles, analytics, B2B SaaS |
| **Material 3** | Dynamic color, motion, mobile parity, elevation via tonal surfaces | Android-adjacent products, consumer apps |
| Microsoft **Fluent 2** | Office-style productivity, density, high-contrast | Productivity, Microsoft ecosystem |
| Shopify **Polaris** | Merchant admin, forms, index tables, content guidelines | Commerce back-offices |
| **Atlassian** DS | Collaboration tools, tokens naming, elevations | Work management |
| Adobe **Spectrum** | Accessibility, internationalization, scale (desktop/mobile) | Creative / pro tools, multi-platform |
| GitHub **Primer** | Developer tools, compact density, functional color | Dev tools |
| **GOV.UK** / **USWDS** | Plain, robust, accessibility-first forms & error summaries | Public sector, transactional services |
| **Radix / shadcn** | Unstyled accessible behavior, CSS-variable theming | Teams wanting minimal opinions + Tailwind |

Borrow **structure and behavior** (inventory, states, ARIA, token tiers, naming); don't copy trademarks, logos, or proprietary icon sets. Name the reference in `direction.reference_system`.

## 4. Creating a new visual direction (new mode)

1. Invoke `/ui-ux-pro-max` and run its design-system generator with the product context, e.g.
   `python3 <ui-ux-pro-max>/scripts/search.py "<product type> <industry> <keywords>" --design-system -p "<Name>" -f markdown`
   Tune with `--variance/--motion/--density 1-10` (dense enterprise ≈ density 8, motion 3).
2. Deep-dive any uncertain dimension with `--domain color|typography|style|ux`.
3. Translate the output into tokens (see `tokens.md` §4): palette → primitives, roles → semantic, fonts → `font.family`, style keywords → radius/shadow/motion choices.
4. Sanity-check distinctiveness with `/frontend-design` guidance if the result reads as a generic template.
5. **Allocate the style** when the direction mixes looks (e.g. editorial serif + brutalist accents + calm UI): record in `direction.allocation` which surfaces each look *owns* and what it is *never used for*, plus a budget ("one expressive moment per screen"). Without this, the loudest style leaks into every form and table.
   ```json
   "allocation": [
     { "name": "Editorial", "owns": "page titles, empty states, marketing sections", "never": "data tables, forms" },
     { "name": "Functional", "owns": "all controls, navigation, data", "never": "hero moments" }
   ]
   ```
6. Decide motion personality, bans and signature moments (`motion.md`) and record them in `ds.config.json → motion`.

## 5. Brief questions (ask only what Phase 0 couldn't answer)

Batch these into one AskUserQuestion round, max 4:
- Product type & primary users (enterprise data tool? consumer? public service?)
- Existing assets: repo / Figma / brand guide / none
- Scope tier: core (MVP, 65 items) · standard (109) · enterprise (all 136) — default **enterprise** when the user asks for "complete"
- Delivery targets beyond HTML/CSS: Tailwind theme, shadcn theme, React wrappers, Figma variables
- Constraints: a11y target (default WCAG 2.2 AA), RTL languages, dark mode required, density needs, browser support

## 6. Recording the decision

Append to `ds.config.json → decisions` (lightweight ADR):

```json
{ "id": "ADR-001", "date": "2026-10-07", "title": "Adopt Carbon structure with Acme brand skin",
  "context": "B2B analytics; audit found 212 distinct colors, no tokens", "decision": "mode=adopt+new",
  "consequences": "Data table + 2x grid from Carbon; palette from ui-ux-pro-max" }
```

Every later non-obvious choice (8px vs 4px grid, focus style, radius language) gets an ADR too — that's what makes the system maintainable.
