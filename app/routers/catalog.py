from __future__ import annotations
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse

from ..services import catalog_fs, templates_lib, skill_links
from ..templating import templates


router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("", response_class=HTMLResponse)
def catalog_view(request: Request):
    return templates.TemplateResponse(
        request, "partials/catalog_panel.html",
        {
            "skills": catalog_fs.list_skills(),
            "statuslines": catalog_fs.list_statuslines(),
            "presets": catalog_fs.list_settings_presets(),
            "doc_prompts": catalog_fs.list_doc_prompts(),
        },
    )


@router.get("/json", response_class=JSONResponse)
def catalog_json():
    return {
        "skills": catalog_fs.list_skills(),
        "statuslines": catalog_fs.list_statuslines(),
        "presets": catalog_fs.list_settings_presets(),
        "doc_prompts": catalog_fs.list_doc_prompts(),
    }


@router.post("/skills/{slug}/update", response_class=JSONResponse)
def update_skill(slug: str):
    try:
        m = catalog_fs.update_skill_from_git(slug)
    except catalog_fs.GitUpdateError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "manifest": m}


@router.post("/skills", response_class=HTMLResponse)
def add_skill(
    request: Request,
    slug: str = Form(...),
    source_git: str = Form(...),
    source_subpath: str = Form(""),
    name: str = Form(""),
    description: str = Form(""),
):
    try:
        catalog_fs.add_skill_from_git(
            slug.strip(),
            source_git.strip(),
            source_subpath=source_subpath.strip(),
            name=name.strip() or None,
            description=description.strip(),
        )
    except catalog_fs.GitUpdateError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return templates.TemplateResponse(
        request, "partials/catalog_panel.html",
        {
            "skills": catalog_fs.list_skills(),
            "statuslines": catalog_fs.list_statuslines(),
            "presets": catalog_fs.list_settings_presets(),
            "doc_prompts": catalog_fs.list_doc_prompts(),
            "flash": f"added skill {slug}",
        },
    )


@router.post("/skills/update-all", response_class=HTMLResponse)
def update_all_skills(request: Request):
    """Refresh every catalog skill that has a source_git in its manifest."""
    results: list[dict] = []
    for s in catalog_fs.list_skills():
        if not s.get("source_git"):
            results.append({"slug": s["slug"], "ok": False, "skipped": True,
                            "msg": "no source_git in manifest"})
            continue
        try:
            m = catalog_fs.update_skill_from_git(s["slug"])
            results.append({"slug": s["slug"], "ok": True,
                            "sha": (m.get("sha") or "")[:8]})
        except catalog_fs.GitUpdateError as e:
            results.append({"slug": s["slug"], "ok": False, "msg": str(e)})
    return templates.TemplateResponse(
        request, "partials/skills_update_results.html",
        {"results": results},
    )


@router.delete("/skills/{slug}", response_class=HTMLResponse)
def delete_catalog_skill(request: Request, slug: str):
    ok = catalog_fs.delete_skill(slug)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return templates.TemplateResponse(
        request, "partials/catalog_panel.html",
        {
            "skills": catalog_fs.list_skills(),
            "statuslines": catalog_fs.list_statuslines(),
            "presets": catalog_fs.list_settings_presets(),
            "doc_prompts": catalog_fs.list_doc_prompts(),
            "flash": f"deleted {slug} from catalog",
        },
    )


# -------- skill manifest editor --------

@router.get("/skills/{slug}/edit", response_class=HTMLResponse)
def skill_edit(request: Request, slug: str):
    try:
        m = catalog_fs.read_skill_manifest(slug)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="not found")
    return templates.TemplateResponse(
        request, "partials/skill_editor.html",
        {"slug": slug, "manifest": m},
    )


@router.put("/skills/{slug}/manifest", response_class=HTMLResponse)
def skill_update_manifest(
    request: Request, slug: str,
    name: str = Form(""), description: str = Form(""),
    source_git: str = Form(""), source_subpath: str = Form(""),
):
    try:
        catalog_fs.update_skill_manifest(slug, {
            "name": name.strip(),
            "description": description.strip(),
            "source_git": source_git.strip(),
            "source_subpath": source_subpath.strip(),
        })
    except FileNotFoundError as e:
        return _inline_error(request, str(e))
    return _full_catalog(request, flash=f"saved manifest for {slug}")


# -------- statusline CRUD --------

@router.get("/statuslines/{slug}/edit", response_class=HTMLResponse)
def statusline_edit(request: Request, slug: str):
    try:
        sl = catalog_fs.read_statusline(slug)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="not found")
    return templates.TemplateResponse(
        request, "partials/statusline_editor.html",
        {"slug": slug, "sl": sl, "is_new": False},
    )


@router.get("/statuslines/new", response_class=HTMLResponse)
def statusline_new(request: Request):
    return templates.TemplateResponse(
        request, "partials/statusline_editor.html",
        {"slug": "", "sl": {"name": "", "description": "", "script": "#!/usr/bin/env bash\n"},
         "is_new": True},
    )


@router.post("/statuslines", response_class=HTMLResponse)
def statusline_create(
    request: Request,
    slug: str = Form(...), name: str = Form(""),
    description: str = Form(""), script: str = Form(""),
):
    try:
        catalog_fs.write_statusline(
            slug.strip(), name=name.strip(), description=description.strip(),
            script=script, must_be_new=True,
        )
    except (ValueError, FileExistsError) as e:
        return _inline_error(request, str(e))
    return _full_catalog(request, flash=f"created statusline {slug}")


@router.put("/statuslines/{slug}", response_class=HTMLResponse)
def statusline_update(
    request: Request, slug: str,
    name: str = Form(""), description: str = Form(""), script: str = Form(""),
):
    try:
        catalog_fs.write_statusline(
            slug, name=name.strip(), description=description.strip(),
            script=script,
        )
    except ValueError as e:
        return _inline_error(request, str(e))
    return _full_catalog(request, flash=f"saved statusline {slug}")


@router.delete("/statuslines/{slug}", response_class=HTMLResponse)
def statusline_del(request: Request, slug: str):
    if not catalog_fs.delete_statusline(slug):
        raise HTTPException(status_code=404, detail="not found")
    return _full_catalog(request, flash=f"deleted statusline {slug}")


# -------- settings preset CRUD --------

@router.get("/presets/{slug}/edit", response_class=HTMLResponse)
def preset_edit(request: Request, slug: str):
    try:
        p = catalog_fs.read_preset(slug)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="not found")
    return templates.TemplateResponse(
        request, "partials/preset_editor.html",
        {"slug": slug, "p": p, "is_new": False},
    )


@router.get("/presets/new", response_class=HTMLResponse)
def preset_new(request: Request):
    return templates.TemplateResponse(
        request, "partials/preset_editor.html",
        {"slug": "", "p": {"name": "", "description": "", "body": {}}, "is_new": True},
    )


def _parse_preset_body(body: str) -> tuple[dict | None, str | None]:
    body = (body or "").strip()
    if not body:
        return {}, None
    import json as _json
    try:
        obj = _json.loads(body)
    except _json.JSONDecodeError as e:
        return None, f"settings.partial.json is not valid JSON: {e.msg} (line {e.lineno}, col {e.colno})"
    if not isinstance(obj, dict):
        return None, "settings.partial.json must be a JSON object (got " + type(obj).__name__ + ")"
    return obj, None


def _inline_error(request: Request, msg: str) -> HTMLResponse:
    resp = templates.TemplateResponse(
        request, "partials/inline_error.html", {"error": msg}, status_code=200,
    )
    # Keep the form intact: redirect the response into the editor's error slot.
    resp.headers["HX-Retarget"] = "#editor-error"
    resp.headers["HX-Reswap"] = "innerHTML"
    return resp


@router.post("/presets", response_class=HTMLResponse)
def preset_create(
    request: Request,
    slug: str = Form(...), name: str = Form(""),
    description: str = Form(""), body: str = Form("{}"),
):
    body_obj, err = _parse_preset_body(body)
    if err:
        return _inline_error(request, err)
    try:
        catalog_fs.write_preset(
            slug.strip(), name=name.strip(), description=description.strip(),
            body=body_obj, must_be_new=True,
        )
    except (ValueError, FileExistsError) as e:
        return _inline_error(request, str(e))
    return _full_catalog(request, flash=f"created preset {slug}")


@router.put("/presets/{slug}", response_class=HTMLResponse)
def preset_update(
    request: Request, slug: str,
    name: str = Form(""), description: str = Form(""), body: str = Form("{}"),
):
    body_obj, err = _parse_preset_body(body)
    if err:
        return _inline_error(request, err)
    try:
        catalog_fs.write_preset(
            slug, name=name.strip(), description=description.strip(),
            body=body_obj,
        )
    except ValueError as e:
        return _inline_error(request, str(e))
    return _full_catalog(request, flash=f"saved preset {slug}")


@router.delete("/presets/{slug}", response_class=HTMLResponse)
def preset_del(request: Request, slug: str):
    if not catalog_fs.delete_preset(slug):
        raise HTTPException(status_code=404, detail="not found")
    return _full_catalog(request, flash=f"deleted preset {slug}")


def _full_catalog(request: Request, flash: str | None = None) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "partials/catalog_panel.html",
        {
            "skills": catalog_fs.list_skills(),
            "statuslines": catalog_fs.list_statuslines(),
            "presets": catalog_fs.list_settings_presets(),
            "doc_prompts": catalog_fs.list_doc_prompts(),
            "flash": flash,
        },
    )


# -------- skill links registry --------

@router.get("/skill-links", response_class=HTMLResponse)
def skill_links_view(request: Request):
    existing_sources = {s.get("source_git") for s in catalog_fs.list_skills() if s.get("source_git")}
    links = skill_links.list_links()
    return templates.TemplateResponse(
        request, "partials/skill_links_panel.html",
        {"links": links, "in_catalog": existing_sources},
    )


@router.post("/skill-links", response_class=HTMLResponse)
def skill_links_add(
    request: Request,
    url: str = Form(""), subpath: str = Form(""),
    name: str = Form(""), description: str = Form(""), suggested_slug: str = Form(""),
):
    try:
        skill_links.add(url, subpath=subpath, name=name, description=description,
                        suggested_slug=suggested_slug)
    except ValueError as e:
        return _inline_error(request, str(e))
    return skill_links_view(request)


@router.delete("/skill-links/{lid}", response_class=HTMLResponse)
def skill_links_remove(request: Request, lid: str):
    if not skill_links.remove(lid):
        raise HTTPException(status_code=404, detail="link not found")
    return skill_links_view(request)


@router.post("/skill-links/{lid}/install", response_class=HTMLResponse)
def skill_links_install(request: Request, lid: str, slug: str = Form("")):
    """Clone the link into the catalog. Uses suggested_slug or the form-provided slug."""
    link = skill_links.get(lid)
    if not link:
        raise HTTPException(status_code=404, detail="link not found")
    final_slug = (slug or link.get("suggested_slug") or "").strip()
    if not final_slug:
        return _inline_error(request, "slug is required (either as form field or as suggested_slug on the link)")
    try:
        catalog_fs.add_skill_from_git(
            final_slug,
            link["url"],
            source_subpath=link.get("subpath") or "",
            name=link.get("name") or None,
            description=link.get("description") or "",
        )
    except catalog_fs.GitUpdateError as e:
        return _inline_error(request, str(e))
    return _full_catalog(request, flash=f"installed {final_slug} from link")


# -------- predesigned template library --------

@router.get("/presets/templates", response_class=HTMLResponse)
def preset_templates_view(request: Request):
    return templates.TemplateResponse(
        request, "partials/preset_templates.html",
        {"items": templates_lib.list_settings_templates(),
         "existing_slugs": {p["slug"] for p in catalog_fs.list_settings_presets()}},
    )


@router.post("/presets/from-template/{tid}", response_class=HTMLResponse)
def preset_from_template(request: Request, tid: str):
    t = templates_lib.get_settings_template(tid)
    if not t:
        raise HTTPException(status_code=404, detail="unknown template")
    try:
        catalog_fs.write_preset(
            t["id"], name=t["name"], description=t["description"],
            body=t["body"], must_be_new=True,
        )
    except FileExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _full_catalog(request, flash=f"added preset {t['id']} from template")


@router.get("/presets/templates/{tid}/copy", response_class=HTMLResponse)
def preset_template_copy(request: Request, tid: str):
    t = templates_lib.get_settings_template(tid)
    if not t:
        raise HTTPException(status_code=404, detail="unknown template")
    return templates.TemplateResponse(
        request, "partials/preset_editor.html",
        {"slug": "", "p": {"name": t["name"], "description": t["description"], "body": t["body"]},
         "is_new": True, "template_id": tid},
    )


@router.get("/doc-prompts/templates", response_class=HTMLResponse)
def doc_templates_view(request: Request):
    existing = {d["kind"] for d in catalog_fs.list_doc_prompts()}
    return templates.TemplateResponse(
        request, "partials/doc_templates.html",
        {"items": templates_lib.list_doc_templates(), "existing": existing},
    )


@router.post("/doc-prompts/from-template/{tid}", response_class=HTMLResponse)
def doc_from_template(request: Request, tid: str):
    t = templates_lib.get_doc_template(tid)
    if not t:
        raise HTTPException(status_code=404, detail="unknown template")
    try:
        catalog_fs.write_doc_prompt(t["id"], t["body"], must_be_new=True)
    except (ValueError, FileExistsError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    return templates.TemplateResponse(
        request, "partials/doc_prompts_manage.html",
        {"doc_prompts": catalog_fs.list_doc_prompts(), "flash": f"added {t['id']} from template"},
    )


@router.get("/doc-prompts/templates/{tid}/copy", response_class=HTMLResponse)
def doc_template_copy(request: Request, tid: str):
    t = templates_lib.get_doc_template(tid)
    if not t:
        raise HTTPException(status_code=404, detail="unknown template")
    return templates.TemplateResponse(
        request, "partials/doc_prompt_editor.html",
        {"kind": "", "body": t["body"], "is_new": True, "template_id": tid},
    )


# -------- marketplaces --------

@router.get("/marketplaces", response_class=HTMLResponse)
def marketplaces_view(request: Request):
    return templates.TemplateResponse(
        request, "partials/marketplaces_panel.html",
        {"marketplaces": catalog_fs.list_marketplaces()},
    )


@router.get("/marketplaces/json", response_class=JSONResponse)
def marketplaces_json():
    return catalog_fs.list_marketplaces()


# -------- doc-prompt CRUD --------

@router.get("/doc-prompts", response_class=HTMLResponse)
def doc_prompts_view(request: Request):
    """List + manage UI."""
    return templates.TemplateResponse(
        request, "partials/doc_prompts_manage.html",
        {"doc_prompts": catalog_fs.list_doc_prompts()},
    )


@router.get("/doc-prompts/{kind}/raw", response_class=PlainTextResponse)
def doc_prompt_raw(kind: str):
    try:
        return catalog_fs.read_doc_prompt(kind)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/doc-prompts/{kind}/edit", response_class=HTMLResponse)
def doc_prompt_edit(request: Request, kind: str):
    try:
        body = catalog_fs.read_doc_prompt(kind)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return templates.TemplateResponse(
        request, "partials/doc_prompt_editor.html",
        {"kind": kind, "body": body, "is_new": False},
    )


@router.get("/doc-prompts/new", response_class=HTMLResponse)
def doc_prompt_new(request: Request):
    return templates.TemplateResponse(
        request, "partials/doc_prompt_editor.html",
        {"kind": "", "body": "", "is_new": True},
    )


@router.post("/doc-prompts", response_class=HTMLResponse)
def doc_prompt_create(request: Request, kind: str = Form(...), body: str = Form("")):
    try:
        catalog_fs.write_doc_prompt(kind, body, must_be_new=True)
    except (ValueError, FileExistsError) as e:
        return _inline_error(request, str(e))
    return templates.TemplateResponse(
        request, "partials/doc_prompts_manage.html",
        {"doc_prompts": catalog_fs.list_doc_prompts(), "flash": f"created {kind}"},
    )


@router.put("/doc-prompts/{kind}", response_class=HTMLResponse)
def doc_prompt_update(request: Request, kind: str, body: str = Form("")):
    try:
        catalog_fs.write_doc_prompt(kind, body)
    except ValueError as e:
        return _inline_error(request, str(e))
    return templates.TemplateResponse(
        request, "partials/doc_prompts_manage.html",
        {"doc_prompts": catalog_fs.list_doc_prompts(), "flash": f"saved {kind}"},
    )


@router.delete("/doc-prompts/{kind}", response_class=HTMLResponse)
def doc_prompt_delete(request: Request, kind: str):
    try:
        ok = catalog_fs.delete_doc_prompt(kind)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return templates.TemplateResponse(
        request, "partials/doc_prompts_manage.html",
        {"doc_prompts": catalog_fs.list_doc_prompts(), "flash": f"deleted {kind}"},
    )
