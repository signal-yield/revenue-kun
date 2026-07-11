"""Tests for POST /api/preview (Issue #80).

Uses only synthetic fixtures already committed to the repo
(`data/dummy_rent_roll.csv`, `data/sample_rentroll_simple.pdf`) or
generated on the fly via `revenue_kun.sample_pdf`. No real property or
tenant information is used.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from revenue_kun.sample_pdf import build_text_only_pdf
from webui.app import app

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DUMMY_CSV = _REPO_ROOT / "data" / "dummy_rent_roll.csv"
_SIMPLE_PDF = _REPO_ROOT / "data" / "sample_rentroll_simple.pdf"


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def _upload(client: TestClient, filename: str, content: bytes, content_type: str = "application/octet-stream"):
    return client.post(
        "/api/preview",
        files={"file": (filename, content, content_type)},
    )


# ---------------------------------------------------------------------------
# Success: CSV
# ---------------------------------------------------------------------------

def test_valid_csv_preview_ok(client):
    response = _upload(client, "rentroll.csv", _DUMMY_CSV.read_bytes(), "text/csv")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["input_type"] == "csv"


def test_valid_csv_preview_unit_count_and_status_summary(client):
    response = _upload(client, "rentroll.csv", _DUMMY_CSV.read_bytes(), "text/csv")
    body = response.json()
    assert body["unit_count"] == 9
    assert body["status_summary"] == {"occupied": 7, "vacant": 2, "unknown": 0}


def test_valid_csv_preview_includes_missing_information(client):
    response = _upload(client, "rentroll.csv", _DUMMY_CSV.read_bytes(), "text/csv")
    body = response.json()
    assert isinstance(body["missing"], list)
    assert len(body["missing"]) > 0
    for item in body["missing"]:
        assert set(item.keys()) == {"field", "message", "severity"}
        assert item["severity"] in ("error", "warning")
    assert any(item["severity"] == "error" for item in body["missing"])


def test_valid_csv_preview_includes_optional_income_summary(client):
    response = _upload(client, "rentroll.csv", _DUMMY_CSV.read_bytes(), "text/csv")
    body = response.json()
    oi = body["optional_income"]
    assert set(oi.keys()) == {"water_income", "parking_income", "other_income"}
    for entry in oi.values():
        assert set(entry.keys()) == {"present", "total"}


def test_valid_csv_preview_rows_do_not_include_tenant_name(client):
    response = _upload(client, "rentroll.csv", _DUMMY_CSV.read_bytes(), "text/csv")
    body = response.json()
    for row in body["rows"]:
        assert set(row.keys()) == {
            "room", "status", "rent", "common_fee",
            "water_income", "parking_income", "other_income",
        }
    assert "アルファ" not in response.text


# ---------------------------------------------------------------------------
# Success: PDF
# ---------------------------------------------------------------------------

def test_valid_pdf_preview_ok(client):
    response = _upload(client, "rentroll.pdf", _SIMPLE_PDF.read_bytes(), "application/pdf")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["input_type"] == "pdf"
    assert body["unit_count"] == 5
    assert body["status_summary"]["occupied"] == 5


# ---------------------------------------------------------------------------
# Privacy: no original filename / filesystem path / traceback leaks
# ---------------------------------------------------------------------------

def test_response_does_not_include_original_filename(client):
    original_name = "super-secret-tenant-rentroll-2026.csv"
    response = _upload(client, original_name, _DUMMY_CSV.read_bytes(), "text/csv")
    assert original_name not in response.text
    assert "secret" not in response.text


def test_response_does_not_include_filesystem_path(client):
    response = _upload(client, "rentroll.csv", _DUMMY_CSV.read_bytes(), "text/csv")
    assert "revenue_kun_webui_" not in response.text
    assert "Traceback" not in response.text


# ---------------------------------------------------------------------------
# Validation / safe failure
# ---------------------------------------------------------------------------

def test_unsupported_extension_is_safe_failure(client):
    response = _upload(client, "rentroll.xlsx", b"whatever", "application/octet-stream")
    assert response.status_code == 400
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["type"] == "invalid_upload"
    assert "Traceback" not in response.text


def test_extensionless_upload_is_safe_failure(client):
    response = _upload(client, "rentroll", b"whatever", "application/octet-stream")
    assert response.status_code == 400
    body = response.json()
    assert body["ok"] is False


def test_malformed_pdf_signature_is_safe_failure(client):
    response = _upload(client, "fake.pdf", b"this is not a pdf file at all", "application/pdf")
    assert response.status_code == 400
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["detail_code"] == "invalid_pdf_signature"


def test_pdf_with_valid_signature_but_corrupted_body_is_safe_failure(client):
    garbage = b"%PDF-1.4\n" + b"not a real pdf body" * 50
    response = _upload(client, "corrupted.pdf", garbage, "application/pdf")
    assert response.status_code == 422
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["type"] == "extraction_failed"
    assert "Traceback" not in response.text


def test_scanned_or_table_less_pdf_is_safe_failure(client, tmp_path):
    """A real PDF with text but no extractable table simulates a scanned/unsupported PDF."""
    pdf_path = tmp_path / "no_table.pdf"
    build_text_only_pdf(pdf_path)
    response = _upload(client, "scanned.pdf", pdf_path.read_bytes(), "application/pdf")
    assert response.status_code == 422
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["type"] == "extraction_failed"
    assert body["error"]["detail_code"] == "rent_roll_table_not_found"


def test_malformed_csv_is_safe_failure(client):
    malformed = "区画,月額賃料_円,稼働状況\n101,not-a-number,稼働\n".encode("utf-8")
    response = _upload(client, "broken.csv", malformed, "text/csv")
    assert response.status_code == 422
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["type"] == "extraction_failed"


def test_oversized_upload_is_safe_failure(client, monkeypatch):
    monkeypatch.setenv("REVENUE_KUN_MAX_UPLOAD_MB", "1")
    oversized = b"x" * (2 * 1024 * 1024)
    response = _upload(client, "big.csv", oversized, "text/csv")
    assert response.status_code == 400
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["detail_code"] == "upload_too_large"


def test_no_file_attached_is_safe_failure(client):
    response = client.post("/api/preview")
    assert response.status_code == 400
    body = response.json()
    assert body["ok"] is False
    assert "Traceback" not in response.text


def test_empty_csv_upload_returns_zero_units_without_crashing(client):
    response = _upload(client, "empty.csv", b"", "text/csv")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["unit_count"] == 0


def test_empty_pdf_upload_is_safe_failure(client):
    response = _upload(client, "empty.pdf", b"", "application/pdf")
    assert response.status_code == 400
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["detail_code"] == "invalid_pdf_signature"


# ---------------------------------------------------------------------------
# Temporary-file cleanup
# ---------------------------------------------------------------------------

def _temp_dir_count() -> int:
    import tempfile

    base = Path(tempfile.gettempdir())
    return len(list(base.glob("revenue_kun_webui_*")))


def test_temp_files_removed_after_successful_preview(client):
    before = _temp_dir_count()
    _upload(client, "rentroll.csv", _DUMMY_CSV.read_bytes(), "text/csv")
    assert _temp_dir_count() == before


def test_temp_files_removed_after_validation_failure(client):
    before = _temp_dir_count()
    _upload(client, "rentroll.xlsx", b"whatever", "application/octet-stream")
    assert _temp_dir_count() == before


def test_temp_files_removed_after_extraction_failure(client, tmp_path):
    pdf_path = tmp_path / "no_table.pdf"
    build_text_only_pdf(pdf_path)
    before = _temp_dir_count()
    _upload(client, "scanned.pdf", pdf_path.read_bytes(), "application/pdf")
    assert _temp_dir_count() == before
