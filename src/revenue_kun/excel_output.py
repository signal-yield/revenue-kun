"""Excel workbook generation for direct capitalization output.

Produces a three-sheet .xlsx workbook:

  Sheet 1: 直接還元法_OER        -- direct cap summary; E2/E3/E5/E6/E7 linked
  Sheet 2: 直接還元法‗費用詳細版 -- detailed expense input (user-editable)
  Sheet 3: 読み取りレントロール    -- extracted rent roll with monthly+annual totals

IMPORTANT: OER cells E2/E3/E5/E6/E7 reference annual total cells in
読み取りレントロール directly.  They do NOT multiply by 12 because
読み取りレントロール already provides annual totals (monthly_total * 12).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from .rent_roll import RentRollUnit

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_VACANT_NOTE = "ユーザーが賃料等を入力可能"
_MONEY_FORMAT = "#,##0"

# Exact sheet names.  費用詳細版 uses U+2017 DOUBLE LOW LINE, not U+005F underscore.
SHEET_OER = "直接還元法_OER"
SHEET_EXPENSE = "直接還元法‗費用詳細版"
SHEET_RENT_ROLL = "読み取りレントロール"

# Column positions in 読み取りレントロール (1-based, openpyxl convention)
_C_ROOM = 1     # 部屋番号
_C_STATUS = 2   # ステータス
_C_RENT = 3     # 月額賃料
_C_CAM = 4      # 月額共益費
_C_UTIL = 5     # 月額水道光熱費
_C_PARKING = 6  # 月額駐車場
_C_OTHER = 7    # 月額その他収入
_C_NOTES = 8    # 備考
_INCOME_COLS = (_C_RENT, _C_CAM, _C_UTIL, _C_PARKING, _C_OTHER)

# OER sheet: (cell_ref, label, income_col_in_rent_roll).
# E4 is intentionally absent -- that row is left for user customization.
_OER_INCOME_CELLS = [
    ("E2", "年額貸室賃料収入",    _C_RENT),
    ("E3", "年額共益費収入",      _C_CAM),
    ("E5", "年額水道光熱費収入",  _C_UTIL),
    ("E6", "年額駐車場収入",      _C_PARKING),
    ("E7", "その他収入",          _C_OTHER),
]

# Styles
_THIN = Side(style="thin")
_FULL_BORDER = Border(left=_THIN, right=_THIN, top=_THIN, bottom=_THIN)
_HEADER_FILL = PatternFill("solid", fgColor="305496")
_HEADER_FONT = Font(color="FFFFFF", bold=True)
_BOLD = Font(bold=True)
_WARN_FONT = Font(color="C00000")


# ---------------------------------------------------------------------------
# Public dataclass
# ---------------------------------------------------------------------------

@dataclass
class DirectCapRow:
    """One unit row for direct-capitalization Excel output.

    Covers the five income columns required by the spec (賃料/共益費/
    水道光熱費/駐車場/その他収入).  The latter three default to None
    because the current RentRollUnit does not track them; users fill
    them in Excel.
    """

    区画: str
    ステータス: str | None
    月額賃料: float | None
    月額共益費: float | None
    月額水道光熱費: float | None = None
    月額駐車場: float | None = None
    月額その他収入: float | None = None
    備考: str | None = None

    @classmethod
    def from_rent_roll_unit(cls, unit: RentRollUnit) -> DirectCapRow:
        """Convert a RentRollUnit to a DirectCapRow.

        Fields absent from RentRollUnit (水道光熱費/駐車場/その他収入) are
        left as None so the user can fill them in Excel.
        Vacant units receive the standard 備考 note automatically.
        """
        note = _VACANT_NOTE if not unit.is_occupied else None
        return cls(
            区画=unit.区画,
            ステータス=unit.稼働状況,
            月額賃料=unit.月額賃料_円,
            月額共益費=unit.月額共益費_円,
            月額水道光熱費=None,
            月額駐車場=None,
            月額その他収入=None,
            備考=note,
        )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def write_direct_cap_workbook(
    path: str | Path,
    rows: list[DirectCapRow],
) -> None:
    """Write the three-sheet direct-capitalization workbook to *path*.

    Sheet order: 直接還元法_OER / 直接還元法‗費用詳細版 / 読み取りレントロール

    OER cells E2/E3/E5/E6/E7 contain cross-sheet references to the annual
    total row in 読み取りレントロール.  They do NOT multiply by 12.
    """
    wb = Workbook()

    # Build the rent roll sheet first to know the annual_total_row index.
    rr_ws = wb.active
    rr_ws.title = SHEET_RENT_ROLL
    annual_total_row = _build_rent_roll_sheet(rr_ws, rows)

    # Insert OER as sheet 0 (leftmost tab).
    oer_ws = wb.create_sheet(SHEET_OER, 0)
    _build_oer_sheet(oer_ws, annual_total_row)

    # Insert expense detail as sheet 1 (between OER and rent roll).
    exp_ws = wb.create_sheet(SHEET_EXPENSE, 1)
    _build_expense_sheet(exp_ws)

    # Remove the default empty sheet created by Workbook().
    if "Sheet" in wb.sheetnames:
        del wb["Sheet"]

    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    wb.save(dest)


# ---------------------------------------------------------------------------
# Sheet builders (private)
# ---------------------------------------------------------------------------

def _build_rent_roll_sheet(ws, rows: list[DirectCapRow]) -> int:
    """Populate 読み取りレントロール.  Returns the annual_total_row (1-based)."""
    headers = [
        "部屋番号", "ステータス",
        "月額賃料", "月額共益費", "月額水道光熱費", "月額駐車場", "月額その他収入",
        "備考",
    ]
    ws.append(headers)
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = _HEADER_FILL
        cell.font = _HEADER_FONT
        cell.alignment = Alignment(horizontal="center")

    # Data rows
    data_start = 2
    for offset, row in enumerate(rows):
        r = data_start + offset
        note = row.備考
        if note is None and _is_vacant(row.ステータス):
            note = _VACANT_NOTE
        ws.cell(r, _C_ROOM,    row.区画)
        ws.cell(r, _C_STATUS,  row.ステータス or "")
        ws.cell(r, _C_RENT,    row.月額賃料)
        ws.cell(r, _C_CAM,     row.月額共益費)
        ws.cell(r, _C_UTIL,    row.月額水道光熱費)
        ws.cell(r, _C_PARKING, row.月額駐車場)
        ws.cell(r, _C_OTHER,   row.月額その他収入)
        ws.cell(r, _C_NOTES,   note)
        for c in _INCOME_COLS:
            ws.cell(r, c).number_format = _MONEY_FORMAT

    n = len(rows)
    data_end = data_start + n - 1  # last data row (inclusive)
    monthly_row = data_start + n       # row after last data row
    annual_row = monthly_row + 1

    # Monthly total row
    ws.cell(monthly_row, _C_ROOM, "月計")
    ws.cell(monthly_row, _C_NOTES, "月額合計")
    for c in _INCOME_COLS:
        col_letter = get_column_letter(c)
        if n > 0:
            formula = f"=SUM({col_letter}{data_start}:{col_letter}{data_end})"
        else:
            formula = "=0"
        cell = ws.cell(monthly_row, c, formula)
        cell.number_format = _MONEY_FORMAT

    # Annual total row  (monthly * 12, with full border)
    ws.cell(annual_row, _C_ROOM, "年計")
    ws.cell(annual_row, _C_NOTES, "年額合計")
    for c in _INCOME_COLS:
        col_letter = get_column_letter(c)
        monthly_cell_ref = f"{col_letter}{monthly_row}"
        formula = f"={monthly_cell_ref}*12"
        cell = ws.cell(annual_row, c, formula)
        cell.number_format = _MONEY_FORMAT
        cell.border = _FULL_BORDER

    return annual_row


def _build_oer_sheet(ws, annual_total_row: int) -> None:
    """Populate 直接還元法_OER.

    E2/E3/E5/E6/E7 reference the annual total row in 読み取りレントロール.
    No *12 is applied here -- annual totals are already in 読み取りレントロール.
    """
    ws["A1"] = "直接還元法（収益試算）"
    ws["A1"].font = Font(bold=True, size=14)
    ws["A2"] = "※ 本値は「収益試算値」であり「収益価格」ではありません。"
    ws["A2"].font = _WARN_FONT

    ws["D4"] = "収入項目"
    ws["E4"] = "年額（円）"
    ws["D4"].font = _BOLD
    ws["E4"].font = _BOLD

    for cell_ref, label, income_col in _OER_INCOME_CELLS:
        row_num = int(cell_ref[1:])
        col_letter = get_column_letter(income_col)
        ws.cell(row_num, 4, label)  # D column label
        # Cross-sheet reference -- NO *12
        formula = f"={SHEET_RENT_ROLL}!{col_letter}{annual_total_row}"
        ws[cell_ref] = formula
        ws[cell_ref].number_format = _MONEY_FORMAT

    # User-editable assumption rows
    assumption_labels = {
        9:  "空室損失率",
        10: "駐車場等の空室損失率",
        11: "貸倒損失",
        12: "経費率",
        13: "資本的支出",
        14: "還元利回り",
    }
    for row_num, label in assumption_labels.items():
        ws.cell(row_num, 4, label).font = _BOLD
        ws.cell(row_num, 5).number_format = "0.000%"


def _build_expense_sheet(ws) -> None:
    """Populate 直接還元法‗費用詳細版 with a minimal user-editable structure."""
    ws["A1"] = "直接還元法 費用詳細版（ユーザー入力）"
    ws["A1"].font = Font(bold=True, size=13)
    ws["A2"] = "※ 各費用は実費または想定値を入力してください。"
    ws["A2"].font = _WARN_FONT

    ws["A4"] = "費目"
    ws["B4"] = "年額（円）"
    ws["A4"].font = _BOLD
    ws["B4"].font = _BOLD

    expense_labels = [
        "管理費・管理委託費",
        "修繕費",
        "損害保険料",
        "固定資産税・都市計画税",
        "その他費用",
    ]
    for i, label in enumerate(expense_labels, start=5):
        ws.cell(i, 1, label)
        ws.cell(i, 2).number_format = _MONEY_FORMAT


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_vacant(status: str | None) -> bool:
    """Return True if *status* indicates a vacant unit."""
    s = (status or "").strip()
    return any(k in s for k in ("空室", "空き", "募集"))
