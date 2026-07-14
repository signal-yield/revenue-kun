"""NOI（運営純収益）の計算。

現行賃料ベースで潜在総収入(GPI)を集計し、空室損失・運営費用を控除する。
欠損項目（運営費用の null、稼働区画の賃料欠損など）は補完せず、
算入できなかった事実を warnings として返す。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .config import Assumptions
from .rent_roll import RentRollUnit


@dataclass
class NOIResult:
    gpi: float                      # 潜在総収入（年額・現行賃料ベース）
    vacancy_loss: float             # 空室損失（GPI×空室損失率）
    egi: float                      # 有効総収入（GPI−空室損失）
    opex_total: float               # 運営費用合計（算入できた項目のみ）
    opex_breakdown: dict[str, float]
    capex: float                    # 資本的支出控除
    noi: float                      # 運営純収益（EGI−運営費用）
    net_income: float               # 直接還元用純収益（NOI−CAPEX）
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    # 収入カテゴリ別内訳（GPI の構成要素）
    rent_income: float = 0.0        # 賃料収入（年額）
    cam_income: float = 0.0         # 共益費収入（年額）
    optional_income_total: float = 0.0  # 付帯収入合計（opt-in 時のみ）


def compute_noi(units: list[RentRollUnit], assumptions: Assumptions) -> NOIResult:
    """レントロールと前提条件から NOI / 純収益を計算する。"""
    warnings: list[str] = []
    notes: list[str] = []

    # --- 潜在総収入(GPI) -------------------------------------------------
    # GPI = 賃料収入 + 共益費収入 + 付帯収入（opt-in 時のみ）
    # 稼働区画で賃料が欠損している場合は補完せず、GPI から除外して警告する。
    rent_income = 0.0
    cam_income = 0.0
    optional_income_total = 0.0
    oi_config = assumptions.optional_income

    for u in units:
        if not u.is_occupied:
            # 空室区画の市場賃料は不明。推測補完しない（欠損扱いは missing 側）。
            continue
        if u.月額賃料_円 is None:
            # 必須項目（月額賃料）の欠損。補完せず GPI から除外する。
            warnings.append(
                f"区画 {u.区画}: 稼働中だが月額賃料（必須）が欠損のため GPI から除外しました（補完なし）。"
            )
            continue
        if u.cam_treated_as_zero:
            # 任意項目（共益費）の欠損は 0 として算入し、その旨を明記する。
            warnings.append(
                f"区画 {u.区画}: 共益費（任意）が欠損のため 0 として算入しました（missing_info に記録）。"
            )
        r = u.月額賃料_円
        c = u.月額共益費_円 if u.月額共益費_円 is not None else 0.0
        rent_income += r * 12
        cam_income += c * 12

        # 付帯収入（opt-in 時のみ算入）— 水道代は収入サイド・費用サイドと混同しない
        if oi_config.include_in_gpi:
            for key in oi_config.columns:
                monthly_oi = u.get_optional_income(key)
                if monthly_oi is not None:
                    optional_income_total += monthly_oi * 12

    gpi = rent_income + cam_income + optional_income_total

    notes.append("GPI は稼働区画の現行賃料ベース（年額）で集計しています。")
    if oi_config.include_in_gpi and oi_config.columns:
        notes.append(
            f"付帯収入（{', '.join(oi_config.columns)}）を GPI に算入しました（opt-in）。"
        )

    # --- 空室損失 -------------------------------------------------------
    if assumptions.vacancy_rate is None:
        vacancy_rate = 0.0
        warnings.append("空室損失率が未設定のため空室損失を 0 として計算しました（補完なし）。")
    else:
        vacancy_rate = assumptions.vacancy_rate
    vacancy_loss = gpi * vacancy_rate
    egi = gpi - vacancy_loss

    # --- 運営費用 -------------------------------------------------------
    opex_breakdown: dict[str, float] = {}
    opex_total = 0.0
    for name, amount in assumptions.opex.items():
        if amount is None:
            warnings.append(f"運営費用「{name}」が欠損のため算入していません（補完なし）。")
            continue
        opex_breakdown[name] = float(amount)
        opex_total += float(amount)

    if any(v is None for v in assumptions.opex.values()):
        warnings.append(
            "運営費用に欠損があるため、運営費用は過小・収益試算値は過大に出ている可能性があります。"
        )

    noi = egi - opex_total

    # --- 資本的支出控除 → 純収益 ---------------------------------------
    if assumptions.capex is None:
        capex = 0.0
        warnings.append("資本的支出が未設定のため 0 として計算しました（補完なし）。")
    else:
        capex = float(assumptions.capex)
    net_income = noi - capex

    return NOIResult(
        gpi=gpi,
        vacancy_loss=vacancy_loss,
        egi=egi,
        opex_total=opex_total,
        opex_breakdown=opex_breakdown,
        capex=capex,
        noi=noi,
        net_income=net_income,
        warnings=warnings,
        notes=notes,
        rent_income=rent_income,
        cam_income=cam_income,
        optional_income_total=optional_income_total,
    )
