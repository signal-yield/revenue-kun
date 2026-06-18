"""Issue #21 評価用 合成リアル風レントロールPDF生成スクリプト。

生成する PDF の特徴:
  - タイトルブロックあり（物件名・作成日）
  - 実務でよく見る列名バリエーション
    号室 / 用途区分 / 面積(㎡) / 賃料（税抜）/ 管理費 / 入居状況
  - 8区画（稼働6・空室2）
  - 末尾に合計行（「合計」ラベル）→ summary row フィルタのテスト
  - すべて架空データ。実在の物件・借主・賃料とは無関係。

使い方:
  python scripts/make_issue21_sample.py --output samples/private/issue21_sample_a.pdf
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

_FONT = "HeiseiKakuGo-W5"

_HEADERS = ["号室", "用途区分", "面積(㎡)", "賃料（税抜）", "管理費", "入居状況"]

_ROWS = [
    ["101", "事務所",   "98.5",  "480,000", "48,000", "入居中"],
    ["102", "事務所",   "98.5",  "460,000", "46,000", "入居中"],
    ["103", "事務所",   "98.5",  "",        "",       "空室"],
    ["201", "店舗",     "145.0", "720,000", "72,000", "入居中"],
    ["202", "店舗",     "145.0", "680,000", "68,000", "入居中"],
    ["301", "住宅",     "55.2",  "165,000", "10,000", "入居中"],
    ["302", "住宅",     "55.2",  "158,000", "10,000", "入居中"],
    ["303", "住宅",     "55.2",  "",        "",       "空室"],
    ["合計", "",        "",      "2,663,000", "254,000", ""],  # summary row
]


def generate(output: Path) -> Path:
    pdfmetrics.registerFont(UnicodeCIDFont(_FONT))
    output.parent.mkdir(parents=True, exist_ok=True)

    style_title = ParagraphStyle(
        "title", fontName=_FONT, fontSize=14, leading=20, spaceAfter=4
    )
    style_sub = ParagraphStyle(
        "sub", fontName=_FONT, fontSize=9, leading=14, spaceAfter=2, textColor=colors.grey
    )

    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    table_data = [_HEADERS] + _ROWS
    col_widths = [22 * mm, 28 * mm, 24 * mm, 34 * mm, 28 * mm, 24 * mm]

    tbl = Table(table_data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("FONTNAME",    (0, 0), (-1, -1), _FONT),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#D9E1F2")),
        ("TEXTCOLOR",   (0, 0), (-1, 0), colors.black),
        ("FONTSIZE",    (0, 0), (-1, 0), 9),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("ALIGN",       (3, 1), (4, -1), "RIGHT"),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#F5F5F5")]),
        ("BACKGROUND",  (0, -1), (-1, -1), colors.HexColor("#EEF0F4")),
        ("FONTNAME",    (0, -1), (-1, -1), _FONT),
        ("TOPPADDING",  (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))

    story = [
        Paragraph("桜ヶ丘ビル　レントロール", style_title),
        Paragraph("作成日：2026年6月16日　　※ 本資料はすべて架空の合成データです", style_sub),
        Spacer(1, 6 * mm),
        tbl,
    ]
    doc.build(story)
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Issue #21 評価用 合成リアル風レントロールPDF生成")
    parser.add_argument(
        "--output",
        default=str(ROOT / "samples" / "private" / "issue21_sample_a.pdf"),
    )
    args = parser.parse_args(argv)
    out = generate(Path(args.output))
    print(f"生成完了: {out}")
    print("※ 物件名・部屋・賃料はすべて架空の合成データです。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
