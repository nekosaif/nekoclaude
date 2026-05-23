# CONVERSATION.md

Notes on what's been discussed between the operator and assistant during recent sessions. Not a transcript — a compressed summary of intent, scope changes, and pivots, so a future session can pick up the thread.

## 2026-05-23

**Initial brief** — build a web UI to manage Claude Code configs across machines. Two top-level scopes: global (`~/.claude/`) and project-specific. UI should:

- List installed skills + the curated catalog separately.
- Stage changes (don't install immediately); apply via a button; log + revert.
- Manage settings, status lines, and have a "scaffold these docs" hand-off to Claude.

**Stack** — Python + uv (operator's preference), HTMX/Alpine/Tailwind via CDN. No Node tooling.

**Built in order:** scaffold → services → routers → UI partials → catalog seed → smoke test. Then iterated:

1. Doc-prompt CRUD UI.
2. Marketplace + add-skill-from-git UI.
3. CRUD for statuslines + presets + skill manifests.
4. Side-by-side colored diff preview.
5. Predesigned templates library (Add as-is + Copy & edit).
6. **Save bug fix** — root cause: HTMX swallowed 4xx silently, so Save appeared broken even when only some validation triggered the 400. Fix: `HX-Retarget` to an `#editor-error` slot + global toast for unhandled errors. Plus tab persistence in localStorage so save responses don't snap the user back to the Skills tab.
7. Skill links registry + bulk update-all.
8. Repo-level docs moved to `.claude/` and added to the templates library.

**Operator preferences seen in this thread:**

- Wants the server bound to `100.100.10.10` (Tailscale).
- Wants visible feedback (diff previews, toasts) rather than silent success.
- Often asks for "every button" testing — comprehensive smoke runs are appreciated.
- Wants the curated library to grow over time — both for skills (via git links) and for templates.
- Prefers the `.claude/` convention for project docs over root-level .md files.
