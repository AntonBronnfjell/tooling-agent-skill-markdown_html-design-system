# Visualizing the system: docs site, Storybook, and framework workbenches

Every design system needs a place to see every component, in every state and theme, **independently of the product**. Choose by target; you can have more than one.

## Contents
1. Zero-dependency docs site
2. Generated Storybook for the HTML/CSS system
3. Storybook for framework adapters (React, Vue, Svelte, Angular, Web Components)
4. Alternatives (Histoire, Ladle, Lookbook, Pattern Lab, Fractal)
5. Docs pages every workbench should have

## 1. Zero-dependency docs site
`ds.py serve <dir>` builds and serves `index.html` + the component pages at `http://127.0.0.1:8000`. Theme, density, RTL and reduced-motion toggles are in every page header. This is the source of truth the other workbenches are generated from.

## 2. Generated Storybook (HTML/CSS system)
```bash
python3 <skill-dir>/scripts/ds.py storybook <dir>   # writes package.json, .storybook/, stories/
cd <dir> && npm install && npm run storybook        # http://localhost:6006
npm run build-storybook                             # static site in storybook-static/ (deploy anywhere)
```
- Framework `@storybook/html-vite` (Storybook 10), addons `@storybook/addon-docs` + `@storybook/addon-a11y` (axe on every story, `a11y.test: 'error'`).
- Every `data-demo` block on a component page becomes a story named `<component-id> · <markers>`, grouped `<Category>/<File>`; the page's usage text becomes the component description; `js/<file>.js` is imported and its `init(root)` runs after render.
- Toolbar globals mirror the docs site: **Theme** (system + every theme in `tokens/themes`), **Density**, **Direction**, **Motion** — applied on `<html>` exactly as in production.
- `Foundations/Tokens` renders every token live (swatches, spacing, radius, shadow, type roles) so theme switches update values.
- `stories/` is regenerated on each run (`npm run stories`); `.storybook/main.js` and `preview.js` are yours to edit (only `--force` overwrites). Never hand-edit generated stories — edit the page.
- Patterns render `layout: 'fullscreen'`.

## 3. Framework adapters
When `targets` includes a framework, the adapter package gets its own Storybook with the same toolbar/addon setup, written stories (not generated):

| Target | Framework package | Story file |
|---|---|---|
| React | `@storybook/react-vite` | `Button.stories.tsx` |
| Vue 3 | `@storybook/vue3-vite` | `Button.stories.ts` |
| Svelte | `@storybook/svelte-vite` / `sveltekit` | `Button.stories.svelte` (CSF via addon-svelte-csf) or `.ts` |
| Angular | `@storybook/angular` | `button.stories.ts` |
| Web Components / Lit | `@storybook/web-components-vite` | `button.stories.ts` |

Conventions (React shown; same shape elsewhere):
```tsx
import type { Meta, StoryObj } from '@storybook/react-vite';
import { fn } from 'storybook/test';
import { Button } from './Button';

const meta = {
  title: 'Actions/Button',                       // same categories as the manifest / storySort
  component: Button,
  args: { children: 'Save changes', onClick: fn() },
  argTypes: {
    variant: { control: 'inline-radio', options: ['primary', 'secondary', 'ghost', 'destructive'] },
    size: { control: 'inline-radio', options: ['sm', 'md', 'lg'] },
  },
} satisfies Meta<typeof Button>;
export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = {};
export const Loading: Story = { args: { loading: true } };      // one export per manifest state/variant
export const Destructive: Story = { args: { variant: 'destructive', children: 'Delete project' } };
```
- `argTypes` options come from the manifest `demos` (`variant:*`, `size:*`); every `state:*` gets a named story so the a11y addon audits it.
- Overlays: a `WithTrigger` render wrapper that owns open state, so the story shows trigger → open → close (focus return is visible).
- Width-sensitive components get a decorator constraining width; patterns use `parameters.layout = 'fullscreen'`.
- `preview.tsx`: import the system CSS (`@acme/design/ds.css`), the same `globalTypes` (theme, density, dir, motion) and a decorator that sets attributes on `document.documentElement`; `tags: ['autodocs']`; `parameters.a11y.test = 'error'`; `options.storySort.order` = manifest category order.
- Fonts: `staticDirs` mapping the package's `fonts/` to the URL the CSS expects.
- If the library build uses a d.ts plugin, filter it out in `viteFinal` — Storybook doesn't need it and it slows builds.

## 4. Alternatives
- **Histoire** — Vue/Svelte-native, lighter than Storybook. **Ladle** — fast React-only, CSF-compatible (stories can move to Storybook later).
- **Lookbook** (Rails ViewComponent), **Pattern Lab** / **Fractal** (template-language component libraries), **Django Pattern Library**.
- Whatever the tool: the same toolbar (theme/density/direction/motion), the same categories, axe on every state.

## 5. Docs pages every workbench should have
`Introduction` (what/why/how to install, generated), `Foundations/Tokens` (live), `Accessibility` (contract summary + keyboard reference per composite widget), `Changelog`/`Migration` link, and `DESIGN.md` linked from the intro.
