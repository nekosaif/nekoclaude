# Changelog

All notable changes to this project will be documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/) loosely; this project pre-dates a formal release cadence so dates are used in place of versions until a 0.1.0 tag.

## [Unreleased]

### Added

- Skill links registry (`state/skill_links.json`): bookmark a git URL + suggested slug; install into the catalog later. Lives in the Skills tab as a collapsible panel.
- Bulk **Update all** button in the Skills tab — re-fetches every catalog skill whose manifest has a `source_git`. Returns a per-skill result list (ok / failed / skipped).
- Predesigned templates library (`app/services/templates_lib.py`): 8 settings presets + 9 doc prompts. "Add as-is" and "Copy & customize" flows for both Settings presets and Doc scaffold tabs.
- Side-by-side colored diff preview for staged ops. Each cart item has a Diff button; aligned left/right rows with green/red/neutral backgrounds.
- Marketplaces tab: shows current `extraKnownMarketplaces`, stages adds via a settings patch on the global target.
- Catalog CRUD across all four types — skills (add-from-git, edit manifest, delete, update-from-git), status lines (create/edit/delete with editable script body), settings presets (create/edit/delete with JSON editor), doc prompts (raw read, create/edit/delete with editable Markdown body).
- Doc-scaffold handoff: writes a `.nekoclaude-handoff-prompt.md` into the project's `.claude/` and tells the user to run `claude < …` to generate the docs.
- Repo-level docs: AGENT.md, DESIGN.md, HANDOFF.md, MEMORY.md, PLAN.md, SECURITY.md.

### Changed

- Active catalog tab now persists in `localStorage` (`nc.catalog.tab`). Previously, every save snapped the UI back to the Skills tab.
- Form endpoints that fail validation now return 200 with `HX-Retarget: #editor-error` so the inline error renders without destroying the form. Previously they returned bare 400s which HTMX silently swallowed.
- Global `htmx:responseError` listener surfaces any unhandled 4xx/5xx as a top-right toast.
- Empty preset body is treated as `{}` (no-op) instead of failing.

### Fixed

- Save button on Settings presets, Status lines, Doc prompts, and Skill manifest all work end-to-end now. Errors surface inline; successes show a toast + flash.

## Initial commit

- FastAPI server (`app/main.py`) bound by default to 127.0.0.1:8000.
- Target picker (global + tracked projects + discover under `$HOME`).
- Installed panel reads user skills, plugin-sourced skills, settings JSON, status line.
- Stage cart, apply (with snapshot), revert per change.
- HTMX + Alpine + Tailwind via CDN; no Node build step.
- Seed catalog: humanizer skill, colorful statusline, opus+xhigh preset, 7 doc prompts.
