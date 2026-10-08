# Accordion

Category: Data Display · page `components/accordion.html` · CSS `css/components/accordion.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `accordion` — Accordion | core | ready · stable | state:collapsed state:expanded state:focus-visible variant:single variant:multiple |
| `disclosure` — Disclosure / Collapsible | core | ready · stable | variant:disclosure |

## Usage

Use an accordion to let people scan section titles of a long checklist or form summary and open only what they need (inspection sections, work-order details on tablet). Use a disclosure for one piece of optional detail ("Show service history"). Don't hide information everyone needs — required fields, errors and the next step stay visible. For switching views of the same object use tabs.
- Single (exclusive, shared name ) — when sections are steps or alternatives; keeps the page short on tablet.
- Multiple — when people compare sections; default.
Content: summary text is a noun phrase in sentence case ("Brakes", "Parts used"), with an optional count in the meta slot ("2 checks"). A disclosure's summary says what opens: "Show service history (12 entries)".

## Anatomy

- Group (accordion) — .accordion , bordered container
- Item — <details class="accordion__item" name="…">
- Summary — <summary class="accordion__summary"> : title, meta, chevron
- Chevron — svg.accordion__icon , rotates 180° when open
- Panel — .accordion__panel
- Disclosure — <details class="disclosure"> with .disclosure__summary and .disclosure__panel

## Examples

### accordion · state:collapsed

```html
<div class="accordion">
            <details class="accordion__item">
              <summary class="accordion__summary"><span class="accordion__title">Engine and drivetrain</span><span class="accordion__meta">3 checks</span><svg class="accordion__icon" aria-hidden="true" focusable="false"><use href="#icon-chevron-down"></use></svg></summary>
              <div class="accordion__panel"><p>Oil level, coolant, drive belt tension.</p></div>
            </details>
            </div>
```

### accordion · state:expanded

```html
<div class="accordion">
            <details class="accordion__item" open>
              <summary class="accordion__summary"><span class="accordion__title">Brakes</span><span class="accordion__meta">2 checks</span><svg class="accordion__icon" aria-hidden="true" focusable="false"><use href="#icon-chevron-down"></use></svg></summary>
              <div class="accordion__panel"><p>Front pads 3 mm — replace before 86,000 km. Rear pads 7 mm.</p></div>
            </details>
            </div>
```

### accordion · state:focus-visible

```html
<div class="accordion">
            <details class="accordion__item">
              <summary class="accordion__summary is-focus-visible"><span class="accordion__title">Tyres</span><span class="accordion__meta">4 checks</span><svg class="accordion__icon" aria-hidden="true" focusable="false"><use href="#icon-chevron-down"></use></svg></summary>
              <div class="accordion__panel"><p>Tread depth above 4 mm on all wheels.</p></div>
            </details>
            </div>
```

### accordion · variant:single

```html
<div class="accordion">
            <details class="accordion__item" name="insp-kx219" open>
              <summary class="accordion__summary"><span class="accordion__title">Engine and drivetrain</span><span class="accordion__meta">3 checks</span><svg class="accordion__icon" aria-hidden="true" focusable="false"><use href="#icon-chevron-down"></use></svg></summary>
              <div class="accordion__panel"><p>Oil level, coolant, drive belt tension.</p></div>
            </details>
            <details class="accordion__item" name="insp-kx219">
              <summary class="accordion__summary"><span class="accordion__title">Brakes</span><span class="accordion__meta">2 checks</span><svg class="accordion__icon" aria-hidden="true" focusable="false"><use href="#icon-chevron-down"></use></svg></summary>
              <div class="accordion__panel"><p>Front pads 3 mm — replace before 86,000 km.</p></div>
            </details>
            <details class="accordion__item" name="insp-kx219">
              <summary class="accordion__summary"><span class="accordion__title">Lights and electrics</span><span class="accordion__meta">5 checks</span><svg class="accordion__icon" aria-hidden="true" focusable="false"><use href="#icon-chevron-down"></use></svg></summary>
              <div class="accordion__panel"><p>Left brake light replaced on 2 Oct.</p></div>
            </details>
            </div>
```

### accordion · variant:multiple

```html
<div class="accordion">
            <details class="accordion__item" open>
              <summary class="accordion__summary"><span class="accordion__title">Parts used</span><span class="accordion__meta">4 items</span><svg class="accordion__icon" aria-hidden="true" focusable="false"><use href="#icon-chevron-down"></use></svg></summary>
              <div class="accordion__panel"><p>Brake pads (front), wear sensor, brake cleaner, cable ties.</p></div>
            </details>
            <details class="accordion__item" open>
              <summary class="accordion__summary"><span class="accordion__title">Labour</span><span class="accordion__meta">3.5 h</span><svg class="accordion__icon" aria-hidden="true" focusable="false"><use href="#icon-chevron-down"></use></svg></summary>
              <div class="accordion__panel"><p>Marta Quintero, 08:10–11:40.</p></div>
            </details>
            <details class="accordion__item">
              <summary class="accordion__summary"><span class="accordion__title">Notes for the driver</span><span class="accordion__meta">1 note</span><svg class="accordion__icon" aria-hidden="true" focusable="false"><use href="#icon-chevron-down"></use></svg></summary>
              <div class="accordion__panel"><p>Bedding-in: avoid hard braking for the first 200 km.</p></div>
            </details>
            </div>
```

### disclosure · variant:disclosure

```html
<details class="disclosure">
              <summary class="disclosure__summary"><svg class="disclosure__icon" aria-hidden="true" focusable="false"><use href="#icon-chevron-right"></use></svg>Show service history (12 entries)</summary>
              <div class="disclosure__panel">
                <p>Last three: oil change 14 Mar, tyre rotation 2 Jun, brake inspection 2 Oct.</p>
              </div>
            </details>
```

## API

Hook | Values | Purpose
.accordion | block class | Group container with dividers
.accordion__item | part class on <details> | One section
name="group-id" | attribute | Same value on all items = only one open at a time (native exclusive accordion)
open | attribute | Expanded state (set initially for sections that start open)
.accordion__summary | __title | __meta | __icon | __panel | part classes | Header row and content
.disclosure , .disclosure__summary | __icon | __panel | block + parts | Single show/hide
.is-hover | .is-focus-visible | docs-only class | Freeze summary states

## Do and don't

Summary: "Brakes · 2 checks"
Do use short, scannable titles with a count.
Summary: "Click here to see more information about brakes"
Don’t write instructions in the summary.
<details><summary>
Do use native details/summary; keyboard and state come for free.
<summary><h3>…</h3></summary>
Don’t put a heading inside summary; it loses its button role. If headings are required use the APG button pattern.

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Moves between summaries (and into open panels' content)
Enter / Space | Opens or closes the focused section
- Role: <summary> is exposed as a button with expanded/collapsed state; nothing to add.
- Exclusive groups use the native name attribute; opening one closes the others and the browser updates every state.
- Find-in-page and fragment links open closed sections automatically (content stays in the DOM).
- Chevron is decorative ( aria-hidden ); the open state is announced, not drawn only. The disclosure chevron mirrors in RTL.
- Motion: height animates with ::details-content where supported, instantly elsewhere and under reduced motion.
- Target: accordion summaries are at least 44px high ( --size-touch-target ).

## Tokens

Custom property | Purpose
--size-touch-target | Minimum summary height
--color-border-default | Group border and dividers
--color-action-ghost-bg-hover | Summary hover fill
--color-text-link | Disclosure trigger text
--color-text-muted | Meta text
--icon-size-md | -sm , --icon-stroke | Chevrons
--motion-duration-base , --motion-easing-standard | Chevron rotation and height animation
--focus-ring-* | Inset focus ring on summaries
