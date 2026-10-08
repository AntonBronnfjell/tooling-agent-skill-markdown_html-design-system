# Plugin evals

`claude plugin eval` cases for this plugin (the skill-creator suite lives in `evals/evals.json`; the two tools don't read each other's files).

```bash
# trigger + safety cases build files and run ds.py, so grant tools and the scaffold:
claude plugin eval . --trust-plugin --scaffold --allow-tools Write Edit "Bash(python3 *)" Bash --runs 1
# negatives only (cheap):
claude plugin eval . --trust-plugin --tag negative --runs 3
```

| Case | Checks |
|---|---|
| new-system-foundations | skill fires; `ds.config.json` created; tokens use DTCG color objects; reply names direction + plan |
| extend-legacy-app | skill fires; `ds.py detect`/`audit` before writing; keeps teal brand + IBM Plex; app files untouched |
| audit-read-only | skill fires; zero `Write` calls; concrete findings |
| negative-python-function | skill must not fire |
| negative-css-question | skill must not fire |
