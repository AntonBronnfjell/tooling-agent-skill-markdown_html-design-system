"""Write <site>/scopes.html from assets/manifest.json and link it from <site>/index.html.

Run by .github/workflows/pages.yml after the example site is assembled, so the page always matches the manifest.
Usage: python .github/scopes_page.py assets/manifest.json _site
"""
import json
import sys
from html import escape
from pathlib import Path

REPO = "https://github.com/AntonBronnfjell/tooling-agent-skill-markdown_html-design-system/blob/main"
TIERS = ("core", "standard", "enterprise")

manifest, site = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")), Path(sys.argv[2])
requires = manifest.get("scope_requires", {})
by_scope = {s: [] for s in manifest["scopes"]}
for cat in manifest["categories"]:
    by_scope[cat.get("scope", "product")] += [(cat, c) for c in cat["components"]]
total = sum(len(v) for v in by_scope.values())

rows, details = [], []
for scope, items in by_scope.items():
    tiers = " / ".join(str(sum(c["tier"] == t for _, c in items)) for t in TIERS)
    needs = ", ".join(f"<code>{escape(r)}</code>" for r in requires.get(scope, [])) or "—"
    doc = "" if scope == "product" else f'<a href="{REPO}/references/components/{scope}.md">{scope}.md</a>'
    rows.append(f"<tr><th scope=\"row\"><a href=\"#{scope}\"><code>{escape(scope)}</code></a></th><td>{len(items)}</td>"
                f"<td>{tiers}</td><td>{needs}</td><td>{doc}</td></tr>")
    lis = "".join(
        f'<li class="ds-index__item"><span>{escape(c["name"])} <code>{escape(c["id"])}</code></span>'
        f'<span class="ds-index__tier">{c["tier"]}{" · needs marketing" if c.get("requires_scopes") else ""}</span></li>'
        for _, c in items)
    details.append(f'<section aria-labelledby="{scope}"><h2 id="{scope}"><code>{escape(scope)}</code> · {len(items)}</h2>'
                   f'<p>{escape(manifest["scopes"][scope])}</p>'
                   f'<details><summary>Components</summary><ul class="ds-index" role="list">{lis}</ul></details></section>')

(site / "scopes.html").write_text(f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Scopes · html-design-system</title>
  <link rel="stylesheet" href="dist/ds.css">
  <link rel="stylesheet" href="docs/docs.css">
  <script src="docs/docs.js" defer></script>
</head>
<body class="ds-docs">
  <a class="sr-only sr-only--focusable" href="#main">Skip to content</a>
  <header class="ds-docs__header">
    <strong><a href="index.html">Fleetline</a></strong>
    <span>All scopes the skill can build · {total} components</span>
    <button type="button" class="ds-theme-toggle" data-theme-toggle>Theme</button>
  </header>
  <main id="main" class="ds-docs__main">
    <section aria-labelledby="title">
      <h1 id="title">Scopes</h1>
      <p>Fleetline is a core-tier <code>product</code> system. The skill can build {total} components across
        {len(by_scope)} scopes. Enable them with <code>ds init --scopes product,&lt;scope&gt;,…</code>; required scopes
        are added automatically, and landing pages also need <code>marketing</code>. Generated from
        <a href="{REPO}/assets/manifest.json">assets/manifest.json</a>.</p>
      <table class="ds-table">
        <caption class="sr-only">Scopes with component counts per tier</caption>
        <thead><tr><th scope="col">Scope</th><th scope="col">Components</th><th scope="col">Core / standard / enterprise</th>
          <th scope="col">Needs</th><th scope="col">Spec</th></tr></thead>
        <tbody>{"".join(rows)}</tbody>
      </table>
    </section>
    {"".join(details)}
  </main>
</body>
</html>
""", encoding="utf-8")

index = site / "index.html"
link = '<a href="dist/tokens.css">tokens.css</a>'
index.write_text(index.read_text(encoding="utf-8").replace(link, f'{link} · <a href="scopes.html">All scopes</a>', 1),
                 encoding="utf-8")
