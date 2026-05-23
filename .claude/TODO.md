# TODO.md

Flat list of next things. Group by intent, not status.

## Hardening

- [ ] Persist cart to `state/carts.json` (keyed by session id; write-through on every mutation).
- [ ] Symlink-safe snapshot: detect `is_symlink()` and preserve as symlink in `logs/<t>/snapshots/<cid>/`.
- [ ] Validate that `_paths_touched_by` covers every op in `_do_op`. Currently kept in sync by convention only.
- [ ] Settings JSON parse errors: surface in UI (the `__parse_error__` sentinel exists in `claude_fs.read_settings` but isn't displayed nicely).

## UX

- [ ] Per-target `settings.json` editor (CodeMirror via CDN, JSON-validated client-side).
- [ ] Streamed bulk update-all progress (SSE or polling).
- [ ] Multi-target selection affordance — checkboxes work but the "first selected drives the panel" model is confusing.
- [ ] Render skill descriptions as markdown in cards.

## Catalog & bootstrap

- [ ] "Bootstrap from templates" button per tab (adds any template not yet in catalog).
- [ ] Admin "Reset catalog to seeds" endpoint behind a confirm modal.
- [ ] Surface `source_subpath` editing on the manifest editor.

## Tests

- [ ] Move `/tmp/nc-smoke.sh` into the repo as `scripts/smoke.sh`.
- [ ] Add `pytest` coverage for `claude_fs`, `snapshot`, `apply` services — pure-function units.

## Docs

- [ ] Screenshot the UI for README.
- [ ] Document the "two-machine sync via git" workflow with an example.
