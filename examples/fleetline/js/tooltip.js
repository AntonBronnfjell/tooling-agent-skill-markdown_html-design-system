/**
 * tooltip.js — hover + focus tooltips on [popover="hint"] (falls back to "manual" where hint is unsupported).
 *
 * <button type="button" class="btn" aria-describedby="tt-odo" data-tooltip-trigger="tt-odo">Odometer</button>
 * <div id="tt-odo" class="tooltip" popover="hint" role="tooltip">Synced from telematics 4 minutes ago</div>
 *
 * - Shows 400ms after pointer enter or keyboard focus; hides on pointer leave (120ms grace so the pointer can
 *   move onto the tooltip — WCAG 1.4.13 hoverable), on blur, and on Esc without moving focus (dismissable).
 * - Anchors the tooltip to its trigger with a per-instance anchor-name; CSS does the placement and flipping.
 * - Esc goes through js/lib/dismiss.js so, inside a dialog, Esc closes the tooltip first, not the dialog.
 * - Without JS the text is still exposed through aria-describedby; it just never appears visually.
 *
 * export init(root = document) — enhances every [data-tooltip-trigger] inside root; safe to call twice.
 */
import { onDismiss } from "./lib/dismiss.js";

const SHOW_DELAY = 400;
const HIDE_DELAY = 120;
let count = 0;

export function init(root = document) {
  root.querySelectorAll("[data-tooltip-trigger]:not([data-enhanced])").forEach((trigger) => {
    const tip = document.getElementById(trigger.dataset.tooltipTrigger);
    if (!tip || typeof tip.showPopover !== "function") return;
    trigger.setAttribute("data-enhanced", "");

    const name = `--tooltip-${(count += 1)}`;
    trigger.style.setProperty("anchor-name", name);
    tip.style.setProperty("position-anchor", name);

    let timer = null;
    let release = null;

    const isOpen = () => tip.matches(":popover-open");
    const close = () => {
      clearTimeout(timer);
      if (release) { release(); release = null; }
      if (isOpen()) tip.hidePopover();
    };
    const open = () => {
      if (isOpen()) return;
      tip.showPopover();
      release = onDismiss(tip, {
        trigger,
        outside: false,
        returnFocus: false,
        onDismiss: () => { release = null; close(); },
      });
    };
    const showSoon = () => { clearTimeout(timer); timer = setTimeout(open, SHOW_DELAY); };
    const hideSoon = () => { clearTimeout(timer); timer = setTimeout(close, HIDE_DELAY); };

    trigger.addEventListener("pointerenter", showSoon);
    trigger.addEventListener("pointerleave", hideSoon);
    trigger.addEventListener("focus", showSoon);
    trigger.addEventListener("blur", close);
    tip.addEventListener("pointerenter", () => clearTimeout(timer));
    tip.addEventListener("pointerleave", hideSoon);
  });
}
