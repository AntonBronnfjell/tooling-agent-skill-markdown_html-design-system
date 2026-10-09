"""Tests for scripts/ds.py and install.py. Stdlib only: python3 -m unittest discover -s tests -v

Golden files in tests/golden/ pin generated output. After an intentional change, review the diff and run
UPDATE_GOLDEN=1 python3 -m unittest discover -s tests
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DS = REPO / "scripts" / "ds.py"
GOLDEN = Path(__file__).resolve().parent / "golden"
sys.path.insert(0, str(REPO / "scripts"))
import ds  # noqa: E402


def run(*args, cwd=None, stdin=None, env=None, check=True):
    p = subprocess.run([sys.executable, str(DS), *map(str, args)], cwd=cwd, input=stdin, capture_output=True,
                       text=True, env={**os.environ, **(env or {})})
    if check and p.returncode != 0:
        raise AssertionError(f"ds.py {' '.join(map(str, args))} failed ({p.returncode}):\n{p.stdout}\n{p.stderr}")
    return p


class Temp(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ds-test-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


class TestManifest(unittest.TestCase):
    def test_manifest_consistency(self):
        m = json.loads((REPO / "assets" / "manifest.json").read_text(encoding="utf-8"))
        ids, files = set(), {}
        docs = {"foundations": "foundations", "actions": "actions", "forms": "forms", "navigation": "navigation",
                "data-display": "data-display", "overlays": "overlays-feedback", "feedback": "overlays-feedback",
                "patterns": "patterns", "marketing": "marketing", "marketing-pages": "marketing", "ai": "ai",
                "ai-patterns": "ai", "commerce": "commerce", "commerce-pages": "commerce", "email": "email",
                "email-templates": "email"}
        for cat in m["categories"]:
            self.assertIn(cat.get("scope", "product"), m["scopes"], cat["id"])
            text = (REPO / "references" / "components" / f"{docs[cat['id']]}.md").read_text(encoding="utf-8")
            for c in cat["components"]:
                self.assertNotIn(c["id"], ids, f"duplicate id {c['id']}")
                ids.add(c["id"])
                d = cat.get("page_dir", "components")
                self.assertEqual(files.setdefault(c["file"], d), d, f"file {c['file']} in two page dirs")
                self.assertIn(c["tier"], ("core", "standard", "enterprise"))
                for marker in c["demos"]:
                    self.assertRegex(marker, r"^(state|variant|size):[\w./-]+$", c["id"])
                self.assertTrue(c["id"] in text or c["file"] in text or c["name"].split(" (")[0] in text,
                                f"{c['id']} has no spec in references/components/{docs[cat['id']]}.md")
        self.assertGreaterEqual(len(ids), 306)

    def test_skill_frontmatter(self):
        s = (REPO / "SKILL.md").read_text(encoding="utf-8")
        fm = s.split("---")[1]
        desc = re.search(r"description: >\n((?:  .*\n)+)", fm).group(1)
        self.assertLessEqual(len(" ".join(desc.split())), 1024)
        self.assertIn("name: html-design-system", fm)
        self.assertLess(s.count("\n"), 500)

    def test_plugin_manifests_agree(self):
        versions = {json.loads((REPO / p).read_text(encoding="utf-8"))["version"]
                    for p in (".claude-plugin/plugin.json", ".cursor-plugin/plugin.json", ".codex-plugin/plugin.json")}
        self.assertEqual(len(versions), 1, versions)
        self.assertIn(f"## [{versions.pop()}]", (REPO / "CHANGELOG.md").read_text(encoding="utf-8"))


class TestColorsAndTokens(unittest.TestCase):
    def test_hex_roundtrip_and_contrast(self):
        obj = ds.hex_to_color_obj("#2563eb")
        self.assertEqual(obj["colorSpace"], "srgb")
        self.assertEqual(ds.color_obj_to_css(obj), "#2563eb")
        self.assertAlmostEqual(ds.contrast(ds.color_rgb(obj), (1, 1, 1)), 5.17, places=1)

    def test_wide_gamut_rendering(self):
        self.assertEqual(ds.color_obj_to_css({"colorSpace": "oklch", "components": [0.6, 0.2, 260]}), "oklch(0.6 0.2 260)")
        self.assertEqual(ds.color_obj_to_css({"colorSpace": "display-p3", "components": [1, 0, 0], "alpha": 0.5}),
                         "color(display-p3 1 0 0 / 0.5)")
        rgb = ds._oklch_to_srgb(0.6, 0.2, 260)
        self.assertTrue(all(0 <= c <= 1 for c in rgb))

    def test_migrate_colors(self):
        tree = {"color": {"$type": "color", "a": {"$value": "#ff000080"}, "b": {"$value": "{color.a}"}}}
        self.assertEqual(ds.migrate_colors_tree(tree), 1)
        self.assertEqual(tree["color"]["a"]["$value"]["alpha"], 0.502)
        self.assertEqual(tree["color"]["b"]["$value"], "{color.a}")


class TestBuild(Temp):
    def _write(self, root, name, text):
        p_ = root / "components" / name
        p_.write_text(text, encoding="utf-8")
        return p_

    def init(self, *extra, name="Golden"):
        root = self.tmp / "ds"
        run("init", root, "--name", name, "--tier", "core", *extra)
        return root

    def test_init_build_check(self):
        root = self.init()
        run("build", root)
        out = run("check", root).stdout
        self.assertIn("- ok", out)
        self.assertIn("Lint (0 issues)", out)
        css = (root / "dist" / "ds.css").read_text(encoding="utf-8")
        self.assertTrue(css.startswith("@layer reset, tokens, base, components, patterns, utilities;"))
        self.assertTrue((root / "tokens" / "resolver.json").exists())

    def test_golden_outputs(self):
        root = self.init()
        run("build", root)
        run("design-md", root)
        run("llms", root)
        for rel in ("dist/tokens.css", "tokens/resolver.json", "DESIGN.md", "llms.txt"):
            got = (root / rel).read_text(encoding="utf-8")
            gold = GOLDEN / rel.replace("/", "__")
            if os.environ.get("UPDATE_GOLDEN") or not gold.exists():
                gold.parent.mkdir(exist_ok=True)
                gold.write_text(got, encoding="utf-8")
                continue
            self.assertEqual(got, gold.read_text(encoding="utf-8"), f"{rel} changed — review, then UPDATE_GOLDEN=1")

    def test_all_scopes(self):
        root = self.init("--scopes", "product,marketing,ai,commerce,email")
        out = run("check", root).stdout
        self.assertIn("- ok", out)
        self.assertRegex(out, r"Coverage: 0/\d+")
        self.assertTrue((root / "tokens" / "scopes" / "ai.json").exists())
        email = run("email", root).stdout
        self.assertIn("0 problem(s)", email)

    def test_lint_rules(self):
        root = self.init()
        (root / "css" / "components" / "x.css").write_text(".x{color:#fff;margin:12px}\n.x:focus{outline:none;}\n", encoding="utf-8")
        (root / "components" / "x.html").write_text('<div onclick="d.showModal()"><img src=a.png></div>', encoding="utf-8")
        out = run("check", root).stdout
        ok_html = ('<button type="button"><svg aria-hidden="true"></svg> Save</button>'
                   '<button type="button">Next <svg aria-hidden="true"></svg></button>')
        self.assertEqual([i for i in ds.lint_file(self._write(root, "ok.html", ok_html)) if "icon-only" in i], [])
        self.assertEqual(ds.lint_file(self._write(root, "art.html", "<article><aside><abbr title='x'>x</abbr></aside></article>")), [])
        bad = self._write(root, "bad.html", '<button type="button"><svg></svg></button>')
        self.assertTrue(any("icon-only" in i for i in ds.lint_file(bad)))
        for needle in ("raw hex color", "raw px spacing", "outline removed", "@layer components", "img without alt",
                       "invoker commands"):
            self.assertIn(needle, out)


class TestSafety(Temp):
    def test_refuses_occupied_folder_and_adopt_keeps_files(self):
        target = self.tmp / "occupied"
        target.mkdir()
        (target / "NOTES.md").write_text("mine", encoding="utf-8")
        p = run("init", target, check=False)
        self.assertNotEqual(p.returncode, 0)
        run("init", target, "--adopt", "--tier", "core")
        self.assertEqual((target / "NOTES.md").read_text(encoding="utf-8"), "mine")

    def test_dry_run_writes_nothing(self):
        target = self.tmp / "dry"
        run("init", target, "--dry-run")
        self.assertFalse(target.exists() and any(target.iterdir()))

    def test_user_edits_survive(self):
        root = self.tmp / "ds"
        run("init", root, "--tier", "core")
        base = root / "css" / "base.css"
        base.write_text(base.read_text(encoding="utf-8") + "/* mine */\n", encoding="utf-8")
        run("init", root, "--force")
        self.assertTrue(base.read_text(encoding="utf-8").endswith("/* mine */\n"))
        run("init", root, "--force", "--force-all")
        self.assertFalse(base.read_text(encoding="utf-8").endswith("/* mine */\n"))

    def test_foreign_package_json_untouched(self):
        root = self.tmp / "ds"
        root.mkdir()
        (root / "package.json").write_text('{"name":"mine"}', encoding="utf-8")
        run("init", root, "--adopt", "--tier", "core")
        run("storybook", root)
        self.assertEqual(json.loads((root / "package.json").read_text(encoding="utf-8")), {"name": "mine"})


class TestProjects(Temp):
    def test_detect_laravel_and_sync(self):
        app = self.tmp / "app"
        (app / "resources" / "css").mkdir(parents=True)
        (app / "artisan").write_text("", encoding="utf-8")
        (app / "composer.json").write_text('{"require":{"laravel/framework":"^12"}}', encoding="utf-8")
        info = json.loads(run("detect", app, "--json").stdout)
        self.assertIn("laravel", info["stacks"])
        self.assertEqual(info["recommended"]["location"], "resources/design-system")
        root = app / info["recommended"]["location"]
        run("init", root, "--project", app, "--tier", "core")
        run("build", root)
        self.assertTrue((app / "resources" / "css" / "design-system" / "ds.css").exists())

    def test_detect_monorepo(self):
        mono = self.tmp / "mono"
        (mono / "apps" / "web").mkdir(parents=True)
        (mono / "packages").mkdir()
        (mono / "package.json").write_text('{"workspaces":["apps/*","packages/*"]}', encoding="utf-8")
        (mono / "apps" / "web" / "package.json").write_text('{"dependencies":{"next":"16"}}', encoding="utf-8")
        info = json.loads(run("detect", mono, "--json").stdout)
        self.assertEqual(info["recommended"]["location"], "packages/design-system")
        self.assertTrue(any(s.startswith("next") for s in info["stacks"]))


class TestAgentOutputs(Temp):
    def test_mcp_server_protocol(self):
        root = self.tmp / "ds"
        run("init", root, "--tier", "core")
        run("mcp", root)
        msgs = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "search", "arguments": {"query": "date"}}}]
        p = subprocess.run([sys.executable, str(root / "mcp" / "server.py")], input="\n".join(map(json.dumps, msgs)) + "\n",
                           capture_output=True, text=True, check=True)
        replies = [json.loads(line) for line in p.stdout.splitlines()]
        self.assertEqual([r["id"] for r in replies], [1, 2, 3])
        self.assertIn("get_component", [t["name"] for t in replies[1]["result"]["tools"]])
        self.assertIn("date-field", replies[2]["result"]["content"][0]["text"])  # core tier: date-picker is standard


class TestInstaller(Temp):
    def test_install_all_and_uninstall(self):
        home = self.tmp / "home"
        (home / ".claude").mkdir(parents=True)
        env = {"HOME": str(home), "USERPROFILE": str(home)}
        p = subprocess.run([sys.executable, str(REPO / "install.py"), "--tools", "all"], env={**os.environ, **env},
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, f"install.py failed:\n{p.stdout}\n{p.stderr}")
        portable = home / ".agents" / "skills" / "html-design-system" / "SKILL.md"
        self.assertTrue(portable.exists())
        fm = portable.read_text(encoding="utf-8").split("---")[1]
        self.assertNotIn("hooks:", fm)
        self.assertIn("license: MIT", fm)
        self.assertFalse((home / ".agents" / "skills" / "html-design-system" / "tests").exists())
        subprocess.run([sys.executable, str(REPO / "install.py"), "--uninstall"], env={**os.environ, **env},
                       capture_output=True, text=True, check=True)
        self.assertFalse(portable.exists())


class TestGenerators(Temp):
    def setUp(self):
        super().setUp()
        self.root = self.tmp / "ds"
        run("init", self.root, "--tier", "enterprise")

    def test_palette_primary_passes_contrast(self):
        out = run("palette", "#0f766e", "--name", "teal", "--dir", self.root, "--primary").stdout
        self.assertIn("all pairs pass", out)
        css = (self.root / "dist" / "tokens.css").read_text(encoding="utf-8")
        self.assertIn("--color-teal-700: #0f766e;", css)   # the seed lands on a step exactly
        self.assertIn("--color-action-primary-bg: var(--color-teal-", css)

    def test_palette_ramp_is_monotonic(self):
        ramp, _ = ds.generate_ramp("#7c3aed")
        lum = [ds.luminance(ds.color_rgb(ramp[s])) for s in ds.PALETTE_STEPS]
        self.assertEqual(lum, sorted(lum, reverse=True))
        ramp_c, _ = ds.generate_ramp("#7c3aed", mode="contrast")
        self.assertAlmostEqual(ds.contrast(ds.color_rgb(ramp_c["600"]), (1, 1, 1)), 4.5, delta=0.15)

    def test_brand_override(self):
        out = run("palette", "#c2410c", "--name", "blue", "--dir", self.root, "--brand", "ember").stdout
        self.assertIn("all pairs pass", out)
        self.assertIn('[data-brand="ember"]', (self.root / "dist" / "tokens.css").read_text(encoding="utf-8"))
        resolver = json.loads((self.root / "tokens" / "resolver.json").read_text(encoding="utf-8"))
        self.assertIn("brand", resolver["modifiers"])

    def test_scale(self):
        run("scale", "type", "--dir", self.root)
        css = (self.root / "dist" / "tokens.css").read_text(encoding="utf-8")
        self.assertRegex(css, r"--font-size-step-0: clamp\(1rem, .*vw, 1\.25rem\);")

    def test_exports(self):
        run("export", self.root)
        ex = self.root / "dist" / "exports"
        for rel in ("tailwind.css", "shadcn.css", "figma/variables.json", "figma/dark.tokens.json", "ios/DesignTokens.swift",
                    "android/values/ds_colors.xml", "android/values-night/ds_colors.xml", "compose/DesignTokens.kt",
                    "flutter/ds_tokens.dart"):
            self.assertTrue((ex / rel).exists(), rel)
        fig = json.loads((ex / "figma" / "variables.json").read_text(encoding="utf-8"))
        ids = {v["id"] for v in fig["variables"]}
        aliases = [v for v in fig["variableModeValues"] if isinstance(v["value"], dict) and v["value"].get("type") == "VARIABLE_ALIAS"]
        self.assertTrue(aliases)
        self.assertTrue(all(a["value"]["id"] in ids for a in aliases))
        self.assertIn("--background: var(--color-bg-canvas);", (ex / "shadcn.css").read_text(encoding="utf-8"))

    def test_icons(self):
        src = self.tmp / "svg"
        src.mkdir()
        (src / "Star Icon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><title>t</title>'
                                           '<path fill="#123456" d="M1.123456 2z"/></svg>', encoding="utf-8")
        run("icons", src, self.root)
        sprite = (self.root / "dist" / "icons.svg").read_text(encoding="utf-8")
        self.assertIn('<symbol id="icon-star-icon" viewBox="0 0 24 24">', sprite)
        self.assertIn('fill="currentColor"', sprite)
        self.assertNotIn("<title>", sprite)

    def test_taste(self):
        page = self.tmp / "slop.html"
        page.write_text('<h1>\u2728 Supercharge your workflow</h1><div style="background:linear-gradient(#6366f1,#ec4899)"></div>'
                        "<button>Get Started</button>", encoding="utf-8")
        self.assertNotEqual(run("taste", page, "--strict", check=False).returncode, 0)
        rules = json.loads(run("taste", page, "--json").stdout)["rules"]
        for r in ("emoji-ui", "buzzwords", "ai-gradient", "generic-cta"):
            self.assertIn(r, rules)
        self.assertEqual(json.loads(run("taste", self.root / "css", "--json").stdout)["score"], 100)

    def test_audit_url_offline(self):
        site = self.tmp / "site"
        site.mkdir()
        (site / "main.css").write_text(".a{color:#0f766e;border-radius:6px}", encoding="utf-8")
        (site / "index.html").write_text('<link rel="stylesheet" href="main.css"><p style="color:#0f766e">x</p>', encoding="utf-8")
        data = json.loads(run("audit", "--url", (site / "index.html").as_uri(), "--json").stdout)
        self.assertEqual(len(data["sources"]), 2)
        self.assertEqual(data["counts"]["colors"]["#0f766e"], 2)
        self.assertIn("extracted", data["suggested_tokens"]["color"])


class TestMobile(Temp):
    """Spec → scaffold → lint → verify, and the icon pipeline. No network, no native SDKs."""

    def setUp(self):
        super().setUp()
        self.root = self.tmp / "ds"
        run("init", self.root, "--tier", "core")

    def test_spec_tokens_and_scaffold_all_targets(self):
        run("mobile", "spec", self.root, "--tokens-only")
        spec = json.loads((self.root / "dist" / "mobile" / "spec.json").read_text(encoding="utf-8"))
        light = spec["tokens"]["light"]
        self.assertIn("color.action.primary.bg", light["color"])
        self.assertNotIn("color.gray.500", light["color"])           # primitives stay out of native themes
        self.assertEqual(light["typography"]["body"]["size"], 16)
        self.assertGreater(light["typography"]["body"]["lineHeight"], 16)   # absolute line height, not a ratio
        out = run("mobile", "scaffold", self.root, "--target", "all").stdout
        self.assertNotIn("missing tokens", out)
        m = self.root / "dist" / "mobile"
        for rel in ("swiftui/DSTheme.swift", "swiftui/DSComponents.swift", "swiftui/Tests/DSSnapshotTests.swift",
                    "compose/DsTheme.kt", "compose/DsComponents.kt", "compose/test/DsSnapshotTest.kt",
                    "flutter/ds_theme.dart", "flutter/ds_components.dart", "flutter/test/ds_golden_test.dart",
                    "react-native/theme.ts", "react-native/DsComponents.tsx", "react-native/DsSnapshots.tsx",
                    "maui/DsTokens.xaml", "web-mobile/web-mobile.css", "swiftui/FIDELITY.md"):
            self.assertTrue((m / rel).exists(), rel)
        for f in m.rglob("*"):
            if f.is_file():
                self.assertNotRegex(f.read_text(encoding="utf-8"), r"@[CDWTE]\(|MISSING_", f.name)   # every marker filled
        # The generated components pass the bad-migration linter they ship with.
        self.assertIn("0 issue(s)", run("mobile", "lint", m).stdout)
        self.assertIn("Color(0xFF", (m / "compose" / "DsTheme.kt").read_text(encoding="utf-8"))
        self.assertIn("leadingDistribution: TextLeadingDistribution.even", (m / "flutter" / "ds_theme.dart").read_text(encoding="utf-8"))

    def test_calibrate_snaps_measurements_to_tokens(self):
        tokens = ds.ensure_mobile_defaults(ds.mobile_tokens(self.root))
        spec = {"button": {"variant:primary+state:default": {"light": {"height": 40, "padding": [0, 12, 0, 12], "radius": 3.0}}}}
        r = ds.calibrate(tokens, spec)["button"]
        self.assertEqual(r["paddingX"]["token"], "space.3")                  # measured 12 px → the token with that value
        self.assertEqual((r["radius"]["value"], r["radius"]["token"]), (3.0, None))   # no token: literal, flagged
        self.assertEqual(r["heightSm"]["source"], "token")                   # not measured → default token

    def test_mobile_lint_rules(self):
        bad = {"View.swift": 'Text("x").font(.system(size: 14)).padding(12).foregroundColor(Color(red: 1, green: 0, blue: 0))\nImage(systemName: "star")',
               "Screen.kt": "Box(Modifier.padding(16.dp).background(Color(0xFF0F766E))) { Icon(Icons.Default.Star, null) }",
               "screen.dart": "Container(color: Colors.red, padding: EdgeInsets.all(8), child: Icon(Icons.star))",
               "Screen.tsx": "<View style={{ backgroundColor: '#ff0000', padding: 12 }} />"}
        for name, code in bad.items():
            (self.tmp / name).write_text(code, encoding="utf-8")
        (self.tmp / "ok.swift").write_text("Text(title).dsText(DSType.body) // ds-lint: ignore\nImage(systemName: \"x\") // ds-lint: ignore", encoding="utf-8")
        out = run("mobile", "lint", self.tmp, "--strict", check=False)
        self.assertNotEqual(out.returncode, 0)
        for msg in ("raw color", "Dynamic Type", "SF Symbol", "Material icon", "magic padding", "framework icon"):
            self.assertIn(msg, out.stdout)
        self.assertNotIn("ok.swift", out.stdout)

    def test_png_roundtrip_and_verify(self):
        refs = self.root / "dist" / "mobile" / "reference"
        refs.mkdir(parents=True)
        nat = self.tmp / "native"
        nat.mkdir()
        rows = [[(15, 118, 110)] * 30 for _ in range(10)]
        ds.use_root(self.root)
        ds.png_write(refs / "button--state_default--light.png", 30, 10, rows)
        ds.png_write(refs / "badge--variant_neutral--light.png", 30, 10, rows)
        w, h, back = ds.png_read(refs / "button--state_default--light.png")
        self.assertEqual((w, h, back[0][0]), (30, 10, (15, 118, 110)))
        shutil.copy(refs / "button--state_default--light.png", nat / "testCore.button--state_default--light.png")  # tool prefix
        out = run("mobile", "verify", self.root, "--native", nat).stdout
        self.assertIn("1/1 snapshots within tolerance", out)
        ds.png_write(nat / "badge--variant_neutral--light.png", 30, 10, [[(255, 0, 0)] * 30 for _ in range(10)])
        self.assertEqual(run("mobile", "verify", self.root, "--native", nat, check=False).returncode, 1)
        self.assertTrue((self.root / "dist" / "mobile" / "diff" / "badge--variant_neutral--light.png").exists())

    def test_icons_add_style_lint_platforms(self):
        mirror = self.tmp / "mirror" / "lucide-static@9.9.9" / "icons"
        mirror.mkdir(parents=True)
        (mirror / "truck.svg").write_text('<!-- @license lucide-static ISC --><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" '
                                          'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
                                          'stroke-linejoin="round"><path d="M3 6h11v10H3z"/><circle cx="17" cy="17" r="2"/>'
                                          '<rect x="14" y="9" width="7" height="7" rx="1"/></svg>', encoding="utf-8")
        env = {"DS_ICON_CDN": (self.tmp / "mirror").as_uri()}
        run("icons-add", "truck", "--set", "lucide", "--version", "9.9.9", "--dir", self.root, "--platforms", "all", env=env)
        self.assertIn("lucide-static@9.9.9 | ISC", (self.root / "icons" / "LICENSES.md").read_text(encoding="utf-8"))
        self.assertIn('id="icon-truck"', (self.root / "dist" / "icons.svg").read_text(encoding="utf-8"))
        icons = self.root / "dist" / "icons"
        self.assertIn('case truck = "truck"', (icons / "swiftui" / "DSIcon.swift").read_text(encoding="utf-8"))
        vd = (icons / "compose" / "drawable" / "ds_icon_truck.xml").read_text(encoding="utf-8")
        self.assertIn('android:pathData="M15 17A2 2 0 1 0 19 17A2 2 0 1 0 15 17Z"', vd)   # circle → arcs
        self.assertIn("addPathNodes", (icons / "compose" / "DsIcons.kt").read_text(encoding="utf-8"))
        self.assertIn("SvgPicture.string", (icons / "flutter" / "ds_icons.dart").read_text(encoding="utf-8"))
        self.assertIn("SvgXml", (icons / "react-native" / "DsIcon.tsx").read_text(encoding="utf-8"))
        run("icons-style", self.root / "icons" / "src", "--dir", self.root)
        style = json.loads((self.root / "icons" / "style.json").read_text(encoding="utf-8"))
        self.assertEqual((style["model"], style["strokeWidth"], style["linecap"]), ("stroke", 2, "round"))
        good, bad = self.tmp / "good.svg", self.tmp / "bad.svg"
        good.write_text('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
                        'stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>', encoding="utf-8")
        bad.write_text('<svg viewBox="0 0 24 24" fill="#f00" stroke-width="1"><path d="M-2 0h30"/><text>x</text></svg>', encoding="utf-8")
        self.assertEqual(run("icons-lint", good, "--dir", self.root).returncode, 0)
        out = run("icons-lint", bad, "--dir", self.root, check=False)
        self.assertEqual(out.returncode, 1)
        for msg in ("hard-coded paint", "not allowed: text", "outside the viewBox"):
            self.assertIn(msg, out.stdout)
        ds_style = ds.icon_style_from_ds(self.root)                          # no icons yet: derived from tokens
        self.assertEqual((ds_style["grid"], ds_style["model"]), (24, "stroke"))

    def test_svg_geometry(self):
        pts, n = ds.path_points("M2 12a10 10 0 1 0 20 0a10 10 0 1 0-20 0")   # full circle, r=10 around (12,12)
        ys = [p[1] for p in pts]
        self.assertAlmostEqual(min(ys), 2, delta=0.2)
        self.assertAlmostEqual(max(ys), 22, delta=0.2)
        self.assertEqual(n, 3)
        self.assertEqual(ds.shape_to_d(ds._svg_root('<polygon points="1,2 3,4 5,6"/>')), "M1 2L3 4L5 6Z")

    def test_native_hook(self):
        app = self.tmp / "app"
        run("mobile", "scaffold", self.root, "--target", "swiftui", "--out", app)
        self.assertTrue((app / ".ds-mobile.json").exists())
        screen = app / "Screen.swift"
        screen.write_text("Text(\"x\").font(.system(size: 13))", encoding="utf-8")
        out = run("hook-post-edit", stdin=json.dumps({"tool_input": {"file_path": str(screen)}})).stdout
        self.assertIn("Dynamic Type", json.loads(out)["hookSpecificOutput"]["additionalContext"])
        outside = self.tmp / "elsewhere.swift"
        outside.write_text("Text(\"x\").font(.system(size: 13))", encoding="utf-8")
        self.assertEqual(run("hook-post-edit", stdin=json.dumps({"tool_input": {"file_path": str(outside)}})).stdout, "")


class TestDocsTooling(Temp):
    def test_playwright_suite_and_status(self):
        root = self.tmp / "ds"
        run("init", root, "--tier", "core")
        shutil.copy(REPO / "assets" / "templates" / "component.html", root / "components" / "button.html")
        run("playwright", root)
        spec = (root / "tests" / "design-system.spec.mjs").read_text(encoding="utf-8")
        self.assertIn('"dark"', spec)
        self.assertIn("requestAnimationFrame", spec)
        pkg = json.loads((root / "package.json").read_text(encoding="utf-8"))
        self.assertIn("@playwright/test", pkg["devDependencies"])
        run("build", root)
        self.assertIn('data-status="beta"', (root / "index.html").read_text(encoding="utf-8"))
        run("llms", root)
        md = (root / "llms" / "button.md").read_text(encoding="utf-8")
        self.assertIn("## API", md)
        self.assertIn("beta", md)


if __name__ == "__main__":
    unittest.main()
