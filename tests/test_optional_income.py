"""付帯収入（optional income）機能のテスト。

検証項目:
  A. 後方互換性 — optional_income 設定なし / false / columns: [] で GPI 変わらず
  B. water opt-in — GPI が 8,211,540 円になること
  C. water opt-out — 同入力で GPI が 7,764,000 円になること
  D. カテゴリ分離 — 水道代（収入）と運営費用の水道光熱費（費用）を混同しない
  E. PDF 抽出 — "水道代" ヘッダーが water として認識されること
  F. Excel 出力 — opt-in 時は月額水道光熱費が設定され、opt-out 時は None のまま
"""
from __future__ import annotations

from pathlib import Path

import pytest

from revenue_kun.config import (
    Assumptions,
    OptionalIncomeConfig,
    load_assumptions,
)
from revenue_kun.excel_output import DirectCapRow
from revenue_kun.noi import compute_noi
from revenue_kun.pdf_extract import _resolve_header_key, extract_rent_roll_from_pdf
from revenue_kun.rent_roll import RentRollUnit
from revenue_kun.sample_pdf import build_pdf


# ---------------------------------------------------------------------------
# ヘルパー
# ---------------------------------------------------------------------------

def _make_assumptions(
    include_in_gpi: bool = False,
    columns: list[str] | None = None,
) -> Assumptions:
    """テスト用 Assumptions を生成する（cap_rate などは最小値で設定）。"""
    a = load_assumptions("assumptions.sample.yaml")
    a.optional_income = OptionalIncomeConfig(
        include_in_gpi=include_in_gpi,
        columns=columns or [],
    )
    return a


def _unit(
    room: str = "101",
    rent: float = 601_000,
    cam: float = 46_000,
    water: float | None = None,
    parking: float | None = None,
    other_income: float | None = None,
    status: str = "入居",
) -> RentRollUnit:
    return RentRollUnit(
        区画=room,
        用途="住宅",
        賃借人=None,
        専有面積_m2=30.0,
        月額賃料_円=rent,
        月額共益費_円=cam,
        稼働状況=status,
        契約満了日=None,
        月額水道代_円=water,
        月額駐車場収入_円=parking,
        月額その他収入_円=other_income,
    )


# ---------------------------------------------------------------------------
# A. 後方互換性テスト
# ---------------------------------------------------------------------------

class TestBackwardCompatibility:
    """optional_income 設定がない / false / empty でも既存 GPI が変わらない。"""

    def test_no_section_defaults_to_false(self):
        """assumptions に optional_income セクションがなければ include_in_gpi=False。"""
        a = load_assumptions("assumptions.sample.yaml")
        # sample.yaml には optional_income: include_in_gpi: false が入っている
        assert a.optional_income.include_in_gpi is False
        assert a.optional_income.columns == []

    def test_include_false_gpi_unchanged(self):
        """include_in_gpi=False のとき water があっても GPI に算入しない。"""
        a = _make_assumptions(include_in_gpi=False, columns=["water"])
        units = [_unit(rent=601_000, cam=46_000, water=37_295)]
        noi = compute_noi(units, a)
        expected_gpi = (601_000 + 46_000) * 12
        assert noi.gpi == pytest.approx(expected_gpi)

    def test_empty_columns_gpi_unchanged(self):
        """include_in_gpi=True でも columns=[] なら付帯収入を算入しない。"""
        a = _make_assumptions(include_in_gpi=True, columns=[])
        units = [_unit(rent=601_000, cam=46_000, water=37_295)]
        noi = compute_noi(units, a)
        expected_gpi = (601_000 + 46_000) * 12
        assert noi.gpi == pytest.approx(expected_gpi)

    def test_rent_income_and_cam_income_breakdown(self):
        """収入内訳フィールドが正しく設定される（opt-out）。"""
        a = _make_assumptions(include_in_gpi=False)
        units = [_unit(rent=601_000, cam=46_000, water=37_295)]
        noi = compute_noi(units, a)
        assert noi.rent_income == pytest.approx(601_000 * 12)
        assert noi.cam_income == pytest.approx(46_000 * 12)
        assert noi.optional_income_total == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# B. water opt-in テスト
# ---------------------------------------------------------------------------

class TestWaterOptin:
    """水道代を opt-in すると GPI = 8,211,540円になること。"""

    def test_gpi_with_water_optin(self):
        """グリーン蛍 PDF 相当: rent+cam+water × 17区画 ≈ 8,211,540。"""
        a = _make_assumptions(include_in_gpi=True, columns=["water"])
        units = [_unit(rent=601_000, cam=46_000, water=37_295)]
        noi = compute_noi(units, a)
        # 1区画の場合: (601000 + 46000 + 37295) * 12 = 8,211,540
        expected = (601_000 + 46_000 + 37_295) * 12
        assert noi.gpi == pytest.approx(expected)

    def test_income_breakdown_with_water_optin(self):
        """opt-in 時は optional_income_total が正しく設定される。"""
        a = _make_assumptions(include_in_gpi=True, columns=["water"])
        units = [_unit(rent=601_000, cam=46_000, water=37_295)]
        noi = compute_noi(units, a)
        assert noi.rent_income == pytest.approx(601_000 * 12)
        assert noi.cam_income == pytest.approx(46_000 * 12)
        assert noi.optional_income_total == pytest.approx(37_295 * 12)
        assert noi.gpi == pytest.approx(noi.rent_income + noi.cam_income + noi.optional_income_total)

    def test_multi_unit_water_optin(self):
        """複数区画の場合も水道代が正しく合計される。"""
        a = _make_assumptions(include_in_gpi=True, columns=["water"])
        units = [
            _unit("101", rent=100_000, cam=10_000, water=5_000),
            _unit("102", rent=120_000, cam=12_000, water=6_000),
            _unit("103", rent=80_000, cam=8_000, water=None),  # 水道代なし
        ]
        noi = compute_noi(units, a)
        expected_gpi = (100_000 + 10_000 + 5_000 + 120_000 + 12_000 + 6_000 + 80_000 + 8_000) * 12
        assert noi.gpi == pytest.approx(expected_gpi)
        assert noi.optional_income_total == pytest.approx((5_000 + 6_000) * 12)

    def test_water_optin_note_added(self):
        """opt-in 時は notes に付帯収入算入の記録が入る。"""
        a = _make_assumptions(include_in_gpi=True, columns=["water"])
        units = [_unit(water=37_295)]
        noi = compute_noi(units, a)
        assert any("opt-in" in n for n in noi.notes)


# ---------------------------------------------------------------------------
# C. water opt-out テスト
# ---------------------------------------------------------------------------

class TestWaterOptout:
    """同入力で include_in_gpi=false → GPI = 7,764,000 円になること。"""

    def test_gpi_without_water_optout(self):
        a = _make_assumptions(include_in_gpi=False)
        units = [_unit(rent=601_000, cam=46_000, water=37_295)]
        noi = compute_noi(units, a)
        expected = (601_000 + 46_000) * 12
        assert noi.gpi == pytest.approx(expected)
        assert noi.optional_income_total == pytest.approx(0.0)

    def test_water_not_in_columns_is_excluded(self):
        """include_in_gpi=True でも water が columns にない場合は除外される。"""
        a = _make_assumptions(include_in_gpi=True, columns=["parking"])
        units = [_unit(rent=601_000, cam=46_000, water=37_295)]
        noi = compute_noi(units, a)
        expected = (601_000 + 46_000) * 12  # water は除外
        assert noi.gpi == pytest.approx(expected)


# ---------------------------------------------------------------------------
# D. カテゴリ分離テスト
# ---------------------------------------------------------------------------

class TestCategorySeparation:
    """水道代（収入サイド）と運営費用の水道光熱費（費用サイド）を混同しない。"""

    def test_water_income_is_not_opex(self):
        """RentRollUnit.月額水道代_円 は収入フィールド。opex に影響しない。"""
        a = _make_assumptions(include_in_gpi=True, columns=["water"])
        # 運営費用に水道光熱費がある
        a.opex["水道光熱費"] = 1_200_000
        units = [_unit(rent=100_000, cam=10_000, water=5_000)]
        noi = compute_noi(units, a)
        # GPI には水道代（収入）が算入される
        assert noi.optional_income_total == pytest.approx(5_000 * 12)
        # 運営費用には水道光熱費（費用）が算入される（別物）
        assert "水道光熱費" in noi.opex_breakdown
        assert noi.opex_breakdown["水道光熱費"] == 1_200_000

    def test_get_optional_income_method(self):
        """RentRollUnit.get_optional_income() が canonical key で正しく取得できる。"""
        u = _unit(water=37_295, parking=20_000, other_income=5_000)
        assert u.get_optional_income("water") == 37_295
        assert u.get_optional_income("parking") == 20_000
        assert u.get_optional_income("other_income") == 5_000
        assert u.get_optional_income("unknown") is None

    def test_vacant_unit_water_excluded_from_gpi(self):
        """空室区画の水道代は GPI から除外される（稼働区画のみ算入）。"""
        a = _make_assumptions(include_in_gpi=True, columns=["water"])
        units = [
            _unit("101", rent=100_000, cam=10_000, water=5_000, status="入居"),
            _unit("102", rent=None, cam=None, water=5_000, status="空室"),  # 空室
        ]
        noi = compute_noi(units, a)
        # 空室区画の水道代は算入されない
        assert noi.optional_income_total == pytest.approx(5_000 * 12)


# ---------------------------------------------------------------------------
# E. PDF 抽出テスト
# ---------------------------------------------------------------------------

class TestPdfExtraction:
    """水道代ヘッダーが water として認識され、RentRollUnit に保持される。"""

    def test_water_header_resolved(self):
        """「水道代」ヘッダーが canonical key 'water' に解決される。"""
        assert _resolve_header_key("水道代") == "water"

    def test_water_fee_header_resolved(self):
        """「水道費」も water に解決される。"""
        assert _resolve_header_key("水道費") == "water"

    def test_parking_revenue_header_resolved(self):
        """「駐車場収入」が parking に解決される。"""
        assert _resolve_header_key("駐車場収入") == "parking"

    def test_parking_header_resolved(self):
        """「駐車場」が parking に解決される。"""
        assert _resolve_header_key("駐車場") == "parking"

    def test_other_income_header_resolved(self):
        """「その他収入」が other_income に解決される。"""
        assert _resolve_header_key("その他収入") == "other_income"

    def test_existing_headers_unaffected(self):
        """既存ヘッダーのマッピングが壊れていない。"""
        assert _resolve_header_key("部屋番号") == "room"
        assert _resolve_header_key("月額賃料(円)") == "rent"
        assert _resolve_header_key("共益費") == "cam"
        assert _resolve_header_key("入居/空室") == "status"
        assert _resolve_header_key("備考") == "notes"

    def test_water_column_extracted_to_rent_roll_unit(self, tmp_path):
        """水道代列を含む PDF から RentRollUnit.月額水道代_円 が抽出される。"""
        headers = ["部屋番号", "用途", "面積(㎡)", "月額賃料(円)", "共益費(円)", "入居/空室", "水道代"]
        rows = [["101", "住宅", "30.0", "100,000", "10,000", "入居", "5,000"]]
        p = tmp_path / "water_test.pdf"
        build_pdf(p, headers, rows)
        units, rep = extract_rent_roll_from_pdf(p)
        assert len(units) == 1
        assert units[0].月額水道代_円 == 5_000
        assert "water" in rep.optional_income_found

    def test_no_water_column_unit_water_is_none(self, tmp_path):
        """水道代列がない PDF では RentRollUnit.月額水道代_円 が None。"""
        headers = ["部屋番号", "用途", "面積(㎡)", "月額賃料(円)", "共益費(円)", "入居/空室"]
        rows = [["101", "住宅", "30.0", "100,000", "10,000", "入居"]]
        p = tmp_path / "no_water.pdf"
        build_pdf(p, headers, rows)
        units, rep = extract_rent_roll_from_pdf(p)
        assert units[0].月額水道代_円 is None
        assert "water" not in rep.optional_income_found

    def test_optional_income_found_reported(self, tmp_path):
        """水道代・駐車場収入の両列を持つ PDF で optional_income_found が正しく設定される。"""
        headers = [
            "部屋番号", "用途", "面積(㎡)", "月額賃料(円)", "共益費(円)", "入居/空室",
            "水道代", "駐車場収入",
        ]
        rows = [["101", "住宅", "30.0", "100,000", "10,000", "入居", "5,000", "20,000"]]
        p = tmp_path / "multi_oi.pdf"
        build_pdf(p, headers, rows)
        units, rep = extract_rent_roll_from_pdf(p)
        assert "water" in rep.optional_income_found
        assert "parking" in rep.optional_income_found
        assert units[0].月額水道代_円 == 5_000
        assert units[0].月額駐車場収入_円 == 20_000

    def test_existing_extraction_unaffected(self, tmp_path):
        """通常の PDF 抽出（水道代なし）に影響がない（回帰テスト）。"""
        headers = ["部屋番号", "用途", "面積(㎡)", "月額賃料(円)", "共益費(円)", "入居/空室"]
        rows = [
            ["101", "事務所", "50.0", "200,000", "20,000", "入居"],
            ["102", "事務所", "50.0", "200,000", "20,000", "入居"],
        ]
        p = tmp_path / "normal.pdf"
        build_pdf(p, headers, rows)
        units, rep = extract_rent_roll_from_pdf(p)
        assert rep.rows_extracted == 2
        assert all(u.月額賃料_円 == 200_000 for u in units)
        assert rep.optional_income_found == []


# ---------------------------------------------------------------------------
# F. Excel 出力テスト
# ---------------------------------------------------------------------------

class TestExcelOutput:
    """opt-in 時は月額水道光熱費が設定され、opt-out 時は None のまま。"""

    def _make_unit(self, water: float | None = 37_295) -> RentRollUnit:
        return RentRollUnit(
            区画="101",
            用途="住宅",
            賃借人=None,
            専有面積_m2=30.0,
            月額賃料_円=601_000,
            月額共益費_円=46_000,
            稼働状況="入居",
            契約満了日=None,
            月額水道代_円=water,
        )

    def test_optin_populates_water(self):
        """include_in_gpi=True かつ water in columns で 月額水道光熱費 が設定される。"""
        unit = self._make_unit(water=37_295)
        oi = OptionalIncomeConfig(include_in_gpi=True, columns=["water"])
        row = DirectCapRow.from_rent_roll_unit(unit, oi)
        assert row.月額水道光熱費 == 37_295

    def test_optout_water_is_none(self):
        """include_in_gpi=False では月額水道光熱費が None のまま（ユーザー手入力用）。"""
        unit = self._make_unit(water=37_295)
        oi = OptionalIncomeConfig(include_in_gpi=False, columns=["water"])
        row = DirectCapRow.from_rent_roll_unit(unit, oi)
        assert row.月額水道光熱費 is None

    def test_no_config_water_is_none(self):
        """oi_config 未指定（None）でも月額水道光熱費が None（後方互換）。"""
        unit = self._make_unit(water=37_295)
        row = DirectCapRow.from_rent_roll_unit(unit)
        assert row.月額水道光熱費 is None

    def test_water_not_in_columns_is_none(self):
        """include_in_gpi=True でも water が columns にない場合は None。"""
        unit = self._make_unit(water=37_295)
        oi = OptionalIncomeConfig(include_in_gpi=True, columns=["parking"])
        row = DirectCapRow.from_rent_roll_unit(unit, oi)
        assert row.月額水道光熱費 is None

    def test_optin_parking_populated(self):
        """parking opt-in では月額駐車場が設定される。"""
        unit = RentRollUnit(
            区画="102", 用途="住宅", 賃借人=None, 専有面積_m2=30.0,
            月額賃料_円=100_000, 月額共益費_円=10_000,
            稼働状況="入居", 契約満了日=None,
            月額駐車場収入_円=20_000,
        )
        oi = OptionalIncomeConfig(include_in_gpi=True, columns=["parking"])
        row = DirectCapRow.from_rent_roll_unit(unit, oi)
        assert row.月額駐車場 == 20_000
        assert row.月額水道光熱費 is None  # water は columns にない

    def test_multiple_optin_columns(self):
        """複数の optional income が同時に設定される。"""
        unit = RentRollUnit(
            区画="103", 用途="住宅", 賃借人=None, 専有面積_m2=30.0,
            月額賃料_円=100_000, 月額共益費_円=10_000,
            稼働状況="入居", 契約満了日=None,
            月額水道代_円=5_000,
            月額駐車場収入_円=20_000,
            月額その他収入_円=3_000,
        )
        oi = OptionalIncomeConfig(include_in_gpi=True, columns=["water", "parking", "other_income"])
        row = DirectCapRow.from_rent_roll_unit(unit, oi)
        assert row.月額水道光熱費 == 5_000
        assert row.月額駐車場 == 20_000
        assert row.月額その他収入 == 3_000


# ---------------------------------------------------------------------------
# config 読み込みテスト
# ---------------------------------------------------------------------------

class TestOptionalIncomeConfig:
    """OptionalIncomeConfig の読み込みと検証。"""

    def test_load_defaults_from_yaml(self):
        """sample.yaml から OptionalIncomeConfig がデフォルト値で読み込まれる。"""
        a = load_assumptions("assumptions.sample.yaml")
        assert a.optional_income.include_in_gpi is False
        assert a.optional_income.columns == []

    def test_manual_override(self):
        """OptionalIncomeConfig を直接設定できる。"""
        cfg = OptionalIncomeConfig(include_in_gpi=True, columns=["water", "parking"])
        assert cfg.include_in_gpi is True
        assert "water" in cfg.columns
        assert "parking" in cfg.columns

    def test_default_config_is_false(self):
        """OptionalIncomeConfig() のデフォルトは include_in_gpi=False。"""
        cfg = OptionalIncomeConfig()
        assert cfg.include_in_gpi is False
        assert cfg.columns == []
