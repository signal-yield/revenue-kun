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

    def __init__(self, message: str, report: ExtractionReport | None = None) -> None:
        super().__init__(message)
        self.report = report


# ヘッダー文言（小文字化して部分一致）→ 内部キー のマッピング。
# 各エントリは (token, canonical_key)。先に書いたトークンが優先（first-match）。
# ルール:
#   - token は小文字・日本語・英語いずれも可（マッチ時に比較側を lower() するため）
#   - 長い・より具体的なトークンを短い・汎用トークンより前に置く
#   - fuzzy matching はしない（完全一致 / 部分文字列一致のみ）
#   - notes 列は現行の行処理では未使用だが、認識しておくことで #8 の接続口になる
_HEADER_KEYS: list[tuple[str, str]] = [
    # ── room（区画番号 / 号室 / unit / room）───────────────────────────
    ("部屋", "room"), ("号室", "room"), ("区画", "room"),
    ("unit", "room"), ("room", "room"),
    # ── use（用途 / 区分）──────────────────────────────────────────────
    ("用途", "use"), ("use", "use"), ("type", "use"),
    # ── area（専有面積 / ㎡ / Floor Area）──────────────────────────────
    ("面積", "area"), ("㎡", "area"), ("floor area", "area"), ("area", "area"),
    # ── rent（月額賃料 / 家賃 / Monthly Rent）──────────────────────────
    ("賃料", "rent"), ("家賃", "rent"), ("monthly rent", "rent"), ("rent", "rent"),
    # ── cam（共益費 / 管理費 / CAM / Service Charge）────────────────────
    ("共益", "cam"), ("管理費", "cam"), ("サービス料", "cam"),
    ("common_fee", "cam"), ("common fee", "cam"), ("service charge", "cam"),
    ("cam", "cam"), ("管理", "cam"),
    # ── status（入居状況 / 稼働 / Occupancy）────────────────────────────
    # Person/tenant-name columns (e.g. 入居者名) are pre-screened by
    # _resolve_header_key via _PERSON_NAME_DENY, so "入居" can remain as
    # a status alias for standalone headers such as "入居" or "入居/空室".
    ("ステータス", "status"),
    ("入居", "status"), ("空室", "status"), ("稼働", "status"), ("状況", "status"),
    ("occupancy", "status"), ("status", "status"),
    # ── notes（備考 / メモ / Remarks）── オプション列、現行処理では未使用
    ("備考", "notes"), ("メモ", "notes"), ("remarks", "notes"), ("notes", "notes"),
]

# これらの列が認識できなければ抽出を継続しない（必須列）
_REQUIRED_KEYS = {"room": "部屋番号", "rent": "月額賃料", "status": "入居状況"}

# room 列にマップされるヘッダートークン（繰り返しヘッダー行の判定に使う）
_ROOM_HEADER_TOKENS: frozenset[str] = frozenset(t for t, k in _HEADER_KEYS if k == "room")

# Column headers containing these substrings are person/tenant-name columns.
# They must not be mapped to 'status' even when they contain a status-adjacent
# token such as "入居". Checked by _resolve_header_key before alias lookup.
_PERSON_NAME_DENY: frozenset[str] = frozenset({"者名", "テナント名", "入居者"})

# Column headers containing these substrings are date-type columns (move-in date,
# contract dates, etc.). They must not be mapped to 'status' even when they contain
# a status-adjacent token such as "入居" (e.g. "入居日" contains "入居").
# Checked by _resolve_header_key alongside _PERSON_NAME_DENY.
_DATE_HEADER_DENY: frozenset[str] = frozenset({"入居日", "開始日", "満了日", "契約日"})

# Room-field values (after collapsing whitespace, lowercased) that identify a
# total / subtotal row. Matched as full string equality, not substring, to avoid
# accidentally dropping room numbers that happen to contain these characters.
_SUMMARY_ROW_LABELS: frozenset[str] = frozenset({"合計", "小計", "総計", "計", "total", "subtotal"})


@dataclass
class ExtractionReport:
    """抽出処理のメタ情報。extraction_log.json に記録する。"""

    pdf_name: str
    rows_extracted: int = 0           # データ行として抽出した件数
    cells_missing: int = 0            # 空欄（欠損）セル数
    pages: int = 0
    column_map: dict[str, int] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    failure_reason: str | None = None  # safe failure 時にセットされる


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
    """小見出し・繰り返しヘッダー行・集計行と判定される場合に True を返す。

    判定基準（いずれか一方）:
    1. 区画フィールドが括弧で始まる小見出し（例: 【1F区画】, [2F]）
    2. 区画フィールドがヘッダートークンを含み、かつ賃料列も非数値文字列である繰り返しヘッダー行
       ※ 賃料が空欄（None）の空室行は条件2の対象外とし、誤除外しない。
    3. 区画フィールドが既知の集計ラベル（合計・小計・総計・計・TOTAL 等）と完全一致する行
       ※ スペース除去・小文字化後に _SUMMARY_ROW_LABELS と照合する（部分一致しない）。
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

    # 3. 集計行（全角/半角スペースを除去して小文字化したあと既知のラベルと完全一致）
    room_normalized = re.sub(r'[\s　]+', '', room).lower()
    if room_normalized in _SUMMARY_ROW_LABELS:
        return True

    return False


def _resolve_header_key(cell: str | None) -> str | None:
    """ヘッダーセル1つを canonical key に変換する。認識できない場合は None。

    _HEADER_KEYS を先頭から走査し、token が cell（小文字化）に含まれる
    最初のエントリの key を返す（first-match）。
    fuzzy matching はしない。
    _PERSON_NAME_DENY / _DATE_HEADER_DENY に該当するヘッダーは status にマップしない。
    """
    c = (_clean(cell) or "").lower()
    if not c:
        return None
    is_non_status_col = (
        any(tok in c for tok in _PERSON_NAME_DENY)
        or any(tok in c for tok in _DATE_HEADER_DENY)
    )
    for token, key in _HEADER_KEYS:
        if key == "status" and is_non_status_col:
            continue
        if token in c:
            return key
    return None


def _build_column_map(header: list[str | None]) -> dict[str, int]:
    """ヘッダー行から「canonical key → 列インデックス」を作る。

    各列を _resolve_header_key() で解決し、同一 key の最初の列だけを登録する。
    """
    col_map: dict[str, int] = {}
    for idx, cell in enumerate(header):
        key = _resolve_header_key(cell)
        if key is not None and key not in col_map:
            col_map[key] = idx
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
                    report.failure_reason = (
                        f"PDF '{path.name}' のヘッダー行を認識できませんでした。"
                        "列名（部屋番号/月額賃料/入居状況 等）を確認してください。"
                    )
                    raise RentRollExtractionError(report.failure_reason, report=report)
                # 必須列の存在チェック（欠ければ明示的エラーで停止）
                missing_cols = [
                    label for key, label in _REQUIRED_KEYS.items() if key not in col_map
                ]
                if missing_cols:
                    cols_text = "、".join(missing_cols)
                    report.failure_reason = (
                        f"PDF '{path.name}' に必須列が見つかりません: "
                        f"{cols_text}。補完せず処理を停止します。"
                    )
                    raise RentRollExtractionError(report.failure_reason, report=report)
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

    # ── Post-extraction safe failure checks ─────────────────────────────────
    # Check 1: 全ページで extract_table() が None → テーブル未検出
    #   ※ ループ内の「ヘッダー行未認識」とは区別する（そちらはループ内で raise 済み）
    if not col_map:
        report.failure_reason = (
            "どのページからもレントロールのテーブルを検出できませんでした。"
            "text-based の単純な表形式PDFを使用してください（スキャンPDF・OCRは非対応）。"
        )
        raise RentRollExtractionError(
            f"PDF '{path.name}': {report.failure_reason}",
            report=report,
        )

    # Check 2: ヘッダーは認識できたがデータ行がゼロ（ヘッダーのみPDF）
    if report.rows_extracted == 0:
        report.failure_reason = (
            "ヘッダー行は認識しましたが、データ行を1件も抽出できませんでした。"
            "テーブルの内容（区画数・欠損行の割合）を確認してください。"
        )
        raise RentRollExtractionError(
            f"PDF '{path.name}': {report.failure_reason}",
            report=report,
        )

    # Check 3: 稼働区画が存在するが、月額賃料を数値として読み取れた行がゼロ
    #   空室のみで賃料が全欠損の場合は正常（GPI=0 は仕様通り）
    occupied_units = [u for u in units if u.is_occupied]
    if occupied_units and all(u.月額賃料_円 is None for u in occupied_units):
        report.failure_reason = (
            f"稼働区画が {len(occupied_units)} 件ありますが、"
            "いずれの月額賃料も数値として読み取れませんでした。"
            "賃料列の書式（円表記・カンマ区切り等）を確認してください。"
        )
        raise RentRollExtractionError(
            f"PDF '{path.name}': {report.failure_reason}",
            report=report,
        )

    return units, report
