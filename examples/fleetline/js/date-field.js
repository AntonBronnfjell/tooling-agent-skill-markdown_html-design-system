/**
 * date-field.js — locale order and lenient month input for .date-field (memorable date).
 *
 * - [data-locale-order] on the fieldset: reorders .date-field__item[data-part="day|month|year"] in the
 *   DOM (so reading and tab order follow) using Intl.DateTimeFormat(locale).formatToParts.
 *   The attribute value is a BCP 47 locale ("en-US", "ja-JP"); empty = the document/browser locale.
 *   Servers should render the right order too — this is a fallback when the locale is only known client-side.
 * - Month inputs accept names ("march", "Mar") and normalise them to a number on blur.
 * - Never auto-advances between inputs (breaks correction and screen readers).
 *
 * export init(root = document) — safe to call twice (data-enhanced).
 */
const monthNames = (locale) => {
  const fmt = (style) => new Intl.DateTimeFormat(locale, { month: style });
  return Array.from({ length: 12 }, (_, i) => {
    const d = new Date(2026, i, 1);
    return [fmt("long").format(d).toLowerCase(), fmt("short").format(d).toLowerCase().replace(".", "")];
  });
};

export function init(root = document) {
  root.querySelectorAll(".date-field:not([data-enhanced])").forEach((field) => {
    field.setAttribute("data-enhanced", "");
    const attr = field.getAttribute("data-locale-order");
    const locale = attr || document.documentElement.lang || navigator.language;

    if (attr !== null) {
      const order = new Intl.DateTimeFormat(locale, { day: "2-digit", month: "2-digit", year: "numeric" })
        .formatToParts(new Date(2026, 2, 14))
        .map((p) => p.type)
        .filter((t) => t === "day" || t === "month" || t === "year");
      const wrap = field.querySelector(".date-field__inputs");
      order.forEach((part) => {
        const item = wrap?.querySelector(`.date-field__item[data-part="${part}"]`);
        if (item) wrap.append(item);
      });
      field.dataset.order = order.map((p) => p[0].toUpperCase()).join("");
    }

    const month = field.querySelector('.date-field__item[data-part="month"] input');
    if (month) {
      const names = monthNames(locale);
      month.addEventListener("blur", () => {
        const v = month.value.trim().toLowerCase().replace(".", "");
        if (!v || /^\d+$/.test(v)) return;
        const i = names.findIndex(([long, short]) => long === v || short === v || (v.length >= 3 && long.startsWith(v)));
        if (i >= 0) month.value = String(i + 1);
      });
    }
  });
}
