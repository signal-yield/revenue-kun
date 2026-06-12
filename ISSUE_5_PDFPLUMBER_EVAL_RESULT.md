# Issue #5 pdfplumber Evaluation Result

## Date
2026-06-12

## Purpose
Evaluate pdfplumber extraction behavior against synthetic-realistic rent roll PDFs.

## Samples
PDF files were generated under `samples/private/` via reportlab and are not committed.

| File | Description |
|------|-------------|
| `sample_a_simple_text_rentroll.pdf` | Single-page, clean table, standard Japanese column names |
| `sample_b_japanese_layout_variation.pdf` | Title block above table, real-world column name variants |
| `sample_c_hard_case_layout.pdf` | Sub-header rows (【1F区画】/【2F区画】) separating unit groups |

All data is fully fabricated. No real tenant names, properties, or rents.

---

## Sample A: Simple text-based rent roll

**Column names in PDF**: 部屋番号 / 用途 / 専有面積（㎡）/ 月額賃料（円）/ 月額共益費（円）/ 入居状況

- **Table detected**: YES — `extract_table()` returned 9 rows (1 header + 8 data rows)
- **Text extracted**: YES — `extract_text()` returned 9 lines
- **Column mapping feasibility**: All 6 columns mapped by existing alias logic without modification
  - 部屋番号 → `room` ✅
  - 月額賃料（円）→ `rent` (via "賃料" substring) ✅
  - 月額共益費（円）→ `cam` (via "共益" substring) ✅
  - 入居状況 → `status` (via "入居" substring) ✅
  - 専有面積（㎡）→ `area` (via "面積" substring) ✅
  - 用途 → `use` ✅
- **Extraction result**: 8 units, 0 required missing, 4 optional missing
  - 2 vacant units (201, 302): 想定賃料 logged as optional missing ✅
  - 2 assumption-side items (建築時期, 管理委託費): expected ✅
- **GPI**: 7,584,000 / **NOI**: −295,200 / **indicated_value**: −28,782,222
  - Note: negative NOI is due to assumptions.sample.yaml opex being calibrated for a larger property — NOT an extraction error. With correctly matched assumptions this would be positive.
- **Observations**: Output files (missing_info.md / xlsx / extraction_log.json) all generated correctly. Disclaimer present. Extraction is fully accurate.
- **Judgment: PASS**

---

## Sample B: Japanese realistic layout variation

**Column names in PDF**: 号室 / 用途区分 / 面積 / 賃料（税抜）/ 管理費 / 空室/入居

- **Table detected**: YES — `extract_table()` returned 8 rows (1 header + 7 data rows); title block and note paragraph above the table were correctly ignored
- **Text extracted**: YES — 10 lines (includes title and note)
- **Column mapping feasibility**: All 6 columns mapped by existing alias logic without modification
  - 号室 → `room` (via "号室" alias) ✅
  - 用途区分 → `use` (via "用途" substring) ✅
  - 面積 → `area` ✅
  - 賃料（税抜）→ `rent` (via "賃料" substring) ✅
  - 管理費 → `cam` (via "管理" substring) ✅
  - 空室/入居 → `status` (via "入居" or "空室" substring) ✅
- **Extraction result**: 7 units, 0 required missing, 4 optional missing
  - 区画102: 管理費 blank → 0扱い (optional missing) ✅
  - 区画202: 賃料 blank + 空室 → 想定賃料 as optional missing ✅
- **GPI**: 8,136,000 / **NOI**: 229,200 / **indicated_value**: −17,128,889
  - Note: indicated_value negative due to same assumptions mismatch as Sample A.
- **Observations**: Title block above table did not interfere with `extract_table()`. Blank cells preserved and handled correctly. Column name variants all resolved by existing alias mapping.
- **Judgment: PASS**

---

## Sample C: Hard case layout

**Column names in PDF**: 部屋番号 / 用途 / 面積（㎡）/ 月額賃料（円）/ 共益費（円）/ 状況

- **Table detected**: YES — `extract_table()` returned 9 rows (1 header + 8 rows including 2 sub-header rows)
- **Text extracted**: YES — 10 lines
- **Column mapping feasibility**: All 6 columns mapped correctly. "状況" → `status` via alias ✅. "賃貸中" in `is_occupied` list ✅.
- **Extraction result**: 8 units reported — but 2 are spurious sub-header rows
  - `【1F区画】`: treated as a vacant unit (status=None → is_occupied=False). No rent, no area → 2 optional missing entries generated.
  - `【2F区画】`: same.
  - Real data units: 6 (101, 102, 103, 201, 202, 203)
  - Reported units: 8 (6 real + 2 spurious sub-header rows)
- **GPI**: 6,096,000 (only real units contribute; sub-header rows add 0) — GPI value is accurate for the 6 real units
- **NOI**: −1,708,800 / **indicated_value**: −60,195,556 (assumptions mismatch, same as A/B)
- **Observations**:
  - No crash; exit code 0. The tool does not fail — it silently treats sub-header rows as vacant units.
  - `extraction_log.json` reports `extracted_units_count: 8` — inflated by 2.
  - `missing_info.md` contains spurious entries for `【1F区画】` and `【2F区画】`.
  - **Root cause**: `extract_table()` correctly detects the merged sub-header rows as table rows. Revenue-kun has no filter to skip rows where the room number matches a non-unit pattern (e.g., `【.*】`).
  - **Fix scope**: A simple row filter (skip rows where room field matches `【.*】` or similar bracket pattern) would resolve this. Estimated effort: small, localized to `pdf_extract.py`.
- **Judgment: PARTIAL** — table detected and columns mapped, but sub-header rows pollute unit count and missing_info. Output requires manual review to identify spurious entries.

---

## Overall findings

| Sample | Table detected | Columns mapped | Accurate output | Judgment |
|--------|:--------------:|:--------------:|:---------------:|:--------:|
| A: Simple text | YES | YES (no changes needed) | YES | **PASS** |
| B: Layout variation | YES | YES (no changes needed) | YES | **PASS** |
| C: Sub-header rows | YES | YES | PARTIAL (spurious rows) | **PARTIAL** |

Key findings:

1. **pdfplumber `extract_table()` is robust for single-page text tables** — including those with title blocks and paragraphs above the table.
2. **Existing alias mapping covers common real-world Japanese column name variants** — 号室, 管理費, 空室/入居, 賃料（税抜）, 用途区分 all resolved without code changes.
3. **Sub-header rows are the primary failure mode** — merged rows used as section dividers (e.g., 【1F区画】) are treated as vacant units. This is the most likely issue in real-world rent roll PDFs from property management systems.
4. **Blank cells are handled correctly** — both required and optional blank cells produce appropriate missing_info entries.
5. **Negative NOI in all samples** reflects assumptions.sample.yaml opex being calibrated for a different property scale — not an extraction defect.

---

## v0.2.0 recommendation

**Include text-based single-page PDF ingestion in v0.2.0**, with the following scope:

| Item | v0.2.0 scope |
|------|:------------:|
| Clean single-page text table (Sample A class) | ✅ Already works |
| Column alias variants — 号室, 管理費, 空室/入居 etc. (Sample B class) | ✅ Already works |
| Sub-header row filter for `【section】`-style rows (Sample C fix) | ✅ Small fix, include |
| OCR / scanned PDF | ❌ Defer to v0.3.0+ |
| Multi-page PDF merging | ❌ Defer to v0.3.0+ |
| Complex merged-cell layouts | ❌ Defer to v0.3.0+ |
| Automated PII masking | ❌ Separate issue |

The sub-header row filter is a small, localized change to `pdf_extract.py` (add a row-skip predicate). It should be included in v0.2.0 to prevent silent miscounts.

---

## Follow-up issues

- **Sub-header row filter** (v0.2.0): Skip rows where room field matches bracket patterns (`【…】`, `[…]`, or all-blank data columns). Localized to `pdf_extract.py`.
- **OCR investigation** (v0.3.0+): tesseract / cloud OCR for scanned PDFs. Open separate issue.
- **Multi-page PDF handling** (v0.3.0+): concatenate tables across pages. Open separate issue.
- **Field mapping configuration** (v0.3.0+): user-configurable `column_map.yaml` for site-specific column names beyond current alias list.
- **Assumptions calibration guidance**: README note clarifying that `assumptions.sample.yaml` is calibrated for the bundled synthetic data and should be replaced for real properties.
