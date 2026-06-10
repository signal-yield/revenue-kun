"""免責・用語統一のテスト（収益価格と表記しない／鑑定評価ではない旨）。"""
from __future__ import annotations

from revenue_kun import DISCLAIMER, VALUE_LABEL


def test_value_label_is_estimate_not_price():
    assert VALUE_LABEL == "収益試算値"
    assert VALUE_LABEL != "収益価格"


def test_disclaimer_states_not_appraisal():
    assert "鑑定評価ではありません" in DISCLAIMER


def test_disclaimer_negates_price_term():
    # 「収益価格ではありません」という否定文脈でのみ収益価格に言及する
    assert "「収益価格」ではありません" in DISCLAIMER
