from __future__ import annotations
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ..services import claude_fs
from ..deps import get_target


router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/{target_id}", response_class=JSONResponse)
def get_settings(target_id: str):
    target = get_target(target_id)
    return claude_fs.read_settings(target)
