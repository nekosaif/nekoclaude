Write `DESIGN.md` at the repo root.

The audience is someone who has read the code but wants to understand the *why*. Architecture decisions, trade-offs, alternatives that were rejected and the reason.

Cover:

1. **Problem statement** — what this codebase is solving. One paragraph.
2. **Key decisions** — for each major architectural choice (storage, transport, framework, file layout, async model, etc.): the decision, two or three alternatives that were considered, and why this one won. Be honest about the trade-offs.
3. **Data model** — the core entities and their relationships. ASCII diagrams over prose where it helps.
4. **Failure modes** — what breaks first if load doubles, if a dependency goes down, if a write fails halfway.
5. **What we're deferring** — known weaknesses that are accepted for now, with the rough plan for when to revisit.

Strong opinions, lightly held. No bullet-soup — when reasoning matters, write paragraphs.
