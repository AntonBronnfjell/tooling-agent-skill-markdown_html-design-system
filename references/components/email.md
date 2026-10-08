# Email components & templates — specs

Scope `email` (enable with `ds.py init --scopes product,email` or add `"email"` to `ds.config.json → scopes`). Components live in `components/<file>.html` (category **Email**); full templates in `patterns/<file>.html` (category **Email Templates**). **Email is a separate rendering target**: it does not link `css/`, does not use `var(--…)`, and does not load `js/`. The docs page for each email component is a normal web page that *embeds* the rendered email in an `<iframe srcdoc>` (so the docs CSS can't leak in) plus a "Source" code block. See `email-build.md` for how tokens become literal values.

## Contents
1. Rules for every email
2. Structure: email-shell, email-header, email-footer, email-spacer
3. Content: email-hero, email-text, email-image, email-button, email-columns
4. Data & utility: email-product-row, email-receipt, email-alert, email-code, email-social
5. Templates

## 1. Rules for every email
Sources: Can I Email, Litmus/Email on Acid dark-mode guides, MJML/React Email/Maizzle output conventions, email accessibility guidance (Email Markup Consortium reports, NSW email design system). Client support changes — re-check caniemail.com before relying on a property.

- **Tables for layout, `role="presentation"` on every layout table** (`cellpadding="0" cellspacing="0" border="0"`), so screen readers don't announce "table, row 1 of 6". The only real data table is `email-receipt` (with `<th scope>`).
- **600px max content width**, centered: outer 100% table → inner `max-width:600px; width:100%` div/table, wrapped in an MSO "ghost table" `<!--[if mso]><table width="600">…<![endif]-->` because Word-engine Outlook ignores `max-width`.
- **Inline CSS** on every element (built by the renderer, not hand-written); a `<style>` block in `<head>` only for progressive enhancement: media queries, `:hover`, dark mode, `[data-ogsc]` hooks. Gmail supports `<style>` in head but strips the whole block on errors and in some non-Gmail-account contexts (GANGA) — *uncertain/varies; design so the inline-only render is complete.*
- **No flexbox, grid, CSS custom properties, `position`, `float` for layout, or web fonts as a requirement.** Word-engine Outlook (classic Outlook for Windows) supports none of these; Microsoft says classic Outlook remains supported until at least 2029, so keep VML/MSO fallbacks for now. Custom properties also fail in Gmail.
- **Tokens resolved to literal values at build** — hex colors (not `rgb()`/`hsl()`/`oklch()`; use 6-digit hex, Outlook mishandles shorthand in some attributes), px sizes (not rem), font stacks with safe fallbacks (`-apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif`). The `email` token profile is a flat map generated from the DS tokens (light + dark).
- **Dark mode**: `<meta name="color-scheme" content="light dark">` + `<meta name="supported-color-schemes" content="light dark">` and `:root{color-scheme:light dark}` in `<style>`; `@media (prefers-color-scheme: dark)` overrides (Apple Mail, Outlook macOS/iOS, some others) + `[data-ogsc]`/`[data-ogsb]` selectors for Outlook.com/apps. Gmail apps and Outlook Windows may **force-invert** regardless — so: never put text in images, avoid pure `#000`/`#fff` (use `#111111`/`#fafafa`-ish tokens so inversion lands well), transparent PNG logos get a **halo** (1–2px light stroke or a padded rounded background) so a dark logo stays visible on dark backgrounds, or ship a dark logo swapped via media query (with the light one as default).
- **Images**: `width` attribute + `style="display:block;max-width:100%;height:auto;border:0"`, meaningful `alt` (or `alt=""` for decorative), styled alt text (`font`, `color` on the img) because many clients block images by default; @2x assets sized down. Never an image-only email (spam score + unreadable with images off). Absolute HTTPS URLs only.
- **Accessibility**: `<html lang="en" dir="ltr">` and repeat `lang`/`dir` on the main wrapper (some clients strip `<html>`); real `<h1>`–`<h3>` and `<p>` (styled inline, margins reset) — not `<td>` with big fonts; `<title>` set to the subject; body text **16px** (14px absolute minimum for small print), line-height ~1.5; contrast 4.5:1 checked on both light and forced-dark backgrounds; link text that makes sense alone ("Reset your password", not "Click here"); underline body links; buttons ≥ 44px tall; reading order = source order (stacked columns).
- **Preheader hack**: first element in `<body>` is a hidden div with the preview text followed by filler (`&#847;&zwnj;&nbsp;` repeated, ~100 chars) so clients don't pull body copy into the preview: `display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:transparent`. It complements, not repeats, the subject.
- **Bulletproof buttons**: padding/border-based `<a>` (not image), with `<!--[if mso]>` `v:roundrect` VML so Outlook renders the shape and the whole area is clickable. See `email-button`.
- **Gmail clips at ~102KB** of HTML (not counting images): budget ≤ 80KB minified; minify, avoid repeated inline style bloat, keep the unsubscribe link reachable (clipping hides the footer). The build reports size and fails above the budget.
- **Plain-text part is required** (multipart/alternative): same content and every link URL written out; the renderer generates it from the same content model (not by stripping HTML).
- **Mobile**: fluid/hybrid layout works without media queries (Gmail apps with non-Google accounts ignore them — *uncertain, varies by version*); media queries only enhance (full-width buttons, larger type).
- **Compliance**: marketing email footer has unsubscribe (one-click `List-Unsubscribe` + `List-Unsubscribe-Post` headers — required by Gmail/Yahoo bulk sender rules since 2024), physical postal address, why-you-got-this line. Transactional email may omit unsubscribe but links notification preferences. BIMI (brand logo in inbox) is DNS/DMARC + SVG Tiny PS — out of scope for templates, mention in docs only.
- **Security copy**: auth emails never include passwords; state expiry; "If you didn't request this, ignore it"; links point to your own domain (no URL shorteners).

## 2. Structure

### email-shell
- `<!doctype html>`, `<html lang dir xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">`, head: `charset utf-8`, `viewport`, `x-apple-disable-message-reformatting`, `format-detection` (telephone=no, date=no, address=no, email=no), color-scheme metas, `<title>`, MSO `<o:OfficeDocumentSettings><o:PixelsPerInch>96` block, `<style>` (resets, media queries, dark mode). Body: `margin:0;padding:0;width:100%;background:<canvas>` → preheader → wrapper `<div role="article" aria-roledescription="email" aria-label="<subject>" lang dir>` → outer table → ghost table 600 → content rows. Variants: dark-mode-aware (dark overrides present), RTL (`dir="rtl"`, `align="right"` attributes flipped by the renderer), Outlook ghost-table demo.

### email-header
- Row with logo `<img width="120" alt="Acme">` (alt = brand name) linked to home; optional "View in browser" small link (text, inline-end). Dark logo variant: two images, the dark-mode one hidden by default (`display:none; mso-hide:all`) and swapped in `@media (prefers-color-scheme: dark)`; fallback halo for clients that invert.

### email-footer
- Small print (14px, muted-but-4.5:1 color): why received ("You're receiving this because you signed up at acme.com"), **Unsubscribe** and **Manage preferences** links (descriptive text), company legal name + postal address (`<address>` is fine, style inline; disable auto-linking with a zero-width joiner or `format-detection`), social links, legal copy. Transactional variant: "Notification settings" instead of unsubscribe, support contact.

### email-spacer
- Spacer: `<tr><td height="24" style="height:24px;font-size:0;line-height:0;mso-line-height-rule:exactly">&nbsp;</td></tr>`. Divider: `td` with `border-top:1px solid <border>` and spacer padding around. Sizes from space tokens (16/24/40px).

## 3. Content

### email-hero
- Optional image (full width) → `<h1>` (28–32px, line-height 1.25) → intro `<p>` → email-button. Background-image variant: CSS `background-image` + `background-color` fallback, and VML `v:rect` with `v:fill type="frame"` inside `<!--[if gte mso 9]>` for Outlook — text must remain readable on the fallback color. Inverse: dark background token with light text (checked against forced inversion).

### email-text
- Headings and paragraphs with all styles inline (`margin:0 0 16px; font-family; font-size:16px; line-height:24px; color`). Lists: real `<ul>`/`<ol>` with explicit `margin`/`padding-inline-start` (Outlook indents differently — *known inconsistency*), or a table-of-bullets fallback. Links: color token + `text-decoration:underline`. Small print variant 14px.

### email-image
- See image rules. Linked variant wraps in `<a>` (alt describes destination). Retina: source 2× width, `width` attribute at 1×. Images-off demo: blocked image showing styled alt text on the bg color.

### email-button
```html
<!--[if mso]>
<v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word"
  href="https://acme.com/verify?t=…" style="height:48px;v-text-anchor:middle;width:220px" arcsize="17%"
  stroke="f" fillcolor="#1F5EFF"><w:anchorlock/>
  <center style="color:#FFFFFF;font-family:Arial,sans-serif;font-size:16px;font-weight:bold">Verify email</center>
</v:roundrect><![endif]-->
<!--[if !mso]><!-- --><a href="https://acme.com/verify?t=…" style="display:inline-block;background:#1F5EFF;color:#FFFFFF;
  font:bold 16px/48px Arial,sans-serif;padding:0 24px;border-radius:8px;text-decoration:none;min-width:172px;text-align:center">Verify email</a><!--<![endif]-->
```
- Label is a specific verb; one primary button per email (secondary = outlined/text link). VML needs fixed width — the renderer estimates width from label length (or use the padding-only "border-based" button with `mso-padding-alt` as a simpler alternative; *trade-off: no rounded corners in Outlook*). Full-width on mobile via media query. Dark mode: button colors chosen to survive inversion (mid-tone brand color, white text). Always followed (in auth emails) by the raw URL as text for copy/paste.

### email-columns
- Hybrid ("spongy") layout: `<!--[if mso]><table><tr><td width="300"><![endif]-->` `<div style="display:inline-block;width:100%;max-width:300px;vertical-align:top">…</div>` `<!--[if mso]></td><td width="300"><![endif]-->`… Columns wrap below 600px without media queries; source order = mobile reading order. Reverse-on-mobile uses `dir="rtl"` on the parent and `dir="ltr"` on children (classic trick). Container font-size 0 to kill inline-block gaps, reset inside.

## 4. Data & utility

### email-product-row
- Image (linked, alt = product name), name (link), price: sale shown as text "Was $40.00, now $28.00" with strike styling (`<del>` isn't reliable announcement — include the words), optional button "Shop now" with product name in surrounding text. Grid-2 uses email-columns.

### email-receipt
- `<table role="table">` (or no role) with `<caption>` (visually styled heading "Order summary"), `<thead>` Item / Qty / Price with `<th scope="col">`, rows with item name as `<th scope="row">`, right-aligned (logical: `align` attribute flipped in RTL) numeric cells with literal currency strings formatted at build (`Intl`/Babel equivalent server-side). Totals in `<tfoot>`: Subtotal, Discount, Shipping, Tax, **Total**. Mobile stacked variant: item name full width, qty+price on the next line via a nested table. Addresses + payment method ("Visa •••• 4242") in two columns below.

### email-alert
- Single-cell table with `border-left:4px solid <status>` + tinted bg, leading `<strong>` text label ("Security notice:", "Payment failed:") — never color-only, no icon fonts (PNG icon with alt optional).

### email-code
- Code on its own line: `font-family:Menlo,Consolas,monospace; font-size:28–32px; letter-spacing:6px; font-weight:bold`, on a subtle bg cell; preceded by "Your verification code is" and followed by expiry ("Expires in 10 minutes"). Plain text, selectable (no image, no individual-digit cells that break copy). Put the code in the subject/preheader only if product policy allows (*trade-off: convenience vs exposure on lock screens*). Magic-link fallback: button + raw URL.

### email-social
- Row of 24–32px PNG icons (`alt="Acme on Instagram"`), spaced with padding not margins; text-links variant for minimal transactional mail; dark-mode variant uses light icons or circular backgrounds.

## 5. Templates (patterns/)

Each template ships: HTML (inlined, minified size shown), plain-text part, subject + preheader examples, light/dark/images-off screenshots in docs, and a client-test checklist (Apple Mail, Gmail web/app, Outlook classic Windows, new Outlook, Outlook.com, Yahoo).

| Template | Composition |
|---|---|
| **email-verify** | shell → header → h1 "Confirm your email" → text → email-button "Verify email" → OR email-code (variant) → raw link → "expires in 24 hours" → "didn't sign up? ignore" → transactional footer. |
| **email-password-reset** | shell → header → h1 → text (requested at time, from device/location if known) → button "Reset password" → raw link → expiry → email-alert (security: "If you didn't request this, your account is still safe…") → support link → footer. |
| **email-order-confirmation** | shell → header → h1 "Thanks for your order, Ana" + order # → delivery estimate → button "View order" → email-receipt (items, totals) → addresses + payment → help/returns text → footer. Shipped variant adds tracking button + carrier; receipt variant drops delivery block. |
| **email-invite** | shell → header → (avatar of inviter, alt name) → h1 "Sam invited you to join Acme Design" → workspace details → button "Accept invite" → expiry → "Not expecting this? Ignore" → footer. |
| **email-newsletter** | shell → header (view in browser) → hero story → email-spacer → 2-col article cards (email-columns: image, h2, excerpt, "Read: <title>" link) → email-product-row (optional) → social → marketing footer (unsubscribe, address). Watch the 102KB budget. |
| **email-notification-digest** | shell → header → h1 "Your weekly summary" → grouped sections (h2 per project, list of items with linked titles, counts, time) → "View all activity" button → footer with prominent "Manage notification settings". Empty-skip variant documents: don't send when there's nothing to say. |

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
