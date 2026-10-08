# Taste: avoiding the generic AI look

`ds.py taste [path] [--strict] [--min-score 80] [--json]` scans CSS, HTML and component files for the tells that make AI-built interfaces look interchangeable, and scores the result out of 100 (each distinct tell costs 5, plus a weight per occurrence). Run it on the design system and on product pages before release; `--strict` fails CI below the minimum score.

| Rule | Why it's flagged | What to do instead |
|---|---|---|
| `ai-gradient`, `tw-ai-gradient` | Purple/indigo/pink gradients are the single most recognizable template look | Use the brand ramp; one gradient moment at most |
| `gradient-text` | Low contrast, hard to read, dated | Solid token color; weight or size for emphasis |
| `glass` | Backdrop blur is costly and illegible over busy content | Elevation surfaces (`color.elevation.surface.*` + shadow pair) |
| `huge-radius`, `soft-shadow` | Everything rounded and floating flattens hierarchy | A deliberate shape language from radius tokens; shadows only where something floats |
| `emoji-ui` | Screen readers read emoji names; reads as filler | Icons from the sprite with proper labels |
| `placeholder-copy` | Lorem ipsum/Acme hide real layout problems | Realistic copy at realistic lengths |
| `buzzwords` | "Supercharge", "seamless", "next-level" say nothing | What it does, for whom, with a number (`content.md`) |
| `generic-cta` | "Get started", "Learn more", "Submit" | Verb + object |
| `inter-only` | Default typeface with no decision behind it | Record the font decision; pair a display face if the brand needs one |
| `center-everything` | Centered body copy is tiring to read | Left-align anything longer than two lines |

The linter catches symptoms. The cure is the decision phase: a direction with a rationale, a style allocation (`decision-guide.md`), and `/frontend-design` or `/ui-ux-pro-max` for a distinctive starting point.
