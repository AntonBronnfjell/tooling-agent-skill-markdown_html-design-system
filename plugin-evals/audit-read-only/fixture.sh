#!/usr/bin/env bash
# Seed a small "legacy" app: teal brand, IBM Plex, ad-hoc CSS (mirrors evals/files/legacy-app).
set -euo pipefail
mkdir -p legacy-app
cat > legacy-app/styles.css <<'CSS'
:root { --brand: #0f766e; --brand-dark: #115e59; --text: #1f2937; }
body { font-family: "IBM Plex Sans", Arial, sans-serif; color: #1f2937; font-size: 15px; }
.btn { padding: 9px 14px; border-radius: 6px; background: #0f766e; color: #fff; border: 0; }
.btn:hover { background: #115e59; }
.card { padding: 18px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,.12); background: #fff; }
.alert-error { background: #fee2e2; color: #b91c1c; padding: 12px; }
.input { border: 1px solid #d1d5db; padding: 8px 10px; border-radius: 6px; }
.input:focus { outline: none; border-color: #0f766e; }
CSS
cat > legacy-app/index.html <<'HTML'
<!doctype html><html><head><link rel="stylesheet" href="styles.css"></head><body>
<div class="card"><h2>Shipments</h2><input class="input" placeholder="Search"><button class="btn">Create</button>
<div class="alert-error">2 shipments delayed</div></div></body></html>
HTML
git init -q && git add -A && git -c user.email=e@e -c user.name=e commit -qm init
