"""PDF抽出の堅牢化テスト（Phase 2.1 / 3パターン＋列名ゆれ＋必須列欠落）。"""
from __future__ import annotations

from pathlib import Path

import pytest

from revenue_kun.pdf_extract import (
    RentRollExtractionError,
    _resolve_header_key,
    extract_rent_roll_from_pdf,
)
from revenue_kun.sample_pdf import PATTERNS, build_pdf, build_text_only_pdf, generate_sample_pdf


@pytest.fixture(scope="module")
def pdfs(tmp_path_factory) -> dict[str, Path]:
    d = tmp_path_factory.mktemp("pdfs")
    out = {}
    for name in PATTERNS:
        p = d / f"sample_rentroll_{name}.pdf"
        out[name] = generate_sample_pdf(p, pattern=name)
    return out


# --- パターン別の基本確認 ------------------------------------------------
def test_simple_no_missing(pdfs):
    units, rep = extract_rent_roll_from_pdf(pdfs["simple"])
    assert rep.rows_extracted == 5
    assert rep.cells_missing == 0
    assert all(u.is_occupied for u in units)
    # 全件、賃料・共益費が揃っている
    assert all(u.月額賃料_円 is not None and u.月額共益費_円 is not None for u in units)


def test_missing_values_not_autofilled(pdfs):
    """欠損は推測補完されず None のまま保持される。"""
    units, rep = extract_rent_roll_from_pdf(pdfs["missing_values"])
    by = {u.区画: u for u in units}
    assert rep.rows_extracted == 5
    # A102: 共益費（任意）欠損 → None のまま、収入計算では 0 扱い
    assert by["A102"].月額共益費_円 is None
    assert by["A102"].cam_treated_as_zero is True
    assert by["A102"].月額収入_円 == 168000  # 168,000 + 0
    # A103: 面積（任意）欠損
    assert by["A103"].専有面積_m2 is None
    # A201: 空室（賃料欠損は補完しない）
    assert not by["A201"].is_occupied
    assert by["A201"].月額賃料_円 is None
    assert rep.cells_missing == 4  # A102共益費, A103面積, A201賃料, A201共益費


def test_different_columns_mapped(pdfs):
    """列名ゆれ（unit/賃料/管理費/area/status 等）でも正しくマップされる。"""
    units, rep = extract_rent_roll_from_pdf(pdfs["different_columns"])
    assert rep.rows_extracted == 3
    # 必須＋任意列がすべて認識されている
    for key in ("room", "rent", "status", "use", "area", "cam"):
        assert key in rep.column_map, f"{key} がマップされていない"
    r1 = next(u for u in units if u.区画 == "R-1")
    assert r1.月額賃料_円 == 500000
    assert r1.月額共益費_円 == 50000
    assert r1.専有面積_m2 == 100
    assert r1.is_occupied


# --- 列名ゆれの最小対応（要件4） ----------------------------------------
@pytest.mark.parametrize(
    "headers",
    [
        ["部屋番号", "用途", "面積(㎡)", "月額賃料(円)", "共益費(円)", "入居/空室"],
        ["号室", "用途", "面積", "賃料", "管理費", "入居状況"],
        ["unit", "type", "area", "rent", "common_fee", "status"],
    ],
)
def test_header_variants_recognized(tmp_path, headers):
    p = tmp_path / "v.pdf"
    build_pdf(p, headers, [["X-1", "事務所", "100", "300,000", "30,000", "入居"]])
    units, rep = extract_rent_roll_from_pdf(p)
    assert {"room", "rent", "status"} <= set(rep.column_map)
    assert units[0].月額賃料_円 == 300000
    assert units[0].月額共益費_円 == 30000


# --- 必須列欠落は明示的エラーで停止（要件3） ----------------------------
def test_missing_required_column_raises(tmp_path):
    p = tmp_path / "norent.pdf"
    # 月額賃料（必須）列が無い
    build_pdf(p, ["部屋番号", "用途", "面積(㎡)", "共益費(円)", "入居/空室"],
              [["101", "事務所", "100", "50,000", "入居"]])
    with pytest.raises(RentRollExtractionError) as ei:
        extract_rent_roll_from_pdf(p)
    assert "月額賃料" in str(ei.value)


def test_unrecognized_header_raises(tmp_path):
    p = tmp_path / "junk.pdf"
    build_pdf(p, ["aaa", "bbb", "ccc"], [["1", "2", "3"]])
    with pytest.raises(RentRollExtractionError):
        extract_rent_roll_from_pdf(p)


# --- sub-header / repeated-header の除外（Issue #6） ----------------------
def test_subheader_rows_excluded(tmp_path):
    """【1F区画】のような括弧小見出し行は除外され、実データ行のみ抽出される。"""
    p = tmp_path / "subheader.pdf"
    headers = ["部屋番号", "用途", "面積(㎡)", "月額賃料(円)", "共益費(円)", "入居/空室"]
    rows = [
        ["【1F区画】", "", "", "", "", ""],        # 括弧小見出し → 除外
        ["101", "事務所", "100.0", "300,000", "30,000", "入居"],
        ["102", "住宅",   "60.0",  "150,000", "10,000", "入居"],
        ["【2F区画】", "", "", "", "", ""],        # 括弧小見出し → 除外
        ["201", "住宅",   "55.0",  "",         "",       "空室"],  # 空室・賃料欠損 → 除外しない
    ]
    build_pdf(p, headers, rows)
    units, rep = extract_rent_roll_from_pdf(p)

    assert rep.rows_extracted == 3, f"sub-header 行が除外されず rows_extracted={rep.rows_extracted}"
    rooms = {u.区画 for u in units}
    assert rooms == {"101", "102", "201"}
    assert "【1F区画】" not in rooms
    assert "【2F区画】" not in rooms
    # 除外したことが report.notes に記録されている
    assert any("【1F区画】" in n for n in rep.notes)
    assert any("【2F区画】" in n for n in rep.notes)
    # 空室区画（201）は欠損があっても除外されない
    unit_201 = next(u for u in units if u.区画 == "201")
    assert not unit_201.is_occupied
    assert unit_201.月額賃料_円 is None


def test_repeated_header_row_excluded(tmp_path):
    """ページ中に再掲されたヘッダー行は除外され、データ行は保持される。"""
    p = tmp_path / "repheader.pdf"
    headers = ["部屋番号", "用途", "面積(㎡)", "月額賃料(円)", "共益費(円)", "入居/空室"]
    rows = [
        ["101", "事務所", "100.0", "300,000", "30,000", "入居"],
        # ページ再掲ヘッダー: 部屋番号セルにヘッダートークン、賃料セルも非数値
        ["部屋番号", "用途", "面積(㎡)", "月額賃料(円)", "共益費(円)", "入居/空室"],
        ["102", "住宅",   "60.0",  "150,000", "10,000", "入居"],
    ]
    build_pdf(p, headers, rows)
    units, rep = extract_rent_roll_from_pdf(p)

    assert rep.rows_extracted == 2
    rooms = {u.区画 for u in units}
    assert rooms == {"101", "102"}
    # 除外したことが report.notes に記録されている
    assert any("部屋番号" in n for n in rep.notes)


# --- column alias mapping（Issue #7）──────────────────────────────────────
# --- safe failure handling（Issue #8）────────────────────────────────────
def test_no_table_pdf_raises(tmp_path):
    """テーブルを含まないPDFは RentRollExtractionError を送出する。"""
    p = build_text_only_pdf(tmp_path / "no_table.pdf")
    with pytest.raises(RentRollExtractionError) as ei:
        extract_rent_roll_from_pdf(p)
    # failure_reason が report に記録されている（report は必ず存在するはず）
    assert ei.value.report is not None
    assert ei.value.report.failure_reason is not None


def test_header_only_pdf_raises(tmp_path):
    """ヘッダー行のみで実データ行がないPDFは RentRollExtractionError を送出する。"""
    p = tmp_path / "header_only.pdf"
    headers = ["部屋番号", "用途", "面積(㎡)", "月額賃料(円)", "共益費(円)", "入居/空室"]
    build_pdf(p, headers, [])  # データ行なし
    with pytest.raises(RentRollExtractionError) as ei:
        extract_rent_roll_from_pdf(p)
    assert "データ行" in str(ei.value)
    assert ei.value.report is not None
    assert ei.value.report.rows_extracted == 0
    assert "データ行" in (ei.value.report.failure_reason or "")


def test_all_null_rent_occupied_raises(tmp_path):
    """稼働区画の賃料がすべて非数値の場合は RentRollExtractionError を送出する。"""
    p = tmp_path / "bad_rent.pdf"
    headers = ["部屋番号", "用途", "面積(㎡)", "月額賃料(円)", "共益費(円)", "入居/空室"]
    rows = [
        ["101", "事務所", "100", "要確認", "30,000", "入居"],
        ["102", "住宅",   "60",  "要確認", "10,000", "入居"],
    ]
    build_pdf(p, headers, rows)
    with pytest.raises(RentRollExtractionError) as ei:
        extract_rent_roll_from_pdf(p)
    assert "稼働区画" in str(ei.value)
    assert ei.value.report is not None
    assert "稼働区画" in (ei.value.report.failure_reason or "")


def test_all_vacant_null_rent_passes(tmp_path):
    """全区画が空室で賃料欠損の場合は safe failure にならない（正常パス）。"""
    p = tmp_path / "all_vacant.pdf"
    headers = ["部屋番号", "用途", "面積(㎡)", "月額賃料(円)", "共益費(円)", "入居/空室"]
    rows = [
        ["101", "事務所", "100", "", "30,000", "空室"],
        ["102", "住宅",   "60",  "", "",        "空室"],
    ]
    build_pdf(p, headers, rows)
    units, rep = extract_rent_roll_from_pdf(p)
    assert rep.rows_extracted == 2
    assert all(not u.is_occupied for u in units)
    assert all(u.月額賃料_円 is None for u in units)
    assert rep.failure_reason is None


# --- column alias mapping（Issue #7）──────────────────────────────────────
@pytest.mark.parametrize("cell, expected_key", [
    # ── room ──
    ("部屋番号",        "room"),
    ("号室",            "room"),
    ("区画番号",        "room"),
    ("Unit No.",        "room"),
    ("Room",            "room"),
    # ── use ──
    ("用途",            "use"),
    ("用途区分",        "use"),
    ("Type",            "use"),
    # ── area ──
    ("専有面積（㎡）",  "area"),
    ("面積",            "area"),
    ("㎡",              "area"),
    ("Area",            "area"),
    ("Floor Area",      "area"),
    # ── rent ──
    ("月額賃料（円）",  "rent"),
    ("賃料（税抜）",    "rent"),
    ("家賃",            "rent"),
    ("Monthly Rent",    "rent"),
    ("Rent",            "rent"),
    # ── cam ──
    ("共益費",          "cam"),
    ("管理費",          "cam"),
    ("サービス料",      "cam"),
    ("CAM",             "cam"),
    ("Common Fee",      "cam"),
    ("Service Charge",  "cam"),
    # ── status ──
    ("入居状況",        "status"),
    ("空室/入居",       "status"),
    ("稼働状況",        "status"),
    ("契約状況",        "status"),
    ("Status",          "status"),
    ("Occupancy",       "status"),
    ("ステータス",        "status"),  # Issue #29
    # ── 入居 は status にマップされる（standalone）; 入居者名/契約者名/テナント名 は除外（Issue #29 follow-up）──
    ("入居",              "status"),
    ("入居者名",          None),
    ("契約者名",          None),
    ("テナント名",        None),
    ("入居者",            None),
    # ── date-type headers containing 入居 must not map to status（Issue #29 follow-up）──
    ("入居日",            None),
    ("入居開始日",        None),
    ("契約開始日",        None),
    ("契約満了日",        None),
    ("契約日",            None),
    ("開始日",            None),
    ("満了日",            None),
    # ── notes（新規 canonical key）──
    ("備考",            "notes"),
    ("メモ",            "notes"),
    ("Remarks",         "notes"),
    ("Notes",           "notes"),
    # ── 未知列 → None（誤変換しない）──
    ("物件名称",        None),
    ("建築年次",        None),
    ("",                None),
    (None,              None),
])
def test_resolve_header_key(cell, expected_key):
    """各ヘッダーセルが正しい canonical key に解決される（または None）。"""
    assert _resolve_header_key(cell) == expected_key

# --- Japanese status column detection（Issue #29）─────────────────────────
def test_japanese_status_column_recognized(tmp_path):
    """ステータス column header is recognized as the status column."""
    p = tmp_path / "status_jp.pdf"
    headers = ["部屋番号", "面積(㎡)", "月額賃料(円)", "共益費(円)", "ステータス"]
    rows = [
        ["101", "30.0", "80,000", "8,000", "入居中"],
        ["102", "30.0", "",       "",       "空室"],
    ]
    build_pdf(p, headers, rows)
    units, rep = extract_rent_roll_from_pdf(p)
    assert "status" in rep.column_map
    assert rep.rows_extracted == 2
    occupied = [u for u in units if u.is_occupied]
    assert len(occupied) == 1
    assert occupied[0].区画 == "101"
    vacant = [u for u in units if not u.is_occupied]
    assert len(vacant) == 1
    assert vacant[0].区画 == "102"


def test_tenant_name_column_not_mapped_to_status(tmp_path):
    """入居者名 column is not mapped to status (false positive suppressed)."""
    p = tmp_path / "tenant_name.pdf"
    headers = ["部屋番号", "入居者名", "面積(㎡)", "月額賃料(円)", "共益費(円)", "入居状況"]
    rows = [
        ["101", "", "30.0", "80,000", "8,000", "入居"],
        ["102", "", "30.0", "",       "",       "空室"],
    ]
    build_pdf(p, headers, rows)
    units, rep = extract_rent_roll_from_pdf(p)
    # status should map to 入居状況 (col 5), not 入居者名 (col 1)
    assert rep.column_map.get("status") == 5
    assert rep.rows_extracted == 2
    assert sum(1 for u in units if u.is_occupied) == 1


def test_status_column_wins_over_tenant_name(tmp_path):
    """When both 入居者名 and ステータス are present, ステータス is selected as status."""
    p = tmp_path / "status_conflict.pdf"
    headers = ["部屋番号", "入居者名", "面積(㎡)", "月額賃料(円)", "共益費(円)", "ステータス"]
    rows = [
        ["101", "", "30.0", "80,000", "8,000", "入居中"],
        ["102", "", "30.0", "80,000", "8,000", "空室"],
        ["103", "", "40.0", "100,000", "10,000", "入居中"],
    ]
    build_pdf(p, headers, rows)
    units, rep = extract_rent_roll_from_pdf(p)
    # ステータス is at col 5, not 入居者名 at col 1
    assert rep.column_map.get("status") == 5, (
        f"status should map to col 5 (ステータス), got col {rep.column_map.get('status')}"
    )
    assert rep.rows_extracted == 3
    occupied = [u for u in units if u.is_occupied]
    assert len(occupied) == 2
    assert {u.区画 for u in occupied} == {"101", "103"}
    vacant = [u for u in units if not u.is_occupied]
    assert len(vacant) == 1
    assert vacant[0].区画 == "102"

def test_standalone_nyukyo_header_recognized(tmp_path):
    """入居 standalone header is recognized as status (no tenant-name false positive)."""
    p = tmp_path / "nyukyo_standalone.pdf"
    headers = ["部屋番号", "面積(㎡)", "月額賃料(円)", "共益費(円)", "入居"]
    rows = [
        ["101", "30.0", "80,000", "8,000", "入居中"],
        ["102", "30.0", "",       "",       "空室"],
    ]
    build_pdf(p, headers, rows)
    units, rep = extract_rent_roll_from_pdf(p)
    assert "status" in rep.column_map
    assert rep.column_map["status"] == 4
    occupied = [u for u in units if u.is_occupied]
    assert len(occupied) == 1
    assert occupied[0].区画 == "101"


def test_nyukyosha_header_not_mapped_to_status(tmp_path):
    """入居者 header (occupant/person name) is not mapped to status."""
    p = tmp_path / "nyukyosha.pdf"
    headers = ["部屋番号", "入居者", "面積(㎡)", "月額賃料(円)", "共益費(円)", "入居状況"]
    rows = [
        ["101", "山田太郎", "30.0", "80,000", "8,000", "入居中"],
        ["102", "",         "30.0", "",        "",       "空室"],
    ]
    build_pdf(p, headers, rows)
    units, rep = extract_rent_roll_from_pdf(p)
    # status must map to 入居状況 (col 5), not 入居者 (col 1)
    assert rep.column_map.get("status") == 5
    assert rep.rows_extracted == 2
    occupied = [u for u in units if u.is_occupied]
    assert len(occupied) == 1
    assert occupied[0].区画 == "101"


def test_nyukyosha_header_with_status_column(tmp_path):
    """When 入居者 and ステータス both present, ステータス wins as status."""
    p = tmp_path / "nyukyosha_status.pdf"
    headers = ["部屋番号", "入居者", "面積(㎡)", "月額賃料(円)", "共益費(円)", "ステータス"]
    rows = [
        ["101", "山田太郎", "30.0", "80,000", "8,000", "入居中"],
        ["102", "",         "30.0", "",        "",       "空室"],
        ["103", "佐藤花子", "40.0", "100,000", "10,000", "入居中"],
    ]
    build_pdf(p, headers, rows)
    units, rep = extract_rent_roll_from_pdf(p)
    # ステータス is at col 5; 入居者 at col 1 must be blocked
    assert rep.column_map.get("status") == 5
    assert rep.rows_extracted == 3
    occupied = [u for u in units if u.is_occupied]
    assert len(occupied) == 2
    assert {u.区画 for u in occupied} == {"101", "103"}


def test_move_in_date_header_not_mapped_to_status(tmp_path):
    """入居日 (move-in date) header is not mapped to status; 入居状況 wins."""
    p = tmp_path / "nyukyo_date.pdf"
    headers = ["部屋番号", "入居日", "面積(㎡)", "月額賃料(円)", "共益費(円)", "入居状況"]
    rows = [
        ["101", "2024/04/01", "30.0", "80,000", "8,000", "入居中"],
        ["102", "",           "30.0", "",        "",       "空室"],
    ]
    build_pdf(p, headers, rows)
    units, rep = extract_rent_roll_from_pdf(p)
    # status must map to 入居状況 (col 5), not 入居日 (col 1)
    assert rep.column_map.get("status") == 5
    assert rep.rows_extracted == 2
    occupied = [u for u in units if u.is_occupied]
    assert len(occupied) == 1
    assert occupied[0].区画 == "101"


def test_move_in_date_header_with_status_column(tmp_path):
    """When 入居日 and ステータス both present, ステータス wins as status."""
    p = tmp_path / "nyukyo_date_status.pdf"
    headers = ["部屋番号", "入居日", "面積(㎡)", "月額賃料(円)", "共益費(円)", "ステータス"]
    rows = [
        ["101", "2024/04/01", "30.0", "80,000", "8,000", "入居中"],
        ["102", "",           "30.0", "85,000", "9,000", "入居中"],
        ["103", "",           "30.0", "",        "",       "空室"],
    ]
    build_pdf(p, headers, rows)
    units, rep = extract_rent_roll_from_pdf(p)
    # ステータス is at col 5; 入居日 at col 1 must be blocked
    assert rep.column_map.get("status") == 5
    assert rep.rows_extracted == 3
    occupied = [u for u in units if u.is_occupied]
    assert len(occupied) == 2
    assert {u.区画 for u in occupied} == {"101", "102"}
    vacant = [u for u in units if not u.is_occupied]
    assert len(vacant) == 1
    assert vacant[0].区画 == "103"


# --- Issue #30: total / summary row filtering ──────────────────────────────────

@pytest.mark.parametrize("room_label", [
    "合 計",
    "合計",
    "小計",
    "総計",
    "計",
    "TOTAL",
    "Total",
    "total",
    "Subtotal",
    "SUBTOTAL",
    "Sub total",
    "subtotal",
])
def test_summary_row_label_is_non_data_row(room_label):
    """Known summary row labels are identified as non-data rows."""
    from revenue_kun.pdf_extract import _is_non_data_row
    # rent=None so condition 2 (repeated header) does not fire
    assert _is_non_data_row(room_label, [None, None], {"rent": 1})


@pytest.mark.parametrize("room_label", [
    "101",
    "201",
    "A-101",
    "1F-01",
    "計画棟101",
    "合計算",
])
def test_normal_room_label_is_not_non_data_row(room_label):
    """Normal room numbers containing summary-like substrings are not excluded."""
    from revenue_kun.pdf_extract import _is_non_data_row
    assert not _is_non_data_row(room_label, [None, None], {"rent": 1})


def test_summary_row_excluded_from_extraction(tmp_path):
    """合 計 row is excluded; remaining 20 rows include 17 occupied and 3 vacant."""
    p = tmp_path / "with_total.pdf"
    headers = ["部屋番号", "面積(㎡)", "月額賃料(円)", "共益費(円)", "ステータス"]
    rows = [
        ["101", "30.0", "80,000", "8,000", "入居中"],
        ["102", "30.0", "85,000", "9,000", "入居中"],
        ["103", "30.0", "",        "",       "空室"],
        ["合 計", "",     "165,000", "17,000", ""],  # must be excluded
    ]
    build_pdf(p, headers, rows)
    units, rep = extract_rent_roll_from_pdf(p)
    assert rep.rows_extracted == 3
    area_labels = [u.区画 for u in units]
    assert "合 計" not in area_labels
    occupied = [u for u in units if u.is_occupied]
    assert len(occupied) == 2
    vacant = [u for u in units if not u.is_occupied]
    assert len(vacant) == 1


def test_multiple_summary_variants_excluded(tmp_path):
    """合計, 小計, TOTAL variants are all excluded from extraction."""
    p = tmp_path / "multi_total.pdf"
    headers = ["部屋番号", "面積(㎡)", "月額賃料(円)", "共益費(円)", "入居状況"]
    rows = [
        ["101", "30.0", "80,000", "8,000", "入居中"],
        ["小計", "", "80,000", "8,000", ""],
        ["102", "30.0", "85,000", "9,000", "入居中"],
        ["TOTAL", "", "165,000", "17,000", ""],
    ]
    build_pdf(p, headers, rows)
    units, rep = extract_rent_roll_from_pdf(p)
    assert rep.rows_extracted == 2
    labels = [u.区画 for u in units]
    assert "小計" not in labels
    assert "TOTAL" not in labels
    assert labels == ["101", "102"]


# --- v0.4.1 hardening regression tests (Issue #44) ───────────────────────────

@pytest.mark.parametrize("room_label", [
    "合　計",   # 合　計 (full-width space)
])
def test_summary_row_fullwidth_space_variant(room_label):
    """合　計 (full-width space) is identified as a non-data row."""
    from revenue_kun.pdf_extract import _is_non_data_row
    assert _is_non_data_row(room_label, [None, None], {"rent": 1})


def test_summary_row_does_not_inflate_gpi(tmp_path):
    """Summary row rent value is not included in the GPI (sum of occupied unit rents)."""
    p = tmp_path / "gpi_check.pdf"
    headers = ["部屋番号", "面積(㎡)", "月額賃料(円)", "共益費(円)", "ステータス"]
    rows = [
        ["101", "30.0", "80,000", "8,000",  "入居中"],
        ["102", "30.0", "85,000", "9,000",  "入居中"],
        ["103", "30.0", "",       "",        "空室"],
        ["合 計", "", "165,000", "17,000", ""],  # 合 計 — must be excluded
    ]
    build_pdf(p, headers, rows)
    units, rep = extract_rent_roll_from_pdf(p)
    assert rep.rows_extracted == 3
    occupied = [u for u in units if u.is_occupied]
    assert len(occupied) == 2
    gpi = sum(u.月額賃料_円 for u in occupied if u.月額賃料_円 is not None)
    # 80,000 + 85,000 = 165,000; summary row 165,000 must NOT be added a second time
    assert gpi == 165_000


@pytest.mark.parametrize("text, expected", [
    # occupied variants
    ("入居中",  "入居"),   # 入居中 → 入居
    ("稼働中",  "入居"),   # 稼働中 → 入居
    ("賃貸中",  "入居"),   # 賃貸中 → 入居
    ("使用中",  "入居"),   # 使用中 → 入居
    # vacant variants
    ("空室",        "空室"),   # 空室 → 空室
    ("空き室",  "空室"),   # 空き室 → 空室
    ("募集中",  "空室"),   # 募集中 → 空室
    # raw passthrough (no alias)
    ("満室",        "満室"),   # 満室 → raw passthrough
    # None
    (None, None),
])
def test_normalize_status(text, expected):
    """Status values normalize to expected canonical strings."""
    from revenue_kun.pdf_extract import _normalize_status
    assert _normalize_status(text) == expected


def test_status_value_boshuchuu_is_vacant(tmp_path):
    """募集中 status value normalizes to 空室 (not counted as occupied)."""
    p = tmp_path / "boshuchuu.pdf"
    headers = ["部屋番号", "面積(㎡)", "月額賃料(円)", "共益費(円)", "入居状況"]
    rows = [
        ["101", "30.0", "80,000", "8,000", "入居中"],   # 入居中
        ["102", "30.0", "",       "",       "募集中"],   # 募集中
        ["103", "30.0", "",       "",       "空室"],          # 空室
    ]
    build_pdf(p, headers, rows)
    units, rep = extract_rent_roll_from_pdf(p)
    assert rep.rows_extracted == 3
    occupied = [u for u in units if u.is_occupied]
    assert len(occupied) == 1
    assert occupied[0].区画 == "101"
    vacant = [u for u in units if not u.is_occupied]
    assert len(vacant) == 2
    assert {u.区画 for u in vacant} == {"102", "103"}


def test_kei_in_non_room_field_does_not_exclude_row(tmp_path):
    """A row is not excluded when 計 appears in a non-room field (notes/remarks).
    Only the room field is checked for summary-row matching."""
    p = tmp_path / "kei_in_notes.pdf"
    headers = ["部屋番号", "面積(㎡)", "月額賃料(円)", "共益費(円)", "入居状況", "備考"]
    rows = [
        ["101", "30.0", "80,000", "8,000", "入居中", "管理費計上済み"],  # 計 in notes
        ["102", "30.0", "85,000", "9,000", "入居中", "合計含む"],        # 合計 in notes
        ["103", "30.0", "",       "",       "空室",   ""],
    ]
    build_pdf(p, headers, rows)
    units, rep = extract_rent_roll_from_pdf(p)
    assert rep.rows_extracted == 3
    assert {u.区画 for u in units} == {"101", "102", "103"}
