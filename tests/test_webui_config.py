"""Tests for webui.config -- the Web UI upload-size setting.

Uses pytest's monkeypatch fixture so environment-variable changes never
leak into other tests.
"""
from __future__ import annotations

import pytest

from webui.config import (
    DEFAULT_MAX_UPLOAD_MB,
    ENV_MAX_UPLOAD_MB,
    WebUIConfigError,
    get_max_upload_bytes,
    get_max_upload_mb,
)


def test_default_when_unset(monkeypatch):
    monkeypatch.delenv(ENV_MAX_UPLOAD_MB, raising=False)
    assert get_max_upload_mb() == DEFAULT_MAX_UPLOAD_MB == 20


def test_positive_override(monkeypatch):
    monkeypatch.setenv(ENV_MAX_UPLOAD_MB, "50")
    assert get_max_upload_mb() == 50


def test_bytes_conversion_matches_mb(monkeypatch):
    monkeypatch.setenv(ENV_MAX_UPLOAD_MB, "3")
    assert get_max_upload_bytes() == 3 * 1024 * 1024


def test_bytes_conversion_uses_default(monkeypatch):
    monkeypatch.delenv(ENV_MAX_UPLOAD_MB, raising=False)
    assert get_max_upload_bytes() == DEFAULT_MAX_UPLOAD_MB * 1024 * 1024


def test_rejects_zero(monkeypatch):
    monkeypatch.setenv(ENV_MAX_UPLOAD_MB, "0")
    with pytest.raises(WebUIConfigError):
        get_max_upload_mb()


def test_rejects_negative(monkeypatch):
    monkeypatch.setenv(ENV_MAX_UPLOAD_MB, "-5")
    with pytest.raises(WebUIConfigError):
        get_max_upload_mb()


def test_rejects_non_numeric(monkeypatch):
    monkeypatch.setenv(ENV_MAX_UPLOAD_MB, "not-a-number")
    with pytest.raises(WebUIConfigError):
        get_max_upload_mb()


def test_rejects_empty_string(monkeypatch):
    monkeypatch.setenv(ENV_MAX_UPLOAD_MB, "")
    with pytest.raises(WebUIConfigError):
        get_max_upload_mb()


def test_rejects_whitespace_only(monkeypatch):
    monkeypatch.setenv(ENV_MAX_UPLOAD_MB, "   ")
    with pytest.raises(WebUIConfigError):
        get_max_upload_mb()


def test_invalid_error_message_does_not_leak_environment(monkeypatch):
    """The error message should name the setting, not dump os.environ."""
    monkeypatch.setenv(ENV_MAX_UPLOAD_MB, "not-a-number")
    monkeypatch.setenv("SOME_UNRELATED_SECRET", "should-not-appear")
    with pytest.raises(WebUIConfigError) as exc_info:
        get_max_upload_mb()
    message = str(exc_info.value)
    assert ENV_MAX_UPLOAD_MB in message
    assert "should-not-appear" not in message
