#!/usr/bin/env python3
"""Install the html-design-system skill into AI coding agents. Stdlib only, Python 3.8+.

  python3 install.py                      # user-level, auto-detect installed agents
  python3 install.py --tools all          # every known agent location
  python3 install.py --tools claude,kiro  # specific agents
  python3 install.py --project .          # project-level (commit the result to share with your team)
  python3 install.py --link               # dev mode: Claude Code gets a symlink to this repo (edits are live)
  python3 install.py --claude-hooks       # also add the lint/coverage hooks to Claude settings.json (always-on)
  python3 install.py --uninstall          # remove everything this installer created
  python3 install.py --list               # show agents, paths and detection status
  add --dry-run to any command to preview.

Layout it creates:
  Claude Code      ~/.claude/skills/html-design-system    full SKILL.md (scoped hooks, argument-hint)
  Shared standard  ~/.agents/skills/html-design-system    portable SKILL.md (agentskills.io frontmatter only)
                   → read by Codex, Cursor, Gemini CLI, GitHub Copilot, Windsurf/Devin, OpenCode, Amp, Goose, Junie
  Own folders      Kiro, Roo Code, Cline                  symlink → shared copy (copy if symlinks unavailable)
  Rule pointer     Continue (~/.continue/rules)           a rule telling the agent to read the skill
  Aider            no skill support: prints the `read:` line to add to .aider.conf.yml
"""
import argparse, glob, json, os, re, shutil, sys
from pathlib import Path

NAME = "html-design-system"
SRC = Path(__file__).resolve().parent
MARKER = ".installed-by-html-design-system"
EXCLUDE = {".git", ".github", "evals", "__pycache__", ".DS_Store", "install.py", "install.sh", "install.ps1", ".gitignore"}
CLAUDE_ONLY_KEYS = {"hooks", "argument-hint", "allowed-tools", "disable-model-invocation", "context", "model", "agent"}
HOME = Path.home()


def vscode_ext(prefix):
    return any(glob.glob(str(HOME / d / "extensions" / f"{prefix}*")) for d in (".vscode", ".vscode-insiders", ".cursor", ".windsurf"))


# kind: "claude" = full copy/link · "portable" = canonical stripped copy · "mirror" = link to portable · "rule" = pointer file
AGENTS = {
    "claude":   {"kind": "claude",   "user": HOME / ".claude/skills",   "project": ".claude/skills",
                 "detect": lambda: (HOME / ".claude").exists() or shutil.which("claude"),
                 "note": "Claude Code (project .claude/skills is also read by Copilot, Cline, OpenCode, Amp, Goose)"},
    "agents":   {"kind": "portable", "user": HOME / ".agents/skills",   "project": ".agents/skills",
                 "detect": lambda: True,
                 "note": "shared standard: Codex, Cursor, Gemini CLI, Copilot, Windsurf/Devin, OpenCode, Amp, Goose, Junie"},
    "kiro":     {"kind": "mirror",   "user": HOME / ".kiro/skills",     "project": ".kiro/skills",
                 "detect": lambda: (HOME / ".kiro").exists() or shutil.which("kiro"), "note": "Kiro"},
    "roo":      {"kind": "mirror",   "user": HOME / ".roo/skills",      "project": ".roo/skills",
                 "detect": lambda: (HOME / ".roo").exists() or vscode_ext("rooveterinaryinc.roo-cline"), "note": "Roo Code"},
    "cline":    {"kind": "mirror",   "user": HOME / ".cline/skills",    "project": ".cline/skills",
                 "detect": lambda: (HOME / ".cline").exists() or vscode_ext("saoudrizwan.claude-dev"), "note": "Cline"},
    "continue": {"kind": "rule",     "user": HOME / ".continue/rules",  "project": ".continue/rules",
                 "detect": lambda: (HOME / ".continue").exists() or vscode_ext("continue.continue"), "note": "Continue (rule pointer)"},
    # Optional explicit folders. These agents already read ~/.agents/skills, so they're only installed when named
    # (installing both would show the skill twice in some agents).
    "cursor":   {"kind": "mirror", "user": HOME / ".cursor/skills",            "project": ".cursor/skills",  "optional": True, "note": "Cursor (own folder)"},
    "copilot":  {"kind": "mirror", "user": HOME / ".copilot/skills",           "project": ".github/skills",  "optional": True, "note": "GitHub Copilot (own folder)"},
    "gemini":   {"kind": "mirror", "user": HOME / ".gemini/skills",            "project": ".gemini/skills",  "optional": True, "note": "Gemini CLI (own folder)"},
    "windsurf": {"kind": "mirror", "user": HOME / ".codeium/windsurf/skills",  "project": ".windsurf/skills", "optional": True, "note": "Windsurf (own folder)"},
    "devin":    {"kind": "mirror", "user": HOME / ".config/devin/skills",      "project": ".devin/skills",   "optional": True, "note": "Devin Desktop (own folder)"},
    "opencode": {"kind": "mirror", "user": HOME / ".config/opencode/skills",   "project": ".opencode/skills", "optional": True, "note": "OpenCode (own folder)"},
    "junie":    {"kind": "mirror", "user": HOME / ".junie/skills",             "project": ".junie/skills",   "optional": True, "note": "Junie (own folder)"},
    "codex":    {"kind": "mirror", "user": HOME / ".codex/skills",             "project": ".agents/skills",  "optional": True, "note": "Codex legacy folder"},
}


class Ctx:
    def __init__(self, dry):
        self.dry = dry

    def do(self, msg, fn=None):
        print(("[dry-run] " if self.dry else "") + msg)
        if fn and not self.dry:
            fn()


# ---------- building the skill folders ----------
def strip_frontmatter(text):
    """Remove Claude-only top-level keys (and their indented blocks) from YAML frontmatter."""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return text
    out, skip = [], False
    for line in m.group(1).splitlines():
        top = re.match(r"^([A-Za-z0-9_-]+):", line)
        if top:
            skip = top.group(1) in CLAUDE_ONLY_KEYS
        elif line and not line[0].isspace():
            skip = False
        if not skip:
            out.append(line)
    fm = "\n".join(out)
    if "compatibility:" not in fm:
        fm += "\ncompatibility: Requires Python 3.8+ for scripts/ds.py. Hooks are Claude Code only; other agents run ds.py check/coverage manually."
    return f"---\n{fm}\n---\n" + text[m.end():]


def copy_tree(dst, portable):
    def ignore(_d, names):
        return [n for n in names if n in EXCLUDE or n.startswith(".") or n.endswith("-workspace")]
    shutil.copytree(SRC, dst, ignore=ignore)
    if portable:
        p = dst / "SKILL.md"
        p.write_text(strip_frontmatter(p.read_text()))
    (dst / MARKER).write_text(json.dumps({"source": str(SRC), "portable": portable}) + "\n")


def is_ours(path):
    return path.is_symlink() or (path / MARKER).exists()


def clear(ctx, path):
    if path.is_symlink() or path.is_file():
        ctx.do(f"  remove {path}", path.unlink)
    elif path.exists():
        if not is_ours(path):
            sys.exit(f"Refusing to overwrite {path}: not created by this installer. Remove it manually.")
        ctx.do(f"  remove {path}", lambda: shutil.rmtree(path))


def link_or_copy(ctx, target, dst):
    def go():
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            dst.symlink_to(target, target_is_directory=True)
        except OSError:  # Windows without developer mode
            shutil.copytree(target, dst)
    ctx.do(f"  link {dst} -> {target}", go)


def rule_text(skill_dir):
    return f"""---
name: {NAME}
description: Use when the user wants to create, extend, audit or finish a design system, UI kit, component library or design tokens for the web.
alwaysApply: false
---

The full skill is installed at `{skill_dir}`. Before doing any design-system work, read `{skill_dir}/SKILL.md` and follow its workflow; its scripts run as `python3 {skill_dir}/scripts/ds.py`.
"""


# ---------- Claude hooks (optional, always-on) ----------
def our_hook(entry):
    return any("ds.py" in h.get("command", "") and " hook-" in h.get("command", "") for h in entry.get("hooks", []))


def claude_hooks(ctx, settings_path, skill_dir, remove=False):
    ds = f'python3 "{skill_dir}/scripts/ds.py"'
    entries = {"PostToolUse": {"matcher": "Write|Edit|MultiEdit", "hooks": [{"type": "command", "command": f"{ds} hook-post-edit"}]},
               "Stop": {"hooks": [{"type": "command", "command": f"{ds} hook-stop"}]}}
    data = json.loads(settings_path.read_text()) if settings_path.exists() else {}
    hooks = data.setdefault("hooks", {})
    for event, entry in entries.items():
        lst = [e for e in hooks.get(event, []) if not our_hook(e)]
        if not remove:
            lst.append(entry)
        if lst:
            hooks[event] = lst
        else:
            hooks.pop(event, None)
    if not hooks:
        data.pop("hooks")

    def write():
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        if settings_path.exists():
            shutil.copy(settings_path, settings_path.with_suffix(".json.bak"))
        settings_path.write_text(json.dumps(data, indent=2) + "\n")
    ctx.do(f"{'remove' if remove else 'add'} design-system hooks in {settings_path} (backup: .json.bak)", write)


# ---------- main ----------
def resolve(a):
    names = list(AGENTS)
    if a.tools == "all":
        chosen = [n for n in names if not AGENTS[n].get("optional")]
    elif a.tools == "auto":
        chosen = [n for n in names if not AGENTS[n].get("optional") and AGENTS[n]["detect"]()]
    else:
        chosen = [t.strip() for t in a.tools.split(",") if t.strip()]
        bad = [t for t in chosen if t not in AGENTS]
        if bad:
            sys.exit(f"Unknown agent(s): {', '.join(bad)}. Known: {', '.join(names)}")
    if any(AGENTS[n]["kind"] in ("mirror", "rule") for n in chosen) and "agents" not in chosen:
        chosen.insert(0, "agents")  # mirrors and rules point at the portable copy
    return chosen


def base_for(a, agent):
    if a.project:
        return Path(a.project).resolve() / AGENTS[agent]["project"]
    return AGENTS[agent]["user"]


def install(a):
    ctx = Ctx(a.dry_run)
    if sys.version_info < (3, 8):
        sys.exit("Python 3.8+ required.")
    chosen = resolve(a)
    portable_dir = base_for(a, "agents") / NAME
    print(f"Installing {NAME} ({'project ' + str(Path(a.project).resolve()) if a.project else 'user level'}) for: {', '.join(chosen)}")
    done_paths = set()
    for agent in chosen:
        spec = AGENTS[agent]
        dst = base_for(a, agent) / NAME
        if spec["kind"] == "rule":
            dst = base_for(a, agent) / f"{NAME}.md"
        if dst in done_paths:
            continue
        done_paths.add(dst)
        print(f"- {agent}: {spec['note']}")
        clear(ctx, dst)
        if spec["kind"] == "claude":
            if a.link and not a.project:
                link_or_copy(ctx, SRC, dst)
            else:
                ctx.do(f"  copy {dst}", lambda d=dst: (d.parent.mkdir(parents=True, exist_ok=True), copy_tree(d, portable=False)))
        elif spec["kind"] == "portable":
            ctx.do(f"  copy {dst} (portable frontmatter)", lambda d=dst: (d.parent.mkdir(parents=True, exist_ok=True), copy_tree(d, portable=True)))
        elif spec["kind"] == "mirror":
            target = os.path.relpath(portable_dir, dst.parent) if a.project else portable_dir
            link_or_copy(ctx, target, dst)
        elif spec["kind"] == "rule":
            skill_dir = portable_dir if not a.project else Path(AGENTS["agents"]["project"]) / NAME
            ctx.do(f"  write {dst}", lambda d=dst, s=skill_dir: (d.parent.mkdir(parents=True, exist_ok=True), d.write_text(rule_text(s))))
    if a.claude_hooks:
        settings = (Path(a.project).resolve() / ".claude/settings.json") if a.project else HOME / ".claude/settings.json"
        skill_dir = base_for(a, "claude") / NAME
        claude_hooks(ctx, settings, "$CLAUDE_PROJECT_DIR/.claude/skills/" + NAME if a.project else skill_dir)
    print("\nAider (no skill support): add to .aider.conf.yml →  read: [" + str(portable_dir / "SKILL.md") + "]")
    print("Done. Restart running agents so they pick up the skill. Try: \"build a design system for <your product>\".")


def uninstall(a):
    ctx = Ctx(a.dry_run)
    for agent, spec in AGENTS.items():
        dst = base_for(a, agent) / (f"{NAME}.md" if spec["kind"] == "rule" else NAME)
        if dst.is_symlink() or (dst.is_file() and spec["kind"] == "rule") or (dst.exists() and is_ours(dst)):
            clear(ctx, dst)
    settings = (Path(a.project).resolve() / ".claude/settings.json") if a.project else HOME / ".claude/settings.json"
    if settings.exists() and any(our_hook(e) for v in json.loads(settings.read_text()).get("hooks", {}).values() for e in v):
        claude_hooks(ctx, settings, "", remove=True)
    print("Uninstalled.")


def list_agents(a):
    for name, spec in AGENTS.items():
        det = "optional" if spec.get("optional") else ("detected" if spec["detect"]() else "not found")
        path = base_for(a, name) / (f"{NAME}.md" if spec["kind"] == "rule" else NAME)
        state = "installed" if path.exists() or path.is_symlink() else "-"
        print(f"{name:9} {det:10} {state:9} {path}  — {spec['note']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tools", default="auto", help="auto (default) | all | comma list: " + ",".join(AGENTS))
    ap.add_argument("--project", metavar="DIR", help="install into a project instead of your user profile")
    ap.add_argument("--link", action="store_true", help="symlink Claude Code install to this repo (live edits)")
    ap.add_argument("--claude-hooks", action="store_true", help="also register hooks in Claude settings.json")
    ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.list:
        list_agents(a)
    elif a.uninstall:
        uninstall(a)
    else:
        install(a)


if __name__ == "__main__":
    main()
