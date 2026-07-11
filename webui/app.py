"""FastAPI application entry point for the local revenue-kun Web UI.

This is a thin adapter outside `src/revenue_kun/`. It must not call
`revenue_kun.cli.run()`, invoke `src/main.py` via subprocess, or duplicate
any extraction / NOI / Excel-generation logic -- see Issue #78 for the
approved architecture decision.

Scope for this foundation (Issue #79): a root page and a health endpoint
only. CSV/PDF preview, optional-income selection, and Excel generation are
implemented in later issues (#80-#82) and are intentionally absent here.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .config import get_max_upload_mb

_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

app = FastAPI(title="revenue-kun Web UI")
_templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return _templates.TemplateResponse(
        request,
        "index.html",
        {"max_upload_mb": get_max_upload_mb()},
    )


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
