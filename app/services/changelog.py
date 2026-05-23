"""Per-target append-only JSONL change log."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json
import uuid

from ..config import LOGS_DIR, Target


def history_path(target: Target) -> Path:
    return LOGS_DIR / target.id / "history.jsonl"


def new_change_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]


def append(target: Target, entry: dict) -> None:
    p = history_path(target)
    p.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(entry, sort_keys=True)
    with p.open("a") as f:
        f.write(line + "\n")


def read_history(target: Target) -> list[dict]:
    p = history_path(target)
    if not p.is_file():
        return []
    out: list[dict] = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def find_entry(target: Target, change_id: str) -> dict | None:
    for e in read_history(target):
        if e.get("change_id") == change_id:
            return e
    return None
