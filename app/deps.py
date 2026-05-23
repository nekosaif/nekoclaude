"""Shared dependencies: target lookup, session id."""
from __future__ import annotations
from fastapi import Request, HTTPException
import secrets

from .services import targets_store
from .config import Target


def session_id(request: Request) -> str:
    sid = request.cookies.get("nc_session")
    if not sid:
        sid = secrets.token_urlsafe(16)
        request.state.new_session_id = sid
    return sid


def targets_by_id() -> dict[str, Target]:
    return {t.id: t for t in targets_store.list_tracked()}


def get_target(target_id: str) -> Target:
    t = targets_by_id().get(target_id)
    if not t:
        raise HTTPException(status_code=404, detail=f"unknown target: {target_id}")
    return t
