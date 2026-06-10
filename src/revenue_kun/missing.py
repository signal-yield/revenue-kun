"""欠損項目の検出。

【方針】欠損は決して推測補完しない。検出して列挙するだけ。
検出結果は missing_info.md と extraction_log.json の双方で利用する。

各欠損は `required`（必須/任意）で区分する:
  - required=True  : 還元利回り、稼働区画の月額賃料（必須セル）。
  - required=False : 共益費・面積・空室の想定賃料・運営費用・物件情報など（0扱い/記録のみ）。
"""
from __future__ import annotations

from dataclasses import dataclass

from .config import Assumptions
from .rent_roll import RentRollUnit


@dataclass
class MissingItem:
    category: str       # 区分（例: 物件情報 / 前提条件 / 運営費用 / レントロール）
    field: str          # 項目名
    location: str       # 出所（例: assumptions / sample_rentroll_simple.pdf 区画202）
    impact: str         # 欠損が計算に与える影響
    required: bool = False  # True=必須項目, False=任意項目


def detect_missing(
    assumptions: Assumptions,
    units: list[RentRollUnit],
    rent_roll_source: str = "rent_roll",
) -> list[MissingItem]:
    """前提条件とレントロールから欠損項目を洗い出す。"""
    items: list[MissingItem] = []

    # --- 物件情報（任意） ----------------------------------------------
    for key, value in assumptions.property_info.items():
        if value is None:
            items.append(
                MissingItem(
                    category="物件情報",
                    field=str(key),
                    location="assumptions: 物件",
                    impact="試算自体には影響しないが、報告書記載が不完全になる。",
                    required=False,
                )
            )

    # --- 直接還元法パラメータ ------------------------------------------
    if assumptions.cap_rate is None:
        items.append(
            MissingItem(
                category="前提条件",
                field="還元利回り",
                location="assumptions: 還元利回り",
                impact="必須項目。収益試算値を算定できない（致命的）。",
                required=True,
            )
        )
    if assumptions.vacancy_rate is None:
        items.append(
            MissingItem(
                category="前提条件",
                field="空室損失率",
                location="assumptions: 空室損失率",
                impact="任意項目。空室損失を 0 として計算するため、収益試算値が過大になりうる。",
                required=False,
            )
        )
    if assumptions.capex is None:
        items.append(
            MissingItem(
                category="前提条件",
                field="資本的支出",
                location="assumptions: 資本的支出",
                impact="任意項目。CAPEX 控除を 0 として計算するため、収益試算値が過大になりうる。",
                required=False,
            )
        )

    # --- 運営費用（任意） ----------------------------------------------
    for name, amount in assumptions.opex.items():
        if amount is None:
            items.append(
                MissingItem(
                    category="運営費用",
                    field=str(name),
                    location=f"assumptions: 運営費用.{name}",
                    impact="任意項目。当該費用を運営費用に算入できず、収益試算値が過大になりうる。",
                    required=False,
                )
            )

    # --- レントロール ---------------------------------------------------
    for u in units:
        loc = f"{rent_roll_source}: 区画{u.区画}"
        if u.is_occupied:
            if u.月額賃料_円 is None:
                # 必須セルの欠損 → 当該行は GPI から除外（計算は停止しない）
                items.append(
                    MissingItem(
                        category="レントロール",
                        field="月額賃料",
                        location=loc,
                        impact="必須項目。稼働区画だが賃料不明のため当該行を GPI から除外（補完なし）。収益試算値が過小になりうる。",
                        required=True,
                    )
                )
            if u.月額共益費_円 is None:
                items.append(
                    MissingItem(
                        category="レントロール",
                        field="月額共益費",
                        location=loc,
                        impact="任意項目。共益費不明のため 0 として算入（補完なし）。収益試算値が過小になりうる。",
                        required=False,
                    )
                )
        else:
            # 空室区画は市場賃料が不明。補完しない旨を明記。
            items.append(
                MissingItem(
                    category="レントロール",
                    field="想定（市場）賃料",
                    location=loc,
                    impact="任意項目。空室区画のため市場賃料を補完せず、満室想定の収益は反映していない。",
                    required=False,
                )
            )
        if u.専有面積_m2 is None:
            items.append(
                MissingItem(
                    category="レントロール",
                    field="専有面積",
                    location=loc,
                    impact="任意項目。面積不明のため坪単価等の検証ができない（計算には影響なし）。",
                    required=False,
                )
            )

    return items
