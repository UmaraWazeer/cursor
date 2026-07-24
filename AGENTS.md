# AGENTS.md

## Cursor Cloud specific instructions

### Current state of the repo
- The `main` branch is effectively empty: it contains only `README.md` (a single `# cursor` heading). There is **no application, no build system, no test suite, and no dependency manifests** (`requirements.txt`, `package.json`, etc.) on `main`.
- The only real code that has existed in the repo lives on feature branches as **standalone Python 3 scripts** (e.g. squad-grouping / Confluence / Miro publishing helpers). These use **only the Python standard library** — there are no third-party dependencies to install.

### Runtimes available in the environment
- Python `3.12.x` (`python3`; note there is no bare `python` alias — use `python3`).
- Node `22.x` and npm `10.x`.

### How to work / verify
- There is nothing to `build`. For Python scripts, use `python3 -m py_compile <file>.py` as a lightweight syntax/lint check and `python3 <file>.py` to run.
- No linter or test framework is configured yet. If you add one (e.g. `ruff`, `pytest`), also add the corresponding manifest so the startup update script can install it (see below).

### Gotcha
- Some historical scripts (e.g. `squad_grouping.py`) **hardcode absolute output paths under `/workspace/`** rather than writing relative to the script. Running them can create untracked files (e.g. `squad_groups.md`, `squad_groups.json`) in the repo root — remove them afterward if you don't intend to commit them.

### Update script (startup)
- The configured startup update script only installs dependencies **if a manifest exists**: `pip3 install -r requirements.txt` when `requirements.txt` is present, and `npm ci`/`npm install` when a Node manifest is present. On the current (empty) `main` it is effectively a no-op. Add the relevant manifest when introducing dependencies so future agents get them automatically.
