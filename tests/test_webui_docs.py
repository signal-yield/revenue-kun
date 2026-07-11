"""Tests for Dockerfile.web and Web UI documentation (Issue #82).

Structural/text checks only -- an actual `docker build`/`docker run` is
exercised manually during PR validation, not in the automated test suite
(no Docker daemon is assumed to be available under pytest).
"""
from __future__ import annotations

from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DOCKERFILE_WEB = _REPO_ROOT / "Dockerfile.web"
_DOCKERFILE_CLI = _REPO_ROOT / "Dockerfile"
_README = _REPO_ROOT / "README.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Dockerfile.web
# ---------------------------------------------------------------------------

def test_dockerfile_web_exists():
    assert _DOCKERFILE_WEB.exists()


def test_dockerfile_web_uses_requirements_web_txt():
    content = _read(_DOCKERFILE_WEB)
    assert "requirements-web.txt" in content


def test_dockerfile_web_starts_the_web_app():
    content = _read(_DOCKERFILE_WEB)
    assert "webui.app:app" in content
    assert "uvicorn" in content


def test_dockerfile_web_does_not_reuse_cli_output_dir():
    content = _read(_DOCKERFILE_WEB)
    assert "mkdir -p output" not in content


def test_existing_cli_dockerfile_is_unchanged():
    content = _read(_DOCKERFILE_CLI)
    assert "requirements.txt" in content
    assert "requirements-web.txt" not in content
    assert 'CMD ["python", "src/main.py", "--help"]' in content


# ---------------------------------------------------------------------------
# README documentation
# ---------------------------------------------------------------------------

def test_readme_documents_web_ui_as_local_only():
    content = _read(_README)
    assert "ローカル実行専用" in content
    assert "ホスティング型SaaSではありません" in content


def test_readme_states_ocr_and_scanned_pdf_unsupported_for_web_ui():
    content = _read(_README)
    assert "OCR・スキャンPDF・スマホ撮影には対応していません" in content


def test_readme_documents_direct_cap_xlsx_output():
    content = _read(_README)
    assert "direct_cap.xlsx" in content


def test_readme_states_output_is_not_appraisal():
    content = _read(_README)
    assert "鑑定評価ではありません" in content


def test_readme_includes_loopback_docker_run_example():
    content = _read(_README)
    assert "docker build -f Dockerfile.web" in content
    assert "127.0.0.1:8000:8000" in content


def test_readme_does_not_claim_public_internet_exposure():
    content = _read(_README)
    assert "インターネットへの公開は想定していません" in content
    forbidden_phrases = ["インターネットに公開してください", "外部に公開してください", "0.0.0.0:8000:8000"]
    for phrase in forbidden_phrases:
        assert phrase not in content


def test_readme_preserves_existing_cli_usage_section():
    content = _read(_README)
    assert "python src/main.py" in content
    assert "--excel-output" in content
