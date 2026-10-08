# Fleetline design system (example)

Built with the [html-design-system](../../README.md) skill to show what it produces. It's a fleet-maintenance SaaS for dispatchers (desktop, dense data) and mechanics (tablet, outdoors).

- **Live:** [docs site](https://antonbronnfjell.github.io/tooling-agent-skill-markdown_html-design-system/) · [Storybook](https://antonbronnfjell.github.io/tooling-agent-skill-markdown_html-design-system/storybook/)
- **Direction:** a new, calm and functional look. The teal brand comes from `ds.py palette '#0f766e' --primary`, mapped by measured contrast in light, dark and high-contrast. Decisions are in `ds.config.json`; the contract is in `DESIGN.md`.
- **Scope:** the core tier of app UI, 68 components and patterns, each with every state, a docs page, accessibility notes and its tokens.

```bash
python3 ../../scripts/ds.py serve .          # docs site at http://127.0.0.1:8000
python3 ../../scripts/ds.py check . --strict # tokens, contrast in every theme, lint, coverage
python3 ../../scripts/ds.py storybook . && npm install && npm run storybook
python3 ../../scripts/ds.py playwright . && npx playwright install chromium && npm run test:ui:update
```

How it was built:
1. `ds.py init`, then `palette`, then the decision record.
2. One reference implementation: typography, layout, button, form field, and the shared JS behaviors.
3. Five parallel builders working from `references/builder-brief.md`.
4. The patterns.
5. The axe, keyboard and taste checks. The fixes they forced (readable hint text on disabled controls, text that changes color on selected fills, links inside alerts, unique landmarks) went back into the skill's component contract.
