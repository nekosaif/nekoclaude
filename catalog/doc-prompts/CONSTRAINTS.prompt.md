Write `.claude/CONSTRAINTS.md`.

List the hard constraints that bound future work. Group by category (Portability, Build, Trust boundary, Versions, etc.). For each, state what's required and (briefly) why.

These are things a future Claude session must NOT violate, even if it would simplify code. Examples:

- No new top-level dependencies without owner sign-off.
- Frontend must work without a build pipeline.
- All target mutations go through `app/services/apply.py`.

Be terse — bullets, not paragraphs.
