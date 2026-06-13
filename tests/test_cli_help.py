"""CLI help text tests (Issue #15).

--help 出力に期待するオプションが含まれることを検証する。
"""
from __future__ import annotations

import pytest

from revenue_kun.cli import build_parser


def test_help_includes_dry_run(capsys):
    """--help に --dry-run が含まれる。"""
    with pytest.raises(SystemExit):
        build_parser().parse_args(["--help"])
    out = capsys.readouterr().out
    assert "--dry-run" in out


def test_help_dry_run_description(capsys):
    """--dry-run の説明が help に含まれる。"""
    with pytest.raises(SystemExit):
        build_parser().parse_args(["--help"])
    out = capsys.readouterr().out
    assert "計算" in out or "診断" in out  # help text の一部が出ている
