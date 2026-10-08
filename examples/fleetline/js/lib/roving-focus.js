/**
 * roving-focus.js — one Tab stop for a composite widget; arrow keys move focus inside it.
 * WAI-ARIA APG "roving tabindex" (toolbar, tabs, menu, listbox, radio-like groups).
 *
 * import { rovingFocus } from "../js/lib/roving-focus.js";
 * const rf = rovingFocus(tablist, {
 *   items: '[role="tab"]',          // selector, relative to the container (required)
 *   orientation: "horizontal",      // "horizontal" (←/→) | "vertical" (↑/↓) | "both"
 *   loop: true,                     // wrap at the ends
 *   homeEnd: true,                  // Home / End jump to first / last
 *   typeahead: false,               // printable keys jump to the next item starting with that text
 *   onMove: (item, prevItem) => {}, // e.g. tabs with automatic activation select `item` here
 * });
 * rf.focus(index | element)  rf.setActive(element) (no focus move)  rf.items()  rf.destroy()
 *
 * Behaviour
 * - Exactly one item has tabindex="0" (the active one); the rest get tabindex="-1".
 *   Initial active item: [aria-selected="true"] → [aria-checked="true"] → [aria-current] → [tabindex="0"] → first.
 * - Items that are `hidden` or natively `disabled` are skipped. aria-disabled="true" items stay
 *   reachable (APG: menus and tabs keep disabled items focusable so they can be discovered).
 * - Horizontal arrows follow the writing direction: in RTL, ArrowLeft moves forward.
 * - Items are re-queried on every key press, so adding/removing items needs no re-init.
 * - No side effects on import. Safe to call twice on the same container (the second call returns the first instance).
 */
const instances = new WeakMap();

const isSkippable = (el) => el.hidden || el.disabled === true || el.closest("[hidden]") !== null;

export function rovingFocus(container, options = {}) {
  if (instances.has(container)) return instances.get(container);
  const {
    items: selector,
    orientation = "horizontal",
    loop = true,
    homeEnd = true,
    typeahead = false,
    onMove,
  } = options;
  if (!selector) throw new Error("rovingFocus: options.items selector is required");

  let buffer = "";
  let bufferTimer;

  const items = () => [...container.querySelectorAll(selector)].filter((el) => !isSkippable(el));

  const setActive = (target) => {
    const list = items();
    if (!list.includes(target)) return;
    for (const el of list) el.tabIndex = el === target ? 0 : -1;
  };

  const focus = (indexOrEl) => {
    const list = items();
    const target = typeof indexOrEl === "number" ? list[indexOrEl] : indexOrEl;
    if (!target) return;
    const prev = list.find((el) => el.tabIndex === 0);
    setActive(target);
    target.focus();
    if (onMove && target !== prev) onMove(target, prev);
  };

  const initial = () => {
    const list = items();
    return (
      list.find((el) => el.getAttribute("aria-selected") === "true") ||
      list.find((el) => el.getAttribute("aria-checked") === "true") ||
      list.find((el) => el.hasAttribute("aria-current")) ||
      list.find((el) => el.getAttribute("tabindex") === "0") ||
      list[0]
    );
  };

  const onKeyDown = (event) => {
    const list = items();
    const current = event.target.closest(selector);
    if (!current || !list.includes(current) || event.altKey || event.ctrlKey || event.metaKey) return;
    const i = list.indexOf(current);
    const rtl = getComputedStyle(container).direction === "rtl";
    const horizontal = orientation !== "vertical";
    const vertical = orientation !== "horizontal";
    const step = (delta) => {
      let next = i + delta;
      if (loop) next = (next + list.length) % list.length;
      else next = Math.max(0, Math.min(list.length - 1, next));
      return next;
    };
    let next = null;
    switch (event.key) {
      case "ArrowRight": if (horizontal) next = step(rtl ? -1 : 1); break;
      case "ArrowLeft": if (horizontal) next = step(rtl ? 1 : -1); break;
      case "ArrowDown": if (vertical) next = step(1); break;
      case "ArrowUp": if (vertical) next = step(-1); break;
      case "Home": if (homeEnd) next = 0; break;
      case "End": if (homeEnd) next = list.length - 1; break;
      default:
        if (typeahead && event.key.length === 1 && event.key.trim()) {
          clearTimeout(bufferTimer);
          buffer += event.key.toLowerCase();
          bufferTimer = setTimeout(() => { buffer = ""; }, 500);
          const ordered = [...list.slice(i + 1), ...list.slice(0, i + 1)];
          const match = ordered.find((el) => el.textContent.trim().toLowerCase().startsWith(buffer));
          if (match) next = list.indexOf(match);
        }
    }
    if (next === null) return;
    event.preventDefault();
    focus(next);
  };

  // Clicking an item makes it the active one, so Tab returns to where the user left off.
  const onFocusIn = (event) => {
    const item = event.target.closest(selector);
    if (item && items().includes(item)) setActive(item);
  };

  const start = initial();
  if (start) setActive(start);
  container.addEventListener("keydown", onKeyDown);
  container.addEventListener("focusin", onFocusIn);

  const api = {
    items,
    focus,
    setActive,
    destroy() {
      container.removeEventListener("keydown", onKeyDown);
      container.removeEventListener("focusin", onFocusIn);
      clearTimeout(bufferTimer);
      instances.delete(container);
    },
  };
  instances.set(container, api);
  return api;
}
