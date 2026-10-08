// docs.js — documentation chrome: theme / density / direction toggles. Not part of the shipped system.
(() => {
  const root = document.documentElement;
  const get = (k) => { try { return localStorage.getItem(k); } catch { return null; } };
  const set = (k, v) => { try { localStorage.setItem(k, v); } catch {} };

  const themes = ["system", "light", "dark", "high-contrast"];
  const apply = (t) => (t === "system" ? root.removeAttribute("data-theme") : root.setAttribute("data-theme", t));
  let theme = get("ds-theme") || "system";
  apply(theme);

  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-theme-toggle], [data-density-toggle], [data-dir-toggle]");
    if (!btn) return;
    if (btn.hasAttribute("data-theme-toggle")) {
      theme = themes[(themes.indexOf(theme) + 1) % themes.length];
      apply(theme); set("ds-theme", theme);
      btn.textContent = `Theme: ${theme}`;
    } else if (btn.hasAttribute("data-density-toggle")) {
      const compact = root.getAttribute("data-density") !== "compact";
      compact ? root.setAttribute("data-density", "compact") : root.removeAttribute("data-density");
      btn.setAttribute("aria-pressed", String(compact));
    } else {
      root.dir = root.dir === "rtl" ? "ltr" : "rtl";
      btn.setAttribute("aria-pressed", String(root.dir === "rtl"));
    }
  });

  addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-theme-toggle]").forEach((b) => (b.textContent = `Theme: ${theme}`));
    // Show each demo's marker as a visible label so reviewers can map demos to the manifest.
    document.querySelectorAll(".ds-demo[data-demo]").forEach((d) => {
      if (d.querySelector(".ds-demo__label")) return;
      const l = document.createElement("span");
      l.className = "ds-demo__label";
      l.textContent = d.dataset.demo;
      d.prepend(l);
    });
  });
})();
