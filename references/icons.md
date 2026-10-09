# Icons: library sets, icons drawn from scratch, and native icon components

Read this when the system needs icons: picking a set, adding icons, drawing a missing one, or shipping icons to apps.

## Rules
- **One set, one style.** Same grid (usually 24), stroke width, caps, joins, corner treatment and visual weight. Mixing Lucide with Material Symbols is the most common icon inconsistency.
- Icons paint with `currentColor` only; size comes from `icon.size.*`; never hard-code a color.
- Decorative icons are hidden from assistive tech; meaningful icons get a name (`aria-label`, `accessibilityLabel`, `contentDescription`, `semanticsLabel`). Icon-only buttons need an accessible name and a tooltip.
- Directional icons (arrows, chevrons, "reply", progress) mirror in RTL; others (clock, checkmark, logos, media play) don't.
- Record the set and its license. Lucide ISC, Tabler MIT, Phosphor MIT, Heroicons MIT, Material Symbols Apache-2.0.

## 1. From a library — `ds.py icons-add`
```bash
ds.py icons-add truck wrench gauge --set lucide --dir <ds> [--version 1.53.0] [--platforms all]
```
Sets: `lucide`, `tabler`, `tabler-filled`, `phosphor`, `heroicons`, `heroicons-solid`, `material-symbols` (names as in the set, e.g. `arrow_forward`). Fetches SVGs from jsDelivr at a pinned version (latest resolved once and written down), refuses anything that isn't a plain SVG (scripts, event handlers, external references), saves to `icons/src/`, appends `icons/LICENSES.md`, rebuilds `dist/icons.svg` and the gallery. It warns when the folder already holds another set. `DS_ICON_CDN` points it at a mirror (`file://` works) for offline or air-gapped builds.

## 2. The style contract — `ds.py icons-style`
```bash
ds.py icons-style icons/src --dir <ds>   # measure the existing set
ds.py icons-style --dir <ds>             # no icons yet: derive from tokens
```
Writes `icons/style.json`: viewBox/grid, paint model (stroke or fill), stroke width, caps, joins, live-area padding (10th percentile of the set), corner radius, complexity range. Without reference icons the style comes from the system: `icon.stroke` for the stroke, round caps/joins when `radius.md ≥ 4` (soft shapes) else square/miter, a 24 grid with 2 px padding.

## 3. Drawing a new icon from scratch
When no set has the concept (a product-specific object, a brand action):
1. Read `icons/style.json` and open 3–5 neighbors from `icons/src/` with similar shapes; copy their construction (how they draw a rectangle, a circle, a corner).
2. Draw on the grid: geometry inside the live area (24 grid, 2 px padding → 2..22), whole or half-pixel coordinates, `stroke="currentColor"` + the set's stroke width, caps and joins, `fill="none"` for stroke sets. Reuse the set's primitives (same corner radius, same circle sizes). No text, transforms, masks, filters, embedded images or styles.
3. `ds.py icons-lint icons/src/<name>.svg --dir <ds>` until it passes (errors exit 1: viewBox, hard-coded paint, forbidden elements, paint model, stroke width, caps/joins, geometry outside the viewBox; warnings: entering the padding, complexity far from the set, transforms).
4. Rebuild (`ds.py icons icons/src <ds>`) and review `docs/icons.html` in light and dark, next to its neighbors at 16, 20 and 24 px. Optical size matters: a filled square looks bigger than a stroked circle with the same box; nudge until the weights match.
5. Add the icon to the system's icon docs with when-to-use notes.

## 4. Native icon components — `ds.py icons … --platforms`
```bash
ds.py icons icons/src <ds> --platforms swiftui,compose,flutter,react-native   # or all
```
Writes `dist/icons/<platform>/` from the optimized sprite (and `ds.py mobile scaffold` copies them into each target's `icons/`):

| Platform | Output | Use |
|---|---|---|
| SwiftUI | `Icons.xcassets/<name>.imageset` (SVG, vector preserved, template rendering) + `DSIcon.swift` enum | `DSIconView(.truck, size: 20, label: "Truck")` or `DSIcon.truck.image` |
| Compose | `DsIcons.kt` (`ImageVector`s via `addPathNodes`) + `drawable/ds_icon_*.xml` VectorDrawables for Views | `Icon(DsIcons.Truck, contentDescription = "Truck", tint = …)` |
| Flutter | `ds_icons.dart` (SVG strings + `DsIcon` widget, flutter_svg) | `DsIcon(DsIcons.truck, size: 20, semanticLabel: 'Truck')` |
| React Native | `DsIcon.tsx` (`SvgXml`, react-native-svg) | `<DsIcon name="truck" size={20} color={colors.textDefault} />` |

Shapes (`line`, `polyline`, `polygon`, `rect` with radii, `circle`, `ellipse`) are converted to path data for Android; strokes, caps and joins carry over. `ds.py mobile lint` flags SF Symbols, Material icons and icon fonts in app code so screens use these components.
