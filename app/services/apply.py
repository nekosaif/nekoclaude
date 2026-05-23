"""The central mutate step: snapshot → write → log."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import shutil

from ..config import Target, CATALOG_DIR
from . import claude_fs, snapshot, changelog
from .stage import Op


def _summarize_op(op: Op) -> str:
    kind = op["kind"]
    p = op["payload"]
    if kind == "install_skill":
        return f"install skill {p.get('slug')}"
    if kind == "remove_skill":
        return f"remove skill {p.get('name')}"
    if kind == "install_statusline":
        return f"install statusline {p.get('slug')}"
    if kind == "patch_settings":
        keys = list((p.get("patch") or {}).keys())
        return f"patch settings: {', '.join(keys) or '(empty)'}"
    if kind == "scaffold_docs":
        return f"scaffold docs: {', '.join(p.get('kinds', []))}"
    return kind


def _paths_touched_by(op: Op, target: Target) -> list[Path]:
    kind = op["kind"]
    p = op["payload"]
    if kind == "install_skill":
        return [target.skills_dir / p["slug"]]
    if kind == "remove_skill":
        return [target.skills_dir / p["name"]]
    if kind == "install_statusline":
        return [target.statusline_path, target.settings_path]
    if kind == "patch_settings":
        return [target.settings_path]
    if kind == "scaffold_docs":
        # handoff drops a prompt file into <target>/.nekoclaude-handoff-prompt.md
        return [target.claude_dir / ".nekoclaude-handoff-prompt.md"]
    return []


def _do_op(op: Op, target: Target) -> dict:
    kind = op["kind"]
    p = op["payload"]
    if kind == "install_skill":
        src = CATALOG_DIR / "skills" / p["slug"]
        if not src.is_dir():
            return {"ok": False, "error": f"unknown catalog skill: {p['slug']}"}
        dest = claude_fs.install_skill(target, src)
        return {"ok": True, "path": str(dest)}
    if kind == "remove_skill":
        ok = claude_fs.remove_skill(target, p["name"])
        return {"ok": ok}
    if kind == "install_statusline":
        src = CATALOG_DIR / "statuslines" / p["slug"]
        if not src.is_dir():
            return {"ok": False, "error": f"unknown catalog statusline: {p['slug']}"}
        dest = claude_fs.install_statusline(target, src)
        return {"ok": True, "path": str(dest)}
    if kind == "patch_settings":
        current = claude_fs.read_settings(target)
        merged = claude_fs.deep_merge(current, p.get("patch") or {})
        claude_fs.write_settings(target, merged)
        return {"ok": True}
    if kind == "scaffold_docs":
        # delegated to a dedicated helper to keep this file slim
        from . import handoff_prompt
        prompt_path = handoff_prompt.write_prompt(target, p.get("kinds", []))
        return {"ok": True, "prompt_path": str(prompt_path)}
    return {"ok": False, "error": f"unknown op: {kind}"}


def apply_all(ops: list[Op], targets_by_id: dict[str, Target]) -> list[dict]:
    """Returns per-target apply results."""
    # Group ops by target so each target gets one snapshot + one history line.
    by_target: dict[str, list[Op]] = {}
    for op in ops:
        for tid in op.get("target_ids") or []:
            by_target.setdefault(tid, []).append(op)

    results: list[dict] = []
    for tid, target_ops in by_target.items():
        target = targets_by_id.get(tid)
        if not target:
            results.append({"target_id": tid, "ok": False, "error": "unknown target"})
            continue

        change_id = changelog.new_change_id()
        # snapshot every touched path before any write
        touched_paths: list[Path] = []
        for op in target_ops:
            touched_paths.extend(_paths_touched_by(op, target))
        for path in touched_paths:
            snapshot.snapshot_path(target, change_id, path)

        op_results: list[dict] = []
        for op in target_ops:
            op_results.append({"op": op, "summary": _summarize_op(op), **_do_op(op, target)})

        entry = {
            "change_id": change_id,
            "ts": datetime.now(timezone.utc).isoformat(),
            "kind": "apply",
            "summary": "; ".join(_summarize_op(o) for o in target_ops),
            "ops": op_results,
        }
        changelog.append(target, entry)
        results.append({"target_id": tid, "ok": True, "change_id": change_id, "entry": entry})
    return results


def revert_change(target: Target, change_id: str) -> dict:
    entry = changelog.find_entry(target, change_id)
    if not entry:
        return {"ok": False, "error": "change not found"}
    # before restoring, snapshot CURRENT state of those paths under a new change_id
    touched_paths: list[Path] = []
    for op_result in entry.get("ops") or []:
        op = op_result.get("op") or {}
        touched_paths.extend(_paths_touched_by(op, target))

    revert_change_id = changelog.new_change_id()
    for path in touched_paths:
        snapshot.snapshot_path(target, revert_change_id, path)

    restored = snapshot.restore(target, change_id)

    new_entry = {
        "change_id": revert_change_id,
        "ts": datetime.now(timezone.utc).isoformat(),
        "kind": "revert",
        "reverted_change_id": change_id,
        "summary": f"revert {change_id}",
        "restored": restored,
    }
    changelog.append(target, new_entry)
    return {"ok": True, "change_id": revert_change_id, "entry": new_entry}
