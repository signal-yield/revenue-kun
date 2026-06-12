"""PDF抽出の堅牢化テスト（Phase 2.1 / 3パターン＋列名ゆれ＋必須列欠落）。"""
from __future__ import annotations

from pathlib import Path

import pytest

from revenue_kun.pdf_extract import (
    RentRollExtractionError,
    _resolve_header_key,
    extract_rent_roll_from_pdf,
)
from revenue_kun.sample_pdf import PATTERNS, build_pdf, generate_sample_pdf


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
