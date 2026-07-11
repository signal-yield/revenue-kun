"""Tests for the browser preview UI added in Issue #81.

Scope: structural checks on the served HTML/JS/CSS and on the JavaScript
source text itself. No real browser automation is used -- per the
project's lightweight test style, string/structure inspection is
sufficient (the actual `/api/preview` behaviour is already covered by
`tests/test_webui_preview.py`).
"""
from __future__ import annotations

import re
from pathlib import Path

from fastapi.testclient import TestClient

from webui.app import app

_APP_JS_PATH = Path(__file__).resolve().parents[1] / "webui" / "static" / "app.js"


def _read_app_js() -> str:
    return _APP_JS_PATH.read_text(encoding="utf-8")


def _read_app_js_code_only() -> str:
    """Return app.js with comments stripped.

    Used for "must not contain X" checks so that explanatory comments
    (e.g. pointing at the future #82 generate endpoint) don't produce
    false positives -- only actual code is scanned.
    """
    source = _read_app_js()
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    source = re.sub(r"//[^\n]*", "", source)
    return source


# ---------------------------------------------------------------------------
# HTML: required notices (Issue #81 section 6)
# ---------------------------------------------------------------------------

def test_root_states_output_is_revenue_estimate_not_appraisal():
    client = TestClient(app)
    response = client.get("/")
    assert "収益試算値" in response.text
    assert "収益価格ではありません" in response.text or "鑑定評価ではありません" in response.text


def test_root_states_no_investment_legal_tax_advice():
    client = TestClient(app)
    response = client.get("/")
    assert "投資助言" in response.text
    assert "法律助言" in response.text
    assert "税務助言" in response.text


def test_root_states_supported_inputs_are_csv_and_text_pdf_only():
    client = TestClient(app)
    response = client.get("/")
    assert "CSV" in response.text
    assert "テキスト抽出可能なPDF" in response.text


# ---------------------------------------------------------------------------
# app.js: fetches /api/preview, never /api/generate
# ---------------------------------------------------------------------------

def test_app_js_fetches_api_preview():
    source = _read_app_js()
    assert "/api/preview" in source


def test_app_js_does_not_fetch_api_generate():
    source = _read_app_js_code_only()
    assert "/api/generate" not in source


# ---------------------------------------------------------------------------
# app.js: no domain logic duplicated in the browser
# ---------------------------------------------------------------------------

def test_app_js_does_not_parse_csv():
    source = _read_app_js()
    assert "csv" not in source.lower() or "split(" not in source


def test_app_js_does_not_reference_pdf_parsing_libraries():
    source = _read_app_js_code_only()
    for forbidden in ("pdfplumber", "pdf.js", "pdfjs", "PDFDocument"):
        assert forbidden.lower() not in source.lower()


def test_app_js_does_not_reference_excel_or_workbook_generation():
    source = _read_app_js_code_only()
    for forbidden in ("openpyxl", "Workbook", "xlsx", "SheetJS"):
        assert forbidden.lower() not in source.lower()


def test_app_js_does_not_reference_noi_or_valuation_terms():
    source = _read_app_js_code_only()
    for forbidden in ("cap_rate", "vacancy_rate", "capitalization", "noi", "gpi = "):
        assert forbidden.lower() not in source.lower()


def test_app_js_does_not_construct_optional_income_config():
    source = _read_app_js()
    assert "OptionalIncomeConfig" not in source
    assert "include_in_gpi" not in source


# ---------------------------------------------------------------------------
# app.js: safe DOM rendering
# ---------------------------------------------------------------------------

def test_app_js_does_not_use_inner_html():
    source = _read_app_js()
    assert "innerHTML" not in source


def test_reset_does_not_wipe_static_results_structure():
    """Regression guard: resetResults() must clear only the dynamic sub-areas.

    An earlier draft called clearChildren(resultsBox) directly, which wiped
    out the static generate button, headings, and table header the first
    time a file was selected -- caught via a live browser check, not by the
    structural tests alone.
    """
    source = _read_app_js_code_only()
    reset_fn = re.search(r"function resetResults\(\)\s*\{(.*?)\n  \}", source, re.DOTALL)
    assert reset_fn is not None
    body = reset_fn.group(1)
    assert "clearChildren(resultsBox)" not in body
    assert "clearChildren(summaryBox)" in body
    assert "clearChildren(rowsTableBody)" in body
    assert "clearChildren(missingList)" in body
    assert "clearChildren(optionalIncomeBox)" in body


def test_app_js_uses_text_content_for_rendering():
    source = _read_app_js()
    assert "textContent" in source


# ---------------------------------------------------------------------------
# Optional-income checkbox defaults (structural guarantee in the JS source)
# ---------------------------------------------------------------------------

def test_app_js_forces_checkboxes_unchecked_by_default():
    source = _read_app_js()
    assert "checkbox.checked = false" in source


def test_app_js_disables_checkbox_when_not_present():
    source = _read_app_js()
    assert "checkbox.disabled = !entry.present" in source


def test_app_js_resets_state_on_new_file_selection():
    source = _read_app_js()
    assert "resetResults" in source
    assert "addEventListener(\"change\"" in source


def test_app_js_retains_selected_file_for_future_generate_flow():
    source = _read_app_js()
    assert "selectedFile" in source


def test_app_js_guards_against_double_submission():
    source = _read_app_js()
    assert "isSubmitting" in source


# ---------------------------------------------------------------------------
# Regression: existing suites remain intact
# ---------------------------------------------------------------------------

def test_existing_root_and_healthz_still_work():
    client = TestClient(app)
    assert client.get("/").status_code == 200
    assert client.get("/healthz").status_code == 200
