"""Read/write the contents of a .claude/ directory.

This is the ONLY layer (along with snapshot/changelog) that touches real
.claude/ paths. Routers must not bypass it.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any
import json
import shutil

from ..config import Target, GLOBAL_CLAUDE
from .yaml_frontmatter import parse as parse_frontmatter


# -------- read --------

def list_installed_skills(target: Target) -> list[dict]:
    """Skills directly under <target>/skills/<name>/SKILL.md."""
    out: list[dict] = []
    if not target.skills_dir.is_dir():
        return out
    for child in sorted(target.skills_dir.iterdir()):
        skill_md = child / "SKILL.md"
        if not skill_md.is_file():
            continue
        fm = parse_frontmatter(skill_md)
        out.append({
            "name": fm.get("name") or child.name,
            "version": fm.get("version"),
            "description": _flatten_desc(fm.get("description")),
            "path": str(child),
            "source": "user",
        })
    return out


def list_plugin_skills() -> list[dict]:
    """Skills surfaced by installed plugins (read-only for us)."""
    manifest = GLOBAL_CLAUDE / "plugins" / "installed_plugins.json"
    if not manifest.is_file():
        return []
    try:
        data = json.loads(manifest.read_text())
    except json.JSONDecodeError:
        return []
    out: list[dict] = []
    for plugin_id, entries in (data.get("plugins") or {}).items():
        for entry in entries or []:
            install_path = entry.get("installPath")
            if not install_path:
                continue
            skills_dir = Path(install_path) / "skills"
            if not skills_dir.is_dir():
                continue
            for child in sorted(skills_dir.iterdir()):
                skill_md = child / "SKILL.md"
                if not skill_md.is_file():
                    continue
                fm = parse_frontmatter(skill_md)
                out.append({
                    "name": fm.get("name") or child.name,
                    "version": fm.get("version") or entry.get("version"),
                    "description": _flatten_desc(fm.get("description")),
                    "path": str(child),
                    "source": f"plugin:{plugin_id}",
                })
    return out


def read_settings(target: Target) -> dict:
    path = target.settings_path
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {"__parse_error__": True, "__raw__": path.read_text()}


def read_statusline(target: Target) -> dict:
    """Resolve the configured status line script and read a preview."""
    settings = read_settings(target)
    status = settings.get("statusLine") or {}
    cmd = status.get("command") or ""
    expanded = Path(cmd.replace("~", str(GLOBAL_CLAUDE.parent))) if cmd else None
    preview = ""
    if expanded and expanded.is_file():
        try:
            preview = "\n".join(expanded.read_text().splitlines()[:25])
        except OSError:
            preview = ""
    return {
        "configured_command": cmd,
        "resolved_path": str(expanded) if expanded else "",
        "exists": bool(expanded and expanded.is_file()),
        "preview": preview,
    }


def _flatten_desc(d: Any) -> str:
    if d is None:
        return ""
    if isinstance(d, str):
        return d.strip()
    return str(d).strip()


# -------- write --------

def install_skill(target: Target, catalog_skill_dir: Path) -> Path:
    """Copy a catalog skill folder into <target>/skills/<slug>/. Overwrites."""
    target.skills_dir.mkdir(parents=True, exist_ok=True)
    dest = target.skills_dir / catalog_skill_dir.name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(catalog_skill_dir, dest, ignore=shutil.ignore_patterns(".git", "manifest.json"))
    return dest


def remove_skill(target: Target, name: str) -> bool:
    dest = target.skills_dir / name
    if dest.is_dir():
        shutil.rmtree(dest)
        return True
    return False


def write_settings(target: Target, settings: dict) -> None:
    target.claude_dir.mkdir(parents=True, exist_ok=True)
    target.settings_path.write_text(json.dumps(settings, indent=2) + "\n")


def deep_merge(base: dict, patch: dict) -> dict:
    """Recursive dict merge. Lists are replaced, not concatenated."""
    out = dict(base)
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def install_statusline(target: Target, catalog_statusline_dir: Path) -> Path:
    """Copy statusline.sh into the target and patch settings.statusLine.command."""
    target.claude_dir.mkdir(parents=True, exist_ok=True)
    src = catalog_statusline_dir / "statusline.sh"
    dest = target.statusline_path
    shutil.copy2(src, dest)
    dest.chmod(0o755)
    settings = read_settings(target)
    settings = deep_merge(settings, {
        "statusLine": {
            "type": "command",
            "command": str(dest),
            "padding": (settings.get("statusLine") or {}).get("padding", 1),
        }
    })
    write_settings(target, settings)
    return dest
