/**
 * menu.js — APG Menu Button behavior on top of the native popover + invoker commands.
 *
 * Markup:
 *   <button type="button" class="btn" aria-haspopup="menu" aria-expanded="false" aria-controls="wo-actions"
 *           commandfor="wo-actions" command="toggle-popover" style="anchor-name:--wo-actions">Actions</button>
 *   <div class="menu" id="wo-actions" popover role="menu" aria-label="Work order actions" style="position-anchor:--wo-actions">
 *     <button type="button" class="menu__item" role="menuitem">…</button>
 *     <!-- submenu: trigger is a menuitem; the sub-popover is a child of this menu so the popover stack nests -->
 *     <button type="button" class="menu__item" role="menuitem" aria-haspopup="menu" aria-expanded="false"
 *             aria-controls="wo-move" commandfor="wo-move" command="toggle-popover">Move to depot</button>
 *     <div class="menu menu--sub" id="wo-move" popover role="menu" aria-label="Move to depot">…</div>
 *   </div>
 *
 * The platform already does: open/close on click, Esc and light dismiss, top layer, focus return for invokers.
 * This module adds: aria-expanded sync, focus to first item on open (last with ↑), roving focus with
 * ↑/↓/Home/End + typeahead (js/lib/roving-focus.js), →/← for submenus (RTL-aware), Tab closes the whole menu,
 * menuitemcheckbox / menuitemradio toggling, aria-disabled items ignored, closing after an action.
 * Emits `menu-select` (bubbles) on the menu with detail { item, value: item.dataset.value, checked }.
 * Fallback: without invoker-command support, trigger clicks call togglePopover().
 *
 * export init(root = document) — enhances every [aria-haspopup="menu"][aria-controls]; safe to call twice.
 */
import { rovingFocus } from "./lib/roving-focus.js";

const ITEMS = '[role="menuitem"], [role="menuitemcheckbox"], [role="menuitemradio"]';
const hasInvokers = typeof HTMLButtonElement !== "undefined" && "command" in HTMLButtonElement.prototype;

const isOpen = (el) => { try { return el.matches(":popover-open"); } catch { return false; } };
const isRtl = (el) => getComputedStyle(el).direction === "rtl";
const parentMenu = (menu) => menu.parentElement && menu.parentElement.closest('[role="menu"][popover]');
const rootMenu = (menu) => { let m = menu; while (parentMenu(m)) m = parentMenu(m); return m; };

function enhance(trigger) {
  const menu = document.getElementById(trigger.getAttribute("aria-controls"));
  if (!menu || !menu.hasAttribute("popover")) return;
  trigger.setAttribute("data-enhanced", "");
  const isSub = trigger.getAttribute("role") === "menuitem";

  // Own only this menu's items (not those of a nested submenu) so each level has its own roving focus.
  for (const item of menu.querySelectorAll(ITEMS)) {
    if (item.closest('[role="menu"]') === menu) item.dataset.menuOwner = menu.id;
  }
  const rf = rovingFocus(menu, {
    items: `[data-menu-owner="${CSS.escape(menu.id)}"]`,
    orientation: "vertical",
    typeahead: true,
  });

  let focusLast = false;
  let returnFocus = false;

  const open = (last = false) => {
    focusLast = last;
    if (isOpen(menu)) { const list = rf.items(); rf.focus(last ? list.length - 1 : 0); return; }
    try { menu.showPopover({ source: trigger }); } catch { menu.showPopover(); }
  };

  if (!hasInvokers) trigger.addEventListener("click", () => menu.togglePopover());

  menu.addEventListener("beforetoggle", (e) => {
    if (e.newState === "closed") returnFocus = menu.contains(document.activeElement) && !("skipReturn" in menu.dataset);
  });
  menu.addEventListener("toggle", (e) => {
    const opened = e.newState === "open";
    trigger.setAttribute("aria-expanded", String(opened));
    if (opened) {
      const list = rf.items();
      rf.focus(focusLast ? list.length - 1 : 0);
      focusLast = false;
    } else {
      if (returnFocus) trigger.focus();
      returnFocus = false;
      delete menu.dataset.skipReturn;
    }
  });

  trigger.addEventListener("keydown", (e) => {
    const forward = isRtl(trigger) ? "ArrowLeft" : "ArrowRight";
    if (!isSub && (e.key === "ArrowDown" || e.key === "ArrowUp")) {
      e.preventDefault();
      open(e.key === "ArrowUp");
    } else if (isSub && e.key === forward) {
      e.preventDefault();
      e.stopPropagation();
      open(false);
    }
  });

  menu.addEventListener("keydown", (e) => {
    if (e.target.closest('[role="menu"]') !== menu) return; // event bubbled from a submenu
    const back = isRtl(menu) ? "ArrowRight" : "ArrowLeft";
    if (e.key === "Tab") {
      // Tab closes every level and lets focus move on naturally (no return to the trigger).
      for (let m = menu; m; m = parentMenu(m)) m.dataset.skipReturn = "";
      rootMenu(menu).hidePopover();
    } else if (isSub && e.key === back) {
      e.preventDefault();
      e.stopPropagation();
      menu.hidePopover();
    }
  });

  menu.addEventListener("click", (e) => {
    const item = e.target.closest(ITEMS);
    if (!item || item.dataset.menuOwner !== menu.id) return;
    if (item.getAttribute("aria-disabled") === "true") {
      e.preventDefault();
      e.stopImmediatePropagation();
      return;
    }
    if (item.hasAttribute("aria-haspopup")) return; // submenu trigger: the invoker opens it
    const role = item.getAttribute("role");
    if (role === "menuitemcheckbox") {
      item.setAttribute("aria-checked", String(item.getAttribute("aria-checked") !== "true"));
    } else if (role === "menuitemradio") {
      const group = item.closest('[role="group"]') || menu;
      for (const r of group.querySelectorAll('[role="menuitemradio"]')) r.setAttribute("aria-checked", String(r === item));
    }
    item.dispatchEvent(new CustomEvent("menu-select", {
      bubbles: true,
      detail: { item, value: item.dataset.value, checked: item.getAttribute("aria-checked") === "true" },
    }));
    // Actions close the menu; checkable items keep it open so several options can be set.
    if (role === "menuitem") rootMenu(menu).hidePopover();
  });
}

export function init(root = document) {
  root.querySelectorAll('[aria-haspopup="menu"][aria-controls]:not([data-enhanced])').forEach(enhance);
}
