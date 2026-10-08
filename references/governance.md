# Lifecycle & governance

A design system is a product. Ship these alongside the components (Phase 6) so it survives past the first build.

## Deliverables
- `DESIGN.md` (generate with `ds.py design-md`): the one-file contract — direction and style allocation, theme table with resolved values, type roles, spacing/radius/layers/breakpoints/motion, consumer rules, component inventory, decisions. Ship it in the package; consuming apps and their AI agents read it instead of 100 pages.
- `README.md` in the system root: what it is, how to consume (`<link rel="stylesheet" href="dist/ds.css">` or per-component CSS), principles, links to docs.
- `CHANGELOG.md` (Keep a Changelog format) and semver: **major** = removed/renamed token or class, changed markup contract; **minor** = new component/variant/token; **patch** = visual fixes.
- `CONTRIBUTING.md`: proposal → design review → build against `component-contract.md` → `ds.py check --strict` passes → docs page → release.
- Component status in each page's usage section: `experimental` · `beta` · `stable` · `deprecated (use X; removal in vN)`.
- Decision log: `ds.config.json → decisions` (ADRs), mirrored in docs.
- Principles (3–5, specific): e.g. "Native first", "Accessible by default — AA is the floor", "Tokens, never values", "One way to do a thing".

## Migration guides
Every major version gets a "Migrating from vN" section (README or `MIGRATION.md`): removed components/props/classes, renamed tokens (old → new table), behavior changes, before/after snippets, and a codemod or search-and-replace list when possible.

## Deprecation
Keep the old class/token as an alias for one major version — for tokens, add `"$deprecated": {"old.path": "new.path"}` to any token file and `ds.py build` emits `--old-path: var(--new-path)` with a comment — show a docs banner, and list migrations in the changelog.

## Packaging, CI, workbench
`ds.py package` (npm exports, see `packaging.md`), `ds.py ci --provider github|gitlab` (check → Storybook to Pages → idempotent publish + tag), `ds.py storybook` (see `storybook.md`).

## Adapters (when `targets` asks)
- **Tailwind v4**: `@theme` block mapping utilities to the semantic vars (via `/ui-styling`).
- **shadcn/ui**: map `--background`, `--foreground`, `--primary`, `--ring`, `--radius` … to semantic tokens.
- **React/Vue/Web Components**: thin wrappers that emit the same markup contract; behavior from the same `js/` modules.
- **Figma**: export tokens as Figma variables (Figma MCP `use_figma` with `/figma-generate-library`) so design and code share one source.
- **Style Dictionary / Tokens Studio**: the DTCG JSON is directly consumable.

## Adoption metrics (optional)
Coverage from `ds.py coverage --json`, token usage counts, number of raw values in product code (`ds.py audit` on consumers) trending down.
