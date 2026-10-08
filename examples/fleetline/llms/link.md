# Link

Category: Actions · page `components/link.html` · CSS `css/components/link.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `link` — Link / Anchor | core | ready · stable | variant:inline variant:standalone variant:external state:visited state:default state:hover state:focus-visible state:active |

## Usage

Use a link to go somewhere: another page, a section, a document. If it changes data or opens a dialog, it's a button . Never put href="#" on something that runs JavaScript.
- Inline links sit in sentences and are always underlined — color alone isn't enough (WCAG 1.4.1).
- Standalone links (end of a card, below a table) drop the underline until hover but keep weight and an arrow.
- External links open in the same tab by default. Use a new tab only when leaving would lose work (a half-filled inspection form), and say so.
- Link text makes sense out of context: "View service history for KX-219", not "here" or "more".

## Anatomy

- Anchor — <a class="link" href>
- Label — the visible text, which is the accessible name
- Icon (optional) — svg.link__icon : arrow for standalone, external-link for new tabs
- Hidden hint (external) — <span class="sr-only"> (opens in new tab)</span>

## Examples

### link · variant:inline state:default

```html
<p>Brake pads were replaced under <a class="link" href="#wo-4182">work order WO-4182</a>. The next inspection is due on 14 November.</p>
```

### link · variant:standalone

```html
<div class="ds-demo__row"><a class="link link--standalone" href="#service-history">View service history for KX-219<svg class="link__icon icon--mirror-rtl" aria-hidden="true" focusable="false"><use href="#icon-arrow-right"></use></svg></a></div>
```

### link · variant:external

```html
<p>Check the <a class="link link--external" href="https://www.fmcsa.dot.gov/regulations" target="_blank" rel="noopener">FMCSA inspection rules<svg class="link__icon" aria-hidden="true" focusable="false"><use href="#icon-external-link"></use></svg><span class="sr-only"> (opens in new tab)</span></a> before signing off.</p>
```

### link · state:visited

```html
<p>You already opened <a class="link is-visited" href="#wo-4182">work order WO-4177</a>.</p>
            <p>Use visited styling in long lists people work through (work-order queues, manuals).</p>
```

### link · state:hover

```html
<p><a class="link is-hover" href="#wo-4182">work order WO-4182</a></p>
```

### link · state:focus-visible

```html
<p><a class="link is-focus-visible" href="#wo-4182">work order WO-4182</a></p>
```

### link · state:active

```html
<p><a class="link is-active" href="#wo-4182">work order WO-4182</a></p>
```

### link · variant:subtle

```html
<p>Assigned to <a class="link link--subtle" href="#mechanic-rosa">Rosa Méndez</a> at North Yard.</p>
            <p>Inherits text color in dense tables; the underline stays.</p>
```

## API

Hook | Values | Purpose
.link | block class | Inline, underlined link
.link--standalone | modifier | Semibold, no underline until hover, optional arrow
.link--external | modifier | With external icon + hidden "(opens in new tab)"
.link--subtle | modifier | Inherits text color (tables)
.link__icon | part | Trailing icon
.is-hover | .is-focus-visible | .is-active | .is-visited | docs-only class | Freeze a state

## Do and don't

Read the brake inspection checklist .
Do write link text that names the destination.
For the checklist, go here .
Don't use "here" or "more" — screen-reader link lists lose the context.

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Moves focus to the link
Enter | Follows the link (Space scrolls the page — that's why actions are buttons)
- Role: native <a href> . Without href it isn't focusable or a link — ds.py check flags it.
- Contrast: --color-text-link and --color-text-link-visited are 4.5:1 on canvas in every theme; the underline is the non-color cue.
- External: the hidden "(opens in new tab)" is part of the name; rel="noopener" is required.
- Forced colors: uses LinkText / VisitedText .

## Tokens

Custom property | Purpose
--color-text-link | Link color
--color-text-link-visited | Visited color
--border-width-thin | -thick | Underline thickness, rest / hover
--color-selected-bg | Active (pressed) highlight
--icon-size-sm | Icon
--focus-ring-* | Focus ring
