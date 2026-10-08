# Visualizing the system: docs site, Storybook, and framework workbenches

Every design system needs a place to see every component, in every state and theme, **independently of the product**. Choose by target; you can have more than one.

## Contents
1. Zero-dependency docs site
2. Generated Storybook for the HTML/CSS system
3. Storybook for framework adapters (React, Vue, Svelte, Angular, Web Components)
4. Backend & non-JS stacks (PHP, Python, Ruby, Java, .NET, Rust, Go, Elixir) — three strategies
5. Alternatives (Histoire, Ladle, Lookbook, Pattern Lab, Fractal)
6. Docs pages every workbench should have

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

## 4. Backend & non-JS stacks

Storybook runs on Node and renders in the browser. Server-rendered templates (Blade, Twig, Jinja/Django, ERB/ViewComponent, Thymeleaf, Razor, HEEx, Go templates) and native/WASM UI (Blazor, Leptos, Yew, Dioxus) can't run inside it directly. Pick one of three strategies — and remember the HTML/CSS system itself already works in every stack: the templates only have to emit the same markup and classes.

### Strategy A — Server-driven bridge (`@storybook/server`) · one Storybook, any backend
Storybook is the UI shell; every story asks your backend for HTML: `GET {server.url}/{story id}?{args}`.

```bash
ds.py storybook <dir> --renderer server --server-url http://localhost:8000/__stories
STORYBOOK_SERVER_URL=http://localhost:3000/storybook npm run storybook   # point at your app instead
```
- Generates `.stories.json` (framework `@storybook/server-webpack5`), one story per page demo, with id `<components|patterns>/<file>/<n>` and the demo's markers as args (`variant=primary&state=default&size=md`).
- `.storybook/preview-head.html` links `dist/ds.css`; the backend returns **fragments only** (no `<html>`, no CSS).
- Theme / density / direction / motion toolbar still works (preview listens to the globals channel and sets attributes on `<html>`); a11y addon audits the server HTML.
- **Reference backend:** `ds.py serve <dir>` answers `/__stories/...` with the exact markup from the component pages (CORS enabled). Start there, then switch the URL to your app — the reference fragments are the contract your templates must match (diff them in tests).

Your backend implements one dev-only route. Shapes (render the template for `file` with `args`; `n` selects the demo when args aren't enough):

| Stack | Route sketch |
|---|---|
| Laravel (Blade) | `Route::get('/storybook/{sub}/{file}/{n}', fn ($sub, $file, $n) => view("ds.$file", request()->query()))` — register only in `local` |
| Symfony (Twig) | `#[Route('/storybook/{sub}/{file}/{n}')]` controller → `$this->render("ds/$file.html.twig", $request->query->all())` |
| Django (templates / django-components) | `path("storybook/<sub>/<file>/<int:n>", view)` → `render(request, f"ds/{file}.html", request.GET.dict())`, wrapped in `if settings.DEBUG` |
| Flask / FastAPI (Jinja2) | `@app.get("/storybook/{sub}/{file}/{n}")` → `templates.TemplateResponse(f"ds/{file}.html", {"request": request, **request.query_params})` |
| Rails (ViewComponent / partials) | `get "storybook/:sub/:file/:n" => "storybook#show"` (dev only) → `render partial: "ds/#{params[:file]}", locals: request.query_parameters, layout: false` |
| Spring Boot (Thymeleaf) | `@GetMapping("/storybook/{sub}/{file}/{n}")` in a `@Profile("dev")` controller → return `"ds/" + file + " :: component"` with `@RequestParam Map` as model |
| ASP.NET Core (Razor) | `app.MapGet("/storybook/{sub}/{file}/{n}", (string file, HttpRequest r) => new RazorComponentResult(...))` or a dev-only MVC action returning `PartialView($"ds/{file}", r.Query)` |
| Phoenix (HEEx) / Go `html/template` | Same idea: dev-only route rendering the component with query params, `Access-Control-Allow-Origin` for the Storybook origin |

Always: dev/test environments only, allow CORS from the Storybook origin, never include layout/CSS in the fragment.

### Strategy B — Universal Web Components · one implementation for many stacks
For a design system consumed by apps in different languages (React here, .NET there, PHP elsewhere): wrap the components that need behavior as **custom elements** (Lit or vanilla), document them with `@storybook/web-components-vite`, ship one ES module bundle + `ds.css` (npm and a CDN), and use the tags in any server template (`<ds-combobox>`, `<ds-dialog>`).
- Keep light DOM (or `::part` + CSS custom properties) so `ds.css` and tokens style them; use form-associated custom elements (`ElementInternals`) for inputs so native forms work.
- Server-rendered templates stay plain HTML with progressive enhancement — the element upgrades when the bundle loads.
- Rust/Leptos/Yew/Dioxus or other WASM UI: compile to WASM and expose custom elements, then document those elements in the same Web Components Storybook.

### Strategy C — Ecosystem-native workbenches · single-stack teams, no Node
| Stack | Tool | Notes |
|---|---|---|
| Rails | **Lookbook** (`lookbook` gem) | Native previews for ViewComponent, Phlex and partials; params as controls. Bridge alternative: `view_component_storybook` gem → `@storybook/server`. |
| Laravel | **Blast** (`area17/blast`, Composer) | Storybook for Blade components, generated from the app. |
| Django | **django-pattern-library** (PyPI) + **storybook-django** (npm) | Pattern library of Django templates; storybook-django renders them inside Storybook via the dev server. |
| Symfony / Twig | `@storybook/html-vite` + a JS Twig compiler (`twig` on npm) | Renders `.twig` in the browser — fast, but only for templates that don't depend on PHP-side functions. |
| Blazor / .NET | **Blazing Story** (NuGet `BlazingStory`) | Storybook-like UI written in .NET; stories as `.stories.razor`. Razor Pages/MVC: use strategy A. |
| Java / Spring | Strategy A (no mature native clone) | |
| Rust (Leptos/Yew/Dioxus) | Strategy B (WASM custom elements) | No established native Storybook clone was found; don't depend on unmaintained ones. |

Whatever you choose, keep the contract identical: same categories, the theme/density/direction/motion toggles, one story per manifest state, and an axe check on every story.

### Choosing
- **Several stacks share one system** → B (web components for behavior, `ds.css` for everything else); optionally A to preview each stack's templates.
- **One backend stack** → C if a native tool exists (Lookbook, Blast, Blazing Story), otherwise A.
- **This skill's HTML/CSS system only** → section 2 (`--renderer html`, default). Use `--renderer server` when the real markup lives in backend templates.

## 5. Alternatives
- **Histoire** — Vue/Svelte-native, lighter than Storybook. **Ladle** — fast React-only, CSF-compatible (stories can move to Storybook later).
- **Lookbook** (Rails ViewComponent), **Pattern Lab** / **Fractal** (template-language component libraries), **Django Pattern Library**.
- Whatever the tool: the same toolbar (theme/density/direction/motion), the same categories, axe on every state.

## 6. Docs pages every workbench should have
`Introduction` (what/why/how to install, generated), `Foundations/Tokens` (live), `Accessibility` (contract summary + keyboard reference per composite widget), `Changelog`/`Migration` link, and `DESIGN.md` linked from the intro.
