"""In-memory staged-change cart keyed by session id."""
from __future__ import annotations
from typing import Literal, TypedDict
import threading


OpKind = Literal[
    "install_skill",       # payload: {"slug": "<catalog skill slug>"}
    "remove_skill",        # payload: {"name": "<skill folder name>"}
    "install_statusline",  # payload: {"slug": "<catalog statusline slug>"}
    "patch_settings",      # payload: {"patch": {...}}  (deep merge)
    "scaffold_docs",       # payload: {"kinds": ["HANDOFF", ...]}
]


class Op(TypedDict):
    kind: OpKind
    payload: dict
    target_ids: list[str]


_LOCK = threading.Lock()
_CARTS: dict[str, list[Op]] = {}


def get(session_id: str) -> list[Op]:
    with _LOCK:
        return list(_CARTS.get(session_id, []))


def add(session_id: str, op: Op) -> list[Op]:
    with _LOCK:
        cart = _CARTS.setdefault(session_id, [])
        cart.append(op)
        return list(cart)


def remove(session_id: str, idx: int) -> list[Op]:
    with _LOCK:
        cart = _CARTS.get(session_id, [])
        if 0 <= idx < len(cart):
            cart.pop(idx)
        return list(cart)


def clear(session_id: str) -> None:
    with _LOCK:
        _CARTS.pop(session_id, None)
