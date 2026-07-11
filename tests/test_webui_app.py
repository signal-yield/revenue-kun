"""Tests for the webui FastAPI application foundation (Issue #79).

Scope: root page and health endpoint only. No CSV/PDF handling, preview,
or Excel generation exists yet -- those belong to later issues.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from webui.app import app
from webui.config import DEFAULT_MAX_UPLOAD_MB


def test_app_is_importable():
    from webui.app import app as imported_app

    assert imported_app is not None


def test_root_returns_200():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200


def test_root_mentions_revenue_kun():
    client = TestClient(app)
    response = client.get("/")
    assert "revenue-kun" in response.text


def test_root_shows_default_upload_limit(monkeypatch):
    monkeypatch.delenv("REVENUE_KUN_MAX_UPLOAD_MB", raising=False)
    client = TestClient(app)
    response = client.get("/")
    assert str(DEFAULT_MAX_UPLOAD_MB) in response.text


def test_root_shows_overridden_upload_limit(monkeypatch):
    monkeypatch.setenv("REVENUE_KUN_MAX_UPLOAD_MB", "42")
    client = TestClient(app)
    response = client.get("/")
    assert "42" in response.text


def test_root_states_ocr_and_scanned_pdf_are_unsupported():
    client = TestClient(app)
    response = client.get("/")
    assert "OCR" in response.text
    assert "スキャンPDF" in response.text


def test_root_states_smartphone_and_saas_are_unsupported():
    client = TestClient(app)
    response = client.get("/")
    assert "スマホ撮影" in response.text
    assert "SaaS" in response.text


def test_root_states_output_is_not_appraisal():
    client = TestClient(app)
    response = client.get("/")
    assert "鑑定評価" in response.text


def test_root_does_not_claim_excel_download_is_available():
    """Preview exists as of #80/#81, but Excel generation/download does not yet (#82)."""
    client = TestClient(app)
    response = client.get("/")
    assert "準備中" in response.text


def test_healthz_returns_minimal_ok_response():
    client = TestClient(app)
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Preview UI presence (Issue #81)
# ---------------------------------------------------------------------------

def test_root_has_file_input_accepting_csv_and_pdf_only():
    client = TestClient(app)
    response = client.get("/")
    assert 'id="file-input"' in response.text
    assert 'accept=".csv,.pdf"' in response.text


def test_root_has_preview_button():
    client = TestClient(app)
    response = client.get("/")
    assert 'id="preview-button"' in response.text


def test_root_has_optional_income_display_area():
    client = TestClient(app)
    response = client.get("/")
    assert 'id="optional-income-box"' in response.text


def test_root_has_disabled_generate_placeholder():
    client = TestClient(app)
    response = client.get("/")
    assert 'id="generate-button"' in response.text
    assert "disabled" in response.text
    assert "次のステップで実装予定" in response.text


def test_root_states_optional_income_excluded_from_gpi_by_default():
    client = TestClient(app)
    response = client.get("/")
    assert "GPI" in response.text
    assert "明示的に選択しない限り" in response.text


def test_root_states_missing_values_are_not_inferred():
    client = TestClient(app)
    response = client.get("/")
    assert "自動的に推定・補完しません" in response.text


def test_root_states_uploads_stay_local():
    client = TestClient(app)
    response = client.get("/")
    assert "外部のAPIやサービスへは送信されません" in response.text


def test_static_app_js_is_served():
    client = TestClient(app)
    response = client.get("/static/app.js")
    assert response.status_code == 200


def test_static_styles_css_is_served():
    client = TestClient(app)
    response = client.get("/static/styles.css")
    assert response.status_code == 200
