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
  ds.py icons <svg-dir> <dir> [--platforms web,swiftui,compose,flutter,react-native|all]
                                     optimized SVG sprite (currentColor) + gallery + native icon components
  ds.py icons-add <names…> --set lucide|tabler|phosphor|heroicons|material-symbols --dir D
                                     fetch icons from a library (pinned version, license recorded), rebuild the sprite
  ds.py icons-style [svg-dir] --dir D   icons/style.json: grid, stroke, caps/joins, padding, complexity (from a set or tokens)
  ds.py icons-lint <svg…> --dir D    check icons (e.g. drawn from scratch) against icons/style.json
  ds.py mobile spec <dir> [--tokens-only]     dist/mobile/spec.json: tokens per theme + measured web boxes + @3x reference PNGs
  ds.py mobile scaffold <dir> --target swiftui,compose,flutter,react-native,maui,web-mobile|all [--out PATH]
                                     native theme + 10 core components + snapshot tests + FIDELITY.md from the spec
  ds.py mobile verify <dir> --native <png-dir>   diff native snapshots against the web references (exit 1 on drift)
  ds.py mobile lint <path…>          catch bad migrations: raw colors, magic numbers, fixed fonts, hover, small targets
  ds.py playwright <dir>             free visual regression + axe + keyboard-focus suite (Playwright) for every page
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
    (re.compile(r"<a\b(?![^>]*\bhref=)[^>]*>", re.I), "<a> without href — use <button> for actions"),   # \b: not <article>/<aside>
    (re.compile(r"user-scalable\s*=\s*no|maximum-scale\s*=\s*1", re.I), "zoom disabled in viewport meta"),
    (re.compile(r"on\w+=\"[^\"]*\.(showModal|show|close|showPopover|hidePopover|togglePopover)\(", re.I),
     "inline JS opening/closing a dialog or popover — use invoker commands: commandfor=\"id\" command=\"show-modal|close|toggle-popover\""),
]
# Stay inside one <button>: "(?:(?!</button>).)*?" stops a leading-icon button from matching up to a later button's end.
ICON_BTN = re.compile(r"<button(?![^>]*aria-label)[^>]*>\s*<svg[^>]*>(?:(?!</button>).)*?</svg>\s*</button>", re.I | re.S)


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
        status = re.search(r'<meta\s+name="ds-status"\s+content="([\w-]+)"', html or "")
        report.append({"id": c["id"], "name": c["name"], "category": cat["id"], "tier": c["tier"],
                       "file": c["file"], "done": not missing, "missing": missing,
                       "status": status.group(1) if status else ("missing" if html is None else "unspecified")})
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
                     ("theme.js", "js/theme.js"), ("lib/invokers.js", "js/lib/invokers.js")]:
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
            + (f'<span class="ds-status" data-status="{r["status"]}">{r["status"]}</span>' if r["status"] in ("experimental", "beta", "stable", "deprecated") else "")
            + f'<span class="ds-index__status">{"Ready" if r["done"] else "Missing " + str(len(r["missing"]))}</span></li>'
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
    socketserver.TCPServer.allow_reuse_address = True   # quick restarts (tests, watch loops) without "address in use"
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
    md += [f"| `{r['id']}` — {r['name']} | {r['tier']} | {'ready' if r['done'] else 'missing'}"
           f"{' · ' + r['status'] if r.get('status') in ('experimental', 'beta', 'stable', 'deprecated') else ''} | {' '.join(r['demos'])} |"
           for r in rows]
    for key, title in (("usage", "Usage"), ("anatomy", "Anatomy")):
        if sec.get(key):
            md += ["", f"## {title}", ""] + [x for x in sec[key] if x.lower() != title.lower()]
    md += ["", "## Examples", ""]
    for section, markers, html in ex.demos:
        md += [f"### {section + ' · ' if section else ''}{markers}", "", "```html", html.strip(), "```", ""]
    for key, title in (("api", "API"), ("dodont", "Do and don't"), ("accessibility", "Accessibility"), ("tokens", "Tokens")):
        if sec.get(key):
            md += [f"## {title}", ""] + [x for x in sec[key] if x.lower() != title.lower()] + [""]
    log = git_log(page)
    if log:
        md += ["## Changes", ""] + [f"- {x}" for x in log] + [""]
    return "\n".join(md).rstrip() + "\n"


def git_log(path, limit=8):
    """Recent commits touching a file (date · subject) — the per-component changelog. Empty outside git."""
    try:
        out = subprocess.check_output(["git", "-C", str(Path(path).parent), "log", f"-{limit}", "--format=%ad · %s",
                                       "--date=short", "--", Path(path).name], text=True, stderr=subprocess.DEVNULL)
        return [line for line in out.splitlines() if line.strip()]
    except Exception:  # noqa: BLE001 - not a repo / git missing
        return []


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
                               "done": bool(r.get("done")), "status": r.get("status"), "doc": f"llms/{f}.md"})
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
    root = Path(a.dir)
    load_cfg(root)
    build_icons(root, Path(a.src), a.license, a.platforms)


def build_icons(root, src, license_=None, platforms="web"):
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
    safe_write(root / "dist" / "icons.json", json.dumps({"icons": names, "license": license_ or "record the icon set license (ADR)"}, indent=1) + "\n")
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
    wanted = ICON_PLATFORMS if platforms == "all" else [p_ for p_ in (platforms or "web").split(",") if p_ and p_ != "web"]
    symbols = sprite_symbols(root) if wanted else []
    for plat in wanted:
        if plat not in ICON_PLATFORMS:
            sys.exit(f"unknown platform {plat}; choose from web, {', '.join(ICON_PLATFORMS)} or all")
        for rel, text in platform_icons(symbols, plat).items():
            safe_write(root / "dist" / "icons" / plat / rel, text)
        print(f"icons for {plat} → dist/icons/{plat}/")


# ---------- mobile: spec → scaffold → lint → verify ----------
# Bad web→mobile migrations come from re-guessed values, literal CSS translation, dropped states, wrong line
# heights, swapped icons and nobody measuring. So: the web system becomes a measured spec (tokens + computed
# boxes + reference PNGs), native code is generated from the spec, and native snapshots are diffed against it.
import struct
import zlib

PRIMITIVE_COLOR = re.compile(r"color\.([\w-]+\.(\d+|a\d+)|alpha\.[\w.-]+)$")


def _px(css):
    m = re.fullmatch(r"\s*(-?\d*\.?\d+)(rem|px|em)?\s*", str(css or ""))
    return float(m.group(1)) * (16 if m.group(2) in ("rem", "em") else 1) if m else None


def _rgba(raw, tf, depth=0):
    """(r, g, b, a) in sRGB 0..1 from a DTCG color value or alias; None if not a color."""
    if isinstance(raw, str) and depth < 20:
        m = re.fullmatch(r"\{([^{}]+)\}", raw.strip())
        if m and m.group(1) in tf:
            return _rgba(tf[m.group(1)]["value"], tf, depth + 1)
    rgb = color_rgb(raw)
    if not rgb:
        return None
    if isinstance(raw, dict):
        return (*rgb, float(raw.get("alpha", 1)))
    hx = raw.strip().lstrip("#")
    return (*rgb, int(hx[6:8], 16) / 255 if len(hx) == 8 else 1.0)


def _shadow_layers(key, tf):
    raw = resolve_raw(key, tf)
    out = []
    for layer in raw if isinstance(raw, list) else [raw]:
        if not isinstance(layer, dict):
            continue
        dim = lambda p: _px(to_css(layer.get(p, 0), "dimension", tf, as_var=False)) or 0
        out.append({"x": dim("offsetX"), "y": dim("offsetY"), "blur": dim("blur"), "spread": dim("spread"),
                    "color": [round(c, 4) for c in (_rgba(layer.get("color", "#00000000"), tf) or (0, 0, 0, 0))],
                    "inset": bool(layer.get("inset"))})
    return out


def mobile_tokens(root):
    """Absolute, platform-ready values per theme. 1 CSS px = 1 pt (iOS) = 1 dp (Android) = 1 logical px (Flutter/RN)."""
    values, flat, themes = _theme_values(root)
    out = {}
    for theme, vals in values.items():
        tf = flat if theme == "light" else {**flat, **flatten(themes[theme])}
        t = {"color": {}, "dimension": {}, "number": {}, "typography": {}, "shadow": {}, "duration": {}, "easing": {}}
        for k, (typ, v) in sorted(vals.items()):
            if typ == "color" and not PRIMITIVE_COLOR.match(k):
                t["color"][k] = [round(x, 4) for x in v]
            elif typ == "dimension":
                t["dimension"][k] = round(v, 2)
            elif typ == "number":
                t["number"][k] = v
        for key in sorted(k for k in tf if k.startswith("typography.")):
            role = key[len("typography."):]
            if not isinstance(tf[key]["value"], dict):
                continue
            tv = tf[key]["value"]
            res = lambda p: to_css(tv[p], None, tf, as_var=False) if p in tv else None
            size = _px(res("fontSize")) or 16
            lh = res("lineHeight")
            lh_px = size * float(lh) if lh and re.fullmatch(r"[\d.]+", lh) else (_px(lh) or round(size * 1.4))
            t["typography"][role] = {"family": (res("fontFamily") or "system-ui").split(",")[0].strip().strip('"'),
                                     "size": round(size, 2), "weight": int(float(res("fontWeight") or 400)),
                                     "lineHeight": round(lh_px, 2)}
        for k, v in sorted(tf.items()):
            try:
                if v["type"] == "shadow":
                    t["shadow"][k] = _shadow_layers(k, tf)
                elif v["type"] == "duration":
                    raw = resolve_raw(k, tf)
                    css = to_css(raw, "duration", tf, as_var=False)
                    n = float(re.match(r"[\d.]+", css).group())
                    t["duration"][k] = n * 1000 if css.endswith("s") and not css.endswith("ms") else n
                elif v["type"] == "cubicBezier" and isinstance(resolve_raw(k, tf), list):
                    t["easing"][k] = [float(x) for x in resolve_raw(k, tf)]
            except (ValueError, TypeError, AttributeError):
                pass   # clamp()/calc()/unresolvable: no single native value
        out[theme] = t
    return out




def _tpl(name):
    """Native/JS templates live in assets/templates/mobile (markers: @C color, @D dimension, @W weight, @T type, @E shadow)."""
    return (SKILL / "assets" / "templates" / "mobile" / name).read_text(encoding="utf-8")


def ref_name(file, marker, theme):
    """Snapshot file name shared by the reference PNGs and the native snapshot tests."""
    safe = re.sub(r"[^\w.+-]", "_", marker)
    return f"{file}--{safe}--{theme}.png"


def block_selectors(root):
    """{file: '.block'} from each component CSS header ("Block alias: .btn"), so wrappers aren't measured as the component."""
    out = {}
    for css in sorted((Path(root) / "css" / "components").glob("*.css")):
        m = re.search(r"Block alias:\s*(\.[\w-]+)", css.read_text(encoding="utf-8", errors="ignore")[:600])
        out[css.stem] = m.group(1) if m else f".{css.stem}"
    return out


def cmd_mobile_spec(a):
    root = Path(a.dir)
    cfg = load_cfg(root)
    build_tokens(root)
    out = root / "dist" / "mobile"
    tokens = mobile_tokens(root)
    measured = out / "measured.json"
    if not a.tokens_only:
        if not shutil.which("node"):
            print("measurement skipped: Node.js not found (token layer only).", file=sys.stderr)
        else:
            import socket
            import time
            safe_write(out / "measure.mjs", _tpl("measure.mjs").replace("__BLOCKS__", json.dumps(block_selectors(root))))
            with socket.socket() as s:
                s.bind(("127.0.0.1", 0))
                port = s.getsockname()[1]
            server = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "serve", str(root), "--port", str(port)],
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                for _ in range(60):   # wait until the docs server answers (it builds first)
                    time.sleep(0.25)
                    with socket.socket() as probe:
                        if probe.connect_ex(("127.0.0.1", port)) == 0:
                            break
                # ESM resolves @playwright/test from the script's folder upward: <ds root>/node_modules (ds.py playwright + npm install).
                r = subprocess.run(["node", str((out / "measure.mjs").resolve()), f"http://127.0.0.1:{port}", str(out.resolve()),
                                    json.dumps(list(tokens)), a.only or ""],
                                   cwd=str(root), capture_output=True, text=True)
                if r.returncode:
                    tail = (r.stderr.strip().splitlines() or r.stdout.strip().splitlines() or [f"exit {r.returncode}"])[-1]
                    print(f"measurement failed ({tail}). Needs @playwright/test: `ds.py playwright {root}` then "
                          "`npm install && npx playwright install chromium`, or pass --tokens-only.", file=sys.stderr)
            finally:
                server.terminate()
    spec = {"$note": "Generated by ds.py mobile spec. 1 CSS px = 1 pt = 1 dp. tokens: resolved per theme. components: computed "
                     "boxes of each docs demo at 390px wide (root + first form control), per theme; reference PNGs at @3x in "
                     "dist/mobile/reference/<file>--<demo>--<theme>.png. Build native from these numbers, never from memory.",
            "name": cfg["name"], "touchTarget": {"ios": 44, "android": 48}, "scale": 3, "tokens": tokens,
            "components": json.loads(measured.read_text(encoding="utf-8")) if measured.exists() else {}}
    safe_write(out / "spec.json", json.dumps(spec, indent=1) + "\n")
    refs = len(list((out / "reference").glob("*.png"))) if (out / "reference").exists() else 0
    print(f"dist/mobile/spec.json: {len(tokens)} themes, {sum(len(t['color']) for t in tokens.values()) // max(1, len(tokens))} "
          f"semantic colors, {len(spec['components'])} measured components, {refs} reference PNGs.")


# --- PNG (stdlib): decode 8-bit non-interlaced (gray, RGB, palette, gray+alpha, RGBA), encode RGB ---
def png_read(path):
    """(width, height, rows of (r, g, b)) with alpha composited over white."""
    data = Path(path).read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path}: not a PNG")
    pos, idat, plte, trns = 8, bytearray(), b"", b""
    while pos < len(data):
        ln, typ = struct.unpack(">I4s", data[pos:pos + 8])
        chunk = data[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, depth, ctype, _, _, interlace = struct.unpack(">IIBBBBB", chunk)
            if depth != 8 or interlace or ctype not in (0, 2, 3, 4, 6):
                raise ValueError(f"{path}: only 8-bit, non-interlaced PNGs are supported (got depth {depth}, interlace {interlace})")
        elif typ == b"PLTE":
            plte = chunk
        elif typ == b"tRNS":
            trns = chunk
        elif typ == b"IDAT":
            idat += chunk
        pos += 12 + ln
    bpp = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ctype]
    raw, stride, prev, rows, i = zlib.decompress(bytes(idat)), w * bpp, bytearray(w * bpp), [], 0
    over = lambda c, al: round(c * al / 255 + 255 * (1 - al / 255))
    for _ in range(h):
        f, line = raw[i], bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        if f:
            for x in range(stride):
                a_ = line[x - bpp] if x >= bpp else 0
                b_ = prev[x]
                if f == 1:
                    line[x] = (line[x] + a_) & 255
                elif f == 2:
                    line[x] = (line[x] + b_) & 255
                elif f == 3:
                    line[x] = (line[x] + ((a_ + b_) >> 1)) & 255
                else:
                    c_ = prev[x - bpp] if x >= bpp else 0
                    p_ = a_ + b_ - c_
                    pa, pb, pc = abs(p_ - a_), abs(p_ - b_), abs(p_ - c_)
                    line[x] = (line[x] + (a_ if pa <= pb and pa <= pc else b_ if pb <= pc else c_)) & 255
        if ctype == 6:
            row = [(over(line[x], line[x + 3]), over(line[x + 1], line[x + 3]), over(line[x + 2], line[x + 3])) for x in range(0, stride, 4)]
        elif ctype == 2:
            row = [tuple(line[x:x + 3]) for x in range(0, stride, 3)]
        elif ctype == 3:
            row = []
            for x in line:
                al = trns[x] if x < len(trns) else 255
                row.append(tuple(over(c, al) for c in plte[x * 3:x * 3 + 3]))
        elif ctype == 4:
            row = [(over(line[x], line[x + 1]),) * 3 for x in range(0, stride, 2)]
        else:
            row = [(g,) * 3 for g in line]
        rows.append(row)
        prev = line
    return w, h, rows


def png_write(path, w, h, rows):
    raw = b"".join(b"\x00" + bytes(v for px in row for v in px[:3]) for row in rows)
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    return safe_write(path, b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                      + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def _oklab(px):
    import math
    L, C, H = _srgb_to_oklch(tuple(c / 255 for c in px))
    return L, C * math.cos(math.radians(H or 0)), C * math.sin(math.radians(H or 0))


def png_compare(ref_path, native_path, threshold=0.03):
    """Scale native to the reference size (nearest neighbor), then per-pixel OKLab ΔE. Pixels over threshold count as drift."""
    rw, rh, ref = png_read(ref_path)
    nw, nh, nat = png_read(native_path)
    diff, bad, worst, cache = [], 0, 0.0, {}
    lab = lambda p: cache[p] if p in cache else cache.setdefault(p, _oklab(p))
    for y in range(rh):
        nrow, row = nat[min(nh - 1, y * nh // rh)], []
        for x, p in enumerate(ref[y]):
            q = nrow[min(nw - 1, x * nw // rw)]
            de = 0.0 if p == q else sum((u - v) ** 2 for u, v in zip(lab(p), lab(q))) ** 0.5
            worst = max(worst, de)
            if de > threshold:
                bad += 1
                row.append((230, 0, 80))
            else:
                row.append(tuple(170 + c // 3 for c in p))   # faded reference where pixels agree
        diff.append(row)
    return {"ref": [rw, rh], "native": [nw, nh], "mismatch": round(100 * bad / max(1, rw * rh), 2),
            "max_delta_e": round(worst * 100, 1)}, diff


def _css_rgba(s):
    """Computed CSS color (rgb()/rgba()/color(srgb …)/oklch()) to (r, g, b, a) 0..1."""
    s = (s or "").strip()
    nums = [float(x) for x in re.findall(r"-?\d*\.?\d+(?:e-?\d+)?", s)]
    if s.startswith("rgb") and len(nums) >= 3:
        return (nums[0] / 255, nums[1] / 255, nums[2] / 255, nums[3] if len(nums) > 3 else 1.0)
    if s.startswith("color(srgb") and len(nums) >= 3:
        return (*nums[:3], nums[3] if len(nums) > 3 else 1.0)
    if s.startswith("oklch") and len(nums) >= 3:
        l_ = nums[0] / 100 if "%" in s.split()[0] else nums[0]
        return (*_oklch_to_srgb(l_, nums[1], nums[2]), nums[3] if len(nums) > 3 else 1.0)
    return None


def match_reference(ref_dir, name):
    """Snapshot tools prefix names (swift-snapshot-testing: testX.<name>.png, Paparazzi: pkg_Class_test_<name>.png):
    accept the reference whose name is a suffix that starts after a '.' or '_'."""
    if (ref_dir / name).exists():
        return ref_dir / name
    for i, ch in enumerate(name):
        if ch in "._" and (ref_dir / name[i + 1:]).exists() and "--" in name[i + 1:]:
            return ref_dir / name[i + 1:]
    return None


def cmd_mobile_verify(a):
    root = Path(a.dir)
    load_cfg(root)
    ref_dir, nat_dir = root / "dist" / "mobile" / "reference", Path(a.native)
    lines = ["# Mobile fidelity report", "", f"Native snapshots `{nat_dir.name}/` vs `dist/mobile/reference` · fail above "
             f"{a.max_diff}% drifting pixels or ±{a.size_tolerance}% size.", "",
             "| Snapshot | Size ref → native | Drift % | Max ΔE | Result |", "|---|---|---|---|---|"]
    failed = compared = 0
    for nat in sorted(nat_dir.glob("*.png")):
        ref = match_reference(ref_dir, nat.name)
        if not ref:
            lines.append(f"| {nat.stem} | | | | no reference with this name (run `ds.py mobile spec`; names must match) |")
            continue
        stats, diff = png_compare(ref, nat)
        compared += 1
        (rw, rh), (nw, nh) = stats["ref"], stats["native"]
        size_ok = abs(nw - rw) <= rw * a.size_tolerance / 100 and abs(nh - rh) <= rh * a.size_tolerance / 100
        ok = size_ok and stats["mismatch"] <= a.max_diff
        if not ok:
            failed += 1
            png_write(root / "dist" / "mobile" / "diff" / nat.name, rw, rh, diff)
        lines.append(f"| {nat.stem} | {rw}×{rh} → {nw}×{nh}{'' if size_ok else ' **size**'} | {stats['mismatch']} | "
                     f"{stats['max_delta_e']} | {'pass' if ok else 'DRIFT: dist/mobile/diff/' + nat.name} |")
    drift = []
    if a.measurements:
        drift = compare_measurements(root, Path(a.measurements))
        lines += ["", "## Measurements", ""] + [f"- {d}" for d in drift or ["all measured values within tolerance"]]
    summary = f"{compared - failed}/{compared} snapshots within tolerance" + (f", {len(drift)} measurement drifts" if a.measurements else "")
    lines += ["", f"**{summary}.**"]
    safe_write(root / "dist" / "mobile" / "fidelity-report.md", "\n".join(lines) + "\n")
    print(f"{summary}. Report: dist/mobile/fidelity-report.md" + (" · diffs: dist/mobile/diff/" if failed else ""))
    if not compared and not a.measurements:
        sys.exit("no native snapshot matched a reference name")
    if failed or drift:
        sys.exit(1)


MEASURE_TOLERANCE = {"width": 1.0, "height": 1.0, "radius": 1.0, "borderWidth": 0.5, "fontSize": 0.01, "lineHeight": 1.0, "gap": 1.0}


def compare_measurements(root, path):
    """Native test dumps {file: {demo: {theme: {width, height, radius, fontSize, background, …}}}}; compare to the spec."""
    spec = json.loads((root / "dist" / "mobile" / "spec.json").read_text(encoding="utf-8")).get("components", {})
    out = []
    for comp, demos in json.loads(Path(path).read_text(encoding="utf-8")).items():
        for demo, themes in demos.items():
            for theme, got in themes.items():
                want = spec.get(comp, {}).get(demo, {}).get(theme)
                if not want:
                    out.append(f"{comp}/{demo}/{theme}: not in spec (check the name)")
                    continue
                for k, tol in MEASURE_TOLERANCE.items():
                    if got.get(k) is not None and want.get(k) is not None and abs(float(got[k]) - float(want[k])) > tol:
                        out.append(f"{comp}/{demo}/{theme} {k}: native {got[k]} vs web {want[k]}")
                for k in ("background", "color", "borderColor"):
                    g, w_ = got.get(k), _css_rgba(want.get(k))
                    g = _css_rgba(g) if isinstance(g, str) else (tuple(g) if g else None)
                    if g and w_ and max(abs(x - y) for x, y in zip(g, w_)) > 2 / 255 + 1e-6:
                        out.append(f"{comp}/{demo}/{theme} {k}: native {_hex_from_rgb(g[:3], g[3])} vs web {_hex_from_rgb(w_[:3], w_[3])}")
    return out


MOBILE_LINT = {
    ".swift": [(r"\b(?:UI)?Color\(\s*(?:red|hue|white):|Color\(\s*hex:|#colorLiteral|Color\(\s*\"#", "raw color: use DSColor"),
               (r"\.font\(\s*\.system\(\s*size:", "fixed font size ignores Dynamic Type: use DSType / .dsText()"),
               (r"\.padding\(\s*(?:\.\w+\s*,\s*)?\d+(?:\.\d+)?\s*\)", "magic padding: use DSDimension"),
               (r"cornerRadius:\s*\d", "magic radius: use DSDimension.radius*"),
               (r"\.onHover\b", "hover has no touch equivalent: use the pressed state"),
               (r"\.frame\([^)]*\bheight:\s*(?:[1-9]|[1-3]\d|4[0-3])(?:\.\d+)?\s*[,)]", "height under 44 pt: touch target too small (pad the hit area)"),
               (r"Image\(\s*systemName:", "SF Symbol: use DSIcon so icons match the design system")],
    ".kt": [(r"\bColor\(\s*0x[0-9A-Fa-f]{6,8}\s*\)|Color\.(?:Red|Blue|Green|Black|White|Gray)\b", "raw color: use DsTheme.colors"),
            (r"\bfontSize\s*=\s*\d", "raw font size: use DsType"),
            (r"\.padding\(\s*(?:\w+\s*=\s*)?\d+(?:\.\d+)?\.dp", "magic padding: use DsDimension"),
            (r"RoundedCornerShape\(\s*\d", "magic radius: use DsDimension.radius*"),
            (r"\bIcons\.(?:Default|Filled|Outlined|Rounded|Sharp|TwoTone|AutoMirrored)\.", "Material icon: use DsIcons"),
            (r"\.hoverable\(|onPointerEvent\(\s*PointerEventType\.Enter", "hover has no touch equivalent: use pressed"),
            (r"\.(?:height|size)\(\s*(?:[1-9]|[1-3]\d|4[0-7])(?:\.\d+)?\.dp\s*\)", "under 48 dp: wrap with minimumInteractiveComponentSize() or pad the hit area")],
    ".dart": [(r"\bColor\(\s*0x[0-9A-Fa-f]{8}\s*\)|Color\.fromRGBO|Color\.fromARGB", "raw color: use DsColors"),
              (r"\bColors\.(?!transparent\b)\w+", "Material palette color: use DsColors"),
              (r"fontSize:\s*\d", "raw font size: use DsType"),
              (r"EdgeInsets\.\w+\(\s*(?:\w+:\s*)?\d", "magic padding: use DsDimension"),
              (r"BorderRadius\.circular\(\s*\d", "magic radius: use DsDimension.radius*"),
              (r"\bIcons\.\w+|CupertinoIcons\.\w+", "framework icon: use DsIcon"),
              (r"\bonHover:", "hover has no touch equivalent: use pressed")],
    ".tsx": [(r"['\"]#[0-9a-fA-F]{3,8}['\"]|['\"]rgba?\(", "raw color: use theme colors"),
             (r"fontSize:\s*\d", "raw font size: use type"),
             (r"\b(?:padding|margin)(?:Horizontal|Vertical|Top|Bottom|Left|Right|Start|End)?:\s*\d", "magic spacing: use dimension"),
             (r"borderRadius:\s*\d", "magic radius: use dimension.radius*"),
             (r"react-native-vector-icons|@expo/vector-icons", "third-party icon font: use DsIcon"),
             (r"\bonHoverIn\b|\bonMouseEnter\b", "hover has no touch equivalent: use pressed")],
}
MOBILE_LINT[".ts"] = MOBILE_LINT[".jsx"] = MOBILE_LINT[".tsx"]
MOBILE_EXEMPT = re.compile(r"^(DSTheme|DsTheme|ds_theme|theme|DSIcon|DsIcon|DsIcons|ds_icons|DesignTokens|ds_tokens|"
                           r"DSSnapshotTests|DsSnapshotTest|DsSnapshots|ds_golden_test)\.\w+$")
MOBILE_SKIP = {"node_modules", "build", ".gradle", "Pods", "DerivedData", ".dart_tool"}


def mobile_lint_file(path):
    path = Path(path)
    rules = MOBILE_LINT.get(path.suffix)
    if not rules or MOBILE_EXEMPT.match(path.name):
        return []
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines, issues = text.splitlines(), []
    for rx, msg in rules:
        for m in re.finditer(rx, text):
            n = text.count("\n", 0, m.start()) + 1
            if "ds-lint: ignore" not in lines[n - 1]:
                issues.append(f"{path}:{n}: {msg}")
    return issues


def cmd_mobile_lint(a):
    files = []
    for p_ in map(Path, a.paths):
        files += [p_] if p_.is_file() else [f for f in sorted(p_.rglob("*")) if f.suffix in MOBILE_LINT and not set(f.parts) & MOBILE_SKIP]
    issues = [i for f in files for i in mobile_lint_file(f)]
    print("\n".join(f"- {i}" for i in issues) or "- ok")
    print(f"{len(issues)} issue(s) in {len(files)} file(s). Deliberate exception: add a `ds-lint: ignore` comment on that line.")
    if issues and a.strict:
        sys.exit(1)


# --- scaffold: recipes calibrated by the measured spec ---
# Each core component prop = (measured path in spec.components[file][demo][light], default token keys / number).
# With a measured spec the web's computed value wins (snapped to the token that has that value, else a literal);
# without one the default tokens are used. FIDELITY.md shows the source of every number.
CORE_RECIPES = {
    "button": ("variant:primary+state:default", {
        "height": ("height", ["button.height.md", "size.control.md", 40]),
        "heightSm": ("size:sm@height", ["button.height.sm", "size.control.sm", 32]),
        "heightLg": ("size:lg@height", ["button.height.lg", "size.control.lg", 48]),
        "paddingX": ("padding.3", ["button.padding-x", "space.4", 16]),
        "radius": ("radius", ["button.radius", "radius.md", 8]),
        "fontSize": ("fontSize", ["button.font-size", "font.size.sm", 14]),
        "fontWeight": ("fontWeight", ["button.font-weight", "font.weight.semibold", 600]),
        "borderWidth": (None, ["border.width.thin", 1]),
        "gap": ("gap", ["space.2", 8])},
        [("background", "action.primary.bg"), ("color", "action.primary.fg")]),
    "text-field": ("state:default", {
        "height": ("control.height", ["input.height.md", "size.control.md", 40]),
        "paddingX": ("control.padding.3", ["input.padding-x", "space.3", 12]),
        "radius": ("control.radius", ["input.radius", "radius.md", 8]),
        "fontSize": ("control.fontSize", ["font.size.md", 16]),
        "borderWidth": ("control.borderWidth", ["border.width.thin", 1]),
        "gap": ("gap", ["space.1-5", "space.2", 6])},
        [("control.background", "input.bg"), ("control.borderColor", "input.border")]),
    "checkbox": ("state:unchecked", {
        "size": ("control.width", ["checkbox.size", "icon.size.md", 20]),
        "rowHeight": ("minHeight", ["size.touch-target", 44]),
        "radius": ("control.radius", ["checkbox.radius", "radius.sm", 4]),
        "borderWidth": ("control.borderWidth", ["border.width.thin", 1]),
        "gap": ("gap", ["space.2", 8])},
        [("control.borderColor", "input.border")]),
    "switch": ("state:off", {
        "width": ("control.width", ["switch.width", 44]),
        "height": ("control.height", ["switch.height", 24]),
        "inset": (None, ["space.0-5", 2]),
        "radius": (None, ["switch.radius", "radius.full", 9999]),
        "rowHeight": ("minHeight", ["size.touch-target", 44]),
        "gap": ("gap", ["space.2", 8])}, []),
    "card": ("variant:basic", {
        "padding": ("padding.0", ["card.padding", "space.4", 16]),
        "radius": ("radius", ["card.radius", "radius.lg", 12]),
        "borderWidth": ("borderWidth", ["border.width.thin", 1]),
        "gap": ("gap", ["space.2", 8])},
        [("background", "surface.raised")]),
    "badge": ("variant:neutral", {
        "height": ("height", ["badge.height", 20]),
        "paddingX": ("padding.3", ["space.2", 8]),
        "radius": ("radius", ["badge.radius", "radius.full", 9999]),
        "fontSize": ("fontSize", ["font.size.xs", 12]),
        "fontWeight": ("fontWeight", ["font.weight.medium", 500]),
        "gap": ("gap", ["space.1", 4])},
        [("background", "bg.muted"), ("color", "text.default")]),
    "alert": ("variant:info", {
        "padding": ("padding.0", ["alert.padding", "space.4", 16]),
        "radius": ("radius", ["alert.radius", "radius.md", 8]),
        "borderWidth": ("borderWidth", ["border.width.thin", 1]),
        "gap": ("gap", ["space.3", 12]),
        "iconSize": (None, ["icon.size.md", 20])},
        [("background", "feedback.info.bg"), ("borderColor", "feedback.info.border")]),
    "avatar": ("variant:initials", {
        "size": ("width", ["avatar.size.md", "size.control.md", 40]),
        "radius": ("radius", ["avatar.radius", "radius.full", 9999]),
        "fontSize": ("fontSize", ["font.size.sm", 14])},
        [("background", "bg.muted")]),
    "tag": ("variant:static", {
        "height": ("height", ["tag.height", "size.control.sm", 28]),
        "paddingX": ("padding.3", ["space.2", 8]),
        "radius": ("radius", ["tag.radius", "radius.sm", 4]),
        "fontSize": ("fontSize", ["font.size.sm", 14]),
        "borderWidth": ("borderWidth", ["border.width.thin", 1]),
        "gap": ("gap", ["space.1", 4])},
        [("borderColor", "border.default")]),
    "divider": ("variant:horizontal", {
        "thickness": ("height", ["divider.thickness", "border.width.thin", 1])}, [("borderColor", "border.default")]),
}
SIZED_SNAPS = {"text-field", "card", "alert", "divider", "checkbox", "switch"}   # block-level: snapshot at the web width
SNAP_DEMOS = {"button": "variant:primary+state:default", "text-field": "state:default", "checkbox": "state:unchecked",
              "switch": "state:off", "card": "variant:basic", "badge": "variant:neutral", "alert": "variant:info",
              "avatar": "variant:initials", "tag": "variant:static", "divider": "variant:horizontal"}
NUMBER_PROPS = {"fontWeight"}


def _measured(spec_components, file, demo, path):
    if "@" in path:
        demo, path = path.split("@", 1)
    node = spec_components.get(file, {}).get(demo, {}).get("light")
    for part in path.split("."):
        if node is None:
            return None
        node = node[int(part)] if isinstance(node, list) else node.get(part)
    if path.endswith("minHeight") and not node:
        return None   # no min-height on the web: keep the platform touch-target default
    return node if isinstance(node, (int, float)) else None


def calibrate(tokens, components_spec):
    """{file: {prop: {value, token, source}}} for the core components."""
    dims, nums = tokens["light"]["dimension"], tokens["light"]["number"]
    out = {}
    for file, (demo, props, _) in CORE_RECIPES.items():
        out[file] = {}
        for prop, (path, defaults) in props.items():
            pool = nums if prop in NUMBER_PROPS else dims
            keys = [d for d in defaults if isinstance(d, str)]
            fallback = next((d for d in defaults if not isinstance(d, str)), 0)
            got = _measured(components_spec, file, demo, path) if path else None
            if got is not None:
                fam = keys[-1].rsplit(".", 1)[0] + "." if keys else "\0"
                match = next((k for k in keys if k in pool and abs(pool[k] - got) < 0.3), None) or next(
                    (k for k, v in pool.items() if k.startswith(fam) and abs(v - got) < 0.3), None)
                out[file][prop] = {"value": got, "token": match, "source": "measured"}
            else:
                key = next((k for k in keys if k in pool), None)
                out[file][prop] = {"value": pool[key] if key else fallback, "token": key, "source": "token" if key else "default"}
    out["_colors"] = calibrate_colors(tokens, components_spec)
    return out


def calibrate_colors(tokens, components_spec):
    """{file: {role: token}} where the web paints a component with a different semantic token than the default role.
    A candidate must match the measured color in every measured theme, so a coincidental match (white = white) loses."""
    out = {}
    for file, (demo, _, checks) in CORE_RECIPES.items():
        themes = components_spec.get(file, {}).get(demo, {})
        for path, role in checks:
            seen = {}
            for theme, box in themes.items():
                node = box
                for part in path.split("."):
                    node = node.get(part) if isinstance(node, dict) else None
                rgba = _css_rgba(node) if isinstance(node, str) else None
                if rgba and rgba[3] > 0 and theme in tokens:
                    seen[theme] = rgba
            if not seen:
                continue
            same = lambda key: all(key in tokens[t]["color"] and max(abs(x - y) for x, y in zip(tokens[t]["color"][key], c)) <= 2 / 255 + 1e-6
                                   for t, c in seen.items())
            default = pick_color(tokens["light"]["color"], role)
            if default and same(default):
                continue
            match = next((k for k in tokens["light"]["color"] if same(k)), None)
            out.setdefault(file, {})[role] = {"token": match, "default": default, "web": seen.get("light") or next(iter(seen.values()))}
    return out


COLOR_FALLBACKS = {
    "input.bg": ["input.bg", "color.bg.surface", "color.bg.canvas"],
    "input.border": ["input.border", "color.border.strong", "color.border.default"],
    "surface.raised": ["color.elevation.surface.raised", "color.bg.surface", "color.bg.canvas"],
    "bg.muted": ["color.bg.muted", "color.bg.subtle", "color.bg.surface"],
    "bg.surface": ["color.bg.surface", "color.bg.canvas"],
    "border.invalid": ["color.border.invalid", "color.feedback.danger.border", "color.feedback.danger.fg"],
    "action.secondary.border": ["color.action.secondary.border", "color.border.default"],
}


def pick_color(colors, role):
    cands = COLOR_FALLBACKS.get(role) or ["color." + role, role]
    if role.endswith("-active"):
        cands += ["color." + role[:-7] + "-hover", "color." + role[:-7]]
    if role.endswith(".icon"):
        cands += ["color." + role[:-5] + ".fg"]
    return next((k for k in cands if k in colors), None)


def color_ident(key):
    return _camel(key[6:] if key.startswith("color.") else key)


SWIFT_WEIGHTS = {100: ".ultraLight", 200: ".thin", 300: ".light", 400: ".regular", 500: ".medium", 600: ".semibold",
                 700: ".bold", 800: ".heavy", 900: ".black"}


def _rgba_hex(c):
    return "".join(f"{round(max(0, min(1, x)) * 255):02X}" for x in c)


def _lit(v):
    return f"{round(v, 2):g}"


class Emitter:
    """Fills @C(role) @D(file.prop) @W(file.prop) @T(role) @E(file) markers with target-language expressions."""

    def __init__(self, tokens, recipes, lang):
        self.t, self.r, self.lang, self.missing = tokens, recipes, lang, []
        self.light = tokens["light"]

    def color(self, role):
        role, _, file = role.partition("|")
        over = self.r.get("_colors", {}).get(file, {}).get(role) if file else None
        k = over["token"] if over and over["token"] else pick_color(self.light["color"], role)
        if not k:
            self.missing.append(role)
            return "MISSING_" + _camel(role)
        name = color_ident(k)
        return {"swift": f"DSColor.{name}", "kotlin": f"DsTheme.colors.{name}", "dart": f"c.{name}", "ts": f"colors.{name}"}[self.lang]

    def dim(self, ref):
        file, prop = ref.split(".", 1)
        v = self.r[file][prop]
        if v["token"]:
            name = _camel(v["token"])
            return {"swift": f"DSDimension.{name}", "kotlin": f"DsDimension.{name}", "dart": f"DsDimension.{name}",
                    "ts": f"dimension.{name}"}[self.lang]
        lit = _lit(v["value"])
        return {"swift": lit, "kotlin": lit + "f", "dart": lit if "." in lit else lit + ".0", "ts": lit}[self.lang]

    def weight(self, ref):
        file, prop = ref.split(".", 1)
        w = int(round(self.r[file][prop]["value"] / 100) * 100) or 400
        return {"swift": SWIFT_WEIGHTS.get(w, ".regular"), "kotlin": f"FontWeight({w})", "dart": f"FontWeight.w{w}", "ts": f"'{w}'"}[self.lang]

    def type_(self, role):
        roles = self.light["typography"]
        role = role if role in roles else "body" if "body" in roles else next(iter(roles), None)
        if role is None:
            self.missing.append("typography.body")
            return "MISSING_TYPE"
        return {"swift": f"DSType.{_camel(role)}", "kotlin": f"DsType.{_camel(role)}", "dart": f"DsType.{_camel(role)}",
                "ts": f"type.{_camel(role)}"}[self.lang]

    def shadow(self, keys):
        k = next((k for k in keys.split("|") if k in self.light["shadow"]), None)
        empty = {"swift": "[]", "kotlin": "0f", "dart": "const <BoxShadow>[]", "ts": "{}"}[self.lang]
        if not k:
            return empty
        return {"swift": f"DSElevation.{_camel(k)}", "kotlin": f"DsElevation.{_camel(k)}", "dart": f"DsElevation.{_camel(k)}",
                "ts": f"elevation.{_camel(k)}"}[self.lang]

    def fill(self, text):
        text = re.sub(r"@C\(([\w.|-]+)\)", lambda m: self.color(m.group(1)), text)
        text = re.sub(r"@D\(([\w.-]+)\)", lambda m: self.dim(m.group(1)), text)
        text = re.sub(r"@W\(([\w.-]+)\)", lambda m: self.weight(m.group(1)), text)
        text = re.sub(r"@T\(([\w.-]+)\)", lambda m: self.type_(m.group(1)), text)
        return re.sub(r"@E\(([\w.|-]+)\)", lambda m: self.shadow(m.group(1)), text)


def _snap_cases(components_spec):
    """[(file, demo, theme, texts, width)] for the snapshot tests: same names and copy as the web references."""
    out = []
    for file, demo in SNAP_DEMOS.items():
        m = components_spec.get(file, {}).get(demo, {})
        for theme in (m or {"light": {}, "dark": {}}):
            box = m.get(theme) or {}
            out.append((file, demo, theme, box.get("texts") or [], box.get("width")))
    return out


def _themes_by_role(tokens):
    names = list(tokens)
    dark = "dark" if "dark" in names else names[0]
    contrast = next((n for n in names if "contrast" in n and "dark" not in n), names[0])
    return names[0] if "light" not in names else "light", dark, contrast


HEAD = "Generated by ds.py mobile scaffold from the {name} design system. Do not edit: change tokens, re-run the scaffold."


# ---------- SwiftUI ----------


def _swift_str(s):
    return json.dumps(s, ensure_ascii=False)


def gen_swiftui(tokens, recipes, components_spec, name):
    light_n, dark_n, hc_n = _themes_by_role(tokens)
    L, D, H = tokens[light_n], tokens[dark_n], tokens[hc_n]
    tri = lambda key, group="color": ", ".join("0x" + _rgba_hex(T[group].get(key, L[group][key])) for T in (L, D, H))
    out = [f"// {HEAD.format(name=name)}", "// 1 CSS px = 1 pt. Colors resolve light / dark / Increase Contrast at runtime.",
           "import SwiftUI", "import UIKit", "",
           "extension UIColor {", "    convenience init(dsRGBA v: UInt32) {",
           "        self.init(red: CGFloat(v >> 24 & 0xFF) / 255, green: CGFloat(v >> 16 & 0xFF) / 255,",
           "                  blue: CGFloat(v >> 8 & 0xFF) / 255, alpha: CGFloat(v & 0xFF) / 255)", "    }", "}", "",
           "func dsColor(_ light: UInt32, _ dark: UInt32, _ contrast: UInt32) -> Color {",
           "    Color(UIColor { t in", "        UIColor(dsRGBA: t.accessibilityContrast == .high ? contrast : t.userInterfaceStyle == .dark ? dark : light)",
           "    })", "}", "", f"/// Themes: light = {light_n}, dark = {dark_n}, Increase Contrast = {hc_n}.", "public enum DSColor {"]
    out += [f"    public static let {color_ident(k)} = dsColor({tri(k)})" for k in L["color"]]
    out += ["}", "", "public enum DSDimension {"]
    out += [f"    public static let {_camel(k)}: CGFloat = {_lit(v)}" for k, v in L["dimension"].items()]
    out += ["}", "", "public enum DSOpacity {"]
    out += [f"    public static let {_camel(k[8:])}: Double = {_lit(v)}" for k, v in L["number"].items() if k.startswith("opacity.")]
    out += ["}", "", "public enum DSMotion {", "    // Durations in ms. Respect accessibilityReduceMotion: no animation, or a cross-fade."]
    out += [f"    public static let {_camel(k[7:] if k.startswith('motion.') else k)}: Double = {_lit(v)}" for k, v in L["duration"].items()]
    out += [f"    public static func {_camel(k[7:] if k.startswith('motion.') else k)}(_ ms: Double) -> Animation "
            f"{{ .timingCurve({', '.join(_lit(x) for x in v)}, duration: ms / 1000) }}" for k, v in L["easing"].items()]
    out += ["}", "", "public struct DSTextStyle {", "    public let family: String", "    public let size: CGFloat",
            "    public let weight: Font.Weight", "    public let lineHeight: CGFloat", "    public let relativeTo: Font.TextStyle",
            "    public var font: Font { .custom(family, size: size, relativeTo: relativeTo).weight(weight) }", "}", "",
            "public enum DSType {"]
    rel = {"display": ".largeTitle", "h1": ".largeTitle", "h2": ".title", "h3": ".title2", "h4": ".title3", "h5": ".headline",
           "h6": ".headline", "lead": ".body", "body": ".body", "small": ".subheadline", "caption": ".caption", "code": ".body"}
    for role, ty in L["typography"].items():
        out.append(f"    public static let {_camel(role)} = DSTextStyle(family: {_swift_str(ty['family'])}, size: {_lit(ty['size'])}, "
                   f"weight: {SWIFT_WEIGHTS.get(round(ty['weight'] / 100) * 100, '.regular')}, lineHeight: {_lit(ty['lineHeight'])}, "
                   f"relativeTo: {rel.get(role, '.body')})")
    out += ["}", "",
            "/// CSS line-height in SwiftUI: the extra leading is split above and below the line (half-leading) and scales",
            "/// with Dynamic Type, so text boxes match the web measurement.",
            "struct DSTextModifier: ViewModifier {", "    let style: DSTextStyle",
            "    @Environment(\\.dynamicTypeSize) private var dynamicTypeSize", "",
            "    func body(content: Content) -> some View {", "        let _ = dynamicTypeSize",
            "        let scale = UIFontMetrics.default.scaledValue(for: style.size) / style.size",
            "        let natural = (UIFont(name: style.family, size: style.size) ?? .systemFont(ofSize: style.size)).lineHeight",
            "        let extra = max(0, style.lineHeight - natural) * scale",
            "        content.font(style.font).lineSpacing(extra).padding(.vertical, extra / 2)", "    }", "}", "",
            "public extension View {", "    func dsText(_ style: DSTextStyle) -> some View { modifier(DSTextModifier(style: style)) }", "",
            "    func dsShadow(_ layers: [DSShadow]) -> some View {",
            "        layers.reduce(AnyView(self)) { AnyView($0.shadow(color: $1.color, radius: $1.radius, x: $1.x, y: $1.y)) }", "    }", "}", "",
            "/// CSS box-shadow layer. SwiftUI radius = blur / 2; spread has no SwiftUI equivalent and is dropped.",
            "public struct DSShadow {", "    public let color: Color", "    public let radius: CGFloat", "    public let x: CGFloat", "    public let y: CGFloat", "}", "",
            "public enum DSElevation {"]
    for k, layers in L["shadow"].items():
        rows = []
        for i, ly in enumerate(layers):
            if ly["inset"]:
                continue
            cols = ", ".join("0x" + _rgba_hex((T["shadow"].get(k) or layers)[min(i, len(T["shadow"].get(k) or layers) - 1)]["color"]) for T in (L, D, H))
            rows.append(f"DSShadow(color: dsColor({cols}), radius: {_lit(ly['blur'] / 2)}, x: {_lit(ly['x'])}, y: {_lit(ly['y'])})")
        out.append(f"    public static let {_camel(k)}: [DSShadow] = [{', '.join(rows)}]")
    out += ["}", ""]
    em = Emitter(tokens, recipes, "swift")
    files = {"DSTheme.swift": "\n".join(out), "DSComponents.swift": em.fill(_tpl("DSComponents.swift").replace("@HEAD", HEAD.format(name=name)))}
    files["Tests/DSSnapshotTests.swift"] = swift_snapshots(_snap_cases(components_spec), em)
    return files, em.missing


def swift_snapshots(cases, em):
    def view(file, texts):
        t = lambda i, d: _swift_str(texts[i] if len(texts) > i else d)
        return {"button": f"Button({t(0, 'Button')}) {{}}.buttonStyle(DSButtonStyle(.primary))",
                "text-field": f"DSTextField({t(0, 'Label')}, text: .constant(\"\")" + (f", hint: {t(1, '')})" if len(texts) > 1 else ")"),
                "checkbox": f"Toggle({t(0, 'Checkbox')}, isOn: .constant(false)).toggleStyle(DSCheckboxStyle())",
                "switch": f"Toggle({t(0, 'Switch')}, isOn: .constant(false)).toggleStyle(DSSwitchStyle())",
                "card": f"DSCard {{ Text({t(0, 'Title')}).dsText(DSType.{_camel('h5') if 'h5' in em.light['typography'] else 'body'}); Text({t(1, 'Body')}).dsText(DSType.body) }}",
                "badge": f"DSBadge({t(0, 'Badge')})",
                "alert": f"DSAlert({t(0, 'Title')}" + (f", message: {t(1, '')}" if len(texts) > 1 else "") + ", tone: .info)",
                "avatar": f"DSAvatar({t(0, 'A B')})",
                "tag": f"DSTag({t(0, 'Tag')})",
                "divider": "DSDivider()"}[file]
    light_n, dark_n, hc_n = _themes_by_role(em.t)
    rows = []
    for file, demo, theme, texts, width in cases:
        if theme not in (light_n, dark_n, hc_n):
            continue
        frame = f".frame(width: {_lit(width)})" if width and file in SIZED_SNAPS else ""
        mode = "dark" if theme == dark_n and theme != light_n else "contrast" if theme == hc_n and theme != light_n else "light"
        rows.append(f'        snap({view(file, texts)}{frame}, "{ref_name(file, demo, theme)[:-4]}", .{mode})')
    return f"""// {HEAD.format(name='this')}
// Snapshot names match dist/mobile/reference/<file>--<demo>--<theme>.png, rendered at @3x like the references.
// Setup: add https://github.com/pointfreeco/swift-snapshot-testing to the test target and `@testable import` your app.
// Then: python3 ds.py mobile verify <ds-dir> --native <path to __Snapshots__/DSSnapshotTests>
import SnapshotTesting
import SwiftUI
import XCTest

final class DSSnapshotTests: XCTestCase {{
    enum Mode {{ case light, dark, contrast }}

    private func snap<V: View>(_ view: V, _ name: String, _ mode: Mode, file: StaticString = #filePath, testName: String = #function, line: UInt = #line) {{
        let host = UIHostingController(rootView: view.fixedSize(horizontal: false, vertical: true))
        host.overrideUserInterfaceStyle = mode == .dark ? .dark : .light
        host.view.backgroundColor = .clear
        let size = host.sizeThatFits(in: CGSize(width: 390, height: CGFloat.greatestFiniteMagnitude))
        var traits = [UITraitCollection(displayScale: 3), UITraitCollection(userInterfaceStyle: mode == .dark ? .dark : .light)]
        if mode == .contrast {{ traits.append(UITraitCollection(accessibilityContrast: .high)) }}
        assertSnapshot(of: host, as: .image(size: size, traits: UITraitCollection(traitsFrom: traits)), named: name,
                       file: file, testName: testName, line: line)
    }}

    func testCoreComponents() {{
{chr(10).join(rows)}
    }}
}}
"""


# ---------- Jetpack Compose ----------
def _argb(c):
    return f"{round(max(0, min(1, c[3])) * 255):02X}" + "".join(f"{round(max(0, min(1, x)) * 255):02X}" for x in c[:3])


def _theme_ident(name):
    return _camel(name) if not name[:1].isdigit() else "t" + _camel(name)




def gen_compose(tokens, recipes, components_spec, name, pkg):
    L = tokens["light"]
    keys = list(L["color"])
    head = f"// {HEAD.format(name=name)}\n// 1 CSS px = 1 dp. Text sizes are sp, so they follow the user's font scale.\npackage {pkg}\n\n"
    imports = ["androidx.compose.animation.core.CubicBezierEasing", "androidx.compose.foundation.isSystemInDarkTheme",
               "androidx.compose.runtime.Composable", "androidx.compose.runtime.CompositionLocalProvider", "androidx.compose.runtime.Immutable",
               "androidx.compose.runtime.staticCompositionLocalOf", "androidx.compose.ui.graphics.Color", "androidx.compose.ui.text.TextStyle",
               "androidx.compose.ui.text.font.FontFamily", "androidx.compose.ui.text.font.FontWeight",
               "androidx.compose.ui.text.style.LineHeightStyle", "androidx.compose.ui.unit.sp"]
    out = [head + "\n".join(f"import {i}" for i in imports), "",
           "@Immutable", "data class DsColors("] + [f"    val {color_ident(k)}: Color," for k in keys] + [")", ""]
    for theme, T in tokens.items():
        out.append(f"val Ds{_theme_ident(theme)[:1].upper() + _theme_ident(theme)[1:]}Colors = DsColors(")
        out += [f"    {color_ident(k)} = Color(0x{_argb(T['color'].get(k, L['color'][k]))})," for k in keys]
        out += [")", ""]
    _, dark_n, _ = _themes_by_role(tokens)
    cap = lambda t: _theme_ident(t)[:1].upper() + _theme_ident(t)[1:]
    out += ["val DsThemes: Map<String, DsColors> = mapOf(" + ", ".join(f'"{t}" to Ds{cap(t)}Colors' for t in tokens) + ")", "",
            "val LocalDsColors = staticCompositionLocalOf { DsLightColors }" if "light" in tokens else
            f"val LocalDsColors = staticCompositionLocalOf {{ Ds{cap(next(iter(tokens)))}Colors }}", "",
            "object DsTheme {", "    val colors: DsColors", "        @Composable get() = LocalDsColors.current", "}", "",
            "/** Wrap the app (and each snapshot). theme = null follows the system light/dark setting. */",
            "@Composable", "fun DsTheme(theme: String? = null, content: @Composable () -> Unit) {",
            f"    val colors = DsThemes[theme ?: if (isSystemInDarkTheme()) \"{dark_n}\" else \"{next(iter(tokens))}\"] ?: LocalDsColors.current",
            "    CompositionLocalProvider(LocalDsColors provides colors, content = content)", "}", "",
            "object DsDimension {", "    const val androidTouchTarget = 48f"]
    out += [f"    const val {_camel(k)} = {_lit(v)}f" for k, v in L["dimension"].items()]
    out += ["}", "", "object DsOpacity {"] + [f"    const val {_camel(k[8:])} = {_lit(v)}f" for k, v in L["number"].items() if k.startswith("opacity.")]
    out += ["}", "", "/** Durations in ms; honor the system 'Remove animations' setting. */", "object DsMotion {"]
    out += [f"    const val {_camel(k[7:] if k.startswith('motion.') else k)} = {round(v)}" for k, v in L["duration"].items()]
    out += [f"    val {_camel(k[7:] if k.startswith('motion.') else k)} = CubicBezierEasing({', '.join(_lit(x) + 'f' for x in v)})" for k, v in L["easing"].items()]
    out += ["}", "", "/** Elevation in dp, from the CSS shadow blur (blur / 2). Material shadows approximate the CSS ones. */", "object DsElevation {"]
    out += [f"    const val {_camel(k)} = {_lit(max([ly['blur'] / 2 for ly in v if not ly['inset']] or [0]))}f" for k, v in L["shadow"].items()]
    out += ["}", "", "/** Register the DS font files: DsFonts.families = mapOf(\"Inter\" to FontFamily(Font(R.font.inter_regular), ...)). */",
            "object DsFonts {", "    var families: Map<String, FontFamily> = emptyMap()", "    fun family(name: String): FontFamily = families[name] ?: FontFamily.Default", "}", "",
            "/** CSS line-height → lineHeight sp with centered, untrimmed leading (= CSS half-leading). */", "object DsType {",
            "    private val leading = LineHeightStyle(LineHeightStyle.Alignment.Center, LineHeightStyle.Trim.None)"]
    for role, ty in L["typography"].items():
        out.append(f"    val {_camel(role)}: TextStyle get() = TextStyle(fontFamily = DsFonts.family(\"{ty['family']}\"), fontSize = {_lit(ty['size'])}.sp, "
                   f"fontWeight = FontWeight({ty['weight']}), lineHeight = {_lit(ty['lineHeight'])}.sp, lineHeightStyle = leading)")
    out += ["}", ""]
    em = Emitter(tokens, recipes, "kotlin")
    files = {"DsTheme.kt": "\n".join(out),
             "DsComponents.kt": em.fill(_tpl("DsComponents.kt").replace("@HEAD", HEAD.format(name=name)).replace("@PKG", pkg))}
    files["test/DsSnapshotTest.kt"] = compose_snapshots(_snap_cases(components_spec), pkg, tokens)
    return files, em.missing


def compose_snapshots(cases, pkg, tokens):
    def view(file, texts):
        t = lambda i, d: json.dumps(texts[i] if len(texts) > i else d, ensure_ascii=False).replace("$", "\\$")
        return {"button": f"DsButton({t(0, 'Button')}, onClick = {{}})",
                "text-field": f"DsTextField(\"\", {{}}, {t(0, 'Label')}" + (f", hint = {t(1, '')})" if len(texts) > 1 else ")"),
                "checkbox": f"DsCheckbox(false, {{}}, {t(0, 'Checkbox')})",
                "switch": f"DsSwitch(false, {{}}, {t(0, 'Switch')})",
                "card": f"DsCard {{ BasicText({t(0, 'Title')}, style = DsType.{'h5' if 'h5' in tokens['light']['typography'] else 'body'}); BasicText({t(1, 'Body')}, style = DsType.body) }}",
                "badge": f"DsBadge({t(0, 'Badge')})",
                "alert": f"DsAlert({t(0, 'Title')}" + (f", message = {t(1, '')})" if len(texts) > 1 else ")"),
                "avatar": f"DsAvatar({t(0, 'A B')})",
                "tag": f"DsTag({t(0, 'Tag')})",
                "divider": "DsDivider()"}[file]
    tests = []
    for file, demo, theme, texts, width in cases:
        if theme not in tokens:
            continue
        name = ref_name(file, demo, theme)
        fn = re.sub(r"\W", "_", name[:-4])
        mod = f"Modifier.testTag(\"snap\").width({_lit(width)}.dp)" if width and file in SIZED_SNAPS else "Modifier.testTag(\"snap\")"
        tests.append(f"    @Test\n    fun `{fn}`() = snap(\"{name}\", \"{theme}\") {{\n        Box({mod}) {{ {view(file, texts)} }}\n    }}\n")
    return f"""// Generated by ds.py mobile scaffold. Roborazzi + Robolectric at xxhdpi (3x) = the web references' @3x.
// Files land in build/ds-snapshots/<file>--<demo>--<theme>.png; then:
//   python3 ds.py mobile verify <ds-dir> --native app/build/ds-snapshots
// Gradle: testImplementation of io.github.takahirom.roborazzi:roborazzi (+ roborazzi-compose), robolectric,
// androidx.compose.ui:ui-test-junit4 and androidx.test.ext:junit; set unitTests.isIncludeAndroidResources = true.
package {pkg}

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.text.BasicText
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.unit.dp
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.github.takahirom.roborazzi.captureRoboImage
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

@RunWith(AndroidJUnit4::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(qualifiers = "w390dp-h844dp-xxhdpi")
class DsSnapshotTest {{
    @get:Rule val compose = createComposeRule()

    private fun snap(file: String, theme: String, content: @Composable () -> Unit) {{
        compose.setContent {{
            DsTheme(theme) {{ CompositionLocalProvider(LocalDsTouchTarget provides false) {{ content() }} }}
        }}
        compose.onNodeWithTag("snap").captureRoboImage("build/ds-snapshots/$file")
    }}

{chr(10).join(tests)}}}
"""


# ---------- Flutter ----------
DART_RESERVED = {"abstract", "as", "assert", "async", "await", "break", "case", "catch", "class", "const", "continue", "default",
                 "do", "else", "enum", "export", "extends", "external", "factory", "false", "final", "finally", "for", "get", "if",
                 "implements", "import", "in", "is", "library", "new", "null", "operator", "part", "rethrow", "return", "set",
                 "static", "super", "switch", "this", "throw", "true", "try", "var", "void", "while", "with", "yield"}



def _flutter_blur(css_blur):
    """Flutter blurRadius → sigma = 0.57735·r + 0.5; CSS blur b → sigma = b / 2. Solve for r so they match."""
    return max(0.0, (css_blur / 2 - 0.5) / 0.57735) if css_blur > 1 else css_blur


def gen_flutter(tokens, recipes, components_spec, name):
    L = tokens["light"]
    keys = list(L["color"])
    first, dark_n, _ = _themes_by_role(tokens)
    out = [f"// {HEAD.format(name=name)}", "// 1 CSS px = 1 logical px. Text scales with MediaQuery.textScaler.",
           "import 'package:flutter/animation.dart';", "import 'package:flutter/widgets.dart';", "",
           "@immutable", "class DsColors {", "  const DsColors({"] + [f"    required this.{color_ident(k)}," for k in keys] + ["  });", ""]
    out += [f"  final Color {color_ident(k)};" for k in keys] + [""]
    for theme, T in tokens.items():
        out.append(f"  static const {_theme_ident(theme)} = DsColors(")
        out += [f"    {color_ident(k)}: Color(0x{_argb(T['color'].get(k, L['color'][k]))})," for k in keys]
        out += ["  );", ""]
    out += ["  static const themes = <String, DsColors>{" + ", ".join(f"'{t}': {_theme_ident(t)}" for t in tokens) + "};", "}", "",
            "/// Wrap the app (and each golden). Without one, colors follow the platform brightness.",
            "class DsTheme extends InheritedWidget {", "  const DsTheme({super.key, required this.colors, required super.child});", "",
            "  final DsColors colors;", "",
            "  static DsColors of(BuildContext context) =>",
            "      context.dependOnInheritedWidgetOfExactType<DsTheme>()?.colors ??",
            f"      (MediaQuery.maybePlatformBrightnessOf(context) == Brightness.dark ? DsColors.{_theme_ident(dark_n)} : DsColors.{_theme_ident(first)});", "",
            "  @override", "  bool updateShouldNotify(DsTheme oldWidget) => colors != oldWidget.colors;", "}", "",
            "class DsDimension {", "  DsDimension._();", "  static const double androidTouchTarget = 48;"]
    out += [f"  static const double {_camel(k)} = {_lit(v)};" for k, v in L["dimension"].items()]
    out += ["}", "", "class DsOpacity {", "  DsOpacity._();"] + [f"  static const double {_camel(k[8:])} = {_lit(v)};" for k, v in L["number"].items() if k.startswith("opacity.")]
    out += ["}", "", "/// Honor MediaQuery.disableAnimations: use Duration.zero.", "class DsMotion {", "  DsMotion._();"]
    out += [f"  static const {_camel(k[7:] if k.startswith('motion.') else k)} = Duration(milliseconds: {round(v)});" for k, v in L["duration"].items()]
    out += [f"  static const {_camel(k[7:] if k.startswith('motion.') else k)} = Cubic({', '.join(_lit(x) for x in v)});" for k, v in L["easing"].items()]
    out += ["}", "", "/// CSS line-height → height ratio with even leading distribution (= CSS half-leading).", "class DsType {", "  DsType._();"]
    for role, ty in L["typography"].items():
        out.append(f"  static const {_camel(role)} = TextStyle(fontFamily: '{ty['family']}', fontSize: {_lit(ty['size'])}, "
                   f"fontWeight: FontWeight.w{round(ty['weight'] / 100) * 100}, height: {round(ty['lineHeight'] / ty['size'], 4)}, "
                   "leadingDistribution: TextLeadingDistribution.even);")
    out += ["}", "", "/// CSS box-shadow layers. blurRadius converted so Flutter's blur sigma equals the CSS one.", "class DsElevation {", "  DsElevation._();"]
    for k, layers in L["shadow"].items():
        rows = [f"BoxShadow(color: Color(0x{_argb(ly['color'])}), offset: Offset({_lit(ly['x'])}, {_lit(ly['y'])}), "
                f"blurRadius: {_lit(_flutter_blur(ly['blur']))}, spreadRadius: {_lit(ly['spread'])})" for ly in layers if not ly["inset"]]
        out.append(f"  static const {_camel(k)} = <BoxShadow>[{', '.join(rows)}];")
    out += ["}", ""]
    em = Emitter(tokens, recipes, "dart")
    files = {"ds_theme.dart": "\n".join(out), "ds_components.dart": em.fill(_tpl("ds_components.dart").replace("@HEAD", HEAD.format(name=name)))}
    files["test/ds_golden_test.dart"] = flutter_goldens(_snap_cases(components_spec), tokens)
    return files, em.missing


def flutter_goldens(cases, tokens):
    def view(file, texts):
        t = lambda i, d: "'" + (texts[i] if len(texts) > i else d).replace("\\", "\\\\").replace("'", "\\'").replace("$", "\\$") + "'"
        return {"button": f"DsButton({t(0, 'Button')}, onPressed: () {{}})",
                "text-field": f"DsTextField(label: {t(0, 'Label')}" + (f", hint: {t(1, '')})" if len(texts) > 1 else ")"),
                "checkbox": f"DsCheckbox(value: false, onChanged: (_) {{}}, label: {t(0, 'Checkbox')})",
                "switch": f"DsSwitch(value: false, onChanged: (_) {{}}, label: {t(0, 'Switch')})",
                "card": f"DsCard(children: [Text({t(0, 'Title')}, style: DsType.{'h5' if 'h5' in tokens['light']['typography'] else 'body'}), Text({t(1, 'Body')}, style: DsType.body)])",
                "badge": f"DsBadge({t(0, 'Badge')})",
                "alert": f"DsAlert({t(0, 'Title')}" + (f", message: {t(1, '')})" if len(texts) > 1 else ")"),
                "avatar": f"DsAvatar({t(0, 'A B')})",
                "tag": f"DsTag({t(0, 'Tag')})",
                "divider": "const DsDivider()"}[file]
    rows = []
    for file, demo, theme, texts, width in cases:
        if theme not in tokens:
            continue
        name = ref_name(file, demo, theme)[:-4]
        w = f", width: {_lit(width)}" if width and file in SIZED_SNAPS else ""
        rows.append(f"  testWidgets('{name}', (t) => snap(t, '{name}', '{theme}', {view(file, texts)}{w}));")
    return f"""// Generated by ds.py mobile scaffold. Goldens at devicePixelRatio 3 = the web references' @3x, same names.
// Load the real fonts first (flutter_test renders Ahem boxes otherwise), e.g. with FontLoader in setUpAll.
//   flutter test --update-goldens test/ds_golden_test.dart
//   python3 ds.py mobile verify <ds-dir> --native test/goldens
import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';

import '../lib/ds/ds_components.dart'; // adjust to where the scaffold lives
import '../lib/ds/ds_theme.dart';

Future<void> snap(WidgetTester tester, String name, String theme, Widget child, {{double? width}}) async {{
  DsConfig.expandTapTargets = false;
  tester.view.devicePixelRatio = 3;
  tester.view.physicalSize = const Size(390 * 3, 844 * 3);
  addTearDown(tester.view.reset);
  await tester.pumpWidget(MediaQuery(
    data: const MediaQueryData(),
    child: Directionality(
      textDirection: TextDirection.ltr,
      child: DsTheme(
        colors: DsColors.themes[theme]!,
        child: Center(child: RepaintBoundary(key: const ValueKey('snap'), child: SizedBox(width: width, child: child))),
      ),
    ),
  ));
  await expectLater(find.byKey(const ValueKey('snap')), matchesGoldenFile('goldens/$name.png'));
}}

void main() {{
{chr(10).join(rows)}
}}
"""


# ---------- React Native ----------


def _rn_hex(c):
    return "#" + _rgba_hex(c) if c[3] < 1 else "#" + _rgba_hex(c)[:6]


def gen_react_native(tokens, recipes, components_spec, name):
    L = tokens["light"]
    keys = list(L["color"])
    first, dark_n, _ = _themes_by_role(tokens)
    out = [f"// {HEAD.format(name=name)}", "// 1 CSS px = 1 dp. Text scales with the OS font size (allowFontScaling).", ""]
    for theme, T in tokens.items():
        out.append(f"const {_theme_ident(theme)} = {{")
        out += [f"  {color_ident(k)}: '{_rn_hex(T['color'].get(k, L['color'][k]))}'," for k in keys]
        out += ["};", ""]
    out += [f"export type DsColors = typeof {_theme_ident(first)};", "",
            "export const themes: Record<string, DsColors> = { " + ", ".join(f"'{t}': {_theme_ident(t)}" for t in tokens) + " };", "",
            "export const dimension = {", "  androidTouchTarget: 48,"]
    out += [f"  {_camel(k)}: {_lit(v)}," for k, v in L["dimension"].items()]
    out += ["} as const;", "", "export const opacity = {"] + [f"  {_camel(k[8:])}: {_lit(v)}," for k, v in L["number"].items() if k.startswith("opacity.")]
    out += ["} as const;", "", "/** Durations in ms + cubic-bezier control points. Skip animation when AccessibilityInfo.isReduceMotionEnabled(). */",
            "export const motion = {"]
    out += [f"  {_camel(k[7:] if k.startswith('motion.') else k)}: {round(v)}," for k, v in L["duration"].items()]
    out += [f"  {_camel(k[7:] if k.startswith('motion.') else k)}: [{', '.join(_lit(x) for x in v)}] as const," for k, v in L["easing"].items()]
    out += ["} as const;", "", "/** lineHeight is absolute, like the measured web value. */", "export const typography = {"]
    for role, ty in L["typography"].items():
        out.append(f"  {_camel(role)}: {{ fontFamily: '{ty['family']}', fontSize: {_lit(ty['size'])}, fontWeight: '{round(ty['weight'] / 100) * 100}' as const, lineHeight: {_lit(ty['lineHeight'])} }},")
    out += ["} as const;", "", "/** CSS box-shadow strings: React Native 0.76+ (New Architecture) renders boxShadow natively. */", "export const elevation = {"]
    for k, layers in L["shadow"].items():
        css = ", ".join(f"{'inset ' if ly['inset'] else ''}{_lit(ly['x'])}px {_lit(ly['y'])}px {_lit(ly['blur'])}px {_lit(ly['spread'])}px "
                        f"{_rn_hex(ly['color'])}" for ly in layers)
        out.append(f"  {_camel(k)}: {{ boxShadow: '{css}' }},")
    out += ["} as const;", ""]
    em = Emitter(tokens, recipes, "ts")
    comp = _tpl("DsComponents.tsx").replace("@HEAD", HEAD.format(name=name)).replace("@DARK", dark_n).replace("@LIGHT", first)
    files = {"theme.ts": "\n".join(out), "DsComponents.tsx": em.fill(comp)}
    files["DsSnapshots.tsx"] = rn_snapshots(_snap_cases(components_spec), tokens)
    return files, em.missing


def rn_snapshots(cases, tokens):
    def view(file, texts):
        t = lambda i, d: json.dumps(texts[i] if len(texts) > i else d, ensure_ascii=False)
        return {"button": f"<DsButton label={{{t(0, 'Button')}}} onPress={{() => {{}}}} />",
                "text-field": f"<DsTextField label={{{t(0, 'Label')}}}" + (f" hint={{{t(1, '')}}}" if len(texts) > 1 else "") + " value=\"\" onChangeText={() => {}} />",
                "checkbox": f"<DsCheckbox value={{false}} onValueChange={{() => {{}}}} label={{{t(0, 'Checkbox')}}} />",
                "switch": f"<DsSwitch value={{false}} onValueChange={{() => {{}}}} label={{{t(0, 'Switch')}}} />",
                "card": f"<DsCard><Text style={{typography.{'h5' if 'h5' in tokens['light']['typography'] else 'body'}}}>{{{t(0, 'Title')}}}</Text><Text style={{typography.body}}>{{{t(1, 'Body')}}}</Text></DsCard>",
                "badge": f"<DsBadge text={{{t(0, 'Badge')}}} />",
                "alert": f"<DsAlert title={{{t(0, 'Title')}}}" + (f" message={{{t(1, '')}}}" if len(texts) > 1 else "") + " />",
                "avatar": f"<DsAvatar name={{{t(0, 'A B')}}} />",
                "tag": f"<DsTag text={{{t(0, 'Tag')}}} />",
                "divider": "<DsDivider />"}[file]
    rows = []
    for file, demo, theme, texts, width in cases:
        if theme not in tokens:
            continue
        w = _lit(width) if width and file in SIZED_SNAPS else "undefined"
        rows.append(f"  {{ name: '{ref_name(file, demo, theme)}', theme: '{theme}', width: {w}, node: {view(file, texts)} }},")
    return f"""// Generated by ds.py mobile scaffold. A dev-only screen: renders each core component like the web reference
// and captures it at the device scale with react-native-view-shot (use a 3x device, e.g. iPhone 15, for @3x parity).
// Copy the files it logs into one folder, then: python3 ds.py mobile verify <ds-dir> --native <folder>
import React, {{ useRef }} from 'react';
import {{ Button, ScrollView, Text, View }} from 'react-native';
import {{ captureRef }} from 'react-native-view-shot';
import {{ DsAlert, DsAvatar, DsBadge, DsButton, DsCard, DsCheckbox, DsDivider, DsSwitch, DsTag, DsTextField, DsThemeProvider }} from './DsComponents';
import {{ typography }} from './theme';

const cases = [
{chr(10).join(rows)}
];

export default function DsSnapshots() {{
  const refs = useRef<Record<string, View | null>>({{}});
  const capture = async () => {{
    for (const c of cases) {{
      const uri = await captureRef(refs.current[c.name]!, {{ format: 'png', result: 'tmpfile', fileName: c.name.replace(/\\.png$/, '') }});
      console.log(`[ds-snapshot] ${{c.name}} ${{uri}}`);
    }}
  }};
  return (
    <ScrollView contentContainerStyle={{{{ padding: 16, gap: 16 }}}}>
      <Button title="Capture all" onPress={{capture}} />
      {{cases.map((c) => (
        <DsThemeProvider key={{c.name}} theme={{c.theme}}>
          <View ref={{(r) => {{ refs.current[c.name] = r; }}}} collapsable={{false}} style={{{{ alignSelf: 'flex-start', width: c.width }}}}>
            {{c.node}}
          </View>
        </DsThemeProvider>
      ))}}
    </ScrollView>
  );
}}
"""


# ---------- .NET MAUI (resources only) and web-mobile (Ionic / Capacitor / PWA) ----------
def gen_maui(tokens, name):
    L = tokens["light"]
    first, dark_n, _ = _themes_by_role(tokens)
    pas = lambda k: _camel(k)[:1].upper() + _camel(k)[1:]
    rows = [f'<?xml version="1.0" encoding="utf-8" ?>', f"<!-- {HEAD.format(name=name)}", "     Merge into App.xaml: <ResourceDictionary Source=\"DsTokens.xaml\" />.",
            "     Colors: {AppThemeBinding Light={StaticResource XLight}, Dark={StaticResource XDark}}. 1 CSS px = 1 device-independent unit. -->",
            '<ResourceDictionary xmlns="http://schemas.microsoft.com/dotnet/2021/maui" xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml">']
    for k in L["color"]:
        for suffix, T in (("Light", tokens[first]), ("Dark", tokens[dark_n])):
            rows.append(f'    <Color x:Key="Ds{pas(color_ident(k))}{suffix}">#{_argb(T["color"].get(k, L["color"][k]))}</Color>')
    rows += [f'    <x:Double x:Key="Ds{pas(k)}">{_lit(v)}</x:Double>' for k, v in L["dimension"].items()]
    for role, ty in L["typography"].items():
        rows.append(f'    <Style x:Key="DsType{pas(role)}" TargetType="Label"><Setter Property="FontFamily" Value="{ty["family"]}" />'
                    f'<Setter Property="FontSize" Value="{_lit(ty["size"])}" /><Setter Property="LineHeight" Value="{round(ty["lineHeight"] / ty["size"], 3)}" /></Style>')
    rows.append("</ResourceDictionary>")
    return {"DsTokens.xaml": "\n".join(rows) + "\n"}




def fidelity_md(target, recipes, tokens, components_spec, missing, name):
    rows, checks = [], []
    for file, props in recipes.items():
        if file == "_colors":
            continue
        for prop, v in props.items():
            src = {"measured": f"web measurement → {'`' + v['token'] + '`' if v['token'] else '**literal (no token has this value)**'}",
                   "token": f"`{v['token']}` (not measured)", "default": "**fallback default (no token, not measured)**"}[v["source"]]
            rows.append(f"| {file} | {prop} | {_lit(v['value'])} | {src} |")
    colors = tokens["light"]["color"]
    for file, (demo, _, color_checks) in CORE_RECIPES.items():
        box = components_spec.get(file, {}).get(demo, {}).get("light")
        for path, role in color_checks:
            node = box
            for part in path.split("."):
                node = node.get(part) if isinstance(node, dict) else None
            want, key = _css_rgba(node) if isinstance(node, str) else None, pick_color(colors, role)
            if not want or not key:
                continue
            got = colors[key]
            same = max(abs(a - b) for a, b in zip(want, got)) <= 2 / 255 + 1e-6
            over = recipes.get("_colors", {}).get(file, {}).get(role)
            verdict = ("ok" if same else f"web uses `{over['token']}`: generated code follows the web" if over and over["token"]
                       else "**MISMATCH: no semantic token has the web color; fix the web or add a token**")
            checks.append(f"| {file} | {path} | {_hex_from_rgb(want[:3], want[3])} | `{key}` {_hex_from_rgb(got[:3], got[3])} | {verdict} |")
    measured = bool(components_spec)
    return "\n".join([
        f"# {name}: {target} fidelity checklist", "",
        "Generated by `ds.py mobile scaffold`. The web system is the source of truth; this file says where each native number came from.", "",
        "## Status", "",
        f"- Measured spec: {'yes, numbers below come from the web' if measured else '**no**: run `ds.py mobile spec <dir>` (needs Playwright), then re-scaffold'}.",
        f"- Missing tokens: {', '.join('`' + m + '`' for m in sorted(set(missing))) if missing else 'none'}.", "",
        "## Same as web (never adapt)", "",
        "- [ ] Every color, size, radius, border, type style and shadow comes from the generated theme. No literals in screens.",
        "- [ ] Anatomy, variants, states, copy and icons match the web component page.",
        "- [ ] Disabled, loading, error, empty and selected states exist; error is never color alone.",
        "- [ ] Text uses the theme roles; line height matches (the theme already converts CSS line-height).",
        "- [ ] Icons come from the DS icon set (`ds.py icons ... --platforms`), not SF Symbols / Material icons.", "",
        "## Platform idioms (adapt on purpose)", "",
        "- [ ] Hover → pressed state. No hover-only affordances.",
        "- [ ] Touch targets ≥ 44 pt (iOS) / 48 dp (Android): hit area grows, the visual box keeps the web size.",
        "- [ ] Focus ring → platform focus (keyboard/TV/switch control) — keep it visible.",
        "- [ ] Dropdown/select → native picker or bottom sheet; modal → sheet; toast → platform snackbar position; tabs/nav → tab bar / navigation stack.",
        "- [ ] Dynamic Type / font scale on; layouts reflow at 200% text.",
        "- [ ] Safe areas, keyboard avoidance, dark mode and increased contrast.", "",
        "## Verify", "",
        "1. Run the generated snapshot tests (same names as `dist/mobile/reference/*.png`).",
        "2. `python3 ds.py mobile verify <ds-dir> --native <snapshot folder>` → `dist/mobile/fidelity-report.md`; fix drift until it passes.",
        "3. `python3 ds.py mobile lint <native src>` → 0 issues (raw colors, magic numbers, fixed fonts, hover, small targets, foreign icons).", "",
        "## Where each number came from", "", "| Component | Prop | Value | Source |", "|---|---|---|---|", *rows, "",
        "## Web colors vs tokens (light)", "",
        *(["| Component | Measured | Web value | Token | |", "|---|---|---|---|---|", *checks] if checks else ["No measured spec yet."]), ""])


SCAFFOLD_GENERATORS = {"swiftui": "Swift / SwiftUI (iOS 16+)", "compose": "Kotlin / Jetpack Compose", "flutter": "Dart / Flutter 3.10+",
                       "react-native": "TypeScript / React Native (Expo ok)", "maui": ".NET MAUI resources", "web-mobile": "CSS for Ionic/Capacitor/PWA"}


def ensure_mobile_defaults(tokens):
    """Names the generated components rely on, filled from tokens or sane defaults (FIDELITY.md flags the gaps)."""
    for T in tokens.values():
        d, n = T["dimension"], T["number"]
        for k, v in (("size.touch-target", 44), ("icon.size.sm", 16), ("icon.size.md", 20), ("space.1", 4)):
            d.setdefault(k, v)
        d.setdefault("icon.stroke", n.get("icon.stroke", 2))
        n.setdefault("opacity.disabled", 0.5)
        T["duration"].setdefault("motion.duration.fast", 120)
        T["easing"].setdefault("motion.easing.standard", [0.2, 0, 0, 1])
    return tokens


def cmd_mobile_scaffold(a):
    root = Path(a.dir)
    cfg = load_cfg(root)
    build_tokens(root)
    tokens = ensure_mobile_defaults(mobile_tokens(root))
    spec_path = root / "dist" / "mobile" / "spec.json"
    comps = json.loads(spec_path.read_text(encoding="utf-8")).get("components", {}) if spec_path.exists() else {}
    if not comps:
        print("note: no measured spec, so values come from tokens only. For web-exact sizes run `ds.py mobile spec` first.", file=sys.stderr)
    recipes = calibrate(tokens, comps)
    targets = list(SCAFFOLD_GENERATORS) if a.target == "all" else a.target.split(",")
    icons = sprite_symbols(root)
    report = []
    for t in targets:
        if t not in SCAFFOLD_GENERATORS:
            sys.exit(f"unknown target {t}; choose from {', '.join(SCAFFOLD_GENERATORS)} or all")
        out = Path(a.out) / t if a.out and len(targets) > 1 else Path(a.out) if a.out else root / "dist" / "mobile" / t
        missing = []
        if t == "swiftui":
            files, missing = gen_swiftui(tokens, recipes, comps, cfg["name"])
        elif t == "compose":
            files, missing = gen_compose(tokens, recipes, comps, cfg["name"], a.package)
        elif t == "flutter":
            files, missing = gen_flutter(tokens, recipes, comps, cfg["name"])
        elif t == "react-native":
            files, missing = gen_react_native(tokens, recipes, comps, cfg["name"])
        elif t == "maui":
            files = gen_maui(tokens, cfg["name"])
        else:
            files = {"web-mobile.css": _tpl("web-mobile.css")}
        if icons and t in ICON_PLATFORMS:
            files.update({f"icons/{k}": v for k, v in platform_icons(icons, t, a.package).items()})
        if t not in ("maui", "web-mobile"):
            files["FIDELITY.md"] = fidelity_md(t, recipes, tokens, comps, missing, cfg["name"])
        for rel, text in files.items():
            safe_write(out / rel, text)
        if a.out:
            safe_write(out / ".ds-mobile.json", json.dumps({"designSystem": os.path.relpath(root.resolve(), out.resolve()), "target": t}, indent=1) + "\n")
        issues = [i for f in files if Path(f).suffix in MOBILE_LINT and not MOBILE_EXEMPT.match(Path(f).name) for i in mobile_lint_file(out / f)] if not STATE["dry_run"] else []
        report.append(f"{t}: {len(files)} files → {_rel(out)}" + (f" · missing tokens: {', '.join(sorted(set(missing)))}" if missing else "")
                      + (f" · lint: {len(issues)}" if issues else ""))
    print("\n".join(report))
    print("Next: run the snapshot tests, then `ds.py mobile verify <dir> --native <snapshots>`. Build the other components "
          "from dist/mobile/spec.json the same way (references/mobile.md).")


# ---------- icons: library fetch, style, lint, platform components ----------
ICON_SETS = {   # set: (npm package, path inside it, license, license url)
    "lucide": ("lucide-static", "icons/{name}.svg", "ISC", "https://lucide.dev/license"),
    "tabler": ("@tabler/icons", "icons/outline/{name}.svg", "MIT", "https://github.com/tabler/tabler-icons/blob/main/LICENSE"),
    "tabler-filled": ("@tabler/icons", "icons/filled/{name}.svg", "MIT", "https://github.com/tabler/tabler-icons/blob/main/LICENSE"),
    "phosphor": ("@phosphor-icons/core", "assets/regular/{name}.svg", "MIT", "https://github.com/phosphor-icons/core/blob/main/LICENSE"),
    "heroicons": ("heroicons", "24/outline/{name}.svg", "MIT", "https://github.com/tailwindlabs/heroicons/blob/master/LICENSE"),
    "heroicons-solid": ("heroicons", "24/solid/{name}.svg", "MIT", "https://github.com/tailwindlabs/heroicons/blob/master/LICENSE"),
    "material-symbols": ("@material-symbols/svg-400", "outlined/{name}.svg", "Apache-2.0", "https://github.com/google/material-design-icons/blob/master/LICENSE"),
}
ICON_PLATFORMS = ["swiftui", "compose", "flutter", "react-native"]
UNSAFE_SVG = re.compile(r"<script|<foreignObject|\son\w+\s*=|javascript:|<!ENTITY|xlink:href\s*=\s*\"(?!#)", re.I)


def _http_get(url, timeout=20):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "html-design-system/ds.py"})
    with urllib.request.urlopen(req, timeout=timeout) as r:   # noqa: S310 - fixed CDN or user-set mirror
        return r.read(300_000)


def cmd_icons_add(a):
    root = Path(a.dir)
    load_cfg(root)
    if a.set not in ICON_SETS:
        sys.exit(f"unknown set {a.set}; choose from {', '.join(ICON_SETS)}")
    pkg, path, lic, lic_url = ICON_SETS[a.set]
    cdn = os.environ.get("DS_ICON_CDN", "https://cdn.jsdelivr.net/npm").rstrip("/")
    version = a.version
    if not version:
        if "DS_ICON_CDN" in os.environ:
            version = "latest"
        else:
            try:
                version = json.loads(_http_get(f"https://data.jsdelivr.com/v1/packages/npm/{pkg}/resolved?specifier=latest"))["version"]
            except Exception as e:  # noqa: BLE001
                sys.exit(f"could not resolve the {pkg} version ({e}); pass --version")
    src = root / "icons" / "src"
    lic_file = root / "icons" / "LICENSES.md"
    existing = lic_file.read_text(encoding="utf-8") if lic_file.exists() else ""
    others = [s for s in ICON_SETS if s != a.set and f"| {s} |" in existing and ICON_SETS[s][0] != pkg]
    if others:
        print(f"warning: icons/src already has icons from {', '.join(others)}. Mixing sets breaks stroke, corner and "
              "proportion consistency; prefer one set, or check new icons with `ds.py icons-lint --style`.", file=sys.stderr)
    got, failed = [], []
    for raw_name in a.names:
        name = raw_name.strip().lower()
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", name):
            failed.append(f"{raw_name}: invalid name")
            continue
        url = f"{cdn}/{pkg}@{version}/{path.format(name=name)}"
        try:
            text = _http_get(url).decode("utf-8")
        except Exception as e:  # noqa: BLE001
            failed.append(f"{name}: {e}")
            continue
        body = re.sub(r"<!--.*?-->", "", text, flags=re.S).strip()
        if not body.startswith("<svg") or UNSAFE_SVG.search(body):
            failed.append(f"{name}: not a plain SVG")
            continue
        safe_write(src / f"{name.replace('_', '-')}.svg", text, kind="owned")
        got.append(name)
    if got and f"| {a.set} |" not in existing:
        head = "" if existing else ("# Icon licenses\n\nRecorded by `ds.py icons-add`. Keep this file with the icons.\n\n"
                                    "| Set | Package | License | |\n|---|---|---|---|\n")
        safe_write(lic_file, existing + head + f"| {a.set} | {pkg}@{version} | {lic} | {lic_url} |\n", kind="owned")
    print(f"{len(got)} icon(s) from {a.set} ({pkg}@{version}, {lic}) → icons/src/" + (f"; failed: {'; '.join(failed)}" if failed else ""))
    if got:
        build_icons(root, src, f"{a.set} ({lic}); see icons/LICENSES.md", a.platforms)
    if failed and not got:
        sys.exit(1)


# --- SVG geometry (stdlib): shapes → path data, path → points, bbox ---
def _f(el, k, d=0.0):
    try:
        return float(re.sub(r"px$", "", el.get(k, d) if isinstance(el.get(k, d), str) else str(el.get(k, d))))
    except ValueError:
        return d


def shape_to_d(el):
    tag = el.tag.split("}")[-1]
    if tag == "path":
        return el.get("d", "")
    if tag == "line":
        return f"M{_lit(_f(el, 'x1'))} {_lit(_f(el, 'y1'))}L{_lit(_f(el, 'x2'))} {_lit(_f(el, 'y2'))}"
    if tag in ("polyline", "polygon"):
        nums = re.findall(r"-?\d*\.?\d+(?:e-?\d+)?", el.get("points", ""))
        pts = [f"{nums[i]} {nums[i + 1]}" for i in range(0, len(nums) - 1, 2)]
        return ("M" + "L".join(pts) + ("Z" if tag == "polygon" else "")) if pts else ""
    if tag == "rect":
        x, y, w, h = _f(el, "x"), _f(el, "y"), _f(el, "width"), _f(el, "height")
        rx = _f(el, "rx", _f(el, "ry"))
        ry = _f(el, "ry", rx)
        rx, ry = min(rx, w / 2), min(ry, h / 2)
        if not rx:
            return f"M{_lit(x)} {_lit(y)}H{_lit(x + w)}V{_lit(y + h)}H{_lit(x)}Z"
        a_ = lambda ex, ey: f"A{_lit(rx)} {_lit(ry)} 0 0 1 {_lit(ex)} {_lit(ey)}"
        return (f"M{_lit(x + rx)} {_lit(y)}H{_lit(x + w - rx)}{a_(x + w, y + ry)}V{_lit(y + h - ry)}{a_(x + w - rx, y + h)}"
                f"H{_lit(x + rx)}{a_(x, y + h - ry)}V{_lit(y + ry)}{a_(x + rx, y)}Z")
    if tag in ("circle", "ellipse"):
        cx, cy = _f(el, "cx"), _f(el, "cy")
        rx = _f(el, "r") if tag == "circle" else _f(el, "rx")
        ry = _f(el, "r") if tag == "circle" else _f(el, "ry")
        return (f"M{_lit(cx - rx)} {_lit(cy)}A{_lit(rx)} {_lit(ry)} 0 1 0 {_lit(cx + rx)} {_lit(cy)}"
                f"A{_lit(rx)} {_lit(ry)} 0 1 0 {_lit(cx - rx)} {_lit(cy)}Z")
    return ""


def _arc_points(x1, y1, rx, ry, phi, fa, fs, x2, y2, n=12):
    """Points along an SVG arc (endpoint → center parameterization, SVG spec F.6.5)."""
    import math
    if not rx or not ry:
        return [(x2, y2)]
    rx, ry, p = abs(rx), abs(ry), math.radians(phi)
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p, y1p = math.cos(p) * dx + math.sin(p) * dy, -math.sin(p) * dx + math.cos(p) * dy
    lam = x1p ** 2 / rx ** 2 + y1p ** 2 / ry ** 2
    if lam > 1:
        rx, ry = rx * lam ** 0.5, ry * lam ** 0.5
    num = rx ** 2 * ry ** 2 - rx ** 2 * y1p ** 2 - ry ** 2 * x1p ** 2
    co = (max(0, num) / (rx ** 2 * y1p ** 2 + ry ** 2 * x1p ** 2 or 1)) ** 0.5 * (-1 if fa == fs else 1)
    cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
    cx, cy = math.cos(p) * cxp - math.sin(p) * cyp + (x1 + x2) / 2, math.sin(p) * cxp + math.cos(p) * cyp + (y1 + y2) / 2
    ang = lambda ux, uy, vx, vy: math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
    t1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not fs and dt > 0:
        dt -= 2 * math.pi
    elif fs and dt < 0:
        dt += 2 * math.pi
    return [(cx + rx * math.cos(t1 + dt * i / n) * math.cos(p) - ry * math.sin(t1 + dt * i / n) * math.sin(p),
             cy + rx * math.cos(t1 + dt * i / n) * math.sin(p) + ry * math.sin(t1 + dt * i / n) * math.cos(p)) for i in range(1, n + 1)]


def path_points(d):
    """(points incl. control points, number of commands) for a path's d attribute."""
    toks = re.findall(r"[MmLlHhVvCcSsQqTtAaZz]|-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", d)
    nargs = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7, "Z": 0}
    pts, cmds, i, cmd, x, y, sx, sy = [], 0, 0, None, 0.0, 0.0, 0.0, 0.0
    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]
            i += 1
            cmds += 1
            if cmd in "Zz":
                x, y = sx, sy
                continue
        if cmd is None or cmd in "Zz":
            break
        up, rel, n = cmd.upper(), cmd.islower(), nargs[cmd.upper()]
        if i + n > len(toks) or any(t.isalpha() for t in toks[i:i + n]):
            break
        v = [float(t) for t in toks[i:i + n]]
        i += n
        if up == "H":
            x = v[0] + (x if rel else 0)
            pts.append((x, y))
        elif up == "V":
            y = v[0] + (y if rel else 0)
            pts.append((x, y))
        elif up == "A":
            ex, ey = v[5] + (x if rel else 0), v[6] + (y if rel else 0)
            pts += _arc_points(x, y, v[0], v[1], v[2], int(v[3]), int(v[4]), ex, ey)
            x, y = ex, ey
        else:
            for k in range(0, n, 2):
                pts.append((v[k] + (x if rel else 0), v[k + 1] + (y if rel else 0)))
            x, y = pts[-1]
            if up == "M":
                sx, sy = x, y
                cmd = "l" if rel else "L"
    return pts, cmds


def _svg_root(text):
    import xml.etree.ElementTree as ET
    return ET.fromstring(re.sub(r"<!--.*?-->", "", text, flags=re.S))


def svg_facts(text):
    """Measured style facts of one icon: viewBox, paint model, stroke, caps/joins, geometry bbox, complexity."""
    root = _svg_root(text)
    vb = [float(x) for x in re.findall(r"-?\d*\.?\d+", root.get("viewBox") or f"0 0 {root.get('width', 24)} {root.get('height', 24)}")]
    facts = {"viewBox": vb, "strokeWidths": set(), "caps": set(), "joins": set(), "fills": set(), "strokes": set(),
             "forbidden": set(), "transforms": 0, "elements": 0, "commands": 0, "points": [], "rx": []}

    def walk(el, inherited):
        paint = dict(inherited)
        for k in ("fill", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin"):
            if el.get(k) is not None:
                paint[k] = el.get(k)
        if el.get("style"):
            facts["forbidden"].add("style attribute")
        if el.get("transform"):
            facts["transforms"] += 1
        tag = el.tag.split("}")[-1]
        if tag in ("text", "image", "foreignObject", "script", "style", "filter", "use", "mask", "pattern"):
            facts["forbidden"].add(tag)
        d = shape_to_d(el) if el is not root else ""
        if d:
            facts["elements"] += 1
            pts, n = path_points(d)
            facts["points"] += pts
            facts["commands"] += n
            fill, stroke = paint.get("fill", "black"), paint.get("stroke", "none")
            facts["fills"].add(fill)
            facts["strokes"].add(stroke)
            if stroke != "none":
                facts["strokeWidths"].add(float(re.sub(r"px$", "", str(paint.get("stroke-width", 1)))))
                facts["caps"].add(paint.get("stroke-linecap", "butt"))
                facts["joins"].add(paint.get("stroke-linejoin", "miter"))
            if tag == "rect" and el.get("rx"):
                facts["rx"].append(_f(el, "rx"))
        for ch in el:
            walk(ch, paint)

    walk(root, {})
    xs, ys = [p[0] for p in facts["points"]], [p[1] for p in facts["points"]]
    facts["bbox"] = [min(xs), min(ys), max(xs), max(ys)] if xs else None
    facts["model"] = ("stroke" if facts["strokes"] - {"none"} and facts["fills"] <= {"none"} else
                      "fill" if facts["strokes"] <= {"none"} else "mixed")
    return facts


def _mode(values, default=None):
    vals = [v for v in values if v is not None]
    return max(set(vals), key=vals.count) if vals else default


def _pct(values, q):
    vals = sorted(values)
    return vals[min(len(vals) - 1, int(q * (len(vals) - 1)))] if vals else None


def icon_style_from_ds(root):
    tokens = mobile_tokens(root)["light"]
    radius = tokens["dimension"].get("radius.md", tokens["dimension"].get("radius.sm", 4))
    rounded = radius >= 4
    return {"source": "derived from design-system tokens (no reference icons)", "grid": 24, "viewBox": [0, 0, 24, 24],
            "model": "stroke", "strokeWidth": tokens["number"].get("icon.stroke", 2), "linecap": "round" if rounded else "square",
            "linejoin": "round" if rounded else "miter", "padding": 2, "cornerRadius": 2 if rounded else 0,
            "complexity": [1, 12], "notes": ["Draw on the 24 grid; keep geometry inside the 2 px padding (live area 20 × 20).",
                                             "Use only currentColor; no fills in a stroke set; whole or half-pixel coordinates."]}


def cmd_icons_style(a):
    files = sorted(Path(a.src).rglob("*.svg")) if a.src else []
    if a.dir:
        load_cfg(Path(a.dir))
    if files:
        facts = []
        for f in files:
            try:
                facts.append(svg_facts(f.read_text(encoding="utf-8", errors="ignore")))
            except Exception:  # noqa: BLE001 - skip unparsable icons
                continue
        vb = _mode([tuple(x["viewBox"]) for x in facts], (0, 0, 24, 24))
        pads = [min(x["bbox"][0] - vb[0], x["bbox"][1] - vb[1], vb[0] + vb[2] - x["bbox"][2], vb[1] + vb[3] - x["bbox"][3])
                for x in facts if x["bbox"] and tuple(x["viewBox"]) == vb]
        sizes = [x["elements"] + x["commands"] for x in facts]
        style = {"source": f"{len(facts)} icons in {Path(a.src).name}/", "grid": vb[2], "viewBox": list(vb),
                 "model": _mode([x["model"] for x in facts], "stroke"),
                 "strokeWidth": _mode([w for x in facts for w in x["strokeWidths"]], None),
                 "linecap": _mode([c for x in facts for c in x["caps"]], None), "linejoin": _mode([j for x in facts for j in x["joins"]], None),
                 "padding": round(max(0, _pct(pads, 0.1) or 0), 2), "cornerRadius": _pct([r for x in facts for r in x["rx"]], 0.5),
                 "complexity": [_pct(sizes, 0.05), _pct(sizes, 0.95)],
                 "notes": ["Thresholds are the 10th percentile padding and the 5th–95th percentile complexity of the reference set."]}
    elif a.dir:
        style = icon_style_from_ds(Path(a.dir))
    else:
        sys.exit("give a folder of reference .svg icons, or --dir <design system> to derive the style from tokens")
    tidy = lambda v: int(v) if isinstance(v, float) and v.is_integer() else [tidy(x) for x in v] if isinstance(v, list) else v
    text = json.dumps({k: tidy(v) for k, v in style.items()}, indent=1, ensure_ascii=False) + "\n"
    if a.dir:
        safe_write(Path(a.dir) / "icons" / "style.json", text, kind="owned")
        print(f"icons/style.json: {style['model']} icons on a {_lit(style['grid'])} grid, stroke {style['strokeWidth']}, "
              f"caps {style['linecap']}, joins {style['linejoin']}, padding {style['padding']} ({style['source']}).")
    else:
        print(text)


def icon_issues(text, style):
    """(errors, warnings) for one SVG against a style.json — the guardrail for icons drawn from scratch."""
    errs, warns = [], []
    if UNSAFE_SVG.search(text):
        errs.append("unsafe content (script, event handler, external reference or entity)")
    try:
        f = svg_facts(text)
    except Exception as e:  # noqa: BLE001
        return [f"not parseable SVG: {e}"], []
    vb = style.get("viewBox") or [0, 0, 24, 24]
    if [round(v, 3) for v in f["viewBox"]] != [round(v, 3) for v in vb]:
        errs.append(f"viewBox {' '.join(_lit(v) for v in f['viewBox'])} ≠ {' '.join(_lit(v) for v in vb)}")
    paints = (f["fills"] | f["strokes"]) - {"none", "currentColor"}
    if paints:
        errs.append(f"hard-coded paint {', '.join(sorted(paints))}: use currentColor")
    if f["forbidden"]:
        errs.append(f"not allowed: {', '.join(sorted(f['forbidden']))}")
    if f["transforms"]:
        warns.append(f"{f['transforms']} transform(s): bake them into the coordinates")
    if style.get("model") and f["model"] != style["model"]:
        errs.append(f"paint model {f['model']} ≠ {style['model']}")
    if style.get("model") == "stroke":
        sw = style.get("strokeWidth")
        if sw and any(abs(w - sw) > 0.01 for w in f["strokeWidths"]):
            errs.append(f"stroke-width {', '.join(_lit(w) for w in sorted(f['strokeWidths']))} ≠ {_lit(sw)}")
        for k, key in (("caps", "linecap"), ("joins", "linejoin")):
            if style.get(key) and f[k] - {style[key]}:
                errs.append(f"stroke-{key} {', '.join(sorted(f[k]))} ≠ {style[key]}")
    if f["bbox"]:
        pad, (x0, y0, x1, y1) = style.get("padding", 0) or 0, f["bbox"]
        if x0 < vb[0] - 0.01 or y0 < vb[1] - 0.01 or x1 > vb[0] + vb[2] + 0.01 or y1 > vb[1] + vb[3] + 0.01:
            errs.append("geometry outside the viewBox")
        elif min(x0 - vb[0], y0 - vb[1], vb[0] + vb[2] - x1, vb[1] + vb[3] - y1) < pad - 0.5:
            warns.append(f"geometry enters the {_lit(pad)} px padding (bbox {', '.join(_lit(v) for v in f['bbox'])})")
    else:
        errs.append("no drawable geometry")
    lo, hi = (list(style.get("complexity") or []) + [None, None])[:2]
    size = f["elements"] + f["commands"]
    if hi and size > hi * 1.5:
        warns.append(f"complexity {size} well above the set (≤ {hi}): simplify for small sizes")
    if lo and size < lo:
        warns.append(f"complexity {size} below the set ({lo}+): may look lighter than its neighbors")
    return errs, warns


def cmd_icons_lint(a):
    style_path = Path(a.style) if a.style else (Path(a.dir) / "icons" / "style.json" if a.dir else None)
    if not style_path or not style_path.exists():
        sys.exit("needs a style: --style icons/style.json, or --dir <design system> (run `ds.py icons-style` first)")
    style = json.loads(style_path.read_text(encoding="utf-8"))
    files = [f for p_ in map(Path, a.paths) for f in ([p_] if p_.is_file() else sorted(p_.rglob("*.svg")))]
    n_err = 0
    for f in files:
        errs, warns = icon_issues(f.read_text(encoding="utf-8", errors="ignore"), style)
        n_err += bool(errs)
        for m in errs:
            print(f"- {f.name}: error: {m}")
        for m in warns:
            print(f"- {f.name}: warning: {m}")
    print(f"{len(files) - n_err}/{len(files)} icon(s) match {style_path} ({style.get('source', '')}).")
    if n_err:
        sys.exit(1)


# --- platform icon components from the optimized sprite ---
def sprite_symbols(root):
    """[(name, viewBox, root paint attrs, inner XML)] from dist/icons.svg."""
    p = Path(root) / "dist" / "icons.svg"
    if not p.exists():
        return []
    out = []
    for m in re.finditer(r'<symbol id="icon-([^"]+)" viewBox="([^"]+)"([^>]*)>(.*?)</symbol>', p.read_text(encoding="utf-8"), re.S):
        attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', m.group(3)))
        out.append((m.group(1), m.group(2), attrs, m.group(4)))
    return out


def _svg_doc(view_box, attrs, inner, color=None):
    vb = view_box.split()
    paint = "".join(f' {k}="{(color if color and v == "currentColor" else v)}"' for k, v in attrs.items())
    body = inner.replace('"currentColor"', f'"{color}"') if color else inner
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{vb[2]}" height="{vb[3]}" viewBox="{view_box}"{paint}>{body}</svg>'


def _icon_paths(attrs, inner):
    """Flatten an icon into [{d, fill, stroke, width, cap, join}] with inherited paint (for VectorDrawable / ImageVector)."""
    import xml.etree.ElementTree as ET
    root = ET.fromstring(f"<g>{inner}</g>")
    out = []

    def walk(el, paint):
        paint = {**paint, **{k: el.get(k) for k in ("fill", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin") if el.get(k)}}
        d = shape_to_d(el) if el.tag != "g" else ""
        if d:
            out.append({"d": d, "fill": paint.get("fill", "currentColor") != "none", "stroke": paint.get("stroke", "none") != "none",
                        "width": float(paint.get("stroke-width", 1)), "cap": paint.get("stroke-linecap", "butt"),
                        "join": paint.get("stroke-linejoin", "miter")})
        for ch in el:
            walk(ch, paint)

    walk(root, {"fill": attrs.get("fill", "currentColor"), **{k: v for k, v in attrs.items() if k != "fill"}})
    return out


def _ident(name, lang):
    base = _camel(name.replace("_", "-"))
    if base[:1].isdigit():
        base = "i" + base
    if lang == "kotlin":
        return base[:1].upper() + base[1:]
    if lang == "swift" and base in {"repeat", "case", "default", "import", "return", "switch", "class", "func", "if", "else", "for",
                                    "in", "is", "let", "var", "while", "do", "self", "super", "true", "false", "nil", "where", "as"}:
        return f"`{base}`"
    if lang == "dart" and base in DART_RESERVED:
        return base + "Icon"
    return base


def platform_icons(symbols, platform, pkg="design.system"):
    files = {}
    if platform == "swiftui":
        files["Icons.xcassets/Contents.json"] = json.dumps({"info": {"author": "xcode", "version": 1}}, indent=1) + "\n"
        cases = []
        for name, vb, attrs, inner in symbols:
            files[f"Icons.xcassets/{name}.imageset/{name}.svg"] = _svg_doc(vb, attrs, inner, "#000000") + "\n"
            files[f"Icons.xcassets/{name}.imageset/Contents.json"] = json.dumps(
                {"images": [{"filename": f"{name}.svg", "idiom": "universal"}], "info": {"author": "xcode", "version": 1},
                 "properties": {"preserves-vector-representation": True, "template-rendering-intent": "template"}}, indent=1) + "\n"
            cases.append(f'    case {_ident(name, "swift")} = "{name}"')
        files["DSIcon.swift"] = ("// Generated by ds.py icons --platforms swiftui. Add Icons.xcassets to the app target.\nimport SwiftUI\n\n"
                                 "public enum DSIcon: String, CaseIterable {\n" + "\n".join(cases) + "\n\n"
                                 "    public var image: Image { Image(rawValue).renderingMode(.template) }\n}\n\n"
                                 "/// Decorative unless a label is given (then it is announced as an image).\n"
                                 "public struct DSIconView: View {\n    let icon: DSIcon\n    var size: CGFloat = 24\n    var label: String?\n\n"
                                 "    public init(_ icon: DSIcon, size: CGFloat = 24, label: String? = nil) {\n"
                                 "        self.icon = icon\n        self.size = size\n        self.label = label\n    }\n\n"
                                 "    public var body: some View {\n        icon.image.resizable().scaledToFit().frame(width: size, height: size)\n"
                                 "            .accessibilityLabel(label ?? \"\").accessibilityHidden(label == nil)\n    }\n}\n")
    elif platform == "compose":
        vals = []
        for name, vb, attrs, inner in symbols:
            _, _, w, h = vb.split()
            paths = _icon_paths(attrs, inner)
            vd = [f'<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="{w}dp" android:height="{h}dp" '
                  f'android:viewportWidth="{w}" android:viewportHeight="{h}" android:tint="?attr/colorControlNormal">']
            adds = []
            for p_ in paths:
                vd.append(f'    <path android:pathData="{p_["d"]}"' + (' android:fillColor="#FF000000"' if p_["fill"] else "")
                          + (f' android:strokeColor="#FF000000" android:strokeWidth="{_lit(p_["width"])}" android:strokeLineCap="{p_["cap"]}"'
                             f' android:strokeLineJoin="{p_["join"]}"' if p_["stroke"] else "") + " />")
                cap = {"round": "Round", "square": "Square"}.get(p_["cap"], "Butt")
                join = {"round": "Round", "bevel": "Bevel"}.get(p_["join"], "Miter")
                adds.append(f'            addPath(addPathNodes("{p_["d"]}"), fill = {"SolidColor(Color.Black)" if p_["fill"] else "null"}, '
                            + (f"stroke = SolidColor(Color.Black), strokeLineWidth = {_lit(p_['width'])}f, strokeLineCap = StrokeCap.{cap}, "
                               f"strokeLineJoin = StrokeJoin.{join})" if p_["stroke"] else "stroke = null)"))
            vd.append("</vector>")
            files[f"drawable/ds_icon_{name.replace('-', '_')}.xml"] = "\n".join(vd) + "\n"
            vals.append(f"    val {_ident(name, 'kotlin')}: ImageVector by lazy {{\n        ImageVector.Builder(\"{name}\", {w}.dp, {h}.dp, {w}f, {h}f).apply {{\n"
                        + "\n".join(adds) + "\n        }.build()\n    }")
        files["DsIcons.kt"] = (f"// Generated by ds.py icons --platforms compose. Tint with Icon(DsIcons.X, contentDescription, tint = ...).\n"
                               f"package {pkg}\n\nimport androidx.compose.ui.graphics.Color\nimport androidx.compose.ui.graphics.SolidColor\n"
                               "import androidx.compose.ui.graphics.StrokeCap\nimport androidx.compose.ui.graphics.StrokeJoin\n"
                               "import androidx.compose.ui.graphics.vector.ImageVector\nimport androidx.compose.ui.graphics.vector.addPathNodes\n"
                               "import androidx.compose.ui.unit.dp\n\nobject DsIcons {\n" + "\n\n".join(vals) + "\n}\n")
    elif platform == "flutter":
        consts = [f"  static const {_ident(n, 'dart')} = r'''{_svg_doc(vb, at, inner)}''';" for n, vb, at, inner in symbols]
        files["ds_icons.dart"] = ("// Generated by ds.py icons --platforms flutter. Needs flutter_svg.\n"
                                  "import 'package:flutter/widgets.dart';\nimport 'package:flutter_svg/flutter_svg.dart';\n\n"
                                  "class DsIcons {\n  DsIcons._();\n" + "\n".join(consts) + "\n\n  static const all = <String, String>{"
                                  + ", ".join(f"'{n}': {_ident(n, 'dart')}" for n, *_ in symbols) + "};\n}\n\n"
                                  "/// Decorative unless semanticLabel is set. Color defaults to IconTheme (like Icon).\n"
                                  "class DsIcon extends StatelessWidget {\n"
                                  "  const DsIcon(this.svg, {super.key, this.size = 24, this.color, this.semanticLabel});\n\n"
                                  "  final String svg;\n  final double size;\n  final Color? color;\n  final String? semanticLabel;\n\n"
                                  "  @override\n  Widget build(BuildContext context) {\n"
                                  "    final c = color ?? IconTheme.of(context).color ?? const Color(0xFF000000);\n"
                                  "    return SvgPicture.string(svg, width: size, height: size, colorFilter: ColorFilter.mode(c, BlendMode.srcIn),\n"
                                  "        semanticsLabel: semanticLabel, excludeFromSemantics: semanticLabel == null);\n  }\n}\n")
    elif platform == "react-native":
        rows = [f"  {json.dumps(n)}: {json.dumps(_svg_doc(vb, at, inner))}," for n, vb, at, inner in symbols]
        files["DsIcon.tsx"] = ("// Generated by ds.py icons --platforms react-native. Needs react-native-svg.\n"
                               "import React from 'react';\nimport { SvgXml } from 'react-native-svg';\n\n"
                               "const icons = {\n" + "\n".join(rows) + "\n} as const;\n\nexport type DsIconName = keyof typeof icons;\n\n"
                               "/** Decorative unless accessibilityLabel is set. color fills currentColor. */\n"
                               "export function DsIcon({ name, size = 24, color, accessibilityLabel }: { name: DsIconName; size?: number; color?: string; accessibilityLabel?: string }) {\n"
                               "  return (\n    <SvgXml xml={icons[name]} width={size} height={size} color={color} accessible={!!accessibilityLabel}\n"
                               "      accessibilityLabel={accessibilityLabel} accessibilityRole={accessibilityLabel ? 'image' : undefined} />\n  );\n}\n")
    return files


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
    # Docs chrome and templates (docs/, _*.html) hold deliberate "don't" examples — they aren't product UI.
    files = [root] if root.is_file() else [p_ for p_ in root.rglob("*") if p_.suffix in exts and not set(p_.parts) & SKIP_DIRS
                                           and "docs" not in p_.relative_to(root).parts and not p_.name.startswith("_")]
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


# ---------- playwright: visual regression + axe, free and local ----------
PLAYWRIGHT_CONFIG = """// Generated by ds.py playwright — free visual regression + accessibility for every docs page.
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  snapshotPathTemplate: '{testDir}/__screenshots__/{projectName}/{arg}{ext}',
  expect: { toHaveScreenshot: { maxDiffPixelRatio: 0.002, animations: 'disabled' } },
  use: { baseURL: 'http://127.0.0.1:4173', reducedMotion: 'reduce', colorScheme: 'light' },
  projects: [{ name: 'chromium', use: { browserName: 'chromium', viewport: { width: 1280, height: 900 } } },
             { name: 'mobile', use: { browserName: 'chromium', viewport: { width: 390, height: 844 }, isMobile: true } }],
  webServer: { command: '__SERVE__', url: 'http://127.0.0.1:4173/index.html', reuseExistingServer: true },
});
"""

PLAYWRIGHT_SPEC = """// Generated by ds.py playwright. Baselines: npx playwright test --update-snapshots (commit tests/__screenshots__).
// Run baselines and checks on the same OS (use the Playwright Docker image in CI) — fonts render differently per OS.
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { readdirSync, existsSync } from 'node:fs';

const pages = ['components', 'patterns'].filter((d) => existsSync(d))
  .flatMap((d) => readdirSync(d).filter((f) => f.endsWith('.html')).map((f) => `${d}/${f}`));
const themes = __THEMES__;

async function open(page, url, theme, dir = 'ltr') {
  // Deterministic: no transition/animation ever runs (installed before any page content), so axe and
  // screenshots always read final colors — never a surface caught mid-fade.
  await page.addInitScript(() => {
    const style = document.createElement('style');
    style.textContent = '*,*::before,*::after{transition:none!important;animation:none!important}';
    (document.head || document.documentElement).appendChild(style);
  });
  await page.goto(`/${url}`);
  await page.evaluate(([t, d]) => {
    t === 'light' ? document.documentElement.removeAttribute('data-theme') : document.documentElement.setAttribute('data-theme', t);
    document.documentElement.dir = d;
  }, [theme, dir]);
  await page.evaluate(() => document.fonts.ready);
  // Let style recalculation settle after the theme switch; without it axe can read a half-applied theme.
  await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  // Wait until nothing is animating (e.g. a popover fading in): axe blends text with half-transparent surfaces.
  await page.waitForFunction(() => document.getAnimations().every((a) => a.playState !== 'running'));
}

for (const url of pages) {
  for (const theme of themes) {
    test(`visual ${url} [${theme}]`, async ({ page }) => {
      await open(page, url, theme);
      await expect(page).toHaveScreenshot(`${url.replace(/[\\\\/]/g, '__')}--${theme}.png`, { fullPage: true });
    });
    test(`a11y ${url} [${theme}]`, async ({ page }) => {
      await open(page, url, theme);
      const { violations } = await new AxeBuilder({ page }).disableRules(['region']).analyze();
      expect(violations.flatMap((v) => v.nodes.map((n) => `${v.id}: ${n.target} ${(n.any[0] || {}).message || ''}`))).toEqual([]);
    });
  }
  test(`visual ${url} [rtl]`, async ({ page }) => {
    await open(page, url, 'light', 'rtl');
    await expect(page).toHaveScreenshot(`${url.replace(/[\\\\/]/g, '__')}--rtl.png`, { fullPage: true });
  });
  test(`keyboard ${url}: focus is always visible`, async ({ page }) => {
    await open(page, url, 'light');
    for (let i = 0; i < 15; i++) {
      await page.keyboard.press('Tab');
      const ok = await page.evaluate(() => {
        const el = document.activeElement;
        if (!el || el === document.body) return true;
        const cs = getComputedStyle(el);
        return cs.outlineStyle !== 'none' || cs.boxShadow !== 'none';
      });
      expect(ok, `focused element ${i + 1} has no visible focus indicator`).toBe(true);
    }
  });
}
"""


def cmd_playwright(a):
    root = Path(a.dir)
    load_cfg(root)
    _, themes = load_tokens(root)
    serve = ("python3 tools/ds/scripts/ds.py serve . --port 4173" if (root / "tools" / "ds").exists()
             else f"python3 {json.dumps(str(SKILL / 'scripts' / 'ds.py'))[1:-1]} serve . --port 4173")
    write_if_missing(root / "playwright.config.mjs", PLAYWRIGHT_CONFIG.replace("__SERVE__", serve), a.force)
    write_if_missing(root / "tests" / "design-system.spec.mjs",
                     PLAYWRIGHT_SPEC.replace("__THEMES__", json.dumps(["light", *[t for t in themes if t != "light"]])), a.force)

    def update(pkg):
        pkg.setdefault("devDependencies", {}).setdefault("@playwright/test", "^1.56.0")
        pkg["devDependencies"].setdefault("@axe-core/playwright", "^4.11.0")
        pkg.setdefault("scripts", {}).setdefault("test:ui", "playwright test")
        pkg["scripts"].setdefault("test:ui:update", "playwright test --update-snapshots")
    merge_json(root / "package.json", update, "Playwright devDependencies/scripts")
    append_lines(root / ".gitignore", ["test-results/", "playwright-report/"])
    print("Playwright suite ready: visual (every page × theme + RTL, desktop + mobile), axe a11y, keyboard focus.\n"
          f"  cd {root} && npm install && npx playwright install chromium && npm run test:ui:update   # first baselines\n"
          "  npm run test:ui                                                                              # then on every change\n"
          "Commit tests/__screenshots__. Create baselines on the same OS as CI (Playwright Docker image).")


# ---------- hooks ----------
def read_hook_input():
    try:
        return json.load(sys.stdin)
    except Exception:  # noqa: BLE001 - hooks must never crash the session
        return {}


def hook_post_edit():
    data = read_hook_input()
    fp = (data.get("tool_input") or {}).get("file_path") or ""
    if fp and Path(fp).suffix in MOBILE_LINT:
        return hook_native_edit(fp)
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


def hook_native_edit(fp):
    """Lint native (Swift/Kotlin/Dart/RN) edits inside a scaffolded mobile app (.ds-mobile.json) or a design system."""
    path = Path(fp).resolve()
    inside = any((p_ / ".ds-mobile.json").exists() for p_ in list(path.parents)[:8])
    if not inside:
        root = find_root(path.parent, depth=0)
        inside = bool(root) and "mobile" in path.relative_to(root).parts[:2]
    if not inside or not path.exists():
        return
    try:
        msgs = mobile_lint_file(path)[:20]
    except Exception as e:  # noqa: BLE001 - hooks must never crash the session
        msgs = [f"ds hook error: {e}"]
    if msgs:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext":
                          "html-design-system mobile checks (fix, or mark a deliberate exception with `ds-lint: ignore`):\n- " + "\n- ".join(msgs)}}))


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
    p.add_argument("--platforms", default="web", help=f"comma list or all: web, {', '.join(ICON_PLATFORMS)}")
    p = sp.add_parser("icons-add"); p.add_argument("names", nargs="+"); p.add_argument("--set", required=True, choices=list(ICON_SETS))
    p.add_argument("--dir", required=True); p.add_argument("--version", help="package version (default: latest, pinned in icons/LICENSES.md)")
    p.add_argument("--platforms", default="web")
    p = sp.add_parser("icons-style"); p.add_argument("src", nargs="?", help="folder of reference icons (omit: derive from tokens)")
    p.add_argument("--dir", help="design system: writes icons/style.json")
    p = sp.add_parser("icons-lint"); p.add_argument("paths", nargs="+"); p.add_argument("--style"); p.add_argument("--dir")
    p = sp.add_parser("mobile"); msp = p.add_subparsers(dest="mobile_cmd", required=True)
    q = msp.add_parser("spec"); q.add_argument("dir"); q.add_argument("--tokens-only", action="store_true")
    q.add_argument("--only", help="comma list of component files to measure, e.g. button,card")
    q = msp.add_parser("scaffold"); q.add_argument("dir"); q.add_argument("--target", default="all", help=f"comma list or all: {', '.join(SCAFFOLD_GENERATORS)}")
    q.add_argument("--out", help="write into the app instead of dist/mobile/<target> (adds .ds-mobile.json so the hook lints edits)")
    q.add_argument("--package", default="design.system", help="Kotlin package for compose")
    q = msp.add_parser("verify"); q.add_argument("dir"); q.add_argument("--native", required=True, help="folder of native snapshot PNGs")
    q.add_argument("--measurements", help="JSON of native measurements {file: {demo: {theme: {width, height, ...}}}}")
    q.add_argument("--max-diff", type=float, default=1.0, help="max %% of pixels over OKLab ΔE 3 (default 1)")
    q.add_argument("--size-tolerance", type=float, default=3.0, help="max %% size difference (default 3)")
    q = msp.add_parser("lint"); q.add_argument("paths", nargs="+"); q.add_argument("--strict", action="store_true")
    p = sp.add_parser("playwright"); p.add_argument("dir"); p.add_argument("--force", action="store_true")
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
     "palette": cmd_palette, "scale": cmd_scale, "export": cmd_export, "icons": cmd_icons, "taste": cmd_taste,
     "icons-add": cmd_icons_add, "icons-style": cmd_icons_style, "icons-lint": cmd_icons_lint,
     "mobile": lambda a: {"spec": cmd_mobile_spec, "scaffold": cmd_mobile_scaffold, "verify": cmd_mobile_verify,
                          "lint": cmd_mobile_lint}[a.mobile_cmd](a),
     "playwright": cmd_playwright}[a.cmd](a)


if __name__ == "__main__":
    main()
