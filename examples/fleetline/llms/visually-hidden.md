# Visually Hidden

Category: Foundations · page `components/visually-hidden.html` · CSS `css/components/visually-hidden.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `visually-hidden` — Visually Hidden / SR only | core | ready · stable | variant:sr-only variant:focusable |

## Usage

Visually hidden content is read by screen readers but takes no space on screen. Use it to add context sighted users get from layout: "Error:" before a field message, the vehicle name after a repeated "Edit" link, the column a table cell belongs to.
- .sr-only — always hidden visually.
- .sr-only--focusable — hidden until it receives keyboard focus; for skip links. Add .skip-link for the revealed style.
- Don't use it to hide content from sighted users that everyone needs, and never put focusable controls inside plain .sr-only .
- For content that should be hidden from everyone use hidden ; to hide decoration from assistive tech use aria-hidden="true" .

## Anatomy

- Hidden text — .sr-only (defined in css/base.css , utilities layer)
- Revealed skip link — .sr-only--focusable + .skip-link

## Examples

### visually-hidden · variant:sr-only

```html
<p class="text-body">Van KX-219 · <a href="#visually-hidden">Edit<span class="sr-only"> van KX-219</span></a></p>
            <p class="text-small text-muted">Screen readers hear "Edit van KX-219"; sighted users see "Edit" next to the vehicle.</p>
```

### visually-hidden · variant:focusable

```html
<a class="skip-link sr-only sr-only--focusable" href="#examples-h">Skip to examples</a>
            <a class="skip-link is-focus-visible" href="#examples-h">Skip to examples</a>
            <p class="text-small text-muted">The first link is hidden until you Tab to it; the second shows its focused look (frozen with <code>.is-focus-visible</code>).</p>
```

## API

Hook | Values | Purpose
.sr-only | utility class (base.css) | Hide visually, keep for assistive tech
.sr-only--focusable | utility class (base.css) | Reveal on :focus-visible / :active
.skip-link | class (visually-hidden.css) | Inverse surface and focus ring when revealed
.is-focus-visible | docs-only class | Freezes the revealed state

## Do and don't

View history for truck HT-507
Do complete repeated link text so it makes sense out of context.
Status: Overdue
Don't hide information sighted users need too; status must be visible text.

## Accessibility

- The technique (1px box, clip-path: inset(50%) , no wrapping) keeps text in the accessibility tree; display: none and visibility: hidden would remove it.
- Rules use !important in the utilities layer on purpose: hiding must never be undone by component or app CSS.
- Skip links must be the first focusable element and target an element with an id ( <main id="main"> ).
- Visually hidden text is translated like any other text; don't hard-code English into CSS content .
Keyboard interaction
Key | Behavior
Tab (first press) | Reveals and focuses the skip link
Enter | Moves to the main content

## Tokens

Custom property | Purpose
--color-bg-inverse , --color-text-inverse | Revealed skip link surface and text
--space-2 | -4 , --radius-md | Skip link padding and shape
--focus-ring-width | -offset | -color | Focus ring
