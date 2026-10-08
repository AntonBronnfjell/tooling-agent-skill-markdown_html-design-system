/**
 * dismiss.js — close a transient surface (menu, popover fallback, listbox, date picker) the same way
 * everywhere: Esc, pointer down outside, optionally focus leaving it; then return focus to the trigger.
 *
 * import { onDismiss } from "../js/lib/dismiss.js";
 * const release = onDismiss(menuEl, {
 *   trigger: buttonEl,          // treated as "inside" for outside-click; receives focus back
 *   onDismiss: (reason) => {},  // reason: "escape" | "outside" | "focusout"; YOU hide the surface here
 *   escape: true,               // Esc closes (only the top-most open surface reacts)
 *   outside: true,              // pointerdown outside surface + trigger closes
 *   focusOut: false,            // focus moving outside closes (APG menu: Tab closes the menu)
 *   returnFocus: true,          // after "escape", or when focus was inside the surface, focus the trigger
 * });
 * release();                    // call when the surface closes for any other reason
 *
 * Notes
 * - Native [popover] and <dialog> already light-dismiss and handle Esc — use this only for surfaces the
 *   platform doesn't manage (JS-positioned fallbacks, comboboxes, custom menus).
 * - A stack keeps nested surfaces sane: Esc closes the innermost surface only, then stops propagation.
 * - An outside pointerdown does not steal focus back to the trigger (the user is focusing something else).
 * - No side effects on import; listeners exist only while a surface is registered.
 */
const stack = [];

function topMost() { return stack[stack.length - 1]; }

function handleKeydown(event) {
  if (event.key !== "Escape" || event.defaultPrevented) return;
  const entry = topMost();
  if (!entry || !entry.escape) return;
  event.preventDefault();
  event.stopPropagation();
  entry.close("escape");
}

function handlePointerdown(event) {
  // Walk from the top so a click inside a nested surface doesn't close its parent.
  for (let i = stack.length - 1; i >= 0; i -= 1) {
    const entry = stack[i];
    if (entry.contains(event.target)) return;
    if (entry.outside) entry.close("outside");
  }
}

function sync() {
  const active = stack.length > 0;
  if (active && !sync.on) {
    document.addEventListener("keydown", handleKeydown, true);
    document.addEventListener("pointerdown", handlePointerdown, true);
  } else if (!active && sync.on) {
    document.removeEventListener("keydown", handleKeydown, true);
    document.removeEventListener("pointerdown", handlePointerdown, true);
  }
  sync.on = active;
}
sync.on = false;

export function onDismiss(surface, options = {}) {
  const {
    trigger = null,
    onDismiss: callback = () => {},
    escape = true,
    outside = true,
    focusOut = false,
    returnFocus = true,
  } = options;

  const entry = {
    surface,
    escape,
    outside,
    contains: (node) => surface.contains(node) || (trigger !== null && trigger.contains(node)),
    close(reason) {
      const focusWasInside = surface.contains(document.activeElement);
      release();
      callback(reason);
      if (returnFocus && trigger && (reason === "escape" || (reason !== "outside" && focusWasInside))) {
        trigger.focus();
      }
    },
  };

  const handleFocusout = (event) => {
    const next = event.relatedTarget;
    if (next && entry.contains(next)) return;
    if (next === null && !document.hasFocus()) return; // window blur: keep open
    entry.close("focusout");
  };

  function release() {
    const i = stack.indexOf(entry);
    if (i !== -1) stack.splice(i, 1);
    if (focusOut) surface.removeEventListener("focusout", handleFocusout);
    sync();
  }

  stack.push(entry);
  if (focusOut) surface.addEventListener("focusout", handleFocusout);
  sync();
  return release;
}

/** Number of registered surfaces — for tests. */
export const openSurfaces = () => stack.length;
