"""Stateless rent-roll preview logic for ``POST /api/preview``.

This module is a thin adapter: it validates the upload, writes it to a
request-specific temporary path (see ``webui.upload``), and calls the
existing ``revenue_kun`` extraction / missing-information functions
directly. It does not call ``revenue_kun.cli.run()``, invoke
``src/main.py`` via subprocess, or duplicate any PDF/CSV parsing or
missing-detection logic -- see Issue #78 for the approved architecture
decision and Issue #80 for this endpoint's scope.

No Excel workbook is generated here; that is out of scope for this
endpoint (see Issue #82).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, BinaryIO

# Make `revenue_kun` importable when this package is run directly (e.g.
# `uvicorn webui.app:app` from the repo root), the same way
# `src/main.py` bootstraps its own import path for the CLI. Under pytest,
# pyproject.toml's `pythonpath = ["src"]` already covers this, so this is
# a no-op there.
_SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from revenue_kun.config import load_assumptions, validate_assumptions
from revenue_kun.missing import MissingItem, detect_missing
from revenue_kun.pdf_extract import RentRollExtractionError, extract_rent_roll_from_pdf
from revenue_kun.rent_roll import RentRollUnit, load_rent_roll

from .config import get_max_upload_bytes
from .upload import (
    UploadTooLargeError,
    UploadValidationError,
    generate_temp_filename,
    request_temp_dir,
    validate_extension,
    write_limited,
)

# Same default assumptions file the CLI uses (see revenue_kun.cli.build_parser).
# The Web UI does not yet accept user-supplied assumptions (see Issue #78);
# this keeps missing-information detection consistent with the existing CLI.
_DEFAULT_ASSUMPTIONS_PATH = Path(__file__).resolve().parents[1] / "assumptions.sample.yaml"

_PDF_SIGNATURE = b"%PDF-"

_OPTIONAL_INCOME_KEYS: tuple[tuple[str, str], ...] = (
    ("water_income", "water"),
    ("parking_income", "parking"),
    ("other_income", "other_income"),
)


class PreviewFailure(Exception):
    """A handled, user-facing preview failure.

    Carries everything needed to render the safe-failure JSON contract:
    no traceback, no filesystem path, no original filename.
    """

    def __init__(
        self,
        error_type: str,
        message: str,
        detail_code: str,
        status_code: int = 400,
    ) -> None:
        super().__init__(message)
        self.error_type = error_type
        self.message = message
        self.detail_code = detail_code
        self.status_code = status_code


def _status_bucket(unit: RentRollUnit) -> str:
    if unit.is_occupied:
        return "occupied"
    status = (unit.稼働状況 or "").strip()
    if any(token in status for token in ("空室", "空き", "募集")):
        return "vacant"
    return "unknown"


def _unit_to_row(unit: RentRollUnit) -> dict[str, Any]:
    return {
        "room": unit.区画,
        "status": _status_bucket(unit),
        "rent": unit.月額賃料_円,
        "common_fee": unit.月額共益費_円,
        "water_income": unit.get_optional_income("water"),
        "parking_income": unit.get_optional_income("parking"),
        "other_income": unit.get_optional_income("other_income"),
    }


def _missing_to_dict(item: MissingItem) -> dict[str, Any]:
    return {
        "field": item.field,
        "message": item.impact,
        "severity": "error" if item.required else "warning",
    }


def _optional_income_summary(units: list[RentRollUnit], canonical_key: str) -> dict[str, Any]:
    """Monthly/annual totals for one optional-income category.

    v0.5.2: optional income is always auto-included in GPI (no opt-in/out
    selection), so this summary also reports that inclusion explicitly —
    see ``gpi_included`` below.
    """
    values = [unit.get_optional_income(canonical_key) for unit in units]
    present = any(value is not None for value in values)
    monthly_total = sum(value for value in values if value is not None)
    return {
        "present": present,
        "monthly_total": monthly_total,
        "annual_total": monthly_total * 12,
        "gpi_included": True,
    }


def _annual_income_total(units: list[RentRollUnit], monthly_values_fn) -> float:
    """Sum monthly_values_fn(unit) over units (None treated as 0), ×12."""
    monthly_total = sum(
        value for value in (monthly_values_fn(u) for u in units) if value is not None
    )
    return monthly_total * 12


def _compute_gpi_annual(units: list[RentRollUnit]) -> float:
    """Total annual GPI: rent + common fee + water + parking + other income.

    Mirrors the direct_cap.xlsx income block exactly (賃料+共益費+水道代収入+
    駐車場収入+その他収入, all auto-included, missing values treated as 0).
    """
    return (
        _annual_income_total(units, lambda u: u.月額賃料_円)
        + _annual_income_total(units, lambda u: u.月額共益費_円)
        + _annual_income_total(units, lambda u: u.get_optional_income("water"))
        + _annual_income_total(units, lambda u: u.get_optional_income("parking"))
        + _annual_income_total(units, lambda u: u.get_optional_income("other_income"))
    )


def build_preview(
    units: list[RentRollUnit],
    missing: list[MissingItem],
    input_type: str,
) -> dict[str, Any]:
    """Assemble the JSON-serializable preview payload.

    Only plain str/int/float/bool/None/list/dict values are used, so this
    is safe to pass directly to a JSON response -- no dataclass or Python
    object is dumped as-is.
    """
    occupied = sum(1 for u in units if _status_bucket(u) == "occupied")
    vacant = sum(1 for u in units if _status_bucket(u) == "vacant")
    unknown = len(units) - occupied - vacant

    return {
        "ok": True,
        "input_type": input_type,
        "unit_count": len(units),
        "status_summary": {"occupied": occupied, "vacant": vacant, "unknown": unknown},
        "rows": [_unit_to_row(u) for u in units],
        "missing": [_missing_to_dict(m) for m in missing],
        "optional_income": {
            response_key: _optional_income_summary(units, canonical_key)
            for response_key, canonical_key in _OPTIONAL_INCOME_KEYS
        },
        "gpi_annual": _compute_gpi_annual(units),
        "diagnostics": {"source": input_type},
    }


def extract_units_from_upload(
    client_filename: str | None, source: BinaryIO
) -> tuple[list[RentRollUnit], str]:
    """Validate, persist, and extract rent-roll units from one upload.

    Shared by the preview endpoint (``/api/preview``) and the workbook
    generation endpoint (``/api/generate``, see ``webui.generate``) so the
    upload-validation and extraction-failure mapping is defined exactly
    once. ``client_filename`` is used only to read its extension; it is
    never written to a temporary path, included in a response, or written
    to logs. ``source`` must expose a synchronous ``.read(n)`` (e.g.
    FastAPI's ``UploadFile.file``).

    Raises ``PreviewFailure`` for any handled validation or extraction
    failure. The request-specific temporary directory used to hold the
    upload is always removed before this function returns or raises.

    Returns ``(units, input_type)`` where ``input_type`` is ``"csv"`` or
    ``"pdf"``.
    """
    try:
        extension = validate_extension(client_filename)
    except UploadValidationError as exc:
        raise PreviewFailure("invalid_upload", str(exc), "unsupported_extension", 400) from exc

    with request_temp_dir() as temp_dir:
        temp_path = temp_dir / generate_temp_filename(extension)
        try:
            write_limited(source, temp_path, max_bytes=get_max_upload_bytes())
        except UploadTooLargeError as exc:
            raise PreviewFailure("invalid_upload", str(exc), "upload_too_large", 400) from exc

        if extension == ".pdf":
            input_type = "pdf"
            with temp_path.open("rb") as f:
                signature = f.read(len(_PDF_SIGNATURE))
            if signature != _PDF_SIGNATURE:
                raise PreviewFailure(
                    "invalid_upload",
                    "有効なPDFファイルではありません。",
                    "invalid_pdf_signature",
                    400,
                )
            try:
                units, _report = extract_rent_roll_from_pdf(temp_path)
            except RentRollExtractionError as exc:
                raise PreviewFailure(
                    "extraction_failed",
                    exc.report.failure_reason if exc.report else str(exc),
                    "rent_roll_table_not_found",
                    422,
                ) from exc
            except Exception as exc:  # any other pdfplumber/pdfminer failure
                raise PreviewFailure(
                    "extraction_failed",
                    "PDFを解析できませんでした。ファイルが破損している可能性があります。",
                    "pdf_parse_error",
                    422,
                ) from exc
        else:
            input_type = "csv"
            try:
                units = load_rent_roll(temp_path)
            except Exception as exc:  # bad encoding, malformed numeric cells, etc.
                raise PreviewFailure(
                    "extraction_failed",
                    "CSVを読み取れませんでした。文字コードや形式を確認してください。",
                    "csv_unreadable",
                    422,
                ) from exc

    return units, input_type


def process_upload(client_filename: str | None, source: BinaryIO) -> dict[str, Any]:
    """Validate, extract, and build a preview response for one upload.

    See ``extract_units_from_upload`` for the shared validation/extraction
    behaviour and its failure contract.
    """
    units, input_type = extract_units_from_upload(client_filename, source)

    assumptions = load_assumptions(_DEFAULT_ASSUMPTIONS_PATH)
    validate_assumptions(assumptions)
    missing = detect_missing(assumptions, units, rent_roll_source=input_type)

    return build_preview(units, missing, input_type)
