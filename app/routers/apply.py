from __future__ import annotations
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from ..services import stage as stage_service
from ..services import apply as apply_service
from ..deps import session_id, targets_by_id
from ..templating import templates


router = APIRouter(prefix="/apply", tags=["apply"])


@router.post("", response_class=HTMLResponse)
def apply_now(request: Request, sid: str = Depends(session_id)):
    cart = stage_service.get(sid)
    results = apply_service.apply_all(cart, targets_by_id())
    stage_service.clear(sid)
    return templates.TemplateResponse(
        request, "partials/apply_results.html",
        {"results": results, "targets": targets_by_id()},
    )
