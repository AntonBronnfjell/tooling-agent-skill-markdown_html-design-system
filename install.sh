#!/usr/bin/env sh
# Install html-design-system into Claude Code, Codex, Cursor, Copilot, Gemini CLI, Windsurf, Cline, Kiro, Roo, OpenCode, ...
#   ./install.sh [install.py options]                     from a clone (e.g. ./install.sh --tools all)
#   curl -fsSL https://raw.githubusercontent.com/AntonBronnfjell/tooling-agent-skill-markdown_html-design-system/main/install.sh | sh -s -- [options]
set -eu

PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(sys.version_info < (3, 8))' 2>/dev/null; then PY="$c"; break; fi
done
[ -n "$PY" ] || { echo "Python 3.8+ is required (the skill's scripts need it too)." >&2; exit 1; }

DIR=$(CDPATH= cd -- "$(dirname -- "$0")" 2>/dev/null && pwd || echo "")
if [ -z "$DIR" ] || [ ! -f "$DIR/install.py" ]; then
  HDS_REPO="${HDS_REPO:-https://github.com/AntonBronnfjell/tooling-agent-skill-markdown_html-design-system.git}"
  command -v git >/dev/null 2>&1 || { echo "git is required for remote install." >&2; exit 1; }
  DIR=$(mktemp -d)
  trap 'rm -rf "$DIR"' EXIT
  git clone --depth 1 "$HDS_REPO" "$DIR" >/dev/null 2>&1
fi

"$PY" "$DIR/install.py" "$@"
