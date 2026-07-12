"""assumptions.yaml の読み込みと検証。

欠損（null）はここでは補完せず、そのまま保持して後段の欠損検出に渡す。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from numbers import Real
from pathlib import Path
from typing import Any

import yaml


class AssumptionsError(ValueError):
    """assumptions.yaml の入力値が不正な場合に送出する（壊れた計算を継続しない）。"""


# 付帯収入として認識する canonical key の集合。
# pdf_extract._HEADER_KEYS のエントリと対応させること。
OPTIONAL_INCOME_CANONICAL_KEYS: frozenset[str] = frozenset(
    {"water", "parking", "other_income"}
)


@dataclass
class OptionalIncomeConfig:
    """付帯収入（水道代・駐車場収入・その他収入）の GPI 算入制御。

    include_in_gpi=False（デフォルト）のとき付帯収入は GPI に算入しない。
    include_in_gpi=True かつ columns に指定した canonical key のみ GPI に算入する。
    有効な columns: water / parking / other_income
    """

    include_in_gpi: bool = False
    columns: list[str] = field(default_factory=list)


@dataclass
class Assumptions:
    """assumptions.yaml の内容を保持する。null はそのまま None で保持する。"""

    property_info: dict[str, Any]
    cap_rate: float | None            # 還元利回り
    vacancy_rate: float | None        # 空室損失率
    opex: dict[str, float | None]     # 運営費用（項目→年額 or None）
    capex: float | None               # 資本的支出（年額）
    sensitivity_cap_deltas: list[float] = field(default_factory=list)
    sensitivity_noi_rates: list[float] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)
    optional_income: OptionalIncomeConfig = field(default_factory=OptionalIncomeConfig)


def load_assumptions(path: str | Path) -> Assumptions:
    """assumptions.yaml を読み込む。

    必須キーが存在しない場合は KeyError を送出するが、値が null の場合は
    補完せず None のまま保持する（欠損検出は missing モジュールが担当）。
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"assumptions.yaml が見つかりません: {path}")

    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    sens = raw.get("感応度分析", {}) or {}
    oi_raw = raw.get("optional_income", {}) or {}
    optional_income = OptionalIncomeConfig(
        include_in_gpi=bool(oi_raw.get("include_in_gpi", False)),
        columns=[str(c) for c in (oi_raw.get("columns") or [])],
    )

    return Assumptions(
        property_info=raw.get("物件", {}) or {},
        cap_rate=raw.get("還元利回り"),
        vacancy_rate=raw.get("空室損失率"),
        opex=raw.get("運営費用", {}) or {},
        capex=raw.get("資本的支出"),
        sensitivity_cap_deltas=sens.get("還元利回り変動幅", []) or [],
        sensitivity_noi_rates=sens.get("NOI変動率", []) or [],
        raw=raw,
        optional_income=optional_income,
    )


def _is_number(v: Any) -> bool:
    # bool は Real のサブクラスだが数値として扱わない
    return isinstance(v, Real) and not isinstance(v, bool)


def validate_assumptions(a: Assumptions) -> None:
    """前提条件の妥当性を検証する。

    1件でも問題があれば、すべての問題を列挙して AssumptionsError を送出する。
    （壊れた値のまま計算を継続しない。欠損の「補完」は一切行わない。）
    """
    errors: list[str] = []

    # --- 還元利回り（必須・正の数） -----------------------------------
    if a.cap_rate is None:
        errors.append("還元利回り(cap_rate) が未設定です（必須項目）。")
    elif not _is_number(a.cap_rate):
        errors.append(f"還元利回り(cap_rate) が数値ではありません: {a.cap_rate!r}。")
    elif a.cap_rate <= 0:
        errors.append(f"還元利回り(cap_rate) は 0 より大きい必要があります: {a.cap_rate}。")

    # --- 空室損失率（必須・0〜1） -------------------------------------
    if a.vacancy_rate is None:
        errors.append("空室損失率(vacancy_rate) が未設定です（必須項目）。")
    elif not _is_number(a.vacancy_rate):
        errors.append(f"空室損失率(vacancy_rate) が数値ではありません: {a.vacancy_rate!r}。")
    elif not (0 <= a.vacancy_rate <= 1):
        errors.append(f"空室損失率(vacancy_rate) は 0〜1 の範囲である必要があります: {a.vacancy_rate}。")

    # --- 資本的支出（任意・指定時は 0 以上） --------------------------
    if a.capex is not None:
        if not _is_number(a.capex):
            errors.append(f"資本的支出(capex) が数値ではありません: {a.capex!r}。")
        elif a.capex < 0:
            errors.append(f"資本的支出(capex) は負の値にできません: {a.capex}。")

    # --- 運営費用（任意項目。null は許容するが、負の値・非数値は不可） ---
    for name, amount in a.opex.items():
        if amount is None:
            continue  # 欠損は許容（補完せず後段で missing 記録）
        if not _is_number(amount):
            errors.append(f"運営費用「{name}」が数値ではありません: {amount!r}。")
        elif amount < 0:
            errors.append(f"運営費用「{name}」は負の値にできません: {amount}。")

    if errors:
        raise AssumptionsError(
            "assumptions の入力値に問題があります（計算を中止しました）:\n  - "
            + "\n  - ".join(errors)
        )
