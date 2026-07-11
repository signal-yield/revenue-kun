"""Stateless workbook generation logic for ``POST /api/generate`` (Issue #82).

This module is a thin adapter: it reuses ``webui.preview.extract_units_from_upload``
for validation/extraction (no PDF/CSV parsing logic is duplicated here),
maps the browser's explicit optional-income selections onto the existing
``revenue_kun.config.OptionalIncomeConfig``, and calls the existing
``revenue_kun.excel_output.write_direct_cap_workbook`` directly. It does not
call ``revenue_kun.cli.run()``, invoke ``src/main.py`` via subprocess, or
generate any Excel formula itself -- see Issue #78 for the approved
architecture decision.

No output is written under ``output/``, and no ``missing_info.md`` /
``extraction_log.json`` is produced -- this endpoint returns only the
``直接還元法_OER`` / ``直接還元法‗費用詳細版`` / ``読み取りレントロール``
workbook (``direct_cap.xlsx``) as in-memory bytes.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import BinaryIO

# Make `revenue_kun` importable when this module is loaded first (e.g. if
# a future entry point imports webui.generate before webui.preview), the
# same way `src/main.py` and `webui/preview.py` bootstrap this import
# path. Under pytest, pyproject.toml's `pythonpath = ["src"]` already
# covers this, so this is a no-op there.
_SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from revenue_kun.config import OptionalIncomeConfig
from revenue_kun.excel_output import DirectCapRow, write_direct_cap_workbook

from .preview import PreviewFailure, extract_units_from_upload
from .upload import generate_temp_filename, request_temp_dir

# Canonical keys accepted by revenue_kun.config.OPTIONAL_INCOME_CANONICAL_KEYS.
_CANONICAL_OPTIONAL_INCOME_KEYS = frozenset({"water", "parking", "other_income"})

# The browser sends whichever string is in each checkbox's
# `data-optional-income-key` attribute (see webui/static/app.js), which is
# the same response-shaped key used in the preview JSON
# (water_income/parking_income/other_income). Accept both that shape and
# the canonical revenue_kun key for robustness.
_UI_KEY_TO_CANONICAL: dict[str, str] = {
    "water_income": "water",
    "parking_income": "parking",
    "other_income": "other_income",
    "water": "water",
    "parking": "parking",
}


def build_optional_income_config(selected_keys: list[str]) -> OptionalIncomeConfig:
    """Map explicit UI optional-income selections onto ``OptionalIncomeConfig``.

    An empty ``selected_keys`` produces the existing default (all optional
    income excluded from GPI, still visible in the rent-roll sheet). GPI
    inclusion is decided here -- once, in this one place -- from exactly
    what the user explicitly selected; nothing is inferred or defaulted to
    "on". Raises ``PreviewFailure`` for any key that maps to neither a
    known UI key nor a canonical ``revenue_kun`` key.
    """
    canonical_keys: list[str] = []
    for key in selected_keys:
        canonical = _UI_KEY_TO_CANONICAL.get(key, key)
        if canonical not in _CANONICAL_OPTIONAL_INCOME_KEYS:
            raise PreviewFailure(
                "invalid_upload",
                f"未対応のoptional incomeカテゴリです: {key}",
                "invalid_optional_income_category",
                400,
            )
        if canonical not in canonical_keys:
            canonical_keys.append(canonical)

    return OptionalIncomeConfig(
        include_in_gpi=bool(canonical_keys),
        columns=canonical_keys,
    )


def generate_workbook(
    client_filename: str | None,
    source: BinaryIO,
    selected_optional_income: list[str],
) -> bytes:
    """Validate, extract, generate the direct-capitalization workbook, and return its bytes.

    Order (matches Issue #82's required workbook lifecycle):
      1. validate the optional-income selections (cheap, no I/O)
      2. validate + extract the upload via ``extract_units_from_upload``
         (its own request-specific temp directory is created and removed
         internally before this function proceeds)
      3. build ``DirectCapRow`` rows from the extracted units
      4. write the workbook to a fresh request-specific temporary path
      5. read the completed workbook into memory
      6. remove that temporary directory
      7. return the bytes (the caller wraps them in a ``StreamingResponse``)

    Raises ``PreviewFailure`` for any handled validation, extraction, or
    generation failure. No workbook is generated on the extraction-failure
    path, and no stale workbook is ever returned -- each call produces (or
    fails to produce) its own bytes from scratch.
    """
    oi_config = build_optional_income_config(selected_optional_income)
    units, _input_type = extract_units_from_upload(client_filename, source)

    rows = [DirectCapRow.from_rent_roll_unit(unit) for unit in units]

    with request_temp_dir() as temp_dir:
        xlsx_path = temp_dir / generate_temp_filename(".xlsx")
        try:
            write_direct_cap_workbook(xlsx_path, rows, oi_config=oi_config)
            data = xlsx_path.read_bytes()
        except PreviewFailure:
            raise
        except Exception as exc:  # any openpyxl/filesystem failure while writing
            raise PreviewFailure(
                "generation_failed",
                "Excelワークブックの生成に失敗しました。",
                "workbook_generation_error",
                500,
            ) from exc

    return data
