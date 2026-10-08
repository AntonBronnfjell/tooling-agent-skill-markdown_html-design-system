#!/usr/bin/env python3
"""html-design-system CLI. Stdlib only.

  ds.py init <dir> [--name N] [--tier core|standard|enterprise] [--force]
  ds.py audit <path>                 inventory an existing codebase's de-facto design system
  ds.py build <dir>                  tokens -> dist/tokens.css, bundle dist/ds.css, docs index.html
  ds.py check <dir> [--strict]       validate tokens + contrast, lint CSS/HTML, coverage summary
  ds.py coverage <dir> [--json] [--all]
  ds.py plan <dir>                   ordered build queue (markdown checklist) of what is missing
  ds.py phase <dir> <discover|decide|plan|build|done>
  ds.py status [path]                one-paragraph state of the nearest design system (for context injection)
  ds.py hook-post-edit | hook-stop   Claude Code hook entry points (read JSON on stdin)
"""
import argparse, json, os, re, shutil, sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
MANIFEST = json.loads((SKILL / "assets" / "manifest.json").read_text())
TIERS = ["core", "standard", "enterprise"]
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "vendor", "graphify-out", "__pycache__"}


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
        body = decls(merged, list(tflat))
        if name == "dark":
            css.append(f"@media (prefers-color-scheme: dark) {{\n  :root:not([data-theme]) {{\n{body}\n  }}\n}}")
        if name == "high-contrast":
            css.append(f"@media (prefers-contrast: more) {{\n  :root:not([data-theme]) {{\n{body}\n  }}\n}}")
        css.append(f':root[data-theme="{name}"] {{\n{body}\n}}')
    if "light" not in themes:
        css.append(':root[data-theme="light"] { color-scheme: light; }')
    out = Path(root) / "dist" / "tokens.css"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n\n".join(css) + "\n")
    return out, flat, themes


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
                     ("component.html", "docs/_component-template.html")]:
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
    print("Build one *file* (page + css) at a time; it closes every component sharing it.\n")
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
    sp.add_parser("hook-post-edit"); sp.add_parser("hook-stop")
    a = ap.parse_args()
    if a.cmd == "hook-post-edit":
        return hook_post_edit()
    if a.cmd == "hook-stop":
        return hook_stop()
    {"init": cmd_init, "audit": cmd_audit, "build": cmd_build, "check": cmd_check,
     "coverage": cmd_coverage, "plan": cmd_plan, "phase": cmd_phase, "status": cmd_status}[a.cmd](a)


if __name__ == "__main__":
    main()
