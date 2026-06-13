"""dry-run mode tests (Issue #14).

--dry-run フラグで入力抽出と診断のみが実行され、
計算・成果物生成がスキップされることを検証する。
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
    d = tmp_path_factory.mktemp("dry_run_pdfs")
    return generate_sample_pdf(d / "simple.pdf", pattern="simple")


# ---------------------------------------------------------------------------
# CSV dry-run
# ---------------------------------------------------------------------------
def test_csv_dry_run_exit_zero(tmp_path):
    """CSV dry-run は exit 0 を返す。"""
    rc = run(ASSUMPTIONS, DUMMY_CSV, str(tmp_path / "out"), dry_run=True)
    assert rc == 0


def test_csv_dry_run_shows_diagnostics(tmp_path, capsys):
    """CSV dry-run で [抽出診断] が stdout に出る。"""
    run(ASSUMPTIONS, DUMMY_CSV, str(tmp_path / "out"), dry_run=True)
    out = capsys.readouterr().out
    assert "[抽出診断]" in out
    assert "CSV" in out
    assert "抽出区画数" in out


def test_csv_dry_run_no_output_files(tmp_path):
    """CSV dry-run で output files が生成されない。"""
    out_dir = tmp_path / "out"
    run(ASSUMPTIONS, DUMMY_CSV, str(out_dir), dry_run=True)
    assert not (out_dir / "revenue_analysis.xlsx").exists()
    assert not (out_dir / "missing_info.md").exists()
    assert not (out_dir / "extraction_log.json").exists()


def test_csv_dry_run_no_calc_output(tmp_path, capsys):
    """CSV dry-run で GPI / NOI 計算行が stdout に出ない。"""
    run(ASSUMPTIONS, DUMMY_CSV, str(tmp_path / "out"), dry_run=True)
    out = capsys.readouterr().out
    assert "潜在総収入" not in out
    assert "運営純収益" not in out
    # VALUE_LABEL は DISCLAIMER にも含まれるため、計算行の書式で確認する
    assert "収益試算値        :" not in out


def test_csv_dry_run_completion_message(tmp_path, capsys):
    """CSV dry-run でドライラン完了メッセージが出る。"""
    run(ASSUMPTIONS, DUMMY_CSV, str(tmp_path / "out"), dry_run=True)
    out = capsys.readouterr().out
    assert "ドライラン" in out
    assert "スキップ" in out


# ---------------------------------------------------------------------------
# PDF dry-run（成功系）
# ---------------------------------------------------------------------------
def test_pdf_dry_run_exit_zero(simple_pdf, tmp_path):
    """PDF dry-run（成功）は exit 0 を返す。"""
    rc = run(ASSUMPTIONS, DUMMY_CSV, str(tmp_path / "out"),
             rent_roll_pdf=str(simple_pdf), dry_run=True)
    assert rc == 0


def test_pdf_dry_run_shows_diagnostics(simple_pdf, tmp_path, capsys):
    """PDF dry-run で [抽出診断]・認識フィールド・抽出区画数が stdout に出る。"""
    run(ASSUMPTIONS, DUMMY_CSV, str(tmp_path / "out"),
        rent_roll_pdf=str(simple_pdf), dry_run=True)
    out = capsys.readouterr().out
    assert "[抽出診断]" in out
    assert "PDF" in out
    assert "認識フィールド" in out
    assert "抽出区画数" in out


def test_pdf_dry_run_no_output_files(simple_pdf, tmp_path):
    """PDF dry-run で output files が生成されない。"""
    out_dir = tmp_path / "out"
    run(ASSUMPTIONS, DUMMY_CSV, str(out_dir),
        rent_roll_pdf=str(simple_pdf), dry_run=True)
    assert not (out_dir / "revenue_analysis.xlsx").exists()
    assert not (out_dir / "missing_info.md").exists()
    assert not (out_dir / "extraction_log.json").exists()


def test_pdf_dry_run_no_calc_output(simple_pdf, tmp_path, capsys):
    """PDF dry-run で GPI / NOI 計算行が stdout に出ない。"""
    run(ASSUMPTIONS, DUMMY_CSV, str(tmp_path / "out"),
        rent_roll_pdf=str(simple_pdf), dry_run=True)
    out = capsys.readouterr().out
    assert "潜在総収入" not in out
    assert "運営純収益" not in out
    # VALUE_LABEL は DISCLAIMER にも含まれるため、計算行の書式で確認する
    assert "収益試算値        :" not in out


# ---------------------------------------------------------------------------
# PDF dry-run（safe failure 系）
# ---------------------------------------------------------------------------
def test_pdf_failure_dry_run_shows_diagnostics_stderr(tmp_path, capsys):
    """PDF safe failure + dry-run で [抽出診断] が stderr に出る。"""
    no_table_pdf = build_text_only_pdf(tmp_path / "no_table.pdf")
    with pytest.raises(RentRollExtractionError):
        run(ASSUMPTIONS, DUMMY_CSV, str(tmp_path / "out"),
            rent_roll_pdf=str(no_table_pdf), dry_run=True)
    err = capsys.readouterr().err
    assert "[抽出診断]" in err
    assert "失敗" in err
    assert "failure_reason" in err


def test_pdf_failure_dry_run_no_extraction_log(tmp_path, capsys):
    """PDF safe failure + dry-run で extraction_log.json が生成されない。"""
    no_table_pdf = build_text_only_pdf(tmp_path / "no_table2.pdf")
    out_dir = tmp_path / "out"
    with pytest.raises(RentRollExtractionError):
        run(ASSUMPTIONS, DUMMY_CSV, str(out_dir),
            rent_roll_pdf=str(no_table_pdf), dry_run=True)
    assert not (out_dir / "extraction_log.json").exists()


# ---------------------------------------------------------------------------
# 通常実行（dry_run=False / デフォルト）への影響なし
# ---------------------------------------------------------------------------
def test_normal_csv_still_generates_output_files(tmp_path):
    """通常実行（CSV）で output files が生成される（既存挙動維持）。"""
    out_dir = tmp_path / "out"
    rc = run(ASSUMPTIONS, DUMMY_CSV, str(out_dir))
    assert rc == 0
    assert (out_dir / "revenue_analysis.xlsx").exists()
    assert (out_dir / "missing_info.md").exists()
    assert (out_dir / "extraction_log.json").exists()


def test_normal_pdf_still_generates_output_files(simple_pdf, tmp_path):
    """通常実行（PDF）で output files が生成される（既存挙動維持）。"""
    out_dir = tmp_path / "out"
    rc = run(ASSUMPTIONS, DUMMY_CSV, str(out_dir), rent_roll_pdf=str(simple_pdf))
    assert rc == 0
    assert (out_dir / "revenue_analysis.xlsx").exists()
    assert (out_dir / "missing_info.md").exists()
    assert (out_dir / "extraction_log.json").exists()


def test_normal_csv_still_shows_calc_output(tmp_path, capsys):
    """通常実行（CSV）で GPI / NOI / 収益試算値が表示される（既存挙動維持）。"""
    run(ASSUMPTIONS, DUMMY_CSV, str(tmp_path / "out"))
    out = capsys.readouterr().out
    assert "潜在総収入" in out
    assert "運営純収益" in out
    assert "収益試算値" in out
