# Commerce components & pages — specs

Scope `commerce` (enable with `ds.py init --scopes product,commerce` or add `"commerce"` to `ds.config.json → scopes`). Components live in `components/<file>.html` (category **Commerce**); full pages in `patterns/<file>.html` (category **Commerce Pages**). Commerce components compose product components (button, radio, checkbox, form-field, select, combobox, drawer, modal, badge, rating, accordion, stepper, table) — never re-style a radio inside a shipping method card; wrap it.

## Contents
1. Rules for every commerce surface
2. Price & product: price, product-badge, product-card, product-gallery, variant-picker, quantity-stepper, stock-delivery, add-to-cart, wishlist-button, size-guide
3. Discovery: facets, sort-control, recently-viewed, reviews-summary, review-item
4. Cart: mini-cart, cart-line-item, order-summary, promo-code
5. Checkout: checkout-steps, address-form, shipping-method, payment-method
6. Post-purchase: order-confirmation, order-tracking
7. Pages

## 1. Rules for every commerce surface
Mostly from Baymard Institute checkout/product-page research; GOV.UK payment-card and address patterns for field details. Percentages quoted by Baymard change with each benchmark — cite the rule, not the number.

- **Show total cost early, no surprise costs.** Shipping (or "Free shipping over $50"), taxes/duties and fees are visible on the PDP or cart, never revealed first at the payment step. Order summary shows every line that makes the total; unknown values say why ("Calculated at next step") instead of `$0.00`.
- **Guest checkout is the default path**, visually first and at least as prominent as sign-in. Account creation is offered *after* purchase (order-confirmation `variant:guest-create-account`: just set a password).
- **Non-color variants are buttons, not dropdowns** (size, material, capacity): visible options let users scan availability at once. `<select>` is only a fallback for > ~12 options (`variant:dropdown-fallback`).
- **Unavailable variants stay visible but marked** — strikethrough/diagonal line *plus* text ("XL — sold out" in the accessible name), still focusable so users learn why; selecting one offers "Notify me", not a dead add-to-cart. Combinations that don't exist at all may be hidden (document per store).
- **Inline validation** on blur (`:user-invalid` + message), never on every keystroke, never only on submit; an error summary at the top of the step on submit (reuse `error-summary`). Errors say how to fix ("Enter a 5-digit ZIP code").
- **Address autocomplete + correct `autocomplete` tokens** on every field (`shipping given-name`, `shipping address-line1`, `postal-code`, `country`, `email`, `tel`, `cc-number`, `cc-exp`, `cc-csc`, `cc-name`). Browser autofill must keep working when a lookup combobox is layered on top.
- **Accessible payment fields** (GOV.UK): card number accepts spaces/hyphens (`inputmode="numeric"`, strip on submit, never `type="number"`), fields in the order printed on the card, one expiry field `MM/YY` or two labelled fields, CVC help explains where to find it. Hosted iframe fields (Stripe/Adyen/Braintree) must get a `title`, visible label outside the frame, and error text mirrored outside the iframe — *uncertainty: iframe internals are vendor-controlled; document what the system can't guarantee.*
- **Trust near the pay button**: lock icon + "Secure checkout" text, accepted card logos (`alt` = brand), return policy link, and the final total repeated beside the "Pay $123.45" button. Pay button label states the amount.
- **Price semantics**: machine value in `<data value="19.99">`; sale = `<del>` (compare-at) + `<ins>` (sale), with visually-hidden "Original price"/"Sale price" text because `<del>`/`<ins>` are not announced by most screen readers. Format with `Intl.NumberFormat(locale, {style:'currency', currency})` — never concatenate "$" + number; respect currency minor units (JPY 0, KWD 3). `tabular-nums` for columns of prices.
- **Never lose the cart or the form**: quantity/remove updates are optimistic with rollback + message; removal offers Undo (5–10 s, not timed-out silently); back button on any checkout step keeps entered data.
- **Live feedback without noise**: cart count, totals and filter result counts update via one polite live region (`js/lib/live-region.js`); add-to-cart success is announced ("Added: Linen shirt, M, 1 item. Cart total $48"). No `aria-live` on price elements themselves.
- **Honest commerce**: no fake countdowns, fake "12 people viewing", pre-ticked insurance/donations/newsletter, or hidden subscription upgrades. Low-stock only when true.
- **Performance**: PDP main image is LCP (`fetchpriority="high"`); PLP images lazy beyond the first row; explicit dimensions/aspect ratio on every product image.
- **Structured data**: PDP documents `Product` + `Offer`/`AggregateOffer` + `AggregateRating` JSON-LD; PLP `BreadcrumbList`.
- **Tokens**: add `commerce.price.sale`, `commerce.price.compare`, `commerce.stock.low|out|in`, `commerce.badge.*`, `commerce.swatch.ring` to the semantic layer and contrast pairs (sale red on white must still meet 4.5:1).

## 2. Price & product

### price
- `<p class="price">` containing `<data value>`; sale: `<del><span class="sr-only">Original price:</span> $40.00</del> <ins><span class="sr-only">Sale price:</span> $28.00</ins>` + optional "Save 30%" badge. Range: "From $18" or "$18–$32". Unit price: "$4.50 / 100 g" (EU legal requirement for many goods). Tax note: "incl. VAT" / "excl. tax" as `<small>`. Subscription: "$12 / month" with billing interval text. Free: the word "Free", not "$0.00". Sizes align with type scale; never color-only for sale (strikethrough + text).

### product-badge
- Text in a `badge` (New, Sale, −30%, Low stock, Sold out, Bestseller). Positioned over media in a fixed corner (logical inset), max two per card, ordered by priority. Never conveys the only stock info — the card text repeats it.

### product-card
- `<article>` → media (aspect-ratio token, `object-fit`, optional second image on hover for pointer devices only), badges, `<h3><a>` title as stretched link, price, rating summary ("4.6 out of 5, 212 reviews"), swatch preview (first 4 + "+3 more" text; swatches are links/buttons that change the card image, not a second stretched link — keep them above the stretched link with `position: relative; z-index`). Quick add: secondary button "Add Linen shirt to cart" (accessible name includes product); for multi-variant products it opens a size popover/drawer. Sold-out: badge + muted image (opacity token) + "Notify me". Loading: skeleton. Container query for horizontal variant.

### product-gallery
- Main `<figure>` + thumbnail `<button>`s (`aria-label="Show image 3 of 7: back view"`, `aria-current="true"` on active). Keyboard: thumbnails are tab stops (or roving focus group); arrows on main image optional. Zoom: hover-lens on pointer devices, tap opens `lightbox` (dialog with pinch zoom, prev/next, Esc). Video slide: poster with play icon in the thumbnail, `<video controls>` with captions, never autoplay with sound. Mobile: horizontal scroll-snap with dot-indicator + "3 / 7" text. Changing the variant swaps to that variant's first image and announces nothing (visual only) — the variant change itself is announced.

### variant-picker
- One `<fieldset>` per option with `<legend>` ("Color: Sage" — legend shows current value), options as `input[type=radio]` styled as swatches (color/image, with name in label, `title` tooltip) or size buttons. States: selected (ring token ≥ 3:1 + check), unavailable (diagonal strike + "sold out" in label text, still selectable → swaps CTA to "Notify me"), focus-visible, invalid when user hits add-to-cart without choosing ("Select a size" error under the legend, focus moves to the fieldset). Selection updates URL (`?variant=`), price, gallery, stock without reload. Color swatches need a 1px border token for white/light colors and forced-colors outlines.

### quantity-stepper
- Wraps `number-input`: `<button aria-label="Decrease quantity">−</button> <input type="number" inputmode="numeric" min="1" max="10" aria-label="Quantity, Linen shirt">` `<button aria-label="Increase quantity">+</button>`. Buttons disable at min/max (at min=1 in cart, show remove instead, or make "−" at 1 remove with confirmation via undo). Max = stock or purchase limit with message ("Only 3 available"). In cart: debounce 500 ms, `aria-busy` on the line during update.

### stock-delivery
- `role="status"` only for the dynamic part after variant change. In stock (icon + "In stock"), low ("Only 2 left" — real numbers only), out ("Sold out — notify me"), preorder ("Ships from 12 Nov"), backorder. Delivery: "Get it Tue 14 – Thu 16 Oct" using `<time>`; "Order within 3 h for next-day" only when computed server-side. Postcode check: small form with `autocomplete="postal-code"`. Pickup: store name, availability, "Change store".

### add-to-cart
- `<form>` with hidden variant id + `<button type="submit">Add to cart</button>`; works without JS (posts to cart). States: loading (`aria-busy`, spinner, label kept, width locked), added (check + "Added" for ~2 s, then opens mini-cart or shows toast with "View cart"), error (inline message + retry; preserve selection), disabled-until-option-selected — **prefer enabled + validation error** over disabled (Baymard: disabled buttons don't explain why). Buy-now (express wallet) as secondary below. Sticky mobile bar: appears when the main button scrolls out, includes price + button, safe-area padding, page gets matching bottom padding.

### wishlist-button
- `button[aria-pressed]` with `aria-label="Save Linen shirt"` (name constant, state via pressed) or visible label "Save"/"Saved". Signed-out: save locally and prompt to sign in to sync — never block. Announce "Saved to wishlist".

### size-guide
- Link-styled button "Size guide" next to the size legend → `modal` or `drawer` containing a real `<table>` (sizes as row headers, measurements as columns, `<caption>`), cm/in segmented control, how-to-measure illustration with text. Fit finder (height/weight → suggested size) is enterprise and must explain its basis.

## 3. Discovery

### facets
- `<form>` (works as GET without JS) of `<details open>` groups → `<fieldset>` checkboxes with counts ("Blue (12)"), color swatches as checkboxes, size buttons as checkboxes, price range (two number inputs + optional dual slider). Apply strategy: desktop instant-apply with polite "Showing 48 results"; mobile drawer with "Show 48 results" apply button and "Clear all". Applied chips row above results (`button` "Remove filter: Blue"). Zero-count options disabled or hidden (document choice). Long lists: "Show more" + in-group search. Filter state in URL.

### sort-control
- `<label>Sort by <select>` (Featured, Price low–high, Newest, Best rated). Native select is enough; change triggers reload/fetch, focus stays on the select, result announced.

### recently-viewed
- `<section aria-labelledby>` + `<ul>` of product-cards (compact) in a scroll-snap row with prev/next buttons; hidden when empty; "Clear history" button; stored in localStorage with try/catch. Same shell powers "You may also like".

### reviews-summary
- Average as text ("4.6 out of 5") + stars (`aria-hidden` since text present) + "Based on 212 reviews". Histogram: `<ul>` of rows, each a `<button>` "5 stars, 140 reviews" filtering the list (`aria-pressed`), bar is decorative (`aria-hidden` div width %) or `<meter>`. "Write a review" CTA. No-reviews state invites first review.

### review-item
- `<article>` → rating (`role="img" aria-label="4 out of 5 stars"`), `<h3>` title, body (truncate with "Read more" disclosure), author + "Verified buyer" text badge, `<time>`, variant purchased ("Size M, fits true to size"), photo thumbnails (open lightbox), "Helpful? Yes (12) / No" buttons with `aria-pressed`, merchant reply indented with label.

## 4. Cart

### mini-cart
- `drawer` (`<dialog>` modal, inline-end) titled "Cart (3 items)". Contents: free-shipping meter (`<progress>` + "You're $12 away from free shipping" — text carries the meaning), compact cart-line-items, subtotal with "Taxes and shipping calculated at checkout" (or real estimates), primary "Checkout", secondary "View cart". Opened after add-to-cart: focus goes to the dialog heading, not the first remove button. Empty: illustration + "Continue shopping". Upsell row optional, below items.

### cart-line-item
- `<li>`: image (link, `alt=""` since title adjacent), title link, options (`<dl>` Color/Size), unit price (if qty > 1), quantity-stepper, line total (`price`), remove (`button` "Remove Linen shirt"), save for later. States: updating (`aria-busy`, dimmed), removed (collapses to "Linen shirt removed. Undo" row, focus to that row), out-of-stock (alert text + must remove/move to proceed), price-changed (notice with old/new price). Compact variant for mini-cart and order-summary.

### order-summary
- `<aside aria-labelledby>` → item list (compact) → `<dl>` rows: Subtotal, Discount (code tag, negative value), Shipping ("Free" / amount / "Calculated at next step"), Tax ("Estimated"), **Total** (larger type, currency code when multi-currency: "USD $123.45"). Mobile checkout: collapsed `<details>` summary "Show order summary — $123.45" at the top. Uses `<dl>`, or a `<table>` when columns (qty/price) matter.

### promo-code
- `<details>` "Add discount or gift card" (collapsed by default — Baymard: prominent coupon fields make users leave to hunt codes) → field + "Apply" button. Applying: `aria-busy`. Applied: removable tag "SPRING10 — −$5.00" + updated summary announced. Invalid/expired: inline error with reason, field keeps value.

## 5. Checkout

### checkout-steps
- `<nav aria-label="Checkout progress"><ol>`: completed steps are links ("Edit shipping"), current has `aria-current="step"`, upcoming are plain text. Step text visible on desktop; on mobile "Step 2 of 4: Shipping". Accordion variant (one-page): each section a heading + edit button + summary of entered data once complete. Uses `stepper` visuals.

### address-form
- Country/region `<select autocomplete="country">` **first**; field set, labels and order change per country (ZIP vs Postcode vs 郵便番号; State vs County vs Prefecture; JP order is postal → prefecture → city). Fields: full name (one field preferred over first/last unless required by carrier), address line 1 (with lookup combobox), line 2 behind "Add apartment, suite, etc." link, city, region, postal code, phone (explain why: "For delivery questions"). Lookup: APG combobox with "Enter address manually" option always visible; a selection fills fields and focus moves to line 2. Validation: postal-code format per country; carrier address verification suggests correction ("Did you mean…?" radio between entered and suggested, entered is default-accepted). Saved addresses: radio cards + "Add new". Billing: "Same as shipping" checkbox checked by default.

### shipping-method
- `<fieldset><legend>Shipping method</legend>` of radio cards: name ("Standard"), delivery estimate with dates ("Arrives Oct 14–16"), price or "Free". Cheapest/default preselected only if it's genuinely the user's best default. Loading rates: skeleton + "Calculating shipping options" status. No rates: error with "Change address". Pickup variant: list of locations with distance and hours.

### payment-method
- Express wallets (Apple Pay, Google Pay, Shop Pay, PayPal) at the **top** of checkout, labeled "Express checkout", separated by "or". Main list: radio cards (Card, PayPal, BNPL "Pay in 4" with full terms link, saved cards "Visa ending 4242, expires 08/27"). Card form appears under the selected card radio: card number (`autocomplete="cc-number"`, brand icon detected, `inputmode="numeric"`), expiry (`cc-exp`), security code (`cc-csc`, help disclosure), name on card (`cc-name`). States: processing (pay button `aria-busy`, whole form inert, prevent double submit), declined (alert at top of payment section, focus moved there, card fields keep non-sensitive data), invalid. Billing address variant. Secure note + lock beside the pay button.

## 6. Post-purchase

### order-confirmation
- `<h1>` "Thank you, Ana! Your order is confirmed" (focus lands on it), order number (copyable), "Confirmation sent to ana@example.com", delivery estimate, summary (order-summary compact), shipping/billing addresses, payment method last 4, next steps, "Continue shopping". Guest: inline "Save your info for next time — create a password" (one field). Payment pending (bank transfer, BNPL review): status alert with what happens next.

### order-tracking
- `<ol>` of steps (Placed → Shipped → Out for delivery → Delivered) with `<time>`, current step `aria-current="step"`, text status not just icons. Carrier + tracking number link (opens carrier site, says so). Delayed/exception: warning alert with reason and new estimate. Split shipment: one timeline per package with item thumbnails. Reuses `timeline`.

## 7. Pages (patterns/)

Realistic product data (names, prices with real formatting, multiple currencies in one demo), light/dark, mobile/desktop, JSON-LD block documented in usage.

| Page | Composition |
|---|---|
| **plp** | header → breadcrumbs → `<h1>` category + result count → (desktop) facets sidebar · (mobile) "Filter" button opening facets drawer + sort-control → applied chips → product-card grid (auto-fill, container queries) → pagination or load-more ("Showing 24 of 120", announced) → recently-viewed → footer. No-results: suggestions + clear filters. |
| **pdp** | header → breadcrumbs → two-column: product-gallery · (h1 title, reviews-summary inline, price, product-badge, variant-picker, size-guide link, quantity-stepper, add-to-cart + buy-now, stock-delivery, wishlist-button, trust/returns line) → details accordions (Description, Materials, Shipping & returns) → reviews-summary + review-item list → recommendations (recently-viewed shell) → sticky add-to-cart on mobile. |
| **cart-page** | header → `<h1>` "Cart (3)" → cart-line-item list · order-summary (total visible above the fold on mobile too) with promo-code, express checkout, primary "Checkout" → saved-for-later → recommendations. Empty state with CTA. |
| **checkout-page** | Minimal header (logo + "Secure checkout", no main nav), no footer links except policies. Multi-step: checkout-steps → Contact (email; "Have an account? Sign in" link — guest is the default) → address-form → shipping-method → payment-method → review & pay (button "Pay $123.45"). One-page: same sections stacked as accordion (`variant:accordion-sections`). Sidebar order-summary (collapsible on mobile). Error summary per step; declined state. |
| **order-confirmation-page** | Minimal header → order-confirmation → order-tracking teaser (Placed) → order-summary → guest account creation → recommendations → footer. |
| **account-orders** | Account shell (settings/side-nav) → `<h1>` Orders → list/table: order #, date, total, status badge, item thumbnails, "View order" → detail: order-tracking, items, addresses, invoice download, Reorder, Return/Cancel (with eligibility text). Empty state. |

## Sources

## Commerce
- Baymard — Checkout UX guide: https://baymard.com/blog/checkout-flow-ux-optimization
- Baymard — Auditing checkout for hidden friction: https://baymard.com/blog/audit-checkout-flow-hidden-friction
- Baymard — research library (product page, cart, checkout, PLP filtering): https://baymard.com/research (some guidelines paywalled; rules cited from public articles)
- GOV.UK Design System — Payment card details: https://design-system.service.gov.uk/patterns/payment-card-details
- GOV.UK Design System — Addresses: https://design-system.service.gov.uk/patterns/addresses/
- web.dev — Payment form best practices: https://web.dev/articles/codelab-payment-form-best-practices
- web.dev — Address form best practices: https://web.dev/articles/codelab-address-form-best-practices
- HTML spec — autofill tokens: https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill
- Shopify Hydrogen React components (Money, ProductPrice, cart components): https://shopify.dev/docs/api/hydrogen-react/latest/components.md
- Shopify Hydrogen ProductPrice: https://shopify.dev/api/hydrogen/components/product-variant/productprice
- Shopify Checkout UI extensions (Polaris web components): https://shopify.dev/docs/api/checkout-ui-extensions/2025-10
- MDN — Intl.NumberFormat: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/NumberFormat
- MDN — <data>, <del>, <ins> (accessibility notes): https://developer.mozilla.org/en-US/docs/Web/HTML/Element/del
- WAI-ARIA APG — Combobox, Radio group: https://www.w3.org/WAI/ARIA/apg/patterns/
- schema.org Product / Offer: https://schema.org/Product

## Email
- Can I Email: https://www.caniemail.com/ (e.g. gap: https://caniemail.com/features/css-gap)
- Litmus — Ultimate guide to dark mode for email: https://www.litmus.com/blog/the-ultimate-guide-to-dark-mode-for-email-marketers
- htmlemail.io — Dark mode email styles: https://htmlemail.io/blog/dark-mode-email-styles
- Email on Acid — dark mode / Outlook guides: https://www.emailonacid.com/blog/
- Noble Desktop — Bulletproof buttons in Outlook (VML): https://www.nobledesktop.com/learn/html-email/bulletproof-buttons-in-outlook
- Campaign Monitor — bulletproof buttons / backgrounds generators: https://buttons.cm/ , https://backgrounds.cm/
- Gmail clipping (102KB): https://mxtoolbox.com/dmarc/email/email-clipping , https://help.drip.com/hc/en-us/articles/4424710412941-Avoid-Email-Clipping-In-Gmail
- Gmail CSS support: https://developers.google.com/gmail/design/css
- Email accessibility: https://email.designsystem.nsw.gov.au/content/accessibility-for-email-content-writers , https://resend.com/blog/6-tips-for-accessible-emails , https://www.emailmarkup.org/en/reports/
- Classic Outlook support until at least 2029: https://petri.com/microsoft-classic-outlook-for-windows-2029/
- MJML: https://documentation.mjml.io/
- React Email: https://react.email/docs
- Maizzle: https://maizzle.com/docs
- Gmail/Yahoo bulk sender requirements (one-click unsubscribe, RFC 8058): https://support.google.com/a/answer/81126 , https://www.rfc-editor.org/rfc/rfc8058
- BIMI Group: https://bimigroup.org/
