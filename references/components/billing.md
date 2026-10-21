# Billing components & pages — specs

Scope `billing` (enable with `ds init --scopes product,billing` or add `"billing"` to `ds.config.json → scopes`). It has no required scopes. Components live in `components/<file>.html` (category **Billing**); full pages in `patterns/<file>.html` (category **Billing Pages**). Billing components compose product components — `payment-card-entry`, `data-table`, `meter`, `alert`, `modal`, `delete-with-confirmation`, `button-primary`, `form-field`, `badge` — wrap them, never re-style them. This is in-app account billing, not storefront checkout and not a marketing page.

## Contents
1. Rules for every billing surface
2. Plan & payment: current-plan, plan-picker, payment-method-list, add-payment-method
3. Invoices & usage: invoice-list, invoice-detail, billing-usage, billing-alert
4. Lifecycle: cancel-flow
5. Money movement: transaction-list, payout-summary, wallet-balance, refund-dialog
6. Tax: tax-info-form
7. Pages

## 1. Rules for every billing surface
Sources: Baymard Institute and GOV.UK payment-card patterns (field order, autofill, error text), SEPA and ACH debit mandate text requirements, the click-to-cancel principle (FTC 2024 Negative Option rule, vacated 2025; state laws still apply), `Intl.NumberFormat` currency formatting, and print-stylesheet practice for invoices. Cite rules, not statistics.

- **Money is formatted, never concatenated.** Use `new Intl.NumberFormat(locale, {style:'currency', currency})` (it respects minor units: JPY 0, KWD 3) and mark the machine value up as `<data value="49.00">$49.00</data>`. Amounts in tables and totals use `font-variant-numeric: tabular-nums` and are end-aligned. Always show the currency when more than one can appear on the page.
- **Sign plus text, never color alone.** Credits, refunds and discounts show a leading sign (`−$12.00`, `+$50.00`) and a text label ("Refund", "Credit"); the semantic color (`color.feedback.<tone>.fg`) only reinforces it (WCAG 1.4.1). Use a real minus sign (U+2212) and `Intl.NumberFormat` `signDisplay: 'always'` for deltas; screen readers need the word, so add visually-hidden "Refund of" where the sign is the only cue.
- **Status is text.** Paid, Open, Overdue, Void, Pending, Refunded, Past due are words in a `badge` (with an icon), never a colored dot. Overdue and past-due state the consequence and date ("Service pauses on Nov 3").
- **Dates are unambiguous.** Render with `Intl.DateTimeFormat` inside `<time datetime>`; renewal and end dates say the exact day ("Renews Nov 3, 2026") and the time zone only when it changes the day.
- **Payment fields follow GOV.UK and Baymard.** Reuse the `payment-card-entry` rules by reference (do not restate or fork them): `autocomplete` `cc-*` tokens, `inputmode="numeric"` (never `type="number"`), spaces tolerated, labels outside hosted iframes, errors mirrored outside the frame. Document what vendor-hosted fields cannot guarantee.
- **Debit mandates carry required text.** SEPA Direct Debit and ACH authorizations show the creditor name and identifier, the mandate reference, what is authorized (recurring or one-off), the amount or how it is determined, the refund/dispute rights and the revocation route, and require an unticked explicit authorization checkbox. Store and show the mandate afterward.
- **Cancelling is as easy as signing up.** Design to the click-to-cancel principle (FTC 2024 Negative Option rule, vacated by the 8th Circuit in 2025; state laws such as California's still require it): cancellation is no harder than sign-up and terms (price, renewal, how to cancel) are clear before charging. The cancel entry point is visible in the billing page (not buried in support), uses the same channel as sign-up (online if you signed up online), and reaches confirmation in no more steps than sign-up took.
- **No dark patterns in billing.** No confirmshaming ("No, I don't want to save money"), no pre-ticked upgrades or add-ons, no hidden fees revealed at confirmation, no countdown pressure, no decoy emphasis that makes "keep" a button and "cancel" a faint link. Both choices are real buttons of comparable weight and honest labels.
- **Destructive and irreversible money actions are confirmed** with the amount and consequence in the dialog (`modal`, or `delete-with-confirmation` for removing a payment method); the confirm button repeats the action and amount ("Refund $12.00"). Focus starts on the least destructive control.
- **Trial, proration and renewal are previewed before commit.** Show what is charged now, what is charged next and when, and any credit applied, before the user confirms a plan change. A downgrade states which features are lost and when.
- **Failures are fixable.** A failed payment says why in plain words ("Your bank declined the charge"), the next retry date, and one fix action; do not show raw gateway codes as the only message. Past-due never blocks access to the billing page itself.
- **Live feedback is calm.** Saving, top-up and refund results announce once via one polite `role="status"` (`js/lib/live-region.js`); persistent problems use `billing-alert` (an `alert` role only when a failure just happened, otherwise `status` or none).
- **Invoices print.** Invoice surfaces ship an `@media print` stylesheet: hide navigation and actions, force a light high-contrast theme, avoid page breaks inside table rows (`break-inside: avoid`), repeat the table head across pages (`thead { display: table-header-group }`), and show the full numbers rather than links.
- **Privacy.** Show only the last four digits and brand of a card, never the full number or CVC; mask bank account numbers except the last digits; do not log or place payment data in the URL.
- **Tokens**: composes product tokens only (`color.text.{default,muted,subtle}`, `color.feedback.<tone>.{bg,fg,border,icon}`, `color.bg.surface`, `color.action.*`). No scope tokens, so no new contrast pairs; every status must keep its text and icon.
- **vs.**:
  - `billing-usage` vs ai `usage-meter`: `billing-usage` is metered plan usage against an allowance with money (seats, API calls, GB, overage cost); `usage-meter` measures model tokens and context.
  - `add-payment-method` vs commerce `payment-method`: `add-payment-method` saves a method to an account; commerce `payment-method` selects a method for one checkout.
  - `plan-picker` vs marketing `pricing-table`: `plan-picker` changes an existing account's plan with proration and the current plan marked; `pricing-table` is for prospects on a landing page.
  - Those scopes may be off; do not depend on them.

## 2. Plan & payment

### current-plan
- Markup: a labelled `<section>` (a region already; no extra `role`) with `<h2>` plan name, price as `<data value>` plus interval ("$49 / month"), a `<dl>` of renewal date, seats, payment method and the primary `button-primary` ("Change plan") with "Cancel plan" as a text link of normal size.
- `state:active`: "Renews Nov 3, 2026 for $49.00" plus next-invoice link. `state:trial`: days left as text ("Trial ends Nov 3 — 5 days left"), what is charged and when, and a "Add payment method" action if none exists.
- `state:past-due`: a `billing-alert` variant at top, the amount due, retry date and "Update payment method"; access consequences stated.
- `state:cancelled-until`: "Cancelled — access until Nov 3, 2026", a clear "Resume plan" button; nothing is charged after that date.
- Status `badge` has text and icon. Mobile: dl stacks, buttons full width. RTL: logical alignment; prices keep digits LTR via `<bdi>`.
- Failure: if plan data cannot load, show an inline error with retry, never an empty card.

### plan-picker
- Markup: `<fieldset>` + `<legend>` "Choose a plan" of native `input[type=radio]` cards (radio group semantics for free; arrows move selection). The interval switch is two radios ("Monthly", "Annual") in a second fieldset, not a custom switch.
- `variant:monthly-annual`: switching interval updates prices in place and announces "Annual billing: $490 per year, you save $98" via the polite live region; savings are stated as an amount.
- `state:proration-preview`: a `role="status"` summary below the cards: "Today: $18.40 prorated charge. From Nov 3: $79.00 / month." Updated on selection, not on every focus; the confirm button repeats the plan name.
- `state:downgrade-warning`: an `alert` (product `alert`) listing features lost and the date; confirmation is an explicit checkbox or second step only if the downgrade deletes data, otherwise just the button.
- The current plan card is marked with text "Current plan" and its radio is disabled with an explanation (not just dimmed). Keyboard: Tab to group, arrows between plans, Space selects, Enter on the confirm button. Reduced motion: no animated price counters.
- RTL: cards flow with logical properties. Failure: proration fetch failure keeps the picker usable and says the amount will be shown before charging.
- For prospects use marketing `pricing-table` instead.

### payment-method-list
- Markup: `<ul>` of items, each: brand text + "ending 4242", expiry as `<time>` ("Expires 08/2026"), a `badge` "Default" when applicable, and a button group: "Make default", "Edit", "Remove" (each with the item in its accessible name: "Remove Visa ending 4242"). Removal uses `delete-with-confirmation`.
- `state:default`: one default, its "Make default" action absent. `state:expired`: `badge` "Expired" with icon and text, "Update card" as the primary action; if it is the only method, a `billing-alert`.
- `state:empty`: "No payment method" with explanation of consequence and an "Add payment method" button; no illustration needed.
- `variant:add`: trailing "Add payment method" button that opens `add-payment-method` (dialog or inline).
- Removing the default or the only method warns what happens to renewals. Brand logos have empty `alt` when brand text is present. Failure: a failed make-default reverts and announces the error via the status region.

### add-payment-method
- Markup: a `<form>` with a type choice as native radios or tabs (`tablist` only if panels are all in the page), then one `<fieldset>` per type. Submit "Save card" / "Authorize and save bank account" / "Save wallet" (labels name the action).
- `variant:card`: composes `payment-card-entry` (all field, autofill and error rules inherited); adds "Set as default" checkbox (unchecked unless it is the first method) and billing postal code. Hosted iframe fields follow the vendor note in section 1.
- `variant:bank-debit-mandate`: account holder, IBAN (SEPA) or routing/account number (ACH) with `inputmode`, validated on blur (IBAN checksum, routing number length), then the mandate text block (see section 1) in a `<section aria-labelledby>`, and an unticked "I authorize ..." checkbox required to submit. Mandate reference appears after saving and by email.
- `variant:wallet`: wallet button from the provider (its own accessible name, e.g. "Pay with Google Pay"), plus text fallback when the wallet is unavailable (`unavailable` explained, not hidden silently).
- Validation: inline on blur, error summary (`error-summary`) on submit, focus moves to it. Async verification (microdeposits, 3-D Secure) uses a polite status and a "we'll email you" fallback.
- RTL: IBAN and card numbers stay LTR (`dir="ltr"` on those inputs). Reduced motion: no card flip animations.
- vs. commerce `payment-method` (checkout selection).

## 3. Invoices & usage

### invoice-list
- Markup: product `data-table` (a native `<table>`, `<caption>` "Invoices", `scope="col"` headers): number (link to invoice-detail), date (`<time>`), amount (`<data>`, end-aligned, tabular-nums), status `badge`, download link ("Download invoice INV-1042 (PDF)"). Mobile: rows become stacked cards with the same text labels.
- `state:paid`: "Paid" + paid date. `state:open`: "Open — due Nov 3" with "Pay now" action. `state:overdue`: "Overdue — 12 days" plus Pay now; no color-only emphasis. `state:void`: "Void" with amount struck through and the text "Void" (do not hide from history).
- `state:empty`: "No invoices yet. Your first invoice appears after your first billing date (Nov 3)."
- Sorting by date default (newest first) with `aria-sort` if sortable; pagination or "Load more" announced ("Showing 12 of 48"). Download shows a status while preparing and announces failure.
- RTL: table mirrors; numbers stay as formatted by locale.

### invoice-detail
- Markup: `<article>` with `<h2>` "Invoice INV-1042", issuer and customer blocks as `<address>`, a `<dl>` for invoice date, due date, PO number and payment terms, then line items as a `<table>` with `<caption>`, subtotal/tax/total as `<tfoot>` rows (total in `<th scope="row">`).
- `variant:line-items-tax`: description, quantity, unit price, amount, tax rate per line; tax breakdown by rate/jurisdiction, tax ID of issuer and (where required) customer; currency stated; reverse-charge note for EU B2B where applicable.
- `state:pay-now`: "Pay $49.00" button (amount in label) with the saved method named ("Visa ending 4242") and an option to change it; result announced via status; a failed attempt shows `billing-alert` `variant:payment-failed`.
- Actions: Download PDF, Print (`window.print()` button plus print stylesheet, section 1), Send copy. Credits and discounts as signed lines with text ("Credit — Referral").
- Mobile: line-items table becomes a definition list per item. Print: hidden actions, light theme.

### billing-usage
- Markup: product `meter` (native `<meter min max value low high optimum>` with a visible label and `aria-valuetext` equivalent text) plus text "8,400 of 10,000 API calls used". Optional breakdown table. Reset date as `<time>`.
- `state:under`: neutral; remaining amount in text. `state:near-limit`: at the threshold (e.g. 80%) shows an icon + "Approaching your limit" and the overage price or upgrade path. `state:over`: "1,200 over — $12.00 overage so far" with the rate, the cap if any, and "Upgrade" or "Set spending limit".
- State is never carried by bar color alone; the numbers and the status sentence repeat it. Polite announcement only when crossing a threshold (once), not on every update.
- Reduced motion: no animated fill. Failure: if usage lags say "Usage updates every hour; last updated 10:42".
- vs. ai `usage-meter` (token and context usage).

### billing-alert
- Markup: product `alert` composition: icon, message, one action link/button, optional dismiss only for non-critical ones. Role: `role="alert"` only when the failure appears dynamically right now; a persistent banner on page load uses `role="status"` or no live role (avoid announcing on every navigation).
- `variant:payment-failed`: "Payment of $49.00 failed — your bank declined it. We'll retry on Nov 3. Update payment method." `variant:card-expiring`: "Visa ending 4242 expires Nov 30. Update card." `variant:trial-ending`: "Your trial ends in 3 days. You'll be charged $49.00 on Nov 3. Add payment method or cancel."
- Each states cause, date or amount, and one action; wording is factual and calm, no urgency theatre. Critical (payment-failed) is not dismissible until resolved; others can be dismissed and stay dismissed until state changes.
- Placement: top of the billing page and, if configured, a compact form in the app shell; focus is not moved on page load. RTL: logical layout.

## 4. Lifecycle

### cancel-flow
- Markup: native `<dialog>` (via `modal`) or a page with a `<form>`; each step has an `<h2>`, a "Step n of 3" text (not color), and focus moves to the heading on step change. Maximum steps: no more than sign-up took; if sign-up was two steps, cancelling is two. The "Cancel plan" entry is visible on the billing page and on `current-plan`.
- `state:reason`: optional reason as native radios ("Too expensive", "Missing a feature", "Not using it", "Other" with textarea); "Skip" is a real button of equal weight; a reason is never required.
- `state:offer`: one retention offer at most (discount, pause, downgrade), described with exact price and duration; two buttons of comparable weight: "Accept offer" and "Continue to cancel" (skippable in one action). No guilt copy, no pre-selected offer, no offer that restarts a cancelled state after the user chose cancel. Offers are dropped entirely if the user already tried one.
- `state:confirm`: restates consequences factually: access ends Nov 3, 2026, what data is kept and for how long, how to export it, what will be charged (nothing more), "Confirm cancellation" (primary) and "Keep my plan" (secondary, plain label). Not a `delete-with-confirmation` typed phrase: no extra friction beyond a single confirm.
- `state:done`: "Your plan is cancelled. You have access until Nov 3, 2026." with confirmation email note, "Resume plan" link, export link; announced via status; focus on heading. If the cancel request fails, say so and give a direct alternative (support link) without dropping the user's input.
- Honest-by-design: the click-to-cancel principle (section 1) is the acceptance test: same channel as sign-up, no mandatory call/chat if sign-up was online, no required login loops. Keyboard: Esc closes the dialog without cancelling. Reduced motion: no animated step transitions.

## 5. Money movement

### transaction-list
- Markup: product `data-table` with `<caption>`, columns date, description, method, status `badge`, amount with sign. Credits/refunds read as "Refund" status plus `−$12.00`; charges plain.
- `variant:filters`: a labelled filter row (date range, status, type) with applied chips and a result count announced politely ("42 transactions"). Filters are native controls; apply on submit or after debounce, never on focus.
- `variant:export`: "Export CSV" button with format choice; preparing state shows progress text; completion announced with a download link; export honors the current filters and says so.
- `state:pending`: status "Pending" with expected settle date; amount shown but excluded from totals with note. `state:refunded`: original row stays, a linked "Refund" row appears (and the original gets a "Refunded" badge, partial amounts as text "Partially refunded $5.00 of $12.00").
- Amounts end-aligned, tabular-nums, correct currency per row. Mobile: stacked cards. RTL: table mirrors, amounts via `<bdi>`.

### payout-summary
- Markup: labelled `<section>` with `<dl>`: available balance, pending balance, next payout amount and date, bank account (last digits). Money as `<data>`.
- `variant:balance`: available, pending (with when it becomes available) and a "Withdraw" action when applicable.
- `variant:schedule`: schedule text ("Daily, 2 business days after charge" / "Every Friday, minimum $50") with a "Change schedule" form using native radios and a minimum-balance field.
- `state:on-hold`: `badge` "On hold" with icon, the reason ("Verification needed"), the amount affected and the exact action ("Upload ID") and who to contact; never an unexplained hold.
- Failure: a failed payout says which bank, why, and the retry date. Reduced motion: none required. Polite status when schedule saves.

### wallet-balance
- Markup: labelled `<section>` with balance as `<data>` (credits may be a non-currency unit: "1,250 credits", formatted with `Intl.NumberFormat` `unit` or plain decimal and the unit word), expiry of credits as text with `<time>`, and a "Top up" button.
- `variant:credits`: breakdown (free, purchased, promotional) with expiry per bucket; consumption order stated.
- `state:top-up`: form with preset amounts as native radios plus custom amount (`inputmode="decimal"`, min/max stated), the payment method named, total shown, button "Add $50.00" (amount in label); result announced "Added $50.00. New balance $62.00". Auto top-up is an unchecked opt-in with threshold shown.
- Signed transactions are text plus sign (see section 1). Failure keeps the balance unchanged and says so. Low balance uses `billing-alert`.

### refund-dialog
- Markup: product `modal` (native `<dialog>` with `aria-labelledby`; a plain dialog, not `alertdialog`, because it contains a form). Title "Refund payment of $49.00"; focus starts on the amount field (partial) or the reason control (full), never on the confirm button.
- `variant:full`: a read-only amount "$49.00", reason (required select or radios), optional note, text consequences ("The customer receives it in 5–10 business days; fees are not returned"), confirm "Refund $49.00".
- `variant:partial`: amount field `inputmode="decimal"` with the maximum refundable stated ("up to $49.00; $5.00 already refunded"), validation on blur and submit, confirm label updates to the entered amount ("Refund $20.00").
- Irreversible action: the confirmation states it cannot be undone; the result is announced via status ("Refunded $20.00") and the originating row updates in transaction-list. Esc closes without action. Failure: the dialog stays open with the error mirrored in an error summary.

## 6. Tax

### tax-info-form
- Markup: `<form>` with `<fieldset>` for business identity: legal name, country (`autocomplete="country"`), address fields (see commerce `address-form` rules by reference), tax ID type and number, "I'm buying as an individual" opt-out. Labels visible; format hint shown before typing ("DE + 9 digits").
- `variant:vat-id`: country-aware VAT field with prefix and format validation on blur, optional VIES lookup shown as a "Verify" button; reverse-charge impact explained ("No VAT will be charged on future invoices").
- `state:invalid`: `:user-invalid` plus message "This VAT number format isn't valid for Germany. Check for a typo, or leave it empty." with `aria-describedby`; error summary on submit.
- `state:verified`: icon + text "Verified — registered name: Example GmbH" beside the field (status announced politely once), with the check date. If the registry is unreachable, say it will be re-checked and allow saving.
- Changes apply to future invoices only unless re-issue is offered (state it). Privacy: not shown in full in logs. RTL: ID fields `dir="ltr"`.

## 7. Pages (patterns/)

Realistic data (several currencies, a past-due case, a trial case), light/dark, mobile/desktop. Pages use the account-shell navigation from the product `side-nav`/`settings` patterns and one `<main>` with one `<h1>`.

### billing-page
- Composition: account shell → `<h1>` Billing → `billing-alert` (only when something needs fixing) → `current-plan` · `payment-method-list` · `billing-usage` → recent `invoice-list` (5 rows, "View all invoices") → tax-info link. The "Cancel plan" entry sits in `current-plan`, visible without searching.
- `variant:overview`: the healthy state; no alert, renewal date and next charge in `current-plan`.
- `state:past-due`: leads with `billing-alert` `variant:payment-failed` (cause, amount due, retry date, "Update payment method"); `current-plan` shows `state:past-due`; the page itself stays fully reachable.
- Mobile: single column in the same order, alert first; invoice rows become cards.

### plans-page
- Composition: account shell → `<h1>` Plans → interval choice → `plan-picker` comparison → feature comparison table → proration preview and confirm. No marketing hero or testimonials; marketing `pricing-table` is not used.
- `variant:in-app`: comparison tied to the signed-in account, with proration and downgrade warnings from `plan-picker`.
- `state:current-highlighted`: the current plan is marked with the text "Current plan" (plus a border), its radio disabled with an explanation; not color-only.
- Mobile: stacked plan cards, current plan first, sticky confirm button stating the plan and amount.

### invoice-page
- Composition: account shell (hidden in print) → breadcrumb back to invoices → `invoice-detail` → actions (Download PDF, Print, Pay now if open).
- `variant:printable`: documents the `@media print` rules: shell and actions hidden, light high-contrast theme, no page breaks inside table rows, repeated table head, expanded URLs where useful, margins via `@page`.
- Mobile: line items become a definition list per item; actions wrap full width.

### transactions-page
- Composition: account shell → `<h1>` Transactions → `transaction-list` with `variant:filters` and `variant:export`, result count announced politely.
- `state:empty`: "No transactions yet", what will appear here and when, and a link back to billing; filters and export are hidden or disabled with explanation.
- Mobile: filters in a collapsible group with applied chips; rows as cards with signed amounts and status text.

### payouts-page
- Composition: account shell → `<h1>` Payouts → `payout-summary` (balance, schedule, on-hold when relevant) → `wallet-balance` (if used) → payout history `data-table` → tax-info link.
- `variant:history`: table with date, amount, destination (last digits), status text, arrival date and statement download; sortable by date, newest first, announced pagination.
- Mobile: summary first, history rows as cards; the on-hold reason and action stay above the fold.
