# DECISIONS.md

ADR-style log of architectural calls. Each entry: what, why, when, what we rejected.

## D1 — Files on disk, no database (initial)

**What:** `catalog/`, `logs/`, `state/` are flat directories. No sqlite.
**Why:** The repo doubles as portable config — `git clone` on a new machine produces a working installation. A database breaks that.
**Rejected:** sqlite (hides state); a single big JSON (concurrent write problems).

## D2 — Server-rendered HTML via HTMX (initial)

**What:** Frontend is HTMX + Alpine + Tailwind via CDN. No bundler.
**Why:** This is a personal tool with mostly server-state interactions. A React SPA would triple the surface area for no UX gain.
**Rejected:** React + Vite (build pipeline), SvelteKit (full-stack overhead).

## D3 — Apply is the only mutation entry point (initial)

**What:** Mutations to a target's `.claude/` go through `app/services/apply.py`. Snapshots happen before writes; history is appended after.
**Why:** Makes revert work uniformly across all op kinds, and keeps the audit trail honest.
**Rejected:** Per-router writes (no way to enforce snapshot discipline).

## D4 — In-memory staging cart (initial)

**What:** `app/services/stage.py` keeps carts in a `dict[session_id, list[Op]]`.
**Why:** Carts are intent-of-the-moment, not durable state. Crashing or restarting wipes them; that's fine.
**Rejected:** Persist to disk (added complexity; cart-recovery semantics get fiddly).
**Revisit:** D4-R below.

## D5 — Doc scaffold hands off to Claude

**What:** Doc-scaffold writes a prompt file into the project's `.claude/` and surfaces a `claude < …` command. The tool does not write the docs itself.
**Why:** The user wants context-aware docs, not generic templates. Letting Claude read the codebase produces better output.
**Rejected:** Server-side template fill-in (too dumb); spawning `claude` from the daemon (UX confusion).

## D6 — HX-Retarget for form errors

**What:** Form endpoints that fail validation return 200 with `HX-Retarget: #editor-error` + `HX-Reswap: innerHTML`.
**Why:** Returning bare 4xx causes HTMX to silently swallow the response. Users saw "Save doesn't work" without any indication of why.
**Rejected:** Raising HTTPException(400, detail=…) — invisible to the user.

## D7 — Active tab persisted in localStorage

**What:** Catalog tab is stored as `nc.catalog.tab` in localStorage and read on Alpine init.
**Why:** Save responses re-render `#catalog-panel`, which re-initializes Alpine. Without persistence the user is yanked back to the Skills tab on every save.
**Rejected:** Don't re-render the whole panel (would require per-tab partial endpoints — more code, more chances to drift).

## D8 — Templates library is code, not data

**What:** `app/services/templates_lib.py` defines the starter library as Python lists.
**Why:** The bundled library should be immutable per-release; users edit copies (in the catalog) rather than the templates themselves.
**Rejected:** Templates in `templates/` directory (would invite editing the source, causing surprise on git pull).

## D9 — Repo docs live in `.claude/` (this addition)

**What:** AGENT, CHANGELOG, DESIGN, HANDOFF, MEMORY, PLAN, SECURITY, plus PROGRESS, TODO, ARCHITECTURE, DECISIONS, CONSTRAINTS, CONVERSATION, EXPERIMENT, LOG, ERRORS all live in `.claude/`. Only `CLAUDE.md` and `README.md` are at root.
**Why:** The `.claude/` directory is the conventional home for Claude-context files; co-locating them keeps the root clean and matches what Claude Code looks for.
**Rejected:** Standard docs at root (clutters the project view, mixes audience: GitHub readers vs Claude sessions).

## D4-R (revisit later) — Cart persistence

Likely to flip if uvicorn reload during dev keeps eating staged changes. Cheap fix.
