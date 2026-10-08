# Imagery, illustration and print

## Contents
- Images
- Dark mode images
- Illustration
- Icons
- Data visualization colors
- Print

## Images
- Fixed aspect-ratio tokens or utilities (`16/9`, `4/3`, `1/1`, `3/2`) plus `object-fit: cover`. Always set `width`/`height` attributes (or `aspect-ratio`) so nothing shifts while loading.
- Responsive: `srcset` + `sizes`, AVIF/WebP via `<picture>`. The LCP image (usually the hero) gets `fetchpriority="high"` and is never lazy; everything else gets `loading="lazy" decoding="async"`.
- **Alt text**: describe the purpose, not the pixels ("Dashboard showing weekly deliveries by region"); `alt=""` for decorative images and for avatars next to a visible name; never "image of…". Text in images must also be in the HTML.
- Captions with `<figure>`/`<figcaption>`; credits and licenses recorded.

## Dark mode images
- Photos usually work in both themes; tune them with a subtle overlay rather than replacing them.
- Screenshots, diagrams and logos need theme variants:
  ```html
  <picture>
    <source srcset="diagram-dark.png" media="(prefers-color-scheme: dark)">
    <img src="diagram-light.png" alt="…" width="800" height="450">
  </picture>
  ```
  `prefers-color-scheme` follows the OS, not a manual `data-theme` toggle. For in-page switching, use inline SVG colored with tokens (`fill: var(--color-text-default)`), `light-dark()` inside the SVG's styles, or swap `src` in `theme.js` `onThemeChange`.
- Logos on dark surfaces: provide a reversed version; never invert a full-color logo with filters.

## Illustration
- Record an illustration ADR: style (flat, outlined, isometric, 3D), stroke width matching the icon set, the palette restricted to token colors, how people are depicted (diverse, non-stereotyped), and where illustration is allowed (empty states, onboarding, marketing — not in dense work surfaces).
- Ship SVG; colors as `currentColor` or token custom properties so illustrations follow themes and brands.
- Decorative illustrations are `aria-hidden="true"`; meaningful ones get a text alternative.

## Icons
- One set, one stroke width, one grid (24px), built into a sprite with `ds.py icons <svg-dir> <ds-dir> --license "<set> (<license>)"`. Licenses: Lucide ISC (parts from Feather MIT), Phosphor MIT, Tabler MIT, Heroicons MIT, Material Symbols Apache-2.0.
- Sizes come from `icon.size.*`; color from `currentColor`. Icon-only buttons need an accessible name and a tooltip.

## Data visualization colors
- Categorical palette: `dataviz.categorical.1…8` (color-blind-safe defaults). For brand-matched sets, generate hues with equal OKLCH lightness and chroma, at least 30° apart, each ≥ 3:1 against the chart surface (`ds.py palette` per hue, then pick the same step from each ramp).
- Sequential: one ramp light→dark; diverging: two ramps meeting at a neutral midpoint.
- Never color alone: pair with labels, patterns or direct annotation. Provide a data table alternative. Detailed chart guidance: `references/components/data-display.md` (chart parts) and the `/dataviz` skill when available.

## Print
`base.css` ships a print layer: light colors, navigation/dialogs/popovers hidden, external link URLs printed after links, cards/tables/figures kept on one page, headings kept with their content. Add `data-print="hide"` (or `.ds-no-print`) to anything else that shouldn't print. Test with the browser's print preview for invoices, receipts, legal pages and reports.
