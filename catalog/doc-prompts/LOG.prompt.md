Write `.claude/LOG.md`.

Dated headings (`## YYYY-MM-DD`), newest at top. Under each date, ONE LINE per material change:

```
- Added X (`path/to/file.py`).
- Fixed bug Y; root cause was Z.
```

Material means something that altered behavior or design — not "added docstring". This is a quick-scan history; `git log` already has the full record.
