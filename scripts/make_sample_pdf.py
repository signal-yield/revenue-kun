"""完全合成データのレントロールPDFを生成するスクリプト。

実行例:
  python scripts/make_sample_pdf.py --output data/sample_rentroll.pdf

生成されるPDFの物件名・部屋・賃料・面積はすべて架空の合成データです。
実在の物件・借主・賃料とは一切関係ありません。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# scripts/ から src/ のパッケージを import できるようにする
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from revenue_kun.sample_pdf import PATTERNS, generate_sample_pdf, pattern_for_filename


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="make_sample_pdf",
        description="合成レントロールPDFを生成する（simple / missing_values / different_columns）",
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "data" / "sample_rentroll_simple.pdf"),
        help="出力PDFのパス",
    )
    parser.add_argument(
        "--pattern",
        choices=sorted(PATTERNS),
        default=None,
        help="生成パターン（未指定なら出力ファイル名から推測）",
    )
    args = parser.parse_args(argv)

    pattern = args.pattern or pattern_for_filename(args.output)
    out = generate_sample_pdf(args.output, pattern=pattern)
    print(f"合成レントロールPDFを生成しました: {out}（pattern={pattern}）")
    print("※ 物件名・部屋・賃料・面積はすべて架空の合成データです。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
