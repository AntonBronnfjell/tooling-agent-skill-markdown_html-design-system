/**
 * side-nav.js — collapse / expand the sidebar to an icon rail and remember the choice.
 *
 * Markup: <nav class="side-nav" aria-label="Workshop" data-persist="fleetline-side-nav">
 *           <div class="side-nav__header">
 *             <button type="button" class="icon-btn side-nav__collapse" aria-expanded="true" aria-label="Collapse navigation">…</button>
 * - aria-expanded on the button is the state; the nav gets [data-collapsed] for styling.
 * - The accessible name switches between "Collapse navigation" and "Expand navigation".
 * - When collapsed, each link gets a title with its label (pointer tooltip); names come from the clipped labels.
 * - data-persist="<key>" stores the state in localStorage (try/catch: private mode keeps it in memory).
 *
 * export init(root = document) — safe to call twice.
 */
const read = (k) => { try { return localStorage.getItem(k); } catch { return null; } };
const write = (k, v) => { try { localStorage.setItem(k, v); } catch { /* private mode */ } };

export function init(root = document) {
  root.querySelectorAll(".side-nav__collapse:not([data-enhanced])").forEach((btn) => {
    const nav = btn.closest(".side-nav");
    if (!nav) return;
    btn.setAttribute("data-enhanced", "");
    const key = nav.dataset.persist;
    const apply = (expanded) => {
      btn.setAttribute("aria-expanded", String(expanded));
      btn.setAttribute("aria-label", expanded ? "Collapse navigation" : "Expand navigation");
      nav.toggleAttribute("data-collapsed", !expanded);
      for (const link of nav.querySelectorAll(".side-nav__link")) {
        const label = link.querySelector(".side-nav__label");
        if (!label) continue;
        if (expanded) link.removeAttribute("title");
        else link.title = label.textContent.trim();
      }
    };
    const saved = key ? read(key) : null;
    apply(saved ? saved === "expanded" : btn.getAttribute("aria-expanded") !== "false");
    btn.addEventListener("click", () => {
      const expanded = btn.getAttribute("aria-expanded") !== "true";
      apply(expanded);
      if (key) write(key, expanded ? "expanded" : "collapsed");
    });
  });
}
