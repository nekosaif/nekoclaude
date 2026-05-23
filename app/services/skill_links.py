"""Persistent registry of skill source URLs the user wants to remember.

This is a *bookmark list*, separate from the catalog itself. A link can be
"installed" (cloned) into the catalog via add_skill_from_git, and remains in
the registry afterwards so the user can re-install on a new machine.
"""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json

from ..config import STATE_DIR


LINKS_FILE = STATE_DIR / "skill_links.json"


def _load() -> list[dict]:
    if not LINKS_FILE.is_file():
        return []
    try:
        data = json.loads(LINKS_FILE.read_text())
    except json.JSONDecodeError:
        return []
    if isinstance(data, dict):
        return list(data.get("links") or [])
    if isinstance(data, list):
        return data
    return []


def _save(links: list[dict]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    LINKS_FILE.write_text(json.dumps({"links": links}, indent=2) + "\n")


def _make_id(url: str, subpath: str) -> str:
    return hashlib.sha1(f"{url}|{subpath}".encode()).hexdigest()[:10]


def list_links() -> list[dict]:
    return _load()


def add(url: str, *, subpath: str = "", name: str = "", description: str = "", suggested_slug: str = "") -> dict:
    url = url.strip()
    subpath = subpath.strip()
    if not url:
        raise ValueError("url is required")
    lid = _make_id(url, subpath)
    links = _load()
    for l in links:
        if l.get("id") == lid:
            # already exists; update non-empty fields
            if name: l["name"] = name
            if description: l["description"] = description
            if suggested_slug: l["suggested_slug"] = suggested_slug
            _save(links)
            return l
    entry = {
        "id": lid,
        "url": url,
        "subpath": subpath,
        "name": name.strip(),
        "description": description.strip(),
        "suggested_slug": suggested_slug.strip(),
        "added_at": datetime.now(timezone.utc).isoformat(),
    }
    links.append(entry)
    _save(links)
    return entry


def get(lid: str) -> dict | None:
    for l in _load():
        if l.get("id") == lid:
            return l
    return None


def remove(lid: str) -> bool:
    links = _load()
    new_links = [l for l in links if l.get("id") != lid]
    if len(new_links) == len(links):
        return False
    _save(new_links)
    return True


def update(lid: str, *, name: str | None = None, description: str | None = None, suggested_slug: str | None = None) -> dict | None:
    links = _load()
    for l in links:
        if l.get("id") == lid:
            if name is not None: l["name"] = name.strip()
            if description is not None: l["description"] = description.strip()
            if suggested_slug is not None: l["suggested_slug"] = suggested_slug.strip()
            _save(links)
            return l
    return None
