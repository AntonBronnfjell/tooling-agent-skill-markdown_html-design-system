// error-summary.js — focus the summary after a failed submit and mark the title (GOV.UK pattern).
// export init(root): idempotent. Links in the summary move focus to their field (not just scroll).
export function init(root = document) {
  const summary = root.querySelector(".error-summary");
  if (!summary || summary.dataset.enhanced) return;
  summary.dataset.enhanced = "1";
  if (!document.title.startsWith("Error: ")) document.title = "Error: " + document.title;
  summary.addEventListener("click", (event) => {
    const link = event.target.closest('a[href^="#"]');
    const field = link && document.getElementById(link.getAttribute("href").slice(1));
    if (field) { event.preventDefault(); field.focus?.(); field.scrollIntoView?.({ block: "center" }); }
  });
  if (root === document && summary.closest("form, .ds-demo") === null) summary.focus();
}
