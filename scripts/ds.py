#!/usr/bin/env python3
"""html-design-system CLI. Stdlib only.

  ds.py init <dir> [--name N] [--tier core|standard|enterprise] [--force]
  ds.py audit <path>                 inventory an existing codebase's de-facto design system
  ds.py build <dir>                  tokens -> dist/tokens.css, bundle dist/ds.css, docs index.html
  ds.py check <dir> [--strict]       validate tokens + contrast, lint CSS/HTML, coverage summary
  ds.py coverage <dir> [--json] [--all]
  ds.py plan <dir>                   ordered build queue (markdown checklist) of what is missing
  ds.py phase <dir> <discover|decide|plan|build|done>
  ds.py storybook <dir> [--force]    generate a standalone Storybook (html-vite) from the component pages
  ds.py serve <dir> [--port 8000]    build and preview the docs site with no dependencies
  ds.py design-md <dir>              write DESIGN.md: the one-file contract (themes, type, scales, rules, inventory)
  ds.py package <dir>                npm-ready package.json (exports css/tokens/js, files, sideEffects)
  ds.py ci <dir> [--provider github|gitlab]   pipeline: check -> Storybook to Pages -> idempotent npm publish
  ds.py status [path]                one-paragraph state of the nearest design system (for context injection)
  ds.py hook-post-edit | hook-stop   Claude Code hook entry points (read JSON on stdin)
"""
import argparse, json, os, re, shutil, sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
MANIFEST = json.loads((SKILL / "assets" / "manifest.json").read_text())
TIERS = ["core", "standard", "enterprise"]
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "vendor", "graphify-out", "__pycache__", "storybook-static"}


# ---------- helpers ----------
def load_cfg(root):
    return json.loads((Path(root) / "ds.config.json").read_text())


def save_cfg(root, cfg):
    (Path(root) / "ds.config.json").write_text(json.dumps(cfg, indent=2) + "\n")


def in_tier(item_tier, cfg_tier):
    return TIERS.index(item_tier) <= TIERS.index(cfg_tier)


def components(cfg=None, all_tiers=False):
    for cat in MANIFEST["categories"]:
        for c in cat["components"]:
            if all_tiers or cfg is None or in_tier(c["tier"], cfg["tier"]):
                yield cat, c


def page_path(root, cat, c):
    sub = "patterns" if cat["id"] == "patterns" else "components"
    return Path(root) / sub / f"{c['file']}.html", Path(root) / "css" / sub / f"{c['file']}.css"


def find_root(start, depth=3):
    """Find the nearest ds.config.json at/below start (depth-limited) or above it."""
    start = Path(start).resolve()
    for p in [start, *start.parents]:
        if (p / "ds.config.json").exists():
            return p
    frontier = [start]
    for _ in range(depth):
        nxt = []
        for d in frontier:
            try:
                for ch in d.iterdir():
                    if ch.is_dir() and ch.name not in SKIP_DIRS and not ch.name.startswith("."):
                        if (ch / "ds.config.json").exists():
                            return ch
                        nxt.append(ch)
            except OSError:
                pass
        frontier = nxt
    return None


# ---------- tokens ----------
def deep_merge(a, b):
    out = dict(a)
    for k, v in b.items():
        out[k] = deep_merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) and "$value" not in v else v
    return out


def flatten(tree, prefix=(), inherited_type=None, out=None):
    out = {} if out is None else out
    t = tree.get("$type", inherited_type)
    for k, v in tree.items():
        if k.startswith("$") or not isinstance(v, dict):
            continue
        if "$value" in v:
            out[".".join(prefix + (k,))] = {"value": v["$value"], "type": v.get("$type", t)}
        else:
            flatten(v, prefix + (k,), t, out)
    return out


REF = re.compile(r"\{([^{}]+)\}")


def var_name(path):
    return "--" + path.replace(".", "-")


def to_css(value, typ, flat, as_var=True):
    """Render a DTCG value as CSS. References become var() (as_var) or resolved values."""
    if isinstance(value, str):
        def rep(m):
            ref = m.group(1)
            if ref not in flat:
                raise ValueError(f"unresolved reference {{{ref}}}")
            return f"var({var_name(ref)})" if as_var else to_css(flat[ref]["value"], flat[ref]["type"], flat, False)
        return REF.sub(rep, value)
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        if typ == "cubicBezier":
            return f"cubic-bezier({', '.join(map(str, value))})"
        if typ == "fontFamily":
            return ", ".join(v if v in GENERIC_FONTS or v.startswith("var(") else f'"{v}"' for v in value)
        if typ == "shadow":
            return ", ".join(to_css(v, typ, flat, as_var) for v in value)
        return " ".join(to_css(v, typ, flat, as_var) for v in value)
    if isinstance(value, dict):
        if "unit" in value and "value" in value:
            return f"{value['value']}{value['unit']}"
        if "hex" in value:
            return value["hex"]
        if typ == "shadow" or {"offsetX", "offsetY"} <= value.keys():
            parts = [to_css(value.get(p, 0), "dimension", flat, as_var) for p in ("offsetX", "offsetY", "blur", "spread")]
            s = " ".join(parts) + " " + to_css(value.get("color", "transparent"), "color", flat, as_var)
            return ("inset " if value.get("inset") else "") + s
        if typ == "border":
            return " ".join(to_css(value[p], None, flat, as_var) for p in ("width", "style", "color") if p in value)
        if typ == "transition":
            return " ".join(to_css(value[p], None, flat, as_var) for p in ("duration", "timingFunction", "delay") if p in value)
        if typ == "typography":
            return None  # composite: emitted as sub-properties
    raise ValueError(f"cannot render value {value!r} ({typ})")


GENERIC_FONTS = {"serif", "sans-serif", "monospace", "system-ui", "ui-sans-serif", "ui-serif", "ui-monospace",
                 "cursive", "fantasy", "-apple-system", "BlinkMacSystemFont", "emoji", "math"}


def load_tokens(root):
    root = Path(root)
    t = root / "tokens"
    base = {}
    files = [t / n for n in ("primitive.json", "semantic.json", "component.json")]
    files += sorted((t / "components").glob("*.json"))  # one file per component: parallel-safe
    for f in files:
        if f.exists():
            try:
                base = deep_merge(base, json.loads(f.read_text()))
            except json.JSONDecodeError as e:
                raise ValueError(f"{f.relative_to(root)}: invalid JSON ({e})")
    themes = {p.stem: json.loads(p.read_text()) for p in sorted((t / "themes").glob("*.json"))} if (t / "themes").exists() else {}
    return base, themes


def decls(flat, keys):
    lines = []
    for k in keys:
        v = flat[k]
        if v["type"] == "typography" and isinstance(v["value"], dict):
            for sub, sv in v["value"].items():
                prop = re.sub(r"(?<!^)(?=[A-Z])", "-", sub).lower()
                lines.append(f"  {var_name(k)}-{prop}: {to_css(sv, None, flat)};")
            continue
        lines.append(f"  {var_name(k)}: {to_css(v['value'], v['type'], flat)};")
    return "\n".join(lines)


def build_tokens(root):
    base, themes = load_tokens(root)
    flat = flatten(base)
    css = ["/* Generated by ds.py build — edit tokens/*.json, not this file. */",
           ":root {\n  color-scheme: light dark;\n" + decls(flat, list(flat)) + "\n}"]
    for name, tree in themes.items():
        tflat = flatten(tree)
        merged = {**flat, **tflat}
        scheme = "dark" if name == "dark" or tree.get("$extensions", {}).get("color-scheme") == "dark" else "light"
        body = f"  color-scheme: {scheme};\n" + decls(merged, list(tflat))
        if name == "dark":
            css.append(f"@media (prefers-color-scheme: dark) {{\n  :root:not([data-theme]) {{\n{body}\n  }}\n}}")
        if name == "high-contrast":
            css.append(f"@media (prefers-contrast: more) {{\n  :root:not([data-theme]) {{\n{body}\n  }}\n}}")
        # Attribute on <html> for the page; class for a themed subtree (e.g. an always-dark media stage).
        # Semantic vars are redeclared here, so the subtree resolves them against its own theme.
        css.append(f'[data-theme="{name}"], .theme-{name} {{\n{body}\n}}')
    if "light" not in themes:
        # Re-declare every themed token with its default value so a light subtree works inside a dark page.
        keys = sorted({k for tree in themes.values() for k in flatten(tree)} & set(flat))
        css.append('[data-theme="light"], .theme-light {\n  color-scheme: light;\n' + decls(flat, keys) + "\n}")
    aliases = deprecated_aliases(base, flat)
    if aliases:
        css.append("/* Deprecated aliases — removed in the next major version. */\n:root {\n" + aliases + "\n}")
    out = Path(root) / "dist" / "tokens.css"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n\n".join(css) + "\n")
    write_token_modules(root, flat)
    return out, flat, themes


def deprecated_aliases(base, flat):
    """`"$deprecated": {"old.name": "new.name"}` at the top of any token file -> var alias with a warning comment."""
    lines = []
    for old, new in (base.get("$deprecated") or {}).items():
        if new in flat:
            lines.append(f"  {var_name(old)}: var({var_name(new)}); /* deprecated: use {var_name(new)} */")
    return "\n".join(lines)


def write_token_modules(root, flat):
    """Build-time token outputs for places CSS variables can't reach (media queries, JS, Sass)."""
    resolved = {}
    for k, v in flat.items():
        if v["type"] == "typography":
            continue
        try:
            resolved[k] = to_css(v["value"], v["type"], flat, as_var=False)
        except ValueError:
            continue
    dist = Path(root) / "dist"
    (dist / "tokens.json").write_text(json.dumps(resolved, indent=1) + "\n")
    scss = ["// Generated by ds.py build — static values (default theme). Use CSS vars at runtime; these are for",
            "// media queries and build-time math only."]
    scss += [f"${k.replace('.', '-')}: {v};" for k, v in resolved.items()]
    bps = {k.split(".", 1)[1]: v for k, v in resolved.items() if k.startswith("breakpoint.")}
    if bps:
        scss.append("$breakpoints: (" + ", ".join(f'"{n}": {v}' for n, v in bps.items()) + ");")
        scss.append("@mixin up($bp) { @media (min-width: map-get($breakpoints, $bp)) { @content; } }")
        scss.append("@mixin down($bp) { @media (max-width: calc(map-get($breakpoints, $bp) - 0.02px)) { @content; } }")
    (dist / "tokens.scss").write_text("\n".join(scss) + "\n")


def hex_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) in (3, 4):
        h = "".join(c * 2 for c in h[:3])
    if not re.fullmatch(r"[0-9a-fA-F]{6}([0-9a-fA-F]{2})?", h):
        return None
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def luminance(rgb):
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = map(f, rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def check_tokens(root, cfg):
    errs, warns = [], []
    try:
        base, themes = load_tokens(root)
        flat = flatten(base)
        for k, v in flat.items():
            to_css(v["value"], v["type"], flat)
            if not v["type"]:
                warns.append(f"token {k} has no $type")
    except Exception as e:  # noqa: BLE001 - report any token failure
        return [f"tokens: {e}"], warns
    groups = {k.split(".")[0] for k in flat}
    need = [g for t in TIERS if in_tier(t, cfg["tier"]) for g in MANIFEST["token_groups_required"][t]]
    for g in need:
        if g not in groups:
            errs.append(f"missing token group '{g}' (tier {cfg['tier']})")
    need_themes = [th for t in TIERS if in_tier(t, cfg["tier"]) for th in MANIFEST["themes_required"][t]]
    for th in need_themes:
        if th != "light" and th not in themes:
            errs.append(f"missing theme tokens/themes/{th}.json")
    for name in ["light", *themes]:
        merged = flat if name == "light" else {**flat, **flatten(themes[name])}
        for fg, bg, minimum in cfg.get("contrast_pairs", []):
            if fg not in merged or bg not in merged:
                errs.append(f"contrast pair {fg} / {bg}: token missing")
                continue
            a = hex_rgb(to_css(merged[fg]["value"], "color", merged, as_var=False))
            b = hex_rgb(to_css(merged[bg]["value"], "color", merged, as_var=False))
            if not a or not b:
                warns.append(f"[{name}] {fg} / {bg}: non-hex color, contrast not checked")
                continue
            ratio = contrast(a, b)
            if ratio < minimum:
                errs.append(f"[{name}] contrast {fg} on {bg} = {ratio:.2f}:1 < {minimum}:1")
    return errs, warns


# ---------- lint ----------
CSS_RULES = [
    (re.compile(r"#[0-9a-fA-F]{3,8}\b"), "raw hex color — use a semantic token var()"),
    (re.compile(r"\b(rgba?|hsla?|oklch|oklab)\("), "raw color function — use a token var()"),
    (re.compile(r"!important"), "!important — fix specificity instead (allowed only in base utilities)"),
    (re.compile(r"outline\s*:\s*(none|0)\s*;"), "outline removed — ensure a :focus-visible replacement exists"),
    (re.compile(r"(?<![\w-])(margin|padding|gap|inset|top|left|right|bottom)[\w-]*\s*:\s*[^;]*\b([2-9]|\d{2,})px"),
     "raw px spacing — use --space-* tokens"),
    (re.compile(r"z-index\s*:\s*\d{2,}"), "raw z-index — use --z-* tokens"),
    (re.compile(r"(transition|animation)[\w-]*\s*:[^;]*\b\d+m?s\b"), "raw duration — use --motion-* tokens"),
]
HTML_RULES = [
    (re.compile(r"<img(?![^>]*\balt=)[^>]*>", re.I), "img without alt"),
    (re.compile(r"tabindex=\"[1-9]", re.I), "positive tabindex"),
    (re.compile(r"<(div|span)[^>]*\bonclick=", re.I), "click handler on div/span — use <button>"),
    (re.compile(r"<button(?![^>]*\btype=)[^>]*>", re.I), "button without explicit type"),
    (re.compile(r"<a(?![^>]*\bhref=)[^>]*>", re.I), "<a> without href — use <button> for actions"),
    (re.compile(r"user-scalable\s*=\s*no|maximum-scale\s*=\s*1", re.I), "zoom disabled in viewport meta"),
]
ICON_BTN = re.compile(r"<button(?![^>]*aria-label)[^>]*>\s*<svg[^>]*>.*?</svg>\s*</button>", re.I | re.S)


def lint_file(path):
    path = Path(path)
    issues = []
    try:
        text = path.read_text(errors="ignore")
    except OSError:
        return issues
    if path.suffix == ".css" and "dist" not in path.parts and path.name != "base.css" and "docs" not in path.parts:
        stripped = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
        # token fallbacks inside var() are fine: var(--x, #fff)
        stripped = re.sub(r"var\([^()]*(\([^()]*\))?[^()]*\)", "var()", stripped)
        for i, line in enumerate(stripped.splitlines(), 1):
            for rx, msg in CSS_RULES:
                if rx.search(line):
                    issues.append(f"{path.name}:{i}: {msg}")
        if ":focus" in text and ":focus-visible" not in text:
            issues.append(f"{path.name}: uses :focus without :focus-visible")
    elif path.suffix == ".html":
        for rx, msg in HTML_RULES:
            for m in rx.finditer(text):
                issues.append(f"{path.name}:{text.count(chr(10), 0, m.start()) + 1}: {msg}")
        for m in ICON_BTN.finditer(text):
            inner = m.group(0)
            if not re.search(r"class=\"[^\"]*sr-only|visually-hidden", inner):
                issues.append(f"{path.name}:{text.count(chr(10), 0, m.start()) + 1}: icon-only button without aria-label")
    return issues


# ---------- coverage ----------
def coverage(root, cfg, all_tiers=False):
    root = Path(root)
    report = []
    cache = {}
    for cat, c in components(cfg, all_tiers):
        page, css = page_path(root, cat, c)
        if page not in cache:
            cache[page] = page.read_text(errors="ignore") if page.exists() else None
        html = cache[page]
        missing = []
        if html is None:
            missing.append(f"page {page.relative_to(root)}")
        else:
            if not re.search(rf'\bid="{re.escape(c["id"])}"', html):
                missing.append(f'section id="{c["id"]}"')
            for d in c["demos"]:
                if f'data-demo="{d}"' not in html and not re.search(rf'data-demo="[^"]*\b{re.escape(d)}(\s|")', html):
                    missing.append(f"demo {d}")
            for s in MANIFEST["doc_sections"]:
                if f'data-doc="{s}"' not in html:
                    missing.append(f"doc section {s}")
        if not css.exists():
            missing.append(f"css {css.relative_to(root)}")
        report.append({"id": c["id"], "name": c["name"], "category": cat["id"], "tier": c["tier"],
                       "file": c["file"], "done": not missing, "missing": missing})
    return report


def summarize(report):
    done = sum(r["done"] for r in report)
    return done, len(report)


# ---------- commands ----------
def cmd_init(a):
    root = Path(a.dir)
    if (root / "ds.config.json").exists() and not a.force:
        sys.exit(f"{root}/ds.config.json exists (use --force to overwrite templates)")
    tpl = SKILL / "assets" / "templates"
    for sub in ("tokens/themes", "tokens/components", "css/components", "css/patterns", "components", "patterns", "docs", "dist", "js"):
        (root / sub).mkdir(parents=True, exist_ok=True)
    for src, dst in [("tokens/primitive.json", "tokens/primitive.json"), ("tokens/semantic.json", "tokens/semantic.json"),
                     ("tokens/component.json", "tokens/component.json"), ("tokens/themes/dark.json", "tokens/themes/dark.json"),
                     ("tokens/themes/high-contrast.json", "tokens/themes/high-contrast.json"),
                     ("base.css", "css/base.css"), ("docs.css", "docs/docs.css"), ("docs.js", "docs/docs.js"),
                     ("component.html", "docs/_component-template.html"),
                     ("theme.js", "js/theme.js")]:
        if a.force or not (root / dst).exists():
            shutil.copy(tpl / src, root / dst)
    cfg = json.loads((tpl / "ds.config.json").read_text())
    cfg.update({"name": a.name or cfg["name"], "tier": a.tier})
    save_cfg(root, cfg)
    build_tokens(root)
    print(f"Initialized design system '{cfg['name']}' (tier {a.tier}) in {root}")
    print("Next: fill ds.config.json brief/direction, edit tokens/*.json, then `ds.py build` and `ds.py plan`.")


def cmd_audit(a):
    root = Path(a.path)
    exts = {".css", ".scss", ".sass", ".less", ".html", ".jsx", ".tsx", ".vue", ".svelte", ".js", ".ts", ".astro"}
    pats = {
        "colors": re.compile(r"(?<![\w&/=\"'])#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b|rgba?\([^)]*\)|hsla?\([^)]*\)|oklch\([^)]*\)"),
        "custom_properties": re.compile(r"(?<![\w-])(--[\w-]+)\s*:(?![\w-])"),
        "font_families": re.compile(r"font-family\s*:\s*([^;}{]+)"),
        "font_sizes": re.compile(r"font-size\s*:\s*([^;}{]+)"),
        "spacing": re.compile(r"(?:margin|padding|gap)[\w-]*\s*:\s*([^;}{]+)"),
        "radii": re.compile(r"border-radius\s*:\s*([^;}{]+)"),
        "shadows": re.compile(r"box-shadow\s*:\s*([^;}{]+)"),
        "breakpoints": re.compile(r"@media[^{]*?\((?:min|max)-width\s*:\s*([^)]+)\)"),
        "tailwind_classes": re.compile(r"\b(?:bg|text|p|px|py|m|mx|my|gap|rounded|shadow)-[\w\[\]#./-]+"),
    }
    counts = {k: {} for k in pats}
    names = {}
    keywords = {c["id"]: [c["id"].split("-")[0], c["file"]] for _, c in components(all_tiers=True)}
    nfiles = 0
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in fns:
            p = Path(dp) / fn
            if p.suffix not in exts:
                continue
            nfiles += 1
            text = p.read_text(errors="ignore")
            for k, rx in pats.items():
                for m in rx.finditer(text):
                    v = (m.group(1) if rx.groups else m.group(0)).strip()[:80]
                    counts[k][v] = counts[k].get(v, 0) + 1
            stem = p.stem.lower()
            for cid, kws in keywords.items():
                if any(kw == stem or stem.startswith(kw + ".") or stem.startswith(kw + "-") for kw in kws):
                    names.setdefault(cid, []).append(str(p.relative_to(root)))
    print(f"# Design inventory: {root}  ({nfiles} files scanned)\n")
    for k, d in counts.items():
        if not d:
            continue
        top = sorted(d.items(), key=lambda x: -x[1])[:25]
        print(f"## {k} — {len(d)} distinct")
        print("\n".join(f"- `{v}` ×{n}" for v, n in top) + "\n")
    print("## Existing component candidates (by file name)")
    for cid, files in sorted(names.items()):
        print(f"- {cid}: {', '.join(sorted(set(files))[:5])}")
    print("\nInterpretation: many distinct colors/spacings = no system yet (consolidate into tokens);"
          " heavy custom_properties/tailwind usage = extract existing tokens instead of inventing new ones.")


def cmd_build(a):
    root = Path(a.dir)
    cfg = load_cfg(root)
    out, _, _ = build_tokens(root)
    parts = [out, root / "css" / "base.css"]
    parts += sorted((root / "css" / "components").glob("*.css")) + sorted((root / "css" / "patterns").glob("*.css"))
    bundle = "\n".join(f"/* ---- {p.relative_to(root)} ---- */\n{p.read_text()}" for p in parts if p.exists())
    (root / "dist" / "ds.css").write_text(bundle)
    write_index(root, cfg)
    print(f"built {out.relative_to(root)}, dist/ds.css ({len(parts)} sources), index.html")


def write_index(root, cfg):
    report = coverage(root, cfg)
    done, total = summarize(report)
    by_cat = {}
    for r in report:
        by_cat.setdefault(r["category"], []).append(r)
    names = {c["id"]: c["name"] for c in MANIFEST["categories"]}
    sections = []
    for cid, rows in by_cat.items():
        sub = "patterns" if cid == "patterns" else "components"
        items = "\n".join(
            f'      <li class="ds-index__item" data-done="{str(r["done"]).lower()}">'
            f'<a href="{sub}/{r["file"]}.html#{r["id"]}">{r["name"]}</a>'
            f'<span class="ds-index__tier">{r["tier"]}</span>'
            f'<span class="ds-index__status">{"Ready" if r["done"] else "Missing " + str(len(r["missing"]))}</span></li>'
            for r in rows)
        sections.append(f'    <section aria-labelledby="cat-{cid}">\n      <h2 id="cat-{cid}">{names[cid]}</h2>\n'
                        f'      <ul class="ds-index" role="list">\n{items}\n      </ul>\n    </section>')
    name = cfg["name"]
    html = f"""<!doctype html>
<html lang="{cfg.get('lang', 'en')}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{name} Design System</title>
  <link rel="stylesheet" href="dist/ds.css">
  <link rel="stylesheet" href="docs/docs.css">
  <script src="docs/docs.js" defer></script>
</head>
<body class="ds-docs">
  <a class="sr-only sr-only--focusable" href="#main">Skip to content</a>
  <header class="ds-docs__header">
    <strong>{name}</strong>
    <span>{done}/{total} components ready · tier {cfg['tier']}</span>
    <button type="button" class="ds-theme-toggle" data-theme-toggle>Theme</button>
  </header>
  <main id="main" class="ds-docs__main">
    <h1>{name} Design System</h1>
    <p>Generated index. Foundations: <a href="components/typography.html">Typography</a> ·
       <a href="dist/tokens.css">tokens.css</a></p>
{chr(10).join(sections)}
  </main>
</body>
</html>
"""
    (Path(root) / "index.html").write_text(html)


def cmd_check(a):
    root = Path(a.dir)
    cfg = load_cfg(root)
    errs, warns = check_tokens(root, cfg)
    lint = []
    for p in sorted(list(root.glob("css/**/*.css")) + list(root.glob("components/*.html")) + list(root.glob("patterns/*.html"))):
        lint += lint_file(p)
    report = coverage(root, cfg)
    done, total = summarize(report)
    print("## Tokens")
    print("\n".join(f"- ERROR {e}" for e in errs) or "- ok")
    for w in warns:
        print(f"- warn {w}")
    print(f"\n## Lint ({len(lint)} issues)")
    print("\n".join(f"- {i}" for i in lint[:200]) or "- ok")
    print(f"\n## Coverage: {done}/{total} complete (tier {cfg['tier']}) — run `ds.py coverage` for details")
    if errs or (a.strict and (lint or done < total)):
        sys.exit(1)


def cmd_coverage(a):
    root = Path(a.dir)
    cfg = load_cfg(root)
    report = coverage(root, cfg, a.all)
    if a.json:
        print(json.dumps(report, indent=1))
        return
    done, total = summarize(report)
    print(f"# Coverage {done}/{total} (tier {cfg['tier']})\n")
    for r in report:
        mark = "x" if r["done"] else " "
        extra = "" if r["done"] else " — missing: " + "; ".join(r["missing"][:8]) + (" …" if len(r["missing"]) > 8 else "")
        print(f"- [{mark}] {r['category']}/{r['id']} ({r['tier']}){extra}")


def cmd_plan(a):
    root = Path(a.dir)
    cfg = load_cfg(root)
    report = coverage(root, cfg)
    todo = [r for r in report if not r["done"]]
    print(f"# Build queue for {cfg['name']} — {len(todo)} items remaining\n")
    print("Order: foundations → actions → forms → navigation → data display → overlays → feedback → patterns.")
    print("Build one *file* (page + css) at a time; it closes every component sharing it.")
    print("Before overlays and composite widgets, build js/lib/ shared behaviors once (roving focus, dismiss, position, hotkey, live region).\n")
    seen = set()
    for r in todo:
        key = (r["category"], r["file"])
        if key in seen:
            continue
        seen.add(key)
        group = [x["id"] for x in todo if (x["category"], x["file"]) == key]
        print(f"- [ ] **{r['category']}/{r['file']}** → {', '.join(group)}")


def cmd_phase(a):
    root = Path(a.dir)
    cfg = load_cfg(root)
    cfg["phase"] = a.phase
    save_cfg(root, cfg)
    print(f"phase = {a.phase}")


def cmd_status(a):
    root = find_root(a.path or os.getcwd())
    if not root:
        print("No design system found (no ds.config.json in or near the working directory). Start at Phase 0.")
        return
    cfg = load_cfg(root)
    report = coverage(root, cfg)
    done, total = summarize(report)
    errs, _ = check_tokens(root, cfg)
    nxt = []
    for r in report:
        if not r["done"] and r["file"] not in nxt:
            nxt.append(r["file"])
    d = cfg.get("direction", {})
    print(f"Design system '{cfg['name']}' at {root} — phase: {cfg.get('phase')}, tier: {cfg['tier']}, "
          f"direction: {d.get('mode') or 'undecided'}{' / ' + d['reference_system'] if d.get('reference_system') else ''}. "
          f"Coverage {done}/{total}; token errors: {len(errs)}. Next files: {', '.join(nxt[:10]) or 'none'}.")


# ---------- storybook & serve ----------
from html.parser import HTMLParser

CAT_TITLES = {"foundations": "Foundations", "actions": "Actions", "forms": "Forms", "navigation": "Navigation",
              "data-display": "Data Display", "overlays": "Overlays", "feedback": "Feedback", "patterns": "Patterns"}
SB_VERSION = "^10.6.1"


class DemoExtractor(HTMLParser):
    """Collect (section_id, markers, inner_html) for every element carrying data-demo, plus the usage text."""

    def __init__(self, src):
        super().__init__(convert_charrefs=True)
        self.src = src
        self.line_starts = [0]
        for m in re.finditer("\n", src):
            self.line_starts.append(m.end())
        self.sections, self.open, self.demos = [], [], []
        self.usage_depth, self.usage = None, []
        self.depth = 0
        self.in_heading = False

    def src_pos(self):
        line, col = self.getpos()
        return self.line_starts[line - 1] + col

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.depth += 1
        self.in_heading = tag in ("h1", "h2", "h3", "h4", "h5", "h6")
        if tag == "section" and a.get("id"):
            self.sections.append((self.depth, a["id"]))
        if a.get("data-doc") == "usage":
            self.usage_depth = self.depth
        if "data-demo" in a and not self.open:
            start = self.src_pos() + len(self.get_starttag_text())
            self.open.append({"tag": tag, "depth": self.depth, "start": start, "markers": a["data-demo"],
                              "section": self.sections[-1][1] if self.sections else None})
        if tag in ("area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"):
            self.depth -= 1

    def handle_endtag(self, tag):
        self.in_heading = False
        if self.open and tag == self.open[-1]["tag"] and self.depth == self.open[-1]["depth"]:
            d = self.open.pop()
            self.demos.append((d["section"], d["markers"], self.src[d["start"]:self.src_pos()].strip()))
        if self.sections and self.sections[-1][0] == self.depth:
            self.sections.pop()
        if self.usage_depth == self.depth:
            self.usage_depth = None
        self.depth -= 1

    def handle_data(self, data):
        if self.usage_depth is not None and not self.open and not self.in_heading and data.strip():
            self.usage.append(data.strip())


def js_ident(text, used):
    base = "".join(w[:1].upper() + w[1:] for w in re.split(r"[^A-Za-z0-9]+", text) if w) or "Story"
    if base[0].isdigit():
        base = "S" + base
    name, i = base, 2
    while name in used:
        name, i = f"{base}{i}", i + 1
    used.add(name)
    return name


def write_if_missing(path, text, force):
    if force or not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return True
    return False


def cmd_storybook(a):
    root = Path(a.dir)
    cfg = load_cfg(root)
    build_tokens(root)
    cmd_build(argparse.Namespace(dir=str(root)))
    tpl = SKILL / "assets" / "templates" / "storybook"
    slug = re.sub(r"[^a-z0-9]+", "-", cfg["name"].lower()).strip("-") or "design-system"
    pkg = {"name": f"{slug}-design-system", "private": True, "type": "module",
           "scripts": {"storybook": "storybook dev -p 6006", "build-storybook": "storybook build -o storybook-static",
                       "stories": ("python3 tools/ds/scripts/ds.py storybook ." if (root / "tools" / "ds").exists()
                                   else "python3 " + json.dumps(str(SKILL / "scripts" / "ds.py"))[1:-1] + " storybook .")},
           "devDependencies": {"storybook": SB_VERSION, "@storybook/html-vite": SB_VERSION, "@storybook/addon-a11y": SB_VERSION,
                               "@storybook/addon-docs": SB_VERSION, "vite": "^8.0.0"}}
    if (root / "package.json").exists() and not a.force:
        existing = json.loads((root / "package.json").read_text())
        for k in ("scripts", "devDependencies"):
            existing.setdefault(k, {})
            for kk, vv in pkg[k].items():
                existing[k].setdefault(kk, vv)
        pkg = existing
    (root / "package.json").write_text(json.dumps(pkg, indent=2) + "\n")
    write_if_missing(root / ".storybook" / "main.js", (tpl / "main.js").read_text(), a.force)
    write_if_missing(root / ".storybook" / "preview.js", (tpl / "preview.js").read_text(), a.force)
    gi = root / ".gitignore"
    lines = gi.read_text().splitlines() if gi.exists() else []
    gi.write_text("\n".join(lines + [x for x in ("node_modules/", "storybook-static/") if x not in lines]) + "\n")

    stories = root / "stories"
    if stories.exists():
        shutil.rmtree(stories)  # fully generated: the pages are the source of truth
    stories.mkdir()
    shutil.copy(tpl / "render.js", stories / "_render.js")
    _, themes = load_tokens(root)
    (stories / "_meta.js").write_text("// GENERATED by ds.py storybook — do not edit.\nexport const themes = "
                                      + json.dumps(["light", *[t for t in themes if t != "light"]]) + ";\n")

    file_cat = {}
    for cat, c in components(cfg, all_tiers=True):
        file_cat.setdefault((cat["id"] == "patterns", c["file"]), cat["id"])
    total = 0
    for sub in ("components", "patterns"):
        for page in sorted((root / sub).glob("*.html")):
            cat = file_cat.get((sub == "patterns", page.stem), "patterns" if sub == "patterns" else "foundations")
            ex = DemoExtractor(page.read_text(errors="ignore"))
            ex.feed(ex.src)
            if not ex.demos:
                continue
            title = f"{CAT_TITLES[cat]}/{page.stem.replace('-', ' ').title()}"
            js = root / "js" / f"{page.stem}.js"
            depth = "../../"
            out = [f"// GENERATED by ds.py storybook from {sub}/{page.name} — edit the page, then re-run `ds.py storybook`.",
                   f"import {{ render }} from '../_render.js';"]
            out.append(f"import * as behavior from '{depth}js/{page.stem}.js';" if js.exists() else "const behavior = null;")
            usage = " ".join(ex.usage)[:600]
            params = {"docs": {"description": {"component": usage}}}
            if cat == "patterns":
                params["layout"] = "fullscreen"
            out.append(f"\nexport default {{\n  title: {json.dumps(title)},\n  parameters: {json.dumps(params, ensure_ascii=False)},\n}};\n")
            used = set()
            for section, markers, html in ex.demos:
                label = f"{section} · {markers}" if section else markers
                name = js_ident(f"{section or ''} {markers}", used)
                out.append(f"export const {name} = {{\n  name: {json.dumps(label)},\n"
                           f"  render: () => render({json.dumps(html, ensure_ascii=False)}, behavior),\n"
                           f"  parameters: {{ docs: {{ source: {{ code: {json.dumps(html, ensure_ascii=False)}, language: 'html' }} }} }},\n}};\n")
                total += 1
            target = stories / CAT_TITLES[cat].lower().replace(" ", "-") / f"{page.stem}.stories.js"
            target.parent.mkdir(exist_ok=True)
            target.write_text("\n".join(out))

    # Foundations: a live token catalog rendered from the same flattened tokens used for tokens.css.
    base, _ = load_tokens(root)
    flat = flatten(base)
    rows = [{"var": var_name(k), "type": v["type"] or "", "path": k} for k, v in flat.items() if v["type"] != "typography"]
    (stories / "foundations").mkdir(exist_ok=True)
    (stories / "foundations" / "tokens.stories.js").write_text(
        "// GENERATED by ds.py storybook — token catalog. Values are read live from CSS, so themes apply.\n"
        f"const tokens = {json.dumps(rows)};\n" + TOKENS_STORY)
    reports = coverage(root, cfg)
    done, tot = summarize(reports)
    intro = (f"import {{ Meta }} from '@storybook/addon-docs/blocks';\n\n<Meta title=\"Introduction\" />\n\n"
             f"# {mdx_escape(cfg['name'])} design system\n\n"
             f"{mdx_escape(cfg.get('direction', {}).get('rationale') or 'Token-driven, accessible HTML/CSS components.')}\n\n"
             f"- Tier **{cfg['tier']}**, coverage **{done}/{tot}** components\n"
             f"- Use the toolbar to switch **theme**, **density** and **direction**; the **Accessibility** panel runs axe on every story.\n"
             f"- Stories are generated from the component pages (`components/*.html`). Edit a page, then run `npm run stories`.\n")
    (stories / "Introduction.mdx").write_text(intro)
    print(f"Storybook ready in {root}: {total} demo stories + token catalog.\n"
          f"  cd {root} && npm install && npm run storybook      (static site: npm run build-storybook)")


def mdx_escape(text):
    return re.sub(r"([{}<>])", r"\\\1", str(text))


TOKENS_STORY = r"""
export default { title: 'Foundations/Tokens', parameters: { layout: 'padded', docs: { description: { component: 'Every design token, rendered with its live value in the current theme.' } } } };

const read = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const groups = (filter) => tokens.filter(filter);

function table(list, preview) {
  const el = document.createElement('table');
  el.className = 'ds-table';
  el.innerHTML = '<thead><tr><th scope="col">Token</th><th scope="col">Value</th><th scope="col">Preview</th></tr></thead>';
  const body = el.createTBody();
  for (const t of list) {
    const tr = body.insertRow();
    tr.innerHTML = `<td><code>${t.var}</code></td><td><code>${read(t.var)}</code></td><td></td>`;
    tr.cells[2].append(preview(t));
  }
  return el;
}
const box = (style) => Object.assign(document.createElement('div'), { style: `inline-size:3rem;block-size:2rem;${style}` });

export const Color = { render: () => table(groups((t) => t.type === 'color'), (t) => box(`background:var(${t.var});border:1px solid var(--color-border-default)`)) };
export const Spacing = { render: () => table(groups((t) => t.path.startsWith('space.')), (t) => box(`inline-size:var(${t.var});background:var(--color-action-primary-bg)`)) };
export const Radius = { render: () => table(groups((t) => t.path.startsWith('radius.')), (t) => box(`border-radius:var(${t.var});background:var(--color-bg-muted);border:1px solid var(--color-border-strong)`)) };
export const Shadow = { render: () => table(groups((t) => t.type === 'shadow'), (t) => box(`box-shadow:var(${t.var});background:var(--color-bg-surface)`)) };
export const Typography = {
  render: () => {
    const wrap = document.createElement('div');
    for (const role of ['display', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'lead', 'body', 'small', 'caption', 'code']) {
      const p = document.createElement('p');
      p.textContent = `${role} — The quick brown fox jumps over the lazy dog`;
      Object.assign(p.style, {
        fontFamily: `var(--typography-${role}-font-family)`, fontSize: `var(--typography-${role}-font-size)`,
        fontWeight: `var(--typography-${role}-font-weight)`, lineHeight: `var(--typography-${role}-line-height)`,
      });
      wrap.append(p);
    }
    return wrap;
  },
};
export const Other = { render: () => table(groups((t) => !['color', 'shadow'].includes(t.type) && !/^(space|radius)\./.test(t.path)), () => document.createTextNode('')) };
"""


def cmd_serve(a):
    import functools, http.server, socketserver
    root = Path(a.dir).resolve()
    cmd_build(argparse.Namespace(dir=str(root)))
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(root))
    with socketserver.TCPServer(("127.0.0.1", a.port), handler) as httpd:
        print(f"Serving {root} at http://127.0.0.1:{a.port}/index.html  (Ctrl+C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


# ---------- DESIGN.md, packaging, CI ----------
def resolved_in(theme_flat, key):
    try:
        return to_css(theme_flat[key]["value"], theme_flat[key]["type"], theme_flat, as_var=False) if key in theme_flat else "—"
    except ValueError:
        return "—"


def cmd_design_md(a):
    """One file a human or agent can read instead of 100 pages: the system's contract."""
    root = Path(a.dir)
    cfg = load_cfg(root)
    build_tokens(root)
    base, themes = load_tokens(root)
    flat = flatten(base)
    theme_flats = {"light": flat, **{n: {**flat, **flatten(t)} for n, t in themes.items()}}
    d, brief = cfg.get("direction", {}), cfg.get("brief", {})
    md = [f"# {cfg['name']} — DESIGN.md", "",
          "> Generated by `ds.py design-md` from `ds.config.json` and `tokens/`. Edit those, then regenerate.",
          "> This is the contract: product code and AI agents should follow it without opening the component pages.", "",
          "## 1. Direction", "",
          f"- **Mode:** {d.get('mode') or '—'}{' · reference: ' + d['reference_system'] if d.get('reference_system') else ''}",
          f"- **Style:** {d.get('style') or '—'}", f"- **Product / audience:** {brief.get('product') or '—'} / {brief.get('audience') or '—'}",
          f"- **Accessibility target:** {brief.get('a11y_target', 'WCAG 2.2 AA')}", f"- **Rationale:** {d.get('rationale') or '—'}"]
    if d.get("allocation"):
        md += ["", "| Style direction | Owns | Never used for |", "|---|---|---|"]
        md += [f"| {x.get('name', '')} | {x.get('owns', '')} | {x.get('never', '')} |" for x in d["allocation"]]
    if cfg.get("principles"):
        md += ["", "**Principles**", ""] + [f"{i}. {p}" for i, p in enumerate(cfg["principles"], 1)]
    keys = ["color.bg.canvas", "color.bg.surface", "color.text.default", "color.text.muted", "color.action.primary.bg",
            "color.action.primary.fg", "color.border.default", "color.border.focus", "color.feedback.danger.fg"]
    md += ["", "## 2. Themes", "", "Apply with `data-theme` on `<html>` (or `.theme-<name>` on a subtree). Default follows the OS.", "",
           "| Token | " + " | ".join(theme_flats) + " |", "|---|" + "---|" * len(theme_flats)]
    md += [f"| `{var_name(k)}` | " + " | ".join(f"`{resolved_in(tf, k)}`" for tf in theme_flats.values()) + " |" for k in keys if k in flat]
    md += ["", "## 3. Typography", "", "| Role | Family | Size | Weight | Line height |", "|---|---|---|---|---|"]
    for k, v in flat.items():
        if v["type"] == "typography" and isinstance(v["value"], dict):
            val = v["value"]
            res = lambda x: to_css(val.get(x, ""), None, flat, as_var=False) if val.get(x) else "—"
            md.append(f"| `{k.split('.', 1)[1]}` | {res('fontFamily')} | {res('fontSize')} | {res('fontWeight')} | {res('lineHeight')} |")

    def scale(prefix, title, note=""):
        rows = [(k, resolved_in(flat, k)) for k in flat if k.startswith(prefix)]
        if rows:
            md.extend(["", f"## {title}", ""] + ([note, ""] if note else []) + [f"- `{var_name(k)}` = `{v}`" for k, v in rows])
    scale("space.", "4. Spacing", "Components never set outer margins; parents own spacing with gap.")
    scale("radius.", "5. Radius")
    scale("z.", "6. Layers (z-index)", "Native `dialog`/`popover` use the top layer; these order fixed and JS-positioned layers. "
          "Anything that opens from a dialog (dropdown, popover, tooltip) sits above `modal`.")
    scale("breakpoint.", "7. Breakpoints", "CSS variables can't be used in @media: use `dist/tokens.scss` (`@include up(md)`) or the literal values.")
    scale("motion.", "8. Motion")
    motion = cfg.get("motion", {})
    if motion.get("bans") or motion.get("moments"):
        md += [""] + [f"- **Banned:** {b}" for b in motion.get("bans", [])] + [f"- **Moment:** {m}" for m in motion.get("moments", [])]
    md += ["", "Reduced motion: `prefers-reduced-motion` or `[data-reduced-motion]` on `<html>` neutralizes transitions and animations."]
    report = coverage(root, cfg)
    done, total = summarize(report)
    md += ["", f"## 9. Components ({done}/{total} ready, tier {cfg['tier']})", ""]
    names = {c["id"]: c["name"] for c in MANIFEST["categories"]}
    for cid in names:
        rows = [r for r in report if r["category"] == cid]
        if rows:
            md.append(f"- **{names[cid]}:** " + ", ".join(f"{r['name']}{'' if r['done'] else ' (missing)'}" for r in rows))
    md += ["", "## 10. Rules every consumer follows", "",
           "- Use semantic tokens (`--color-*`, `--space-*`, …), never primitives (`--color-blue-600`) or raw values.",
           "- Use native elements first (`button`, `a[href]`, `dialog`, `details`, `input` types); ARIA only to fill gaps.",
           "- Every control has a visible label; icon-only controls have an accessible name and a tooltip.",
           "- Focus is always visible; overlays return focus to their trigger; nothing is conveyed by color alone.",
           "- Logical properties only (`margin-inline-start`), so RTL works; hit targets ≥ 24px.",
           "- Forms validate on submit/blur with an error summary + inline messages; never disable paste.",
           "", "## 11. Consuming", "",
           "```html", '<link rel="stylesheet" href="dist/ds.css">', '<script type="module">import { initTheme } from "./js/theme.js"; initTheme();</script>', "```",
           "", "Build-time tokens: `dist/tokens.scss`, `dist/tokens.json`. Source tokens (DTCG): `tokens/`."]
    if cfg.get("decisions"):
        md += ["", "## 12. Decisions", ""] + [f"- **{x.get('id', '')} {x.get('title', '')}** — {x.get('decision', '')}. {x.get('consequences', '')}" for x in cfg["decisions"]]
    if cfg.get("design_notes"):
        md += ["", "## Notes", "", cfg["design_notes"]]
    (root / "DESIGN.md").write_text("\n".join(md) + "\n")
    print(f"wrote {root / 'DESIGN.md'}")


def cmd_package(a):
    root = Path(a.dir)
    cfg = load_cfg(root)
    pj = root / "package.json"
    pkg = json.loads(pj.read_text()) if pj.exists() else {}
    slug = re.sub(r"[^a-z0-9]+", "-", cfg["name"].lower()).strip("-") or "design-system"
    pkg.setdefault("name", cfg.get("package_name") or f"{slug}-design-system")
    if pkg["name"].endswith("-design-system") and cfg.get("package_name"):
        pkg["name"] = cfg["package_name"]
    pkg.setdefault("version", cfg.get("version", "0.1.0"))
    pkg.setdefault("description", f"{cfg['name']} design system — tokens, CSS components and docs")
    pkg.pop("private", None)
    pkg["type"] = "module"
    pkg["style"] = "dist/ds.css"
    pkg["exports"] = {".": "./dist/ds.css", "./ds.css": "./dist/ds.css", "./tokens.css": "./dist/tokens.css",
                      "./tokens.json": "./dist/tokens.json", "./tokens.scss": "./dist/tokens.scss",
                      "./css/*": "./css/*", "./js/*": "./js/*", "./tokens/*": "./tokens/*", "./fonts/*": "./fonts/*",
                      "./DESIGN.md": "./DESIGN.md", "./package.json": "./package.json"}
    pkg["files"] = [f for f in ("dist/ds.css", "dist/tokens.css", "dist/tokens.json", "dist/tokens.scss", "css", "js", "tokens", "fonts", "DESIGN.md")
                    if (root / f.split("/")[0]).exists() or f == "DESIGN.md"]
    pkg["sideEffects"] = ["*.css"]
    pkg.setdefault("publishConfig", {"access": "public"})
    pkg.setdefault("scripts", {})["prepack"] = "python3 tools/ds/scripts/ds.py build . && python3 tools/ds/scripts/ds.py design-md ." \
        if (root / "tools" / "ds").exists() else "echo 'run ds.py build + design-md before packing'"
    pj.write_text(json.dumps(pkg, indent=2) + "\n")
    cmd_design_md(a)
    print(f"package.json ready: {pkg['name']}@{pkg['version']} — exports dist/ds.css, tokens (css/json/scss), css/*, js/*")


def vendor_tools(root):
    """Copy ds.py + manifest + templates into <root>/tools/ds so CI and teammates don't need the skill installed."""
    dst = Path(root) / "tools" / "ds"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(SKILL / "scripts", dst / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(SKILL / "assets", dst / "assets")
    return dst


def cmd_ci(a):
    root = Path(a.dir).resolve()
    load_cfg(root)
    vendor_tools(root)
    try:
        import subprocess
        repo = Path(subprocess.check_output(["git", "-C", str(root), "rev-parse", "--show-toplevel"], text=True).strip())
    except Exception:  # noqa: BLE001 - not a git repo
        repo = root
    rel = os.path.relpath(root, repo)
    tpl = (SKILL / "assets" / "templates" / "ci" / ("github-actions.yml" if a.provider == "github" else "gitlab-ci.yml")).read_text()
    out = repo / (".github/workflows/design-system.yml" if a.provider == "github" else ".gitlab-ci.yml")
    if out.exists() and not a.force:
        sys.exit(f"{out} exists — merge manually or pass --force")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(tpl.replace("__DIR__", rel))
    pj = root / "package.json"
    if pj.exists():
        pkg = json.loads(pj.read_text())
        pkg.setdefault("scripts", {})["stories"] = "python3 tools/ds/scripts/ds.py storybook ."
        pj.write_text(json.dumps(pkg, indent=2) + "\n")
    print(f"wrote {out} and vendored tools to {root / 'tools/ds'}.\n"
          "Commit package-lock.json (run npm install once). Secrets: NPM_TOKEN to publish; GitHub: enable Pages → 'GitHub Actions'.")


# ---------- hooks ----------
def read_hook_input():
    try:
        return json.load(sys.stdin)
    except Exception:  # noqa: BLE001 - hooks must never crash the session
        return {}


def hook_post_edit():
    data = read_hook_input()
    fp = (data.get("tool_input") or {}).get("file_path") or ""
    if not fp or not fp.endswith((".css", ".html", ".json")):
        return
    root = find_root(Path(fp).parent, depth=0)
    if not root:
        return
    msgs = []
    try:
        cfg = load_cfg(root)
        if fp.endswith(".json") and "/tokens/" in fp:
            errs, _ = check_tokens(root, cfg)
            if not errs:
                build_tokens(root)
                msgs.append("tokens rebuilt → dist/tokens.css")
            msgs += [f"token error: {e}" for e in errs[:15]]
        else:
            msgs += lint_file(fp)[:20]
            if fp.endswith(".html") and ("/components/" in fp or "/patterns/" in fp):
                stem = Path(fp).stem
                rows = [r for r in coverage(root, cfg) if r["file"] == stem and not r["done"]]
                for r in rows:
                    msgs.append(f"{r['id']} still missing: {'; '.join(r['missing'][:10])}")
    except Exception as e:  # noqa: BLE001
        msgs.append(f"ds hook error: {e}")
    if msgs:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                                 "additionalContext": "html-design-system checks:\n- " + "\n- ".join(msgs)}}))


def hook_stop():
    data = read_hook_input()
    if data.get("stop_hook_active"):
        return
    root = find_root(data.get("cwd") or os.getcwd())
    if not root:
        return
    try:
        cfg = load_cfg(root)
    except Exception:  # noqa: BLE001
        return
    if cfg.get("phase") != "build" or cfg.get("gate", "block") == "off":
        return
    report = coverage(root, cfg)
    todo = [r for r in report if not r["done"]]
    errs, _ = check_tokens(root, cfg)
    if not todo and not errs:
        return
    done, total = summarize(report)
    files = []
    for r in todo:
        if r["file"] not in files:
            files.append(r["file"])
    reason = (f"Design system '{cfg['name']}' is in build phase but incomplete: {done}/{total} components ready, "
              f"{len(errs)} token errors. Next files to build: {', '.join(files[:8])}. "
              f"Continue building (run `python3 {SKILL}/scripts/ds.py plan {root}`), or if you must stop to ask the user "
              f"something, set `ds.py phase {root} plan` first.")
    if cfg.get("gate", "block") == "warn":
        print(json.dumps({"systemMessage": reason}))
    else:
        print(json.dumps({"decision": "block", "reason": reason}))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("init"); p.add_argument("dir"); p.add_argument("--name"); p.add_argument("--force", action="store_true")
    p.add_argument("--tier", choices=TIERS, default="enterprise")
    p = sp.add_parser("audit"); p.add_argument("path")
    p = sp.add_parser("build"); p.add_argument("dir")
    p = sp.add_parser("check"); p.add_argument("dir"); p.add_argument("--strict", action="store_true")
    p = sp.add_parser("coverage"); p.add_argument("dir"); p.add_argument("--json", action="store_true"); p.add_argument("--all", action="store_true")
    p = sp.add_parser("plan"); p.add_argument("dir")
    p = sp.add_parser("phase"); p.add_argument("dir"); p.add_argument("phase", choices=["discover", "decide", "plan", "build", "done"])
    p = sp.add_parser("status"); p.add_argument("path", nargs="?")
    p = sp.add_parser("storybook"); p.add_argument("dir"); p.add_argument("--force", action="store_true")
    p = sp.add_parser("serve"); p.add_argument("dir"); p.add_argument("--port", type=int, default=8000)
    p = sp.add_parser("design-md"); p.add_argument("dir")
    p = sp.add_parser("package"); p.add_argument("dir")
    p = sp.add_parser("ci"); p.add_argument("dir"); p.add_argument("--provider", choices=["github", "gitlab"], default="github")
    p.add_argument("--force", action="store_true")
    sp.add_parser("hook-post-edit"); sp.add_parser("hook-stop")
    a = ap.parse_args()
    if a.cmd == "hook-post-edit":
        return hook_post_edit()
    if a.cmd == "hook-stop":
        return hook_stop()
    {"init": cmd_init, "audit": cmd_audit, "build": cmd_build, "check": cmd_check,
     "coverage": cmd_coverage, "plan": cmd_plan, "phase": cmd_phase, "status": cmd_status,
     "storybook": cmd_storybook, "serve": cmd_serve, "design-md": cmd_design_md, "package": cmd_package, "ci": cmd_ci}[a.cmd](a)


if __name__ == "__main__":
    main()
