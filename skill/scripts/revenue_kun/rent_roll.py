"""レントロール（賃貸借明細）の読み込み。

Phase 1 ではダミーCSV（data/dummy_rent_roll.csv）を読み込む。
Phase 2 以降で PDF 抽出結果をこの構造に流し込む想定。
空欄セルは推測補完せず None として保持する。
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RentRollUnit:
    """1区画分の賃貸借情報。賃料等が不明なら None。"""

    区画: str
    用途: str | None
    賃借人: str | None
    専有面積_m2: float | None
    月額賃料_円: float | None
    月額共益費_円: float | None
    稼働状況: str | None
    契約満了日: str | None
    # 付帯収入（optional income）— opt-in 時のみ GPI に算入
    # 水道代は収入サイド（運営費用の水道光熱費とは別管理）
    月額水道代_円: float | None = None
    月額駐車場収入_円: float | None = None
    月額その他収入_円: float | None = None

    def get_optional_income(self, key: str) -> float | None:
        """canonical key で付帯収入の月額を取得する。"""
        _map: dict[str, float | None] = {
            "water": self.月額水道代_円,
            "parking": self.月額駐車場収入_円,
            "other_income": self.月額その他収入_円,
        }
        return _map.get(key)

    @property
    def is_occupied(self) -> bool:
        # CSV は「稼働」、PDF は「入居」を稼働中として扱う
        return (self.稼働状況 or "").strip() in ("稼働", "入居", "賃貸中", "使用中")

    @property
    def cam_treated_as_zero(self) -> bool:
        """共益費（任意項目）が欠損のため 0 として扱ったかどうか。"""
        return self.月額賃料_円 is not None and self.月額共益費_円 is None

    @property
    def 月額収入_円(self) -> float | None:
        """賃料＋共益費の月額合計。

        - 月額賃料（必須）が欠損なら None を返す（GPI から除外され、補完しない）。
        - 共益費（任意）が欠損なら 0 として扱う（補完ではなく明示的な 0 算入）。
        """
        if self.月額賃料_円 is None:
            return None
        cam = self.月額共益費_円 if self.月額共益費_円 is not None else 0.0
        return self.月額賃料_円 + cam


def _to_float(value: str | None) -> float | None:
    """空欄・空白は None。数値化できればfloat。"""
    if value is None:
        return None
    s = value.strip()
    if s == "":
        return None
    return float(s.replace(",", ""))


def _to_str(value: str | None) -> str | None:
    if value is None:
        return None
    s = value.strip()
    return s if s != "" else None


def load_rent_roll(path: str | Path) -> list[RentRollUnit]:
    """ダミーCSVからレントロールを読み込む。"""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"レントロールCSVが見つかりません: {path}")

    units: list[RentRollUnit] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            units.append(
                RentRollUnit(
                    区画=_to_str(row.get("区画")) or "",
                    用途=_to_str(row.get("用途")),
                    賃借人=_to_str(row.get("賃借人")),
                    専有面積_m2=_to_float(row.get("専有面積_m2")),
                    月額賃料_円=_to_float(row.get("月額賃料_円")),
                    月額共益費_円=_to_float(row.get("月額共益費_円")),
                    稼働状況=_to_str(row.get("稼働状況")),
                    契約満了日=_to_str(row.get("契約満了日")),
                )
            )
    return units
