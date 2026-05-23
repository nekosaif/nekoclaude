# nekoclaude

Local web UI to manage Claude Code configs across machines. Manages `~/.claude/` (global) and any number of project-local `.claude/` directories from a single browser tab. Every change is staged, diff-previewed, and applied with a snapshot so it can be reverted.

## Quick start

```bash
uv sync
uv run uvicorn app.main:app --reload          # binds 127.0.0.1:8000
```

Or to reach it from other devices on a tailnet / LAN:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open the host in a browser.

## How it works

Diagrams generated using the bundled [architecture-diagram](catalog/skills/architecture-diagram/) skill (dark-theme SVG following its design system). Interactive versions with PNG/PDF export at [`docs/architecture.html`](docs/architecture.html) and [`docs/apply-flow.html`](docs/apply-flow.html).

### System architecture

![nekoclaude architecture](docs/architecture.svg)

Browser → FastAPI routers → services (the filesystem-boundary layer) → either the repo's own storage (`catalog/`, `logs/`, `state/`) or out to a target `.claude/` directory. Mutations always snapshot first.

### Apply flow

![Apply request flow](docs/apply-flow.svg)

Click Apply → cart is read → for each target, the touched paths are snapshotted into `logs/<t>/snapshots/<cid>/` → claude_fs writes to the target → changelog appends a JSONL line → response renders per-target results.

## Layout

```
app/
  main.py             FastAPI entrypoint, routers + static
  config.py           Path constants, Target dataclass, slug derivation
  deps.py             Session id + target resolution helpers
  templating.py       Jinja2 instance + pretty_json filter
  routers/            Thin HTTP handlers; no fs writes outside services
  services/           Only layer that touches .claude/ filesystems
    claude_fs.py        read/write skills + settings + statusline on targets
    catalog_fs.py       read/write the repo's catalog/
    apply.py            the snapshot→write→log mutation pipeline
    snapshot.py         selective copy + restore for revert
    changelog.py        per-target append-only JSONL
    stage.py            in-memory cart keyed by session cookie
    preview.py          side-by-side aligned diffs for staged ops
    targets_store.py    state/targets.json persistence + discovery
    skill_links.py      state/skill_links.json bookmark registry
    templates_lib.py    bundled starter library of presets + doc prompts
  templates/          Jinja2 templates (base + partials)
  static/             app.css, app.js

catalog/
  skills/<slug>/        manifest.json + SKILL.md + supporting files
  statuslines/<slug>/   manifest.json + statusline.sh
  settings-presets/<slug>/  manifest.json + settings.partial.json
  doc-prompts/          <KIND>.prompt.md files

logs/<target-slug>/   history.jsonl + snapshots/<change-id>/
state/                targets.json, skill_links.json
```

Project docs live in [`.claude/`](.claude/) (the directory Claude Code auto-loads):

- [`.claude/PROGRESS.md`](.claude/PROGRESS.md) — what's done vs what's pending (30-second scan)
- [`.claude/TODO.md`](.claude/TODO.md) — flat list of next things
- [`.claude/ARCHITECTURE.md`](.claude/ARCHITECTURE.md) — module → responsibility map
- [`.claude/DESIGN.md`](.claude/DESIGN.md) — trade-offs and rejected alternatives
- [`.claude/DECISIONS.md`](.claude/DECISIONS.md) — ADR-style log
- [`.claude/CONSTRAINTS.md`](.claude/CONSTRAINTS.md) — hard rules
- [`.claude/HANDOFF.md`](.claude/HANDOFF.md) — current WIP state for a pickup
- [`.claude/MEMORY.md`](.claude/MEMORY.md) — glossary + don't-repeat-this
- [`.claude/CONVERSATION.md`](.claude/CONVERSATION.md) — operator-intent thread
- [`.claude/EXPERIMENT.md`](.claude/EXPERIMENT.md) — tried / considered / failed
- [`.claude/LOG.md`](.claude/LOG.md) — dated work log
- [`.claude/ERRORS.md`](.claude/ERRORS.md) — known bugs + fixed incidents
- [`.claude/AGENT.md`](.claude/AGENT.md) — operating manual for future Claude sessions
- [`.claude/PLAN.md`](.claude/PLAN.md) — next milestone
- [`.claude/SECURITY.md`](.claude/SECURITY.md) — threat model
- [`.claude/CHANGELOG.md`](.claude/CHANGELOG.md) — chronological changes
