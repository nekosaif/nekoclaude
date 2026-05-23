# DESIGN.md

## Problem

Bootstrapping Claude Code (`~/.claude/`) on a new machine — and keeping configs in sync across machines — is a pile of manual `cp`, `git clone`, and `jq` edits. We want a single repo that can be `git clone`'d to any machine and a web UI that lets the user choose which curated skills, status lines, settings, and doc scaffolds to push into local `.claude/` directories (global or per-project), with revertible apply.

## Key decisions

### Storage: plain files in the repo

`catalog/`, `logs/`, `state/` are all flat directories of JSON + Markdown + shell scripts. **No database.**

- Alternative considered: sqlite for the cart, history, snapshots. Rejected because it breaks the "rsync the repo and you have your config on the new machine" property and adds a dependency.
- Trade-off: linear scans for everything. At catalog sizes <1000 entries, irrelevant.

### Frontend: HTMX + Alpine via CDN, no build step

The UI is server-rendered HTML partials. No bundler, no npm, no Vite.

- Alternative considered: React SPA + JSON API. Rejected because (a) this app's interactions are inherently server-state, (b) shipping a build pipeline contradicts the "lightweight portable repo" goal.
- Trade-off: rich client-side behavior is awkward. The diff viewer, for instance, is server-rendered each click rather than diffed in JS. Fine for a personal tool; would not scale to multi-user.

### Mutations always: snapshot → write → log

`apply.py` is the only router that mutates a target `.claude/`. Before any write, it copies the *touched* subtree into `logs/<target-slug>/snapshots/<change-id>/`. After the write, it appends one line to `history.jsonl`.

- Alternative considered: full `.claude/` dump per change. Rejected — wasteful for large `.claude/` dirs.
- Alternative considered: git on the target `.claude/`. Rejected — invasive, conflicts with the user's own git.
- Trade-off: revert restores files but doesn't undo *side effects* (e.g. if a status-line script triggered a session restart). In practice these are pure file ops, so this is fine.

### Staging is in-memory, per-session

The cart of pending changes lives in `app/services/stage.py` as a dict keyed by session cookie. Lost on server restart.

- Alternative considered: persist to `state/carts.json`. Rejected — carts represent a few clicks of intent; nothing valuable is lost.
- Trade-off: if you stage 10 changes then `uv run uvicorn` reloads (which happens on every code edit during dev), you lose them. Mild annoyance, surfaced via the dev-server reload behavior.

### Doc scaffold delegates to Claude

The HANDOFF/CHANGELOG/AGENT/etc. button writes a *prompt file* into the project's `.claude/` and tells the user to `claude < .claude/.nekoclaude-handoff-prompt.md`. The tool does not write the docs itself.

- Alternative considered: write template stubs directly. Rejected — the user wants context-aware docs, not generic templates.
- Alternative considered: invoke `claude` from the server. Rejected — interactive sessions are confusing when launched from a daemon; the user wants to see the work happen in their terminal.
- Trade-off: requires a manual second step. Tolerable for a tool used a few times per machine.

### Error visibility: HX-Retarget + global toast

Form endpoints that fail validation return 200 with `HX-Retarget: #editor-error` so the user sees the message inline without losing form state. Anything that escapes that (real 5xx, network failures) fires a top-right toast via `htmx:responseError`.

- Alternative considered: return 400 and let HTMX show a default error UI. Rejected — HTMX 1.x has no default error UI, and 400s caused the original "Save doesn't work" bug.

## Data model

```
Target           one of: global ~/.claude  or  project <path>/.claude/
  ├─ skills/<name>/SKILL.md       user-installed (managed by this tool)
  ├─ settings.json | settings.local.json
  └─ statusline.sh                                  (optional)

Catalog          curated library inside this repo
  ├─ skills/<slug>/         manifest.json + SKILL.md + supporting files
  ├─ statuslines/<slug>/    manifest.json + statusline.sh
  ├─ settings-presets/<slug>/  manifest.json + settings.partial.json
  └─ doc-prompts/<KIND>.prompt.md

Logs             append-only per-target history
  └─ <target-slug>/
      ├─ history.jsonl             one line per apply or revert
      └─ snapshots/<change-id>/    pre-mutation file copies
```

Op kinds in the cart: `install_skill`, `remove_skill`, `install_statusline`, `patch_settings`, `scaffold_docs`. Each maps to a write in `apply.py:_do_op` and a snapshot set in `apply.py:_paths_touched_by`. Keep these two in sync; adding an op kind to one without the other will silently break revert.

## Failure modes

- **Concurrent applies to the same target.** Two users (or two tabs) clicking Apply simultaneously will interleave snapshots and writes. No locking. In practice this is a single-user tool; if it grows, add `fcntl` lock per `logs/<target-slug>/`.
- **Disk full mid-snapshot.** The snapshot writes fail, then the mutation fails too. Result: partial snapshot directory, no history entry. Garbage-collectable by hand.
- **Network unreachable during `update_skill_from_git`.** Caught explicitly; raises `GitUpdateError` and the route returns an inline error with the git stderr. The catalog skill folder is rolled back before re-throwing.
- **Settings file has a `__parse_error__` key.** That's a sentinel `claude_fs.read_settings()` injects when the file is unparseable JSON. The UI surfaces it; deep-merging on top of an unparseable file would lose data, so we treat it as `{}` for staging purposes.

## What we're deferring

- **Plugin install/enable/disable.** Out of scope; Claude Code owns that. Surfacing them read-only is enough.
- **Auth.** Binds to a Tailscale IP at the user's request — assumed trusted tailnet. A real deployment would need at least HTTP basic auth.
- **Bulk apply to multiple machines from one UI.** This is a per-machine tool; cross-machine sync is "git push/pull the repo".
- **Schema validation for `settings.partial.json`.** We accept any JSON object; Claude Code does its own validation when it reads the merged file.
