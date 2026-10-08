/**
 * password-input.js — reveal toggle, strength meter and live requirement list for .password.
 *
 * Markup: see css/components/password-input.css. The toggle ships `hidden`; without JS the field is a
 * plain password input. Optional hooks on the <input>:
 *   data-strength="meter-id"  → <meter class="password__meter" id="meter-id" min="0" max="4" low="2" high="3" optimum="4">
 *                               + an element [data-strength-text] inside .password__strength
 *   data-rules="list-id"      → <ul class="password__rules" id="list-id"> li[data-rule="length:12|digit|upper|symbol"]
 * Requirement changes are announced politely after a typing pause; the meter text is always visible.
 *
 * export init(root = document) — safe to call twice (data-enhanced).
 */
const LABELS = ["Very weak", "Weak", "Fair", "Good", "Strong"];
const TESTS = {
  length: (v, n) => [...v].length >= Number(n || 12),
  digit: (v) => /\d/.test(v),
  upper: (v) => /[A-Z]/.test(v) && /[a-z]/.test(v),
  symbol: (v) => /[^A-Za-z0-9]/.test(v),
};

const score = (v) => {
  if (!v) return 0;
  let s = [...v].length >= 12 ? 2 : [...v].length >= 8 ? 1 : 0;
  s += /\d/.test(v) && /[A-Za-z]/.test(v) ? 1 : 0;
  s += /[^A-Za-z0-9]/.test(v) || (/[A-Z]/.test(v) && /[a-z]/.test(v)) ? 1 : 0;
  return Math.min(4, s);
};

export function init(root = document) {
  root.querySelectorAll(".password:not([data-enhanced])").forEach((box) => {
    const input = box.querySelector(".input__control");
    const toggle = box.querySelector(".password__toggle");
    if (!input) return;
    box.setAttribute("data-enhanced", "");

    if (toggle) {
      const label = toggle.querySelector("[data-label]") || toggle;
      toggle.hidden = false;
      toggle.addEventListener("click", () => {
        const show = input.type === "password";
        input.type = show ? "text" : "password";
        toggle.setAttribute("aria-pressed", String(show));
        label.textContent = show ? "Hide" : "Show";
      });
      // Never submit a revealed password as plain text history: hide again on submit.
      input.form?.addEventListener("submit", () => {
        input.type = "password";
        toggle.setAttribute("aria-pressed", "false");
        label.textContent = "Show";
      });
    }

    const meter = input.dataset.strength && document.getElementById(input.dataset.strength);
    const meterText = meter?.closest(".password__strength")?.querySelector("[data-strength-text]");
    const rules = input.dataset.rules && document.getElementById(input.dataset.rules);
    let live;
    if (rules) {
      live = document.createElement("span");
      live.className = "sr-only";
      live.setAttribute("role", "status");
      rules.after(live);
    }
    let timer;
    const update = () => {
      const v = input.value;
      if (meter) {
        const s = score(v);
        meter.value = s;
        if (meterText) meterText.textContent = v ? LABELS[s] : "";
      }
      if (rules) {
        const met = [];
        rules.querySelectorAll("li[data-rule]").forEach((li) => {
          const [name, arg] = li.dataset.rule.split(":");
          const ok = TESTS[name]?.(v, arg) ?? false;
          li.dataset.met = String(ok);
          if (ok) met.push(li.textContent.trim());
        });
        clearTimeout(timer);
        timer = setTimeout(() => {
          const total = rules.querySelectorAll("li[data-rule]").length;
          live.textContent = `${met.length} of ${total} requirements met`;
        }, 800);
      }
    };
    input.addEventListener("input", update);
    update();
  });
}
