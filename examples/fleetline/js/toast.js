/**
 * toast.js — transient global notices with one polite live region.
 *
 * import { toast, init } from "../js/toast.js";
 * toast({ tone: "success", title: "Work order WO-1042 closed", message: "Invoice sent to Northside Depot." });
 * toast({ tone: "info", title: "Work order deleted", action: { label: "Undo", onAction: () => restore() } });
 *
 * - One host per page: <section class="toast-region" popover="manual" aria-label="Notifications"> with an
 *   <ol class="toast-region__list"> and a visually hidden role="status" (polite) node. The host lives in the
 *   top layer (above dialogs); without popover support it is position: fixed with --z-toast.
 * - Announcements: title + message are copied into the status node, so the screen reader hears the text
 *   once (not the button names). Danger toasts are still polite: anything urgent belongs in an alert.
 * - Timing: 6s, 10s with an action (WCAG 2.2.1). The timer of every toast pauses while the pointer is over
 *   the region or focus is inside it, and restarts with the remaining time when it leaves.
 * - Max 3 visible: the oldest is dismissed when a 4th arrives. Each toast has a close button.
 * - Closing a toast that holds focus returns focus to where it was before entering the region.
 *
 * export init(root = document) — wires [data-toast] buttons inside root (docs demos):
 *   <button type="button" data-toast data-toast-tone="success" data-toast-title="…" data-toast-message="…"
 *           data-toast-action="Undo">…</button>
 * Safe to call twice (data-enhanced). No side effects on import.
 */
const DURATION = 6000;
const DURATION_WITH_ACTION = 10000;
const MAX_VISIBLE = 3;

const ICONS = {
  info: '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
  success: '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
  warning: '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
  danger: '<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/>',
};
const CLOSE = '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>';
const svg = (paths, cls) =>
  `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">${paths}</svg>`;

export const prefersReducedMotion = () =>
  matchMedia("(prefers-reduced-motion: reduce)").matches || document.documentElement.hasAttribute("data-reduced-motion");

let host = null;

function region() {
  if (host && host.el.isConnected) return host;
  const el = document.createElement("section");
  el.className = "toast-region";
  el.setAttribute("aria-label", "Notifications");
  const list = document.createElement("ol");
  list.className = "toast-region__list";
  const status = document.createElement("div");
  status.className = "sr-only";
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  el.append(list, status);
  if ("popover" in HTMLElement.prototype) el.popover = "manual";
  document.body.append(el);
  if (el.popover) el.showPopover();

  host = { el, list, status, paused: false, returnTo: null, toasts: new Set() };
  const pause = () => { host.paused = true; host.toasts.forEach((t) => t.pause()); };
  const resume = () => { host.paused = false; host.toasts.forEach((t) => t.resume()); };
  el.addEventListener("pointerenter", pause);
  el.addEventListener("pointerleave", () => { if (!el.contains(document.activeElement)) resume(); });
  el.addEventListener("focusin", (e) => {
    if (e.relatedTarget && !el.contains(e.relatedTarget)) host.returnTo = e.relatedTarget;
    pause();
  });
  el.addEventListener("focusout", (e) => { if (!el.contains(e.relatedTarget) && !el.matches(":hover")) resume(); });
  return host;
}

function announce(h, text) {
  h.status.textContent = "";
  requestAnimationFrame(() => { h.status.textContent = text; });
}

export function toast({ tone = "info", title, message = "", action = null, duration } = {}) {
  const h = region();
  const li = document.createElement("li");
  li.className = `toast toast--${tone}`;
  li.innerHTML =
    `${svg(ICONS[tone] || ICONS.info, "toast__icon")}<div class="toast__content"><p class="toast__title"></p>` +
    `${message ? '<p class="toast__message"></p>' : ""}</div>`;
  li.querySelector(".toast__title").textContent = title;
  if (message) li.querySelector(".toast__message").textContent = message;

  if (action) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn btn--secondary btn--sm toast__action";
    btn.textContent = action.label;
    btn.addEventListener("click", () => { action.onAction?.(); dismiss(); });
    li.append(btn);
  }
  const close = document.createElement("button");
  close.type = "button";
  close.className = "btn btn--ghost btn--sm toast__close";
  close.setAttribute("aria-label", "Dismiss notification");
  close.innerHTML = svg(CLOSE, "btn__icon");
  close.addEventListener("click", () => dismiss());
  li.append(close);

  let remaining = duration ?? (action ? DURATION_WITH_ACTION : DURATION);
  let started = 0;
  let timer = null;
  const entry = {
    pause() { if (timer) { clearTimeout(timer); timer = null; remaining -= Date.now() - started; } },
    resume() { if (!timer && remaining > 0) { started = Date.now(); timer = setTimeout(dismiss, remaining); } },
  };

  function dismiss() {
    if (!h.toasts.has(entry)) return;
    h.toasts.delete(entry);
    clearTimeout(timer);
    const hadFocus = li.contains(document.activeElement);
    let removed = false;
    const remove = () => {
      if (removed) return;
      removed = true;
      li.remove();
      if (hadFocus) {
        const next = h.list.querySelector(".toast__close");
        (next || (h.returnTo?.isConnected ? h.returnTo : null))?.focus();
        if (!next) h.returnTo = null;
      }
    };
    if (prefersReducedMotion()) return remove();
    li.dataset.state = "closing";
    li.addEventListener("transitionend", remove, { once: true });
    setTimeout(remove, 400); // safety net if transitionend never fires
  }

  entry.dismissNow = dismiss;
  h.list.append(li);
  h.toasts.add(entry);
  while (h.toasts.size > MAX_VISIBLE) {
    const oldest = h.toasts.values().next().value;
    oldest.dismissNow();
  }
  if (!h.paused) entry.resume();
  announce(h, message ? `${title}. ${message}` : title);
  return { dismiss };
}

export function init(root = document) {
  root.querySelectorAll("[data-toast]:not([data-enhanced])").forEach((btn) => {
    btn.setAttribute("data-enhanced", "");
    btn.addEventListener("click", () => {
      const d = btn.dataset;
      toast({
        tone: d.toastTone,
        title: d.toastTitle,
        message: d.toastMessage,
        action: d.toastAction ? { label: d.toastAction, onAction: () => toast({ tone: "info", title: d.toastActionDone || "Change undone" }) } : null,
      });
    });
  });
}
