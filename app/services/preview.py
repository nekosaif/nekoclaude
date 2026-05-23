"""Compute side-by-side diffs for a staged op without writing anything."""
from __future__ import annotations
from pathlib import Path
from typing import Iterable
import difflib
import json

from ..config import Target, CATALOG_DIR
from . import claude_fs


MAX_LINES_PER_FILE = 400  # truncate huge diffs for sanity
BINARY_SNIFF_BYTES = 1024


def _read_text(path: Path) -> str | None:
    """Read text file; return None if missing, '<binary>' if not utf-8 text."""
    if not path.is_file():
        return None
    try:
        chunk = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in chunk[:BINARY_SNIFF_BYTES]:
        return "<binary>"
    try:
        return chunk.decode("utf-8")
    except UnicodeDecodeError:
        return "<binary>"


def _aligned_diff(before: str | None, after: str | None) -> list[dict]:
    """Return aligned left/right rows. Each row: {left, right, tag}.

    tag ∈ {equal, delete, insert, replace}. None on a side means "blank".
    """
    a = (before or "").splitlines() if before is not None else []
    b = (after or "").splitlines() if after is not None else []
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    rows: list[dict] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                rows.append({"left": a[i1 + k], "right": b[j1 + k], "tag": "equal"})
        elif tag == "delete":
            for k in range(i2 - i1):
                rows.append({"left": a[i1 + k], "right": None, "tag": "delete"})
        elif tag == "insert":
            for k in range(j2 - j1):
                rows.append({"left": None, "right": b[j1 + k], "tag": "insert"})
        elif tag == "replace":
            la = i2 - i1
            lb = j2 - j1
            for k in range(max(la, lb)):
                rows.append({
                    "left": a[i1 + k] if k < la else None,
                    "right": b[j1 + k] if k < lb else None,
                    "tag": "replace",
                })
    if len(rows) > MAX_LINES_PER_FILE:
        rows = rows[:MAX_LINES_PER_FILE] + [{
            "left": f"... ({len(rows) - MAX_LINES_PER_FILE} more lines truncated) ...",
            "right": f"... ({len(rows) - MAX_LINES_PER_FILE} more lines truncated) ...",
            "tag": "equal",
        }]
    return rows


def _kind_for(before: str | None, after: str | None) -> str:
    if before is None and after is not None:
        return "added"
    if before is not None and after is None:
        return "removed"
    if before == after:
        return "unchanged"
    return "modified"


def _file_preview(rel: str, before: str | None, after: str | None) -> dict:
    return {
        "path": rel,
        "kind": _kind_for(before, after),
        "rows": _aligned_diff(before, after) if (before or after) else [],
    }


def _walk_files(d: Path) -> list[Path]:
    if not d.is_dir():
        return []
    return [p for p in sorted(d.rglob("*")) if p.is_file()]


def preview_install_skill(target: Target, slug: str) -> list[dict]:
    src_dir = CATALOG_DIR / "skills" / slug
    if not src_dir.is_dir():
        return [{"path": slug, "kind": "error", "error": f"catalog skill not found: {slug}"}]
    dest_dir = target.skills_dir / slug
    out: list[dict] = []
    # files from catalog (the new state), skipping manifest.json and .git
    src_files = []
    for p in _walk_files(src_dir):
        rel = p.relative_to(src_dir)
        parts = rel.parts
        if parts and parts[0] in (".git", "manifest.json"):
            continue
        if parts and parts[0] == "manifest.json":
            continue
        src_files.append(rel)
    # union with current files at dest (for files only present pre-install)
    dest_files = set()
    if dest_dir.is_dir():
        for p in _walk_files(dest_dir):
            dest_files.add(p.relative_to(dest_dir))
    src_set = set(src_files)
    all_rels = sorted(src_set | dest_files, key=lambda r: r.as_posix())
    for rel in all_rels:
        before = _read_text(dest_dir / rel) if (dest_dir / rel).is_file() else None
        after = _read_text(src_dir / rel) if rel in src_set else None
        out.append(_file_preview(f"skills/{slug}/{rel.as_posix()}", before, after))
    return out


def preview_remove_skill(target: Target, name: str) -> list[dict]:
    dest_dir = target.skills_dir / name
    if not dest_dir.is_dir():
        return [{"path": f"skills/{name}/", "kind": "noop", "rows": []}]
    out = []
    for p in _walk_files(dest_dir):
        rel = p.relative_to(dest_dir)
        before = _read_text(p)
        out.append(_file_preview(f"skills/{name}/{rel.as_posix()}", before, None))
    return out


def preview_install_statusline(target: Target, slug: str) -> list[dict]:
    src_dir = CATALOG_DIR / "statuslines" / slug
    if not src_dir.is_dir():
        return [{"path": slug, "kind": "error", "error": f"catalog statusline not found: {slug}"}]
    src_sh = src_dir / "statusline.sh"
    new_script = src_sh.read_text(encoding="utf-8", errors="replace") if src_sh.is_file() else ""
    old_script = _read_text(target.statusline_path)
    # also a settings patch
    current_settings = claude_fs.read_settings(target)
    new_settings = claude_fs.deep_merge(current_settings, {
        "statusLine": {
            "type": "command",
            "command": str(target.statusline_path),
            "padding": (current_settings.get("statusLine") or {}).get("padding", 1),
        }
    })
    return [
        _file_preview("statusline.sh", old_script, new_script),
        _file_preview(
            target.settings_path.name,
            json.dumps(current_settings, indent=2) if current_settings else None,
            json.dumps(new_settings, indent=2),
        ),
    ]


def preview_patch_settings(target: Target, patch: dict) -> list[dict]:
    current = claude_fs.read_settings(target)
    merged = claude_fs.deep_merge(current, patch or {})
    before = json.dumps(current, indent=2) if current else None
    after = json.dumps(merged, indent=2)
    return [_file_preview(target.settings_path.name, before, after)]


def preview_scaffold_docs(target: Target, kinds: list[str]) -> list[dict]:
    # We don't pre-build the prompt body — just show "new file" with note.
    dest = target.claude_dir / ".nekoclaude-handoff-prompt.md"
    msg = f"(will hold prompts for: {', '.join(kinds) or '(empty)'})"
    before = _read_text(dest) if dest.is_file() else None
    after = msg if before is None else msg
    return [_file_preview(dest.name, before, after)]


def preview_op(op: dict, target: Target) -> list[dict]:
    kind = op.get("kind")
    payload = op.get("payload") or {}
    if kind == "install_skill":
        return preview_install_skill(target, payload.get("slug", ""))
    if kind == "remove_skill":
        return preview_remove_skill(target, payload.get("name", ""))
    if kind == "install_statusline":
        return preview_install_statusline(target, payload.get("slug", ""))
    if kind == "patch_settings":
        return preview_patch_settings(target, payload.get("patch") or {})
    if kind == "scaffold_docs":
        return preview_scaffold_docs(target, payload.get("kinds") or [])
    return [{"path": "?", "kind": "error", "error": f"no preview for op kind {kind!r}"}]
