# Builder brief (subagent prompt template)

A complete system is ~100 files. Building it serially in one context risks running out of room and quietly skipping components. After tokens and the foundations/actions/forms basics are done in the main thread (they set the conventions), fan out the remaining categories to subagents — one per category, in parallel — using this brief. Fill the `<…>` slots.

```
You are building part of the "<NAME>" HTML/CSS design system at <ABS_DIR>.
Skill directory: <SKILL_DIR>

Read first (in order):
1. <SKILL_DIR>/references/component-contract.md — Definition of Done (markup convention, states, CSS rules, a11y).
2. <SKILL_DIR>/references/components/<CATEGORY_FILE>.md — specs for your components.
3. <ABS_DIR>/ds.config.json — direction & decisions; respect every ADR.
4. <ABS_DIR>/dist/tokens.css — the only values you may use.
5. <ABS_DIR>/components/button.html and css/components/button.css — the reference implementation; copy its page structure and conventions exactly.

Your files (build every one; each file covers several manifest components):
<PASTE the relevant lines from `ds.py plan <ABS_DIR>`>

For each file:
- Write css/<components|patterns>/<file>.css and <components|patterns>/<file>.html (from docs/_component-template.html).
- Put component tokens in tokens/components/<file>.json (your own file — never edit shared token files).
- JS only when native HTML can't do it: js/<file>.js, vanilla ES module exporting init(root), progressive enhancement; reuse js/lib/* behaviors (roving focus, dismiss, position, hotkey, live region) — never re-implement them.
- Framework targets: per component write the test first, then the component, then the story (references/testing.md, references/storybook.md).
- Run `python3 <SKILL_DIR>/scripts/ds.py coverage <ABS_DIR>` and fix until your files' components are [x].
- Run `python3 <SKILL_DIR>/scripts/ds.py check <ABS_DIR>` and fix lint issues in your files.

Do not edit files outside your list. If you need a new semantic token, don't invent it — list it in your report.

Report back: files written, coverage lines for your components, tokens you added, and any requested semantic tokens or open questions.
```

After all subagents finish: merge requested semantic tokens (main thread only), run `ds.py build` and `ds.py check`, and review a sample page from each category for consistency with the reference implementation.
