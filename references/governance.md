# Lifecycle & governance

A design system is a product. Ship these alongside the components (Phase 6) so it survives past the first build.

## Deliverables
- `README.md` in the system root: what it is, how to consume (`<link rel="stylesheet" href="dist/ds.css">` or per-component CSS), principles, links to docs.
- `CHANGELOG.md` (Keep a Changelog format) and semver: **major** = removed/renamed token or class, changed markup contract; **minor** = new component/variant/token; **patch** = visual fixes.
- `CONTRIBUTING.md`: proposal → design review → build against `component-contract.md` → `ds.py check --strict` passes → docs page → release.
- Component status in each page's usage section: `experimental` · `beta` · `stable` · `deprecated (use X; removal in vN)`.
- Decision log: `ds.config.json → decisions` (ADRs), mirrored in docs.
- Principles (3–5, specific): e.g. "Native first", "Accessible by default — AA is the floor", "Tokens, never values", "One way to do a thing".

## Deprecation
Keep the old class/token as an alias for one major version, emit a CSS comment and docs banner, and list migrations in the changelog.

## Adapters (when `targets` asks)
- **Tailwind v4**: `@theme` block mapping utilities to the semantic vars (via `/ui-styling`).
- **shadcn/ui**: map `--background`, `--foreground`, `--primary`, `--ring`, `--radius` … to semantic tokens.
- **React/Vue/Web Components**: thin wrappers that emit the same markup contract; behavior from the same `js/` modules.
- **Figma**: export tokens as Figma variables (Figma MCP `use_figma` with `/figma-generate-library`) so design and code share one source.
- **Style Dictionary / Tokens Studio**: the DTCG JSON is directly consumable.

## Adoption metrics (optional)
Coverage from `ds.py coverage --json`, token usage counts, number of raw values in product code (`ds.py audit` on consumers) trending down.
