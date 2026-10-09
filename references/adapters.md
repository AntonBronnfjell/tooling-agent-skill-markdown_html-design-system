# Adapters and exports

`ds.py export <dir> --target <targets>` writes framework and platform outputs to `dist/exports/` from the same DTCG tokens — no Style Dictionary or Node needed. Re-run after every token change (or add it to CI).

## Contents
- Tailwind CSS v4
- shadcn/ui
- Figma
- iOS, Android, Compose, Flutter
- Multi-brand and palettes
- When to use Style Dictionary instead

## Tailwind CSS v4 (`--target tailwind`)
```css
@import "tailwindcss";
@import "@acme/design-system/ds.css";               /* tokens + components; its layers sort after Tailwind's */
@import "@acme/design-system/dist/exports/tailwind.css";
```
- Tailwind's own theme variables with the same names as ours (`--radius-*`, `--shadow-*`, `--breakpoint-*`) are overridden by the design-system token layer automatically, so `rounded-md` and `shadow-lg` use your tokens.
- `tailwind.css` adds an `@theme inline` block of **theme-aware aliases**: `bg-canvas`, `bg-surface`, `text-fg`, `text-fg-muted`, `bg-primary`, `text-on-primary`, `border-line`, `ring-ring`, `text-error`, …, plus every semantic color as `*-ds-<path>` (e.g. `bg-ds-feedback-danger-bg`), `font-sans/serif/mono`, `text-xs…7xl`, and `--spacing` = `--space-1` so `p-4` = `--space-4`.
- `inline` matters: utilities reference `var(--color-…)`, so dark mode and brands switch without rebuilding.
- If you use `/ui-styling`, it can build on this file instead of guessing a theme.

## shadcn/ui (`--target shadcn`)
`shadcn.css` defines shadcn's variable names (`--background`, `--foreground`, `--card`, `--popover`, `--primary(-foreground)`, `--secondary`, `--muted`, `--accent`, `--destructive`, `--border`, `--input`, `--ring`, `--radius`, `--chart-1…5`, `--sidebar-*`) as `var()` references to design-system tokens, plus a `.dark` block with the dark theme so shadcn's `.dark` toggle and the system's `[data-theme="dark"]` both work. Import it after `dist/ds.css` and before your app CSS. shadcn component markup keeps working; colors, radius and focus rings now come from your tokens and pass your contrast checks.

## Figma (`--target figma`)
- `figma/variables.json` is the request body for `POST /v1/files/:file_key/variables` (Figma Variables REST API): a **Primitives** collection (one mode) and a **Semantic** collection with one mode per theme (light, dark, high-contrast, …). Semantic variables are real **aliases** of primitives where the token is an alias, so Figma shows `primary → teal/700` just like the code. Colors are `{r,g,b,a}` 0–1, dimensions in px.
  ```bash
  curl -X POST "https://api.figma.com/v1/files/$FILE_KEY/variables" \
       -H "X-Figma-Token: $FIGMA_TOKEN" -H "Content-Type: application/json" \
       --data @dist/exports/figma/variables.json
  ```
  The write endpoint requires a full seat on an Enterprise plan. Re-posting creates duplicates — for updates, fetch existing ids first and switch actions to `UPDATE` (or delete the collections).
- `figma/<mode>.tokens.json` — resolved DTCG per mode for Figma's native variables import or plugins like Tokens Studio.
- With the Figma MCP available, `/figma-generate-library` can build components on top of these variables.

## iOS, Android, Compose, Flutter
| Target | Files | Dark mode |
|---|---|---|
| `ios` | `ios/DesignTokens.swift` — `DSColor.colorActionPrimaryBg` (SwiftUI `Color` over a dynamic `UIColor`), `DSDimension.space4` (pt) | resolved at runtime by `userInterfaceStyle` |
| `android` | `values/ds_colors.xml`, `values-night/ds_colors.xml`, `values/ds_dimens.xml` (dp; font sizes in sp) | resource qualifiers |
| `compose` | `DesignTokens.kt` — `DsColorsLight`, `DsColorsDark`, `DsDimensions` | pick the object from `isSystemInDarkTheme()` |
| `flutter` | `ds_tokens.dart` — `DsColorsLight`, `DsColorsDark`, `DsDimensions` | pick from `MediaQuery.platformBrightnessOf(context)` |

Semantic colors only (primitive ramps are left out on purpose: apps should use roles). Wide-gamut tokens are converted to sRGB. Fluid `clamp()` sizes have no native equivalent and are skipped.

## Multi-brand and palettes
- `ds.py palette '#0f766e' --name teal --dir <ds> --primary` adds a ramp and remaps primary/link/focus/selected in every theme, choosing steps by measured contrast.
- `ds.py palette '#c2410c' --name blue --dir <ds> --brand ember` writes `tokens/brands/ember.json`, overriding the `blue` ramp only for that brand. The build emits `[data-brand="ember"]` (set it on `<html>`, the same element as `data-theme`), the contrast check runs for every brand × theme, and `resolver.json` gains a `brand` modifier.
- Exports use the default brand; export per brand by building a copy with the brand file promoted (planned).

## When to use Style Dictionary instead
Use Style Dictionary (v5) or Terrazzo when you need custom transforms, many more platforms, or a JS build pipeline. They read the same `tokens/*.json` and `tokens/resolver.json`. Style Dictionary's DTCG 2025.10 support was still marked "work in progress" in its v5 docs, so check color-object support before switching.

## Full mobile apps
These exports are token files only. To ship components on iOS, Android, Flutter, React Native or MAUI with measured fidelity, use `ds.py mobile spec` + `ds.py mobile scaffold` (`references/mobile.md`).
