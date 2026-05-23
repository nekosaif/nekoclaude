"""Read and update the curated catalog under catalog/."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json
import shutil
import subprocess
import tempfile

from ..config import CATALOG_DIR


def _read_manifest(d: Path) -> dict:
    p = d / "manifest.json"
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        return {}


def _write_manifest(d: Path, m: dict) -> None:
    (d / "manifest.json").write_text(json.dumps(m, indent=2) + "\n")


def list_skills() -> list[dict]:
    out: list[dict] = []
    base = CATALOG_DIR / "skills"
    if not base.is_dir():
        return out
    for child in sorted(base.iterdir()):
        if not child.is_dir():
            continue
        m = _read_manifest(child)
        out.append({
            "slug": child.name,
            "name": m.get("name") or child.name,
            "description": m.get("description") or "",
            "source_git": m.get("source_git") or "",
            "source_subpath": m.get("source_subpath") or "",
            "version": m.get("version") or "",
            "sha": m.get("sha") or "",
            "last_updated": m.get("last_updated") or "",
            "path": str(child),
        })
    return out


def list_statuslines() -> list[dict]:
    out: list[dict] = []
    base = CATALOG_DIR / "statuslines"
    if not base.is_dir():
        return out
    for child in sorted(base.iterdir()):
        if not child.is_dir():
            continue
        m = _read_manifest(child)
        out.append({
            "slug": child.name,
            "name": m.get("name") or child.name,
            "description": m.get("description") or "",
            "path": str(child),
        })
    return out


def list_settings_presets() -> list[dict]:
    out: list[dict] = []
    base = CATALOG_DIR / "settings-presets"
    if not base.is_dir():
        return out
    for child in sorted(base.iterdir()):
        if not child.is_dir():
            continue
        m = _read_manifest(child)
        preset_path = child / "settings.partial.json"
        body = {}
        if preset_path.is_file():
            try:
                body = json.loads(preset_path.read_text())
            except json.JSONDecodeError:
                body = {}
        out.append({
            "slug": child.name,
            "name": m.get("name") or child.name,
            "description": m.get("description") or "",
            "body": body,
            "path": str(child),
        })
    return out


def list_doc_prompts() -> list[dict]:
    base = CATALOG_DIR / "doc-prompts"
    if not base.is_dir():
        return []
    out = []
    for p in sorted(base.glob("*.prompt.md")):
        kind = p.name.removesuffix(".prompt.md")
        out.append({"kind": kind, "path": str(p)})
    return out


_KIND_RE = __import__("re").compile(r"^[A-Za-z0-9_-]+$")


def _doc_prompt_path(kind: str) -> Path:
    if not _KIND_RE.match(kind):
        raise ValueError(f"invalid kind {kind!r}: use letters, digits, _ or - only")
    return CATALOG_DIR / "doc-prompts" / f"{kind}.prompt.md"


def read_doc_prompt(kind: str) -> str:
    p = _doc_prompt_path(kind)
    if not p.is_file():
        raise FileNotFoundError(f"doc prompt not found: {kind}")
    return p.read_text(encoding="utf-8")


def write_doc_prompt(kind: str, body: str, *, must_be_new: bool = False) -> Path:
    p = _doc_prompt_path(kind)
    if must_be_new and p.exists():
        raise FileExistsError(f"doc prompt already exists: {kind}")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    return p


def delete_doc_prompt(kind: str) -> bool:
    p = _doc_prompt_path(kind)
    if not p.is_file():
        return False
    p.unlink()
    return True


def get_skill_dir(slug: str) -> Path | None:
    d = CATALOG_DIR / "skills" / slug
    return d if d.is_dir() else None


def get_statusline_dir(slug: str) -> Path | None:
    d = CATALOG_DIR / "statuslines" / slug
    return d if d.is_dir() else None


# -------- update from git --------

class GitUpdateError(RuntimeError):
    pass


def update_skill_from_git(slug: str) -> dict:
    """Refresh catalog/skills/<slug>/ from its manifest's source_git."""
    skill_dir = CATALOG_DIR / "skills" / slug
    if not skill_dir.is_dir():
        raise GitUpdateError(f"unknown skill: {slug}")
    m = _read_manifest(skill_dir)
    source = m.get("source_git")
    subpath = m.get("source_subpath") or ""  # e.g. "skills/foo" if monorepo
    if not source:
        raise GitUpdateError(f"skill {slug} has no source_git in manifest.json")

    with tempfile.TemporaryDirectory(prefix="nekoclaude-clone-") as tmp:
        tmp_path = Path(tmp)
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", source, str(tmp_path / "repo")],
                check=True, capture_output=True, text=True,
            )
        except subprocess.CalledProcessError as e:
            raise GitUpdateError(f"git clone failed: {e.stderr.strip()}") from e

        sha = subprocess.run(
            ["git", "-C", str(tmp_path / "repo"), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()

        src_root = tmp_path / "repo" / subpath if subpath else tmp_path / "repo"
        if not src_root.is_dir():
            raise GitUpdateError(f"subpath {subpath!r} not found in cloned repo")

        # nuke and replace skill body, keeping manifest
        keep = skill_dir / "manifest.json"
        if keep.is_file():
            backup = keep.read_text()
        else:
            backup = None
        for child in list(skill_dir.iterdir()):
            if child.name == "manifest.json":
                continue
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
        # copy new content
        for item in src_root.iterdir():
            if item.name == ".git":
                continue
            dest = skill_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest, ignore=shutil.ignore_patterns(".git"))
            else:
                shutil.copy2(item, dest)

        m["sha"] = sha
        m["last_updated"] = datetime.now(timezone.utc).isoformat()
        _write_manifest(skill_dir, m)
        return m


def write_skill_manifest(slug: str, manifest: dict) -> None:
    skill_dir = CATALOG_DIR / "skills" / slug
    skill_dir.mkdir(parents=True, exist_ok=True)
    _write_manifest(skill_dir, manifest)


def delete_skill(slug: str) -> bool:
    skill_dir = CATALOG_DIR / "skills" / slug
    if not skill_dir.is_dir():
        return False
    shutil.rmtree(skill_dir)
    return True


def read_skill_manifest(slug: str) -> dict:
    skill_dir = CATALOG_DIR / "skills" / slug
    if not skill_dir.is_dir():
        raise FileNotFoundError(f"unknown skill: {slug}")
    return _read_manifest(skill_dir)


def update_skill_manifest(slug: str, fields: dict) -> dict:
    """Merge given fields into the manifest. Cannot change slug."""
    skill_dir = CATALOG_DIR / "skills" / slug
    if not skill_dir.is_dir():
        raise FileNotFoundError(f"unknown skill: {slug}")
    m = _read_manifest(skill_dir)
    for k, v in fields.items():
        if k == "slug":
            continue
        m[k] = v
    _write_manifest(skill_dir, m)
    return m


# -------- statusline CRUD --------

_SLUG_RE = __import__("re").compile(r"^[A-Za-z0-9_-]+$")


def _check_slug(slug: str) -> None:
    if not _SLUG_RE.match(slug):
        raise ValueError(f"invalid slug {slug!r}: use letters, digits, _ or - only")


def read_statusline(slug: str) -> dict:
    d = CATALOG_DIR / "statuslines" / slug
    if not d.is_dir():
        raise FileNotFoundError(f"unknown statusline: {slug}")
    m = _read_manifest(d)
    script = ""
    sh = d / "statusline.sh"
    if sh.is_file():
        script = sh.read_text(encoding="utf-8")
    return {
        "slug": slug,
        "name": m.get("name") or slug,
        "description": m.get("description") or "",
        "script": script,
    }


def write_statusline(
    slug: str, *, name: str, description: str, script: str, must_be_new: bool = False
) -> Path:
    _check_slug(slug)
    d = CATALOG_DIR / "statuslines" / slug
    if must_be_new and d.exists():
        raise FileExistsError(f"statusline already exists: {slug}")
    d.mkdir(parents=True, exist_ok=True)
    _write_manifest(d, {"name": name or slug, "description": description})
    sh = d / "statusline.sh"
    sh.write_text(script, encoding="utf-8")
    sh.chmod(0o755)
    return d


def delete_statusline(slug: str) -> bool:
    d = CATALOG_DIR / "statuslines" / slug
    if not d.is_dir():
        return False
    shutil.rmtree(d)
    return True


# -------- settings preset CRUD --------

def read_preset(slug: str) -> dict:
    d = CATALOG_DIR / "settings-presets" / slug
    if not d.is_dir():
        raise FileNotFoundError(f"unknown preset: {slug}")
    m = _read_manifest(d)
    body = {}
    p = d / "settings.partial.json"
    if p.is_file():
        try:
            body = json.loads(p.read_text())
        except json.JSONDecodeError:
            body = {}
    return {
        "slug": slug,
        "name": m.get("name") or slug,
        "description": m.get("description") or "",
        "body": body,
    }


def write_preset(
    slug: str, *, name: str, description: str, body: dict, must_be_new: bool = False
) -> Path:
    _check_slug(slug)
    if not isinstance(body, dict):
        raise ValueError("preset body must be a JSON object")
    d = CATALOG_DIR / "settings-presets" / slug
    if must_be_new and d.exists():
        raise FileExistsError(f"preset already exists: {slug}")
    d.mkdir(parents=True, exist_ok=True)
    _write_manifest(d, {"name": name or slug, "description": description})
    (d / "settings.partial.json").write_text(json.dumps(body, indent=2) + "\n")
    return d


def delete_preset(slug: str) -> bool:
    d = CATALOG_DIR / "settings-presets" / slug
    if not d.is_dir():
        return False
    shutil.rmtree(d)
    return True


def add_skill_from_git(
    slug: str,
    source_git: str,
    *,
    source_subpath: str = "",
    name: str | None = None,
    description: str = "",
) -> dict:
    """Create a new catalog/skills/<slug>/ by cloning source_git.

    If source_subpath is set, only that subtree of the repo is copied.
    The skill's SKILL.md frontmatter (if present) is parsed for default
    name/description when not provided.
    """
    if "/" in slug or slug.startswith("."):
        raise GitUpdateError(f"invalid slug: {slug!r}")
    skill_dir = CATALOG_DIR / "skills" / slug
    if skill_dir.exists():
        raise GitUpdateError(f"skill {slug} already exists in catalog")
    if not source_git.strip():
        raise GitUpdateError("source_git is required")

    skill_dir.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix="nekoclaude-clone-") as tmp:
            tmp_path = Path(tmp)
            try:
                subprocess.run(
                    ["git", "clone", "--depth", "1", source_git, str(tmp_path / "repo")],
                    check=True, capture_output=True, text=True,
                )
            except subprocess.CalledProcessError as e:
                raise GitUpdateError(f"git clone failed: {e.stderr.strip()}") from e

            sha = subprocess.run(
                ["git", "-C", str(tmp_path / "repo"), "rev-parse", "HEAD"],
                check=True, capture_output=True, text=True,
            ).stdout.strip()

            src_root = tmp_path / "repo" / source_subpath if source_subpath else tmp_path / "repo"
            if not src_root.is_dir():
                raise GitUpdateError(f"subpath {source_subpath!r} not found in cloned repo")

            for item in src_root.iterdir():
                if item.name == ".git":
                    continue
                dest = skill_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, ignore=shutil.ignore_patterns(".git"))
                else:
                    shutil.copy2(item, dest)

            # try to read frontmatter for defaults
            from .yaml_frontmatter import parse as parse_frontmatter
            fm = parse_frontmatter(skill_dir / "SKILL.md")
            inferred_name = fm.get("name")
            inferred_desc = fm.get("description")
            if isinstance(inferred_desc, str):
                inferred_desc = inferred_desc.strip()

            manifest = {
                "name": name or inferred_name or slug,
                "description": description or inferred_desc or "",
                "source_git": source_git,
                "source_subpath": source_subpath,
                "version": fm.get("version") or "",
                "sha": sha,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }
            _write_manifest(skill_dir, manifest)
            return manifest
    except Exception:
        # roll back on any failure so we don't leave a half-cloned dir
        if skill_dir.exists():
            shutil.rmtree(skill_dir, ignore_errors=True)
        raise


# -------- marketplace settings helpers (operate on global settings.json) --------

from ..config import GLOBAL_CLAUDE


def _global_settings_path() -> Path:
    return GLOBAL_CLAUDE / "settings.json"


def list_marketplaces() -> dict:
    p = _global_settings_path()
    if not p.is_file():
        return {}
    try:
        data = json.loads(p.read_text())
    except json.JSONDecodeError:
        return {}
    return data.get("extraKnownMarketplaces") or {}


def marketplace_patch(name: str, source: dict | str) -> dict:
    """Return a settings patch that adds the given marketplace entry."""
    if not name.strip():
        raise ValueError("marketplace name is required")
    return {"extraKnownMarketplaces": {name: source}}
