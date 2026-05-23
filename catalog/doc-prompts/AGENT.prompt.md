Write `AGENT.md` at the repo root.

This file is the operating manual a future Claude session reads before doing work in this repo. It is NOT a tutorial for humans — it's specifically for agentic Claude Code sessions.

Cover:

1. **Repo intent in one sentence.**
2. **What touches what** — the cross-file invariants that aren't obvious from any single file. Where does data flow? What's the contract between modules? Which file is the source of truth for X?
3. **Build / test / run** — the *minimum* commands needed to verify a change.
4. **Conventions to respect** — naming patterns, where to add new code of type X, what `// TODO`s mean here, what's deliberately unfinished.
5. **Don't do this** — pitfalls past sessions hit. Be specific: "don't add a new top-level dependency without checking pyproject.toml", "don't touch generated/ — it's overwritten", etc.

Skip generic dev advice. Skip anything `ls` and `grep` reveal.
