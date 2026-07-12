"""収益還元クン (revenue-kun) CLI ロジック。

エントリポイントは `src/main.py`。実行例:
  python src/main.py --assumptions assumptions.sample.yaml --output ./output
  python src/main.py --assumptions assumptions.sample.yaml --rent-roll-pdf data/sample_rentroll.pdf --output ./output
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import DISCLAIMER, VALUE_LABEL, __version__
from .config import AssumptionsError, load_assumptions, validate_assumptions
from .missing import detect_missing
from .noi import compute_noi
from .outputs import (
    write_excel,
    write_extraction_failure_log,
    write_extraction_log,
    write_missing_info,
)
from .excel_output import DirectCapRow, write_direct_cap_workbook
from .pdf_extract import RentRollExtractionError, extract_rent_roll_from_pdf
from .rent_roll import load_rent_roll
from .sensitivity import build_sensitivity
from .valuation import direct_capitalization

# src/revenue_kun/cli.py → parents[2] = プロジェクトルート
ROOT = Path(__file__).resolve().parents[2]


def _yen(value: float | None) -> str:
    return "（算定不能）" if value is None else f"{value:,.0f} 円"


def _print_diagnostics_summary(
    *,
    input_type: str,
    units: int | None = None,
    column_map: dict | None = None,
    failure: bool = False,
    failure_reason: str | None = None,
) -> None:
    """抽出診断サマリーを出力する。failure=True のときは stderr へ出力する。"""
    out = sys.stderr if failure else sys.stdout
    print("[抽出診断]", file=out)
    print(f"  入力形式       : {input_type}", file=out)
    if column_map:
        fields = ", ".join(sorted(column_map.keys()))
        print(f"  認識フィールド  : {fields}", file=out)
    if failure:
        print("  抽出結果       : 失敗", file=out)
        if failure_reason:
            print(f"  failure_reason : {failure_reason}", file=out)
    else:
        if units is not None:
            print(f"  抽出区画数     : {units}", file=out)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="revenue-kun",
        description="収益還元クン: 直接還元法による収益試算ツール（鑑定評価ではありません）",
    )
    p.add_argument("--assumptions", default=str(ROOT / "assumptions.sample.yaml"),
                   help="前提条件YAMLのパス")
    p.add_argument("--rent-roll", default=str(ROOT / "data" / "dummy_rent_roll.csv"),
                   help="レントロールCSVのパス（--rent-roll-pdf 未指定時に使用）")
    p.add_argument("--rent-roll-pdf", default=None,
                   help="レントロールPDFのパス（指定するとPDFから抽出する）")
    p.add_argument("--output", "--out", dest="output", default=str(ROOT / "output"),
                   help="出力ディレクトリ")
    p.add_argument("--dry-run", action="store_true", default=False,
                   help="入力抽出と診断のみを実行し、計算・成果物生成は行わない")
    p.add_argument("--excel-output", dest="excel_output", default=None,
                   help="直接還元法Excelワークブックの出力パス（.xlsx）")
    p.add_argument("--version", action="version", version=f"revenue-kun {__version__}")
    return p


def run(
    assumptions_path: str,
    rent_roll_path: str,
    out_dir: str,
    rent_roll_pdf: str | None = None,
    dry_run: bool = False,
    excel_output_path: str | None = None,
) -> int:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    use_pdf = rent_roll_pdf is not None
    mode = "Phase 2 / PDF抽出" if use_pdf else "Phase 1 / ダミーCSV"
    if dry_run:
        mode += " / ドライラン"
    print("=" * 64)
    print(f"  収益還元クン v{__version__}  （{mode}）")
    print("  " + DISCLAIMER)
    print("=" * 64)

    # 1. 入力読み込み＋検証（不正値なら計算を継続しない）
    assumptions = load_assumptions(assumptions_path)
    validate_assumptions(assumptions)

    extraction_method = "dummy"
    phase = "Phase 1 (dummy CSV)"
    extraction_meta: dict = {}
    if use_pdf:
        try:
            units, report = extract_rent_roll_from_pdf(rent_roll_pdf)
        except RentRollExtractionError as exc:
            _print_diagnostics_summary(
                input_type="PDF",
                failure=True,
                failure_reason=exc.report.failure_reason if exc.report else str(exc),
            )
            if not dry_run:
                write_extraction_failure_log(
                    out / "extraction_log.json",
                    pdf_name=Path(rent_roll_pdf).name,
                    failure_reason=str(exc),
                    rows_extracted=exc.report.rows_extracted if exc.report else 0,
                    pages=exc.report.pages if exc.report else 0,
                    executed_at=datetime.now(timezone.utc).isoformat(),
                )
            raise
        extraction_method = "pdf"
        phase = "Phase 2 (PDF extraction)"
        extraction_meta = {
            "pdf_name": report.pdf_name,
            "pages": report.pages,
            "rows_extracted": report.rows_extracted,
            "cells_missing": report.cells_missing,
            "column_map": report.column_map,
            "notes": report.notes,
            "optional_income_found": report.optional_income_found,
        }
        rr_source = report.pdf_name
        print(f"PDF抽出: {report.pdf_name} から {report.rows_extracted} 区画を抽出しました"
              f"（欠損セル {report.cells_missing} 件）。")
        for n in report.notes:
            print(f"  [注記] {n}")
        if report.optional_income_found:
            for oi_key in report.optional_income_found:
                print(
                    f"  [付帯収入] {oi_key} 列を抽出しました → "
                    "経常的な付帯収入として direct_cap.xlsx の両計算シートへ自動算入します。"
                )
            if assumptions.optional_income.include_in_gpi or assumptions.optional_income.columns:
                print(
                    "  [注記] assumptions.yaml の optional_income 設定は非推奨です"
                    "（v0.5.2以降、付帯収入は選択によらず自動算入されます）。"
                )
        _print_diagnostics_summary(
            input_type="PDF",
            units=report.rows_extracted,
            column_map=report.column_map,
        )
    else:
        units = load_rent_roll(rent_roll_path)
        rr_source = Path(rent_roll_path).name
        print(f"レントロール: {len(units)} 区画を読み込みました。")
        _print_diagnostics_summary(input_type="CSV", units=len(units))

    if dry_run:
        print("[ドライラン] 入力抽出と診断を完了しました。計算・成果物生成はスキップしました。")
        print("=" * 64)
        return 0

    # 2. 欠損検出（補完しない）
    missing = detect_missing(assumptions, units, rent_roll_source=rr_source)
    n_required = sum(1 for m in missing if m.required)
    n_optional = len(missing) - n_required
    print(f"欠損項目: {len(missing)} 件を検出しました"
          f"（必須 {n_required} / 任意 {n_optional}、補完していません）。")

    # 3. NOI 計算
    noi = compute_noi(units, assumptions)
    print(f"  潜在総収入(GPI)   : {_yen(noi.gpi)}")
    print(f"  有効総収入(EGI)   : {_yen(noi.egi)}")
    print(f"  運営純収益(NOI)   : {_yen(noi.noi)}")
    print(f"  純収益(還元対象)  : {_yen(noi.net_income)}")

    # 4. 直接還元法
    valuation = direct_capitalization(noi, assumptions)
    print(f"  {VALUE_LABEL}        : {_yen(valuation.estimated_value)}")

    # 5. 感応度分析
    sensitivity = build_sensitivity(noi, assumptions)
    if sensitivity is None:
        print("  感応度分析        : 還元利回り未設定のため実施せず")

    # 警告表示
    for w in noi.warnings:
        print(f"  [警告] {w}")

    # 6-9. 出力
    missing_path = out / "missing_info.md"
    xlsx_path = out / "revenue_analysis.xlsx"
    log_path = out / "extraction_log.json"

    input_files = {
        "assumptions": str(Path(assumptions_path).name),
        "rent_roll": rr_source,
    }
    output_files = {
        "missing_info": str(missing_path),
        "revenue_analysis": str(xlsx_path),
        "extraction_log": str(log_path),
    }
    executed_at = datetime.now(timezone.utc).isoformat()

    write_missing_info(missing_path, missing)
    write_excel(xlsx_path, assumptions, units, noi, valuation, sensitivity, missing)
    write_extraction_log(
        log_path, assumptions, units, missing, noi, valuation,
        input_files=input_files,
        rent_roll_pdf=(rr_source if use_pdf else None),
        output_files=output_files,
        executed_at=executed_at,
        extraction_method=extraction_method,
        phase=phase,
        pdf_extraction=extraction_meta,
    )

    # 10. 直接還元法 Excel ワークブック（--excel-output 指定時のみ）
    if excel_output_path is not None:
        dc_rows = [DirectCapRow.from_rent_roll_unit(u) for u in units]
        write_direct_cap_workbook(excel_output_path, dc_rows, oi_config=assumptions.optional_income)

    print("-" * 64)
    print("出力ファイル:")
    print(f"  - {missing_path}")
    print(f"  - {xlsx_path}")
    print(f"  - {log_path}")
    if excel_output_path is not None:
        print(f"  - {excel_output_path}")
    print("=" * 64)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return run(args.assumptions, args.rent_roll, args.output,
                   rent_roll_pdf=args.rent_roll_pdf,
                   dry_run=args.dry_run,
                   excel_output_path=args.excel_output)
    except OSError as e:
        print(f"[エラー] {e}", file=sys.stderr)
        return 1
    except RentRollExtractionError as e:
        print(f"[抽出エラー] {e}", file=sys.stderr)
        return 2
    except AssumptionsError as e:
        print(f"[前提条件エラー] {e}", file=sys.stderr)
        return 3
