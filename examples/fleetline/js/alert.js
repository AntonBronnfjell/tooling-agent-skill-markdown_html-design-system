/**
 * alert.js — dismiss button for inline alerts (the only part of .alert that needs JS).
 *
 * <div class="alert alert--warning" id="overdue-kx24"> … <button type="button" class="btn btn--ghost btn--sm alert__dismiss"
 *      aria-label="Dismiss: Vehicle KX-24 is overdue for service" data-alert-return="fleet-h">…</button></div>
 *
 * - Hides the alert (hidden attribute) and moves focus somewhere sensible, so it isn't lost on <body>:
 *   the element named by data-alert-return, else the next focusable element after the alert.
 * - Dispatches a bubbling "alert:dismiss" event on the alert so apps can persist the choice.
 * - Without JS the button does nothing harmful; prefer server-rendered dismissal for critical notices.
 *
 * export init(root = document) — enhances every .alert__dismiss inside root; safe to call twice.
 */
const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), select, textarea, [tabindex]:not([tabindex="-1"])';

function nextFocusable(el) {
  const all = [...document.querySelectorAll(FOCUSABLE)];
  return all.find((n) => !el.contains(n) && (el.compareDocumentPosition(n) & Node.DOCUMENT_POSITION_FOLLOWING));
}

export function init(root = document) {
  root.querySelectorAll(".alert__dismiss:not([data-enhanced])").forEach((btn) => {
    btn.setAttribute("data-enhanced", "");
    btn.addEventListener("click", () => {
      const alert = btn.closest(".alert");
      if (!alert) return;
      const target = document.getElementById(btn.dataset.alertReturn || "") || nextFocusable(alert);
      alert.hidden = true;
      alert.dispatchEvent(new CustomEvent("alert:dismiss", { bubbles: true }));
      if (target) {
        if (!target.matches(FOCUSABLE) && !target.hasAttribute("tabindex")) target.setAttribute("tabindex", "-1");
        target.focus();
      }
    });
  });
}
