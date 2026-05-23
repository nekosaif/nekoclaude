# PLAN.md

Plan for the next milestone: **harden the daily-use experience** before sharing the repo with another machine.

## Goal

Tool runs the same on a freshly cloned repo as on the current machine. Catalog-bootstrap, error-handling, and apply/revert are bulletproof for the single-user case.

## Non-goals

- Multi-user auth.
- Bulk apply across multiple machines from one UI (handled by `git push/pull` of the repo).
- A real frontend build pipeline.
- Plugin install/enable/disable.

## Phases

### Phase 1 — Persist the cart (S)

`app/services/stage.py` keeps the cart in a module-level dict. Lost on reload.

- Move to file-backed storage at `state/carts.json`, keyed by session id.
- Load on startup; write-through on every add/remove/clear.
- Verify: stage 3 ops → restart server → cart still shows 3 ops.

### Phase 2 — First-run bootstrap (S/M)

A freshly cloned repo's `catalog/` ships with the curated seeds. But a user on a new machine might want to wipe and re-seed from `templates_lib.py`.

- Add `/catalog/reset-to-seeds` admin endpoint (gated behind a confirmation modal).
- Add a "Bootstrap from templates" button in each tab that walks all templates and adds any that aren't in the catalog.
- Verify: rm -rf catalog/skills + catalog/statuslines + catalog/settings-presets + catalog/doc-prompts → click bootstrap → all default content restored.

### Phase 3 — Symlink-safe snapshots (S)

`snapshot.snapshot_path` follows symlinks via `shutil.copy2`. A symlinked file inside a target `.claude/` would be silently dereferenced on snapshot and again on restore — breaking the link.

- Detect symlinks; preserve them as symlinks in the snapshot dir.
- Verify: create a symlink inside `/tmp/nc-test/.claude/`, snapshot, restore, confirm it's still a link.

### Phase 4 — Better update-all UX (M)

`/catalog/skills/update-all` blocks the request for the duration of every clone.

- Stream progress via SSE or just `htmx-ext-sse`.
- Show a per-skill spinner during clone, final ok/fail tick.
- Verify: trigger with 5 catalog skills having real `source_git`; watch them resolve one-by-one.

### Phase 5 — Per-target settings editor (S)

Right now settings only flow through preset patches. A direct edit-this-target's-settings.json textbox would close the loop.

- New router `app/routers/settings.py` already has GET; add PUT that goes through `claude_fs.write_settings` via the apply pipeline.
- Editor partial with CodeMirror via CDN, JSON-validated client-side.
- Verify: open editor for `/tmp/nc-test`, change `model` field, save, verify the file content matches.

## Risks

- **Symlink behavior is OS-specific.** Linux symlinks behave one way, macOS hfsplus / apfs another, Windows... we don't run on Windows. Document Linux/macOS only.
- **SSE through uvicorn requires `httptools` + careful response buffering.** If it gets messy, just poll a `/catalog/skills/update-all/status` endpoint instead.
- **Carts persisted to disk become a small attack surface.** No real attack — single-user — but malformed JSON could crash startup. Wrap the load in try/except and reset on failure.

## Open questions

- Should the cart persistence be per-session (cookie-keyed) or just one cart globally for the single user? Probably global; sessions add no value here.
- Bootstrap should this overwrite existing catalog entries with the same slug, or skip? Default: skip with a "(already exists)" badge. Reset endpoint handles the wipe case explicitly.
- Should the per-target settings editor schema-validate against known Claude Code keys? Probably not — Claude Code may add keys we don't know about. Just validate JSON syntax.
