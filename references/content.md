# Content design

Words are part of the interface. Every component page's **usage** section carries the content rules for that component; this file is the system-wide guide they point to. Record the voice decisions in `ds.config.json → principles` (or an ADR) so `DESIGN.md` publishes them.

## Contents
- Voice and tone
- Writing rules for every component
- Errors
- Empty states
- Buttons, links and calls to action
- Inclusive and accessible language
- Internationalization
- Numbers, dates and units
- Checking content

## Voice and tone
- **Voice is constant** — 3–4 adjectives with "this, not that" pairs, e.g. *clear, not clever · warm, not chummy · confident, not bossy*.
- **Tone adapts to the moment**: celebrate lightly on success, be calm and specific in errors, neutral in settings, careful in destructive or legal moments. Write a small tone table for the product: situation → how the user feels → how we sound → example.
- **Plain language first**: aim for reading age ~9–12 for consumer products (GOV.UK's bar), short sentences, common words, active voice, the user as "you".

## Writing rules for every component
- **Front-load** the important words; people scan the first two.
- **Sentence case** everywhere (titles, buttons, labels, menu items) — easier to read and to translate.
- **Labels are nouns, buttons are verbs.** Field labels say what to enter ("Email address"), not instructions ("Enter your email").
- **Hint text** explains format or why we ask — never repeats the label, never replaces it (placeholders disappear).
- **No ambiguity in numbers and time**: "3 days left" beats "Expires soon".
- **Length budgets**: button ≤ 3 words, toast ≤ 2 lines, tooltip ≤ 1 short sentence, error summary items ≤ 1 line.

## Errors
Pattern: **what happened → why (if useful) → how to fix it**, in that order, in the user's words, without blame.

| Bad | Good |
|---|---|
| Invalid input | Enter a date in the past, like 27 3 2007 |
| Error 403 | You don't have access to this project. Ask an admin to add you. |
| Oops! Something went wrong 😕 | We couldn't save your changes. Check your connection and try again. |

- Inline field errors start with what to do ("Enter…", "Select…"); the error summary repeats them as links to the fields (GOV.UK pattern).
- Never only "Something went wrong": give a reference ID for support on system errors.
- Don't apologize for the user's mistakes; do apologize for ours.
- Destructive confirmations name the object and consequence: "Delete 3 projects? This can't be undone." — buttons "Delete projects" / "Cancel", never "OK".

## Empty states
- Say **why it's empty** and the **one next action**: first use ("You haven't created a project yet." + "Create project"), no results ("No results for 'tx-42'." + "Clear filters"), cleared ("You're all caught up.").
- No jokes in work tools when the user is blocked; a light touch is fine for "all caught up".

## Buttons, links and calls to action
- **Verb + object**: "Download report", "Invite teammate", "Start free trial". Avoid "Get started", "Learn more", "Click here", "Submit" (`ds.py taste` flags them).
- Link text makes sense **out of context** (screen-reader link lists): "Read the pricing FAQ", not "here".
- Keep primary/secondary labels parallel ("Save draft" / "Publish").

## Inclusive and accessible language
- People-first or identity-first per community preference; avoid ableist idioms ("crazy", "blind to", "lame"), gendered defaults ("guys", "he" for unknown users — use "they"), and violent metaphors ("kill", "execute" in user-facing copy where avoidable).
- Avoid "simply", "just", "easy" — it isn't for everyone.
- Don't rely on direction or color in instructions ("click the green button on the right"); name the control.
- Emoji: decorative only, never the only carrier of meaning; screen readers read their names.

## Internationalization
- **Expansion**: allow +30–40% text length for most languages, and +200–300% for very short strings (labels, buttons). Layouts must wrap, never truncate key actions. German, Finnish and Russian are good stress tests.
- **Never concatenate sentence fragments** ("You have " + n + " items"); word order and grammar differ. Use full messages with placeholders.
- **Plurals and gender** with ICU MessageFormat — CLDR plural categories are `zero one two few many other` (English uses `one`/`other`; Arabic uses all six):
  `{count, plural, =0 {No files} one {# file} other {# files}}`.
- **Bidirectional text**: logical CSS properties (already a system rule), `dir="auto"` on user-generated content, mirrored directional icons.
- **Pseudo-localization** before translation: render strings as `[Ŝåvé çĥåñĝéš ~~~~~~]` (accents + ~40% padding + brackets) to catch truncation, concatenation and hard-coded text. Add it as a docs toggle next to RTL when the product ships in more than one language.

## Numbers, dates and units
- Format with the platform, never by hand: `Intl.NumberFormat` (currency, percent, compact "1.2K", units), `Intl.DateTimeFormat`, `Intl.RelativeTimeFormat` ("3 days ago"), `Intl.ListFormat` ("A, B, and C"), `Intl.PluralRules`.
- Show absolute dates on hover/focus or in `title`/`<time datetime>` when you show relative ones.
- Store and transmit ISO 8601 / UTC; display in the user's time zone and say which when it matters.
- Currency: code or symbol per locale; never assume `$`.

## Checking content
- `ds.py taste` flags buzzwords, placeholder copy, vague CTAs and emoji UI.
- Review checklist per component page: label/button/error/empty/success copy written; length budget respected; reads well when translated literally; no meaning carried only by color, emoji or position.
- Sources worth adopting wholesale: [GOV.UK style guide](https://www.gov.uk/guidance/style-guide), [Polaris content](https://polaris.shopify.com/content), [Polaris error messages](https://polaris.shopify.com/content/error-messages), [Atlassian content](https://atlassian.design/foundations/content), [Microsoft Writing Style Guide](https://learn.microsoft.com/style-guide), [Unicode CLDR plural rules](https://cldr.unicode.org/index/cldr-spec/plural-rules).
