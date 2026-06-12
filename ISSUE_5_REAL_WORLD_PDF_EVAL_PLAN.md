# Issue #5 Real-world PDF Evaluation Plan

## Date
2026-06-12

## Purpose
Evaluate whether revenue-kun can ingest real-world or realistic rent roll PDFs in v0.2.0+.
This document defines sample requirements, extraction targets, success criteria, privacy policy,
and the decision gate for whether real-world PDF support enters v0.2.0 or is deferred.

## Current baseline
- v0.1.0 passes CSV base and synthetic PDF E2E scenarios.
- v0.1.0 does not support real-world rent roll PDFs, OCR, multi-page merging, merged-cell layouts, or automated PII masking.
- v0.1.0 extraction relies on `pdfplumber` `page.extract_table()` against reportlab-generated single-page text tables.

---

## Evaluation samples

### Sample A: Text-based simple rent roll PDF
- **Description**: A single-page, text-based PDF with a clean tabular rent roll. Likely produced by a property management system or exported from Excel via PDF print. Column headers are standard (部屋番号 / 用途 / 面積 / 月額賃料 / 共益費 / 入居状況 or close variants). No merged cells, no images.
- **Expected difficulty**: Low. This is the best-case for `pdfplumber` and the closest analog to the v0.1.0 synthetic PDFs.
- **Required fields**: 部屋番号（または号室）、月額賃料、入居状況。面積・共益費はあれば望ましい。
- **Expected outcome**: PASS or PARTIAL. Table should be detected. Column alias mapping may need minor tuning for non-synthetic header variants.

### Sample B: Realistic layout variation PDF
- **Description**: A text-based PDF with layout variations common in practice — different column ordering, title rows above the data table, sub-headers (e.g. "1F区画" / "2F区画"), or a cover sheet preceding the rent roll table on page 2. Column names may differ (e.g., 賃料 instead of 月額賃料; 管理費 instead of 共益費; 区画 instead of 部屋番号).
- **Expected difficulty**: Medium. `pdfplumber` should detect the table body, but page selection and column mapping will require validation. Sub-headers or grouped rows may confuse `extract_table()`.
- **Required fields**: Same as Sample A. Alias mapping coverage will be the key evaluation point.
- **Expected outcome**: PARTIAL likely. Core fields extractable; layout-specific heuristics may be needed for page selection or row skipping.

### Sample C: Hard case PDF
- **Description**: A PDF that represents known failure modes: (a) scanned document requiring OCR, (b) multi-page rent roll with merged header cells spanning columns, or (c) a complex layout where unit rows are split across pages or use variable-width columns. May also be a PDF produced by a third-party property platform with non-standard encoding.
- **Expected difficulty**: High. One or more of OCR, merged-cell handling, multi-page concatenation, or encoding normalization will be required.
- **Required fields**: Same as Sample A, but extraction reliability is the evaluation target — not field completeness.
- **Expected outcome**: FAIL expected. Establishes the boundary of `pdfplumber`-only approach and clarifies what v0.3.0+ must address.

---

## Required extraction fields

The following fields must be evaluated for each sample:

| Field | Internal key | Required | Alias examples |
|-------|-------------|:--------:|----------------|
| Unit / room number | `room` | ✅ | 部屋番号, 号室, 区画, unit, room |
| Tenant occupancy status | `status` | ✅ | 入居状況, 入居, 稼働, 空室, status |
| Monthly rent | `rent` | ✅ | 月額賃料, 賃料, rent |
| Common area fee / service charge | `cam` | — | 共益費, 管理費, common_fee |
| Floor area | `area` | — | 面積, area |
| Use / type | `use` | — | 用途, use, type |
| Notes or remarks | — | — | 備考, 特記事項, remarks |

Fields marked ✅ are required by `RentRollExtractionError` logic. Missing required fields cause extraction to stop (exit code 2).

---

## Evaluation procedure

1. Place test PDFs under a **non-committed local folder** (e.g., `eval/real_pdfs/` — add to `.gitignore` if not already).
2. Run `pdfplumber` extraction via the existing CLI:
   ```powershell
   python src/main.py --assumptions assumptions.sample.yaml --rent-roll-pdf <path_to_pdf> --output ./eval_output
   ```
3. Record whether `pdfplumber` detects a table (`page.extract_table()` returns non-None).
4. Record which columns are mapped to internal keys and which are unmapped.
5. Record any fields that are missing, null, or mis-aligned.
6. Record whether `missing_info.md` and `extraction_log.json` accurately reflect the extraction result.
7. Record whether the final `revenue_analysis.xlsx` is explainable without code inspection.
8. **Do not commit PDFs containing personal information.**
9. If extraction fails with `RentRollExtractionError`, record the exact error message and the unrecognized column names.

---

## Success criteria

### PASS
- Text-based PDF table is detected by `pdfplumber`.
- All three required fields (`room`, `status`, `rent`) are mapped via existing alias logic.
- Optional fields that are present in the PDF are also mapped correctly.
- Missing optional fields are logged in `missing_info.md` without error.
- `extraction_log.json` records PDF name, unit count, and missing item counts accurately.
- Output (`missing_info.md`, `revenue_analysis.xlsx`) is explainable to a third party without code inspection.

### PARTIAL
- Table is detected, but one or more of the following apply:
  - A required field column is present but not recognized by current alias mapping (fixable by adding an alias).
  - Sub-header rows or blank rows cause spurious unit entries that need filtering.
  - Multi-page PDF results in only the first page being processed (documented limitation, not a crash).
  - `missing_info.md` output is partially inaccurate due to row mis-alignment.
- Output can be reviewed and corrected manually, but cannot be trusted without inspection.

### FAIL
- `pdfplumber` returns None for `extract_table()` — table is not recognized as a table structure.
- OCR is required (scanned image PDF).
- Merged cells cause required field columns to be mis-aligned or lost.
- Extraction produces values that cannot be traced back to the source document without expert review.
- Personal information handling becomes a blocker (e.g., tenant names appear in output files with no masking path).

---

## Privacy / anonymization policy

- **Do not commit real rent roll PDFs** to the repository under any circumstances.
- Do not commit tenant names, company names, room-level personally identifiable information, or confidential rent data.
- Use anonymized or synthetic-realistic samples for any repository-side evidence (screenshots, extracted snippets).
- If real documents are used locally during evaluation, record only extraction behavior, failure class, and field mapping results — not the document contents.
- Evaluation output folders (`eval_output/`, `eval/real_pdfs/`) must be listed in `.gitignore` before any evaluation run begins.
- If a real PDF is accidentally staged, run `git rm --cached <file>` immediately before committing.

---

## Decision criteria for v0.2.0

| Condition | Decision |
|-----------|----------|
| Sample A → PASS and Sample B → PASS or PARTIAL (fixable with alias additions) | **Include text-based PDF ingestion in v0.2.0** |
| Sample A → PASS but Sample B → FAIL due to layout heuristics | **Include Sample A class only; document Sample B as known limitation** |
| Sample A → PARTIAL (alias fix needed only) | **Fix aliases in v0.2.0; defer layout heuristics** |
| Sample C → FAIL (expected) | **Defer OCR / merged-cell to v0.3.0+; open separate issues** |
| Any sample → PII masking required for output to be safe | **Block v0.2.0 PDF ingestion; open PII masking issue first** |
| OCR required even for Sample A | **Defer all real-world PDF ingestion to v0.3.0+** |

**Default stance**: If only alias mapping additions are needed (no structural changes to `pdf_extract.py`), that is in scope for v0.2.0. If `extract_table()` reliability or page-selection logic requires architectural change, defer.

---

## Follow-up issues

The following are **out of scope for Issue #5** and should be opened as separate issues if evaluation reveals they are needed:

- **OCR investigation** — tesseract / AWS Textract / Azure Form Recognizer comparison for scanned PDFs
- **Multi-page PDF handling** — concatenating rent roll tables across pages
- **Merged-cell layout handling** — pre-processing or alternative extraction strategy
- **PII masking workflow** — detecting and redacting tenant names / corporate names from output files
- **Field mapping configuration** — user-configurable column alias file (e.g., `column_map.yaml`) for site-specific PDFs
