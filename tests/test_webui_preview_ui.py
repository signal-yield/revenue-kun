"""Tests for the browser preview UI (Issue #81) and generate/download UI (Issue #82).

Scope: structural checks on the served HTML/JS/CSS and on the JavaScript
source text itself. No real browser automation is used -- per the
project's lightweight test style, string/structure inspection is
sufficient (the actual `/api/preview` and `/api/generate` behaviour is
already covered by `tests/test_webui_preview.py` and
`tests/test_webui_generate.py`).
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


def _extract_generate_click_handler(source: str) -> str:
    """Return the body of generateButton's click handler.

    It is the last top-level statement in the IIFE, so everything from its
    start to the file's closing `})();` belongs to it -- a non-greedy
    regex bounded at the first `});` would stop inside a nested
    `.forEach(...)` call instead.
    """
    start = source.index('generateButton.addEventListener("click"')
    end = source.rindex("})();")
    return source[start:end]


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
# app.js: fetches /api/preview and /api/generate (Issue #82)
# ---------------------------------------------------------------------------

def test_app_js_fetches_api_preview():
    source = _read_app_js()
    assert "/api/preview" in source


def test_app_js_fetches_api_generate():
    source = _read_app_js_code_only()
    assert "/api/generate" in source


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


def test_app_js_does_not_generate_excel_content_client_side():
    """app.js may reference "workbook"/"xlsx" only as a downloaded artifact
    (e.g. downloadWorkbookBlob, the direct_cap.xlsx filename) -- it must not
    construct spreadsheet content itself."""
    source = _read_app_js_code_only()
    for forbidden in ("openpyxl", "sheetjs", "xlsx.utils", "new workbook(", "=sum(", "cell.value"):
        assert forbidden not in source.lower()


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
# v0.5.2: optional income is read-only (no checkboxes, no selection UI)
# ---------------------------------------------------------------------------

def test_app_js_has_no_checkbox_for_optional_income():
    source = _read_app_js_code_only()
    assert "type = \"checkbox\"" not in source
    assert "optional-income-checkbox" not in source


def test_app_js_renders_optional_income_as_read_only_table():
    source = _read_app_js_code_only()
    render_fn = re.search(
        r"function renderOptionalIncome\(optionalIncome\)\s*\{(.*?)\n  \}",
        source, re.DOTALL,
    )
    assert render_fn is not None
    body = render_fn.group(1)
    assert "monthly_total" in body
    assert "annual_total" in body
    assert "checkbox" not in body


def test_app_js_renders_gpi_annual():
    source = _read_app_js_code_only()
    assert "renderGpiAnnual" in source
    assert "gpi_annual" in source in source


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
# Generate/download flow (Issue #82)
# ---------------------------------------------------------------------------

def test_app_js_enables_generate_button_only_after_successful_preview():
    source = _read_app_js_code_only()
    render_preview_fn = re.search(r"function renderPreview\(data\)\s*\{(.*?)\n  \}", source, re.DOTALL)
    assert render_preview_fn is not None
    assert "generateButton.disabled = false" in render_preview_fn.group(1)


def test_app_js_disables_generate_button_on_safe_failure():
    source = _read_app_js_code_only()
    show_error_fn = re.search(r"function showError\(message\)\s*\{(.*?)\n  \}", source, re.DOTALL)
    assert show_error_fn is not None
    assert "generateButton.disabled = true" in show_error_fn.group(1)


def test_app_js_disables_generate_button_on_new_file_selection():
    source = _read_app_js_code_only()
    reset_fn = re.search(r"function resetResults\(\)\s*\{(.*?)\n  \}", source, re.DOTALL)
    assert reset_fn is not None
    assert "generateButton.disabled = true" in reset_fn.group(1)


def test_app_js_generate_handler_appends_selected_file():
    source = _read_app_js_code_only()
    handler = _extract_generate_click_handler(source)
    assert 'formData.append("file", selectedFile)' in handler


def test_app_js_generate_handler_does_not_send_optional_income_selection():
    """v0.5.2: 収入は自動算入のため、選択を送信するコードは存在しない。"""
    source = _read_app_js_code_only()
    handler = _extract_generate_click_handler(source)
    assert "optional_income" not in handler
    assert "getSelectedOptionalIncomeKeys" not in source


def test_app_js_has_blob_download_path():
    source = _read_app_js_code_only()
    assert "response.blob()" in source
    assert "downloadWorkbookBlob" in source
    assert 'link.download = "direct_cap.xlsx"' in source


def test_app_js_distinguishes_json_error_from_binary_response():
    source = _read_app_js_code_only()
    handler = _extract_generate_click_handler(source)
    assert "content-type" in handler
    assert "application/json" in handler


def test_app_js_generate_guards_against_double_submission():
    source = _read_app_js_code_only()
    handler = _extract_generate_click_handler(source)
    assert "if (isSubmitting)" in handler


def test_app_js_does_not_display_original_filename():
    source = _read_app_js_code_only()
    assert "file.name" not in source


# ---------------------------------------------------------------------------
# Regression: existing suites remain intact
# ---------------------------------------------------------------------------

def test_existing_root_and_healthz_still_work():
    client = TestClient(app)
    assert client.get("/").status_code == 200
    assert client.get("/healthz").status_code == 200
