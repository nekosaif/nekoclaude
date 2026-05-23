# MEMORY.md

Long-lived facts about this project.

## Glossary

- **Target** — a `.claude/` directory we manage. Either `global` (`~/.claude/`) or a project (`<some/path>/.claude/`).
- **Target slug** — deterministic short ID derived from the target's absolute path. `global` for the home one; `home_saif_foo` for `/home/saif/foo/.claude/`. Used as directory names under `logs/`.
- **Cart / staged ops** — pending changes the user has queued but not yet applied. Lives in memory keyed by session cookie.
- **Snapshot** — pre-write copy of the exact files/dirs an apply will touch. Lives at `logs/<target-slug>/snapshots/<change-id>/`. Used by revert.
- **Catalog** — this repo's curated library of installable items (skills, status lines, settings presets, doc prompts). User-editable via UI.
- **Templates library** — read-only set of *starter content* baked into `app/services/templates_lib.py`. You "Add" (clone into catalog) or "Copy & edit" (open editor pre-filled).
- **Skill link** — a bookmarked git URL kept in `state/skill_links.json`. Separate from the catalog; can be installed into the catalog later.
- **Marketplace** — a Claude Code plugin source (a key under `extraKnownMarketplaces` in `settings.json`). We surface them read-only and let users stage adds via a settings patch.

## External systems

- **Claude Code** (`~/.claude/`): the thing we manage. Plugin manifest at `~/.claude/plugins/installed_plugins.json` is read-only for us.
- **Tailscale** is how the server is reached from other devices on the user's tailnet. Server binds to `100.100.10.10:8000`.
- **CDN libs**: HTMX 1.9.12, AlpineJS 3.x, Tailwind v3 — all loaded directly from unpkg/cdn.tailwindcss.com. No npm involvement.
- **`uv`** for Python dependency / env management. Replaces pip+venv.

## Decisions worth remembering

- **Plugin-sourced skills are read-only.** We display them (parsed from `installed_plugins.json`) but never edit. Plugin lifecycle is Claude Code's domain — fighting that would create incompatibilities. See `app/services/claude_fs.py:list_plugin_skills`.
- **Active catalog tab is persisted in `localStorage` under `nc.catalog.tab`.** Necessary because save responses re-render the whole `#catalog-panel` div, which re-initializes Alpine. Without persistence, every save snaps the user back to the Skills tab. See `app/templates/partials/catalog_panel.html`.
- **The `humanizer` seed in the catalog has empty `source_git`.** Originally copied from `~/.claude/skills/humanizer/` at first-run, not cloned. Update-all correctly skips it. Don't "fix" this by inventing a source URL — that would break update-all when someone tries it on a fresh machine.
- **Error responses from form endpoints use `HX-Retarget: #editor-error`.** Returning bare 400s caused a silent-save bug; HTMX swallows 4xx by default. Keep the inline-error pattern; don't switch to raising HTTPException for form-layer validation.
- **Status line scripts are chmod'd 0o755 on write.** Claude Code invokes them; they need to be executable. See `app/services/claude_fs.py:install_statusline` and `catalog_fs.py:write_statusline`.

## Don't-repeat-this

- **Don't bypass `app/services/apply.py`.** Early in development a direct `claude_fs.install_skill()` call from a router skipped the snapshot step. Reverting that change was impossible. Apply is the only legal mutation entry point. Enforced by convention, not by types — be careful.
- **Don't rename catalog slugs through the editor.** The UI's Edit form for skills does not let you change the slug for a reason: the slug is the directory name, used to look up installed copies on targets. Renaming would orphan all prior installs and snapshots. Delete + re-add if you really need a different slug.
- **Don't autostart bulk update on page load.** Tempting, but cloning N repos at startup is slow and you might be offline. Keep it behind the explicit "↻ Update all" button with the confirm prompt.
