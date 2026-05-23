"""Shared Jinja2 templates instance."""
from __future__ import annotations
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json

TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _to_pretty_json(value) -> str:
    try:
        return json.dumps(value, indent=2, sort_keys=False)
    except (TypeError, ValueError):
        return str(value)


templates.env.filters["pretty_json"] = _to_pretty_json
