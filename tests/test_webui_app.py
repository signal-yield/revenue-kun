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


def test_root_does_not_claim_preview_or_download_are_available():
    """This foundation has no preview/download feature yet; the page must not imply otherwise."""
    client = TestClient(app)
    response = client.get("/")
    assert "準備中" in response.text


def test_healthz_returns_minimal_ok_response():
    client = TestClient(app)
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
