# Scope Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add 13 opt-in scopes (226 components) plus account-settings and notification additions to the `product` scope, with scope dependencies and marketing-gated landing pages.

**Architecture:** Data-first. The manifest gets new `scopes`, a top-level `scope_requires` map, new `<scope>` / `<scope>-pages` categories, and an optional per-component `requires_scopes`. `ds.py` gains `expand_scopes()` and a `requires_scopes` filter in `components()`. Each scope ships `references/components/<scope>.md` and, where the spec says so, a token template in `assets/templates/scopes/<scope>/`.

**Tech Stack:** Python 3.8+ stdlib (`scripts/ds.py`), `unittest`, JSON manifest, DTCG 2025.10 tokens, Markdown reference docs.

**Spec:** `docs/superpowers/specs/2026-10-17-scope-expansion-design.md`. The catalog in §4 is the source of truth for every component id, tier and demo list. This plan does not copy the catalog; each task names the spec section to transcribe.

## Global Constraints

- `ds.py` stays stdlib-only, Python 3.8+.
- The manifest is written with `json.dumps(m, indent=1, ensure_ascii=True) + "\n"`, so diffs stay minimal.
- Component ids are globally unique. Tiers are `core|standard|enterprise`. Demo markers match `^(state|variant|size):[\w./-]+$`. A spec entry like `variant:grouped-first|middle|last` expands to three markers.
- Every component id must appear in its scope's reference doc (enforced by `test_manifest_consistency`).
- Color is never the only signal (WCAG 1.4.1). Every presence, delta, live, speaking and highlight state also has text or an icon.
- Commits use the repo-local email `71841746+AntonBronnfjell@users.noreply.github.com` (already configured). **No `Co-Authored-By` lines.**
- Never stage the user's unrelated `SKILL.md` hook-path change unless the task edits SKILL.md (Task 16). If it does, include it and mention that in the commit body.
- Test command for every task: `python3 -m unittest discover -s tests` (run from the repo root). It must pass before each commit.

---

## Shared procedure: adding a scope (Tasks 2–8 and 10–15)

Each scope task supplies these inputs: **scope key**, **scope description**, **categories** (id + name), **spec section**, **token template** (yes/no + token list), **sources**, and **"vs." notes**.

**A. Manifest.** Run from the repo root, with `NEW` filled from the spec section:

```bash
python3 - <<'EOF'
import json
p = "assets/manifest.json"
m = json.load(open(p, encoding="utf-8"))
SCOPE, DESC = "<scope key>", "<scope description>"
NEW = {  # category id -> (name, page_dir or None, [components])
    "<scope>": ("<Name>", None, [
        {"id": "...", "name": "...", "tier": "core", "file": "...", "demos": ["state:..."],
         "aria": "...", "native": "...", "desc": "..."},
    ]),
    "<scope>-pages": ("<Name> Pages", "patterns", [ ... ]),
}
m["scopes"][SCOPE] = DESC
m["categories"] = [c for c in m["categories"] if c["id"] not in NEW]  # idempotent re-run
for cid, (name, pdir, comps) in NEW.items():
    cat = {"id": cid, "name": name, "scope": SCOPE}
    if pdir:
        cat["page_dir"] = pdir
    cat["components"] = comps
    m["categories"].append(cat)
open(p, "w", encoding="utf-8").write(json.dumps(m, indent=1, ensure_ascii=True) + "\n")
EOF
```

How to fill each component dict from a spec line `` - `id` (t): demos. notes ``:
- `id`, `tier` (c=core, s=standard, e=enterprise) and `demos`: verbatim from the spec.
- `file`: same as `id`, unless the task says otherwise.
- `name`: Title Case of the id, with a short qualifier when the id alone is ambiguous (e.g. `"Seek Bar"`, `"Message Bubble (person-to-person)"`).
- `aria`: the ARIA pattern from the spec note, or the closest APG pattern (`"slider"`, `"log"`, `"grid"`, `"dialog"`, `"alertdialog"`, `"combobox"`, `"feed"`, `"region"`, `"toolbar"`, `"menu"`, `"radiogroup"`, `"tablist"`). Use `null` for plain landmarks or pages.
- `native`: the native HTML the build uses first (e.g. `"input[type=range]"`, `"button"`, `"table"`, `"dialog"`, `"[popover] + menu"`, `"video + track"`, `"main"`).
- `desc`: one sentence built from the spec note.
- Landing pages: add `"requires_scopes": ["marketing"]`.

Worked example (spec §4.1 `seek-bar`):

```json
{"id": "seek-bar", "name": "Seek Bar", "tier": "core", "file": "seek-bar",
 "demos": ["state:default", "state:buffering", "variant:chapters", "variant:hover-preview", "state:live-edge", "state:disabled"],
 "aria": "slider", "native": "input[type=range]",
 "desc": "Scrubber with buffered and played ranges, chapter ticks and hover preview; aria-valuetext reads \"1:23 of 4:56\"."}
```

**B. Reference doc** `references/components/<scope>.md`. Use the same skeleton as `references/components/commerce.md`:

```markdown
# <Name> components & pages — specs

Scope `<scope>` (enable with `ds.py init --scopes product,<scope>`; it adds <required scopes> automatically). Components live in `components/<file>.html` (category **<Name>**); full pages in `patterns/<file>.html` (category **<Name> Pages**). <Name> components compose <product/base components> — wrap them, never re-style them.

## Contents
1. Rules for every <name> surface
2. <group> : ids…
…
N. Pages

## 1. Rules for every <name> surface
- **<Rule in bold>.** One to three sentences, citing the source by name (rule, not statistic). 8–14 rules.
- **Tokens**: the scope tokens and contrast pairs (or "composes product tokens only").
- **vs.**: when to use which overlapping component.

## 2. <group>
### <id>
- Markup (native element first), every listed demo explained in one line each, keyboard map, live-region behavior, reduced-motion behavior, RTL notes, failure states. 4–10 bullets.
…
## N. Pages
### <page id>
- Composition (which components, in what layout), each variant, mobile behavior, landing pages: which marketing sections (hero, feature-split, testimonials, pricing-table, faq, cta-band, site-footer…) in order.
```

Each `### <id>` heading must use the exact component id.

**C. Token template**, only when the task says "yes". Create `assets/templates/scopes/<scope>/` with the same file layout and format as `assets/templates/scopes/ai/`:
- `tokens.json`: top-level `$description`, then groups (`color` with `$type: "color"`, plus `size`, etc.). Primitives use DTCG color objects `{"colorSpace": "srgb", "components": [r, g, b], "hex": "#rrggbb"}`; semantic tokens alias them (`"{color.gray.950}"`).
- `themes/dark.json` and `themes/high-contrast.json`: override only the semantic tokens that change, each with a `$description` giving the measured contrast (compute it with `python3 -c "import sys; sys.path.insert(0,'scripts'); import ds; print(ds.contrast(ds.color_rgb(ds.hex_to_color_obj('#aaaaaa')), ds.color_rgb(ds.hex_to_color_obj('#111111'))))"`).
- `contrast_pairs.json`: a list of `[fg token, bg token, min ratio]` (4.5 for text, 3 for UI glyphs and large text).

**D. Verify and commit.**

```bash
python3 -m unittest discover -s tests
python3 scripts/ds.py init /tmp/ds-<scope> --name T --tier enterprise --scopes product,<scope>,marketing && \
python3 scripts/ds.py check /tmp/ds-<scope> | head -20 && python3 scripts/ds.py plan /tmp/ds-<scope> | grep -c "<first id of the scope>" ; rm -rf /tmp/ds-<scope>
```

Expected: the tests pass, `check` shows `- ok` for tokens with no contrast failures, and `plan` lists the new ids.

```bash
git add assets/manifest.json references/components/<scope>.md assets/templates/scopes/<scope>
git commit -m "feat(<scope>): <scope> scope — <n> components + <m> pages"
```

---

### Task 1: Scope dependencies and gated components in `ds.py`

**Files:**
- Modify: `scripts/ds.py:216-222` (`components`), `scripts/ds.py:740-744` (`cmd_init` scopes), `scripts/ds.py:4528` (`--scopes` help), plus a new function placed right above `components`
- Modify: `assets/manifest.json` (add an empty top-level `"scope_requires": {}` after `"scopes"`)
- Test: `tests/test_ds.py` (`TestManifest.test_manifest_consistency`, `TestBuild.test_all_scopes`, new `TestScopes`)

**Interfaces:**
- Produces: `ds.expand_scopes(scopes: list[str]) -> list[str]`. It keeps order, removes duplicates and appends required scopes transitively. `ds.components(cfg)` honors `requires_scopes` and expanded scopes. Manifest key `scope_requires: dict[str, list[str]]`. Component key `requires_scopes: list[str]` (optional).

- [ ] **Step 1: Write the failing tests.** Add `from unittest import mock` to the imports at the top of `tests/test_ds.py`, then insert before `class TestBuild`:

```python
class TestScopes(unittest.TestCase):
    def test_expand_scopes_transitive_and_ordered(self):
        with mock.patch.dict(ds.MANIFEST, {"scope_requires": {"live": ["video"], "video": ["playback"]}}):
            self.assertEqual(ds.expand_scopes(["product", "live"]), ["product", "live", "video", "playback"])
            self.assertEqual(ds.expand_scopes(["product", "video", "live"]), ["product", "video", "live", "playback"])
            self.assertEqual(ds.expand_scopes(["product"]), ["product"])

    def test_requires_scopes_gates_component(self):
        comp = {"id": "x-landing", "name": "X", "tier": "core", "file": "x-landing", "demos": ["state:default"],
                "aria": None, "native": "main", "desc": "", "requires_scopes": ["marketing"]}
        cats = [{"id": "x", "name": "X", "scope": "product", "components": [comp]}]
        with mock.patch.dict(ds.MANIFEST, {"categories": cats}):
            self.assertEqual(list(ds.components({"tier": "core", "scopes": ["product"]})), [])
            self.assertEqual(len(list(ds.components({"tier": "core", "scopes": ["product", "marketing"]}))), 1)

    def test_hand_edited_config_gets_required_scopes(self):
        cats = [{"id": "p", "name": "P", "scope": "playback",
                 "components": [{"id": "p1", "name": "P1", "tier": "core", "file": "p1", "demos": ["state:default"],
                                 "aria": None, "native": "button", "desc": ""}]}]
        with mock.patch.dict(ds.MANIFEST, {"categories": cats, "scope_requires": {"music": ["playback"]}}):
            self.assertEqual(len(list(ds.components({"tier": "core", "scopes": ["product", "music"]}))), 1)
```

Also in `TestManifest.test_manifest_consistency`, replace the line
`text = (REPO / "references" / "components" / f"{docs[cat['id']]}.md").read_text(encoding="utf-8")`
with
```python
            doc = docs.get(cat["id"], cat.get("scope", "product"))  # opt-in scopes: references/components/<scope>.md
            text = (REPO / "references" / "components" / f"{doc}.md").read_text(encoding="utf-8")
```
replace `{docs[cat['id']]}` in the assertion message with `{doc}`, and after the loop add:
```python
        for k, reqs in m.get("scope_requires", {}).items():
            self.assertIn(k, m["scopes"])
            for r in reqs:
                self.assertIn(r, m["scopes"], f"scope_requires[{k}] -> unknown {r}")
```

In `TestBuild.test_all_scopes`, replace the hard-coded scope list:
```python
    def test_all_scopes(self):
        root = self.init("--scopes", ",".join(ds.MANIFEST["scopes"]))
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest tests.test_ds.TestScopes -v`
Expected: FAIL with `AttributeError: module 'ds' has no attribute 'expand_scopes'`.

- [ ] **Step 3: Implement.** In `scripts/ds.py`, insert directly above `def components(`:

```python
def expand_scopes(scopes):
    """Add the base scopes each scope needs (manifest scope_requires), transitively; requested order first."""
    out = list(dict.fromkeys(scopes))
    for s in out:  # out grows while iterating -> fixed point
        out += [r for r in MANIFEST.get("scope_requires", {}).get(s, []) if r not in out]
    return out
```

Replace the body of `components`:

```python
def components(cfg=None, all_tiers=False):
    scopes = set(expand_scopes((cfg or {}).get("scopes") or ["product"]))
    for cat in MANIFEST["categories"]:
        if cfg is not None and cat.get("scope", "product") not in scopes:
            continue  # e.g. marketing sections only when "marketing" is in ds.config.json scopes
        for c in cat["components"]:
            if cfg is not None and not set(c.get("requires_scopes", ())) <= scopes:
                continue  # e.g. a scope's landing page only when marketing is on too
            if all_tiers or cfg is None or in_tier(c["tier"], cfg["tier"]):
                yield cat, c
```

In `cmd_init`, directly after the `if a.scopes:` block (before `bad = ...`):

```python
    asked = list(cfg["scopes"])
    cfg["scopes"] = expand_scopes(asked)
    if len(cfg["scopes"]) > len(asked):
        print(f"scopes: {', '.join(asked)} (+ {', '.join(cfg['scopes'][len(asked):])}, required)")
```

Change the `--scopes` help at line 4528:

```python
    p.add_argument("--scopes", help="comma list, default product. Known: " + ", ".join(MANIFEST["scopes"]))
```

Change the module docstring line 4 to `[--scopes product,marketing,...]` (unchanged meaning, no hard-coded full list).

In `assets/manifest.json`, insert `"scope_requires": {}` after `"scopes"` (re-serialize with the Global Constraints format):

```bash
python3 - <<'EOF'
import json
p = "assets/manifest.json"; m = json.load(open(p, encoding="utf-8"))
m = {k: m[k] for k in ("version", "doc_sections", "tiers", "scopes")} | {"scope_requires": {}} | {k: v for k, v in m.items() if k not in ("version", "doc_sections", "tiers", "scopes", "scope_requires")}
open(p, "w", encoding="utf-8").write(json.dumps(m, indent=1, ensure_ascii=True) + "\n")
EOF
```

(Python 3.9+ is needed for `|` here; this is a dev-time step, not shipped code. On 3.8, use `{**a, **b}`.)

- [ ] **Step 4: Run all tests**

Run: `python3 -m unittest discover -s tests`
Expected: all pass. Golden files are unchanged, because product-only output doesn't change.

- [ ] **Step 5: Commit**

```bash
git add scripts/ds.py tests/test_ds.py assets/manifest.json
git commit -m "feat(ds): scope_requires expansion and requires_scopes gating"
```

---

### Task 2: `playback` base scope

Follow the **Shared procedure** with:
- **Scope key:** `playback`. **Description:** `"Base scope (added automatically by video/live/music/podcast/reading/messaging): transport, seek, volume, speed, captions, transcript, queue, mini-player"`.
- **Categories:** `playback` "Playback" (components only, no pages category).
- **Spec section:** §4.1 (11 components). `js/lib/media.js` is a documented behavior, not a manifest entry: describe it in doc §1 (Media Session metadata/actions, keyboard map Space/K, J/L, ←/→, M, C, F, one polite live region).
- **Token template:** yes. Tokens `color.media.surface` (always dark), `color.media.scrim`, `color.media.fg`, `color.media.track.rail|buffered|played`, `color.media.live`, `color.media.focus`. Contrast pairs: `[color.media.fg, color.media.surface, 4.5]`, `[color.media.fg, color.media.scrim, 4.5]` (captions), `[color.media.live, color.media.surface, 3]`, `[color.media.track.played, color.media.track.rail, 3]`, `[color.media.focus, color.media.surface, 3]`.
- **Sources:** WCAG 2.2 1.2.2 / 1.2.4 / 1.2.5 / 2.2.2 / 1.4.2 (audio control), WebVTT, Media Session API, Remote Playback API, the FCC caption display settings (as user-setting precedent), ARIA APG slider and menu button.
- **vs. notes:** `media-stage` (product) is a static hero surface, not a player. `video-section` (marketing) is a page section, and when interactive it embeds `video-player`.
- Commit: `feat(playback): playback base scope — 11 shared player components`.

---

### Task 3: `video` scope

**Files:** `assets/manifest.json`, `references/components/video.md`, `tests/test_ds.py`

- [ ] **Step 1: Write the failing init test.** Add to `class TestBuild`:

```python
    def test_init_expands_required_scopes(self):
        root = self.init("--scopes", "product,video")
        cfg = json.loads((root / "ds.config.json").read_text(encoding="utf-8"))
        self.assertEqual(cfg["scopes"], ["product", "video", "playback"])
        self.assertTrue((root / "tokens" / "scopes" / "playback.json").exists())
        ids = {c["id"] for _, c in ds.components({**cfg, "tier": "standard"})}
        self.assertIn("seek-bar", ids)
        self.assertNotIn("video-landing", ids)  # requires marketing
        self.assertIn("video-landing", {c["id"] for _, c in ds.components({**cfg, "tier": "standard",
                                                                            "scopes": cfg["scopes"] + ["marketing"]})})
```

- [ ] **Step 2:** Run `python3 -m unittest tests.test_ds.TestBuild.test_init_expands_required_scopes -v`. Expected: FAIL with `unknown scope(s) ['video']`.
- [ ] **Step 3:** Follow the **Shared procedure** with:
  - **Scope key:** `video`. **Description:** `"Video UI: player, cards, chapters, end screen, creator header, upload; watch/home/channel/library/search/studio pages (add for video platforms)"`.
  - In the manifest script, also set `m["scope_requires"]["video"] = ["playback"]`.
  - **Categories:** `video` "Video", `video-pages` "Video Pages" (`patterns`).
  - **Spec section:** §4.2 (9 components + 7 pages; `video-landing` gets `requires_scopes: ["marketing"]`).
  - **Token template:** no (uses playback tokens).
  - **Sources:** WCAG 1.2.x and 2.2.2, `prefers-reduced-motion`, the no-autoplay-with-sound rule (browser autoplay policies), `loading="lazy"` + `fetchpriority` for thumbnails, `VideoObject` JSON-LD for watch pages.
  - **vs. notes:** `video-card` vs `post-card` (feed item with author and body); `creator-header` vs messaging `channel-header`.
- [ ] **Step 4:** `python3 -m unittest discover -s tests`. Expected: PASS.
- [ ] **Step 5:** Commit `feat(video): video scope — 9 components + 7 pages` (include `tests/test_ds.py`).

---

### Task 4: `live` scope

Follow the **Shared procedure** with:
- **Scope key:** `live`. **Description:** `"Livestreaming UI: live player, live badge, live chat, reactions, schedule, polls, tips, go-live panel; live/directory/studio pages (requires video)"`. Set `m["scope_requires"]["live"] = ["video"]`.
- **Categories:** `live` "Live", `live-pages` "Live Pages" (`patterns`).
- **Spec section:** §4.3 (8 components + 4 pages; `live-landing` gets `requires_scopes: ["marketing"]`).
- **Token template:** no (`color.media.live` comes from playback).
- **Sources:** ARIA APG `log` role, WCAG 2.2.2 and 2.3.3 (reactions), WCAG 4.1.3 status messages (throttled chat announcements), HLS/DASH low-latency vocabulary (live edge, DVR window).
- **vs. notes:** `live-chat` vs messaging `message-thread` (a broadcast audience, not a conversation) vs ai `conversation`.
- **Extra test** (add to `TestScopes`, write it first and see it fail before the manifest edit):

```python
    def test_live_pulls_video_and_playback(self):
        self.assertEqual(ds.expand_scopes(["product", "live"]), ["product", "live", "video", "playback"])
```

- Commit: `feat(live): live scope — 8 components + 4 pages`.

---

### Task 5: `music` scope

Follow the **Shared procedure** with:
- **Scope key:** `music`. **Description:** `"Music UI: now-playing bar and view, track rows/lists, artwork cards, lyrics, playlists, equalizer; home/album/playlist/artist/library/search pages"`. Set `m["scope_requires"]["music"] = ["playback"]`.
- **Categories:** `music` "Music", `music-pages` "Music Pages" (`patterns`).
- **Spec section:** §4.4 (10 components + 7 pages; `music-landing` gets `requires_scopes: ["marketing"]`).
- **Token template:** no.
- **Sources:** Media Session API (artwork, track metadata, next/previous), ARIA APG grid vs table (track list uses `table`), WCAG 2.2.2 (synced lyrics auto-scroll can be paused), explicit-content labelling as text (not only an "E" glyph).
- **vs. notes:** `artwork-card` vs `card` vs `video-card`; `save-toggle` vs `toggle-button` (a specialised `aria-pressed` toggle with a save/unsave name).
- Commit: `feat(music): music scope — 10 components + 7 pages`.

---

### Task 6: `podcast` scope

Follow the **Shared procedure** with:
- **Scope key:** `podcast`. **Description:** `"Podcast UI: podcast player, episodes, shows, show notes, downloads, clips; home/show/episode/queue pages"`. Set `m["scope_requires"]["podcast"] = ["playback"]`.
- **Categories:** `podcast` "Podcast", `podcast-pages` "Podcast Pages" (`patterns`).
- **Spec section:** §4.5 (7 components + 5 pages; `podcast-landing` gets `requires_scopes: ["marketing"]`).
- **Token template:** no.
- **Sources:** Podcasting 2.0 namespace (chapters, transcript tags), WCAG 1.2.1 (transcripts for audio-only), Media Session seekbackward/seekforward, `PodcastEpisode` JSON-LD.
- **vs. notes:** `podcast-player` vs music `now-playing-bar` (skip intervals, chapters, sleep timer by default); `episode-row` vs music `track-row`.
- Commit: `feat(podcast): podcast scope — 7 components + 5 pages`.

---

### Task 7: `reading` scope

Follow the **Shared procedure** with:
- **Scope key:** `reading`. **Description:** `"Reading UI: ebook reader (paged/scroll, settings, TOC, highlights, notes), audiobooks, comics/manga, long-form articles, TTS; library/book/reader/read-later pages"`. Set `m["scope_requires"]["reading"] = ["playback"]`.
- **Categories:** `reading` "Reading", `reading-pages` "Reading Pages" (`patterns`).
- **Spec section:** §4.6 (16 components + 5 pages; `reading-landing` gets `requires_scopes: ["marketing"]`).
- **Token template:** yes. Tokens `color.reader.paper|sepia|night.bg|fg|link|selection`, `color.reader.highlight.yellow|green|blue|pink`, `size.reader.measure` (`66ch`), `size.reader.leading` (`1.6`). The night theme is part of `tokens.json` (reader themes are user-chosen, independent of app theme). `themes/dark.json` overrides only the highlight colors for dark surfaces; `themes/high-contrast.json` maps paper to pure black on white. Contrast pairs: each `fg`/`bg` and `link`/`bg` at 4.5, plus `[color.reader.paper.fg, color.reader.highlight.<c>, 4.5]` for each highlight.
- **Sources:** EPUB 3.3 and EPUB Media Overlays, Readium CSS user settings, CSS `writing-mode` and logical properties, CSS Custom Highlight API, WCAG 1.4.12 text spacing and 1.4.8 visual presentation (measure, user-chosen colors), `speechSynthesis` (Web Speech API).
- **vs. notes:** `article-reader` vs `prose` (product typography for authored content) and `blog-article` (marketing page); `comic-viewer` vs `lightbox`.
- Commit: `feat(reading): reading scope — 16 components + 5 pages`.

---

### Task 8: `messaging` scope

Follow the **Shared procedure** with:
- **Scope key:** `messaging`. **Description:** `"Messaging UI (person-to-person): DMs and groups, channels and threads, voice/video calls, support chat widget; inbox/workspace/call/support pages"`. Set `m["scope_requires"]["messaging"] = ["playback"]`.
- **Categories:** `messaging` "Messaging", `messaging-pages` "Messaging Pages" (`patterns`).
- **Spec section:** §4.7 (23 components + 5 pages; `messaging-landing` gets `requires_scopes: ["marketing"]`). Expand `variant:grouped-first|middle|last` to three markers.
- **Token template:** yes. Tokens `color.message.own.bg|fg`, `color.message.other.bg|fg`, `color.presence.online|away|busy|offline`. Contrast pairs: own and other fg/bg at 4.5, each presence color vs `color.bg.surface` at 3.
- **Sources:** ARIA APG `log`, `grid` (emoji picker), `combobox` (mentions), `alertdialog` (incoming call); WCAG 4.1.3 status messages (typing and receipts, throttled); WCAG 2.2.2 (typing animation); `getUserMedia` permission UX (device check before join); WCAG 2.5.8 target size for call controls.
- **vs. notes:** `message-bubble` vs ai `chat-message` (assistant turns, sources, tools) vs product `comment-thread` (document discussion); `channel-header` vs video `creator-header`; `support-panel` vs ai `copilot-panel`.
- Commit: `feat(messaging): messaging scope — 23 components + 5 pages`.

---

### Task 9: `product` additions — account settings and notifications

**Files:**
- Modify: `assets/manifest.json` (append to existing categories `patterns`, `forms`, `feedback`)
- Modify: `references/components/patterns.md`, `references/components/forms.md`, `references/components/overlays-feedback.md`

- [ ] **Step 1: Manifest.** Spec §4.14. Append the 10 `settings-*` / `notification-inbox` entries to the `patterns` category, `preference-matrix` to `forms`, and `notification-permission-prompt` to `feedback`:

```bash
python3 - <<'EOF'
import json
p = "assets/manifest.json"; m = json.load(open(p, encoding="utf-8"))
ADD = {"patterns": [ ...10 dicts from spec §4.14... ],
       "forms": [ {"id": "preference-matrix", ...} ],
       "feedback": [ {"id": "notification-permission-prompt", ...} ]}
for cat in m["categories"]:
    have = {c["id"] for c in cat["components"]}
    cat["components"] += [c for c in ADD.get(cat["id"], []) if c["id"] not in have]
open(p, "w", encoding="utf-8").write(json.dumps(m, indent=1, ensure_ascii=True) + "\n")
EOF
```

Fill the dicts using the rules from the Shared procedure step A. `settings-*` pages: `aria: null`, `native: "form"`.

- [ ] **Step 2: Docs.**
  - In `patterns.md`, add a section **Account settings suite** after the existing `settings` entry. It covers shared rules (side-nav shell from `settings`; per-section save, or auto-save with a status message, never both; destructive actions last and separated; re-authentication before security changes; email change verifies the new address before switching), then one `### <id>` per page.
  - In `forms.md`, add `### preference-matrix` (a `table` with `th scope=col` channels and `th scope=row` events; a column "all" toggle is a tri-state checkbox; disabled cells say why).
  - In `overlays-feedback.md`, add `### notification-permission-prompt` (soft ask in-page first; call `Notification.requestPermission()` only from that button; the denied state explains how to re-enable per browser; never prompt on page load).
  - `settings-appearance` must document wiring to `js/theme.js` (theme, density and `data-reduced-motion`).
- [ ] **Step 3:** `python3 -m unittest discover -s tests`. Expected: PASS.
- [ ] **Step 4:** Commit `feat(product): account settings suite, notification inbox, preference matrix, permission prompt`.

---

### Task 10: `billing` scope

Follow the **Shared procedure** with:
- **Scope key:** `billing`. **Description:** `"Billing & payments UI (in-app): current plan, plan change, payment methods, invoices, usage, cancel flow, transactions, payouts, wallet, tax info; billing/plans/invoice/transactions/payouts pages"`. No `scope_requires`.
- **Categories:** `billing` "Billing", `billing-pages` "Billing Pages" (`patterns`).
- **Spec section:** §4.8 (14 components + 5 pages). No landing page (spec D8).
- **Token template:** no.
- **Sources:** Baymard and GOV.UK payment-card patterns (reuse `payment-card-entry` rules by reference), SEPA/ACH mandate text requirements, FTC Negative Option rule (cancelling is as easy as signing up; cite as a rule), `Intl.NumberFormat` currency formatting, print styles for invoices.
- **vs. notes:** `billing-usage` vs ai `usage-meter`; `add-payment-method` vs commerce `payment-method` (checkout selection); `plan-picker` vs marketing `pricing-table`.
- Commit: `feat(billing): billing scope — 14 components + 5 pages`.

---

### Task 11: `analytics` scope

Follow the **Shared procedure** with:
- **Scope key:** `analytics`. **Description:** `"Reports & metrics UI: filter bar, report tables, export, freshness, metric definitions, scorecards, funnel/cohort/pivot, report builder, scheduled reports, alerts; overview/report/library/builder pages"`.
- **Categories:** `analytics` "Analytics", `analytics-pages` "Analytics Pages" (`patterns`).
- **Spec section:** §4.9 (13 components + 4 pages).
- **Token template:** yes, minimal. `color.metric.delta.up|down|flat` aliasing the existing success/danger/neutral text tokens, with a `$description` saying "always paired with an arrow icon and a signed number". Contrast pairs: each vs `color.bg.surface` at 4.5. Dark and high-contrast themes override only if the aliases don't already adapt; otherwise omit the `themes/` folder.
- **Sources:** `references/imagery.md` dataviz palette; WCAG 1.4.1 and 1.1.1 (every chart has a table or text alternative); ARIA APG grid for `pivot-table`; `Intl.NumberFormat` compact notation; time zones stated on date filters.
- **vs. notes:** `scorecard` vs product `stat` (stat already does trend + sparkline; scorecard adds a target); `report-table` vs `data-table`.
- Commit: `feat(analytics): analytics scope — 13 components + 4 pages`.

---

### Task 12: `erp` scope

Follow the **Shared procedure** with:
- **Scope key:** `erp`. **Description:** `"ERP / back-office UI: record header, line-item editor, status workflow, master-data lookup, approvals, audit log, inventory, print layouts, batch edit, import wizard; record list/form, PO, inventory, approvals, import pages"`.
- **Categories:** `erp` "ERP", `erp-pages` "ERP Pages" (`patterns`).
- **Spec section:** §4.10 (10 components + 6 pages).
- **Token template:** no.
- **Sources:** ARIA APG grid (spreadsheet-like `line-item-editor`: arrow keys, Enter to edit, Escape to cancel, F2), SAP Fiori and Oracle Redwood object-page conventions (cite as precedent), CSS paged media `@page`, WCAG 3.3.4 error prevention for legal and financial submissions (review step before posting).
- **vs. notes:** `line-item-editor` vs `data-table` (editable cells, totals); `status-workflow` vs `stepper`; `master-data-lookup` vs `combobox`.
- Commit: `feat(erp): erp scope — 10 components + 6 pages`.

---

### Task 13: `calendar` scope

Follow the **Shared procedure** with:
- **Scope key:** `calendar`. **Description:** `"Calendar & scheduling UI: month/week/day/agenda views, event chip and editor, slot picker, recurrence, availability, time zones, resource scheduler; calendar/booking/availability/event pages"`.
- **Categories:** `calendar` "Calendar", `calendar-pages` "Calendar Pages" (`patterns`). Component ids are `calendar-month` etc. They don't collide with product `calendar` (whose file is `date-picker`).
- **Spec section:** §4.11 (11 components + 4 pages).
- **Token template:** no (event categories use the dataviz palette with text labels).
- **Sources:** ARIA APG grid (month view), RFC 5545 RRULE, `Intl.DateTimeFormat` + IANA time zones, WCAG 2.5.7 dragging alternatives (resource scheduler has a move dialog).
- **vs. notes:** `calendar-month` vs product `calendar` (date selection inside an input).
- Commit: `feat(calendar): calendar scope — 11 components + 4 pages`.

---

### Task 14: `maps` scope

Follow the **Shared procedure** with:
- **Scope key:** `maps`. **Description:** `"Maps & location UI: accessible map container, markers, clusters, popups, controls, location search/picker, map-list sync, directions, area selection; store locator, map search, directions pages"`.
- **Categories:** `maps` "Maps", `maps-pages` "Maps Pages" (`patterns`).
- **Spec section:** §4.12 (10 components + 3 pages).
- **Token template:** yes. Tokens `color.map.pin.default|selected|visited`, `color.map.route`, `color.map.cluster.bg|fg`. `themes/dark.json` only (map tiles are provider-themed). Contrast pairs: `[color.map.cluster.fg, color.map.cluster.bg, 4.5]` and each pin vs `color.bg.surface` at 3.
- **Sources:** WCAG 2.1.1 keyboard and 2.5.7 dragging alternatives (pan buttons), 1.1.1 (list alternative for markers), Geolocation permission UX (ask from a button), the provider attribution requirements of MapLibre/OSM, Google and Mapbox; "what the system can't guarantee" for third-party tiles.
- **vs. notes:** `map-popup` vs `popover`/`hover-card`; `location-search` vs `combobox` and product `address-entry`.
- Commit: `feat(maps): maps scope — 10 components + 3 pages`.

---

### Task 15: `social` scope

Follow the **Shared procedure** with:
- **Scope key:** `social`. **Description:** `"Social UI: profile header, follow, user rows, reactions, post composer, share sheet, stories, suggestions, report/block; profile/feed/post/followers/explore pages"`.
- **Categories:** `social` "Social", `social-pages` "Social Pages" (`patterns`).
- **Spec section:** §4.13 (11 components + 6 pages; `social-landing` gets `requires_scopes: ["marketing"]`).
- **Token template:** no.
- **Sources:** Web Share API with copy-link fallback, WCAG 2.2.2 (stories auto-advance pause), 2.5.8 target size, ARIA APG `feed`; safety rules (report and block reachable from every post and profile; blocked-state copy).
- **vs. notes:** `post-composer` vs `composer`; `reaction-bar` vs messaging `message-reactions`; `profile-header` vs video `creator-header`.
- Commit: `feat(social): social scope — 11 components + 6 pages`.

---

### Task 16: Docs, counts, version 1.2.0, eval

**Files:**
- Modify: `SKILL.md` (frontmatter description line 8, line 41 counts, line 101 scope guidance, line 156 references list), `README.md` (lines 61 and 453 counts, plus a scope list section if one exists), `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `.cursor-plugin/plugin.json` (version `1.2.0` + counts in descriptions), `CHANGELOG.md`, `references/builder-brief.md`, `evals/evals.json`, `tests/test_ds.py` (raise the `assertGreaterEqual(len(ids), 306)` floor)

- [ ] **Step 1: Get the real numbers.**

```bash
python3 - <<'EOF'
import json, collections
m = json.load(open("assets/manifest.json"))
n = collections.Counter(); cats = len(m["categories"])
for c in m["categories"]:
    n[c.get("scope", "product")] += len(c["components"])
print(sum(n.values()), "components ·", cats, "categories ·", len(m["tiers"]), "tiers ·", len(m["scopes"]), "scopes"); print(dict(n))
EOF
```

- [ ] **Step 2: Raise the test floor.** In `test_manifest_consistency`, set `self.assertGreaterEqual(len(ids), <total from step 1>)`. Run the tests; they should pass.
- [ ] **Step 3: SKILL.md.**
  - Line 41: replace `306 components across 16 categories, 3 tiers and 5 scopes — ...` with the new numbers and the scope list.
  - Line 101: extend the scope guidance with one clause per new scope (`video`/`live`/`music`/`podcast` for media products, base `playback` added automatically; `reading` for books, comics, articles; `messaging` for person-to-person chat, channels, calls, support widget; `billing` for in-app subscriptions and payments; `analytics` for reports and metrics; `erp` for back-office records; `calendar` for scheduling; `maps` for location; `social` for profiles and following; landing pages for consumer scopes need `marketing` too).
  - Line 156: list the new reference files.
  - The frontmatter `description` must stay ≤ 1024 chars (`test_skill_frontmatter`) and SKILL.md < 500 lines.
- [ ] **Step 4: README + plugin manifests.** Update counts everywhere `306` appears (`grep -rn "306" README.md .claude-plugin .codex-plugin .cursor-plugin SKILL.md`). Set `"version": "1.2.0"` in all three plugin.json files (and marketplace.json if it carries a version).
- [ ] **Step 5: CHANGELOG.** Add a `## [1.2.0] - 2026-10-17` section above 1.1.0: Added (each scope with its counts, product additions, `scope_requires`, `requires_scopes`), Changed (`--scopes` help lists the manifest scopes; `test_all_scopes` covers every scope).
- [ ] **Step 6: builder-brief.md.** Add one line: "Opt-in scope categories read `references/components/<scope>.md`; landing pages (`requires_scopes`) compose marketing sections — build those first."
- [ ] **Step 7: Eval.** Append to `evals/evals.json` `evals`:

```json
{
  "id": 4,
  "prompt": "We're launching a podcast app with a public marketing site. Set up the design system foundations and build plan in ./design-system, standard tier — don't build components yet.",
  "expected_output": "ds.config.json scopes include product, podcast, marketing and the auto-added playback; playback tokens present; ds.py plan lists podcast-player, seek-bar and podcast-landing; phase not 'build'.",
  "files": []
}
```

- [ ] **Step 8:** `python3 -m unittest discover -s tests`. Expected: PASS (including `test_plugin_manifests_agree`, which needs `## [1.2.0]` in the CHANGELOG).
- [ ] **Step 9:** Commit `docs: 1.2.0 — new scopes across SKILL.md, README, plugin manifests, CHANGELOG, eval`.

---

## Execution notes

- Task 1 must land first. After that, Tasks 2–15 touch disjoint reference files, but they all edit `assets/manifest.json`. Run them serially, or in parallel with each subagent returning its `NEW` dict and doc file while the controller applies the manifest edits one at a time. Tasks 3 and 4 depend on Task 2 (playback); Task 4 also depends on Task 3.
- Task 16 runs last.
