"""E2Eテスト: 合成PDF3パターンを CLI 経由で実行し、出力ファイルと
extraction_log.json の固定スキーマを検証する。

  PDF → NOI整理 → 収益試算値 → missing_info / extraction_log
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from revenue_kun.cli import run
from revenue_kun.config import load_assumptions
from revenue_kun.missing import detect_missing
from revenue_kun.noi import compute_noi
from revenue_kun.pdf_extract import extract_rent_roll_from_pdf
from revenue_kun.rent_roll import load_rent_roll
from revenue_kun.sample_pdf import PATTERNS, generate_sample_pdf
from revenue_kun.valuation import direct_capitalization

ASSUMPTIONS = "assumptions.sample.yaml"
DUMMY_CSV = "data/dummy_rent_roll.csv"

# extraction_log の固定スキーマ（必須トップレベルキー）
REQUIRED_LOG_KEYS = {
    "input_files",
    "rent_roll_pdf",
    "extracted_units_count",
    "missing_required_count",
    "missing_optional_count",
    "missing_required_items",
    "missing_optional_items",
    "gpi",
    "noi",
    "indicated_value",
    "output_files",
    "executed_at",
}

# パターン別の期待値（assumptions.sample.yaml 前提で検算済み）
EXPECTED = {
    "simple": {
        "rows": 5, "cells_missing": 0, "missing": 2,
        "req": 0, "opt": 2, "gpi": 26016000, "noi": 17215200,
    },
    "missing_values": {
        "rows": 5, "cells_missing": 4, "missing": 5,
        "req": 0, "opt": 5, "gpi": 9816000, "noi": 1825200,
    },
    "different_columns": {
        "rows": 3, "cells_missing": 0, "missing": 2,
        "req": 0, "opt": 2, "gpi": 21780000, "noi": 13191000,
    },
}


@pytest.fixture(scope="module")
def pdfs(tmp_path_factory) -> dict[str, Path]:
    d = tmp_path_factory.mktemp("e2e_pdfs")
    return {name: generate_sample_pdf(d / f"{name}.pdf", pattern=name) for name in PATTERNS}


@pytest.mark.parametrize("pattern", list(PATTERNS))
def test_metrics_match_expected(pdfs, pattern):
    exp = EXPECTED[pattern]
    a = load_assumptions(ASSUMPTIONS)
    units, rep = extract_rent_roll_from_pdf(pdfs[pattern])
    miss = detect_missing(a, units, rent_roll_source=rep.pdf_name)
    noi = compute_noi(units, a)
    val = direct_capitalization(noi, a)

    assert rep.rows_extracted == exp["rows"]
    assert rep.cells_missing == exp["cells_missing"]
    assert len(miss) == exp["missing"]
    assert sum(1 for m in miss if m.required) == exp["req"]
    assert sum(1 for m in miss if not m.required) == exp["opt"]
    assert noi.gpi == exp["gpi"]
    assert noi.noi == exp["noi"]
    # 収益試算値 = 純収益 / 還元利回り（鑑定評価ではない）
    assert val.estimated_value == noi.net_income / a.cap_rate


@pytest.mark.parametrize("pattern", list(PATTERNS))
def test_extraction_log_fixed_schema(pdfs, pattern, tmp_path):
    out = tmp_path / pattern
    rc = run(ASSUMPTIONS, DUMMY_CSV, str(out), rent_roll_pdf=str(pdfs[pattern]))
    assert rc == 0

    missing_md = out / "missing_info.md"
    xlsx = out / "revenue_analysis.xlsx"
    log_path = out / "extraction_log.json"
    assert missing_md.exists() and xlsx.exists() and log_path.exists()

    log = json.loads(log_path.read_text(encoding="utf-8"))
    exp = EXPECTED[pattern]

    # 固定スキーマのキーが必ず存在する
    assert REQUIRED_LOG_KEYS <= set(log), f"欠けているキー: {REQUIRED_LOG_KEYS - set(log)}"

    assert log["extraction_method"] == "pdf"
    assert log["rent_roll_pdf"] == pdfs[pattern].name
    assert log["input_files"]["rent_roll"] == pdfs[pattern].name
    assert log["extracted_units_count"] == exp["rows"]
    assert log["missing_required_count"] == exp["req"]
    assert log["missing_optional_count"] == exp["opt"]
    assert len(log["missing_required_items"]) == exp["req"]
    assert len(log["missing_optional_items"]) == exp["opt"]
    assert log["gpi"] == exp["gpi"]
    assert log["noi"] == exp["noi"]
    assert log["indicated_value"] is not None
    # output_files に3つの出力先が記録される
    assert set(log["output_files"]) == {"missing_info", "revenue_analysis", "extraction_log"}
    # executed_at が ISO8601 文字列
    assert isinstance(log["executed_at"], str) and "T" in log["executed_at"]
    # PDF抽出の付加情報
    assert log["pdf_extraction"]["rows_extracted"] == exp["rows"]
    assert log["pdf_extraction"]["cells_missing"] == exp["cells_missing"]

    # missing_info.md: 欠損ありパターンでは欠損が明記され、免責が常に入る
    md = missing_md.read_text(encoding="utf-8")
    if pattern == "missing_values":
        assert "月額共益費" in md
        assert "想定（市場）賃料" in md
    assert "鑑定評価ではありません" in md


def test_required_cell_missing_excludes_row_and_logs(tmp_path):
    """必須セル欠損（CSV 区画302: 稼働だが賃料なし）は行を除外し、
    missing_required として記録される（計算は停止しない）。"""
    out = tmp_path / "csv"
    rc = run(ASSUMPTIONS, DUMMY_CSV, str(out))  # CSV経路
    assert rc == 0
    log = json.loads((out / "extraction_log.json").read_text(encoding="utf-8"))
    assert log["rent_roll_pdf"] is None
    # 稼働区画の賃料欠損（必須セル）が1件以上 required として記録される
    assert log["missing_required_count"] >= 1
    rents = [m for m in log["missing_required_items"] if m["field"] == "月額賃料"]
    assert rents, "必須セル欠損（月額賃料）が記録されていない"
    # それでも収益試算値は算定される（行除外で継続）
    assert log["indicated_value"] is not None
