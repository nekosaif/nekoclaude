# LOG.md

Dated work log. Newest at top. One line per material change.

## 2026-05-23

- Authored `.claude/{PROGRESS,TODO,ARCHITECTURE,DECISIONS,CONSTRAINTS,CONVERSATION,EXPERIMENT,LOG,ERRORS}.md` for this repo.
- Moved AGENT/CHANGELOG/DESIGN/HANDOFF/MEMORY/PLAN/SECURITY into `.claude/` (only `CLAUDE.md` and `README.md` remain at root).
- Wrote mermaid `how it works` diagram into README.
- Skill links registry + bulk update-all shipped (`app/services/skill_links.py`, `app/templates/partials/skill_links_panel.html`).
- Templates library: 8 settings presets + 9 doc prompts wired into both "Add" and "Copy & edit" flows.
- Save bug fixed: HX-Retarget + global toast; catalog tab persisted in localStorage.
- Side-by-side colored diff preview added (`app/services/preview.py`).
- CRUD wired for statuslines, settings presets, doc prompts, and skill manifests.
- Marketplaces tab: add via staged settings patch on global.
- Initial scaffold + services + routers + UI + smoke test (65/65).
