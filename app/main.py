"""FastAPI entrypoint."""
from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import secrets

from .config import ensure_dirs
from .templating import templates
from .deps import session_id
from .routers import (
    targets as targets_router,
    installed as installed_router,
    catalog as catalog_router,
    stage as stage_router,
    apply as apply_router,
    revert as revert_router,
    settings as settings_router,
)
from .services import targets_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_dirs()
    yield


app = FastAPI(title="nekoclaude", lifespan=lifespan)

STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(targets_router.router)
app.include_router(installed_router.router)
app.include_router(catalog_router.router)
app.include_router(stage_router.router)
app.include_router(apply_router.router)
app.include_router(revert_router.router)
app.include_router(settings_router.router)


@app.middleware("http")
async def ensure_session(request: Request, call_next):
    response = await call_next(request)
    new_sid = getattr(request.state, "new_session_id", None)
    if new_sid:
        response.set_cookie("nc_session", new_sid, httponly=True, samesite="lax")
    return response


@app.get("/", response_class=HTMLResponse)
def index(request: Request, sid: str = Depends(session_id)):
    return templates.TemplateResponse(
        request, "base.html",
        {
            "targets": targets_store.list_tracked(),
            "discovered": targets_store.discover(),
        },
    )
