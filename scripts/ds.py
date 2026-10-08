#!/usr/bin/env python3
"""html-design-system CLI. Stdlib only.

  ds.py init <dir> [--name N] [--tier core|standard|enterprise] [--scopes product,marketing] [--force]
  ds.py audit [path] [--url URL] [--json]   inventory the de-facto design system of a codebase or a live site
  ds.py build <dir>                  tokens -> dist/tokens.css, bundle dist/ds.css, docs index.html
  ds.py check <dir> [--strict]       validate tokens + contrast, lint CSS/HTML, coverage summary
  ds.py coverage <dir> [--json] [--all]
  ds.py plan <dir>                   ordered build queue (markdown checklist) of what is missing
  ds.py phase <dir> <discover|decide|plan|build|done>
  ds.py storybook <dir> [--renderer html|server] [--server-url URL] [--force]
                                     standalone Storybook from the component pages (html-vite, or @storybook/server
                                     so PHP/Python/Ruby/Java/.NET backends render their own templates)
  ds.py serve <dir> [--port 8000]    build and preview the docs site with no dependencies
  ds.py design-md <dir>              write DESIGN.md: the one-file contract (themes, type, scales, rules, inventory)
  ds.py package <dir>                npm-ready package.json (exports css/tokens/js, files, sideEffects)
  ds.py ci <dir> [--provider github|gitlab]   pipeline: check -> Storybook to Pages -> idempotent npm publish
  ds.py detect [project] [--json]    read an existing project (stack, monorepo, styles, Storybook, CI) and propose a
                                     non-conflicting location + sync targets — writes nothing
  ds.py migrate-colors <dir>         convert legacy hex-string color tokens to DTCG 2025.10 color objects
  ds.py email <dir> [--strict]       render email/src templates with literal token values (light + dark) into dist/email
                                     and check client safety (tables, no var()/flex/rem, alt, lang, size, plain text)
  ds.py llms <dir>                   llms.txt, llms-full.txt, llms/<file>.md per component, dist/ds-index.json (for agents)
  ds.py mcp <dir>                    MCP server (stdio, stdlib) so any agent can query components, tokens and DESIGN.md
  ds.py palette <hex> [--name N] [--mode curve|contrast] [--dir D] [--primary] [--brand B]
                                     OKLCH ramp (50–950) from one color + contrast-checked primary mapping per theme
  ds.py scale type|space [--dir D] [--min-size/--max-size/--min-ratio/--max-ratio/--min-vw/--max-vw]
                                     Utopia fluid type/space scales as clamp() tokens
  ds.py export <dir> [--target tailwind,shadcn,figma,ios,android,compose,flutter|all]
                                     framework/platform outputs in dist/exports (no dependencies)
  ds.py icons <svg-dir> <dir>        optimized SVG sprite (currentColor) + icon gallery page
  ds.py taste [path] [--strict]      lint for the generic "AI look" (purple gradients, glass, buzzwords, emoji UI, …)
  ds.py sync <dir>                   copy built CSS/tokens/js into the host project's own folders (owned files only)
  Global: --dry-run (print every planned write) · --force-all (overwrite even files you created or edited)
  Files ds.py didn't create, and files you edited after it created them, are never overwritten (ledger: .ds-owned.json)
  ds.py status [path]                one-paragraph state of the nearest design system (for context injection)
  ds.py hook-post-edit | hook-stop   Claude Code hook entry points (read JSON on stdin)
"""
import argparse, atexit, hashlib, json, os, re, shutil, subprocess, sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
MANIFEST = json.loads((SKILL / "assets" / "manifest.json").read_text(encoding="utf-8"))
TIERS = ["core", "standard", "enterprise"]
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "vendor", "graphify-out", "__pycache__", "storybook-static"}


# ---------- safe writes: never clobber files ds.py didn't create ----------
# Every file ds.py writes is recorded in <ds root>/.ds-owned.json with its hash. A path that already exists
# and is not in the ledger belongs to the user/project and is never overwritten (unless --force). Files that
# ds.py *owns* but the user edited are also kept for "owned" writes (templates, config, CI); "generated"
# outputs (dist/, stories/, index.html) are rebuilt. --dry-run prints every planned write instead.
STATE = {"dry_run": False, "force": False, "root": None, "ledger": None, "dirty": False, "skipped": []}
LEDGER = ".ds-owned.json"
LEDGER_SKIP = {"node_modules", ".git", "storybook-static", "__pycache__"}


def _sha(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode()).hexdigest()[:16]


def use_root(root):
    """Bind writes to a design-system root and load (or bootstrap) its ownership ledger."""
    root = Path(root).resolve()
    if STATE["root"] == root:
        return root
    STATE.update(root=root, ledger=None, dirty=False)
    lp = root / LEDGER
    if lp.exists():
        STATE["ledger"] = json.loads(lp.read_text(encoding="utf-8")).get("files", {})
    else:
        STATE["ledger"] = {}
        if (root / "ds.config.json").exists():
            # Systems created before the ledger existed: everything inside the ds root was made by the skill.
            for dp, dns, fns in os.walk(root):
                dns[:] = [d for d in dns if d not in LEDGER_SKIP]
                for fn in fns:
                    f = Path(dp) / fn
                    if fn != LEDGER:
                        STATE["ledger"][os.path.relpath(f, root)] = _sha(f.read_bytes())
            STATE["dirty"] = True
    return root


def _save_ledger():
    if STATE["root"] is not None and STATE["dirty"] and not STATE["dry_run"] and STATE["root"].exists():
        (STATE["root"] / LEDGER).write_text(json.dumps({"version": 1, "note": "Files created by ds.py (html-design-system). "
                                                        "ds.py never overwrites files missing from this list.",
                                                        "files": dict(sorted(STATE["ledger"].items()))}, indent=1) + "\n", encoding="utf-8")


atexit.register(_save_ledger)


def _rel(path):
    return os.path.relpath(Path(path).resolve(), STATE["root"]) if STATE["root"] else str(path)


def safe_write(path, data, kind="generated"):
    """Write text/bytes to path unless that would clobber a file ds.py doesn't own. Returns True if written."""
    path = Path(path)
    key, new = _rel(path), _sha(data)
    if path.exists():
        cur = _sha(path.read_bytes())
        if cur == new:
            STATE["ledger"][key] = new
            return False
        known = STATE["ledger"].get(key) if STATE["ledger"] is not None else None
        if not STATE["force"]:
            if known is None:
                return _skip(path, "exists and was not created by ds.py")
            if kind == "owned" and known != cur:
                return _skip(path, "was edited after ds.py created it")
    if STATE["dry_run"]:
        print(f"[dry-run] {'update' if path.exists() else 'create'} {key}")
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    # Bytes, not write_text: no \r\n translation on Windows, so the ledger hash matches the file exactly.
    path.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))
    if STATE["ledger"] is not None:
        STATE["ledger"][key] = new
        STATE["dirty"] = True
    return True


def safe_copy(src, dst, kind="generated"):
    return safe_write(dst, Path(src).read_bytes(), kind)


def safe_remove_owned(directory):
    """Delete only ledger-owned files under directory (used to regenerate stories/)."""
    directory = Path(directory)
    if not directory.exists():
        return
    for f in sorted(directory.rglob("*"), reverse=True):
        if f.is_file() and _rel(f) in (STATE["ledger"] or {}):
            if STATE["dry_run"]:
                print(f"[dry-run] remove {_rel(f)}")
            else:
                f.unlink()
                STATE["ledger"].pop(_rel(f), None)
                STATE["dirty"] = True
        elif f.is_dir() and not any(f.iterdir()) and not STATE["dry_run"]:
            f.rmdir()


def merge_json(path, update, describe):
    """Additive merge into a JSON file. Files ds.py doesn't own are left alone; the snippet is printed instead."""
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    before = json.dumps(data, sort_keys=True)
    update(data)
    if path.exists() and _rel(path) not in (STATE["ledger"] or {}) and not STATE["force"]:
        if json.dumps(data, sort_keys=True) != before:
            _skip(path, "belongs to your project — merge this yourself")
            print(f"  suggested {describe} for {_rel(path)}:\n" + json.dumps(data, indent=2)[:1500], file=sys.stderr)
        return False
    return safe_write(path, json.dumps(data, indent=2) + "\n", kind="generated")


def append_lines(path, lines):
    """Append missing lines (e.g. .gitignore). Never edits a file ds.py doesn't own; prints the lines instead."""
    path = Path(path)
    cur = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    missing = [x for x in lines if x not in cur]
    if not missing:
        return False
    if path.exists() and _rel(path) not in (STATE["ledger"] or {}) and not STATE["force"]:
        return _skip(path, "belongs to your project — add these lines yourself: " + ", ".join(missing))
    return safe_write(path, "\n".join(cur + missing) + "\n")


def _skip(path, why):
    STATE["skipped"].append(f"{_rel(path)}: {why}")
    print(f"skip {_rel(path)} — {why} (kept yours; --force-all overwrites)", file=sys.stderr)
    return False


# ---------- helpers ----------
def load_cfg(root):
    cfgp = Path(root) / "ds.config.json"
    if not cfgp.exists():
        sys.exit(f"No design system at {root} (no ds.config.json). Run `ds.py detect` to find or place one, then `ds.py init`.")
    use_root(root)
    return json.loads(cfgp.read_text(encoding="utf-8"))


def save_cfg(root, cfg):
    use_root(root)
    safe_write(Path(root) / "ds.config.json", json.dumps(cfg, indent=2) + "\n", kind="generated")


def in_tier(item_tier, cfg_tier):
    return TIERS.index(item_tier) <= TIERS.index(cfg_tier)


PAGE_CATS = {c["id"] for c in MANIFEST["categories"] if c.get("page_dir") == "patterns"}


def page_dir(cat_id):
    """Full-page categories (patterns, marketing pages) live in patterns/; everything else in components/."""
    return "patterns" if cat_id in PAGE_CATS else "components"


def components(cfg=None, all_tiers=False):
    scopes = set((cfg or {}).get("scopes") or ["product"])
    for cat in MANIFEST["categories"]:
        if cfg is not None and cat.get("scope", "product") not in scopes:
            continue  # e.g. marketing sections only when "marketing" is in ds.config.json scopes
        for c in cat["components"]:
            if all_tiers or cfg is None or in_tier(c["tier"], cfg["tier"]):
                yield cat, c


def page_path(root, cat, c):
    sub = page_dir(cat["id"])
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


# ---------- DTCG 2025.10 colors: {"colorSpace", "components", "alpha"?, "hex"?} ----------
def _hex_from_rgb(rgb, alpha=1):
    h = "#" + "".join(f"{round(max(0, min(1, c)) * 255):02x}" for c in rgb)
    return h + (f"{round(alpha * 255):02x}" if alpha < 1 else "")


def _num(x):
    return f"{round(x, 4):g}"


def color_obj_to_css(v):
    cs, comps, alpha = v.get("colorSpace", "srgb"), v.get("components", []), v.get("alpha", 1)
    a = f" / {_num(alpha)}" if alpha < 1 else ""
    if cs == "srgb":
        return _hex_from_rgb(comps, alpha) if len(comps) == 3 and all(isinstance(c, (int, float)) for c in comps) else v.get("hex", "#000000")
    if cs in ("oklch", "oklab", "lab", "lch", "hwb"):
        return f"{cs}({' '.join(_num(c) if isinstance(c, (int, float)) else 'none' for c in comps)}{a})"
    if cs == "hsl":
        h, s_, l_ = comps
        return f"hsl({_num(h)} {_num(s_)}% {_num(l_)}%{a})"
    return f"color({cs} {' '.join(_num(c) for c in comps)}{a})"   # display-p3, rec2020, srgb-linear, xyz-d65, ...


def _oklch_to_srgb(l_, c, h):
    import math
    a_, b_ = c * math.cos(math.radians(h or 0)), c * math.sin(math.radians(h or 0))
    l1 = (l_ + 0.3963377774 * a_ + 0.2158037573 * b_) ** 3
    m1 = (l_ - 0.1055613458 * a_ - 0.0638541728 * b_) ** 3
    s1 = (l_ - 0.0894841775 * a_ - 1.2914855480 * b_) ** 3
    lin = (4.0767416621 * l1 - 3.3077115913 * m1 + 0.2309699292 * s1,
           -1.2684380046 * l1 + 2.6097574011 * m1 - 0.3413193965 * s1,
           -0.0041960863 * l1 - 0.7034186147 * m1 + 1.7076147010 * s1)
    return tuple(max(0, min(1, 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055)) for x in lin)


def _p3_to_srgb(r, g, b):
    dec = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in (r, g, b)]
    m = ((1.2249, -0.2247, 0.0), (-0.0420, 1.0419, 0.0), (-0.0197, -0.0786, 1.0979))   # linear P3 -> linear sRGB
    lin = [sum(m[i][j] * dec[j] for j in range(3)) for i in range(3)]
    return tuple(max(0, min(1, 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055)) for x in lin)


def color_rgb(v):
    """sRGB 0..1 tuple for contrast checks from a DTCG color object or a legacy hex string; None if unknown."""
    if isinstance(v, str):
        return hex_rgb(v) if v.startswith("#") else None
    if not isinstance(v, dict):
        return None
    cs, comps = v.get("colorSpace"), v.get("components") or []
    try:
        if cs == "srgb":
            return tuple(float(c) for c in comps[:3])
        if cs == "oklch":
            return _oklch_to_srgb(*comps[:3])
        if cs == "display-p3":
            return _p3_to_srgb(*comps[:3])
    except (TypeError, ValueError):
        pass
    return hex_rgb(v["hex"]) if v.get("hex") else None


def resolve_raw(key, flat, depth=0):
    """Follow a pure alias chain ("{a.b}") to the underlying $value."""
    v = flat[key]["value"]
    if isinstance(v, str) and depth < 20:
        m = re.fullmatch(r"\{([^{}]+)\}", v.strip())
        if m and m.group(1) in flat:
            return resolve_raw(m.group(1), flat, depth + 1)
    return v


def hex_to_color_obj(h):
    rgb = hex_rgb(h)
    if rgb is None:
        return h
    hx = h.strip().lstrip("#").lower()
    alpha = int(hx[6:8], 16) / 255 if len(hx) == 8 else 1
    obj = {"colorSpace": "srgb", "components": [round(c, 4) for c in rgb], "hex": _hex_from_rgb(rgb)}
    if alpha < 1:
        obj["alpha"] = round(alpha, 4)
    return obj


def migrate_colors_tree(tree, inherited=None):
    """Convert legacy hex-string color $values in a token tree to DTCG 2025.10 objects (in place). Returns count."""
    n, t = 0, tree.get("$type", inherited) if isinstance(tree, dict) else inherited
    for k, v in (tree.items() if isinstance(tree, dict) else []):
        if k.startswith("$") or not isinstance(v, dict):
            continue
        if "$value" in v:
            if v.get("$type", t) == "color" and isinstance(v["$value"], str) and v["$value"].startswith("#"):
                v["$value"] = hex_to_color_obj(v["$value"])
                n += 1
        else:
            n += migrate_colors_tree(v, t)
    return n


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
        if typ == "gradient":   # DTCG: [{color, position 0..1}]; angle via $extensions is not portable, so 90deg default
            stops = ", ".join(f"{to_css(st['color'], 'color', flat, as_var)} {_num(st.get('position', 0) * 100)}%" for st in value)
            return f"linear-gradient(90deg, {stops})"
        return " ".join(to_css(v, typ, flat, as_var) for v in value)
    if isinstance(value, dict):
        if "unit" in value and "value" in value:
            return f"{value['value']}{value['unit']}"
        if "colorSpace" in value and "components" in value:
            return color_obj_to_css(value)
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


def load_brands(root):
    """tokens/brands/<brand>.json: brand overrides (usually primitives: ramps, fonts, radius)."""
    d = Path(root) / "tokens" / "brands"
    return {p_.stem: json.loads(p_.read_text(encoding="utf-8")) for p_ in sorted(d.glob("*.json"))} if d.exists() else {}


def dependents(flat, changed):
    """Keys whose value (transitively) references any changed key — they must be redeclared next to an override."""
    out, frontier = set(), set(changed)
    while frontier:
        nxt = set()
        for k, v in flat.items():
            if k in out or k in changed:
                continue
            blob = json.dumps(v["value"])
            if any("{" + c + "}" in blob for c in frontier):
                nxt.add(k)
        out |= nxt
        frontier = nxt
    return out


def load_tokens(root):
    root = Path(root)
    t = root / "tokens"
    base = {}
    files = [t / n for n in ("primitive.json", "semantic.json", "component.json")]
    files += sorted((t / "components").glob("*.json"))  # one file per component: parallel-safe
    files += sorted((t / "scopes").glob("*.json"))      # tokens added by optional scopes (ai, commerce, ...)
    files += sorted((t / "scales").glob("*.json"))      # ds.py scale (fluid type/space)
    files += sorted((t / "palettes").glob("*.json"))    # ds.py palette (ramps; may remap primary/link/focus)
    for f in files:
        if f.exists():
            try:
                base = deep_merge(base, json.loads(f.read_text(encoding="utf-8")))
            except json.JSONDecodeError as e:
                raise ValueError(f"{f.relative_to(root)}: invalid JSON ({e})")
    themes = {}
    # themes/dark.json is the theme; themes/dark.<scope>.json files are add-ons merged into it.
    for p in sorted((t / "themes").glob("*.json"), key=lambda p: (p.name.count("."), p.name)) if (t / "themes").exists() else []:
        name = p.name.split(".")[0]
        themes[name] = deep_merge(themes.get(name, {}), json.loads(p.read_text(encoding="utf-8")))
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
    for bname, btree in load_brands(root).items():
        bflat = flatten(btree)
        merged = {**flat, **bflat}
        keys = list(bflat) + sorted(dependents(merged, set(bflat)))
        css.append(f'/* Brand "{bname}": set data-brand on <html> (same element as data-theme). */\n'
                   f'[data-brand="{bname}"], .brand-{bname} {{\n' + decls(merged, keys) + "\n}")
    aliases = deprecated_aliases(base, flat)
    if aliases:
        css.append("/* Deprecated aliases — removed in the next major version. */\n:root {\n" + aliases + "\n}")
    out = Path(root) / "dist" / "tokens.css"
    safe_write(out, "\n\n".join(css) + "\n")
    write_token_modules(root, flat)
    write_resolver(root, themes)
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
    safe_write(dist / "tokens.json", json.dumps(resolved, indent=1) + "\n")
    scss = ["// Generated by ds.py build — static values (default theme). Use CSS vars at runtime; these are for",
            "// media queries and build-time math only."]
    scss += [f"${k.replace('.', '-')}: {v};" for k, v in resolved.items()]
    bps = {k.split(".", 1)[1]: v for k, v in resolved.items() if k.startswith("breakpoint.")}
    if bps:
        scss.append("$breakpoints: (" + ", ".join(f'"{n}": {v}' for n, v in bps.items()) + ");")
        scss.append("@mixin up($bp) { @media (min-width: map-get($breakpoints, $bp)) { @content; } }")
        scss.append("@mixin down($bp) { @media (max-width: calc(map-get($breakpoints, $bp) - 0.02px)) { @content; } }")
    safe_write(dist / "tokens.scss", "\n".join(scss) + "\n")


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
    legacy = [k for k, v in flat.items() if v["type"] == "color" and isinstance(v["value"], str) and v["value"].startswith("#")]
    if legacy:
        warns.append(f"{len(legacy)} color tokens use hex strings — not DTCG 2025.10 (needs {{colorSpace, components}}); "
                     f"run `ds.py migrate-colors <dir>` (e.g. {legacy[0]})")
    groups = {k.split(".")[0] for k in flat}
    need = [g for t in TIERS if in_tier(t, cfg["tier"]) for g in MANIFEST["token_groups_required"][t]]
    for g in need:
        if g not in groups:
            errs.append(f"missing token group '{g}' (tier {cfg['tier']})")
    need_themes = [th for t in TIERS if in_tier(t, cfg["tier"]) for th in MANIFEST["themes_required"][t]]
    for th in need_themes:
        if th != "light" and th not in themes:
            errs.append(f"missing theme tokens/themes/{th}.json")
    brand_sets = [(None, flat)] + [(b, {**flat, **flatten(t)}) for b, t in load_brands(root).items()]
    combos = [(b, name, (bf if name == "light" else {**bf, **flatten(themes[name])})) for b, bf in brand_sets for name in ["light", *themes]]
    for brand, name, merged in combos:
        if brand:
            name = f"{brand}/{name}"
        for fg, bg, minimum in cfg.get("contrast_pairs", []):
            if fg not in merged or bg not in merged:
                errs.append(f"contrast pair {fg} / {bg}: token missing")
                continue
            a = color_rgb(resolve_raw(fg, merged))
            b = color_rgb(resolve_raw(bg, merged))
            if not a or not b:
                warns.append(f"[{name}] {fg} / {bg}: color space without a hex fallback, contrast not checked")
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
    (re.compile(r"on\w+=\"[^\"]*\.(showModal|show|close|showPopover|hidePopover|togglePopover)\(", re.I),
     "inline JS opening/closing a dialog or popover — use invoker commands: commandfor=\"id\" command=\"show-modal|close|toggle-popover\""),
]
ICON_BTN = re.compile(r"<button(?![^>]*aria-label)[^>]*>\s*<svg[^>]*>.*?</svg>\s*</button>", re.I | re.S)


def lint_file(path):
    path = Path(path)
    issues = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return issues
    if path.suffix == ".css" and "email" in path.stem:
        return issues   # email CSS must use literal values and !important (client quirks) — checked by `ds.py email`
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
        base_css = next((pp / "css" / "base.css" for pp in path.parents if (pp / "ds.config.json").exists()), None)
        layered = base_css is not None and "@layer" in _read(base_css)
        want = "patterns" if "patterns" in path.parts else "components"
        if layered and path.parent.name in ("components", "patterns") and not re.search(rf"@layer\s+{want}\b", text):
            issues.append(f"{path.name}: wrap rules in `@layer {want} {{ … }}` (cascade layers; see references/css-architecture.md)")
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
            cache[page] = page.read_text(encoding="utf-8", errors="ignore") if page.exists() else None
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
        sys.exit(f"{root}/ds.config.json exists. --force re-runs init: missing templates are restored, files you "
                 "edited are kept (only the global --force-all overwrites them).")
    if root.exists() and any(root.iterdir()) and not (root / "ds.config.json").exists() and not a.adopt:
        sys.exit(f"{root} already has files that aren't a design system. Pick another folder (`ds.py detect` suggests one) "
                 "or pass --adopt to add the system alongside them — existing files are never overwritten.")
    use_root(root)
    tpl = SKILL / "assets" / "templates"
    for sub in ("tokens/themes", "tokens/components", "css/components", "css/patterns", "components", "patterns", "docs", "dist", "js"):
        if not STATE["dry_run"]:
            (root / sub).mkdir(parents=True, exist_ok=True)
    for src, dst in [("tokens/primitive.json", "tokens/primitive.json"), ("tokens/semantic.json", "tokens/semantic.json"),
                     ("tokens/component.json", "tokens/component.json"), ("tokens/themes/dark.json", "tokens/themes/dark.json"),
                     ("tokens/themes/high-contrast.json", "tokens/themes/high-contrast.json"),
                     ("base.css", "css/base.css"), ("docs.css", "docs/docs.css"), ("docs.js", "docs/docs.js"),
                     ("component.html", "docs/_component-template.html"),
                     ("theme.js", "js/theme.js")]:
        safe_copy(tpl / src, root / dst, kind="owned")
    cfg = json.loads((tpl / "ds.config.json").read_text(encoding="utf-8"))
    if (root / "ds.config.json").exists():   # re-init: keep every decision already recorded
        cfg.update(json.loads((root / "ds.config.json").read_text(encoding="utf-8")))
    if a.name:
        cfg["name"] = a.name
    if a.tier:
        cfg["tier"] = a.tier
    if a.scopes:
        cfg["scopes"] = [x.strip() for x in a.scopes.split(",") if x.strip()]
    bad = [x for x in cfg["scopes"] if x not in MANIFEST["scopes"]]
    if bad:
        sys.exit(f"unknown scope(s) {bad}; known: {list(MANIFEST['scopes'])}")
    for scope in cfg.get("scopes", []):
        sdir = SKILL / "assets" / "templates" / "scopes" / scope
        if not sdir.exists():
            continue
        if (sdir / "tokens.json").exists():
            safe_copy(sdir / "tokens.json", root / "tokens" / "scopes" / f"{scope}.json", kind="owned")
        for tf in sorted((sdir / "src").glob("*")) if (sdir / "src").exists() else []:
            safe_copy(tf, root / "email" / "src" / tf.name, kind="owned")
        for th in sorted((sdir / "themes").glob("*.json")) if (sdir / "themes").exists() else []:
            safe_copy(th, root / "tokens" / "themes" / f"{th.stem}.{scope}.json", kind="owned")
        if (sdir / "contrast_pairs.json").exists():
            pairs = cfg.setdefault("contrast_pairs", [])
            pairs += [x for x in json.loads((sdir / "contrast_pairs.json").read_text(encoding="utf-8")) if x not in pairs]
    if a.project:
        info = detect_project(a.project)
        cfg["project"] = {"root": os.path.relpath(Path(a.project).resolve(), root.resolve()),
                          "stacks": info["stacks"], "sync": info["recommended"]["sync"],
                          "storybook": info["recommended"]["storybook"], "ci": info["recommended"]["ci"]}
    save_cfg(root, cfg)
    if STATE["dry_run"]:
        print(f"[dry-run] would initialize '{cfg['name']}' in {root}; nothing written")
        return
    build_tokens(root)
    print(f"Initialized design system '{cfg['name']}' (tier {cfg['tier']}) in {root}")
    print("Next: fill ds.config.json brief/direction, edit tokens/*.json, then `ds.py build` and `ds.py plan`.")


AUDIT_PATTERNS = {
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


def inventory(texts):
    """Count design values across text blobs (files or fetched pages)."""
    counts = {k: {} for k in AUDIT_PATTERNS}
    for text in texts:
        for k, rx in AUDIT_PATTERNS.items():
            for m in rx.finditer(text):
                v = (m.group(1) if rx.groups else m.group(0)).strip()[:80]
                counts[k][v] = counts[k].get(v, 0) + 1
    return counts


def fetch_site(url, max_files=20, max_bytes=2_000_000):
    """Fetch a page and its stylesheets (read-only, no cookies). Returns [(source, text)]."""
    import urllib.parse
    import urllib.request

    def get(u):
        req = urllib.request.Request(u, headers={"User-Agent": "html-design-system-audit/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:  # noqa: S310 - user-supplied URL, read-only
            return r.read(max_bytes).decode("utf-8", errors="ignore")
    html = get(url)
    out = [(url, html)]
    hrefs = re.findall(r"<link[^>]+rel=[\"']?stylesheet[\"']?[^>]*>", html, re.I)
    for tag in hrefs[:max_files]:
        m = re.search(r"href=[\"']([^\"']+)", tag)
        if m:
            css_url = urllib.parse.urljoin(url, m.group(1))
            try:
                out.append((css_url, get(css_url)))
            except Exception as e:  # noqa: BLE001 - keep auditing what we could fetch
                print(f"skip {css_url}: {e}", file=sys.stderr)
    return out


def print_inventory(title, counts, nsources, names=None):
    print(f"# Design inventory: {title}  ({nsources} sources scanned)\n")
    for k, d in counts.items():
        if not d:
            continue
        top = sorted(d.items(), key=lambda x: -x[1])[:25]
        print(f"## {k} — {len(d)} distinct")
        print("\n".join(f"- `{v}` ×{n}" for v, n in top) + "\n")
    if names is not None:
        print("## Existing component candidates (by file name)")
        for cid, files in sorted(names.items()):
            print(f"- {cid}: {', '.join(sorted(set(files))[:5])}")
    print("\nInterpretation: many distinct colors/spacings = no system yet (consolidate into tokens);"
          " heavy custom_properties/tailwind usage = extract existing tokens instead of inventing new ones.")


def suggested_primitives(counts, limit=12):
    """Most-used literal colors as DTCG color objects — a starting point for extend mode."""
    tree, n = {"$type": "color"}, 0
    for v, _ in sorted(counts["colors"].items(), key=lambda x: -x[1]):
        if v.startswith("#") and hex_rgb(v):
            n += 1
            tree[f"extracted-{n}"] = {"$value": hex_to_color_obj(v), "$description": f"seen ×{counts['colors'][v]}"}
        if n >= limit:
            break
    return {"color": {"extracted": tree}}


def cmd_audit(a):
    if a.url:
        sources = fetch_site(a.url)
        counts = inventory(t for _, t in sources)
        if a.json:
            print(json.dumps({"url": a.url, "sources": [u for u, _ in sources], "counts": counts,
                              "suggested_tokens": suggested_primitives(counts)}, indent=1))
            return
        print_inventory(a.url, counts, len(sources))
        print("\n## Suggested primitive colors (DTCG, extend mode)\n\n```json\n"
              + json.dumps(suggested_primitives(counts), indent=1) + "\n```")
        return
    root = Path(a.path)
    exts = {".css", ".scss", ".sass", ".less", ".html", ".jsx", ".tsx", ".vue", ".svelte", ".js", ".ts", ".astro"}
    names, texts = {}, []
    keywords = {c["id"]: [c["id"].split("-")[0], c["file"]] for _, c in components(all_tiers=True)}
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in fns:
            p_ = Path(dp) / fn
            if p_.suffix not in exts:
                continue
            texts.append(p_.read_text(encoding="utf-8", errors="ignore"))
            stem = p_.stem.lower()
            for cid, kws in keywords.items():
                if any(kw == stem or stem.startswith(kw + ".") or stem.startswith(kw + "-") for kw in kws):
                    names.setdefault(cid, []).append(str(p_.relative_to(root)))
    counts = inventory(texts)
    if a.json:
        print(json.dumps({"path": str(root), "files": len(texts), "counts": counts, "components": names,
                          "suggested_tokens": suggested_primitives(counts)}, indent=1))
        return
    print_inventory(str(root), counts, len(texts), names)


def cmd_build(a):
    root = Path(a.dir)
    cfg = load_cfg(root)
    out, _, _ = build_tokens(root)
    parts = [out, root / "css" / "base.css"]
    parts += sorted((root / "css" / "components").glob("*.css")) + sorted((root / "css" / "patterns").glob("*.css"))
    def section(p_):
        body = p_.read_text(encoding="utf-8")
        return f"@layer tokens {{\n{body}\n}}" if p_ == out else body   # tokens are layered so app CSS can override them
    bundle = "@layer reset, tokens, base, components, patterns, utilities;\n\n" + "\n".join(
        f"/* ---- {p_.relative_to(root)} ---- */\n{section(p_)}" for p_ in parts if p_.exists())
    safe_write(root / "dist" / "ds.css", bundle)
    write_index(root, cfg)
    if cfg.get("project", {}).get("sync"):
        cmd_sync(argparse.Namespace(dir=str(root)))
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
        sub = page_dir(cid)
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
    safe_write(Path(root) / "index.html", html)


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
          f"Scopes: {', '.join(cfg.get('scopes') or ['product'])}. Coverage {done}/{total}; token errors: {len(errs)}. "
          f"Next files: {', '.join(nxt[:10]) or 'none'}.")


# ---------- storybook & serve ----------
from html.parser import HTMLParser

CAT_TITLES = {"foundations": "Foundations", "actions": "Actions", "forms": "Forms", "navigation": "Navigation",
              "data-display": "Data Display", "overlays": "Overlays", "feedback": "Feedback", "patterns": "Patterns",
              "marketing": "Marketing", "marketing-pages": "Marketing Pages", "ai": "AI", "ai-patterns": "AI Patterns",
              "commerce": "Commerce", "commerce-pages": "Commerce Pages", "email": "Email", "email-templates": "Email Templates"}
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
    """Config the user is expected to edit: create once; later runs keep their version (--force regenerates)."""
    if path.exists() and not force:
        return False
    return safe_write(path, text, kind="owned")


def iter_pages(root, cfg):
    """Yield (sub, page_path, category_id, extractor) for every component/pattern page that has demos."""
    file_cat = {}
    for cat, c in components(cfg, all_tiers=True):
        file_cat.setdefault((page_dir(cat["id"]) == "patterns", c["file"]), cat["id"])
    for sub in ("components", "patterns"):
        for page in sorted((Path(root) / sub).glob("*.html")):
            ex = DemoExtractor(page.read_text(encoding="utf-8", errors="ignore"))
            ex.feed(ex.src)
            if ex.demos:
                yield sub, page, file_cat.get((sub == "patterns", page.stem), "patterns" if sub == "patterns" else "foundations"), ex


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
           "devDependencies": {"storybook": SB_VERSION, "@storybook/addon-a11y": SB_VERSION, "@storybook/addon-docs": SB_VERSION,
                               **({"@storybook/server-webpack5": SB_VERSION} if a.renderer == "server"
                                  else {"@storybook/html-vite": SB_VERSION, "vite": "^8.0.0"})}}
    pkg["scripts"]["stories"] += f" --renderer {a.renderer}" if a.renderer != "html" else ""
    def merge(existing):
        for k, v in pkg.items():
            if isinstance(v, dict):
                existing.setdefault(k, {})
                for kk, vv in v.items():
                    existing[k].setdefault(kk, vv)
            else:
                existing.setdefault(k, v)
    merge_json(root / "package.json", merge, "scripts/devDependencies")
    server = a.renderer == "server"
    write_if_missing(root / ".storybook" / "main.js", (tpl / ("main.server.js" if server else "main.js")).read_text(encoding="utf-8"), a.force)
    write_if_missing(root / ".storybook" / "preview.js", (tpl / ("preview.server.js" if server else "preview.js")).read_text(encoding="utf-8")
                     .replace("__SERVER_URL__", a.server_url), a.force)
    if server:
        write_if_missing(root / ".storybook" / "preview-head.html", (tpl / "preview-head.server.html").read_text(encoding="utf-8"), a.force)
    append_lines(root / ".gitignore", ["node_modules/", "storybook-static/"])

    stories = root / "stories"
    safe_remove_owned(stories)  # stories are fully generated from the pages; files you added there are kept
    safe_copy(tpl / "render.js", stories / "_render.js")
    _, themes = load_tokens(root)
    safe_write(stories / "_meta.js", "// GENERATED by ds.py storybook — do not edit.\nexport const themes = "
               + json.dumps(["light", *[t for t in themes if t != "light"]]) + ";\n")

    total = 0
    for sub, page, cat, ex in iter_pages(root, cfg):
        title = story_title(cat, page)
        if server:
            total += write_server_stories(stories, sub, page, cat, ex)
            continue
        js = root / "js" / f"{page.stem}.js"
        depth = "../../"
        out = [f"// GENERATED by ds.py storybook from {sub}/{page.name} — edit the page, then re-run `ds.py storybook`.",
               f"import {{ render }} from '../_render.js';"]
        out.append(f"import * as behavior from '{depth}js/{page.stem}.js';" if js.exists() else "const behavior = null;")
        usage = " ".join(ex.usage)[:600]
        params = {"docs": {"description": {"component": usage}}}
        if cat in PAGE_CATS or cat == "marketing":
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
        safe_write(target, "\n".join(out))

    # Foundations: a live token catalog rendered from the same flattened tokens used for tokens.css.
    base, _ = load_tokens(root)
    flat = flatten(base)
    rows = [{"var": var_name(k), "type": v["type"] or "", "path": k} for k, v in flat.items() if v["type"] != "typography"]
    if server:
        safe_write(stories / "foundations" / "tokens.stories.json", json.dumps(
            {"title": "Foundations/Tokens", "parameters": {"server": {"id": "foundations/tokens"}},
             "stories": [{"name": "All tokens"}]}, indent=1) + "\n")
    else:
        safe_write(stories / "foundations" / "tokens.stories.js",
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
    safe_write(stories / "Introduction.mdx", intro)
    print(f"Storybook ({a.renderer}) ready in {root}: {total} demo stories + token catalog.\n"
          f"  cd {root} && npm install && npm run storybook      (static site: npm run build-storybook)")
    if cfg.get("project", {}).get("storybook") == "compose":
        print("  Your project already has a Storybook — compose this one into it instead of merging configs.\n"
              "  Add to your .storybook/main.* (ds.py does not edit it):\n"
              "    refs: { 'design-system': { title: 'Design System', url: 'http://localhost:6006' } },\n"
              "  (in production point url at the deployed design-system Storybook, e.g. its GitHub Pages URL)")
    if server:
        port = re.search(r":(\d+)", a.server_url.split("//", 1)[-1])
        print(f"  Backend: stories fetch {a.server_url}/<id>. Reference backend: `ds.py serve {root} --port {port.group(1) if port else 80}`.\n"
              f"  Your stack: implement GET <url>/<sub>/<file>/<n> returning the fragment — references/storybook.md §4.")


def story_title(cat, page):
    return f"{CAT_TITLES[cat]}/{page.stem.replace('-', ' ').title()}"


def write_server_stories(stories, sub, page, cat, ex):
    """@storybook/server stories: the backend renders GET {url}/{sub}/{file}/{n}; args arrive as query params."""
    entries = []
    for n, (section, markers, _html) in enumerate(ex.demos):
        args = dict(m.split(":", 1) for m in markers.split() if ":" in m)
        entries.append({"name": f"{section} | {markers}" if section else markers,  # ASCII keeps story ids linkable
                        "parameters": {"server": {"id": f"{sub}/{page.stem}/{n}"}},
                        "args": {k.replace("-", "_"): v for k, v in args.items()}})
    params = {"server": {"id": f"{sub}/{page.stem}/0"},
              "docs": {"description": {"component": " ".join(ex.usage)[:600]}}}
    if cat in PAGE_CATS or cat == "marketing":
        params["layout"] = "fullscreen"
    target = stories / CAT_TITLES[cat].lower().replace(" ", "-") / f"{page.stem}.stories.json"
    safe_write(target, json.dumps({"title": story_title(cat, page), "parameters": params, "stories": entries},
                                 indent=1, ensure_ascii=False) + "\n")
    return len(entries)


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


def story_fragment(root, cfg, story_id):
    """Reference HTML for a server-rendered story id: `<sub>/<file>/<n>` or `foundations/tokens`."""
    if story_id == "foundations/tokens":
        base, _ = load_tokens(root)
        rows = "".join(
            f'<tr><td><code>{var_name(k)}</code></td><td>'
            + (f'<span style="display:inline-block;inline-size:2rem;block-size:1rem;background:var({var_name(k)});'
               f'border:1px solid var(--color-border-default)"></span>' if v["type"] == "color" else "")
            + "</td></tr>" for k, v in flatten(base).items() if v["type"] != "typography")
        return f'<table class="ds-table"><thead><tr><th scope="col">Token</th><th scope="col">Preview</th></tr></thead><tbody>{rows}</tbody></table>'
    parts = story_id.split("/")
    if len(parts) != 3 or parts[0] not in ("components", "patterns") or not parts[2].isdigit():
        return None
    for sub, page, _cat, ex in iter_pages(root, cfg):
        if sub == parts[0] and page.stem == parts[1]:
            n = int(parts[2])
            return ex.demos[n][2] if n < len(ex.demos) else None
    return None


def cmd_serve(a):
    import functools, http.server, socketserver
    root = Path(a.dir).resolve()
    cmd_build(argparse.Namespace(dir=str(root)))
    cfg = load_cfg(root)

    class Handler(http.server.SimpleHTTPRequestHandler):
        """Static docs site + the reference fragment endpoint used by `storybook --renderer server`."""

        def end_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            super().end_headers()

        def do_GET(self):
            path = self.path.split("?", 1)[0]
            if not path.startswith("/__stories/"):
                return super().do_GET()
            html = story_fragment(root, cfg, path[len("/__stories/"):].strip("/"))
            body = (html if html is not None else "<p>Unknown story</p>").encode()
            self.send_response(200 if html is not None else 404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    handler = functools.partial(Handler, directory=str(root))
    with socketserver.TCPServer(("127.0.0.1", a.port), handler) as httpd:
        print(f"Serving {root} at http://127.0.0.1:{a.port}/index.html — story fragments at /__stories/<sub>/<file>/<n>  (Ctrl+C to stop)")
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


def _yaml_scalar(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return _num(v)
    return json.dumps(str(v), ensure_ascii=False)   # JSON strings are valid YAML double-quoted scalars


def _yaml(obj, indent=0):
    pad, out = "  " * indent, []
    for k, v in obj.items():
        key = k if re.fullmatch(r"[A-Za-z0-9_-]+", str(k)) else json.dumps(k)
        if isinstance(v, dict):
            out.append(f"{pad}{key}:")
            out.append(_yaml(v, indent + 1))
        elif isinstance(v, list):
            out.append(f"{pad}{key}: [" + ", ".join(_yaml_scalar(x) for x in v) + "]")
        else:
            out.append(f"{pad}{key}: {_yaml_scalar(v)}")
    return "\n".join(x for x in out if x)


def design_md_frontmatter(root, cfg, flat):
    """Google DESIGN.md (alpha) front matter: literal values from the default theme + component token groups."""
    def lit(key):
        if key not in flat:
            return None
        raw = resolve_raw(key, flat)
        if flat[key]["type"] == "color":
            if isinstance(raw, dict) and raw.get("colorSpace") not in (None, "srgb"):
                return color_obj_to_css(raw)
            rgb = color_rgb(raw)
            return _hex_from_rgb(rgb) if rgb else None
        try:
            return to_css(raw, flat[key]["type"], flat, as_var=False)
        except (ValueError, TypeError, KeyError):
            return None
    colors = {}
    for name, key in (("primary", "color.action.primary.bg"), ("on-primary", "color.action.primary.fg"),
                      ("secondary", "color.action.secondary.bg"), ("on-secondary", "color.action.secondary.fg"),
                      ("background", "color.bg.canvas"), ("surface", "color.bg.surface"), ("surface-subtle", "color.bg.subtle"),
                      ("on-surface", "color.text.default"), ("muted", "color.text.muted"), ("link", "color.text.link"),
                      ("outline", "color.border.default"), ("outline-strong", "color.border.strong"), ("focus", "color.border.focus"),
                      ("error", "color.feedback.danger.icon"), ("error-container", "color.feedback.danger.bg"),
                      ("on-error-container", "color.feedback.danger.fg"),
                      ("success", "color.feedback.success.icon"), ("warning", "color.feedback.warning.icon"),
                      ("info", "color.feedback.info.icon"), ("selected", "color.selected.bg"), ("danger", "color.action.danger.bg"),
                      ("on-danger", "color.action.danger.fg")):
        v = lit(key)
        if v:
            colors[name] = v
    typography = {}
    for k, v in flat.items():
        if v["type"] == "typography" and isinstance(v["value"], dict):
            t = {}
            for prop in ("fontFamily", "fontSize", "fontWeight", "lineHeight", "letterSpacing"):
                if prop in v["value"]:
                    val = to_css(v["value"][prop], None, flat, as_var=False)
                    if prop == "fontFamily":
                        val = val.split(",")[0].strip().strip('"')
                    t[prop] = int(val) if prop == "fontWeight" and val.isdigit() else val
            typography[k.split(".", 1)[1]] = t
    rounded = {k.split(".", 1)[1]: lit(k) for k in flat if k.startswith("radius.")}
    spacing = {k.split(".", 1)[1]: lit(k) for k in flat if k.startswith("space.") and k != "space.px"}
    comps = {
        "button-primary": {"backgroundColor": "{colors.primary}", "textColor": "{colors.on-primary}", "rounded": "{rounded.md}",
                           "height": lit("size.control.md") or "40px", "padding": "0 16px"},
        "button-secondary": {"backgroundColor": "{colors.secondary}", "textColor": "{colors.on-secondary}", "rounded": "{rounded.md}"},
        "button-destructive": {"backgroundColor": "{colors.danger}", "textColor": "{colors.on-danger}", "rounded": "{rounded.md}"},
        "input": {"backgroundColor": "{colors.surface}", "textColor": "{colors.on-surface}", "rounded": "{rounded.md}",
                  "height": lit("size.control.md") or "40px"},
        "card": {"backgroundColor": "{colors.surface}", "textColor": "{colors.on-surface}", "rounded": "{rounded.lg}",
                 "padding": lit("card.padding") or "24px"},
        "well": {"backgroundColor": "{colors.surface-subtle}", "textColor": "{colors.on-surface}", "rounded": "{rounded.md}"},
        "link": {"textColor": "{colors.link}"},
        "caption": {"textColor": "{colors.muted}", "typography": "{typography.caption}"},
        "alert-error": {"backgroundColor": "{colors.error-container}", "textColor": "{colors.on-error-container}", "rounded": "{rounded.md}"},
        "error-text": {"textColor": "{colors.error}"},
        "alert-success": {"textColor": "{colors.success}"},
        "alert-warning": {"textColor": "{colors.warning}"},
        "alert-info": {"textColor": "{colors.info}"},
        "list-item-selected": {"backgroundColor": "{colors.selected}", "textColor": "{colors.on-surface}"},
        "divider-strong": {"backgroundColor": "{colors.outline-strong}", "height": "1px"},
        "focus-ring": {"backgroundColor": "{colors.focus}", "width": lit("focus.ring.width") or "2px"},
    }
    if "button-primary" in comps and lit("color.action.primary.bg-hover"):
        colors["primary-hover"] = lit("color.action.primary.bg-hover")
        comps["button-primary-hover"] = {"backgroundColor": "{colors.primary-hover}"}
    d = cfg.get("direction", {})
    fm = {"version": "alpha", "name": cfg["name"],
          "description": d.get("rationale") or d.get("style") or f"{cfg['name']} design system (tier {cfg['tier']})",
          "colors": colors, "typography": typography, "rounded": rounded, "spacing": spacing, "components": comps}
    return "---\n" + _yaml(fm) + "\n---\n"


def cmd_design_md(a):
    """DESIGN.md in Google's format (front matter tokens + ordered prose sections), plus this system's contract."""
    root = Path(a.dir)
    cfg = load_cfg(root)
    build_tokens(root)
    base, themes = load_tokens(root)
    flat = flatten(base)
    theme_flats = {"light": flat, **{n: {**flat, **flatten(t)} for n, t in themes.items()}}
    d, brief = cfg.get("direction", {}), cfg.get("brief", {})
    md = [design_md_frontmatter(root, cfg, flat),
          f"<!-- Generated by `ds.py design-md` from ds.config.json and tokens/ — edit those, then regenerate. "
          f"Validate with `npx @google/design.md lint DESIGN.md`. -->", "",
          "## Overview", "",
          f"{d.get('style') or 'Token-driven, accessible HTML/CSS design system.'} "
          f"Mode: {d.get('mode') or 'new'}{' (reference: ' + d['reference_system'] + ')' if d.get('reference_system') else ''}. "
          f"Product: {brief.get('product') or '—'}; audience: {brief.get('audience') or '—'}.", "",
          f"{d.get('rationale') or ''}".strip()]
    if d.get("allocation"):
        md += ["", "| Style direction | Owns | Never used for |", "|---|---|---|"]
        md += [f"| {x.get('name', '')} | {x.get('owns', '')} | {x.get('never', '')} |" for x in d["allocation"]]
    if cfg.get("principles"):
        md += ["", "Principles:", ""] + [f"{i}. {p_}" for i, p_ in enumerate(cfg["principles"], 1)]
    keys = ["color.bg.canvas", "color.bg.surface", "color.text.default", "color.text.muted", "color.action.primary.bg",
            "color.action.primary.fg", "color.border.default", "color.border.focus", "color.feedback.danger.fg"]
    md += ["", "## Colors", "",
           "Semantic tokens only — never primitives (`--color-blue-600`) or raw values in components. Every theme is "
           "contrast-checked (text 4.5:1, UI boundaries and focus 3:1). Apply a theme with `data-theme` on `<html>`, or "
           "`.theme-<name>` on a subtree.", "",
           "| Token | " + " | ".join(theme_flats) + " |", "|---|" + "---|" * len(theme_flats)]
    md += [f"| `{var_name(k)}` | " + " | ".join(f"`{resolved_in(tf, k)}`" for tf in theme_flats.values()) + " |" for k in keys if k in flat]
    md += ["", "## Typography", "", "| Role | Family | Size | Weight | Line height |", "|---|---|---|---|---|"]
    for k, v in flat.items():
        if v["type"] == "typography" and isinstance(v["value"], dict):
            val = v["value"]
            res = lambda x: to_css(val.get(x, ""), None, flat, as_var=False) if val.get(x) else "—"
            md.append(f"| `{k.split('.', 1)[1]}` | {res('fontFamily')} | {res('fontSize')} | {res('fontWeight')} | {res('lineHeight')} |")

    def scale(prefix):
        return [f"- `{var_name(k)}` = `{resolved_in(flat, k)}`" for k in flat if k.startswith(prefix)]
    md += ["", "## Layout", "", "Components never set outer margins; parents own spacing with `gap`. Logical properties only "
           "(RTL works). Breakpoints can't use CSS variables in `@media`: use `dist/tokens.scss` (`@include up(md)`) or the literals.", ""]
    md += scale("space.") + [""] + scale("breakpoint.") + [""] + scale("size.container.")
    md += ["", "## Elevation & Depth", "",
           "Elevation pairs a surface with a shadow; dark themes lift surfaces instead of relying on shadows. Native `dialog`/`popover` "
           "use the top layer; z-index orders fixed and JS-positioned layers, and anything opened from a dialog sits above `modal`.", ""]
    md += scale("color.elevation.") + scale("elevation.") + scale("shadow.") + [""] + scale("z.")
    md += ["", "## Shapes", ""] + scale("radius.") + scale("border.")
    md += ["", "## Motion", ""] + scale("motion.")
    motion = cfg.get("motion", {})
    md += [f"- **Banned:** {b_}" for b_ in motion.get("bans", [])] + [f"- **Moment:** {m}" for m in motion.get("moments", [])]
    md += ["", "Reduced motion: `prefers-reduced-motion` or `[data-reduced-motion]` on `<html>` neutralizes transitions and animations."]
    report = coverage(root, cfg)
    done, total = summarize(report)
    md += ["", "## Components", "", f"{done}/{total} ready (tier {cfg['tier']}, scopes: {', '.join(cfg.get('scopes') or ['product'])}). "
           "Each has a docs page with every variant and state, an accessibility section and its tokens.", ""]
    names = {c["id"]: c["name"] for c in MANIFEST["categories"]}
    for cid in names:
        rows = [r for r in report if r["category"] == cid]
        if rows:
            md.append(f"- **{names[cid]}:** " + ", ".join(f"{r['name']}{'' if r['done'] else ' (missing)'}" for r in rows))
    md += ["", "## Do's and Don'ts", "",
           "- Do use semantic tokens (`--color-*`, `--space-*`, …); don't use primitives or raw values.",
           "- Do use native elements first (`button`, `a[href]`, `dialog`, `details`, `input` types); ARIA only fills gaps.",
           "- Do give every control a visible label; icon-only controls get an accessible name and a tooltip.",
           "- Do keep focus visible and return it to the trigger when overlays close; don't convey anything by color alone.",
           "- Do keep hit targets ≥ 24px and use logical properties; don't remove outlines without a :focus-visible replacement.",
           "- Do validate forms on submit/blur with an error summary and inline messages; don't disable paste.",
           "- Don't stack more than one primary action per region; don't animate layout properties.",
           "", "## Accessibility", "",
           f"Target: {brief.get('a11y_target', 'WCAG 2.2 AA')}. That satisfies EN 301 549 v4.1.1 (EU Accessibility Act) and exceeds "
           "ADA Title II (WCAG 2.1 AA). See ACCESSIBILITY.md for the conformance statement.",
           "", "## Consuming", "",
           "```html", '<link rel="stylesheet" href="dist/ds.css">', '<script type="module">import { initTheme } from "./js/theme.js"; initTheme();</script>', "```",
           "", "Agents: `llms.txt` indexes every component page as Markdown. Build-time tokens: `dist/tokens.scss`, `dist/tokens.json`; "
           "source tokens (DTCG 2025.10): `tokens/` with `tokens/resolver.json`."]
    if cfg.get("decisions"):
        md += ["", "## Decisions", ""] + [f"- **{x.get('id', '')} {x.get('title', '')}** — {x.get('decision', '')}. {x.get('consequences', '')}" for x in cfg["decisions"]]
    if cfg.get("design_notes"):
        md += ["", "## Notes", "", cfg["design_notes"]]
    safe_write(root / "DESIGN.md", "\n".join(md) + "\n")
    write_a11y_statement(root, cfg)
    print(f"wrote {_rel(root / 'DESIGN.md')} (Google DESIGN.md format) and ACCESSIBILITY.md")


def write_a11y_statement(root, cfg):
    """Accessibility conformance statement template (EAA / EN 301 549 / ADA Title II), kept once you edit it."""
    brief = cfg.get("brief", {})
    text = f"""# Accessibility statement — {cfg['name']}

> Template generated by `ds.py design-md`. Fill the bracketed parts, have it reviewed, then publish it with the product.
> Once you edit this file, ds.py will not overwrite it.

## Commitment
[Organization] wants [product] to be usable by everyone. The {cfg['name']} design system targets **{brief.get('a11y_target', 'WCAG 2.2 AA')}**.

## Standards
- **WCAG 2.2 Level AA** — design-system target and test basis.
- **EN 301 549 v4.1.1** (references WCAG 2.2) — the harmonised standard for the **European Accessibility Act** (in force since 28 June 2025).
- **ADA Title II** (US public entities) requires WCAG 2.1 AA — covered by the WCAG 2.2 AA target.
- Section 508 (US federal) — references WCAG 2.0 AA via EN 301 549 alignment.

## Conformance status
[Fully | Partially] conformant with WCAG 2.2 AA. Known exceptions:
- [Component/page] — [issue] — [workaround] — [planned fix date]

## How it's tested
- Automated: axe on every Storybook story and every docs page in light, dark and high-contrast themes; contrast pairs for every token combination (`ds.py check`).
- Manual: keyboard-only walkthrough, screen readers ([NVDA + Firefox], [VoiceOver + Safari], [TalkBack + Chrome]), 200% zoom and 320px reflow, reduced motion, forced colors.
- Last full audit: [date] by [auditor].

## Feedback and contact
Report a barrier: [email / form]. We reply within [N] business days. [EU: enforcement body / complaints procedure for your member state.]

## Date
Prepared [date]; last reviewed [date].
"""
    safe_write(Path(root) / "ACCESSIBILITY.md", text, kind="owned")


def cmd_package(a):
    root = Path(a.dir)
    cfg = load_cfg(root)
    slug = re.sub(r"[^a-z0-9]+", "-", cfg["name"].lower()).strip("-") or "design-system"
    files = [f for f in ("dist/ds.css", "dist/tokens.css", "dist/tokens.json", "dist/tokens.scss", "css", "js", "tokens", "fonts", "DESIGN.md")
             if (root / f.split("/")[0]).exists() or f == "DESIGN.md"]
    vendored = (root / "tools" / "ds").exists()

    def update(pkg):
        if cfg.get("package_name"):
            pkg["name"] = cfg["package_name"]
        pkg.setdefault("name", f"{slug}-design-system")
        pkg.setdefault("version", cfg.get("version", "0.1.0"))
        pkg.setdefault("description", f"{cfg['name']} design system — tokens, CSS components and docs")
        pkg.pop("private", None)
        pkg["type"] = "module"
        pkg["style"] = "dist/ds.css"
        pkg["exports"] = {".": "./dist/ds.css", "./ds.css": "./dist/ds.css", "./tokens.css": "./dist/tokens.css",
                          "./tokens.json": "./dist/tokens.json", "./tokens.scss": "./dist/tokens.scss",
                          "./css/*": "./css/*", "./js/*": "./js/*", "./tokens/*": "./tokens/*", "./fonts/*": "./fonts/*",
                          "./DESIGN.md": "./DESIGN.md", "./llms.txt": "./llms.txt", "./package.json": "./package.json"}
        pkg["files"] = files + ["llms.txt", "llms"]
        pkg["sideEffects"] = ["*.css"]
        pkg.setdefault("publishConfig", {"access": "public"})
        pkg.setdefault("scripts", {})["prepack"] = ("python3 tools/ds/scripts/ds.py build . && python3 tools/ds/scripts/ds.py design-md ."
                                                   if vendored else "echo 'run ds.py build + design-md before packing'")
        update.result = pkg

    merge_json(root / "package.json", update, "npm package fields")
    cmd_design_md(a)
    pkg = getattr(update, "result", {})
    print(f"package.json ready: {pkg.get('name')}@{pkg.get('version')} — exports dist/ds.css, tokens (css/json/scss), css/*, js/*")


def vendor_tools(root):
    """Copy ds.py + manifest + templates into <root>/tools/ds so CI and teammates don't need the skill installed."""
    dst = Path(root) / "tools" / "ds"
    for base in ("scripts", "assets"):
        for f in sorted((SKILL / base).rglob("*")):
            if f.is_file() and "__pycache__" not in f.parts:
                safe_copy(f, dst / base / f.relative_to(SKILL / base))
    return dst


def git_root(path):
    try:
        return Path(subprocess.check_output(["git", "-C", str(path), "rev-parse", "--show-toplevel"], text=True,
                                            stderr=subprocess.DEVNULL).strip())
    except Exception:  # noqa: BLE001 - not a git repo / git missing
        return None


def cmd_ci(a):
    root = Path(a.dir).resolve()
    load_cfg(root)
    repo = git_root(root) or root
    provider = a.provider or ("gitlab" if (repo / ".gitlab-ci.yml").exists() else "github")
    vendor_tools(root)
    rel = os.path.relpath(root, repo)
    tpl = (SKILL / "assets" / "templates" / "ci" / ("github-actions.yml" if provider == "github" else "gitlab-ci.yml")).read_text(encoding="utf-8")
    body = tpl.replace("__DIR__", rel)
    if provider == "github":
        out = repo / ".github" / "workflows" / "design-system.yml"   # its own file: never touches your workflows
        safe_write(out, body, kind="owned")
        note = f"wrote {_rel(out)}"
    elif (repo / ".gitlab-ci.yml").exists():
        out = root / "ci" / "design-system.gitlab-ci.yml"              # your pipeline stays yours: include this file
        safe_write(out, body, kind="owned")
        note = (f"wrote {_rel(out)}. Add to your .gitlab-ci.yml:\n  include:\n    - local: '{os.path.relpath(out, repo)}'\n"
                "  (and make sure its stages — check, build, publish — exist in your `stages:` list)")
    else:
        out = repo / ".gitlab-ci.yml"
        safe_write(out, body, kind="owned")
        note = f"wrote {_rel(out)}"
    merge_json(root / "package.json", lambda pkg: pkg.setdefault("scripts", {}).__setitem__(
        "stories", "python3 tools/ds/scripts/ds.py storybook ."), "stories script")
    print(f"{note}\nVendored tools to {_rel(root / 'tools/ds')}. Commit package-lock.json (run npm install once). "
          "Secrets: NPM_TOKEN to publish; GitHub: enable Pages → 'GitHub Actions'.")


# ---------- existing projects: detect, place, sync ----------
STACKS = [
    # (name, test(project) -> bool, styles target, js target, preferred ds location)
    ("laravel", lambda p: (p / "artisan").exists() and "laravel/framework" in _read(p / "composer.json"),
     "resources/css/design-system", "resources/js/design-system", "resources/design-system"),
    ("symfony", lambda p: "symfony/framework-bundle" in _read(p / "composer.json"),
     "assets/styles/design-system", "assets/design-system", "design-system"),
    ("wordpress", lambda p: (p / "wp-config.php").exists() or (p / "style.css").exists() and "Theme Name:" in _read(p / "style.css"),
     "assets/css/design-system", "assets/js/design-system", "design-system"),
    ("django", lambda p: (p / "manage.py").exists(), "static/design-system", "static/design-system", "design_system"),
    ("flask/fastapi", lambda p: any(k in _read(p / "requirements.txt") + _read(p / "pyproject.toml") for k in ("flask", "fastapi", "Flask", "FastAPI")),
     "static/design-system", "static/design-system", "design-system"),
    ("rails", lambda p: "rails" in _read(p / "Gemfile"), "app/assets/stylesheets/design-system", "app/javascript/design-system", "design-system"),
    ("phoenix", lambda p: (p / "mix.exs").exists() and "phoenix" in _read(p / "mix.exs"), "assets/css/design-system", "assets/js/design-system", "design-system"),
    ("aspnet", lambda p: any(p.glob("*.csproj")) or any(p.glob("*/*.csproj")), "wwwroot/css/design-system", "wwwroot/js/design-system", "design-system"),
    ("spring", lambda p: (p / "pom.xml").exists() or (p / "build.gradle").exists() or (p / "build.gradle.kts").exists(),
     "src/main/resources/static/design-system", "src/main/resources/static/design-system", "design-system"),
    ("go", lambda p: (p / "go.mod").exists(), "static/design-system", "static/design-system", "design-system"),
    ("next", lambda p: "\"next\"" in _read(p / "package.json"), "src/styles/design-system", "src/design-system", "design-system"),
    ("nuxt", lambda p: "\"nuxt\"" in _read(p / "package.json"), "assets/css/design-system", "assets/design-system", "design-system"),
    ("astro", lambda p: "\"astro\"" in _read(p / "package.json"), "src/styles/design-system", "src/design-system", "design-system"),
    ("sveltekit", lambda p: "\"@sveltejs/kit\"" in _read(p / "package.json"), "src/lib/design-system", "src/lib/design-system", "design-system"),
    ("angular", lambda p: (p / "angular.json").exists(), "src/styles/design-system", "src/design-system", "design-system"),
    ("vite/react/vue/svelte", lambda p: any(f'"{k}"' in _read(p / "package.json") for k in ("react", "vue", "svelte", "vite", "lit")),
     "src/styles/design-system", "src/design-system", "design-system"),
    ("hugo", lambda p: (p / "hugo.toml").exists() or (p / "config.toml").exists() and (p / "layouts").exists(),
     "assets/css/design-system", "assets/js/design-system", "design-system"),
    ("jekyll", lambda p: (p / "_config.yml").exists(), "assets/css/design-system", "assets/js/design-system", "design-system"),
]
STYLE_HINTS = ["src/styles", "styles", "src/css", "css", "assets/css", "assets/styles", "resources/css", "static/css",
               "public/css", "app/assets/stylesheets", "wwwroot/css", "src/main/resources/static"]
TOKEN_HINTS = ["tokens", "src/tokens", "design-tokens", "tokens.json", "theme.json", "src/theme", "tailwind.config.js",
               "tailwind.config.ts", "tailwind.config.cjs", "components.json", "src/app/globals.css", "app/globals.css"]


def _read(path):
    try:
        return Path(path).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def detect_project(project):
    """Read the host project and propose where the design system goes and how it plugs in — without writing."""
    p = Path(project).resolve()
    pkg = {}
    try:
        pkg = json.loads(_read(p / "package.json") or "{}")
    except json.JSONDecodeError:
        pass
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    workspaces = pkg.get("workspaces", [])
    if isinstance(workspaces, dict):
        workspaces = workspaces.get("packages", [])
    if (p / "pnpm-workspace.yaml").exists():
        workspaces += re.findall(r"-\s*['\"]?([^'\"\n]+)", _read(p / "pnpm-workspace.yaml"))
    stacks = [name for name, test, *_ in STACKS if test(p)]
    primary = next((x for x in STACKS if x[0] in stacks), None)
    # Monorepos: the apps live in workspace packages — report their stacks too (e.g. "next (apps/web)").
    for glob_ in workspaces:
        for d in sorted(p.glob(glob_.rstrip("/"))):
            if d.is_dir() and "node_modules" not in d.parts:
                stacks += [f"{name} ({os.path.relpath(d, p)})" for name, test, *_ in STACKS if test(d)]
    pm = next((m for f, m in (("pnpm-lock.yaml", "pnpm"), ("yarn.lock", "yarn"), ("bun.lockb", "bun"), ("bun.lock", "bun"),
                              ("package-lock.json", "npm")) if (p / f).exists()), "npm" if pkg else None)
    storybook = None
    for d in [p, *[x for x in p.glob("*/") if x.name not in SKIP_DIRS], *[x for x in p.glob("*/*/") if "node_modules" not in x.parts]]:
        if (d / ".storybook").is_dir():
            main = next(iter(sorted((d / ".storybook").glob("main.*"))), None)
            fw = re.search(r"@storybook/([\w-]+)", _read(main)) if main else None
            storybook = {"dir": os.path.relpath(d / ".storybook", p), "framework": fw.group(1) if fw else "unknown"}
            break
    existing_ds = [os.path.relpath(c.parent, p) for c in p.glob("**/ds.config.json") if "node_modules" not in c.parts][:5]
    # Where the system should live: the stack's convention, a workspace folder in monorepos, never an occupied folder.
    candidates = []
    bases = [g.rstrip("/*").rstrip("/") for g in workspaces]
    for base in sorted((b for b in bases if b and "*" not in b), key=lambda b: (b not in ("packages", "libs", "shared"), b)):
        candidates.append(f"{base}/design-system")  # a design system is a package, not an app
    if primary:
        candidates.append(primary[4])
    candidates += ["design-system", "ds", "packages/design-system"]
    location = next((c for c in candidates if not (p / c).exists() or (p / c / "ds.config.json").exists()
                     or not any((p / c).iterdir())), "design-system-ds")
    monorepo = bool(workspaces)
    styles = None if monorepo else primary[2] if primary else next((f"{h}/design-system" for h in STYLE_HINTS if (p / h).is_dir()), None)
    js = primary[3] if primary else None
    sync = {}
    if styles:
        sync = {"dist/ds.css": f"{styles}/ds.css", "dist/tokens.css": f"{styles}/tokens.css"}
        if any(s_ in stacks for s_ in ("laravel", "symfony", "next", "nuxt", "astro", "sveltekit", "angular", "vite/react/vue/svelte")):
            sync["dist/tokens.scss"] = f"{styles}/_tokens.scss"
        if js:
            sync["js/theme.js"] = f"{js}/theme.js"
    css_approach = [name for name, hit in (
        ("tailwind", "tailwindcss" in deps or any((p / f).exists() for f in ("tailwind.config.js", "tailwind.config.ts", "tailwind.config.cjs"))),
        ("shadcn", (p / "components.json").exists() and "shadcn" in _read(p / "components.json")),
        ("sass", "sass" in deps or any(p.glob("src/**/*.scss"))),
        ("css-modules", any(p.glob("src/**/*.module.css")) or any(p.glob("src/**/*.module.scss"))),
        ("styled-components/emotion", "styled-components" in deps or "@emotion/react" in deps),
        ("vanilla-extract", "@vanilla-extract/css" in deps)) if hit]
    dirty = None
    if git_root(p):
        try:
            dirty = bool(subprocess.check_output(["git", "-C", str(p), "status", "--porcelain"], text=True).strip())
        except Exception:  # noqa: BLE001
            pass
    ci = "gitlab" if (p / ".gitlab-ci.yml").exists() else "github" if (p / ".github" / "workflows").is_dir() else None
    return {
        "project": str(p), "stacks": stacks or ["unknown"], "package_manager": pm, "workspaces": workspaces,
        "css": css_approach, "storybook": storybook, "ci": ci, "git_dirty": dirty,
        "existing_design_systems": existing_ds,
        "existing_styles": [h for h in STYLE_HINTS if (p / h).is_dir()],
        "existing_tokens_or_themes": [h for h in TOKEN_HINTS if (p / h).exists()],
        "recommended": {
            "location": existing_ds[0] if existing_ds else location,
            "sync": sync,
            "storybook": ("compose" if storybook and storybook["framework"] not in ("html-vite", "server-webpack5") else "own"),
            "consume": ("workspace dependency: add the design-system package to each app's dependencies "
                        "(\"workspace:*\" with pnpm/yarn/bun, \"*\" with npm) and import its CSS" if monorepo
                        else "sync" if sync else "link dist/ds.css directly"),
            "ci": ci or "github",
        },
    }


def cmd_migrate_colors(a):
    root = Path(a.dir)
    load_cfg(root)
    total = 0
    for f in sorted((root / "tokens").rglob("*.json")):
        if f.name == "resolver.json":
            continue
        tree = json.loads(f.read_text(encoding="utf-8"))
        n = migrate_colors_tree(tree)
        if n:
            safe_write(f, json.dumps(tree, indent=2) + "\n")
            total += n
            print(f"{_rel(f)}: {n} colors → DTCG 2025.10 objects")
    print(f"migrated {total} color tokens" if total else "all color tokens already use DTCG 2025.10 objects")


def write_resolver(root, themes):
    """tokens/resolver.json — DTCG Resolver Module (2025.10) description of how sets and themes combine."""
    t = Path(root) / "tokens"
    sources = [{"$ref": n} for n in ("primitive.json", "semantic.json", "component.json") if (t / n).exists()]
    sources += [{"$ref": f"components/{p.name}"} for p in sorted((t / "components").glob("*.json"))] if (t / "components").exists() else []
    contexts = {"light": []}
    contexts.update({n: [{"$ref": f"themes/{n}.json"}] for n in themes if n != "light"})
    brands = sorted(p_.stem for p_ in (t / "brands").glob("*.json")) if (t / "brands").exists() else []
    doc = {"name": "Generated by ds.py build", "version": "2025-11-01",
           "description": "Base sets, then the theme modifier. CSS: [data-theme=<context>] / .theme-<context>.",
           "sets": {"base": {"sources": sources}},
           "modifiers": {"theme": {"description": "Color theme", "contexts": contexts, "default": "light"}},
           "resolutionOrder": [{"$ref": "#/sets/base"}, {"$ref": "#/modifiers/theme"}]}
    if brands:
        doc["modifiers"]["brand"] = {"description": "Brand (white-label) — CSS: [data-brand=<context>]",
                                     "contexts": {"default": [], **{b: [{"$ref": f"brands/{b}.json"}] for b in brands}},
                                     "default": "default"}
        doc["resolutionOrder"] = [{"$ref": "#/sets/base"}, {"$ref": "#/modifiers/brand"}, {"$ref": "#/modifiers/theme"}]
    safe_write(t / "resolver.json", json.dumps(doc, indent=2) + "\n")


def cmd_detect(a):
    info = detect_project(a.project)
    if a.json:
        print(json.dumps(info, indent=2))
        return
    r = info["recommended"]
    print(f"# Project: {info['project']}\n")
    print(f"- Stack: {', '.join(info['stacks'])} · package manager: {info['package_manager'] or '—'} · CSS: {', '.join(info['css']) or 'plain'}")
    print(f"- Monorepo workspaces: {', '.join(info['workspaces']) or 'none'}")
    print(f"- Existing styles: {', '.join(info['existing_styles']) or 'none'} · tokens/themes: {', '.join(info['existing_tokens_or_themes']) or 'none'}")
    print(f"- Storybook: {info['storybook'] or 'none'} · CI: {info['ci'] or 'none'} · uncommitted changes: {info['git_dirty']}")
    if info["existing_design_systems"]:
        print(f"- Existing design system(s): {', '.join(info['existing_design_systems'])} → resume it, don't create a second one")
    print(f"\n## Recommended plan (nothing has been written)\n")
    print(f"- Design system folder: `{r['location']}` (self-contained; never mixed into your source folders)")
    if r["sync"]:
        print("- After each build, `ds.py sync` copies outputs into your app's own folders:")
        for src, dst in r["sync"].items():
            print(f"    {src} → {dst}")
    print(f"- Apps consume it via: {r['consume']}")
    print(f"- Storybook: {'compose into your existing Storybook via `refs` (your config is not edited)' if r['storybook'] == 'compose' else 'its own Storybook inside the design-system folder'}")
    print(f"- CI: {r['ci']} ({'separate include file; your .gitlab-ci.yml is not edited' if r['ci'] == 'gitlab' else 'its own workflow file'})")
    if "tailwind" in info["css"] or "shadcn" in info["css"]:
        print("- Tailwind/shadcn found: extend mode — map their theme into tokens (`ds.py audit`), then emit a Tailwind adapter via /ui-styling")
    if info["git_dirty"]:
        print("- ⚠ Uncommitted changes: commit or stash first so every ds.py change is easy to review and revert")
    print(f"\nNext: ds.py init {r['location']} --project {info['project']} --dry-run   (preview), then without --dry-run")


def cmd_sync(a):
    """Copy build outputs into the host project's conventional folders (only files ds.py owns there)."""
    root = Path(a.dir).resolve()
    cfg = load_cfg(root)
    proj = (root / cfg.get("project", {}).get("root", "..")).resolve()
    mapping = cfg.get("project", {}).get("sync") or {}
    if not mapping:
        print("No sync targets in ds.config.json → project.sync (run `ds.py detect` for suggestions).")
        return
    n = 0
    for src, dst in mapping.items():
        s_ = root / src
        if not s_.exists():
            print(f"skip {src} — not built yet (run ds.py build)", file=sys.stderr)
            continue
        n += bool(safe_copy(s_, proj / dst, kind="owned"))  # inside your app: once you edit it, it's yours
    skipped = f"; kept {len(STATE['skipped'])} file(s) you edited" if STATE["skipped"] else ""
    print((f"synced {n} file(s) into {proj}" if n else f"project copies up to date ({proj})") + skipped)


# ---------- email ----------
EMAIL_CHECKS = [
    (re.compile(r"var\("), "CSS custom property (var()) — email clients don't support them; use $tokens"),
    (re.compile(r"display\s*:\s*(flex|grid)"), "flex/grid layout — use role=presentation tables"),
    (re.compile(r"\d+(\.\d+)?rem\b"), "rem unit — use px in email"),
    (re.compile(r"<img(?![^>]*\balt=)[^>]*>", re.I), "img without alt"),
    (re.compile(r"<img(?![^>]*\bwidth=)[^>]*>", re.I), "img without width attribute (Outlook)"),
    (re.compile(r"<table(?![^>]*role=\"presentation\")[^>]*>", re.I), "layout table without role=\"presentation\""),
    (re.compile(r"href=\"(#|)\""), "empty or # link"),
    (re.compile(r">\s*(click here|here|read more)\s*<", re.I), "vague link text"),
]


def email_profile(root, theme=None):
    """Flat {token_with_underscores: literal} map: colors as hex, rem as px — what email clients understand."""
    base, themes = load_tokens(root)
    flat = flatten(base)
    if theme:
        flat = {**flat, **flatten(themes.get(theme, {}))}
    out = {}
    for k, v in flat.items():
        raw = resolve_raw(k, flat)
        if v["type"] == "color":
            rgb = color_rgb(raw)
            val = _hex_from_rgb(rgb) if rgb else None
        else:
            try:
                val = to_css(raw, v["type"], flat, as_var=False)
            except (ValueError, TypeError, KeyError):
                val = None
            if val and "rem" in val:
                val = re.sub(r"(-?\d*\.?\d+)rem", lambda m: f"{round(float(m.group(1)) * 16)}px", val)
        if val is not None:
            out[re.sub(r"[.-]", "_", k)] = val
    return out


def cmd_email(a):
    """Render email/src/*.html|txt with literal token values into dist/email/, then check client safety."""
    from string import Template
    root = Path(a.dir)
    load_cfg(root)
    src = root / "email" / "src"
    if not src.exists():
        sys.exit(f"No {_rel(src)}/ — add the email scope (`ds.py init {root} --force --scopes ...,email`) or create templates there.")
    light = email_profile(root)
    dark = {f"dark_{k}": v for k, v in email_profile(root, "dark").items()}
    values = {**light, **dark}
    out_dir = root / "dist" / "email"
    safe_write(out_dir / "tokens.light.json", json.dumps(light, indent=1) + "\n")
    safe_write(out_dir / "tokens.dark.json", json.dumps({k[5:]: v for k, v in dark.items()}, indent=1) + "\n")
    problems = 0
    for f in sorted(src.glob("*.html")) + sorted(src.glob("*.txt")):
        try:
            rendered = Template(f.read_text(encoding="utf-8")).substitute(values)
        except KeyError as e:
            print(f"✗ {f.name}: unknown token ${e.args[0]}")
            problems += 1
            continue
        safe_write(out_dir / f.name, rendered)
        if f.suffix != ".html":
            continue
        found = [msg for rx, msg in EMAIL_CHECKS if rx.search(re.sub(r"<!--.*?-->", "", rendered, flags=re.S))]
        size = len(rendered.encode())
        if size > 80_000:
            found.append(f"{size // 1024}KB — Gmail clips around 102KB; keep under 80KB")
        for needle, msg in (("<html lang=", "missing lang on <html>"), ('name="color-scheme"', "missing color-scheme meta"),
                            ("<title>", "missing <title>")):
            if needle not in rendered:
                found.append(msg)
        if not (src / f"{f.stem}.txt").exists():
            found.append("no plain-text part (add <name>.txt)")
        problems += len(found)
        print(f"{'✓' if not found else '✗'} {f.name}" + "".join(f"\n    - {m}" for m in found))
    print(f"rendered into {_rel(out_dir)}; {problems} problem(s)")
    if problems and a.strict:
        sys.exit(1)


# ---------- agent-readable outputs: llms.txt, per-component markdown, MCP server ----------
class DocToMarkdown(HTMLParser):
    """Turn a component page's data-doc sections (except examples) into compact markdown."""
    BLOCK = {"p", "li", "tr", "h2", "h3", "h4", "dt", "dd", "pre", "table", "ul", "ol", "section"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.sections, self.cur, self.depth, self.sec_depth, self.line, self.skip = {}, None, 0, None, [], 0

    def flush(self, prefix=""):
        t = " ".join(" ".join(self.line).split())
        if t and self.cur:
            self.sections.setdefault(self.cur, []).append(prefix + t)
        self.line = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.depth += 1
        if a.get("data-doc") and a["data-doc"] != "examples" and self.cur is None:
            self.cur, self.sec_depth = a["data-doc"], self.depth
        elif a.get("data-doc") == "examples":
            self.skip = self.depth
        if tag in self.BLOCK:
            self.flush()
        if tag in ("th", "td") and self.line:
            self.line.append("|")
        if tag in ("br", "hr", "img", "input", "meta", "link", "source", "wbr", "col"):
            self.depth -= 1

    def handle_endtag(self, tag):
        if tag in self.BLOCK:
            self.flush("- " if tag == "li" else "")
        if self.skip == self.depth:
            self.skip = 0
        if self.sec_depth == self.depth:
            self.flush()
            self.cur, self.sec_depth = None, None
        self.depth -= 1

    def handle_data(self, data):
        if self.cur and not self.skip and data.strip():
            self.line.append(data.strip())


def component_markdown(root, sub, page, cat, ex, rows):
    conv = DocToMarkdown()
    conv.feed(page.read_text(encoding="utf-8", errors="ignore"))
    sec = conv.sections
    md = [f"# {story_title(cat, page).split('/')[-1]}", "",
          f"Category: {CAT_TITLES.get(cat, cat)} · page `{sub}/{page.name}` · CSS `css/{sub}/{page.stem}.css`"
          + (f" · JS `js/{page.stem}.js` (export `init(root)`)" if (Path(root) / "js" / f"{page.stem}.js").exists() else ""), "",
          "| Component | Tier | Status | Required demos |", "|---|---|---|---|"]
    md += [f"| `{r['id']}` — {r['name']} | {r['tier']} | {'ready' if r['done'] else 'missing'} | {' '.join(r['demos'])} |" for r in rows]
    for key, title in (("usage", "Usage"), ("anatomy", "Anatomy")):
        if sec.get(key):
            md += ["", f"## {title}", ""] + [x for x in sec[key] if x.lower() != title.lower()]
    md += ["", "## Examples", ""]
    for section, markers, html in ex.demos:
        md += [f"### {section + ' · ' if section else ''}{markers}", "", "```html", html.strip(), "```", ""]
    for key, title in (("accessibility", "Accessibility"), ("tokens", "Tokens")):
        if sec.get(key):
            md += [f"## {title}", ""] + [x for x in sec[key] if x.lower() != title.lower()] + [""]
    return "\n".join(md).rstrip() + "\n"


def cmd_llms(a):
    """llms.txt + llms-full.txt + llms/<file>.md + dist/ds-index.json (what the MCP server and agents read)."""
    root = Path(a.dir)
    cfg = load_cfg(root)
    build_tokens(root)
    report = {r["id"]: r for r in coverage(root, cfg)}
    by_file, pages = {}, {}
    for cat, c in components(cfg):
        by_file.setdefault((page_dir(cat["id"]), c["file"]), []).append({**c, **report.get(c["id"], {}), "category": cat["id"],
                                                                        "scope": cat.get("scope", "product")})
    for sub, page, cat, ex in iter_pages(root, cfg):
        rows = by_file.get((sub, page.stem), [])
        if rows:
            pages[(sub, page.stem)] = component_markdown(root, sub, page, cat, ex, rows)
            safe_write(root / "llms" / f"{page.stem}.md", pages[(sub, page.stem)])
    index_rows = []
    for (sub, f), rows in by_file.items():
        for r in rows:
            index_rows.append({"id": r["id"], "name": r["name"], "category": r["category"], "scope": r["scope"], "tier": r["tier"],
                               "file": f, "desc": r["desc"], "demos": r["demos"], "aria": r.get("aria"), "native": r.get("native"),
                               "done": bool(r.get("done")), "doc": f"llms/{f}.md"})
    base, themes = load_tokens(root)
    flat = flatten(base)
    tokens = {}
    for name, tf in {"light": flat, **{n: {**flat, **flatten(t)} for n, t in themes.items()}}.items():
        tokens[name] = {var_name(k): resolved_in(tf, k) for k in tf if tf[k]["type"] != "typography"}
    safe_write(root / "dist" / "ds-index.json", json.dumps({"name": cfg["name"], "tier": cfg["tier"],
                                                            "scopes": cfg.get("scopes", ["product"]),
                                                            "components": index_rows, "tokens": tokens}, indent=1) + "\n")
    done = sum(r["done"] for r in index_rows)
    lines = [f"# {cfg['name']} design system", "",
             f"> {cfg.get('direction', {}).get('style') or 'Token-driven, accessible HTML/CSS design system'}. "
             f"{done}/{len(index_rows)} components ready. Use semantic CSS custom properties and the documented markup; "
             "never invent styles.", "",
             "## Contract", "",
             "- [DESIGN.md](DESIGN.md): tokens (front matter), rules, do's and don'ts",
             "- [Tokens (resolved, per theme)](dist/ds-index.json): machine index of components and token values",
             "- [Tokens CSS](dist/tokens.css) · [Bundle](dist/ds.css) · [DTCG sources](tokens/resolver.json)", ""]
    names = {c["id"]: c["name"] for c in MANIFEST["categories"]}
    for cid, cname in names.items():
        rows = [r for r in index_rows if r["category"] == cid and (page_dir(cid), r["file"]) in pages]
        if rows:
            lines += [f"## {cname}", ""]
            seen = set()
            for r in rows:
                if r["file"] not in seen:
                    seen.add(r["file"])
                    same = [x["name"] for x in rows if x["file"] == r["file"]]
                    lines.append(f"- [{', '.join(same)}](llms/{r['file']}.md): {r['desc']}")
            lines.append("")
    missing = [r["id"] for r in index_rows if not r["done"]]
    if missing:
        lines += ["## Not built yet", "", ", ".join(missing), ""]
    safe_write(root / "llms.txt", "\n".join(lines))
    design = (root / "DESIGN.md").read_text(encoding="utf-8") if (root / "DESIGN.md").exists() else ""
    safe_write(root / "llms-full.txt", "\n\n".join([design, *pages.values()]))
    print(f"wrote llms.txt, llms-full.txt, {len(pages)} pages in llms/, dist/ds-index.json")


def cmd_mcp(a):
    root = Path(a.dir).resolve()
    load_cfg(root)
    cmd_llms(argparse.Namespace(dir=str(root)))
    server = root / "mcp" / "server.py"
    safe_copy(SKILL / "assets" / "templates" / "mcp_server.py", server, kind="owned")
    print(f"""MCP server: {_rel(server)} (stdio, no dependencies). Connect it:
  Claude Code:  claude mcp add design-system -- python3 {server}
  Cursor / VS Code / others (mcp.json):
    {{"mcpServers": {{"design-system": {{"command": "python3", "args": ["{server}"]}}}}}}
Tools: list_components, get_component, search, get_tokens, get_design_md. Re-run `ds.py llms` after changes.""")


# ---------- generators: palette, scale ----------
PALETTE_STEPS = ["50", "100", "200", "300", "400", "500", "600", "700", "800", "900", "950"]
PALETTE_L = [0.971, 0.936, 0.885, 0.808, 0.704, 0.637, 0.577, 0.505, 0.444, 0.396, 0.258]   # ≈ Tailwind v4 lightness curve
PALETTE_C = [0.08, 0.18, 0.35, 0.6, 0.85, 1.0, 1.0, 0.9, 0.75, 0.6, 0.45]                   # × seed chroma
PALETTE_CONTRAST = [1.05, 1.15, 1.3, 1.5, 2.0, 3.0, 4.5, 6.0, 8.0, 12.0, 15.0]             # vs white (Leonardo mode)


def _srgb_to_oklch(rgb):
    import math
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    l_ = (0.4122214708 * lin[0] + 0.5363325363 * lin[1] + 0.0514459929 * lin[2]) ** (1 / 3)
    m_ = (0.2119034982 * lin[0] + 0.6806995451 * lin[1] + 0.1073969566 * lin[2]) ** (1 / 3)
    s_ = (0.0883024619 * lin[0] + 0.2817188376 * lin[1] + 0.6299787005 * lin[2]) ** (1 / 3)
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    A = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    B = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return L, math.hypot(A, B), (math.degrees(math.atan2(B, A)) + 360) % 360


def _oklch_linear(l_, c, h):
    import math
    a_, b_ = c * math.cos(math.radians(h)), c * math.sin(math.radians(h))
    l1 = (l_ + 0.3963377774 * a_ + 0.2158037573 * b_) ** 3
    m1 = (l_ - 0.1055613458 * a_ - 0.0638541728 * b_) ** 3
    s1 = (l_ - 0.0894841775 * a_ - 1.2914855480 * b_) ** 3
    return (4.0767416621 * l1 - 3.3077115913 * m1 + 0.2309699292 * s1,
            -1.2684380046 * l1 + 2.6097574011 * m1 - 0.3413193965 * s1,
            -0.0041960863 * l1 - 0.7034186147 * m1 + 1.7076147010 * s1)


def _in_srgb(l_, c, h):
    return all(-1e-4 <= x <= 1 + 1e-4 for x in _oklch_linear(l_, c, h))


def _fit(l_, c, h):
    while c > 0 and not _in_srgb(l_, c, h):   # reduce chroma until it fits sRGB — never clip hue/lightness
        c -= 0.002
    return max(c, 0)


def _l_for_contrast(target, c, h, against=(1, 1, 1)):
    lo, hi = 0.0, 1.0
    for _ in range(24):
        mid = (lo + hi) / 2
        ratio = contrast(_oklch_to_srgb(mid, _fit(mid, c, h), h), against)
        lo, hi = (lo, mid) if ratio < target else (mid, hi)
    return (lo + hi) / 2


def generate_ramp(seed_hex, mode="curve"):
    rgb = hex_rgb(seed_hex)
    if rgb is None:
        sys.exit(f"not a hex color: {seed_hex}")
    L0, C0, H = _srgb_to_oklch(rgb)
    C0 = max(C0, 0.02)
    ramp = {}
    anchor = min(range(len(PALETTE_L)), key=lambda i: abs(PALETTE_L[i] - L0))
    for i, step in enumerate(PALETTE_STEPS):
        c = C0 * PALETTE_C[i]
        if mode == "contrast":
            l_ = _l_for_contrast(PALETTE_CONTRAST[i], c, H)
        else:
            l_ = PALETTE_L[i] + (L0 - PALETTE_L[anchor]) * max(0, 1 - abs(i - anchor) / 3)   # pull neighbours toward the seed
        c = _fit(l_, c, H)
        srgb = _oklch_to_srgb(l_, c, H)
        ramp[step] = {"colorSpace": "oklch", "components": [round(l_, 4), round(c, 4), round(H, 2)], "hex": _hex_from_rgb(srgb)}
    if mode == "curve":
        ramp[PALETTE_STEPS[anchor]] = {**hex_to_color_obj(seed_hex), "colorSpace": "srgb"}   # the seed itself, exactly
    return ramp, PALETTE_STEPS[anchor]


def map_semantics(name, ramp, canvas_dark=(0.008, 0.024, 0.09)):
    """Choose ramp steps for primary/link/focus/selected per theme — by measured contrast, not by assumption."""
    white = (1, 1, 1)
    rgb = {s: color_rgb(v) for s, v in ramp.items()}
    ref = lambda s: f"{{color.{name}.{s}}}"
    nxt = lambda s, k=1: PALETTE_STEPS[min(len(PALETTE_STEPS) - 1, PALETTE_STEPS.index(s) + k)]
    prv = lambda s, k=1: PALETTE_STEPS[max(0, PALETTE_STEPS.index(s) - k)]
    light_bg = next((s for s in PALETTE_STEPS if contrast(rgb[s], white) >= 4.5), "700")
    focus = next((s for s in PALETTE_STEPS if contrast(rgb[s], white) >= 3), light_bg)
    sel_fg = next((s for s in PALETTE_STEPS[5:] if contrast(rgb[s], rgb["50"]) >= 4.5), "900")
    dark_bg = next((s for s in ("500", "400", "300") if contrast(rgb[s], canvas_dark) >= 4.5), "300")
    dark_link = next((s for s in ("400", "300", "200") if contrast(rgb[s], canvas_dark) >= 4.5), "200")
    hc_bg = next((s for s in PALETTE_STEPS if contrast(rgb[s], white) >= 7), "900")
    light = {"color": {"action": {"primary": {"bg": {"$value": ref(light_bg)}, "bg-hover": {"$value": ref(nxt(light_bg))},
                                              "bg-active": {"$value": ref(nxt(light_bg, 2))}, "fg": {"$value": "{color.gray.0}"}}},
                       "text": {"link": {"$value": ref(light_bg)}}, "border": {"focus": {"$value": ref(focus)}},
                       "selected": {"bg": {"$value": ref("50")}, "fg": {"$value": ref(sel_fg)}, "border": {"$value": ref(light_bg)}}}}
    dark = {"color": {"action": {"primary": {"bg": {"$value": ref(dark_bg)}, "bg-hover": {"$value": ref(prv(dark_bg))},
                                             "bg-active": {"$value": ref(prv(dark_bg, 2))}, "fg": {"$value": "{color.gray.950}"}}},
                      "text": {"link": {"$value": ref(dark_link)}}, "border": {"focus": {"$value": ref(dark_link)}},
                      "selected": {"bg": {"$value": ref("900")}, "fg": {"$value": ref("100")}, "border": {"$value": ref(dark_link)}}}}
    hc = {"color": {"action": {"primary": {"bg": {"$value": ref(hc_bg)}, "fg": {"$value": "{color.gray.0}"}}},
                    "text": {"link": {"$value": ref(hc_bg)}}}}
    return light, dark, hc


def cmd_palette(a):
    ramp, anchor = generate_ramp(a.color, a.mode)
    name = a.name
    print(f"# {name} ramp from {a.color} (OKLCH, mode {a.mode}; seed sits at step {anchor})\n")
    print("| step | hex | oklch | vs white | vs #020617 |\n|---|---|---|---|---|")
    for s, v in ramp.items():
        rgb = color_rgb(v)
        print(f"| {s} | `{_hex_from_rgb(rgb)}` | `{color_obj_to_css({**v, 'colorSpace': 'oklch'}) if v['colorSpace'] == 'oklch' else 'seed'}` "
              f"| {contrast(rgb, (1, 1, 1)):.2f} | {contrast(rgb, (0.008, 0.024, 0.09)):.2f} |")
    light, dark, hc = map_semantics(name, ramp)
    primitive = {"color": {"$type": "color", name: {s: {"$value": v} for s, v in ramp.items()}}}
    if not a.dir:
        print("\nPreview only. To write it: ds.py palette <hex> --name <name> --dir <ds> [--primary] [--brand <brand>]")
        return
    root = Path(a.dir)
    load_cfg(root)
    if a.brand:   # brand override: same primitive names, different values — see tokens.md "Multi-brand"
        target = root / "tokens" / "brands" / f"{a.brand}.json"
        cur = json.loads(_read(target) or "{}")
        safe_write(target, json.dumps(deep_merge(cur, primitive), indent=2) + "\n", kind="generated")
    else:
        safe_write(root / "tokens" / "palettes" / f"{name}.json", json.dumps(
            deep_merge(primitive, light if a.primary else {}), indent=2) + "\n", kind="generated")
        if a.primary:
            safe_write(root / "tokens" / "themes" / f"dark.palette-{name}.json", json.dumps(dark, indent=2) + "\n", kind="generated")
            safe_write(root / "tokens" / "themes" / f"high-contrast.palette-{name}.json", json.dumps(hc, indent=2) + "\n", kind="generated")
    errs, _ = check_tokens(root, load_cfg(root))
    build_tokens(root)
    print(f"\nWrote {name} → {_rel(target) if a.brand else 'tokens/palettes/' + name + '.json'}"
          f"{' (+ primary mapping for light/dark/high-contrast)' if a.primary and not a.brand else ''}. "
          f"Contrast check: {'all pairs pass' if not errs else str(len(errs)) + ' problem(s)'}")
    for e in errs:
        print(f"  - {e}")


UTOPIA_SPACE = {"3xs": 0.25, "2xs": 0.5, "xs": 0.75, "s": 1, "m": 1.5, "l": 2, "xl": 3, "2xl": 4, "3xl": 6}


def _clamp(min_px, max_px, min_vw, max_vw):
    slope = (max_px - min_px) / (max_vw - min_vw)
    intercept = min_px - slope * min_vw
    return f"clamp({_num(min_px / 16)}rem, {_num(intercept / 16)}rem + {_num(slope * 100)}vw, {_num(max_px / 16)}rem)"


def cmd_scale(a):
    """Utopia-style fluid scales: type steps and space sizes as clamp() between two viewports."""
    lo, hi = sorted((a.min_vw, a.max_vw))
    if a.kind == "type":
        tree = {"font": {"size": {"$type": "dimension", "$description": f"Fluid type scale {a.min_size}px@{lo} ×{a.min_ratio} → "
                                                                            f"{a.max_size}px@{hi} ×{a.max_ratio} (Utopia)"}}}
        for i in range(a.steps_down * -1, a.steps_up + 1):
            mn, mx = a.min_size * a.min_ratio ** i, a.max_size * a.max_ratio ** i
            tree["font"]["size"][f"step-{i}" if i >= 0 else f"step-n{-i}"] = {"$value": _clamp(mn, mx, lo, hi)}
    else:
        tree = {"space": {"$type": "dimension", "$description": f"Fluid space scale from {a.min_size}px@{lo} → {a.max_size}px@{hi} (Utopia)"}}
        names = list(UTOPIA_SPACE)
        for n_, mult in UTOPIA_SPACE.items():
            tree["space"][f"fluid-{n_}"] = {"$value": _clamp(a.min_size * mult, a.max_size * mult, lo, hi)}
        for x, y in zip(names, names[1:]):   # one-up pairs: s-m grows faster, for section gaps
            tree["space"][f"fluid-{x}-{y}"] = {"$value": _clamp(a.min_size * UTOPIA_SPACE[x], a.max_size * UTOPIA_SPACE[y], lo, hi)}
    text = json.dumps(tree, indent=2) + "\n"
    if not a.dir:
        print(text + "\nPreview only. Add --dir <ds> to write tokens/scales/" + a.kind + ".json")
        return
    root = Path(a.dir)
    load_cfg(root)
    safe_write(root / "tokens" / "scales" / f"{a.kind}.json", text, kind="generated")
    build_tokens(root)
    print(f"wrote tokens/scales/{a.kind}.json — map typography roles / spacing to these in semantic.json when ready. "
          "Rem terms keep text zoomable (WCAG 1.4.4); keep max ≤ 2.5 × min.")


# ---------- exports: tailwind, shadcn, figma, native ----------
SHADCN_MAP = {"background": "color.bg.canvas", "foreground": "color.text.default", "card": "color.elevation.surface.raised",
              "card-foreground": "color.text.default", "popover": "color.elevation.surface.overlay",
              "popover-foreground": "color.text.default", "primary": "color.action.primary.bg",
              "primary-foreground": "color.action.primary.fg", "secondary": "color.action.secondary.bg",
              "secondary-foreground": "color.action.secondary.fg", "muted": "color.bg.muted", "muted-foreground": "color.text.muted",
              "accent": "color.bg.subtle", "accent-foreground": "color.text.default", "destructive": "color.action.danger.bg",
              "border": "color.border.default", "input": "color.border.strong", "ring": "color.border.focus",
              "chart-1": "dataviz.categorical.1", "chart-2": "dataviz.categorical.2", "chart-3": "dataviz.categorical.3",
              "chart-4": "dataviz.categorical.4", "chart-5": "dataviz.categorical.5", "sidebar": "color.bg.subtle",
              "sidebar-foreground": "color.text.default", "sidebar-primary": "color.action.primary.bg",
              "sidebar-primary-foreground": "color.action.primary.fg", "sidebar-accent": "color.bg.muted",
              "sidebar-accent-foreground": "color.text.default", "sidebar-border": "color.border.default",
              "sidebar-ring": "color.border.focus"}
TAILWIND_ALIASES = {"canvas": "color.bg.canvas", "surface": "color.bg.surface", "subtle": "color.bg.subtle", "muted": "color.bg.muted",
                    "fg": "color.text.default", "fg-muted": "color.text.muted", "fg-subtle": "color.text.subtle",
                    "link": "color.text.link", "primary": "color.action.primary.bg", "primary-hover": "color.action.primary.bg-hover",
                    "on-primary": "color.action.primary.fg", "danger": "color.action.danger.bg", "on-danger": "color.action.danger.fg",
                    "line": "color.border.default", "line-strong": "color.border.strong", "ring": "color.border.focus",
                    "selected": "color.selected.bg", "info": "color.feedback.info.icon", "success": "color.feedback.success.icon",
                    "warning": "color.feedback.warning.icon", "error": "color.feedback.danger.icon"}


def _camel(key):
    parts = re.split(r"[.\-]", key)
    out = parts[0] + "".join(p_[:1].upper() + p_[1:] for p_ in parts[1:])
    return ("t" + out) if out[:1].isdigit() else out


def _theme_values(root):
    """{theme: {key: (type, literal)}} with colors resolved to sRGB (r,g,b,a) and dimensions to px floats."""
    base, themes = load_tokens(root)
    flat = flatten(base)
    out = {}
    for name, tf in {"light": flat, **{n: {**flat, **flatten(t)} for n, t in themes.items()}}.items():
        vals = {}
        for k, v in tf.items():
            raw = resolve_raw(k, tf)
            if v["type"] == "color":
                rgb = color_rgb(raw)
                if rgb:
                    alpha = raw.get("alpha", 1) if isinstance(raw, dict) else (int(raw.strip().lstrip("#")[6:8], 16) / 255 if isinstance(raw, str) and len(raw.strip().lstrip("#")) == 8 else 1)
                    vals[k] = ("color", (*rgb, alpha))
            elif v["type"] == "dimension":
                try:
                    css = to_css(raw, "dimension", tf, as_var=False)
                except (ValueError, TypeError):
                    css = ""
                m = re.fullmatch(r"(-?\d*\.?\d+)(rem|px)", str(css).strip())   # clamp()/% etc. have no single native value
                if m:
                    vals[k] = ("dimension", float(m.group(1)) * (16 if m.group(2) == "rem" else 1))
            elif v["type"] in ("number", "fontWeight") and isinstance(raw, (int, float)):
                vals[k] = ("number", float(raw))
        out[name] = vals
    return out, flat, themes


def export_tailwind(root, flat):
    lines = ["/* Generated by ds.py export --target tailwind. Use with Tailwind CSS v4:", "   @import \"tailwindcss\";",
             "   @import \"<design-system>/dist/ds.css\";              (tokens + components; its layers come after Tailwind's)",
             "   @import \"<design-system>/dist/exports/tailwind.css\";",
             "   Same-named theme variables (--radius-*, --shadow-*, --breakpoint-*) are overridden by ds tokens automatically;",
             "   the aliases below add theme-aware utilities such as bg-primary, text-fg-muted, border-line, ring-ring. */",
             "@theme inline {"]
    lines += [f"  --color-{alias}: var({var_name(k)});" for alias, k in TAILWIND_ALIASES.items() if k in flat]
    lines += [f"  --color-ds-{k[6:].replace('.', '-')}: var({var_name(k)});" for k, v in flat.items()
              if v["type"] == "color" and k.startswith("color.") and not re.match(r"color\.(gray|blue|red|green|amber|violet|alpha)\.", k)]
    lines += ["  --font-sans: var(--font-family-sans);", "  --font-serif: var(--font-family-serif);", "  --font-mono: var(--font-family-mono);"]
    lines += [f"  --text-{k.split('.')[-1]}: var({var_name(k)});" for k in flat if k.startswith("font.size.")]
    lines += ["  --spacing: var(--space-1);", "}"]
    return "\n".join(lines) + "\n"


def export_shadcn(root, flat, themes):
    def block(sel, tf, keys):
        rows = [f"  --{n}: var({var_name(k)});" for n, k in SHADCN_MAP.items() if k in tf and k in keys]
        return f"{sel} {{\n" + "\n".join(rows) + "\n}"
    head = ("/* Generated by ds.py export --target shadcn — shadcn/ui variable names pointing at design-system tokens.\n"
            "   Import after dist/ds.css. Theme switching stays on the design system: [data-theme=dark] or .dark both work. */\n")
    root_block = block(":root", flat, set(SHADCN_MAP.values())) .replace("}", f"  --radius: var(--radius-md);\n}}")
    dark = ""
    if "dark" in themes:
        tflat = {**flat, **flatten(themes["dark"])}
        dark = "\n\n.dark {\n  color-scheme: dark;\n" + decls(tflat, list(flatten(themes["dark"]))) + "\n}"
    return head + root_block + dark + "\n"


def export_figma(root, values):
    """Body for POST /v1/files/:file_key/variables (Figma Variables REST API) + DTCG per mode for Figma's native import."""
    cols = {"primitives": "col_primitives", "semantic": "col_semantic"}
    modes = list(values)
    body = {"variableCollections": [{"action": "CREATE", "id": "col_primitives", "name": "Primitives", "initialModeId": "mode_prim"},
                                    {"action": "CREATE", "id": "col_semantic", "name": "Semantic", "initialModeId": "mode_light"}],
            "variableModes": [{"action": "UPDATE", "id": "mode_prim", "name": "Value", "variableCollectionId": "col_primitives"},
                              {"action": "UPDATE", "id": "mode_light", "name": "light", "variableCollectionId": "col_semantic"}]
            + [{"action": "CREATE", "id": f"mode_{m}", "name": m, "variableCollectionId": "col_semantic"} for m in modes if m != "light"],
            "variables": [], "variableModeValues": []}
    base, themes = load_tokens(root)
    flat = flatten(base)
    mode_flats = {"light": flat, **{n: {**flat, **flatten(t)} for n, t in themes.items()}}
    prim_ids = {}
    for k, (typ, val) in values["light"].items():
        raw = flat[k]["value"]
        is_alias = isinstance(raw, str) and raw.startswith("{")
        col = "semantic" if is_alias or not re.match(r"(color\.(gray|blue|red|green|amber|violet|alpha)|space|radius|font|z|breakpoint|opacity|border)\b", k) else "primitives"
        vid = "var_" + re.sub(r"\W", "_", k)
        if col == "primitives":
            prim_ids[k] = vid
        body["variables"].append({"action": "CREATE", "id": vid, "name": k.replace(".", "/"), "variableCollectionId": cols[col],
                                  "resolvedType": "COLOR" if typ == "color" else "FLOAT"})
        for m in (["prim"] if col == "primitives" else modes):
            mv = values["light" if m == "prim" else m].get(k)
            if not mv:
                continue
            fv = {"r": round(mv[1][0], 4), "g": round(mv[1][1], 4), "b": round(mv[1][2], 4), "a": round(mv[1][3], 4)} if typ == "color" else round(mv[1], 3)
            if m != "prim":   # semantic → alias the primitive variable when the token is a plain alias in this mode
                ref_ = re.fullmatch(r"\{([^{}]+)\}", str(mode_flats[m].get(k, {}).get("value", "")).strip())
                if ref_ and ref_.group(1) in prim_ids:
                    fv = {"type": "VARIABLE_ALIAS", "id": prim_ids[ref_.group(1)]}
            body["variableModeValues"].append({"variableId": vid, "modeId": f"mode_{m}", "value": fv})
    per_mode = {}
    for m, vals in values.items():
        tree = {}
        for k, (typ, val) in vals.items():
            node = tree
            for part in k.split(".")[:-1]:
                node = node.setdefault(part, {})
            node[k.split(".")[-1]] = ({"$type": "color", "$value": {"colorSpace": "srgb", "components": [round(c, 4) for c in val[:3]],
                                                                    "alpha": round(val[3], 4), "hex": _hex_from_rgb(val[:3])}}
                                      if typ == "color" else {"$type": "number" if typ == "number" else "dimension",
                                                              "$value": val if typ == "number" else {"value": val, "unit": "px"}})
        per_mode[m] = tree
    return body, per_mode


def export_native(values, target):
    light, dark = values["light"], values.get("dark", values["light"])
    colors = sorted(k for k, (t, _) in light.items() if t == "color" and not re.match(r"color\.(gray|blue|red|green|amber|violet|alpha)\.", k))
    dims = sorted(k for k, (t, _) in light.items() if t == "dimension")
    h8 = lambda c: f"{round(c[3] * 255):02X}" + _hex_from_rgb(c[:3])[1:].upper()
    if target == "ios":
        rows = [f"    static let {_camel(k)} = Color(UIColor {{ $0.userInterfaceStyle == .dark ? "
                f"UIColor(red: {dark.get(k, light[k])[1][0]:.4f}, green: {dark.get(k, light[k])[1][1]:.4f}, blue: {dark.get(k, light[k])[1][2]:.4f}, alpha: {dark.get(k, light[k])[1][3]:.3f}) : "
                f"UIColor(red: {light[k][1][0]:.4f}, green: {light[k][1][1]:.4f}, blue: {light[k][1][2]:.4f}, alpha: {light[k][1][3]:.3f}) }})" for k in colors]
        dims_rows = [f"    static let {_camel(k)}: CGFloat = {light[k][1]:g}" for k in dims]
        return {"DesignTokens.swift": "// Generated by ds.py export --target ios. Light/dark resolve at runtime.\nimport SwiftUI\nimport UIKit\n\n"
                "public enum DSColor {\n" + "\n".join(rows) + "\n}\n\npublic enum DSDimension {\n" + "\n".join(dims_rows) + "\n}\n"}
    if target == "android":
        res = lambda vals: "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<!-- Generated by ds.py export --target android -->\n<resources>\n" + "\n".join(
            f"    <color name=\"ds_{re.sub(r'[.-]', '_', k)}\">#{h8(vals.get(k, light[k])[1])}</color>" for k in colors) + "\n</resources>\n"
        dimens = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<resources>\n" + "\n".join(
            f"    <dimen name=\"ds_{re.sub(r'[.-]', '_', k)}\">{light[k][1]:g}{'sp' if k.startswith('font.size') else 'dp'}</dimen>" for k in dims) + "\n</resources>\n"
        return {"values/ds_colors.xml": res(light), "values-night/ds_colors.xml": res(dark), "values/ds_dimens.xml": dimens}
    if target == "compose":
        obj = lambda name, vals: f"object {name} {{\n" + "\n".join(f"    val {_camel(k)} = Color(0x{h8(vals.get(k, light[k])[1])})" for k in colors) + "\n}"
        return {"DesignTokens.kt": "// Generated by ds.py export --target compose\npackage design.system\n\nimport androidx.compose.ui.graphics.Color\n"
                "import androidx.compose.ui.unit.dp\n\n" + obj("DsColorsLight", light) + "\n\n" + obj("DsColorsDark", dark)
                + "\n\nobject DsDimensions {\n" + "\n".join(f"    val {_camel(k)} = {light[k][1]:g}.dp" for k in dims) + "\n}\n"}
    if target == "flutter":
        cls = lambda name, vals: f"class {name} {{\n  {name}._();\n" + "\n".join(
            f"  static const Color {_camel(k)} = Color(0x{h8(vals.get(k, light[k])[1])});" for k in colors) + "\n}"
        return {"ds_tokens.dart": "// Generated by ds.py export --target flutter\nimport 'package:flutter/painting.dart';\n\n"
                + cls("DsColorsLight", light) + "\n\n" + cls("DsColorsDark", dark) + "\n\nclass DsDimensions {\n  DsDimensions._();\n"
                + "\n".join(f"  static const double {_camel(k)} = {light[k][1]:g};" for k in dims) + "\n}\n"}
    raise ValueError(target)


EXPORT_TARGETS = ["tailwind", "shadcn", "figma", "ios", "android", "compose", "flutter"]


def cmd_export(a):
    root = Path(a.dir)
    load_cfg(root)
    build_tokens(root)
    targets = EXPORT_TARGETS if a.target == "all" else a.target.split(",")
    values, flat, themes = _theme_values(root)
    out = root / "dist" / "exports"
    for t in targets:
        if t == "tailwind":
            safe_write(out / "tailwind.css", export_tailwind(root, flat))
        elif t == "shadcn":
            safe_write(out / "shadcn.css", export_shadcn(root, flat, themes))
        elif t == "figma":
            body, per_mode = export_figma(root, values)
            safe_write(out / "figma" / "variables.json", json.dumps(body, indent=1) + "\n")
            for m, tree in per_mode.items():
                safe_write(out / "figma" / f"{m}.tokens.json", json.dumps(tree, indent=1) + "\n")
        elif t in ("ios", "android", "compose", "flutter"):
            for rel, text in export_native(values, t).items():
                safe_write(out / t / rel, text)
        else:
            sys.exit(f"unknown target {t}; choose from {', '.join(EXPORT_TARGETS)} or all")
        print(f"exported {t} → {_rel(out / (t if t not in ('tailwind', 'shadcn') else t + '.css'))}")
    if "figma" in targets:
        print("Figma: POST dist/exports/figma/variables.json to /v1/files/<file_key>/variables (needs a full seat on an "
              "Enterprise plan), or import dist/exports/figma/<mode>.tokens.json with Figma's DTCG import / Tokens Studio.")


# ---------- icons ----------
def optimize_svg(text, name):
    import xml.etree.ElementTree as ET
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    root = ET.fromstring(re.sub(r"<!--.*?-->", "", text, flags=re.S))
    svg_ns = "{http://www.w3.org/2000/svg}"
    drop = {"title", "desc", "metadata", "defs"} if not root.findall(f".//{svg_ns}defs/*") else {"title", "desc", "metadata"}
    for parent in list(root.iter()):
        for child in list(parent):
            tag = child.tag.split("}")[-1]
            if tag in drop or child.tag.startswith("{http://www.inkscape") or child.tag.startswith("{http://sodipodi"):
                parent.remove(child)
    for el in root.iter():
        for attr in list(el.attrib):
            if attr.startswith("{") and ("inkscape" in attr or "sodipodi" in attr) or attr in ("data-name", "class", "id"):
                del el.attrib[attr]
        for paint in ("fill", "stroke"):
            v = el.get(paint)
            if v and v not in ("none", "currentColor") and not v.startswith("url("):
                el.set(paint, "currentColor")
        if el.get("d"):
            el.set("d", re.sub(r"(\d+\.\d{3})\d+", r"\1", el.get("d")))
    view_box = root.get("viewBox") or f"0 0 {root.get('width', '24')} {root.get('height', '24')}"
    inner = "".join(ET.tostring(ch, encoding="unicode") for ch in root)
    inner = re.sub(r"\s+xmlns(:\w+)?=\"[^\"]+\"", "", inner)
    paint = "".join(f' {k}="{root.get(k)}"' for k in ("fill", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin") if root.get(k))
    paint = re.sub(r'(fill|stroke)="(?!none|currentColor)[^"]*"', r'\1="currentColor"', paint)
    return f'<symbol id="icon-{name}" viewBox="{view_box}"{paint}>{inner}</symbol>'


def cmd_icons(a):
    src, root = Path(a.src), Path(a.dir)
    load_cfg(root)
    files = sorted(src.rglob("*.svg"))
    if not files:
        sys.exit(f"no .svg files under {src}")
    symbols, names, before, failed = [], [], 0, []
    for f in files:
        name = re.sub(r"[^a-z0-9-]+", "-", f.stem.lower()).strip("-")
        raw = f.read_text(encoding="utf-8", errors="ignore")
        before += len(raw.encode())
        try:
            symbols.append(optimize_svg(raw, name))
            names.append(name)
        except Exception as e:  # noqa: BLE001 - report and continue
            failed.append(f"{f.name}: {e}")
    sprite = ('<svg xmlns="http://www.w3.org/2000/svg" aria-hidden="true" style="display:none">\n'
              + "\n".join(symbols) + "\n</svg>\n")
    safe_write(root / "dist" / "icons.svg", sprite)
    safe_write(root / "dist" / "icons.json", json.dumps({"icons": names, "license": a.license or "record the icon set license (ADR)"}, indent=1) + "\n")
    tiles = "\n".join(f'      <li class="ds-icons__item"><svg class="icon" aria-hidden="true"><use href="../dist/icons.svg#icon-{n}"></use></svg>'
                      f'<code>{n}</code></li>' for n in names)
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Icons — Design System</title>
<link rel="stylesheet" href="../dist/ds.css"><link rel="stylesheet" href="../docs/docs.css"><script src="../docs/docs.js" defer></script>
<style>.ds-icons{{list-style:none;padding:0;display:grid;gap:var(--space-3);grid-template-columns:repeat(auto-fill,minmax(8rem,1fr))}}
.ds-icons__item{{display:grid;justify-items:center;gap:var(--space-2);padding:var(--space-3);border:var(--border-width-thin) solid var(--color-border-default);border-radius:var(--radius-md)}}
.ds-icons .icon{{inline-size:var(--icon-size-lg);block-size:var(--icon-size-lg)}}</style></head>
<body class="ds-docs"><main id="main" class="ds-docs__main"><h1>Icons ({len(names)})</h1>
<p>Usage: <code>&lt;svg class="icon" aria-hidden="true"&gt;&lt;use href="dist/icons.svg#icon-NAME"&gt;&lt;/use&gt;&lt;/svg&gt;</code> — icons inherit <code>currentColor</code>; give meaningful icons <code>role="img"</code> and an <code>aria-label</code>.</p>
<ul class="ds-icons" role="list">
{tiles}
</ul></main></body></html>
"""
    safe_write(root / "docs" / "icons.html", page)
    after = len(sprite.encode())
    print(f"{len(names)} icons → dist/icons.svg ({before // 1024}KB → {after // 1024}KB), gallery docs/icons.html"
          + (f"; {len(failed)} failed: " + "; ".join(failed[:5]) if failed else "")
          + ". Light optimization only (metadata, editor attributes, precision, currentColor) — not a full SVGO.")


# ---------- taste: the "generic AI look" linter ----------
TASTE_RULES = [
    ("ai-gradient", re.compile(r"(linear|radial)-gradient\([^)]*(#(?:6366f1|8b5cf6|a855f7|7c3aed|ec4899|d946ef|3b82f6)|purple|violet|indigo|fuchsia)", re.I),
     "Purple/indigo/pink gradient — the most recognizable generic-AI look. Use the brand ramp, or no gradient."),
    ("tw-ai-gradient", re.compile(r"\b(from|via|to)-(purple|violet|indigo|fuchsia|pink)-\d{3}\b"),
     "Tailwind purple→pink gradient utilities — same problem, utility-class edition."),
    ("gradient-text", re.compile(r"background-clip\s*:\s*text|\bbg-clip-text\b"),
     "Gradient text — reserve for one signature moment at most; it hurts contrast and readability."),
    ("glass", re.compile(r"backdrop-filter\s*:\s*blur|\bbackdrop-blur(-\w+)?\b"),
     "Glassmorphism blur — costly, low-contrast over busy backgrounds; use elevation tokens instead."),
    ("huge-radius", re.compile(r"border-radius\s*:\s*(2[4-9]|[3-9]\d)px|\brounded-(2xl|3xl)\b"),
     "Very large radii on everything reads as a template. Use radius tokens and a deliberate shape language."),
    ("soft-shadow", re.compile(r"box-shadow\s*:[^;]*\b([4-9]\d|\d{3})px\b|\bshadow-2xl\b"),
     "Huge soft shadows everywhere. Use the elevation scale (raised/overlay) only where something floats."),
    ("emoji-ui", re.compile(r"<(h[1-6]|button|a)\b[^>]*>[^<]*[\U0001F300-\U0001FAFF✨⚡✅⭐]", re.U),
     "Emoji in headings/buttons — screen readers announce them by name; use the icon system."),
    ("placeholder-copy", re.compile(r"lorem ipsum|\bJohn Doe\b|\bAcme( Inc| Corp)?\b", re.I),
     "Placeholder copy — real content length drives real layout."),
    ("buzzwords", re.compile(r"\b(supercharge|unlock (the|your)|seamless(ly)?|revolutioni[sz]e|elevate your|empower(s|ing)? (you|your)|game[- ]changer|next[- ]level|cutting[- ]edge|effortless(ly)?)\b", re.I),
     "Generic marketing buzzwords — say what the product does, for whom, with a number if possible (references/content.md)."),
    ("generic-cta", re.compile(r">\s*(Get Started|Learn More|Click Here|Submit)\s*<", re.I),
     "Vague CTA label — use a specific verb + object (\"Start free trial\", \"Download report\")."),
    ("inter-only", re.compile(r"font-family\s*:\s*['\"]?Inter['\"]?\s*,\s*(system-ui|sans-serif)", re.I),
     "Inter + system fallback as the only typeface — fine for UI, but pair a display face or make it a recorded decision."),
    ("center-everything", re.compile(r"text-align\s*:\s*center|\btext-center\b"),
     "Centered text — fine for heroes, tiring for anything longer than two lines; left-align body copy."),
]


def cmd_taste(a):
    root = Path(a.path)
    exts = {".css", ".scss", ".html", ".jsx", ".tsx", ".vue", ".svelte", ".astro", ".md", ".mdx"}
    files = [root] if root.is_file() else [p_ for p_ in root.rglob("*") if p_.suffix in exts and not set(p_.parts) & SKIP_DIRS]
    hits, per_rule = [], {}
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        for rule, rx, why in TASTE_RULES:
            for m in rx.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                hits.append((rule, f, line, m.group(0)[:60].strip()))
                per_rule[rule] = per_rule.get(rule, 0) + 1
    # center-everything only matters in bulk
    if per_rule.get("center-everything", 0) < 8:
        hits = [h for h in hits if h[0] != "center-everything"]
        per_rule.pop("center-everything", None)
    # Each distinct tell costs 5 (they compound into "template look"), plus a severity weight per occurrence (max 5).
    weight = {"ai-gradient": 8, "tw-ai-gradient": 6, "placeholder-copy": 5, "buzzwords": 4, "emoji-ui": 4, "gradient-text": 4,
              "glass": 4, "generic-cta": 3, "huge-radius": 2, "soft-shadow": 2, "inter-only": 2, "center-everything": 1}
    score = max(0, 100 - sum(5 + min(n, 5) * weight.get(r, 2) for r, n in per_rule.items()))
    if a.json:
        print(json.dumps({"score": score, "rules": per_rule,
                          "hits": [{"rule": r, "file": str(f), "line": ln, "match": m} for r, f, ln, m in hits]}, indent=1))
    else:
        print(f"# Taste check: {root} — score {score}/100 ({len(files)} files)\n")
        why = {r: w for r, _, w in TASTE_RULES}
        for rule, n in sorted(per_rule.items(), key=lambda x: -x[1]):
            print(f"## {rule} ×{n}\n{why[rule]}")
            for r, f, ln, m in [h for h in hits if h[0] == rule][:6]:
                print(f"- {f}:{ln} `{m}`")
            print()
        if not per_rule:
            print("No generic-AI tells found.")
    if a.strict and score < a.min_score:
        sys.exit(1)


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
    for stream in (sys.stdout, sys.stderr):   # Windows consoles (cp1252) must not crash on → ✓ —
        try:
            stream.reconfigure(errors="backslashreplace")
        except (AttributeError, ValueError):
            pass
    for flag, key in (("--dry-run", "dry_run"), ("--force-all", "force")):
        if flag in sys.argv:
            sys.argv.remove(flag)
            STATE[key] = True
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("init"); p.add_argument("dir"); p.add_argument("--name"); p.add_argument("--force", action="store_true")
    p.add_argument("--tier", choices=TIERS, help="default: enterprise (or the existing system's tier)")
    p.add_argument("--scopes", help="comma list, default product: product (app UI), marketing, ai, commerce, email")
    p.add_argument("--project", help="host project root: records stack + sync targets from `ds.py detect`")
    p.add_argument("--adopt", action="store_true", help="allow a non-empty folder; existing files are never overwritten")
    p = sp.add_parser("audit"); p.add_argument("path", nargs="?", default=".")
    p.add_argument("--url", help="audit a live site instead: fetches the page and its stylesheets (read-only)")
    p.add_argument("--json", action="store_true")
    p = sp.add_parser("build"); p.add_argument("dir")
    p = sp.add_parser("check"); p.add_argument("dir"); p.add_argument("--strict", action="store_true")
    p = sp.add_parser("coverage"); p.add_argument("dir"); p.add_argument("--json", action="store_true"); p.add_argument("--all", action="store_true")
    p = sp.add_parser("plan"); p.add_argument("dir")
    p = sp.add_parser("phase"); p.add_argument("dir"); p.add_argument("phase", choices=["discover", "decide", "plan", "build", "done"])
    p = sp.add_parser("status"); p.add_argument("path", nargs="?")
    p = sp.add_parser("detect"); p.add_argument("project", nargs="?", default="."); p.add_argument("--json", action="store_true")
    p = sp.add_parser("sync"); p.add_argument("dir")
    p = sp.add_parser("migrate-colors"); p.add_argument("dir")
    p = sp.add_parser("email"); p.add_argument("dir"); p.add_argument("--strict", action="store_true")
    p = sp.add_parser("llms"); p.add_argument("dir")
    p = sp.add_parser("palette"); p.add_argument("color", help="seed hex, e.g. '#0f766e'")
    p.add_argument("--name", default="brand"); p.add_argument("--mode", choices=["curve", "contrast"], default="curve")
    p.add_argument("--dir", help="design system to write into (omit to preview)")
    p.add_argument("--primary", action="store_true", help="also map primary/link/focus/selected to this ramp in every theme")
    p.add_argument("--brand", help="write as a brand override (tokens/brands/<brand>.json) instead")
    p = sp.add_parser("scale"); p.add_argument("kind", choices=["type", "space"]); p.add_argument("--dir")
    p.add_argument("--min-size", type=float, default=16); p.add_argument("--max-size", type=float, default=20)
    p.add_argument("--min-ratio", type=float, default=1.2); p.add_argument("--max-ratio", type=float, default=1.25)
    p.add_argument("--min-vw", type=float, default=320); p.add_argument("--max-vw", type=float, default=1240)
    p.add_argument("--steps-up", type=int, default=5); p.add_argument("--steps-down", type=int, default=2)
    p = sp.add_parser("export"); p.add_argument("dir")
    p.add_argument("--target", default="all", help=f"comma list or all: {', '.join(EXPORT_TARGETS)}")
    p = sp.add_parser("icons"); p.add_argument("src", help="folder of .svg files"); p.add_argument("dir")
    p.add_argument("--license", help="icon set license to record, e.g. 'Lucide (ISC)'")
    p = sp.add_parser("taste"); p.add_argument("path", nargs="?", default=".")
    p.add_argument("--json", action="store_true"); p.add_argument("--strict", action="store_true")
    p.add_argument("--min-score", type=int, default=80)
    p = sp.add_parser("mcp"); p.add_argument("dir")
    p = sp.add_parser("storybook"); p.add_argument("dir"); p.add_argument("--force", action="store_true")
    p.add_argument("--renderer", choices=["html", "server"], default="html",
                   help="html: client-rendered from the pages (default). server: @storybook/server, a backend renders each story")
    p.add_argument("--server-url", default="http://127.0.0.1:8000/__stories", help="backend base URL for --renderer server")
    p = sp.add_parser("serve"); p.add_argument("dir"); p.add_argument("--port", type=int, default=8000)
    p = sp.add_parser("design-md"); p.add_argument("dir")
    p = sp.add_parser("package"); p.add_argument("dir")
    p = sp.add_parser("ci"); p.add_argument("dir"); p.add_argument("--provider", choices=["github", "gitlab"],
                                                                     help="default: gitlab if the repo has .gitlab-ci.yml, else github")
    p.add_argument("--force", action="store_true")
    sp.add_parser("hook-post-edit"); sp.add_parser("hook-stop")
    a = ap.parse_args()
    if a.cmd == "hook-post-edit":
        return hook_post_edit()
    if a.cmd == "hook-stop":
        return hook_stop()
    {"init": cmd_init, "audit": cmd_audit, "build": cmd_build, "check": cmd_check,
     "coverage": cmd_coverage, "plan": cmd_plan, "phase": cmd_phase, "status": cmd_status,
     "storybook": cmd_storybook, "serve": cmd_serve, "design-md": cmd_design_md, "package": cmd_package, "ci": cmd_ci,
     "detect": cmd_detect, "sync": cmd_sync, "migrate-colors": cmd_migrate_colors, "email": cmd_email,
     "llms": cmd_llms, "mcp": cmd_mcp,
     "palette": cmd_palette, "scale": cmd_scale, "export": cmd_export, "icons": cmd_icons, "taste": cmd_taste}[a.cmd](a)


if __name__ == "__main__":
    main()
