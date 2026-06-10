"""感応度分析（直接還元法）。

還元利回り（絶対値の増減）と NOI（変動率）を振って、
収益試算値のマトリクスを生成する。
"""
from __future__ import annotations

from dataclasses import dataclass

from .config import Assumptions
from .noi import NOIResult


@dataclass
class SensitivityTable:
    cap_rates: list[float]          # 列見出しに使う還元利回り（基準±変動幅）
    noi_rates: list[float]          # 行見出しに使う NOI 変動率
    base_cap_rate: float
    base_net_income: float
    # values[i][j] = NOI変動率 noi_rates[i] × 還元利回り cap_rates[j] の収益試算値
    values: list[list[float | None]]


def build_sensitivity(noi: NOIResult, assumptions: Assumptions) -> SensitivityTable | None:
    """感応度マトリクスを生成する。還元利回りが無ければ None。"""
    base_cap = assumptions.cap_rate
    if base_cap is None or base_cap <= 0:
        return None

    cap_deltas = assumptions.sensitivity_cap_deltas or [0.0]
    noi_rates = assumptions.sensitivity_noi_rates or [0.0]

    cap_rates = [round(base_cap + d, 6) for d in cap_deltas]
    base_ni = noi.net_income

    values: list[list[float | None]] = []
    for r in noi_rates:
        row: list[float | None] = []
        adj_ni = base_ni * (1 + r)
        for c in cap_rates:
            row.append(adj_ni / c if c > 0 else None)
        values.append(row)

    return SensitivityTable(
        cap_rates=cap_rates,
        noi_rates=noi_rates,
        base_cap_rate=base_cap,
        base_net_income=base_ni,
        values=values,
    )
