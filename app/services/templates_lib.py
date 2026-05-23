"""Predesigned templates library.

Two flows in the UI per item:
- Add as-is: creates a catalog entry using this template's content + suggested slug.
- Copy & customize: opens the standard editor partial pre-filled with this template,
  letting the user pick their own slug and tweak the body before saving.
"""
from __future__ import annotations


SETTINGS_PRESET_TEMPLATES: list[dict] = [
    {
        "id": "opus-xhigh",
        "name": "Opus + xhigh effort",
        "description": "Sets model to opus and effortLevel to xhigh. Use for heavyweight thinking work.",
        "body": {"model": "opus", "effortLevel": "xhigh"},
    },
    {
        "id": "sonnet-medium",
        "name": "Sonnet + medium effort",
        "description": "Lighter default for routine tasks. Sonnet is faster; medium effort balances cost.",
        "body": {"model": "sonnet", "effortLevel": "medium"},
    },
    {
        "id": "haiku-low",
        "name": "Haiku + low effort",
        "description": "Cheapest option for simple, single-pass work.",
        "body": {"model": "haiku", "effortLevel": "low"},
    },
    {
        "id": "allow-readonly-bash",
        "name": "Allow read-only Bash",
        "description": "Permits common read-only shell commands without prompting (git status/diff, ls, cat, rg, grep, find, wc, head, tail).",
        "body": {
            "permissions": {
                "allow": [
                    "Bash(git status)",
                    "Bash(git diff:*)",
                    "Bash(git log:*)",
                    "Bash(git show:*)",
                    "Bash(ls:*)",
                    "Bash(cat:*)",
                    "Bash(rg:*)",
                    "Bash(grep:*)",
                    "Bash(find:*)",
                    "Bash(wc:*)",
                    "Bash(head:*)",
                    "Bash(tail:*)",
                    "Bash(pwd)",
                    "Bash(which:*)",
                ]
            }
        },
    },
    {
        "id": "allow-pkg-managers",
        "name": "Allow package managers",
        "description": "Permits npm/pnpm/uv/pip read commands and common dev-server invocations without prompting.",
        "body": {
            "permissions": {
                "allow": [
                    "Bash(npm install:*)",
                    "Bash(npm run:*)",
                    "Bash(npm test:*)",
                    "Bash(pnpm install:*)",
                    "Bash(pnpm run:*)",
                    "Bash(uv sync:*)",
                    "Bash(uv run:*)",
                    "Bash(pip install:*)",
                ]
            }
        },
    },
    {
        "id": "skip-dangerous-prompt",
        "name": "Skip dangerous-mode prompt",
        "description": "Bypasses the dangerous-mode confirmation. Use with care — most useful on trusted local machines.",
        "body": {"skipDangerousModePermissionPrompt": True},
    },
    {
        "id": "statusline-padding-2",
        "name": "Status line padding = 2",
        "description": "Slightly more vertical breathing room around the status line output.",
        "body": {"statusLine": {"padding": 2}},
    },
    {
        "id": "marketplace-thedotmack",
        "name": "Marketplace: thedotmack/claude-mem",
        "description": "Registers the thedotmack marketplace as a known source for plugins like claude-mem.",
        "body": {
            "extraKnownMarketplaces": {
                "thedotmack": {
                    "source": {"source": "github", "repo": "thedotmack/claude-mem"}
                }
            }
        },
    },
]


DOC_PROMPT_TEMPLATES: list[dict] = [
    {
        "id": "HANDOFF",
        "name": "HANDOFF.md",
        "description": "WIP state, next moves, open questions, gotchas. For someone picking up the work cold.",
        "body": """Write `HANDOFF.md` at the repo root.

The audience is a teammate (or future-you) who needs to pick up this codebase cold. Lead with the work-in-progress state, not the architecture.

Cover, in this order:

1. **Current state** — what's working, what's broken, what's half-built. Branch names, PRs in flight, uncommitted scratch.
2. **The next moves** — the 2–4 things that would be touched next, in priority order, with enough context for someone else to start without asking.
3. **Open questions** — decisions waiting on input, with the options that were considered.
4. **Gotchas** — things that surprised the author (failing tests that don't matter, env quirks, sneaky coupling between modules).
5. **Where to look** — file paths for the most critical entry points.

No marketing tone. Bullets and code references over paragraphs.
""",
    },
    {
        "id": "CHANGELOG",
        "name": "CHANGELOG.md",
        "description": "Keep-a-Changelog format; appends to existing if present.",
        "body": """Write or update `CHANGELOG.md` at the repo root.

Use [Keep a Changelog](https://keepachangelog.com/) format with semver section headings. If a changelog already exists, **append** new sections — do not rewrite history.

Walk `git log` (oldest → newest if no prior changelog, else from the last documented version) and group entries under: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`. Skip trivial commits (typo fixes, formatting, merge commits). Be concise — one line per change, present tense.

Leave an unreleased `## [Unreleased]` section at the top for in-flight work.
""",
    },
    {
        "id": "AGENT",
        "name": "AGENT.md",
        "description": "Operating manual for future Claude sessions in this repo.",
        "body": """Write `AGENT.md` at the repo root.

This file is the operating manual a future Claude session reads before doing work in this repo. It is NOT a tutorial for humans — it's specifically for agentic Claude Code sessions.

Cover:

1. **Repo intent in one sentence.**
2. **What touches what** — the cross-file invariants that aren't obvious from any single file. Where does data flow? What's the contract between modules? Which file is the source of truth for X?
3. **Build / test / run** — the *minimum* commands needed to verify a change.
4. **Conventions to respect** — naming patterns, where to add new code of type X, what `// TODO`s mean here, what's deliberately unfinished.
5. **Don't do this** — pitfalls past sessions hit. Be specific: "don't add a new top-level dependency without checking pyproject.toml", "don't touch generated/ — it's overwritten", etc.

Skip generic dev advice. Skip anything `ls` and `grep` reveal.
""",
    },
    {
        "id": "DESIGN",
        "name": "DESIGN.md",
        "description": "Architecture decisions, alternatives, trade-offs.",
        "body": """Write `DESIGN.md` at the repo root.

The audience is someone who has read the code but wants to understand the *why*. Architecture decisions, trade-offs, alternatives that were rejected and the reason.

Cover:

1. **Problem statement** — what this codebase is solving. One paragraph.
2. **Key decisions** — for each major architectural choice (storage, transport, framework, file layout, async model, etc.): the decision, two or three alternatives that were considered, and why this one won. Be honest about the trade-offs.
3. **Data model** — the core entities and their relationships. ASCII diagrams over prose where it helps.
4. **Failure modes** — what breaks first if load doubles, if a dependency goes down, if a write fails halfway.
5. **What we're deferring** — known weaknesses that are accepted for now, with the rough plan for when to revisit.

Strong opinions, lightly held. No bullet-soup — when reasoning matters, write paragraphs.
""",
    },
    {
        "id": "MEMORY",
        "name": "MEMORY.md",
        "description": "Long-lived project facts: glossary, externals, decisions, footguns.",
        "body": """Write `MEMORY.md` at the repo root.

This is a project-scoped memory file: long-lived facts about THIS project that future contributors (human or Claude) should not have to rediscover.

Cover:

1. **Domain glossary** — terms that mean something specific here. One line each.
2. **External systems** — what other services, APIs, dashboards, or repos this project depends on, and the canonical link/path for each.
3. **People and ownership** — who owns which module (if known). If solo, skip.
4. **Decisions worth remembering** — past calls that look weird in the code but were intentional. Tie each to the file or commit where the choice landed.
5. **Don't-repeat-this** — incidents, near-misses, or footguns. Two sentences each: what happened, how it was avoided going forward.

Keep it tight. If a fact is already in the code or in `git log`, don't restate it here.
""",
    },
    {
        "id": "PLAN",
        "name": "PLAN.md",
        "description": "Next milestone plan with phases, risks, open questions.",
        "body": """Write `PLAN.md` at the repo root.

A scoped, executable plan for the *next* milestone — not a roadmap. The reader is whoever picks up the work after you and needs to start coding.

Cover:

1. **Goal** — one sentence. What's done at the end.
2. **Non-goals** — what's explicitly out of scope. Be ruthless; everything not listed gets cut.
3. **Phases** — 3–6 ordered steps. For each: the change in code terms (which files, which functions), the verification step (test command, manual check), the rough size (S/M/L).
4. **Risks** — what could break or take longer than expected, and the mitigation.
5. **Open questions** — things the author isn't sure about. List them so they get answered before code starts, not during.

If the milestone is ambiguous, write the plan to clarify it — don't paper over the ambiguity.
""",
    },
    {
        "id": "SECURITY",
        "name": "SECURITY.md",
        "description": "Threat model, reporting, secrets, dependencies, known weaknesses.",
        "body": """Write `SECURITY.md` at the repo root.

Cover:

1. **Threat model in one paragraph** — what this codebase trusts, what it doesn't, and where the trust boundary is.
2. **Reporting a vulnerability** — preferred contact method, what info to include, expected response time. If unknown, leave a `<TODO: contact>` placeholder rather than inventing details.
3. **Secrets and credentials** — how they're stored, how they're rotated, what would happen if they leaked. Be specific: list the actual env vars / secret-manager paths used.
4. **Dependencies** — how upstream CVEs are tracked. Name the tool (dependabot, renovate, etc.) or be explicit that there isn't one yet.
5. **Known weaknesses** — what's accepted-as-is, with reasoning. Don't lie about a clean bill of health.

Be honest. A short, accurate SECURITY.md beats a long, aspirational one.
""",
    },
    {
        "id": "README",
        "name": "README.md",
        "description": "Standard project intro — what / why / install / run / layout.",
        "body": """Write or refresh `README.md` at the repo root.

Audience: someone landing on the repo for the first time.

Sections (in order):

1. **One-line tagline.**
2. **What it is** — two sentences max. What problem it solves; who it's for.
3. **Quick start** — the minimum commands to get it running locally. Copy-paste-able.
4. **Layout** — a flat list of top-level directories with one-line purposes.
5. **Links** — to CLAUDE.md / DESIGN.md / CONTRIBUTING / etc. if they exist.

Skip: badges no one will maintain, marketing language, table-of-contents for a short doc.
""",
    },
    {
        "id": "ROADMAP",
        "name": "ROADMAP.md",
        "description": "Forward-looking, less detailed than PLAN.md.",
        "body": """Write `ROADMAP.md` at the repo root.

Three sections, time-bounded:

1. **Now** — what is being actively worked on this week.
2. **Next** — what's lined up for the following 1–2 months. Brief, one line each.
3. **Later** — fuzzier bets, ideas that may or may not happen. Tag with `?` if uncertain.

This is NOT a commitment doc — items can shift between sections freely. Date the file (`Updated YYYY-MM-DD`).
""",
    },
    {
        "id": "PROGRESS",
        "name": ".claude/PROGRESS.md",
        "description": "Quick snapshot of done vs in-flight vs not-started. Scanned in 30 seconds.",
        "body": """Write `.claude/PROGRESS.md`.

Three flat sections, bullet-listed, no prose:

1. **Done** — material capabilities that are working today.
2. **In flight** — actively being worked on right now.
3. **Not started** — known next items that haven't been touched.

Be specific. "Auth" is bad. "JWT-based session auth with refresh tokens" is good. Cross-reference file paths or function names where it helps.
""",
    },
    {
        "id": "TODO",
        "name": ".claude/TODO.md",
        "description": "Flat checklist of next things, grouped by intent.",
        "body": """Write `.claude/TODO.md`.

Group items by intent (Hardening, UX, Tests, Docs, etc.). Within each group, GitHub-style checkboxes:

```
- [ ] Specific task with enough context to start without asking.
```

Skip status (in-progress, blocked, etc.) — that lives elsewhere. Skip items you've already done.
""",
    },
    {
        "id": "ARCHITECTURE",
        "name": ".claude/ARCHITECTURE.md",
        "description": "Module → responsibility map. Companion to DESIGN (the why); this is the what.",
        "body": """Write `.claude/ARCHITECTURE.md`.

Cover:

1. **Layers** — ASCII diagram showing the major layers (frontend, API, services, storage, etc.) with arrows for data flow.
2. **Module responsibilities** — a table: each module/file → one-line ownership statement.
3. **Request / event shapes** — what crosses the boundaries. JSON shapes, message types, etc.
4. **Frontend state** — what lives in URL, cookies, localStorage, server session.

Concrete file paths and function names. No marketing.
""",
    },
    {
        "id": "DECISIONS",
        "name": ".claude/DECISIONS.md",
        "description": "ADR-style log of architectural calls.",
        "body": """Write `.claude/DECISIONS.md`.

Each entry follows ADR-lite:

```
## D<n> — Short title (date)

**What:** one sentence stating the decision.
**Why:** the reasoning.
**Rejected:** alternative(s) considered and why they lost.
**Revisit:** (optional) trigger that would make us re-open this.
```

Number sequentially. Newest at bottom. Keep entries short — a paragraph each, not pages.
""",
    },
    {
        "id": "CONSTRAINTS",
        "name": ".claude/CONSTRAINTS.md",
        "description": "Hard rules — things you can't violate without breaking the project.",
        "body": """Write `.claude/CONSTRAINTS.md`.

List the hard constraints that bound future work. Group by category (Portability, Build, Trust boundary, Versions, etc.). For each, state what's required and (briefly) why.

These are things a future Claude session must NOT violate, even if it would simplify code. Examples:

- No new top-level dependencies without owner sign-off.
- Frontend must work without a build pipeline.
- All target mutations go through `app/services/apply.py`.

Be terse — bullets, not paragraphs.
""",
    },
    {
        "id": "CONVERSATION",
        "name": ".claude/CONVERSATION.md",
        "description": "Compressed summary of operator intent across recent sessions.",
        "body": """Write `.claude/CONVERSATION.md`.

NOT a transcript. A compressed summary so a future Claude session can pick up the thread without re-reading every prior message. Cover:

1. **Initial brief** — what the operator originally asked for.
2. **Scope changes / pivots** — when and why direction shifted.
3. **Operator preferences seen so far** — small things that matter (e.g., "prefers comprehensive smoke tests after changes", "binds server to Tailscale IP", "wants .claude/ for project docs").

Dated sections, newest at bottom or top — pick one and stick with it.
""",
    },
    {
        "id": "EXPERIMENT",
        "name": ".claude/EXPERIMENT.md",
        "description": "Ideas tried, considered, or rejected. Scratch space.",
        "body": """Write `.claude/EXPERIMENT.md`.

Three sections:

1. **Tried** — experiments that ran (whether or not they shipped). One paragraph each: what was tried, what was learned, where it ended up.
2. **Considered, not implemented** — ideas evaluated but deferred. Include the trade-off.
3. **Failed paths** — things that didn't work. Save the next session from repeating them.

This is the dump-ground for "I thought about doing X". Keep it; it's cheap to write and valuable to read months later.
""",
    },
    {
        "id": "LOG",
        "name": ".claude/LOG.md",
        "description": "Dated work log. One line per material change.",
        "body": """Write `.claude/LOG.md`.

Dated headings (`## YYYY-MM-DD`), newest at top. Under each date, ONE LINE per material change:

```
- Added X (`path/to/file.py`).
- Fixed bug Y; root cause was Z.
```

Material means something that altered behavior or design — not "added docstring". This is a quick-scan history; `git log` already has the full record.
""",
    },
    {
        "id": "ERRORS",
        "name": ".claude/ERRORS.md",
        "description": "Open bugs + historical incidents with root cause and fix.",
        "body": """Write `.claude/ERRORS.md`.

Two top sections:

1. **Open** — known bugs and edge cases not yet fixed. One bullet each.
2. **Fixed** — historical incidents. For each: dated subheader, symptom, root cause, fix. So a future session can search for "I'm seeing X" and find the precedent.

Be honest. Don't hide design weaknesses; future sessions need to know.
""",
    },
]


def list_settings_templates() -> list[dict]:
    return [
        {"id": t["id"], "name": t["name"], "description": t["description"]}
        for t in SETTINGS_PRESET_TEMPLATES
    ]


def get_settings_template(tid: str) -> dict | None:
    for t in SETTINGS_PRESET_TEMPLATES:
        if t["id"] == tid:
            return t
    return None


def list_doc_templates() -> list[dict]:
    return [
        {"id": t["id"], "name": t["name"], "description": t["description"]}
        for t in DOC_PROMPT_TEMPLATES
    ]


def get_doc_template(tid: str) -> dict | None:
    for t in DOC_PROMPT_TEMPLATES:
        if t["id"] == tid:
            return t
    return None
