"""Snapshot only the subtrees that an apply will mutate."""
from __future__ import annotations
from pathlib import Path
import shutil

from ..config import LOGS_DIR, Target


def snapshot_root_for(target: Target, change_id: str) -> Path:
    return LOGS_DIR / target.id / "snapshots" / change_id


def snapshot_path(target: Target, change_id: str, abs_path: Path) -> Path:
    """Snapshot a single file or directory under <abs_path> if it exists.

    The snapshot path mirrors the relative location under the target's claude_dir.
    Returns the snapshot path (even if source did not exist; caller may want to
    record a tombstone marker).
    """
    root = snapshot_root_for(target, change_id)
    try:
        rel = abs_path.resolve().relative_to(target.claude_dir.resolve())
    except ValueError:
        # outside the target's .claude/ — snapshot under absolute marker
        rel = Path("__abs__") / abs_path.as_posix().lstrip("/")
    dest = root / rel
    dest.parent.mkdir(parents=True, exist_ok=True)

    if abs_path.is_dir():
        shutil.copytree(abs_path, dest, dirs_exist_ok=True)
    elif abs_path.is_file():
        shutil.copy2(abs_path, dest)
    else:
        # tombstone: record absence so revert can delete
        (dest.parent / (dest.name + ".__absent__")).write_text("")
    return dest


def restore(target: Target, change_id: str) -> list[str]:
    """Restore snapshot files back into the target. Returns paths touched."""
    root = snapshot_root_for(target, change_id)
    if not root.is_dir():
        return []
    touched: list[str] = []
    for src in root.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(root)
        if rel.parts and rel.parts[0] == "__abs__":
            # outside-claude_dir entries — rebuild absolute path
            abs_target = Path("/") / Path(*rel.parts[1:])
        else:
            abs_target = target.claude_dir / rel

        if src.name.endswith(".__absent__"):
            real_target = abs_target.parent / src.name.removesuffix(".__absent__")
            if real_target.is_dir():
                shutil.rmtree(real_target)
            elif real_target.is_file():
                real_target.unlink()
            touched.append(str(real_target))
            continue

        abs_target.parent.mkdir(parents=True, exist_ok=True)
        if abs_target.is_dir():
            shutil.rmtree(abs_target)
        shutil.copy2(src, abs_target)
        touched.append(str(abs_target))
    return touched
