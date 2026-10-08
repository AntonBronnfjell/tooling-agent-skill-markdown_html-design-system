# Skip Link

Category: Navigation · page `components/skip-link.html` · CSS `css/components/skip-link.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `skip-link` — Skip Link | core | ready · stable | state:hidden state:focus-visible |

## Usage

Every Fleetline page starts with a skip link so keyboard and switch users can jump past the top navigation straight to the content. It's invisible until focused.
- Make it the first focusable element in <body> .
- Label: "Skip to main content". Add more only for big landmarks ("Skip to search", "Skip to vehicle list").
- Give the target tabindex="-1" so focus actually moves there in every browser.

## Anatomy

- Link — <a class="skip-link" href="#main"> , clipped off-screen until focused
- Target — <main id="main" tabindex="-1">

## Examples

### skip-link · state:hidden

```html
<div inert><a class="skip-link skip-link--preview" href="#main">Skip to main content</a></div><p>Nothing shows until the link receives keyboard focus. Press <kbd>Tab</kbd> once after this page loads to see the real one at the top of the window.</p>
```

### skip-link · state:focus-visible

```html
<div class="ds-demo__row"><div inert><a class="skip-link skip-link--preview is-focus-visible" href="#main">Skip to main content</a></div></div>
```

### skip-link · variant:multiple

```html
<div class="ds-demo__row"><div inert style="display:flex; gap:var(--space-2); flex-wrap:wrap;"><a class="skip-link skip-link--preview is-focus-visible" href="#main">Skip to main content</a><a class="skip-link skip-link--preview is-focus-visible" href="#search">Skip to search</a></div></div>
            <p>Several skip links are fine on dense dispatch screens; each shows when focused.</p>
```

## API

Hook | Values | Purpose
.skip-link | block class | Hidden until focused, then fixed at the top inline-start corner above sticky headers
.skip-link--preview | docs-only modifier | Render in flow inside a demo
.is-focus-visible | docs-only class | Freeze the visible state

## Do and don't

<a class="skip-link" href="#main"> as the first element of <body> .
Do put it first and point it at a focusable target.
.skip-link { display: none }
Don't hide it with display: none — it then never receives focus.

## Accessibility

Keyboard interaction
Key | Behavior
Tab (first press) | Focuses and reveals the skip link
Enter | Moves focus to #main ; the next Tab continues from there
- WCAG 2.4.1 Bypass Blocks. The link is clipped (not display:none ), so it stays in the tab order.
- When visible it uses the primary action colors (4.5:1) and sits at --z-tooltip , above sticky headers.
- Forced colors: adds a 2px border.

## Tokens

Custom property | Purpose
--color-action-primary-bg | -fg | Visible colors
--z-tooltip | Stays above sticky headers and overlays
--elevation-overlay | Shadow
--space-2 | -4 , --button-radius | Position, padding, shape
--focus-ring-* | Focus ring
