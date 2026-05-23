Write or update `CHANGELOG.md` at the repo root.

Use [Keep a Changelog](https://keepachangelog.com/) format with semver section headings. If a changelog already exists, **append** new sections — do not rewrite history.

Walk `git log` (oldest → newest if no prior changelog, else from the last documented version) and group entries under: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`. Skip trivial commits (typo fixes, formatting, merge commits). Be concise — one line per change, present tense.

Leave an unreleased `## [Unreleased]` section at the top for in-flight work.
