# ERRORS.md

Known bugs, edge cases, and historical incidents.

## Open

- **Cart is lost on uvicorn reload.** In-memory by design (see DECISIONS.md D4), but during dev this means every code edit nukes staged changes. Workaround: stage + apply in one sitting, or run without `--reload`.
- **`shutil.copy2` in snapshot follows symlinks.** A symlinked file in a `.claude/` would be dereferenced on snapshot and restored as a regular file on revert. No symlinks observed in real `.claude/` dirs, but defensive fix is in PLAN.md Phase 3.
- **Concurrent applies are not serialized.** No `fcntl` lock. Single-user assumption.
- **Settings file with `__parse_error__` sentinel renders raw text in the installed panel.** Acceptable but ugly. Should show a clear "unparseable JSON" header.

## Fixed

### Save button silently doing nothing (2026-05-23)

**Symptom:** clicking Save on Settings preset editor produced no visible feedback; the file did not update.

**Root cause:** form validation tripped a 400 on the server. HTMX 1.9.x swallows 4xx responses by default — no swap, no error UI. The user assumed it didn't work.

**Fix:** All form-mutation routes return 200 with `HX-Retarget: #editor-error` + the inline error partial. Added a global `htmx:responseError` listener that surfaces unhandled 4xx/5xx as a top-right toast. Also made the preset body parser accept empty input (treated as `{}`).

### Save jumps user back to Skills tab (2026-05-23)

**Symptom:** saving a preset reloaded the catalog panel, which re-initialized Alpine `x-data` with `tab: 'skills'`. The user thought their save reverted.

**Fix:** Persist active tab in `localStorage.nc.catalog.tab`; read on init.

### Empty-string url to `/skill-links` returned 422 (2026-05-23)

**Symptom:** FastAPI's `Form(...)` treats empty string as missing, so an empty url field returned a JSON 422 instead of our friendly inline error.

**Fix:** Changed to `Form("")` and validated inside the service (`skill_links.add` raises ValueError on empty url, caught by the route).

### marketplaces-panel didn't auto-load (2026-05-23)

**Symptom:** Clicking the Marketplaces tab showed "loading…" forever.

**Root cause:** Used `hx-trigger="intersect once"` but the panel sits inside an `x-show`'d div (display:none), and IntersectionObserver doesn't fire while hidden.

**Fix:** Changed to `hx-trigger="load"`. The fetch runs once on initial DOM connect; results stay cached in the swapped HTML until next catalog re-render.
