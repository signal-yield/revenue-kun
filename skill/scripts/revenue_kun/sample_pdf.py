"""完全合成データのレントロールPDFを生成する（Phase 2.1 / 3パターン）。

【重要】
  - ここで使う物件名・部屋・賃料・面積は **すべて架空の合成データ** です。
  - 実在の物件・借主・賃料とは一切関係ありません。
  - 一部セルは空欄にし、欠損検出の動作を確認できるようにしています。

パターン:
  - simple            : 全区画が稼働・全項目あり（欠損なしの基準ケース）
  - missing_values    : 任意項目（共益費・面積）の欠損と空室を含むケース
  - different_columns : 列名ゆれ（号室/賃料/管理費/area/status 等）のケース

PDFは単純な罫線付きの表（1ページ）とし、pdfplumber で抽出しやすくしています。
"""
from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

_FONT = "HeiseiKakuGo-W5"  # reportlab 同梱の日本語CIDフォント

# 後方互換（旧コード/テスト用）: 既定ヘッダー
HEADERS = ["部屋番号", "用途", "面積(㎡)", "月額賃料(円)", "共益費(円)", "入居/空室"]

# 空文字 "" は「PDF上に記載がない（欠損）」を意味する。

# --- パターン1: simple（欠損なし・全稼働） ------------------------------
_SIMPLE_HEADERS = ["部屋番号", "用途", "面積(㎡)", "月額賃料(円)", "共益費(円)", "入居/空室"]
_SIMPLE_ROWS = [
    ["101", "事務所", "100.0", "500,000", "50,000", "入居"],
    ["102", "事務所", "100.0", "480,000", "48,000", "入居"],
    ["201", "店舗", "120.0", "600,000", "60,000", "入居"],
    ["202", "住宅", "60.0", "200,000", "15,000", "入居"],
    ["301", "住宅", "60.0", "200,000", "15,000", "入居"],
]

# --- パターン2: missing_values（任意項目の欠損＋空室） ------------------
_MISSING_HEADERS = ["部屋番号", "用途", "面積(㎡)", "月額賃料(円)", "共益費(円)", "入居/空室"]
_MISSING_ROWS = [
    ["A101", "住宅", "42.5", "138,000", "8,000", "入居"],
    ["A102", "住宅", "42.5", "168,000", "", "入居"],     # 共益費（任意）欠損 → 0扱い
    ["A103", "住宅", "", "150,000", "9,000", "入居"],     # 面積（任意）欠損
    ["A201", "住宅", "55.0", "", "", "空室"],             # 空室（賃料記載なし＝想定賃料欠損）
    ["B101", "店舗", "88.0", "320,000", "25,000", "入居"],
]

# --- パターン3: different_columns（列名ゆれ／英語ヘッダー） --------------
_DIFFCOL_HEADERS = ["unit", "用途", "area", "rent", "common_fee", "status"]
_DIFFCOL_ROWS = [
    ["R-1", "事務所", "100", "500,000", "50,000", "入居"],
    ["R-2", "事務所", "100", "450,000", "45,000", "入居"],
    ["R-3", "店舗", "150", "700,000", "70,000", "入居"],
]

PATTERNS: dict[str, dict] = {
    "simple": {"headers": _SIMPLE_HEADERS, "rows": _SIMPLE_ROWS},
    "missing_values": {"headers": _MISSING_HEADERS, "rows": _MISSING_ROWS},
    "different_columns": {"headers": _DIFFCOL_HEADERS, "rows": _DIFFCOL_ROWS},
}

# 後方互換: 旧テストが参照していた SYNTHETIC_ROWS
SYNTHETIC_ROWS = _MISSING_ROWS


def pattern_for_filename(path: str | Path) -> str:
    """出力ファイル名からパターンを推測する。既定は simple。"""
    name = Path(path).stem.lower()
    if "different_columns" in name or "diffcol" in name:
        return "different_columns"
    if "missing" in name:
        return "missing_values"
    return "simple"


def build_pdf(path: str | Path, headers: list[str], rows: list[list[str]]) -> Path:
    """任意のヘッダー・行データから罫線付き表PDFを生成する（汎用ビルダ）。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    pdfmetrics.registerFont(UnicodeCIDFont(_FONT))

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "JPTitle", parent=styles["Title"], fontName=_FONT, fontSize=14
    )
    body_style = ParagraphStyle(
        "JPBody", parent=styles["Normal"], fontName=_FONT, fontSize=8, leading=11
    )

    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
    )

    elems = [
        Paragraph("レントロール（賃貸借明細表）", title_style),
        Spacer(1, 4 * mm),
        Paragraph(
            "物件名：サンプル・レジデンス（架空）　／　"
            "本表は完全合成データであり、実在の物件・借主・賃料とは一切関係ありません。",
            body_style,
        ),
        Spacer(1, 4 * mm),
    ]

    data = [headers] + rows
    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), _FONT),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#305496")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (2, 1), (-2, -1), "RIGHT"),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF2FA")]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elems.append(table)
    elems.append(Spacer(1, 6 * mm))
    elems.append(
        Paragraph(
            "（注）空欄のセルは原資料に記載がないことを示します。本ツールは欠損を推測補完しません。",
            body_style,
        )
    )

    doc.build(elems)
    return path


def build_text_only_pdf(path: str | Path) -> Path:
    """テーブルを含まないテキストのみのPDFを生成する（safe failure テスト用）。

    pdfplumber の extract_table() がテーブルを検出できないケースを再現する。
    reportlab の Paragraph 要素は罫線を持たないため、テーブルとして認識されない。
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pdfmetrics.registerFont(UnicodeCIDFont(_FONT))

    styles = getSampleStyleSheet()
    body_style = ParagraphStyle(
        "JPBodyText", parent=styles["Normal"], fontName=_FONT, fontSize=10, leading=14
    )
    doc = SimpleDocTemplate(str(path), pagesize=A4)
    doc.build([
        Paragraph("このPDFにはテーブルが含まれていません。", body_style),
        Paragraph("賃料情報は表形式で記録されていないため、本ツールで抽出できません。", body_style),
    ])
    return path


def generate_sample_pdf(path: str | Path, pattern: str | None = None) -> Path:
    """合成レントロールPDFを生成して保存する。

    pattern 未指定の場合は出力ファイル名から推測する（既定: simple）。
    """
    if pattern is None:
        pattern = pattern_for_filename(path)
    if pattern not in PATTERNS:
        raise ValueError(
            f"未知のパターン: {pattern}（有効: {', '.join(PATTERNS)}）"
        )
    spec = PATTERNS[pattern]
    return build_pdf(path, spec["headers"], spec["rows"])


if __name__ == "__main__":
    # 通常は scripts/make_sample_pdf.py から呼び出すこと
    out = Path(__file__).resolve().parents[2] / "data" / "sample_rentroll_simple.pdf"
    generate_sample_pdf(out)
    print(f"生成しました: {out}")
