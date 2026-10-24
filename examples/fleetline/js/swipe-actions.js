/**
 * swipe-actions.js — scroll-snap swipe rows (css/components/swipe-actions.css).
 *
 * The browser does the swipe: the row is a horizontal scroll-snap container. This module only reads the result:
 * puts every row at rest (content in view), keeps hidden actions `inert` so Tab never lands on them, keeps one row
 * open at a time, closes a row when its content is tapped, arms the full swipe (.is-full) past half the trailing
 * zone and runs the edge action when the row settles there. RTL-aware; instant (no smooth scroll) under reduced motion.
 * Every action is also in the row's "More actions" menu, so none of this is the only way (WCAG 2.5.7).
 *
 * export init(root = document) — enhances every .swipe-row that isn't a docs freeze; safe to call twice.
 */
const FROZEN = ".is-revealed-trailing, .is-revealed-leading, .is-full-swipe, .is-focus-visible";
const reduce = () => matchMedia("(prefers-reduced-motion: reduce)").matches || document.documentElement.hasAttribute("data-reduced-motion");
let openRow = null;

function enhance(row) {
  const track = row.querySelector(".swipe-row__track");
  const content = row.querySelector(".swipe-row__content");
  const lead = row.querySelector(".swipe-row__actions--leading");
  const trail = row.querySelector(".swipe-row__actions--trailing");
  if (!track || !content) return;
  row.setAttribute("data-enhanced", "");

  const rtl = () => getComputedStyle(track).direction === "rtl";
  const pos = () => Math.abs(track.scrollLeft);   // distance from the inline start, both directions
  const rest = () => (lead ? lead.offsetWidth : 0);
  const buttons = () => (trail ? [...trail.children].reduce((w, b) => w + b.offsetWidth, 0) : 0);
  const fullAt = () => rest() + buttons() + (trail ? trail.offsetWidth - buttons() : 0) / 2;
  const go = (x, smooth) => track.scrollTo({ left: (rtl() ? -1 : 1) * x, behavior: smooth && !reduce() ? "smooth" : "instant" });
  const close = (smooth = true) => go(rest(), smooth);
  row.swipeClose = close;

  const settle = () => {
    const s = pos();
    const full = trail && s >= fullAt();
    const leading = lead && s < rest() - 1;
    const trailing = trail && !full && s > rest() + 1;
    if (lead) lead.inert = !leading;
    if (trail) trail.inert = !trailing;
    row.classList.toggle("is-full", Boolean(full));
    if (leading || trailing) {
      if (openRow && openRow !== row) openRow.swipeClose();
      openRow = row;
    } else if (openRow === row) {
      openRow = null;
    }
    if (full) {
      trail.lastElementChild.click();   // the edge action; the app removes the row and offers Undo if it deletes
      close();
    }
  };

  let timer;
  track.addEventListener("scroll", () => {
    row.classList.toggle("is-full", Boolean(trail) && pos() >= fullAt());
    if (!("onscrollend" in window)) { clearTimeout(timer); timer = setTimeout(settle, 120); }
  }, { passive: true });
  track.addEventListener("scrollend", settle);

  // Tapping the content of an open row closes it instead of following the link.
  content.addEventListener("click", (e) => {
    if (openRow === row && !e.target.closest(".swipe-row__menu")) { e.preventDefault(); close(); }
  }, true);
  for (const b of row.querySelectorAll(".swipe-row__action")) b.addEventListener("click", () => close());

  close(false);
  if (lead) lead.inert = true;
  if (trail) trail.inert = true;
}

export function init(root = document) {
  for (const row of root.querySelectorAll(".swipe-row:not([data-enhanced])")) {
    if (!row.matches(FROZEN)) enhance(row);
  }
}
