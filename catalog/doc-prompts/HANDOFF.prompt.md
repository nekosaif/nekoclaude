Write `HANDOFF.md` at the repo root.

The audience is a teammate (or future-you) who needs to pick up this codebase cold. Lead with the work-in-progress state, not the architecture.

Cover, in this order:

1. **Current state** — what's working, what's broken, what's half-built. Branch names, PRs in flight, uncommitted scratch.
2. **The next moves** — the 2–4 things that would be touched next, in priority order, with enough context for someone else to start without asking.
3. **Open questions** — decisions waiting on input, with the options that were considered.
4. **Gotchas** — things that surprised the author (failing tests that don't matter, env quirks, sneaky coupling between modules).
5. **Where to look** — file paths for the most critical entry points.

No marketing tone. Bullets and code references over paragraphs.
