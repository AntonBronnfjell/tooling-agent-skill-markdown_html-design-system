# Marketing sections & pages — specs

Scope `marketing` (enable with `ds.py init --scopes product,marketing` or add `"marketing"` to `ds.config.json → scopes`). Sections live in `components/<file>.html` (category **Marketing Sections**); full pages in `patterns/<file>.html` (category **Marketing Pages**). Pages compose sections; sections compose product components (buttons, cards, accordion, form fields, avatar, badge) — never re-style a button inside a hero.

## Contents
1. Rules for every marketing surface
2. Header, navigation & footer: announcement-bar, marketing-header, mega-menu, sticky-cta, locale-switcher, site-footer
3. Above the fold: hero
4. Proof: logo-cloud, testimonials, stats-band, press-mentions, trust-badges, social-proof-rating
5. Product story: feature-grid, feature-split, bento-grid, steps, video-section, gallery, integrations-grid
6. Conversion: pricing-table, comparison-table, cta-band, newsletter-signup, waitlist-form, countdown, faq
7. Content & company: blog-card-grid, content-section, team-grid, contact-section, roadmap, changelog-feed, app-store-badges, cookie-consent
8. Pages

## 1. Rules for every marketing surface
- **One `<h1>` per page** (the hero headline); sections start at `<h2>`; headings never skip levels. Eyebrows/overlines are `<p>` before the heading.
- **Performance is a design constraint:** the hero image/video poster is the LCP element — `fetchpriority="high"`, never `loading="lazy"`, explicit `width/height` (or `aspect-ratio`) so nothing shifts; everything below the fold lazy-loads. Serve AVIF/WebP via `<picture>` + `srcset`/`sizes`. No layout shift from web fonts (`font-display: swap` + metric-matched fallback).
- **Section rhythm** comes from tokens: `--section-padding-block-sm|md|lg` (fluid `clamp()`), `--section-gap`, `--section-max-inline`; display type from `--typography-display-*`. Sections are full-bleed backgrounds with a centered container — alternate `bg.canvas` / `bg.subtle` / `.theme-dark` (inverse) bands, never more than one inverse band in a row.
- **CTA hierarchy:** one primary action per section (button primary), at most one secondary (secondary/ghost or link). Labels are specific verbs ("Start free trial", "Book a demo"), not "Submit"/"Click here". Repeat the same primary CTA across the page.
- **Honest persuasion:** no fake scarcity, no pre-ticked consent, no confirm-shaming ("No thanks, I hate saving money"), reject/decline as visible as accept, prices include what users will actually pay.
- **SEO & sharing:** each page demo documents `<title>`, meta description, canonical, Open Graph/Twitter image, and JSON-LD where relevant (`Organization`, `Product`/`Offer` for pricing, `FAQPage`, `Article`/`BlogPosting`, `BreadcrumbList`).
- **Motion budget:** one signature motion moment per page at most (hero or bento hover); marquees and count-ups stop under reduced motion; nothing auto-advances without a pause control.
- **Analytics-ready, not analytics-coupled:** CTAs and forms carry `data-track="<section>-<action>"` hooks; no vendor scripts in the system.
- **i18n:** copy can grow ~35% (German, Finnish); layouts must not depend on headline length; logical properties throughout.

## 2. Header, navigation & footer

### announcement-bar
- Full-width strip above the header: short message + link ("Read the launch post →"). Dismiss button `aria-label="Dismiss announcement"`; dismissal persisted (localStorage, try/catch) and keyed by announcement id so a new one shows again. It's a `region` with a label, not an alert (it's present on load).

### marketing-header
- `<header>` → logo link, `<nav aria-label="Main">` (links or mega-menu triggers), secondary links (Sign in), primary CTA button. Variants: transparent over the hero (text uses the hero's theme — wrap in `.theme-dark` over dark media), sticky solid after scroll (toggle a class via IntersectionObserver on a sentinel, not scroll listeners), mobile: menu button (`aria-expanded`, `aria-controls`) opening a full-height disclosure panel; the CTA stays visible.
- Sticky header height feeds `scroll-padding-top` so anchor jumps and focused elements aren't hidden.

### mega-menu
- **Disclosure navigation, not `role="menu"`:** trigger `<button aria-expanded aria-controls>`; panel is a region of grouped link lists with headings, optional featured card. Opens on click (hover-intent optional, with delay, never hover-only); Esc closes and returns focus; Tab moves through links naturally and leaving the panel closes it. On mobile it becomes nested disclosures in the menu panel.

### sticky-cta
- Appears after the hero's CTA scrolls out of view (IntersectionObserver), hides near the footer CTA. Mobile: bottom bar with safe-area padding; the page gets matching bottom padding so content and focus are never covered (WCAG 2.4.11). Not announced; just reachable.

### locale-switcher
- Native `<select>` (labelled "Language") or a disclosure listing languages **in their own language** (`Deutsch`, `日本語`) with `lang` attributes on each option/link; never flags for languages. Region and language may be separate. Switching navigates to the localized URL (hreflang alternates documented).

### site-footer
- `<footer>` (contentinfo): logo + one-line description, link columns with headings (Product, Company, Resources, Legal), newsletter-signup (inline variant), social icon links (`aria-label="Acme on LinkedIn"`), locale-switcher, legal bar (© year, Privacy, Terms, Cookie settings — reopens cookie-consent preferences). Columns collapse into `<details>` groups on mobile. Variants: fat, with newsletter, minimal (single row), legal bar only.

## 3. Above the fold

### hero
- Anatomy: optional eyebrow/announcement pill → `<h1>` headline (≤ ~10 words, `display` or `display-lg`, `text-wrap: balance`) → subhead (≤ 2 sentences, `lead`, `--size-measure`) → CTA group (primary + secondary) → optional social proof line ("Trusted by 4,000 teams" + avatar group or rating) → media.
- Variants: centered; split media (copy at inline-start, media at inline-end, stacks on mobile with copy first); with email capture (inline form: label — visible or `sr-only` — email input + submit, consent microcopy, success state inline); with video (poster image is the LCP; play button opens/plays with captions; never autoplay with sound; muted ambient loops pause under reduced motion and have a pause control); with product shot (framed screenshot, `alt` describes what it shows); inverse (on `.theme-dark` or brand gradient — contrast pairs checked for text over it).
- Text over images needs a scrim token and a contrast check against the darkest/lightest image area; prefer not overlaying text on busy imagery.

## 4. Proof

### logo-cloud
- `<ul>` of logos, each `<img alt="Company name">` (not "logo"), monochrome via CSS (`filter: grayscale(1)` + opacity, or single-color SVG using `currentColor`), equal optical size (fixed height box, `object-fit: contain`). Heading like "Trusted by teams at". Marquee variant: CSS animation duplicating the list (`aria-hidden` on the duplicate), pauses on hover/focus and stops under reduced motion; provide a pause button if it runs > 5s.

### testimonials
- `<figure>` → `<blockquote>` (the quote, `<p>`s) → `<figcaption>` (avatar `alt=""` since the name is adjacent, name, role, company, optional company logo). Single large quote, grid (masonry-like with `columns`), carousel (follows the carousel spec: no autoplay, prev/next, "2 of 6"), with rating (stars as `role="img" aria-label="5 out of 5 stars"`). Real attribution only; long quotes truncate with "Read more" disclosure.

### stats-band
- `<dl>`: `<dt>` label, `<dd>` big value (`tabular-nums`, display size) with unit and footnote marker if claims need sourcing. Count-up only on first reveal, final value in the DOM from the start, disabled under reduced motion.

### press-mentions · trust-badges · social-proof-rating
- Press: outlet logos (`alt` = outlet name) or pull quotes linking to the article. Trust: SOC 2 / ISO 27001 / GDPR / HIPAA badges as images with full names in `alt`, linking to the trust center; never decorative-only. Rating summary: "4.8 out of 5 from 1,240 reviews on G2" as text + stars (`aria-hidden` stars when the text says it), link to the source.

## 5. Product story

### feature-grid
- `<ul>` of features: icon (decorative, `aria-hidden`), `<h3>` title, short text, optional "Learn more" link whose accessible name includes the feature ("Learn more about audit logs"). 3 columns desktop → 2 → 1 via auto-fit grid. Icons share one style and size token.

### feature-split
- Two-column section: copy (eyebrow, `<h2>`, text, checklist `<ul>` with check icons, CTA) and media (screenshot, illustration, short muted loop). Alternating variant flips media side every other row with `:nth-child(even)` + `order`/grid areas — DOM order stays copy-then-media for screen readers and mobile.

### bento-grid
- CSS grid with explicit spans (`grid-column: span 2`, `grid-row: span 2`) collapsing to a single column on small screens; each tile is a card (title, text, media). Hover lift via shadow tokens only; if tiles are links, use the card stretched-link pattern. Keep reading order sensible when spans reflow.

### steps
- `<ol>` with large step numbers (CSS counters, `aria-hidden` on the visual number since `<ol>` already conveys order), title, text, optional media per step; horizontal on desktop, vertical timeline on mobile.

### video-section
- `<figure>`: poster + play button (`aria-label="Play video: Product tour, 2 minutes"`) that swaps in `<video controls>` or a privacy-friendly embed (load third-party iframes only after click — facade pattern). Captions `<track kind="captions">` required; transcript in a disclosure below.

### gallery
- `<ul>` of `<figure>`s with captions; grid or CSS `columns` masonry; clicking opens the lightbox (overlay spec) with prev/next. All images lazy, responsive `sizes`.

### integrations-grid
- Logo tiles linking to integration pages; category filter chips (toggle buttons / radio group) that filter the list without reloading, with result count announced politely and a no-results state with "Clear filters". Optional search input.

## 6. Conversion

### pricing-table
- Billing toggle = radio group or segmented control ("Monthly" / "Annual — save 20%"), not a switch, and it updates all prices; announce the change politely ("Showing annual prices"). Prices in the DOM for both periods (swap with `hidden`) so there's no layout jump.
- Plan card: name, one-line audience, price (`<data value="29">$29</data>` + "/user/month", billed-annually note), primary CTA, feature list (`<ul>` with check icons; unavailable features shown with text "Not included", not just a gray icon), optional "Most popular" badge (text, not color-only) on the highlighted plan (elevated border + `selected` tokens). Enterprise card swaps price for "Custom" + "Contact sales".
- Equal-height cards, CTA aligned at the bottom (grid + `align-content`). Taxes/currency note under the table. Mobile: cards stack, highlighted plan first or a plan switcher (tabs).

### comparison-table
- Real `<table>`: plans as column headers (`scope="col"`), features as row headers (`scope="row"`), grouped by `<tbody>` with group header rows; check/cross icons carry text ("Included"/"Not included", visually hidden). Sticky header row with plan names + CTAs on scroll; horizontal scroll container on mobile (focusable region with label) with sticky first column.

### cta-band
- `<section>` with `<h2>`, one sentence, primary (+ optional secondary) CTA. Centered, split (copy + CTA side by side), inverse (on `.theme-dark` or brand surface). Usually the last section before the footer.

### newsletter-signup · waitlist-form
- Form with visible label (or `sr-only` + placeholder example), `type="email" autocomplete="email"`, submit button with specific label ("Subscribe"), consent microcopy with privacy link, honeypot field for bots (visually hidden, `tabindex="-1"`, `autocomplete="off"`). States: submitting (`aria-busy`, disabled submit), success (replace the form with a message and move focus to it), invalid (inline error + `aria-invalid`), server error (keep the email). Waitlist adds optional role/company and shows queue position on success.

### countdown
- `<time datetime="2026-11-01T17:00:00Z">` with a visual countdown; `role="timer"` but **not** `aria-live` per second — announce only on meaningful changes (e.g. "Launch starts in 1 hour"). Static text fallback without JS; "Live now" / "Ended" states; time zone shown.

### faq
- `<details>`/`<summary>` accordion (exclusive with `name` optional), questions as the summary text, answers as prose; two-column variant splits the list on desktop; ends with a "Still have questions? Contact us" CTA. Document emitting `FAQPage` JSON-LD from the same content.

## 7. Content & company

### blog-card-grid
- `<ul>` of `<article>` cards: cover image (lazy, fixed aspect ratio), category tag, `<h3>` title as the stretched link, excerpt (line clamp 3), author avatar + name, `<time datetime>`, reading time. Featured variant: first post spans two columns with larger type; list variant: horizontal cards. Loading skeletons and empty state.

### content-section
- Long-form `.prose` with `--size-measure`, optional sticky TOC (`toc` component) and aside (callouts, related links). Anchored headings with copy-link buttons (`aria-label="Copy link to section: Data retention"`).

### team-grid
- `<ul>` of `<figure>`: photo (`alt=""` when the name is adjacent), name, role, optional short bio (disclosure) and social links with full accessible names ("Ana Ruiz on GitHub").

### contact-section
- Contact form (name, email, company, topic select, message, consent) following form rules + error summary; contact details in `<address>` with `tel:`/`mailto:` links; map is optional, lazy, with a text address and "Open in Maps" link (map is never the only way). Success state replaces the form and receives focus.

### roadmap · changelog-feed
- Roadmap: columns (Now / Next / Later) of cards with status badges (text), or a timeline; no dates promised unless real. Changelog: `<ol>` of `<article>`s with `<time>`, version, tags (New / Improved / Fixed as text badges), prose, optional media; anchor per entry; RSS/subscribe link.

### app-store-badges
- Official Apple/Google badge artwork (follow their brand guidelines — don't recolor), `alt="Download on the App Store"` / `alt="Get it on Google Play"`, consistent height; QR variant for desktop with the URL as text too.

### cookie-consent
- Banner (non-modal region at the bottom, or a modal `<dialog>` where law requires blocking) with **Accept all, Reject all, Customize** at equal visual weight; preferences dialog lists categories (Necessary — always on, disabled checkbox with explanation; Analytics; Marketing) with **nothing pre-checked**; Save preferences. Choice persisted; a "Cookie settings" link in the footer reopens it. No tracking scripts load before consent (document the `data-consent-category` contract). Focus moves into the banner only if it's modal; otherwise it's reachable near the start of the tab order (or via skip link).

## 8. Pages (patterns/)

Each page is a full composition of sections with realistic copy (not lorem ipsum — copy length drives layout), demoed in light and dark, mobile and desktop, with its SEO/meta block documented in the usage section.

| Page | Composition |
|---|---|
| **landing-page** | announcement-bar? → marketing-header → hero → logo-cloud → feature-grid / bento-grid → feature-split ×2–3 → stats-band → testimonials → pricing teaser or cta-band → faq → cta-band → site-footer (+ cookie-consent). Variants: SaaS, product (physical/app), minimal (hero + 3 features + CTA). |
| **pricing-page** | header → short hero (h1 + toggle) → pricing-table → comparison-table → trust-badges → faq → cta-band (talk to sales) → footer. |
| **legal-page** | header → title + last updated `<time>` → content-section with TOC and anchored headings → contact for privacy questions → footer. Print-friendly. |
| **about-page** | hero (mission) → story content-section → stats-band → values feature-grid → team-grid → press-mentions → careers cta-band. |
| **blog-index** | header → featured post → category filter chips → blog-card-grid → pagination/load more → newsletter-signup. Empty state for filters. |
| **blog-article** | header → breadcrumbs → title, meta (author, date, reading time), cover → content-section with TOC → author box → share links → related blog-card-grid → newsletter. `Article` JSON-LD. |
| **contact-page** | short hero → contact-section → office locations (description list) → faq (support links). |
| **waitlist-page** | minimal header (logo only) → centered hero with waitlist-form (+ countdown optional) → small social proof → minimal footer. |
| **changelog-page** | hero (subscribe) → filters (tags) → changelog-feed → pagination. |
| **careers-page** | hero → values/benefits feature-grid → team photos gallery → job list (filterable list-group: title, team, location, type) → job detail (content-section + apply CTA) → no-openings empty state with talent-network signup. |
| **customer-stories** | index: filter by industry → card grid with result metric ("−40% churn"); story: hero with customer logo → stats-band → content-section with pull quotes (testimonials) → cta-band. |
