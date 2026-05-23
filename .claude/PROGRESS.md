# PROGRESS.md

Snapshot of what's done vs what's pending. Lighter than HANDOFF.md — meant to be scanned in 30 seconds.

## Done

- FastAPI server + HTMX/Alpine/Tailwind UI, no build step.
- Targets: add/discover/remove, global + project scopes.
- Installed panel: user skills, plugin-sourced skills, settings JSON, status line.
- Catalog CRUD for all four types (skills, statuslines, settings presets, doc prompts).
- Add catalog skill from git URL; bulk update-all.
- Skill links registry (bookmark URLs separate from the catalog).
- Predesigned templates library: 8 settings presets, 9 doc prompts; Add as-is + Copy & edit.
- Marketplaces add via settings patch.
- Stage cart, side-by-side colored diff per op, apply with snapshot, per-change revert.
- Doc-scaffold hand-off to Claude via prompt file.
- Inline error rendering (HX-Retarget) + global error toast.
- Tab persistence in localStorage.
- 65-check end-to-end smoke test, all passing.

## In flight

- Repo-level documentation under `.claude/` (this file + the others).

## Not started

- Cart persistence to `state/carts.json` (currently in-memory, lost on uvicorn reload).
- First-run bootstrap from `templates_lib.py` (reset/re-seed catalog).
- Symlink-safe snapshots (`shutil.copy2` follows links today).
- Streamed progress for bulk update-all.
- Per-target settings.json editor (only preset patches today).
