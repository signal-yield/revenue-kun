"""レントロールPDFからの賃料情報抽出（Phase 2）。

単純な罫線付きの表PDFを対象とし、pdfplumber でテーブルを抽出する。
抽出するのは以下の項目（要件）:
  部屋番号 / 用途 / 面積 / 月額賃料 / 共益費 / 入居・空室

【方針】抽出できないセルは推測補完せず None とし、欠損として後段に渡す。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import pdfplumber

from .rent_roll import RentRollUnit


class RentRollExtractionError(Exception):
    """PDFから必須列を認識できない等、抽出を継続できない場合に送出する。"""


# ヘッダー文言（小文字化して部分一致）→ 内部キー のマッピング。
# 日本語の表記ゆれ・英語名に最小対応する。
_HEADER_KEYS: list[tuple[str, str]] = [
    # room（部屋番号 / 号室 / 区画 / unit / room）
    ("部屋", "room"), ("号室", "room"), ("区画", "room"),
    ("unit", "room"), ("room", "room"),
    # use（用途）
    ("用途", "use"), ("use", "use"), ("type", "use"),
    # area（面積 / area）
    ("面積", "area"), ("area", "area"),
    # rent（月額賃料 / 賃料 / rent）
    ("賃料", "rent"), ("rent", "rent"),
    # cam（共益費 / 管理費 / common_fee）
    ("共益", "cam"), ("管理費", "cam"),
    ("common_fee", "cam"), ("common fee", "cam"), ("管理", "cam"),
    # status（入居状況 / 入居 / 空室 / 稼働 / status）
    ("入居", "status"), ("空室", "status"), ("稼働", "status"),
    ("status", "status"), ("状況", "status"),
]

# これらの列が認識できなければ抽出を継続しない（必須列）
_REQUIRED_KEYS = {"room": "部屋番号", "rent": "月額賃料", "status": "入居状況"}

# room 列にマップされるヘッダートークン（繰り返しヘッダー行の判定に使う）
_ROOM_HEADER_TOKENS: frozenset[str] = frozenset(t for t, k in _HEADER_KEYS if k == "room")


@dataclass
class ExtractionReport:
    """抽出処理のメタ情報。extraction_log.json に記録する。"""

    pdf_name: str
    rows_extracted: int = 0           # データ行として抽出した件数
    cells_missing: int = 0            # 空欄（欠損）セル数
    pages: int = 0
    column_map: dict[str, int] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


def _clean(text: str | None) -> str | None:
    """セル文字列を正規化。空欄・ダッシュは None。"""
    if text is None:
        return None
    s = text.replace("\n", "").strip()
    if s in ("", "-", "—", "ー", "−", "‐", "/", "なし", "N/A"):
        return None
    return s


def _to_number(text: str | None) -> float | None:
    """金額・面積文字列を数値化。記号付き・カンマ込みに対応。失敗時 None。"""
    s = _clean(text)
    if s is None:
        return None
    # 数字・小数点以外を除去（円, ㎡, カンマ, 空白 等）
    cleaned = re.sub(r"[^\d.]", "", s)
    if cleaned in ("", "."):
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _normalize_status(text: str | None) -> str | None:
    """入居/空室 ステータスを正規化。"""
    s = _clean(text)
    if s is None:
        return None
    if any(k in s for k in ("入居", "稼働", "賃貸中", "使用中")):
        return "入居"
    if any(k in s for k in ("空室", "空き", "空き室", "募集")):
        return "空室"
    return s  # 不明な値はそのまま保持（補完しない）


def _is_non_data_row(room: str, raw: list[str | None], col_map: dict[str, int]) -> bool:
    """小見出し・繰り返しヘッダー行と判定される場合に True を返す。

    判定基準（いずれか一方）:
    1. 区画フィールドが括弧で始まる小見出し（例: 【1F区画】, [2F]）
    2. 区画フィールドがヘッダートークンを含み、かつ賃料列も非数値文字列である繰り返しヘッダー行
       ※ 賃料が空欄（None）の空室行は条件2の対象外とし、誤除外しない。
    """
    # 1. 括弧で始まる小見出し（全角【】・半角[]・全角（）・半角()）
    if re.match(r'^[【\[\(（]', room):
        return True

    # 2. 繰り返しヘッダー行
    #    区画フィールドにヘッダートークン（部屋・号室・unit・room 等）が含まれ、
    #    かつ賃料列が非空かつ非数値（ヘッダーラベル文字列）の場合に限定する。
    room_lower = room.lower()
    if any(tok in room_lower for tok in _ROOM_HEADER_TOKENS):
        rent_idx = col_map.get("rent")
        if rent_idx is not None and rent_idx < len(raw):
            rent_raw = _clean(raw[rent_idx])
            if rent_raw is not None and _to_number(rent_raw) is None:
                return True

    return False


def _build_column_map(header: list[str | None]) -> dict[str, int]:
    """ヘッダー行から「内部キー→列インデックス」を作る。表記ゆれ・英語名に対応。"""
    col_map: dict[str, int] = {}
    for idx, cell in enumerate(header):
        c = (_clean(cell) or "").lower()
        for token, key in _HEADER_KEYS:
            if token in c and key not in col_map:
                col_map[key] = idx
                break
    return col_map


def extract_rent_roll_from_pdf(
    path: str | Path,
) -> tuple[list[RentRollUnit], ExtractionReport]:
    """PDFからレントロールを抽出する。

    Returns:
        (units, report)
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"レントロールPDFが見つかりません: {path}")

    report = ExtractionReport(pdf_name=path.name)
    units: list[RentRollUnit] = []
    col_map: dict[str, int] = {}

    with pdfplumber.open(str(path)) as pdf:
        report.pages = len(pdf.pages)
        for page in pdf.pages:
            table = page.extract_table()
            if not table:
                continue

            start = 0
            # 先頭行をヘッダーとしてマッピングを構築
            if not col_map:
                col_map = _build_column_map(table[0])
                if not col_map:
                    raise RentRollExtractionError(
                        f"PDF '{path.name}' のヘッダー行を認識できませんでした。"
                        "列名（部屋番号/月額賃料/入居状況 等）を確認してください。"
                    )
                # 必須列の存在チェック（欠ければ明示的エラーで停止）
                missing_cols = [
                    label for key, label in _REQUIRED_KEYS.items() if key not in col_map
                ]
                if missing_cols:
                    raise RentRollExtractionError(
                        f"PDF '{path.name}' に必須列が見つかりません: "
                        f"{', '.join(missing_cols)}。補完せず処理を停止します。"
                    )
                report.column_map = col_map
                # 任意列が無い場合は注記（処理は継続）
                for key, label in (("area", "面積"), ("cam", "共益費"), ("use", "用途")):
                    if key not in col_map:
                        report.notes.append(f"任意列「{label}」が無いため当該項目は欠損として扱います。")
                start = 1

            for raw in table[start:]:
                # 完全な空行はスキップ
                if not any(_clean(c) for c in raw):
                    continue

                def get(key: str) -> str | None:
                    i = col_map.get(key)
                    if i is None or i >= len(raw):
                        return None
                    return raw[i]

                room = _clean(get("room"))
                if room is None:
                    # 部屋番号が無い行はデータ行とみなさない
                    continue
                if _is_non_data_row(room, raw, col_map):
                    report.notes.append(f"「{room}」行を小見出し・ヘッダーと判定し除外しました。")
                    continue

                area = _to_number(get("area"))
                rent = _to_number(get("rent"))
                cam = _to_number(get("cam"))
                status = _normalize_status(get("status"))
                use = _clean(get("use"))

                # 欠損セルのカウント（抽出対象6項目のうち空だったもの）
                for v in (use, area, rent, cam, status):
                    if v is None:
                        report.cells_missing += 1

                units.append(
                    RentRollUnit(
                        区画=room,
                        用途=use,
                        賃借人=None,           # PDFには借主名を含めない（合成データ方針）
                        専有面積_m2=area,
                        月額賃料_円=rent,
                        月額共益費_円=cam,
                        稼働状況=status,
                        契約満了日=None,        # 本PDFの抽出対象外
                    )
                )
                report.rows_extracted += 1

    return units, report
