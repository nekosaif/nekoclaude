# ARCHITECTURE.md

Concrete map of code → responsibilities. Companion to DESIGN.md (which covers the *why*); this covers the *what*.

## Layers

```
Browser
  HTMX requests → returns HTML partials, Alpine handles local state
  ↓
FastAPI routers   (app/routers/)
  Thin HTTP handlers. No filesystem writes outside services.
  ↓
Services          (app/services/)
  The only layer that touches a target .claude/ or the repo's catalog/
  ↓
Filesystem
  Target .claude/ dirs · repo catalog/ · repo logs/ · repo state/
```

## Module responsibilities

| Module | Owns |
|---|---|
| `app/main.py` | Wiring: include routers, mount static, lifespan |
| `app/config.py` | Paths, `Target` dataclass, slug derivation |
| `app/deps.py` | Session id cookie, target-by-id lookup |
| `app/templating.py` | Jinja2 instance + `pretty_json` filter |
| `routers/targets.py` | List/add/remove/discover tracked `.claude/` |
| `routers/installed.py` | Render the "what's installed" panel per target |
| `routers/catalog.py` | All catalog CRUD + templates + marketplaces + skill links |
| `routers/stage.py` | Cart add/remove/clear/diff |
| `routers/apply.py` | The Apply button |
| `routers/revert.py` | History + per-change revert |
| `routers/settings.py` | Read settings.json for a target |
| `services/claude_fs.py` | Read/write skills + settings + statusline on a target |
| `services/catalog_fs.py` | Catalog reads + git-based add/update; doc-prompt CRUD; marketplace helpers |
| `services/snapshot.py` | Selective copy of touched subtrees + restore |
| `services/changelog.py` | Append-only JSONL history per target |
| `services/apply.py` | The snapshot → write → log pipeline; revert orchestration |
| `services/stage.py` | In-memory cart keyed by session cookie |
| `services/preview.py` | Per-op file-by-file aligned diff |
| `services/targets_store.py` | `state/targets.json` persistence + filesystem discovery |
| `services/skill_links.py` | `state/skill_links.json` bookmark registry |
| `services/templates_lib.py` | Bundled starter library (settings presets + doc prompts) |
| `services/handoff_prompt.py` | Build the prompt file written to a project's `.claude/` |

## Request shapes

- Most endpoints return **HTML partials** (Jinja2). JSON endpoints exist only where Alpine needs them for client-side state (`/targets`, `/catalog/json`, `/stage/json`, `/history/{id}/json`, `/settings/{id}`).
- Form endpoints accept `application/x-www-form-urlencoded` (HTMX default) or `multipart/form-data`. Both work because FastAPI's `Form(...)` parses either.

## Error path

All form-mutation routes follow:

```python
try:
    do_the_work(...)
except (ValueError, FileExistsError, FileNotFoundError) as e:
    return _inline_error(request, str(e))   # 200 + HX-Retarget: #editor-error
return _full_catalog(request, flash="...")  # 200 + full panel re-render
```

Unhandled exceptions return 500, which the browser surfaces as a top-right toast via the global `htmx:responseError` listener.

## Frontend state

- `localStorage["nc.catalog.tab"]` — active catalog tab.
- `localStorage["nc.selectedTargets"]` — array of target ids the user has checked.
- Session cookie `nc_session` — opaque token used to scope the cart server-side.
- Alpine `x-data` scopes — collapsible sections (`showLib`, `showAddSkill`, `showLinks`, etc.). Not persisted; collapse on re-render is acceptable.
