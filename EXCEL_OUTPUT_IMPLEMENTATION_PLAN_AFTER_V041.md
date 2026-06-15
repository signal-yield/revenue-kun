# Excel Output Implementation Plan After v0.4.1

## 1. Purpose

This document breaks the approved Excel output spec into safe, sequenced implementation steps.
It does not modify code — it is a planning document only.

> **重要**: 本ツールは不動産鑑定評価ではありません。出力される金額は「収益試算値」であり、
> 鑑定評価による「収益価格」ではありません。欠損項目は補完しません。

---

## 2. Source of Truth

All Excel output behavior is governed by:

- **`EXCEL_OUTPUT_SPEC_AFTER_V041.md`** — merged in PR #51, main HEAD `adb7a58`
- **Approved template**: `revenue_kun_direct_cap_output_template_v7_vacant_note_unified.xlsx`

If this implementation plan conflicts with the spec, the spec takes precedence.

---

## 3. Current Parser / Output State

| Item | State |
|------|-------|
| PDF parser | v0.4.1 — text-based PDF extraction, 161 tests passing |
| Current output | CLI prints summary to terminal (text) |
| Excel output | Not yet implemented |
| OCR / scanned PDF | Not implemented, out of scope |
| Real-world PDF verification | Not claimed |

The v0.4.1 parser correctly extracts unit rows, occupancy status, and income figures from text-based rent roll PDFs.
This extraction output is the upstream input to the new Excel generation stage.

---

## 4. Required Excel Output Behavior

| Requirement | Detail |
|-------------|--------|
| Output format | `.xlsx` workbook |
| Sheets | `直接還元法_OER`, `直接還元法‗費用詳細版`, `読み取りレントロール` |
| Rent roll population | One row per unit from PDF extraction |
| Monthly total row | Summed by income category in `読み取りレントロール` |
| Annual total row | Monthly total × 12, directly below monthly total row |
| OER income cells | E2/E3/E5/E6/E7 reference annual total cells in `読み取りレントロール` |
| OER ×12 guard | OER sheet must NOT multiply by 12 — annual totals already in `読み取りレントロール` |
| Vacant-unit 備考 | `ユーザーが賃料等を入力可能` |
| Thousands separators | All numeric money cells |
| Annual total row borders | Full border |
| Below annual total row | No borders |

---

## 5. Data Mapping

### PDF extraction → 読み取りレントロール columns

| Source field | Target column | Notes |
|--------------|---------------|-------|
| Unit number / 部屋番号 | 部屋番号 | |
| Occupancy status / ステータス | ステータス | normalized: 入居 / 空室 |
| Monthly rent / 賃料 | 月額賃料 | blank if vacant |
| Common area fee / 共益費 | 月額共益費 | blank if vacant |
| Utilities / 水道光熱費 | 月額水道光熱費 | blank if vacant |
| Parking / 駐車場 | 月額駐車場 | blank if vacant |
| Other income / その他 | 月額その他収入 | blank if vacant |
| Notes / 備考 | 備考 | `ユーザーが賃料等を入力可能` if vacant |

### 読み取りレントロール totals → 直接還元法_OER

| 読み取りレントロール cell | OER cell | Label |
|--------------------------|----------|-------|
| 年額賃料合計 | E2 | 年額貸室賃料収入 |
| 年額共益費合計 | E3 | 年額共益費収入 |
| 年額水道光熱費合計 | E5 | 年額水道光熱費収入 |
| 年額駐車場合計 | E6 | 年額駐車場収入 |
| 年額その他収入合計 | E7 | その他収入 |

OER cell formulas take the form: `=読み取りレントロール!<annual_total_cell>`
No `* 12` is applied.

---

## 6. Workbook Generation Strategy

### Recommended library

- **openpyxl** — pure Python, no Excel installation required, supports formula strings and cell formatting.

### Generation approach

1. Create a new workbook from scratch (or clone the approved template).
2. Populate `読み取りレントロール`:
   a. Write header row.
   b. Write one data row per extracted unit.
   c. Write monthly total row (SUM formulas over data rows, per income column).
   d. Write annual total row (monthly total cell × 12, per income column).
   e. Apply borders to annual total row.
   f. Apply thousands-separator number format to all money columns.
3. Populate `直接還元法_OER`:
   a. Write static labels and user-editable assumption cells.
   b. Set E2/E3/E5/E6/E7 as cross-sheet references to annual total cells in `読み取りレントロール`.
4. Populate `直接還元法‗費用詳細版`:
   a. Write static structure with user-editable detailed expense inputs.
5. Save workbook to the output path specified via CLI argument.

### Template vs. scratch

Using the approved template as a base is preferred to preserve formatting, styles, and layout that are not fully specified here.
If generating from scratch, all formatting requirements in Section 8 must be applied explicitly.

---

## 7. Formula Requirements

| Location | Formula | Rule |
|----------|---------|------|
| `読み取りレントロール` monthly total row | `=SUM(<data_range>)` per income column | Sums occupied unit values only via SUM (blanks ignored) |
| `読み取りレントロール` annual total row | `=<monthly_total_cell>*12` per income column | Converts monthly to annual |
| `直接還元法_OER` E2 | `=読み取りレントロール!<年額賃料合計_cell>` | No ×12 |
| `直接還元法_OER` E3 | `=読み取りレントロール!<年額共益費合計_cell>` | No ×12 |
| `直接還元法_OER` E5 | `=読み取りレントロール!<年額水道光熱費合計_cell>` | No ×12 |
| `直接還元法_OER` E6 | `=読み取りレントロール!<年額駐車場合計_cell>` | No ×12 |
| `直接還元法_OER` E7 | `=読み取りレントロール!<年額その他収入合計_cell>` | No ×12 |

Summary rows from the PDF (合計, 小計, 総計, etc.) must be excluded before writing data rows — the v0.4.1 parser already handles this.

---

## 8. Formatting Requirements

| Requirement | Detail |
|-------------|--------|
| Thousands separators | `#,##0` number format on all money columns |
| Annual total row borders | `openpyxl` `Border(left=Side(...), right=..., top=..., bottom=...)` on all cells in the row |
| Below annual total row | No border style set |
| Vacant-unit 備考 text | `ユーザーが賃料等を入力可能` — written as cell value, not formula |
| Sheet tab names | Exact strings: `直接還元法_OER`, `直接還元法‗費用詳細版`, `読み取りレントロール` |

---

## 9. CLI / API Integration Plan

### Proposed CLI change

Current behavior:
```
python -m revenue_kun <pdf_path>
# prints summary to terminal
```

Proposed behavior:
```
python -m revenue_kun <pdf_path> --output <output_path>.xlsx
# writes Excel workbook to <output_path>
```

- `--output` is optional; default output path: `<pdf_basename>_revenue_kun.xlsx` in the current directory.
- The terminal summary print may be retained alongside Excel output or suppressed via a flag.
- No breaking change to the existing parser logic — Excel generation is a new output stage downstream of extraction.

### Module structure

| Module | Role |
|--------|------|
| `src/revenue_kun/pdf_extract.py` | Existing — extracts unit rows from PDF (unchanged) |
| `src/revenue_kun/excel_writer.py` | New — builds the workbook from extracted rows |
| `src/revenue_kun/cli.py` | Updated — adds `--output` argument, calls `excel_writer` |

---

## 10. Test Plan

All tests should be added to `tests/` and run via `pytest`.

| # | Test | Assertion |
|---|------|-----------|
| 1 | Workbook has required sheets | `wb.sheetnames` contains all 3 sheet names exactly |
| 2 | OER cells contain cross-sheet formulas | E2/E3/E5/E6/E7 values start with `=読み取りレントロール!` |
| 3 | OER cells do not contain `*12` | Formula strings do not contain `*12` or `* 12` |
| 4 | Rent roll sheet has monthly total row | Row with 月額賃料合計 label exists |
| 5 | Rent roll sheet has annual total row | Row with 年額賃料合計 label exists, directly below monthly total row |
| 6 | Annual total row formulas exist | Cells in annual total row contain formula strings of the form `=<ref>*12` |
| 7 | Vacant-unit 備考 normalized | Vacant unit rows have `備考` = `ユーザーが賃料等を入力可能` |
| 8 | Thousands separators applied | Money column cells have `number_format` containing `#,##0` |
| 9 | No formula errors | No cell value equals `#REF!`, `#VALUE!`, `#NAME?`, or similar |
| 10 | Summary rows excluded from income totals | Rows with labels 合計/小計/総計/計/TOTAL are not written as data rows |
| 11 | Existing parser tests remain passing | Full test suite: 161 passed, 0 failed (baseline) |

Integration test fixture: use `realistic_anonymized_001` or a minimal synthetic fixture with known row count and income values.

---

## 11. Risks and Guardrails

| Risk | Mitigation |
|------|------------|
| Double ×12 annualization | OER cell formula test (test #3) explicitly checks for absence of `*12` |
| Summary rows counted as unit rows | Test #10 asserts summary labels are excluded; v0.4.1 parser already filters these |
| Sheet name typo (especially `‗` vs `_` in 費用詳細版) | Test #1 asserts exact sheet names including Unicode characters |
| Cross-sheet reference broken after save/reopen | openpyxl formula strings are written as-is; verify with Excel or xlrd after generation |
| Formatting not applied | Tests #7 and #8 assert number_format and 備考 text |
| Real-world PDF layout variation | Not in scope for this implementation phase; gated by Issue #21 |
| OCR / scanned PDF | Not implemented; parser scope unchanged from v0.4.1 |
| Private data in test fixtures | Use only anonymized or synthetic fixtures; no private PDFs or PII committed |

---

## 12. Proposed Implementation PR Sequence

| PR | Branch | Content | Dependency |
|----|--------|---------|------------|
| A | `feat/excel-writer-base` | Add `excel_writer.py`: workbook creation, sheet structure, rent roll population, monthly/annual totals, formatting | None |
| B | `feat/oer-sheet-linking` | Add OER sheet with E2/E3/E5/E6/E7 cross-sheet references; verify no ×12 in OER | PR A |
| C | `feat/expense-detail-sheet` | Add `直接還元法‗費用詳細版` sheet structure | PR A |
| D | `feat/cli-output-flag` | Add `--output` CLI flag; integrate `excel_writer` into CLI pipeline | PR A, B, C |
| E | `test/excel-writer-integration` | Integration tests covering all 11 items in Section 10 | PR D |

Each PR should pass the full test suite (161 + new tests) before merge.
No PR should touch the PDF parser logic in `pdf_extract.py` unless a regression is found.

---

*Created: 2026-06-15*
*Source of truth: EXCEL_OUTPUT_SPEC_AFTER_V041.md (merged PR #51, main adb7a58)*
*Approved template: revenue_kun_direct_cap_output_template_v7_vacant_note_unified.xlsx*
