"""Tests for webui.upload -- extension validation and temp-file foundation.

Uses only synthetic, non-PII filenames and byte content.
"""
from __future__ import annotations

import io
from pathlib import Path

import pytest

from webui.upload import (
    UploadTooLargeError,
    UploadValidationError,
    generate_temp_filename,
    request_temp_dir,
    validate_extension,
    write_limited,
)


# ---------------------------------------------------------------------------
# validate_extension
# ---------------------------------------------------------------------------

def test_csv_is_allowed():
    assert validate_extension("rentroll.csv") == ".csv"


def test_pdf_is_allowed():
    assert validate_extension("rentroll.pdf") == ".pdf"


def test_uppercase_csv_is_allowed():
    assert validate_extension("RENTROLL.CSV") == ".csv"


def test_uppercase_pdf_is_allowed():
    assert validate_extension("RENTROLL.PDF") == ".pdf"


def test_unsupported_extension_is_rejected():
    with pytest.raises(UploadValidationError):
        validate_extension("rentroll.xlsx")


def test_missing_extension_is_rejected():
    with pytest.raises(UploadValidationError):
        validate_extension("rentroll")


def test_disguised_executable_is_rejected():
    """A trailing .exe must not slip through just because .csv appears earlier."""
    with pytest.raises(UploadValidationError):
        validate_extension("rentroll.csv.exe")


def test_empty_filename_is_rejected():
    with pytest.raises(UploadValidationError):
        validate_extension("")


def test_none_filename_is_rejected():
    with pytest.raises(UploadValidationError):
        validate_extension(None)


# ---------------------------------------------------------------------------
# generate_temp_filename
# ---------------------------------------------------------------------------

def test_generated_filename_does_not_contain_original_name():
    original = "confidential-tenant-rentroll.csv"
    generated = generate_temp_filename(".csv")
    assert generated.endswith(".csv")
    assert "confidential" not in generated
    assert "tenant" not in generated
    assert "rentroll" not in generated
    assert original.split(".")[0] not in generated


def test_generated_filenames_are_unique():
    first = generate_temp_filename(".pdf")
    second = generate_temp_filename(".pdf")
    assert first != second


# ---------------------------------------------------------------------------
# request_temp_dir
# ---------------------------------------------------------------------------

def test_temp_dir_removed_on_normal_exit():
    with request_temp_dir() as path:
        assert path.exists()
        (path / "scratch.txt").write_text("synthetic content")
    assert not path.exists()


def test_temp_dir_removed_on_exception():
    captured_path: Path | None = None
    with pytest.raises(RuntimeError):
        with request_temp_dir() as path:
            captured_path = path
            assert path.exists()
            raise RuntimeError("simulated failure inside the request")
    assert captured_path is not None
    assert not captured_path.exists()


def test_temp_dir_is_request_specific_not_shared():
    with request_temp_dir() as first:
        with request_temp_dir() as second:
            assert first != second


# ---------------------------------------------------------------------------
# write_limited
# ---------------------------------------------------------------------------

def test_write_limited_writes_full_content_under_limit(tmp_path):
    payload = b"synthetic,csv,content\n" * 10
    destination = tmp_path / "out.csv"
    written = write_limited(io.BytesIO(payload), destination, max_bytes=len(payload) + 1)
    assert written == len(payload)
    assert destination.read_bytes() == payload


def test_write_limited_reads_in_chunks_not_all_at_once(tmp_path):
    payload = b"x" * 100
    destination = tmp_path / "out.csv"
    read_calls = []

    class _CountingReader:
        def __init__(self, data: bytes) -> None:
            self._buf = io.BytesIO(data)

        def read(self, n: int) -> bytes:
            read_calls.append(n)
            return self._buf.read(n)

    write_limited(_CountingReader(payload), destination, max_bytes=1000, chunk_size=10)
    assert len(read_calls) > 1
    assert all(n == 10 for n in read_calls[:-1])


def test_write_limited_raises_when_over_limit(tmp_path):
    payload = b"y" * 2048
    destination = tmp_path / "out.pdf"
    with pytest.raises(UploadTooLargeError):
        write_limited(io.BytesIO(payload), destination, max_bytes=1024, chunk_size=256)


def test_write_limited_deletes_partial_file_when_over_limit(tmp_path):
    payload = b"z" * 2048
    destination = tmp_path / "out.pdf"
    with pytest.raises(UploadTooLargeError):
        write_limited(io.BytesIO(payload), destination, max_bytes=1024, chunk_size=256)
    assert not destination.exists()
