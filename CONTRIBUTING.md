# Contributing

Thanks for improving the skill. The repo root **is** the skill (`SKILL.md`) and a Claude Code plugin (`.claude-plugin/`).

## Set up

```bash
git clone https://github.com/AntonBronnfjell/tooling-agent-skill-markdown_html-design-system.git
cd tooling-agent-skill-markdown_html-design-system
python3 install.py --tools claude --link     # Claude Code uses your working copy live
python3 -m unittest discover -s tests -v      # stdlib tests, no dependencies
claude plugin validate --strict .claude-plugin/plugin.json
```

## Rules of the house

- **Stdlib only.** `scripts/ds.py` must run on Python 3.8+ with no third-party packages. Generated projects may use npm tools (Storybook), never the CLI itself.
- **Never clobber user files.** Every write in `ds.py` goes through `safe_write` / `safe_copy` / `merge_json` / `append_lines`. Raw `write_text` is a review blocker.
- **Keep `SKILL.md` lean** (< 500 lines, description ≤ 1024 characters with ~100 spare). Detail belongs in `references/`; long reference files start with a contents list.
- **Golden outputs** in `tests/golden/` change only on purpose: run `python3 -m unittest discover -s tests` and, after reviewing the diff, `UPDATE_GOLDEN=1 python3 -m unittest discover -s tests`.

## Adding a component

1. Add the item to `assets/manifest.json` (unique `id` and `file`, tier, every required `demos` marker, `aria`, `native`, `desc`).
2. Add its spec to the matching `references/components/<category>.md` (anatomy, native element, keyboard, ARIA, states, pitfalls).
3. Run the tests — `test_manifest_consistency` checks ids, files, demo marker syntax and that every component is documented.
4. For a new scope: a category with `"scope"`, an entry in `scopes`, a reference file, optional `assets/templates/scopes/<scope>/` token files, and a case in `plugin-evals/`.

## Adding a ds.py command

Add the function, its subparser and dispatch entry, a line in the module docstring, a row in `SKILL.md`'s toolkit table, the README CLI reference, and a test in `tests/test_ds.py`.

## Mobile and icon templates

- Native component templates live in `assets/templates/mobile/` (`DSComponents.swift`, `DsComponents.kt`, `ds_components.dart`, `DsComponents.tsx`, `measure.mjs`, `web-mobile.css`). They are not compilable as-is: markers are filled by `ds.py mobile scaffold` — `@C(role|file)` color (the `|file` part lets a measured web color override the role), `@D(file.prop)` dimension from `CORE_RECIPES`, `@W(file.prop)` font weight, `@T(role)` type style, `@E(keys)` shadow, `@HEAD`/`@PKG`.
- New component props go in `CORE_RECIPES` (measured path + default tokens) so `FIDELITY.md` can report their source.
- Generated code must stay clean under `ds.py mobile lint` (a test checks it) and compile on the real SDKs: the `mobile` CI job builds Swift (iOS SDK), Compose (Gradle), Flutter (analyze + golden run) and React Native (`tsc --strict`). Locally, `swiftc -typecheck` works on macOS with Xcode.
- Icon sets: add to `ICON_SETS` (npm package, path pattern, license, license URL) and to `references/icons.md`.

## Evals

- `evals/evals.json` — skill-creator format (qualitative iteration).
- `plugin-evals/` — `claude plugin eval .` cases (trigger + outcome graders, with a no-plugin baseline). Run before releases: `claude plugin eval . --trust-plugin --runs 1`.

## Releases

Update `CHANGELOG.md`, bump `version` in `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json` and `.codex-plugin/plugin.json`, then tag `vX.Y.Z` and create a GitHub release. Plugin users only receive updates when the version changes.
