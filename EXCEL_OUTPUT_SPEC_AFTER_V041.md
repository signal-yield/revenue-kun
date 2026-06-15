# Excel Output Spec After v0.4.1

## 1. Purpose

This document defines the approved Excel output workflow for revenue-kun after v0.4.1.

revenue-kun is not a Markdown report generator.
The user-facing artifact is an Excel workbook that allows users to:

- inspect the extracted rent roll from the input PDF,
- edit vacant-unit assumptions and other editable cells directly in Excel, and
- refine the direct capitalization (直接還元法) calculation.

The approved sample workbook is:
`revenue_kun_direct_cap_output_template_v7_vacant_note_unified.xlsx`

> **重要**: 本ツールは不動産鑑定評価ではありません。出力される金額は「収益試算値」であり、
> 鑑定評価による「収益価格」ではありません。欠損項目は補完しません。

---

## 2. Approved Input / Output Model

| Item | Value |
|------|-------|
| Input | Rent roll PDF |
| Output | Excel workbook (`.xlsx`) |
| Parser scope | Text-based PDFs only |
| OCR support | Not implemented |
| Scanned PDF support | Out of scope |

The output workbook is the primary deliverable.
The tool does not produce a Markdown summary, a plain-text report, or a JSON payload as a final output.

---

## 3. Output Workbook Structure

The output workbook contains the following sheets:

| Sheet name | Role |
|------------|------|
| `直接還元法_OER` | Direct capitalization summary and OER calculation |
| `直接還元法‗費用詳細版` | Detailed expense input sheet |
| `読み取りレントロール` | Extracted rent roll rows from the PDF |

No additional sheets are created automatically.

---

## 4. 直接還元法_OER Sheet Behavior

Only the following cells are automatically linked from `読み取りレントロール` at this stage:

| Cell | Label |
|------|-------|
| E2 | 年額貸室賃料収入 |
| E3 | 年額共益費収入 |
| E5 | 年額水道光熱費収入 |
| E6 | 年額駐車場収入 |
| E7 | その他収入 |

These cells reference the annual total rows in `読み取りレントロール`.

**Do not multiply by 12 in the OER sheet.**
The `読み取りレントロール` sheet already provides annual totals.
The OER sheet reads annual figures directly; no further annualization is applied there.

All other inputs on `直接還元法_OER` (空室損失率, 貸倒損失, 経費率, 還元利回り, etc.) remain user-editable.

---

## 5. 読み取りレントロール Sheet Behavior

This sheet contains the extracted rent roll rows populated from the input PDF.

### Row layout

- One row per unit, populated from PDF extraction.
- Users edit extracted cells directly in Excel — there is no split between "PDF read" columns and "user input" columns.
- If a unit is vacant, the `備考` cell should contain:

  ```
  ユーザーが賃料等を入力可能
  ```

### Total rows

The sheet includes a **monthly total row** with one cell per income category:

| Category | Label |
|----------|-------|
| 賃料 | 月額賃料合計 |
| 共益費 | 月額共益費合計 |
| 水道光熱費 | 月額水道光熱費合計 |
| 駐車場 | 月額駐車場合計 |
| その他収入 | 月額その他収入合計 |

Directly below the monthly total row, the sheet includes an **annual total row**:

| Category | Label |
|----------|-------|
| 賃料 | 年額賃料合計 |
| 共益費 | 年額共益費合計 |
| 水道光熱費 | 年額水道光熱費合計 |
| 駐車場 | 年額駐車場合計 |
| その他収入 | 年額その他収入合計 |

Annual total row formulas convert monthly totals to annual totals (monthly total × 12).

### Formatting rules

- Annual total row has borders.
- No unnecessary borders below the annual total row.
- All numeric money values use thousands separators.

---

## 6. User-Editable Assumptions

The following inputs are user-editable and are not populated automatically from the PDF:

| Assumption | Sheet |
|------------|-------|
| 空室損失率 | `直接還元法_OER` |
| 駐車場等の空室損失率 | `直接還元法_OER` |
| 貸倒損失 | `直接還元法_OER` |
| 経費率 | `直接還元法_OER` |
| 資本的支出 | `直接還元法_OER` |
| 還元利回り | `直接還元法_OER` |
| Detailed expense line items | `直接還元法‗費用詳細版` |

Users also edit rent roll cells directly in `読み取りレントロール`, including vacant-unit income assumptions.

---

## 7. Formula Requirements

- Annual total row formulas in `読み取りレントロール` must be: `= monthly_total_cell × 12`
- OER sheet income cells (E2, E3, E5, E6, E7) must reference the corresponding annual total cells in `読み取りレントロール` directly, without an additional `× 12` factor.
- All formula references must use standard Excel cell references (e.g., `=読み取りレントロール!C42`).
- No hardcoded values for income figures — all income values flow from `読み取りレントロール`.

---

## 8. Formatting Requirements

| Requirement | Detail |
|-------------|--------|
| Thousands separators | All numeric money cells use `#,##0` or equivalent format |
| Annual total row borders | Full border on all cells of the annual total row |
| Below annual total row | No borders (clean termination) |
| Vacant unit 備考 | Cell text: `ユーザーが賃料等を入力可能` |
| Sheet names | Exact as specified in Section 3 |

---

## 9. Out of Scope

The following are explicitly out of scope for this spec:

| Out of scope | Detail |
|--------------|--------|
| OCR | Not implemented |
| Scanned PDF support | Not implemented |
| Real-world PDF verification | Not claimed. Qualifying real-world text-based evaluation pending (Issue #21). |
| Formal appraisal | Not provided. Output is 収益試算値, not 鑑定評価額. |
| Investment advice | Not provided. |
| Legal advice | Not provided. |
| Tax advice | Not provided. |
| Fully automated judgment | Not intended. User must verify and edit assumptions. |
| Completed Claude Skill release | The Claude Skill integration has not been released. This spec does not claim it. |
| Private PDFs / PII | No private PDFs, tenant names, property names, or local paths are committed. |

---

## 10. How This Changes the Next Roadmap

Before v0.4.1, the primary output was a CLI-printed summary or Markdown report.

After this spec, the primary output is the Excel workbook.
This reorients the implementation roadmap as follows:

| Before | After |
|--------|-------|
| CLI prints a text/Markdown summary | CLI writes an `.xlsx` workbook |
| GPI is computed and printed inline | GPI flows into `直接還元法_OER` via `読み取りレントロール` |
| User reads output in terminal | User opens output in Excel, edits assumptions |
| No capitalization output | Direct capitalization output is the core deliverable |

The PDF parser (v0.4.1) remains the upstream input stage.
The Excel output stage is the new downstream deliverable to be implemented.

---

## 11. Next Implementation Tasks

| Priority | Task | Notes |
|----------|------|-------|
| 1 | Implement `読み取りレントロール` sheet population from PDF extraction | Writes extracted unit rows, monthly totals, annual totals |
| 2 | Implement `直接還元法_OER` sheet with linked income cells | E2/E3/E5/E6/E7 reference annual totals from `読み取りレントロール` |
| 3 | Implement `直接還元法‗費用詳細版` sheet | User-editable detailed expense inputs |
| 4 | Apply formatting (thousands separators, borders, vacant-unit 備考) | Per Section 8 |
| 5 | Write integration tests against the approved template | Validate sheet names, formula structure, cell references |
| 6 | Update CLI to accept PDF input and write `.xlsx` output | Replace or augment current print-to-terminal behavior |

Implementation tasks are tracked via Issue #48 and follow-on issues.

---

*Created: 2026-06-15*
*Approved template: revenue_kun_direct_cap_output_template_v7_vacant_note_unified.xlsx*
*Based on: v0.4.1 (tag/release), main HEAD 5a5505d*
