/**
 * theme-toggle.js — wires the two theme-toggle forms to js/theme.js.
 * - Cycling button: <button class="btn btn--ghost theme-toggle" data-theme-cycle data-themes="system light dark">
 *   (handled by theme.js init; the [data-theme-label] text "Theme: dark" is the accessible name).
 * - Radio group: <fieldset class="theme-choice" data-theme-choice> with radios name="theme" value="system|light|dark".
 *   Changing a radio calls setTheme(); the checked radio follows theme changes from anywhere (other tab, button).
 * Call initTheme() once per page (in <head> use the no-flash snippet from theme.js).
 *
 * export init(root = document) — safe to call twice.
 */
import { init as initCycle, setTheme, getTheme, onThemeChange } from "./theme.js";

export function init(root = document) {
  const cycles = root.querySelectorAll("[data-theme-cycle]:not([data-enhanced])");
  if (cycles.length) {
    initCycle(root);
    cycles.forEach((b) => b.setAttribute("data-enhanced", ""));
  }
  root.querySelectorAll("[data-theme-choice]:not([data-enhanced])").forEach((group) => {
    group.setAttribute("data-enhanced", "");
    const sync = (theme) => {
      for (const r of group.querySelectorAll('input[type="radio"]')) r.checked = r.value === theme;
    };
    group.addEventListener("change", (e) => {
      if (e.target.matches('input[type="radio"]')) setTheme(e.target.value);
    });
    onThemeChange(sync);
    sync(getTheme());
  });
}
