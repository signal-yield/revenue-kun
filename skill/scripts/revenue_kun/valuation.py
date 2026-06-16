"""直接還元法による収益試算値の算定。

  収益試算値 = 純収益 ÷ 還元利回り

【重要】この値は「収益試算値」であり、鑑定評価の「収益価格」ではない。
"""
from __future__ import annotations

from dataclasses import dataclass

from .config import Assumptions
from .noi import NOIResult


@dataclass
class ValuationResult:
    net_income: float          # 還元対象の純収益
    cap_rate: float | None     # 還元利回り
    estimated_value: float | None  # 収益試算値（None=算定不能）
    note: str


def direct_capitalization(noi: NOIResult, assumptions: Assumptions) -> ValuationResult:
    """直接還元法で収益試算値を算定する。

    還元利回りが欠損または不正（0以下）の場合は算定せず None を返す。
    """
    cap_rate = assumptions.cap_rate

    if cap_rate is None:
        return ValuationResult(
            net_income=noi.net_income,
            cap_rate=None,
            estimated_value=None,
            note="還元利回りが未設定のため収益試算値を算定できません（補完なし）。",
        )
    if cap_rate <= 0:
        return ValuationResult(
            net_income=noi.net_income,
            cap_rate=cap_rate,
            estimated_value=None,
            note=f"還元利回りが不正値（{cap_rate}）のため収益試算値を算定できません。",
        )

    value = noi.net_income / cap_rate
    return ValuationResult(
        net_income=noi.net_income,
        cap_rate=cap_rate,
        estimated_value=value,
        note="直接還元法（収益試算値 = 純収益 ÷ 還元利回り）による試算値です。鑑定評価ではありません。",
    )
