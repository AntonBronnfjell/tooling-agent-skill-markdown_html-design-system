// theme.js — runtime theme API. Created by `ds.py init`; part of the shipped system.
// Usage: import { initTheme, setTheme, getTheme, onThemeChange } from './js/theme.js'; initTheme();
// No-flash: inline this in <head> BEFORE stylesheets so the first paint uses the saved theme:
//   <script>try{var t=localStorage.getItem("ds-theme");if(t&&t!=="system")document.documentElement.dataset.theme=t}catch(e){}</script>
const KEY = "ds-theme";
const root = document.documentElement;
const listeners = new Set();

const read = () => { try { return localStorage.getItem(KEY) || "system"; } catch { return "system"; } };
const write = (t) => { try { localStorage.setItem(KEY, t); } catch { /* private mode: keep in-memory only */ } };

function apply(theme) {
  theme === "system" ? root.removeAttribute("data-theme") : root.setAttribute("data-theme", theme);
  listeners.forEach((fn) => fn(theme));
}

/** Current choice: "system" or a theme name from tokens/themes. */
export const getTheme = () => root.getAttribute("data-theme") || "system";

/** Effective scheme after resolving "system" (reads the theme's color-scheme declared in tokens.css). */
export function getColorScheme() {
  if (getTheme() === "system") return matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  return getComputedStyle(root).colorScheme.trim().startsWith("dark") ? "dark" : "light";
}

export function setTheme(theme) { write(theme); apply(theme); }

export function onThemeChange(fn) { listeners.add(fn); return () => listeners.delete(fn); }

export function initTheme() {
  apply(read());
  // Keep tabs in sync.
  addEventListener("storage", (e) => { if (e.key === KEY) apply(e.newValue || "system"); });
}

/** Progressive enhancement for a theme toggle: <button data-theme-cycle data-themes="system light dark">. */
export function init(scope = document) {
  scope.querySelectorAll("[data-theme-cycle]").forEach((btn) => {
    const themes = (btn.dataset.themes || "system light dark").split(/\s+/);
    const label = () => (btn.querySelector("[data-theme-label]") || btn).textContent = `Theme: ${getTheme()}`;
    btn.addEventListener("click", () => setTheme(themes[(themes.indexOf(getTheme()) + 1) % themes.length]));
    onThemeChange(label);
    label();
  });
}
