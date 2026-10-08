# Motion

Motion is part of the brand and the most common source of accessibility failures. Decide it explicitly in Phase 1 and record it in `ds.config.json → motion`, which `ds.py design-md` publishes:

```json
"motion": {
  "personality": "calm, functional",
  "bans": ["spring/bounce easing", "parallax", "autoplaying carousels", "scale > 1.02 on hover", "animating layout properties"],
  "moments": ["overlay enter/exit: fade + 8px slide, motion.duration.base", "toast: slide from edge", "accordion: grid-template-rows 0fr→1fr"]
}
```

## Vocabulary
- **Durations** `motion.duration.instant|fast|base|slow|slower` and **easings** `motion.easing.standard|enter|exit|emphasized`. Enter uses decelerate (`enter`), exit uses accelerate (`exit`) and is shorter than enter.
- Enterprise and data-dense UIs: mostly `fast`/`base`, no decorative motion. Consumer/brand: allow one or two signature moments, not more.
- When JS animates (Web Animations API, GSAP, Motion One), import durations/easings from `dist/tokens.json` so JS and CSS can't drift.

## Inventory (decide each, document in the component pages)
State changes (hover/press: color only, `fast`) · overlays (dialog, drawer, popover, menu: fade + small translate) · disclosure (accordion/details: height via `grid-template-rows` or `interpolate-size`) · feedback (toast enter/exit, progress) · skeleton shimmer · page/route transitions (View Transitions API, optional) · scroll-linked effects (rarely; never required to read content).

## Reduced motion — two switches, one rule
`base.css` neutralizes transitions/animations under `@media (prefers-reduced-motion: reduce)` **and** `[data-reduced-motion]` on `<html>` (docs/Storybook toggle, in-app setting). JS must check both before animating:

```js
export const prefersReducedMotion = () =>
  matchMedia('(prefers-reduced-motion: reduce)').matches || document.documentElement.hasAttribute('data-reduced-motion');
```

Under reduced motion: replace movement with opacity or nothing; stop autoplay, parallax, shimmer, count-ups; keep functional feedback (focus, progress) instant.

## Rules
- Animate `transform`/`opacity`; the only allowed layout animation is disclosure height via `grid-template-rows` / `interpolate-size`.
- Nothing flashes more than 3 times per second (WCAG 2.3.1). Anything that moves for > 5s can be paused (2.2.2).
- Entry/exit for top-layer elements: `@starting-style` + `transition-behavior: allow-discrete` on `display`/`overlay`.
- Motion never carries meaning alone (a shake on error also needs the error message).
- Tests and Storybook interaction checks should run with motion disabled or mocked so they assert behavior, not timing.
