// invokers.js — fallback for invoker commands (commandfor / command) in browsers without native support.
// Created by `ds.py init`. Native support (Baseline 2025) makes this a no-op.
// Usage: <button commandfor="dlg" command="show-modal">, command="close" | "request-close" | "toggle-popover" | "show-popover" | "hide-popover".
export function init(root = document) {
  if ("commandForElement" in HTMLButtonElement.prototype) return;   // native: nothing to do
  if (root.__dsInvokers) return;
  root.__dsInvokers = true;
  root.addEventListener("click", (event) => {
    const button = event.target.closest("button[commandfor][command]");
    if (!button || button.disabled) return;
    const target = document.getElementById(button.getAttribute("commandfor"));
    if (!target) return;
    const command = button.getAttribute("command");
    const actions = {
      "show-modal": () => target.showModal?.(),
      "close": () => target.close?.(button.value),
      "request-close": () => (target.requestClose ? target.requestClose(button.value) : target.close?.(button.value)),
      "toggle-popover": () => target.togglePopover?.(),
      "show-popover": () => target.showPopover?.(),
      "hide-popover": () => target.hidePopover?.(),
    };
    if (actions[command]) {
      event.preventDefault();
      actions[command]();
    }
  });
}
