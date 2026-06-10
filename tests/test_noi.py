"""NOI計算・直接還元法・感応度分析のテスト（CSV経路）。"""
from __future__ import annotations

from revenue_kun.config import load_assumptions
from revenue_kun.noi import compute_noi
from revenue_kun.rent_roll import RentRollUnit, load_rent_roll
from revenue_kun.sensitivity import build_sensitivity
from revenue_kun.valuation import direct_capitalization

ROOT_ASSUMPTIONS = "assumptions.sample.yaml"
DUMMY_CSV = "data/dummy_rent_roll.csv"


def _unit(room, rent, cam, status="稼働", area=50.0):
    return RentRollUnit(
        区画=room, 用途="事務所", 賃借人="テスト",
        専有面積_m2=area, 月額賃料_円=rent, 月額共益費_円=cam,
        稼働状況=status, 契約満了日=None,
    )


def test_gpi_excludes_vacant_and_missing_rent():
    assumptions = load_assumptions(ROOT_ASSUMPTIONS)
    units = [
        _unit("1", 100000, 10000, "稼働"),      # 1,320,000/年
        _unit("2", None, 10000, "稼働"),         # 賃料欠損 → 除外
        _unit("3", 100000, 10000, "空室"),       # 空室 → 除外
    ]
    noi = compute_noi(units, assumptions)
    assert noi.gpi == 110000 * 12
    # 欠損による除外が警告される（補完しない）
    assert any("区画 2" in w for w in noi.warnings)


def test_direct_capitalization_value():
    assumptions = load_assumptions(ROOT_ASSUMPTIONS)
    units = [_unit("1", 100000, 0, "稼働")]
    noi = compute_noi(units, assumptions)
    val = direct_capitalization(noi, assumptions)
    # 試算値 = 純収益 / 還元利回り
    assert val.estimated_value == noi.net_income / assumptions.cap_rate
    assert val.cap_rate == assumptions.cap_rate


def test_missing_cap_rate_yields_no_value():
    assumptions = load_assumptions(ROOT_ASSUMPTIONS)
    assumptions.cap_rate = None  # 欠損
    units = [_unit("1", 100000, 0, "稼働")]
    noi = compute_noi(units, assumptions)
    val = direct_capitalization(noi, assumptions)
    assert val.estimated_value is None  # 補完せず算定不能


def test_dummy_csv_pipeline_runs():
    assumptions = load_assumptions(ROOT_ASSUMPTIONS)
    units = load_rent_roll(DUMMY_CSV)
    noi = compute_noi(units, assumptions)
    val = direct_capitalization(noi, assumptions)
    sens = build_sensitivity(noi, assumptions)
    assert val.estimated_value is not None
    assert sens is not None
    # 感応度: 基準セル（NOI 0% × 基準利回り）が試算値と一致
    base_i = sens.noi_rates.index(0.0)
    base_j = sens.cap_rates.index(sens.base_cap_rate)
    assert abs(sens.values[base_i][base_j] - val.estimated_value) < 1e-6


def test_occupied_status_accepts_csv_and_pdf_labels():
    assert _unit("1", 1, 1, "稼働").is_occupied
    assert _unit("1", 1, 1, "入居").is_occupied
    assert not _unit("1", 1, 1, "空室").is_occupied
