# Tokens & foundations

## Contents
1. Three tiers
2. File layout & format (DTCG)
3. Naming
4. Filling tokens from a direction
5. Required groups by tier
6. Themes, density, RTL
7. Contrast & validation
8. Gotchas

## 1. Three tiers

| Tier | File | Example | Who references it |
|---|---|---|---|
| Primitive | `tokens/primitive.json` | `color.blue.600 = #2563eb`, `space.4 = 1rem` | Only semantic tokens |
| Semantic | `tokens/semantic.json` (+ `tokens/themes/*.json` overrides) | `color.action.primary.bg = {color.blue.600}` | Component tokens and component CSS |
| Component | `tokens/component.json` (shared examples) + `tokens/components/<file>.json` (one per component file) | `button.radius = {radius.md}` | That component's CSS |

Why: rebranding = edit primitives; dark mode = override semantic; one-off component tweak = component token. Component CSS must never reach for a primitive (`--color-blue-600`) — lint can't catch every case, so review for it.

## 2. File layout & format

W3C Design Tokens Community Group format (DTCG 2025.10): every token is an object with `$value`, optional `$type`, `$description`; groups may set `$type` for children; aliases are `"{path.to.token}"`.

```json
{ "space": { "$type": "dimension", "4": { "$value": { "value": 1, "unit": "rem" } } },
  "color": { "$type": "color", "text": { "default": { "$value": "{color.gray.900}" } } } }
```

`ds.py build` merges primitive + semantic + component into `:root`, and each `tokens/themes/<name>.json` into `:root[data-theme="<name>"]` (plus `prefers-color-scheme: dark` for `dark`, `prefers-contrast: more` for `high-contrast`). Output: `dist/tokens.css`. Composite `typography` tokens become sub-properties: `--typography-h1-font-size`, `--typography-h1-line-height`, …

Supported `$type`s: color, dimension, fontFamily, fontWeight, number, duration, cubicBezier, shadow (single or list), border, transition, typography. Colors as hex strings (hex8 for alpha) so contrast can be verified.

## 3. Naming

`<category>.<concept>.<variant>.<state>` — lowercase, hyphens inside a segment.
- `color.action.primary.bg-hover`, `color.feedback.danger.fg`, `color.border.focus`
- Name by **role, not appearance**: `color.text.muted`, never `color.text.gray`.
- Component tokens: `<component>.<property>[.<variant>]` → `button.height.md`, `card.padding`.
- CSS var = path with dots → hyphens: `--color-action-primary-bg-hover`.

## 4. Filling tokens from a direction

| Direction input | Becomes |
|---|---|
| Brand / primary color | Generate a 50–950 ramp in `color.<brand>`; `action.primary.bg` = the step that gives ≥4.5:1 with its fg (usually 600 on light, 400–500 on dark) |
| Neutral choice (cool/warm/pure gray) | `color.gray` ramp; drives all bg/text/border roles |
| Status colors | `red/green/amber/blue` ramps → `feedback.*` (bg 50 / fg 900 / border 200 / icon 600–700 light; inverted for dark) |
| Font pairing | `font.family.sans` (UI), `serif`/display if any, `mono` |
| Type scale (e.g. 1.2 minor third, 1.25 major third) | `font.size.xs…5xl`; dense enterprise ≈ 14px body option |
| Base grid (4 or 8px) | `space.*` (keep 4px steps available even on 8px grids) |
| Style keywords (soft/rounded, sharp/brutalist, glass) | `radius.*`, `shadow.*`, `border.width.*`, overlay blur |
| Motion personality | `motion.duration.*`, `motion.easing.*` (enterprise: fast & subtle) |
| Density (comfortable/compact) | `density.*` + `size.control.*` |
| Existing CSS vars / Tailwind theme (extend mode) | Map 1:1 into primitives, keep their names in `$description` for traceability |

## 5. Required groups (checked by `ds.py check`)

- **core:** color, font, space, radius, shadow, border, motion, z, breakpoint, size, focus — themes: light (default) + dark
- **standard:** + opacity, density, icon
- **enterprise:** + dataviz — themes: + high-contrast

Also expected (not machine-checked): `typography` composites for display, display-lg, h1–h6, lead, body, small, caption, code.

Marketing scope: `section.padding-block.{sm,md,lg}`, `section.gap`, `section.max-inline` define landing-page rhythm. String values such as `clamp(3.5rem, 9vw, 6rem)` are allowed for fluid sizes (DTCG has no clamp type; the build passes strings through).

## 6. Themes, density, RTL

- **Themes** override semantic tokens only; never redefine primitives in a theme file.
- Apply `data-theme` on `<html>` for the page. For a **subtree** (an always-dark media stage, an inverted promo band) use `class="theme-dark"` (or `data-theme` on the element): `ds.py build` emits every theme as `[data-theme=x], .theme-x` and redeclares the themed semantic tokens there, so they resolve against that subtree's theme. A `.theme-light` block is generated too, for light islands inside dark pages.
- Each theme sets `color-scheme`, so native controls and scrollbars match. Mark a custom dark theme with `"$extensions": {"color-scheme": "dark"}`.
- Runtime switching, persistence and no-flash first paint: `js/theme.js` (copied by `ds.py init`).
- **Density:** `[data-density="compact"]` swaps `--size-control-*` / padding vars in component CSS (`.btn { padding-inline: var(--density-comfortable-control-padding-x) }` and a compact override).
- **RTL:** use logical properties everywhere (`margin-inline-start`, `inset-inline-end`, `padding-block`); mirror directional icons with `:dir(rtl) .icon--directional { transform: scaleX(-1) }`. Docs pages have an RTL toggle — check every component in it.

## 7. Contrast & validation

`ds.config.json → contrast_pairs` lists `[fg, bg, min]`; `ds.py check` resolves each pair in every theme and fails below the minimum. Defaults cover text (4.5:1), UI boundaries & focus (3:1, WCAG 1.4.11), action fg/bg, feedback, selected. **Add a pair whenever you add a new fg/bg combination** (e.g. a badge, a tag color) — it's the cheapest a11y guarantee in the system.

## 8. Gotchas

- CSS custom properties cannot be used in `@media` queries — `ds.py build` also writes `dist/tokens.scss` (`$breakpoints`, `@include up(md)` / `down(md)`) and `dist/tokens.json` (resolved values for JS, charts, animations). Plain CSS: mirror the literal values or use container queries.
- Renaming a token: add `"$deprecated": {"old.path": "new.path"}` to the token file; the build emits an alias var with a deprecation comment for one major version.
- Fonts are part of the foundations: decide self-hosting and subsets in Phase 2 (see `packaging.md`).
- Don't put `!important` or raw values in components to "fix" a token; fix the token.
- Keep primitives exhaustive but semantic tokens *few*: if two semantic tokens always share a value and a meaning, merge them.
- After editing any `tokens/*.json`, the PostToolUse hook rebuilds `dist/tokens.css` and reports errors; if hooks aren't active, run `ds.py build`.
