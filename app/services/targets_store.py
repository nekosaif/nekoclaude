"""Persistent list of tracked project .claude/ directories."""
from __future__ import annotations
from pathlib import Path
import json
import subprocess

from ..config import (
    TARGETS_FILE, STATE_DIR, HOME, GLOBAL_CLAUDE,
    Target, target_for_claude_dir,
)


def _load() -> list[str]:
    if not TARGETS_FILE.is_file():
        return []
    try:
        data = json.loads(TARGETS_FILE.read_text())
        return [str(p) for p in data.get("paths", [])]
    except (json.JSONDecodeError, OSError):
        return []


def _save(paths: list[str]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    TARGETS_FILE.write_text(json.dumps({"paths": sorted(set(paths))}, indent=2) + "\n")


def list_tracked() -> list[Target]:
    out: list[Target] = [target_for_claude_dir(GLOBAL_CLAUDE)]
    for p in _load():
        path = Path(p)
        if path.is_dir():
            out.append(target_for_claude_dir(path))
    return out


def add(claude_dir: str) -> Target:
    path = Path(claude_dir).expanduser().resolve()
    if not path.is_dir():
        raise FileNotFoundError(f".claude directory not found: {path}")
    if path.name != ".claude":
        # be lenient — if user pointed at the project root, descend
        candidate = path / ".claude"
        if candidate.is_dir():
            path = candidate
        else:
            raise ValueError(f"path is not a .claude directory: {path}")
    paths = _load()
    paths.append(str(path))
    _save(paths)
    return target_for_claude_dir(path)


def remove(target_id: str) -> bool:
    paths = _load()
    new_paths = [p for p in paths if target_for_claude_dir(Path(p)).id != target_id]
    if len(new_paths) == len(paths):
        return False
    _save(new_paths)
    return True


def discover() -> list[Target]:
    """find .claude dirs under $HOME (depth-capped) that we don't yet track."""
    tracked = {t.claude_dir for t in list_tracked()}
    out: list[Target] = []
    try:
        result = subprocess.run(
            ["find", str(HOME), "-maxdepth", "4", "-name", ".claude", "-type", "d"],
            capture_output=True, text=True, timeout=10,
        )
    except (subprocess.SubprocessError, OSError):
        return out
    for line in result.stdout.splitlines():
        p = Path(line.strip())
        if not p.is_dir() or p in tracked:
            continue
        out.append(target_for_claude_dir(p))
    return out
