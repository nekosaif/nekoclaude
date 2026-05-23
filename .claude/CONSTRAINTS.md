# CONSTRAINTS.md

Hard constraints — things you can't violate without breaking the project.

## Portability

- The repo must work after `git clone` + `uv sync` + `uv run uvicorn app.main:app` on Linux and macOS. No machine-specific paths in tracked files (only `state/targets.json` and `state/skill_links.json` may contain machine-local data; both are git-ignored if the user prefers).
- No assumption of being inside `$HOME` or any particular CWD. `app/config.py` derives the repo root from `__file__`.

## No build pipeline for the frontend

- HTMX, Alpine, Tailwind are loaded from CDNs. We do not introduce `npm`, `node_modules`, Vite, or any bundler.
- Static assets in `app/static/` are hand-written CSS + vanilla JS.

## Single user, single process

- No assumption of concurrent users. Cart is per-session-cookie but isn't designed to scale.
- No file locking on `logs/`, `catalog/`, or `state/`. Concurrent applies could interleave; documented in DESIGN.md but not defended against.

## Trust boundary at the bind interface

- The HTTP server has no auth and no CSRF protection. The deployment model assumes the bound interface is trusted (localhost or trusted-LAN/tailnet only).
- Don't add features that would only be safe with auth (e.g. an exposed shell command runner).

## Mutations only via `apply.py`

- Routers must not `open()`, `write_text()`, `shutil.copy*`, or `os.remove` against a target `.claude/`. All writes go through `app/services/apply.py`, which snapshots first and logs after.
- Routes that need to mutate but bypass this discipline are bugs.

## Services own the filesystem boundary

- `app/services/` is the only layer that touches absolute paths outside the repo. Routers must not import `os.path` / `pathlib.Path` for anything beyond URL/route parsing.

## Plugin-installed skills are read-only

- We surface them via `claude_fs.list_plugin_skills()`. We never write to `~/.claude/plugins/`.

## No new top-level Python deps casually

- `pyproject.toml` should stay short. Anything we can do with stdlib (`difflib`, `pathlib`, `json`, `shutil`, `subprocess`), we do with stdlib.

## Versions

- Python ≥ 3.11 (required for `from __future__ import annotations` w/ `X | None` syntax to work cleanly).
- HTMX 1.9.x — not 2.x (2.x has breaking changes around request URL params).
