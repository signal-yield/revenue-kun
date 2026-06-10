"""assumptions.yaml の入力バリデーションのテスト（出荷ハードニング）。"""
from __future__ import annotations

import pytest

from revenue_kun.config import (
    Assumptions,
    AssumptionsError,
    load_assumptions,
    validate_assumptions,
)

ASSUMPTIONS = "assumptions.sample.yaml"


def _base(**over) -> Assumptions:
    """妥当な前提条件を作り、一部だけ上書きする。"""
    kwargs = dict(
        property_info={},
        cap_rate=0.045,
        vacancy_rate=0.05,
        opex={"水道光熱費": 1200000, "管理委託費": None},  # null は許容
        capex=1000000,
    )
    kwargs.update(over)
    return Assumptions(**kwargs)


def test_sample_assumptions_are_valid():
    """同梱の assumptions.sample.yaml は検証を通る。"""
    validate_assumptions(load_assumptions(ASSUMPTIONS))


def test_valid_baseline_passes():
    validate_assumptions(_base())  # 例外が出ないこと


@pytest.mark.parametrize("bad", [0, -0.01, -1])
def test_cap_rate_non_positive_raises(bad):
    with pytest.raises(AssumptionsError) as ei:
        validate_assumptions(_base(cap_rate=bad))
    assert "還元利回り" in str(ei.value)


def test_cap_rate_missing_raises():
    with pytest.raises(AssumptionsError) as ei:
        validate_assumptions(_base(cap_rate=None))
    assert "還元利回り" in str(ei.value)


@pytest.mark.parametrize("bad", [-0.1, 1.5, 2])
def test_vacancy_rate_out_of_range_raises(bad):
    with pytest.raises(AssumptionsError) as ei:
        validate_assumptions(_base(vacancy_rate=bad))
    assert "空室損失率" in str(ei.value)


def test_vacancy_rate_missing_raises():
    with pytest.raises(AssumptionsError):
        validate_assumptions(_base(vacancy_rate=None))


def test_negative_opex_raises():
    with pytest.raises(AssumptionsError) as ei:
        validate_assumptions(_base(opex={"維持修繕費": -500000}))
    assert "維持修繕費" in str(ei.value)


def test_negative_capex_raises():
    with pytest.raises(AssumptionsError):
        validate_assumptions(_base(capex=-1))


def test_opex_null_is_allowed():
    """任意費用の null は許容（補完せず後段で欠損記録）。"""
    validate_assumptions(_base(opex={"管理委託費": None, "租税公課": 100}))


def test_multiple_errors_are_all_reported():
    with pytest.raises(AssumptionsError) as ei:
        validate_assumptions(_base(cap_rate=0, vacancy_rate=2, capex=-1))
    msg = str(ei.value)
    assert "還元利回り" in msg and "空室損失率" in msg and "資本的支出" in msg
