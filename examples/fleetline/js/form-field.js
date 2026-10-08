/**
 * form-field.js — live character counter for .field (the only part of form-field that needs JS).
 *
 * Markup:
 *   <input id="wo-title" class="input" data-counter="wo-title-count" aria-describedby="wo-title-hint wo-title-count">
 *   <p class="field__counter" id="wo-title-count" data-max="80">0 of 80 characters</p>
 *
 * - Visible count updates on every input; the polite announcement is debounced (typing pause) so
 *   screen readers aren't flooded: a separate visually hidden role="status" node receives the text.
 * - Over the limit: data-over="true" + the control gets aria-invalid="true". Typing is never blocked
 *   (no maxlength), so pasted text can be edited down.
 * - Without JS the static counter text still states the limit.
 *
 * export init(root = document) — enhances every [data-counter] inside root; safe to call twice.
 */
const ANNOUNCE_DELAY = 800;

const message = (count, max) => {
  const left = max - count;
  return left >= 0
    ? `${count} of ${max} characters`
    : `${-left} ${-left === 1 ? "character" : "characters"} too many`;
};

export function init(root = document) {
  root.querySelectorAll("[data-counter]:not([data-enhanced])").forEach((control) => {
    const counter = document.getElementById(control.dataset.counter);
    if (!counter) return;
    const max = Number(counter.dataset.max);
    if (!Number.isFinite(max)) return;
    control.setAttribute("data-enhanced", "");

    const live = document.createElement("span");
    live.className = "sr-only";
    live.setAttribute("role", "status");
    counter.after(live);

    let timer;
    const update = () => {
      const count = [...control.value].length;
      const text = message(count, max);
      const over = count > max;
      counter.textContent = text;
      counter.dataset.over = String(over);
      if (over) control.setAttribute("aria-invalid", "true");
      else if (control.dataset.counterInvalid !== "keep") control.removeAttribute("aria-invalid");
      clearTimeout(timer);
      timer = setTimeout(() => { live.textContent = text; }, ANNOUNCE_DELAY);
    };
    control.addEventListener("input", update);
    counter.textContent = message([...control.value].length, max);
    counter.dataset.over = String([...control.value].length > max);
  });
}
