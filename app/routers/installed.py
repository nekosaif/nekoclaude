from __future__ import annotations
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from ..services import claude_fs
from ..deps import get_target
from ..templating import templates


router = APIRouter(prefix="/installed", tags=["installed"])


@router.get("/{target_id}", response_class=HTMLResponse)
def installed_for(request: Request, target_id: str):
    target = get_target(target_id)
    user_skills = claude_fs.list_installed_skills(target)
    plugin_skills = claude_fs.list_plugin_skills() if target.kind == "global" else []
    settings = claude_fs.read_settings(target)
    statusline = claude_fs.read_statusline(target)
    return templates.TemplateResponse(
        request, "partials/installed_panel.html",
        {
            "target": target,
            "user_skills": user_skills,
            "plugin_skills": plugin_skills,
            "settings": settings,
            "statusline": statusline,
        },
    )
