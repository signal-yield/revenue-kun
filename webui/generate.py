"""Stateless workbook generation logic for ``POST /api/generate`` (Issue #82).

This module is a thin adapter: it reuses ``webui.preview.extract_units_from_upload``
for validation/extraction (no PDF/CSV parsing logic is duplicated here) and
calls the existing ``revenue_kun.excel_output.write_direct_cap_workbook``
directly. It does not call ``revenue_kun.cli.run()``, invoke ``src/main.py``
via subprocess, or generate any Excel formula itself -- see Issue #78 for
the approved architecture decision.

v0.5.2 product boundary: the Web UI does not collect an optional-income
selection. Every recurring income item (賃料/共益費/水道代収入/駐車場収入/
その他収入) extracted from the upload is always reflected in both
calculation sheets -- see ``revenue_kun.excel_output`` for details. The
``selected_optional_income`` parameter below is accepted only for backward
compatibility with older frontend code that may still send it; its value
is ignored and has no effect on the generated workbook.

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

from revenue_kun.excel_output import DirectCapRow, write_direct_cap_workbook

from .preview import PreviewFailure, extract_units_from_upload
from .upload import generate_temp_filename, request_temp_dir


def generate_workbook(
    client_filename: str | None,
    source: BinaryIO,
    selected_optional_income: list[str] | None = None,
) -> bytes:
    """Validate, extract, generate the direct-capitalization workbook, and return its bytes.

    *selected_optional_income* is accepted for backward compatibility only
    (deprecated; see module docstring) and is not used -- recurring income
    is always auto-included in both calculation sheets regardless of its
    value.

    Order (matches Issue #82's required workbook lifecycle):
      1. validate + extract the upload via ``extract_units_from_upload``
         (its own request-specific temp directory is created and removed
         internally before this function proceeds)
      2. build ``DirectCapRow`` rows from the extracted units
      3. write the workbook to a fresh request-specific temporary path
      4. read the completed workbook into memory
      5. remove that temporary directory
      6. return the bytes (the caller wraps them in a ``StreamingResponse``)

    Raises ``PreviewFailure`` for any handled validation, extraction, or
    generation failure. No workbook is generated on the extraction-failure
    path, and no stale workbook is ever returned -- each call produces (or
    fails to produce) its own bytes from scratch.
    """
    del selected_optional_income  # deprecated, no effect (see docstring)
    units, _input_type = extract_units_from_upload(client_filename, source)

    rows = [DirectCapRow.from_rent_roll_unit(unit) for unit in units]

    with request_temp_dir() as temp_dir:
        xlsx_path = temp_dir / generate_temp_filename(".xlsx")
        try:
            write_direct_cap_workbook(xlsx_path, rows)
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
