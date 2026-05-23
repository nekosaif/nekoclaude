from __future__ import annotations
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Any
import json

from ..services import stage as stage_service
from ..services import preview as preview_service
from ..deps import session_id, targets_by_id
from ..templating import templates


router = APIRouter(prefix="/stage", tags=["stage"])


def _render_cart(request: Request, sid: str) -> HTMLResponse:
    cart = stage_service.get(sid)
    return templates.TemplateResponse(
        request, "partials/cart_panel.html",
        {"cart": cart, "targets": targets_by_id()},
    )


@router.get("", response_class=HTMLResponse)
def get_cart(request: Request, sid: str = Depends(session_id)):
    return _render_cart(request, sid)


@router.post("/add", response_class=HTMLResponse)
async def add_op(request: Request, sid: str = Depends(session_id)):
    form = await request.form()
    kind = form.get("kind")
    target_ids = form.getlist("target_ids")
    if not target_ids:
        raise HTTPException(status_code=400, detail="select at least one target")
    payload_raw = form.get("payload") or "{}"
    try:
        payload = json.loads(payload_raw)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"bad payload json: {e}")
    op = {"kind": kind, "payload": payload, "target_ids": target_ids}
    stage_service.add(sid, op)
    return _render_cart(request, sid)


@router.post("/remove/{idx}", response_class=HTMLResponse)
def remove_op(request: Request, idx: int, sid: str = Depends(session_id)):
    stage_service.remove(sid, idx)
    return _render_cart(request, sid)


@router.post("/clear", response_class=HTMLResponse)
def clear_cart(request: Request, sid: str = Depends(session_id)):
    stage_service.clear(sid)
    return _render_cart(request, sid)


@router.get("/json", response_class=JSONResponse)
def cart_json(sid: str = Depends(session_id)) -> Any:
    return stage_service.get(sid)


@router.get("/diff/{idx}", response_class=HTMLResponse)
def diff_op(request: Request, idx: int, sid: str = Depends(session_id)):
    cart = stage_service.get(sid)
    if idx < 0 or idx >= len(cart):
        raise HTTPException(status_code=404, detail="op not in cart")
    op = cart[idx]
    targets = targets_by_id()
    per_target: list[dict] = []
    for tid in op.get("target_ids") or []:
        target = targets.get(tid)
        if not target:
            per_target.append({"target_id": tid, "label": tid, "files": [], "error": "unknown target"})
            continue
        per_target.append({
            "target_id": tid,
            "label": target.label,
            "files": preview_service.preview_op(op, target),
        })
    return templates.TemplateResponse(
        request, "partials/diff_view.html",
        {"op": op, "idx": idx, "per_target": per_target},
    )
