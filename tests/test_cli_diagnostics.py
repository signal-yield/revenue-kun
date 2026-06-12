"""CLI diagnostics summary tests (Issue #13).

extraction diagnostics summary が CLI 出力に含まれることを検証する。
CSV 正常系・PDF 正常系・PDF safe failure 系の3ケースをカバーする。
"""
from __future__ import annotations

import pytest

from revenue_kun.cli import run
from revenue_kun.pdf_extract import RentRollExtractionError
from revenue_kun.sample_pdf import build_text_only_pdf, generate_sample_pdf

ASSUMPTIONS = "assumptions.sample.yaml"
DUMMY_CSV = "data/dummy_rent_roll.csv"


@pytest.fixture(scope="module")
def simple_pdf(tmp_path_factory):
    d = tmp_path_factory.mktemp("diag_pdfs")
    return generate_sample_pdf(d / "simple.pdf", pattern="simple")


# ---------------------------------------------------------------------------
# CSV 正常系
# ---------------------------------------------------------------------------
def test_csv_diagnostics_stdout(tmp_path, capsys):
    """CSV 正常系で [抽出診断] が stdout に出力される。"""
    rc = run(ASSUMPTIONS, DUMMY_CSV, str(tmp_path / "out"))
    assert rc == 0
    out = capsys.readouterr().out
    assert "[抽出診断]" in out
    assert "CSV" in out
    assert "抽出区画数" in out


def test_csv_diagnostics_no_fields_line(tmp_path, capsys):
    """CSV 経路では '認識フィールド' 行は出力されない（列マップなし）。"""
    run(ASSUMPTIONS, DUMMY_CSV, str(tmp_path / "out"))
    out = capsys.readouterr().out
    assert "認識フィールド" not in out


# ---------------------------------------------------------------------------
# PDF 正常系
# ---------------------------------------------------------------------------
def test_pdf_diagnostics_stdout(simple_pdf, tmp_path, capsys):
    """PDF 正常系で [抽出診断]・認識フィールド・抽出区画数が stdout に出る。"""
    rc = run(ASSUMPTIONS, DUMMY_CSV, str(tmp_path / "out"), rent_roll_pdf=str(simple_pdf))
    assert rc == 0
    out = capsys.readouterr().out
    assert "[抽出診断]" in out
    assert "PDF" in out
    assert "認識フィールド" in out
    assert "抽出区画数" in out


def test_pdf_diagnostics_fields_are_canonical(simple_pdf, tmp_path, capsys):
    """認識フィールドは canonical key（room, rent 等）で表示される。"""
    run(ASSUMPTIONS, DUMMY_CSV, str(tmp_path / "out"), rent_roll_pdf=str(simple_pdf))
    out = capsys.readouterr().out
    # simple パターンは room/rent/status を必ず含む
    assert "room" in out
    assert "rent" in out
    assert "status" in out


# ---------------------------------------------------------------------------
# PDF safe failure 系
# ---------------------------------------------------------------------------
def test_pdf_failure_diagnostics_stderr(tmp_path, capsys):
    """テーブルなし PDF は safe failure になり、[抽出診断] が stderr に出力される。"""
    no_table_pdf = build_text_only_pdf(tmp_path / "no_table.pdf")
    with pytest.raises(RentRollExtractionError):
        run(ASSUMPTIONS, DUMMY_CSV, str(tmp_path / "out"), rent_roll_pdf=str(no_table_pdf))
    err = capsys.readouterr().err
    assert "[抽出診断]" in err
    assert "PDF" in err
    assert "失敗" in err
    assert "failure_reason" in err


def test_pdf_failure_diagnostics_not_stdout(tmp_path, capsys):
    """safe failure の診断は stdout には出ない（stderr のみ）。"""
    no_table_pdf = build_text_only_pdf(tmp_path / "no_table2.pdf")
    with pytest.raises(RentRollExtractionError):
        run(ASSUMPTIONS, DUMMY_CSV, str(tmp_path / "out"), rent_roll_pdf=str(no_table_pdf))
    captured = capsys.readouterr()
    assert "[抽出診断]" not in captured.out
    assert "[抽出診断]" in captured.err


def test_pdf_failure_machine_readable_failure_reason_unchanged(tmp_path, capsys):
    """failure_reason は extraction_log.json に machine-readable で記録される（互換維持）。"""
    import json
    no_table_pdf = build_text_only_pdf(tmp_path / "no_table3.pdf")
    out_dir = tmp_path / "out"
    with pytest.raises(RentRollExtractionError):
        run(ASSUMPTIONS, DUMMY_CSV, str(out_dir), rent_roll_pdf=str(no_table_pdf))
    log = json.loads((out_dir / "extraction_log.json").read_text(encoding="utf-8"))
    assert log["failure"] is True
    assert log["failure_reason"]  # machine-readable value は空でない
