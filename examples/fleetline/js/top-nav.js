/**
 * top-nav.js — mobile "Menu" disclosure for .top-nav.
 *
 * Markup: <button type="button" class="btn btn--ghost top-nav__toggle" aria-controls="main-nav-panel">…Menu</button>
 *         <div class="top-nav__panel" id="main-nav-panel">…</div>
 * - Without JS the toggle has no aria-expanded → CSS hides it and the panel stays visible.
 * - init sets aria-expanded="false" (collapsed below the narrow breakpoint), click toggles it,
 *   Esc closes and returns focus to the toggle (js/lib/dismiss.js). Outside clicks don't close it (it's in-flow).
 *
 * export init(root = document) — safe to call twice.
 */
import { onDismiss } from "./lib/dismiss.js";

export function init(root = document) {
  root.querySelectorAll(".top-nav__toggle[aria-controls]:not([data-enhanced])").forEach((btn) => {
    const panel = document.getElementById(btn.getAttribute("aria-controls"));
    if (!panel) return;
    btn.setAttribute("data-enhanced", "");
    let release = null;
    const set = (open) => {
      btn.setAttribute("aria-expanded", String(open));
      if (open && !release) {
        release = onDismiss(panel, { trigger: btn, outside: false, onDismiss: () => { release = null; set(false); } });
      } else if (!open && release) {
        release();
        release = null;
      }
    };
    set(btn.getAttribute("aria-expanded") === "true");
    btn.addEventListener("click", () => set(btn.getAttribute("aria-expanded") !== "true"));
  });
}
