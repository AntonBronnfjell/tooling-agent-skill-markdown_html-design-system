/**
 * tabs.js — WAI-ARIA APG Tabs.
 *
 * Markup:
 *   <div class="tabs" data-activation="manual">            (omit data-activation for automatic activation)
 *     <div class="tabs__list" role="tablist" aria-label="Van KX-219">
 *       <button type="button" class="tabs__tab" role="tab" id="t1" aria-selected="true" aria-controls="p1">Overview</button>
 *       …
 *     </div>
 *     <div class="tabs__panel" role="tabpanel" id="p1" aria-labelledby="t1" tabindex="0">…</div>
 *   </div>
 *
 * - One Tab stop for the tablist; ←/→ (RTL-aware), Home/End move focus (js/lib/roving-focus.js).
 * - Automatic activation selects on focus (cheap panels); manual waits for Enter/Space/click (expensive panels).
 * - aria-disabled="true" tabs stay focusable but can't be selected.
 * - Progressive enhancement: without JS every panel is visible; init hides the unselected ones.
 * - Emits `tabs-change` (bubbles) on the tablist with detail { tab, panel }.
 *
 * export init(root = document) — enhances every [role="tablist"] inside root; safe to call twice.
 */
import { rovingFocus } from "./lib/roving-focus.js";

export function init(root = document) {
  root.querySelectorAll('[role="tablist"]:not([data-enhanced])').forEach((list) => {
    list.setAttribute("data-enhanced", "");
    const manual = (list.closest("[data-activation]")?.dataset.activation || list.dataset.activation) === "manual";
    const tabs = () => [...list.querySelectorAll('[role="tab"]')];
    const panelOf = (tab) => document.getElementById(tab.getAttribute("aria-controls"));

    let rf;
    const select = (tab, announce = true) => {
      if (!tab || tab.getAttribute("aria-disabled") === "true") return;
      for (const t of tabs()) {
        const on = t === tab;
        t.setAttribute("aria-selected", String(on));
        const panel = panelOf(t);
        if (panel) panel.hidden = !on;
      }
      if (rf) rf.setActive(tab);
      if (announce) list.dispatchEvent(new CustomEvent("tabs-change", { bubbles: true, detail: { tab, panel: panelOf(tab) } }));
    };

    rf = rovingFocus(list, {
      items: '[role="tab"]',
      orientation: list.getAttribute("aria-orientation") === "vertical" ? "vertical" : "horizontal",
      onMove: (tab) => { if (!manual) select(tab); },
    });

    list.addEventListener("click", (e) => {
      const tab = e.target.closest('[role="tab"]');
      if (tab && list.contains(tab)) select(tab);
    });

    const initial = tabs().find((t) => t.getAttribute("aria-selected") === "true")
      || tabs().find((t) => t.getAttribute("aria-disabled") !== "true");
    select(initial, false);
  });
}
