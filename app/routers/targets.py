from __future__ import annotations
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse

from ..services import targets_store
from ..templating import templates


router = APIRouter(prefix="/targets", tags=["targets"])


@router.get("", response_class=JSONResponse)
def list_targets():
    return [
        {"id": t.id, "label": t.label, "claude_dir": str(t.claude_dir), "kind": t.kind}
        for t in targets_store.list_tracked()
    ]


@router.get("/discover", response_class=JSONResponse)
def discover():
    return [
        {"id": t.id, "label": t.label, "claude_dir": str(t.claude_dir), "kind": t.kind}
        for t in targets_store.discover()
    ]


@router.post("/add", response_class=HTMLResponse)
def add_target(request: Request, path: str = Form(...)):
    try:
        t = targets_store.add(path)
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    return templates.TemplateResponse(
        request, "partials/target_list.html",
        {"targets": targets_store.list_tracked(), "added": t.id},
    )


@router.post("/remove/{target_id}", response_class=HTMLResponse)
def remove_target(request: Request, target_id: str):
    ok = targets_store.remove(target_id)
    if not ok:
        raise HTTPException(status_code=404, detail="target not found or is global")
    return templates.TemplateResponse(
        request, "partials/target_list.html",
        {"targets": targets_store.list_tracked()},
    )
