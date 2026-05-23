# AGENT.md

Operating manual for a future Claude Code session in this repo.

## Repo intent

Local web UI to manage Claude Code configs (`~/.claude/` global + per-project `.claude/`) across machines: read what's installed, stage curated changes, apply with snapshot+revert.

## What touches what

- **`app/services/` is the only layer that touches a target `.claude/` filesystem.** Routers never `open()` a target path directly. If you add a new mutation, add it to a service first and route it through `apply.py`.
- **Every write goes: snapshot → mutate → log.** `app/services/apply.py:_paths_touched_by` decides which subtrees get snapshotted before any write. If you add a new op kind, you MUST add its touched-paths to that switch — otherwise revert silently won't restore your write.
- **Staging is in-memory, keyed by session cookie** (`app/services/stage.py`). The cart is *not* persisted across server restarts. The client mirrors it in `localStorage` only for cross-tab visual continuity.
- **Plugin-sourced skills are read-only.** `claude_fs.list_plugin_skills()` reads `~/.claude/plugins/installed_plugins.json` and walks `installPath/skills/`. We display them but never edit them; plugin lifecycle belongs to Claude Code.
- **Target slugs are deterministic from absolute paths.** `config.slugify_path()` — global is the literal string `"global"`; everything else becomes the parent path with `/` replaced by `_`. Used as `logs/<slug>/` directory names.

## Build / test / run

```bash
uv sync
uv run uvicorn app.main:app --host 100.100.10.10 --port 8000 --reload
```

Smoke test all endpoints:

```bash
bash /tmp/nc-smoke.sh   # 65 checks; expect all PASS
```

Live activity is visible at the configured host:8000.

## Conventions

- **Editor partials follow one pattern.** Each has `<div id="editor-error" class="mb-2"></div>` + a form with `hx-{post|put}` and `hx-target="#catalog-panel"`. On validation failure the router returns `_inline_error(request, msg)` which sets `HX-Retarget: #editor-error` so the form fields persist. Do not break this contract — it's the difference between "Save works" and "Save silently fails".
- **Routers return HTML partials by default.** Use the matching `partials/*.html` template, not JSON. JSON variants exist only on `/catalog/json`, `/stage/json`, `/history/{id}/json`, `/targets` (for the Alpine bootstrap).
- **`hx-target` for editor saves is `#catalog-panel`.** This causes a full catalog re-render after a successful save. The active tab is preserved by Alpine reading `localStorage.getItem('nc.catalog.tab')` on init.
- **No JSON parsing in jinja templates** — pre-format in the router (`pretty_json` filter exists for display only).

## Don't do this

- **Don't bypass services.** Routers calling `open()` or `shutil` directly will eventually destroy a user's `.claude/` because they'll skip the snapshot step. The pattern exists for a reason.
- **Don't return bare 400s from form endpoints.** HTMX swallows them silently. Use `_inline_error` so the user sees what went wrong.
- **Don't touch `~/.claude/plugins/installed_plugins.json` or anything under `~/.claude/projects/`.** Those are Claude Code's domain.
- **Don't add backwards-compat shims for the cart format.** It's session-scoped and ephemeral — if you change the op shape, no migration is needed; just bump the cookie name or accept that in-flight carts get dropped.
- **Don't introduce a database.** Files in `catalog/`, `logs/`, `state/` are the whole storage layer. Adding sqlite breaks the "rsync the repo to a new machine" property.
- **Don't add new top-level deps casually.** Frontend deliberately uses CDN scripts (HTMX, Alpine, Tailwind) to avoid a Node build step. Keep Python deps in `pyproject.toml` minimal.
