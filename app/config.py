"""Path constants and target resolution."""
from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
import os


REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOG_DIR = REPO_ROOT / "catalog"
LOGS_DIR = REPO_ROOT / "logs"
STATE_DIR = REPO_ROOT / "state"
TARGETS_FILE = STATE_DIR / "targets.json"
SESSION_FILE = STATE_DIR / "session.json"

HOME = Path(os.path.expanduser("~"))
GLOBAL_CLAUDE = HOME / ".claude"


@dataclass(frozen=True)
class Target:
    """A .claude/ directory we manage: global or a project's."""
    id: str            # slug used as a logs/ subdir
    label: str         # human-friendly
    claude_dir: Path   # the .claude/ path itself
    kind: str          # "global" | "project"

    @property
    def settings_path(self) -> Path:
        # global uses settings.json; project uses settings.local.json
        if self.kind == "global":
            return self.claude_dir / "settings.json"
        return self.claude_dir / "settings.local.json"

    @property
    def skills_dir(self) -> Path:
        return self.claude_dir / "skills"

    @property
    def statusline_path(self) -> Path:
        return self.claude_dir / "statusline.sh"


def slugify_path(p: Path) -> str:
    """Deterministic slug for a .claude/ path. Global is special-cased."""
    p = p.resolve()
    if p == GLOBAL_CLAUDE:
        return "global"
    parent = p.parent
    return parent.as_posix().lstrip("/").replace("/", "_") or "root"


def target_for_claude_dir(claude_dir: Path) -> Target:
    claude_dir = claude_dir.resolve()
    if claude_dir == GLOBAL_CLAUDE:
        return Target(id="global", label="~/.claude (global)", claude_dir=claude_dir, kind="global")
    return Target(
        id=slugify_path(claude_dir),
        label=str(claude_dir.parent),
        claude_dir=claude_dir,
        kind="project",
    )


def ensure_dirs() -> None:
    for d in (CATALOG_DIR, LOGS_DIR, STATE_DIR,
              CATALOG_DIR / "skills",
              CATALOG_DIR / "statuslines",
              CATALOG_DIR / "settings-presets",
              CATALOG_DIR / "doc-prompts"):
        d.mkdir(parents=True, exist_ok=True)
