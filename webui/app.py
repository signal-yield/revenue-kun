"""FastAPI application entry point for the local revenue-kun Web UI.

This is a thin adapter outside `src/revenue_kun/`. It must not call
`revenue_kun.cli.run()`, invoke `src/main.py` via subprocess, or duplicate
any extraction / NOI / Excel-generation logic -- see Issue #78 for the
approved architecture decision.

Scope so far:
  - Issue #79: root page and a health endpoint.
  - Issue #80: `POST /api/preview` -- CSV/PDF preview only, no Excel
    generation, no optional-income opt-in UI. Those remain for #81/#82.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from .config import get_max_upload_mb
from .preview import PreviewFailure, process_upload

_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

app = FastAPI(title="revenue-kun Web UI")
_templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))


def _safe_failure_response(status_code: int, error_type: str, message: str, detail_code: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "ok": False,
            "error": {"type": error_type, "message": message, "detail_code": detail_code},
        },
    )


@app.exception_handler(RequestValidationError)
def _on_request_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Keep the ok/false contract even for malformed requests (e.g. no file attached).

    FastAPI's default handler would otherwise return a differently shaped
    `{"detail": [...]}` body, which later Web UI screens (#81) should not
    have to special-case separately from PreviewFailure responses.
    """
    return _safe_failure_response(
        400,
        "invalid_upload",
        "リクエストの形式が正しくありません。ファイルを1件添付してください。",
        "invalid_request",
    )


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


@app.post("/api/preview")
def preview(file: UploadFile = File(...)) -> JSONResponse:
    """Preview one uploaded CSV or text-based PDF rent roll.

    Stateless: nothing from this request is retained afterward. No
    workbook is generated here -- see Issue #82 for `/api/generate`.
    """
    try:
        result = process_upload(file.filename, file.file)
    except PreviewFailure as exc:
        return _safe_failure_response(exc.status_code, exc.error_type, exc.message, exc.detail_code)
    return JSONResponse(content=result)
