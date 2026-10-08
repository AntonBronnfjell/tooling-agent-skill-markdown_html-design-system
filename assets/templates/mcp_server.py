#!/usr/bin/env python3
"""MCP server for this design system (stdio, JSON-RPC 2.0, Python stdlib only). Created by `ds.py mcp`.

Lets any MCP client (Claude, Cursor, VS Code, Codex, …) query the system instead of guessing:
  list_components · get_component · search · get_tokens · get_design_md
It reads what `ds.py llms` generates (dist/ds-index.json, llms/*.md) and DESIGN.md — rerun `ds.py llms` after changes.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROTOCOL = "2025-06-18"


def index():
    p = ROOT / "dist" / "ds-index.json"
    if not p.exists():
        raise RuntimeError("dist/ds-index.json missing — run `ds.py llms <design-system dir>` first")
    return json.loads(p.read_text())


def text(s):
    return {"content": [{"type": "text", "text": s}]}


def list_components(args):
    rows = index()["components"]
    for key in ("category", "scope", "tier"):
        if args.get(key):
            rows = [r for r in rows if r.get(key) == args[key]]
    if args.get("status") in ("ready", "missing"):
        rows = [r for r in rows if r["done"] == (args["status"] == "ready")]
    lines = [f"- {r['id']} ({r['category']}, {r['tier']}{'' if r['done'] else ', missing'}): {r['desc']}" for r in rows]
    return text(f"{len(rows)} components\n" + "\n".join(lines))


def get_component(args):
    cid = args.get("id", "")
    row = next((r for r in index()["components"] if r["id"] == cid or r["file"] == cid), None)
    if not row:
        return text(f"No component '{cid}'. Use list_components or search.")
    doc = ROOT / row["doc"]
    body = doc.read_text() if doc.exists() else "(no docs page yet — component not built)"
    return text(f"{json.dumps(row, indent=1)}\n\n{body}")


def search(args):
    q = (args.get("query") or "").lower().split()
    scored = []
    for r in index()["components"]:
        hay = " ".join([r["id"], r["name"], r["desc"], r["category"], " ".join(r.get("demos", []))]).lower()
        score = sum(hay.count(w) for w in q)
        if score:
            scored.append((score, r))
    scored.sort(key=lambda x: -x[0])
    return text("\n".join(f"- {r['id']}: {r['name']} — {r['desc']}" for _, r in scored[:15]) or "No matches.")


def get_tokens(args):
    tokens = index()["tokens"]
    theme = args.get("theme") or "light"
    if theme not in tokens:
        return text(f"Unknown theme '{theme}'. Themes: {', '.join(tokens)}")
    prefix = args.get("prefix", "")
    rows = {k: v for k, v in tokens[theme].items() if k.startswith(prefix)}
    return text(json.dumps(rows, indent=1))


def get_design_md(_args):
    p = ROOT / "DESIGN.md"
    return text(p.read_text() if p.exists() else "DESIGN.md missing — run `ds.py design-md`.")


TOOLS = {
    "list_components": (list_components, "List design-system components, optionally filtered.",
                        {"category": {"type": "string"}, "scope": {"type": "string"}, "tier": {"type": "string"},
                         "status": {"type": "string", "enum": ["ready", "missing"]}}),
    "get_component": (get_component, "Full docs for one component: usage, anatomy, every variant/state as HTML, accessibility, tokens.",
                      {"id": {"type": "string", "description": "component id or file name, e.g. button-primary or button"}}),
    "search": (search, "Find components by keyword (name, description, states).", {"query": {"type": "string"}}),
    "get_tokens": (get_tokens, "Design tokens as CSS custom properties with resolved values for a theme.",
                   {"theme": {"type": "string", "description": "light (default), dark, high-contrast, …"},
                    "prefix": {"type": "string", "description": "e.g. --color-action or --space"}}),
    "get_design_md": (get_design_md, "The DESIGN.md contract: tokens front matter, rules, do's and don'ts.", {}),
}


def handle(msg):
    method, mid, params = msg.get("method"), msg.get("id"), msg.get("params") or {}
    if method == "initialize":
        result = {"protocolVersion": params.get("protocolVersion", PROTOCOL), "capabilities": {"tools": {}},
                  "serverInfo": {"name": "design-system", "version": "1.0.0"},
                  "instructions": "Use these tools before writing UI: reuse components and tokens instead of inventing styles."}
    elif method == "tools/list":
        result = {"tools": [{"name": n, "description": d, "inputSchema": {"type": "object", "properties": props}}
                            for n, (_, d, props) in TOOLS.items()]}
    elif method == "tools/call":
        name = params.get("name")
        if name not in TOOLS:
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32602, "message": f"Unknown tool {name}"}}
        try:
            result = TOOLS[name][0](params.get("arguments") or {})
        except Exception as e:  # noqa: BLE001 - report tool errors to the client, don't crash
            result = {"content": [{"type": "text", "text": f"Error: {e}"}], "isError": True}
    elif method == "ping":
        result = {}
    elif mid is None:          # notifications (e.g. notifications/initialized) need no reply
        return None
    else:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"Method not found: {method}"}}
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            reply = handle(json.loads(line))
        except json.JSONDecodeError:
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
        if reply is not None:
            sys.stdout.write(json.dumps(reply) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
