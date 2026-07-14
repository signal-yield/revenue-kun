from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "plugins" / "revenue-kun" / ".codex-plugin" / "plugin.json"
MARKETPLACE_PATH = ROOT / ".agents" / "plugins" / "marketplace.json"
CANONICAL_SKILL = ROOT / ".agents" / "skills" / "revenue-kun" / "SKILL.md"
PACKAGED_SKILL = ROOT / "plugins" / "revenue-kun" / "skills" / "revenue-kun" / "SKILL.md"
DOC_PATH = ROOT / "docs" / "CODEX_PLUGIN_MARKETPLACE.md"
INSTALL_DOC_PATH = ROOT / "docs" / "CODEX_PLUGIN_INSTALL.md"
SUBMISSION_DOC_PATH = ROOT / "docs" / "CODEX_DIRECTORY_SUBMISSION.md"
PRIVACY_PATH = ROOT / "docs" / "privacy.html"
TERMS_PATH = ROOT / "docs" / "terms.html"
SUPPORT_PATH = ROOT / "docs" / "support.html"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_manifest_required_fields_and_paths() -> None:
    manifest = load_json(MANIFEST_PATH)
    assert manifest["name"] == "revenue-kun"
    assert manifest["version"] == "0.5.2"
    assert manifest["description"]
    assert manifest["author"]["name"]
    assert manifest["homepage"].startswith("https://")
    assert manifest["repository"] == "https://github.com/signal-yield/revenue-kun"
    assert manifest["license"] == "Apache-2.0"
    assert manifest["skills"] == "./skills/"
    assert PACKAGED_SKILL.exists()


def test_version_is_consistent() -> None:
    manifest = load_json(MANIFEST_PATH)
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip().lstrip("v")
    package_version = None
    init_text = (ROOT / "src" / "revenue_kun" / "__init__.py").read_text(encoding="utf-8")
    for line in init_text.splitlines():
        if line.startswith("__version__"):
            package_version = line.split("=", 1)[1].strip().strip("'\"")
            break
    assert manifest["version"] == version
    assert package_version in (None, version)


def test_marketplace_schema_and_linkage() -> None:
    catalog = load_json(MARKETPLACE_PATH)
    assert catalog["name"]
    assert catalog["interface"]["displayName"]
    assert isinstance(catalog["plugins"], list) and catalog["plugins"]
    plugin = catalog["plugins"][0]
    assert plugin == {
        "name": "revenue-kun",
        "source": {"source": "local", "path": "./plugins/revenue-kun"},
        "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        "category": "Productivity",
    }
    assert plugin["name"] == load_json(MANIFEST_PATH)["name"]


def test_packaged_skill_matches_canonical_skill() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/sync_codex_plugin_skill.py", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert CANONICAL_SKILL.read_bytes() == PACKAGED_SKILL.read_bytes()


def test_sync_check_fails_for_deliberate_mismatch(tmp_path: Path) -> None:
    temporary_root = tmp_path / "repo"
    source = temporary_root / ".agents" / "skills" / "revenue-kun"
    destination = temporary_root / "plugins" / "revenue-kun" / "skills" / "revenue-kun"
    scripts = temporary_root / "scripts"
    source.mkdir(parents=True)
    destination.mkdir(parents=True)
    scripts.mkdir()
    (source / "SKILL.md").write_text("canonical\n", encoding="utf-8")
    (destination / "SKILL.md").write_text("stale\n", encoding="utf-8")
    shutil.copy2(ROOT / "scripts" / "sync_codex_plugin_skill.py", scripts)

    result = subprocess.run(
        [sys.executable, "scripts/sync_codex_plugin_skill.py", "--check"],
        cwd=temporary_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "content differs: SKILL.md" in result.stderr


def test_public_links_and_license_exist() -> None:
    manifest = load_json(MANIFEST_PATH)
    assert (ROOT / "README.md").exists()
    assert (ROOT / "LICENSE").exists()
    assert DOC_PATH.exists()
    assert INSTALL_DOC_PATH.exists()
    assert SUBMISSION_DOC_PATH.exists()
    assert PRIVACY_PATH.exists()
    assert TERMS_PATH.exists()
    assert SUPPORT_PATH.exists()
    assert manifest["homepage"] in (ROOT / "README.md").read_text(encoding="utf-8")
    assert manifest["interface"]["privacyPolicyURL"] == "https://signal-yield.github.io/revenue-kun/privacy.html"
    assert manifest["interface"]["termsOfServiceURL"] == "https://signal-yield.github.io/revenue-kun/terms.html"


def test_guardrail_language() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (MANIFEST_PATH, PACKAGED_SKILL, DOC_PATH)
    )
    public_copy = "\n".join(
        path.read_text(encoding="utf-8") for path in (MANIFEST_PATH, DOC_PATH)
    )
    assert "hosted SaaS" in text or "hosted SaaS".lower() in text.lower()
    assert "OCR" in text
    assert "スキャンPDF" in text or "Scanned PDF" in text
    assert "収益試算値" in text
    forbidden_positive_claims = [
        "OCR対応",
        "スキャンPDF対応",
        "hosted SaaSとして提供",
        "収益価格を算定します",
        "実務検証済み",
        "完全互換",
        "全エージェント対応",
    ]
    for phrase in forbidden_positive_claims:
        assert phrase not in public_copy


def test_directory_submission_materials_are_complete() -> None:
    text = SUBMISSION_DOC_PATH.read_text(encoding="utf-8")
    assert text.count("### Positive Test ") == 5
    assert text.count("### Negative Test ") == 3
    for required in [
        "https://platform.openai.com/plugins",
        "https://signal-yield.github.io/revenue-kun/privacy.html",
        "https://signal-yield.github.io/revenue-kun/terms.html",
        "https://signal-yield.github.io/revenue-kun/support.html",
        "Submit for Review",
        "Apps Management",
        "verified developer or business identity",
        "127.0.0.1",
        "OCR",
        "scanned PDFs",
        "hosted SaaS",
        "income-estimation values",
    ]:
        assert required in text


def test_public_support_page_has_required_submission_guidance() -> None:
    text = SUPPORT_PATH.read_text(encoding="utf-8")
    for required in [
        "Bug Reports",
        "Security Issues",
        "Support Scope",
        "synthetic or safely redacted data",
        "Do not post security-sensitive details",
        "127.0.0.1",
        "OCR",
        "hosted SaaS",
        "real-estate appraisal",
        "privacy.html",
        "terms.html",
        "https://github.com/signal-yield/revenue-kun/issues",
    ]:
        assert required in text


def test_codex_marketplace_install_docs_are_user_ready() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    page = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    install_doc = INSTALL_DOC_PATH.read_text(encoding="utf-8")
    combined = "\n".join([readme, page, install_doc])

    for required in [
        "codex plugin marketplace add signal-yield/revenue-kun",
        "codex plugin marketplace list",
        "codex plugin marketplace remove signal-yield",
        "repo-hosted Codex Marketplace",
        "Marketplace `signal-yield`",
        "Plugin `revenue-kun`",
        "/plugins",
        "signal-yield` marketplace",
        "open `revenue-kun`, and install it",
        "127.0.0.1",
        "hosted SaaS",
        "OCR",
        "scanned PDFs",
        "smartphone-captured images",
        "income-estimation values",
        "not a real-estate appraisal",
        "does not send input files to external services",
    ]:
        assert required in combined

    forbidden_claims = [
        "OpenAI公式Directoryに掲載済み",
        "official Directory listing is available",
        "verified publisher display is available",
        "codex plugin add revenue-kun@signal-yield",
        "OCR対応",
        "hosted SaaSとして提供",
    ]
    for phrase in forbidden_claims:
        assert phrase not in combined


def test_no_private_property_artifacts_are_packaged() -> None:
    plugin_root = ROOT / "plugins" / "revenue-kun"
    forbidden_suffixes = {".pdf", ".xlsx", ".xls", ".csv"}
    packaged = [p for p in plugin_root.rglob("*") if p.is_file() and p.suffix.lower() in forbidden_suffixes]
    assert packaged == []
