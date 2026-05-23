from __future__ import annotations
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

from ..services import changelog, apply as apply_service
from ..deps import get_target
from ..templating import templates


router = APIRouter(prefix="/history", tags=["history"])


@router.get("/{target_id}", response_class=HTMLResponse)
def history_view(request: Request, target_id: str):
    target = get_target(target_id)
    entries = list(reversed(changelog.read_history(target)))
    return templates.TemplateResponse(
        request, "partials/history_panel.html",
        {"target": target, "entries": entries},
    )


@router.get("/{target_id}/json", response_class=JSONResponse)
def history_json(target_id: str):
    target = get_target(target_id)
    return changelog.read_history(target)


@router.post("/{target_id}/revert/{change_id}", response_class=HTMLResponse)
def revert(request: Request, target_id: str, change_id: str):
    target = get_target(target_id)
    result = apply_service.revert_change(target, change_id)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("error") or "revert failed")
    entries = list(reversed(changelog.read_history(target)))
    return templates.TemplateResponse(
        request, "partials/history_panel.html",
        {"target": target, "entries": entries, "just_reverted": change_id},
    )
