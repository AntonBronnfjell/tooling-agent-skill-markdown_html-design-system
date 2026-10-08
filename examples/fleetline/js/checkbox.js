/**
 * checkbox.js — indeterminate state and "select all" for .checkbox.
 *
 * - [data-indeterminate] on a .checkbox__input sets .indeterminate = true (a JS-only DOM state).
 * - [data-select-all] on a .checkbox__input with aria-controls="id1 id2 …" controls those checkboxes:
 *   all checked → checked, none → unchecked, some → indeterminate; toggling it sets every child.
 * - Without JS, every checkbox still works on its own.
 *
 * export init(root = document) — safe to call twice (data-enhanced).
 */
export function init(root = document) {
  root.querySelectorAll(".checkbox__input[data-indeterminate]:not([data-enhanced])").forEach((box) => {
    box.setAttribute("data-enhanced", "");
    box.indeterminate = true;
  });

  root.querySelectorAll(".checkbox__input[data-select-all]:not([data-enhanced])").forEach((all) => {
    const ids = (all.getAttribute("aria-controls") || "").split(/\s+/).filter(Boolean);
    const kids = ids.map((id) => document.getElementById(id)).filter(Boolean);
    if (!kids.length) return;
    all.setAttribute("data-enhanced", "");

    const sync = () => {
      const on = kids.filter((k) => k.checked).length;
      all.checked = on === kids.length;
      all.indeterminate = on > 0 && on < kids.length;
    };
    all.addEventListener("change", () => {
      kids.forEach((k) => { if (!k.disabled) k.checked = all.checked; });
      sync();
    });
    kids.forEach((k) => k.addEventListener("change", sync));
    sync();
  });
}
