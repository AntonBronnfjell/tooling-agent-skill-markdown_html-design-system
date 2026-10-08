/**
 * search-input.js — clear button and "/" shortcut for .search.
 *
 * - .search__clear (ships `hidden`) appears while the field has a value; clicking it empties the field,
 *   fires an `input` event and returns focus to the field. Esc in a filled field does the same (native).
 * - [data-shortcut="/"] on .search: pressing "/" outside a text field focuses the search input.
 * - Without JS the native search field still works, including the browser's own clear control.
 *
 * export init(root = document) — safe to call twice (data-enhanced).
 */
const typing = (el) => el.closest("input, textarea, select, [contenteditable='true']");

export function init(root = document) {
  root.querySelectorAll(".search:not([data-enhanced])").forEach((search) => {
    const input = search.querySelector(".search__control");
    const clear = search.querySelector(".search__clear");
    if (!input) return;
    search.setAttribute("data-enhanced", "");

    if (clear) {
      const sync = () => { clear.hidden = input.value === ""; };
      input.addEventListener("input", sync);
      clear.addEventListener("click", () => {
        input.value = "";
        input.dispatchEvent(new Event("input", { bubbles: true }));
        input.focus();
      });
      sync();
    }

    const key = search.dataset.shortcut;
    if (key) {
      document.addEventListener("keydown", (e) => {
        if (e.key !== key || e.metaKey || e.ctrlKey || e.altKey || typing(e.target)) return;
        e.preventDefault();
        input.focus();
      });
    }
  });
}
