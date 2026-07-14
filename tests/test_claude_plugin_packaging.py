"""Tests for the Claude Code plugin packaging of revenue-kun.

Structural/content checks only. Actual `claude plugin validate` / marketplace
install is exercised manually during PR validation (the `claude` CLI is not
assumed to be available under pytest).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE_PATH = ROOT / ".claude-plugin" / "marketplace.json"
PLUGIN_ROOT = ROOT / "claude-plugins" / "revenue-kun"
MANIFEST_PATH = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
CANONICAL_SKILL_DIR = ROOT / "skill"
PACKAGED_SKILL_DIR = PLUGIN_ROOT / "skills" / "revenue-kun"
PACKAGED_SKILL_MD = PACKAGED_SKILL_DIR / "SKILL.md"
DOC_DIR = ROOT / "docs" / "claude-code-plugin"

# Files that must never be intentionally left in the current state of PR #100
# (Codex plugin). This test suite must not assume those files exist.
CODEX_PLUGIN_ROOT = ROOT / "plugins" / "revenue-kun"
CODEX_MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
CODEX_SYNC_SCRIPT = ROOT / "scripts" / "sync_codex_plugin_skill.py"
CODEX_TEST_FILE = ROOT / "tests" / "test_codex_plugin_packaging.py"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# plugin.json
# ---------------------------------------------------------------------------

def test_plugin_manifest_required_and_metadata_fields():
    manifest = load_json(MANIFEST_PATH)
    assert manifest["name"] == "revenue-kun"
    assert manifest["description"]
    assert manifest["author"]["name"]
    assert manifest["homepage"].startswith("https://")
    assert manifest["repository"] == "https://github.com/signal-yield/revenue-kun"
    assert manifest["license"] == "Apache-2.0"
    assert isinstance(manifest["keywords"], list) and manifest["keywords"]


def test_plugin_name_matches_directory_name():
    manifest = load_json(MANIFEST_PATH)
    assert manifest["name"] == PLUGIN_ROOT.name


def test_version_is_consistent_with_version_file_and_package():
    manifest = load_json(MANIFEST_PATH)
    version_file = (ROOT / "VERSION").read_text(encoding="utf-8").strip().lstrip("v")

    init_text = (ROOT / "src" / "revenue_kun" / "__init__.py").read_text(encoding="utf-8")
    package_version = None
    for line in init_text.splitlines():
        if line.startswith("__version__"):
            package_version = line.split("=", 1)[1].strip().strip("'\"")
            break

    assert manifest["version"] == version_file
    assert package_version == version_file

    marketplace = load_json(MARKETPLACE_PATH)
    plugin_entry = marketplace["plugins"][0]
    assert plugin_entry["version"] == version_file


# ---------------------------------------------------------------------------
# marketplace.json
# ---------------------------------------------------------------------------

def test_marketplace_is_at_repo_root_for_github_shorthand_install():
    # Required so `/plugin marketplace add signal-yield/revenue-kun` works.
    assert MARKETPLACE_PATH.exists()
    assert MARKETPLACE_PATH.parent == ROOT / ".claude-plugin"


def test_marketplace_schema_and_linkage():
    marketplace = load_json(MARKETPLACE_PATH)
    assert marketplace["name"]
    assert marketplace["owner"]["name"]
    assert isinstance(marketplace["plugins"], list) and marketplace["plugins"]

    plugin_entry = marketplace["plugins"][0]
    assert plugin_entry["name"] == "revenue-kun"
    assert plugin_entry["source"] == "./claude-plugins/revenue-kun"
    assert plugin_entry["name"] == load_json(MANIFEST_PATH)["name"]


# ---------------------------------------------------------------------------
# Skill sync (skill/ is canonical)
# ---------------------------------------------------------------------------

def test_sync_check_passes_for_committed_state():
    result = subprocess.run(
        [sys.executable, "scripts/sync_claude_plugin_skill.py", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_sync_check_detects_intentional_drift(tmp_path):
    # Introduce a deliberate mismatch, confirm --check fails, then restore.
    original = PACKAGED_SKILL_MD.read_bytes()
    try:
        PACKAGED_SKILL_MD.write_bytes(original + b"\n# intentional drift for test\n")
        result = subprocess.run(
            [sys.executable, "scripts/sync_claude_plugin_skill.py", "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode != 0
    finally:
        PACKAGED_SKILL_MD.write_bytes(original)

    # Re-sync should restore a clean --check pass.
    sync_result = subprocess.run(
        [sys.executable, "scripts/sync_claude_plugin_skill.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert sync_result.returncode == 0, sync_result.stdout + sync_result.stderr
    check_result = subprocess.run(
        [sys.executable, "scripts/sync_claude_plugin_skill.py", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert check_result.returncode == 0, check_result.stdout + check_result.stderr


def test_packaged_skill_matches_canonical_skill_md():
    assert (CANONICAL_SKILL_DIR / "SKILL.md").read_bytes() == PACKAGED_SKILL_MD.read_bytes()


# ---------------------------------------------------------------------------
# No duplicate manual maintenance / no private data
# ---------------------------------------------------------------------------

def test_no_private_or_generated_artifacts_are_packaged():
    forbidden_suffixes = {".pdf", ".xlsx", ".xls", ".csv"}
    packaged = [
        p for p in PLUGIN_ROOT.rglob("*")
        if p.is_file() and p.suffix.lower() in forbidden_suffixes
    ]
    assert packaged == []


def test_no_pycache_in_packaged_skill():
    pycache_paths = [p for p in PACKAGED_SKILL_DIR.rglob("__pycache__")]
    pyc_files = [p for p in PACKAGED_SKILL_DIR.rglob("*.pyc")]
    assert pycache_paths == []
    assert pyc_files == []


# ---------------------------------------------------------------------------
# Docs presence and guardrail language
# ---------------------------------------------------------------------------

def test_required_docs_exist():
    assert (ROOT / "README.md").exists()
    assert (ROOT / "LICENSE").exists()
    assert (DOC_DIR / "README.md").exists()
    assert (DOC_DIR / "MARKETPLACE_JA.md").exists()
    assert (DOC_DIR / "MARKETPLACE_EN.md").exists()
    assert (DOC_DIR / "SECURITY_AND_PRIVACY.md").exists()
    assert (DOC_DIR / "SUBMISSION_CHECKLIST.md").exists()


def test_public_copy_has_no_forbidden_affirmative_claims():
    # SUBMISSION_CHECKLIST.md is intentionally excluded: it is a checklist that
    # names the forbidden phrases in order to check for their absence
    # elsewhere (the same pattern CLAUDE.md itself uses), not marketplace-
    # facing marketing copy.
    public_paths = [
        MANIFEST_PATH,
        MARKETPLACE_PATH,
        DOC_DIR / "README.md",
        DOC_DIR / "MARKETPLACE_JA.md",
        DOC_DIR / "MARKETPLACE_EN.md",
        DOC_DIR / "SECURITY_AND_PRIVACY.md",
    ]
    public_copy = "\n".join(p.read_text(encoding="utf-8") for p in public_paths)

    forbidden_positive_claims = [
        "収益価格を算定します",
        "OCRに対応しています",
        "スキャンPDFに対応しています",
        "hosted SaaSとして利用できます",
        "クラウドSaaSとして利用できます",
        "実務検証済み",
        "完全互換",
        "全エージェント対応",
    ]
    for phrase in forbidden_positive_claims:
        assert phrase not in public_copy, f"forbidden affirmative claim found: {phrase!r}"


def test_public_copy_states_negated_scope_correctly():
    public_copy = "\n".join(
        (DOC_DIR / name).read_text(encoding="utf-8")
        for name in ("MARKETPLACE_JA.md", "MARKETPLACE_EN.md", "SECURITY_AND_PRIVACY.md")
    )
    assert "収益価格ではありません" in public_copy or "not an appraised value" in public_copy
    assert "OCRには対応していません" in public_copy or "OCR-required" in public_copy
    assert "hosted SaaSではありません" in public_copy or "not exposed as a hosted SaaS" in public_copy or "local-execution only" in public_copy


def test_local_web_ui_bind_and_healthz_documented():
    text = (DOC_DIR / "MARKETPLACE_JA.md").read_text(encoding="utf-8")
    assert "127.0.0.1" in text
    assert "/healthz" in text
    assert "0.0.0.0" not in text


# ---------------------------------------------------------------------------
# Independence from the Codex plugin (PR #100)
# ---------------------------------------------------------------------------

def test_does_not_reuse_codex_plugin_root_directory():
    # The Codex plugin (PR #100, not yet merged) uses plugins/revenue-kun/.
    # This Claude Code plugin must use a distinct root to avoid future collision.
    assert PLUGIN_ROOT != CODEX_PLUGIN_ROOT
    assert PLUGIN_ROOT == ROOT / "claude-plugins" / "revenue-kun"


def test_codex_plugin_files_untouched_by_this_branch():
    # These files belong to PR #100 and are not expected to exist on a branch
    # created from main before that PR merges. If they do exist (e.g. this
    # branch was later rebased on top of a merged PR #100), this test only
    # asserts this branch does not overwrite them with Claude-Code-specific
    # content; it does not require them to exist.
    for path in (CODEX_PLUGIN_ROOT, CODEX_MARKETPLACE, CODEX_SYNC_SCRIPT, CODEX_TEST_FILE):
        if path.exists():
            assert "claude-plugins" not in path.read_text(encoding="utf-8", errors="ignore")


# ---------------------------------------------------------------------------
# revenue-kun core logic is untouched
# ---------------------------------------------------------------------------

def test_core_logic_directories_are_not_part_of_the_plugin_package():
    # The plugin packages a synced copy of skill/, not src/ or webui/ directly.
    for forbidden_dir_name in ("src", "webui"):
        assert not (PLUGIN_ROOT / forbidden_dir_name).exists()
