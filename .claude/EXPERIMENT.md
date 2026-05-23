# EXPERIMENT.md

Ideas tried, scratch experiments, things considered but not committed.

## Tried

- **HTMX `hx-vals` with Alpine binding** for the skill-link install button. Switched to a hidden form approach because `:hx-vals` evaluating Alpine state was fragile across reloads.
- **Returning bare 400 for form validation errors.** Looked correct from the server. Was invisible in the browser. Replaced with `HX-Retarget: #editor-error` + 200 status.
- **Templates as files under `app/data/templates/`.** Switched to in-code lists in `app/services/templates_lib.py` because the values are small and code is easier to grep.

## Considered, not implemented

- **`htmx-ext-sse`** for streaming the bulk update-all progress. Listed in PLAN.md as Phase 4. The Python `subprocess.run(["git","clone",...])` call would need to become async; reasonable but not free.
- **CodeMirror via CDN** for the JSON editor in preset/settings forms. Plain textarea works; CodeMirror would add syntax highlighting and lint-on-the-fly. Worth doing once per-target settings editor lands.
- **Versioning catalog/ in git.** Currently mutable both ways: shipped seeds + UI edits. Could enforce that all catalog edits go through git commits. Would make state portable but constrains daily use. Deferred.
- **A "dry-run" Apply** that only renders diffs without writing. Half the value of the existing Diff button — would be nice as a top-level confirmation step before Apply but not essential.

## Failed paths

- **Auto-loading `#marketplaces-panel` via `hx-trigger="intersect once"`.** With Alpine's `x-show` (display:none) the IntersectionObserver doesn't always fire. Switched to `hx-trigger="load"`.

## Open ideas

- Make the catalog a git submodule pointing at an "official curated" repo, with the local catalog being an overlay. Lets users share curation without forking the whole tool. Complexity vs benefit unclear.
- Use the `/diff` endpoint output for a "compare two targets" view — "what's different between global and this project's settings?". Cheap to build, useful for sync verification.
