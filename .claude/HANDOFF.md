# HANDOFF.md

## Current state

- All planned CRUD paths work: skills (add-from-git, edit manifest, delete, bulk update-all), status lines (create/edit/delete with editable script body), settings presets (create/edit/delete with JSON body editor), doc prompts (create/edit/delete + raw text reader), marketplaces (add-via-staged-settings-patch), targets (add/discover/remove).
- Stage → diff (side-by-side, color-coded) → apply (snapshot + log) → revert is end-to-end working.
- Skill links registry (`state/skill_links.json`) stores bookmarked git URLs that can be installed into the catalog later.
- Predesigned templates library (8 settings presets, 9 doc prompts) lives in `app/services/templates_lib.py`; both "Add as-is" and "Copy & customize" flows are wired.
- Smoke test: `/tmp/nc-smoke.sh` — 65 checks, all passing on last run.

## What's only partly built

- **`source_subpath`** for catalog skills is supported by the service layer (`add_skill_from_git`) but no UI surfaces it well for the simple "Update from git" path — it's only used at add time.
- **Statusline editor preview**: no live preview of what the script output will look like. User has to apply to see it.
- **Multi-target diff** works but the UI shows targets stacked, not side-by-side. Fine for 1–2 targets, gets long beyond that.
- **No bulk apply across targets from one cart op**: each op already supports multiple `target_ids`, but the UI's target picker is single-select-feeling; multi-select works via checkboxes but the affordance isn't obvious.

## The next moves

1. **Add per-target settings editor** — currently settings only flow through preset patches. A direct "edit settings.json" surface would be useful for one-off tweaks. Hook would go in `app/routers/settings.py` (already exists, only has GET) and a new editor partial.
2. **Cache the cart to `state/carts.json`** — cheap fix, removes the "uvicorn reload nuked my staged changes" annoyance during dev.
3. **Audit the snapshot for symlinks** — `snapshot.snapshot_path` uses `shutil.copy2` which follows symlinks. If a `.claude/` ever contains a symlink (uncommon but possible for plugins), revert would write to the wrong path. Use `copystat` + check `is_symlink()`.
4. **Markdown rendering for skill descriptions in cards** — descriptions are often multi-paragraph; currently they're rendered as plain text. A small `markdown-it` via CDN would be enough.

## Open questions

- Should the catalog be **versioned in git**, or treated as machine-local mutable state? Currently it's both — the repo ships seed entries, but the UI can add/edit. If the user expects two machines' catalogs to stay in sync, they need to commit after edits. Document this expectation in the README; haven't yet.
- Should `update-all-skills` run in a background task? Right now it's synchronous and blocks the request for as long as `git clone` takes. Fine for a handful of skills, terrible for 50.

## Gotchas

- **Cart is session-cookie keyed.** If you clear cookies you lose your cart. No big deal but worth knowing.
- **Catalog reload re-inits Alpine.** Active tab is preserved via `localStorage.getItem('nc.catalog.tab')`. Active sub-state inside a tab (e.g. `showLib`, `showAddSkill`) is NOT preserved. Acceptable; it just collapses on save.
- **`humanizer` catalog entry has empty `source_git`.** It was seeded by direct file copy at first-run, not cloned. Update-all currently skips it with "no source_git in manifest" — that's correct behavior.
- **The `app/templates/` directory has a name collision** with `templates` (the Jinja instance variable) in some imports. Don't name a new module `app/templates.py` — use `app/templating.py` (already does).
- **Server is bound to `100.100.10.10:8000`** (Tailscale). No auth. Anyone on the tailnet can drive the UI.

## Where to look

- Entry point: `app/main.py`
- Mutation hot path: `app/services/apply.py` → `claude_fs.py` + `snapshot.py` + `changelog.py`
- Cart: `app/services/stage.py` (in-memory) + `app/static/app.js` (`stage()` helper)
- UI shell: `app/templates/base.html`
- The biggest partial: `app/templates/partials/catalog_panel.html` (~250 lines, all 5 tabs)
- Smoke test: `/tmp/nc-smoke.sh`
