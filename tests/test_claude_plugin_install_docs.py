"""Documentation tests for the Claude Code Plugin GitHub-repo install guide.

These are content/structure checks only — they do not invoke the `claude`
CLI. Actual `claude plugin marketplace add` / `install` lifecycle is
exercised manually during PR validation.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
INDEX_HTML = ROOT / "docs" / "index.html"
INSTALL_GUIDE = ROOT / "docs" / "CLAUDE_CODE_PLUGIN_INSTALL.md"

MARKETPLACE_ADD_CMD = "claude plugin marketplace add signal-yield/revenue-kun"
PLUGIN_INSTALL_CMD = "claude plugin install revenue-kun@revenue-kun"

# The Codex Plugin's own install command, which must not be touched by this work.
CODEX_MARKETPLACE_ADD_CMD = "codex plugin marketplace add signal-yield/revenue-kun"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_readme_has_claude_code_plugin_section():
    text = _read(README)
    assert "## Claude Code Plugin" in text


def test_readme_contains_marketplace_add_and_install_commands():
    text = _read(README)
    assert MARKETPLACE_ADD_CMD in text
    assert PLUGIN_INSTALL_CMD in text


def test_readme_contains_management_commands():
    text = _read(README)
    assert "claude plugin details revenue-kun@revenue-kun" in text
    assert "claude plugin disable revenue-kun@revenue-kun" in text
    assert "claude plugin enable revenue-kun@revenue-kun" in text
    assert "claude plugin uninstall revenue-kun@revenue-kun" in text
    assert "claude plugin marketplace remove revenue-kun" in text


def test_readme_links_to_install_guide():
    text = _read(README)
    assert "docs/CLAUDE_CODE_PLUGIN_INSTALL.md" in text


def test_readme_codex_plugin_command_is_unchanged():
    text = _read(README)
    assert CODEX_MARKETPLACE_ADD_CMD in text


def test_pages_contain_marketplace_add_and_install_commands():
    text = _read(INDEX_HTML)
    assert MARKETPLACE_ADD_CMD in text
    assert PLUGIN_INSTALL_CMD in text


def test_pages_have_distinct_claude_code_and_codex_plugin_cards():
    text = _read(INDEX_HTML)
    assert 'id="claude-code-plugin"' in text
    assert 'id="codex-plugin"' in text
    assert text.index('id="claude-code-plugin"') < text.index('id="codex-plugin"')


def test_pages_codex_plugin_card_command_is_unchanged():
    text = _read(INDEX_HTML)
    assert CODEX_MARKETPLACE_ADD_CMD in text


def test_pages_preserve_privacy_terms_support_links():
    text = _read(INDEX_HTML)
    assert 'href="privacy.html"' in text
    assert 'href="terms.html"' in text
    assert 'href="support.html"' in text


def test_install_guide_exists_and_has_required_sections():
    assert INSTALL_GUIDE.exists()
    text = _read(INSTALL_GUIDE)
    for heading in (
        "## Prerequisites",
        "## 1. Add the Marketplace",
        "## 2. Install the Plugin",
        "## 3. Confirm with Plugin Details",
        "## Skill Detection",
        "## Usage Examples",
        "## Local Web UI",
        "## Disable",
        "## Enable",
        "## Uninstall",
        "## Remove the Marketplace",
        "## Troubleshooting",
        "## Claude Code Official Marketplace vs. This Repository",
        "## Security / Privacy",
        "## Support",
    ):
        assert heading in text, f"missing section: {heading!r}"


def test_install_guide_contains_marketplace_and_install_commands():
    text = _read(INSTALL_GUIDE)
    assert MARKETPLACE_ADD_CMD in text
    assert PLUGIN_INSTALL_CMD in text


def test_install_guide_does_not_claim_official_marketplace_listing():
    # "verified publisher" is intentionally not in this forbidden list: the
    # guide legitimately names it under "Not part of this work" (the same
    # negation pattern used elsewhere in this repo's guardrail checks).
    text = _read(INSTALL_GUIDE)
    forbidden = [
        "公式Marketplaceに掲載済み",
        "official Marketplace listing is complete",
        "already listed in the official",
    ]
    for phrase in forbidden:
        assert phrase not in text, f"forbidden claim found: {phrase!r}"
    assert "Not part of this work" in text
    assert "Submission to the official Claude Code Marketplace" in text


def test_no_hosted_saas_or_ocr_affirmative_claims():
    public_paths = [README, INDEX_HTML, INSTALL_GUIDE]
    public_copy = "\n".join(_read(p) for p in public_paths)

    forbidden_positive_claims = [
        "hosted SaaSとして利用できます",
        "hosted SaaS is available",
        "OCRに対応しています",
        "OCR is supported",
        "スキャンPDFに対応しています",
        "scanned PDFs are supported",
        "収益価格を算定します",
    ]
    for phrase in forbidden_positive_claims:
        assert phrase not in public_copy, f"forbidden affirmative claim found: {phrase!r}"


def test_bind_is_localhost_only_everywhere_mentioned():
    # "0.0.0.0" itself is allowed to appear in prose that explicitly says it
    # is NOT used (negation context); what must never appear is an actual
    # instruction to bind there.
    text = _read(INSTALL_GUIDE)
    assert "127.0.0.1" in text
    assert "--host 0.0.0.0" not in text
    assert "never exposed on `0.0.0.0`" in text or "not launch on `0.0.0.0`" in text
