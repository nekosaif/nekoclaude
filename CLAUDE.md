# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A local web UI to manage Claude Code configurations: `~/.claude/` (global) and per-project `.claude/` directories. The tool reads what's already there, exposes a curated catalog of preferred skills/statuslines/settings (full copies stored in `catalog/`), stages changes across one or many targets, applies them with a pre-write snapshot, and supports per-change revert.

## Run

```bash
uv sync
uv run uvicorn app.main:app --reload
```

Single command. No Node tooling — frontend is HTMX + Alpine + Tailwind via CDN, no build step.

## Architecture

- **`app/services/`** is the only layer that touches the filesystem. Routers never `open()` a `.claude/` file directly — they go through `claude_fs`, `catalog_fs`, `snapshot`, or `changelog`. This keeps the mutation surface auditable.
- **Mutations always go: snapshot → apply → log.** `apply.py` is the only router that writes to a target `.claude/`. It records a snapshot of just the subtrees it will touch into `logs/<target-slug>/snapshots/<change-id>/`, then writes, then appends a JSONL line to `logs/<target-slug>/history.jsonl`. Reverts replay snapshots and record their own history line (so reverts are themselves revertible).
- **Staging is in-memory per session.** `stage.py` keeps a per-session cart of pending ops; nothing hits disk until `/apply` is called. The cart is also mirrored to `localStorage` on the client so reloads don't lose it.
- **Plugin-sourced skills are read-only.** We surface them in the installed panel (parsed from `~/.claude/plugins/installed_plugins.json`) but never touch them — plugin lifecycle is Claude Code's own concern.

## Things that are not obvious from the code

- Target slugs are derived from the absolute path: `~/.claude/` → `global`, `/home/saif/foo/.claude/` → `home_saif_foo`. Used as dir names under `logs/`. See `app/services/changelog.py`.
- The doc-scaffold feature (HANDOFF/CHANGELOG/etc.) deliberately does **not** write the docs itself — it writes a prompt file into the project's `.claude/` and surfaces a `claude < …` command the user runs interactively. Source prompts live in `catalog/doc-prompts/` and are user-editable.
- The "Update from git" button on a catalog item clones to a temp dir, copies the relevant subtree over `catalog/<type>/<slug>/`, and bumps `manifest.json`. It never touches any target `.claude/` — that still requires staging + apply.

## Out of scope (don't add these without asking)

- Editing things under `~/.claude/projects/` (memory + sessions).
- Plugin install/enable/disable — handled by Claude Code.
- Auth on the web UI — assumed localhost-only, binds to 127.0.0.1.
- Remote sync — push/pull this repo by hand to move state between machines.
