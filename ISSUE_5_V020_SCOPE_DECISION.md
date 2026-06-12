# Issue #5 v0.2.0 Scope Decision

## Date
2026-06-12

## Purpose
Decide the v0.2.0 implementation scope based on pdfplumber evaluation results documented in
`ISSUE_5_PDFPLUMBER_EVAL_RESULT.md`.

---

## Evaluation summary

### Sample A — Simple text-based rent roll
- **Result: PASS**
- **Key finding**: `pdfplumber` detects single-page, clean-table PDFs with zero code changes required. All standard Japanese column names (部屋番号 / 月額賃料 / 月額共益費 / 入居状況 / 専有面積 / 用途) map correctly via existing alias logic. Blank cells and vacant units handled correctly. This class of PDF is already supported.

### Sample B — Japanese realistic layout variation
- **Result: PASS**
- **Key finding**: Title blocks and notes above the table do not interfere with `extract_table()`. Real-world column name variants (号室, 管理費, 賃料（税抜）, 空室/入居, 用途区分) are all resolved by the existing alias list without modification. Blank cells in optional columns (管理費, 賃料) produce correct `missing_info` entries. This class of PDF is already supported.

### Sample C — Sub-header row layout
- **Result: PARTIAL**
- **Key finding**: Table and columns are detected correctly. The failure mode is sub-header rows (`【1F区画】`, `【2F区画】`) being treated as vacant units, inflating `extracted_units_count` and generating spurious `missing_info` entries. GPI is numerically correct (sub-header rows contribute 0 rent), but the unit count and log are misleading. A simple row-skip predicate in `pdf_extract.py` resolves this. The tool does not crash; it fails silently — which is the more dangerous failure mode for a calculation tool.

---

## v0.2.0 recommended scope

### Include

| Item | Rationale |
|------|-----------|
| Text-based single-page PDF ingestion (Sample A / B class) | Already works; zero code changes needed. Include with documentation confirming support. |
| Sub-header row filter (`【…】` / `[…]` pattern skip) | Small, localized fix to `pdf_extract.py`. Prevents silent unit-count inflation. Required for safe output. |
| Explicit column alias documentation | Document which column names are recognized. Enables users to verify their PDF is in scope. |
| Conservative failure on unrecognized required columns | Already implemented via `RentRollExtractionError` (exit code 2). Confirm behavior in docs. |
| `assumptions.sample.yaml` calibration guidance | README note that bundled sample assumptions are calibrated for synthetic data, not real properties. |

### Exclude

| Item | Reason |
|------|--------|
| OCR / scanned PDFs | Requires external library (tesseract / cloud API). Architectural change. Defer. |
| Multi-page PDF merging | Requires page-concatenation logic. Out of scope for a targeted fix release. Defer. |
| Complex merged-cell layouts | `extract_table()` mis-aligns columns; no reliable fix without structural changes. Defer. |
| Automated PII masking | No clear trigger condition; requires named-entity detection or allowlist. Separate issue. |
| Layout-specific heuristics for individual property management systems | Would require per-vendor logic; brittle and not generalizable. Defer or reject. |
| User-configurable column alias file (`column_map.yaml`) | Useful but non-trivial; adds configuration surface area. Defer to v0.3.0+. |

---

## Implementation principle

v0.2.0 should support only text-based PDFs where `pdfplumber` can extract table-like structures
with reasonable reliability. The bar is: **output that a non-engineer can verify against the
source document without code inspection**.

Ambiguous or unreliable PDFs must fail safely:
- If a required column is missing → `RentRollExtractionError` (exit code 2, already implemented)
- If a row is a non-unit sub-header → skip with log entry, not silent inclusion
- If extraction produces a unit count that differs from the visible rows → log a warning

Silent miscounts (Sample C behavior) violate the "no auto-completion, no silent suppression"
design principle of revenue-kun. Fixing the sub-header row filter is therefore not optional
for v0.2.0 — it is a correctness requirement.

---

## Follow-up issues to create

| Issue | Target | Description |
|-------|--------|-------------|
| Sub-header row filter | v0.2.0 | Skip rows where room field matches `【…】`, `[…]`, or where all data columns are blank/None. Localized to `pdf_extract.py`. |
| OCR investigation | v0.3.0+ | Evaluate tesseract / AWS Textract / Azure Form Recognizer for scanned PDFs. |
| Multi-page PDF handling | v0.3.0+ | Concatenate rent roll tables across pages before extraction. |
| Merged-cell layout handling | v0.3.0+ | Pre-processing or alternative extraction strategy for complex table layouts. |
| PII masking workflow | Separate | Detect and redact tenant / company names from output files before sharing. |
| User-configurable column alias file | v0.3.0+ | Allow `column_map.yaml` for site-specific column names beyond the built-in alias list. |
| Real-world sample collection policy | v0.2.0 prep | Define anonymization checklist for collecting and sharing real-world test PDFs. |

---

## Final decision

**Proceed with v0.2.0 limited text-based PDF ingestion.**

Rationale:
- Sample A and Sample B already pass with zero code changes. These represent the most common
  PDF output from property management systems (system-generated, text-based, single-page).
- The only required code change for v0.2.0 is the sub-header row filter — small, localized,
  and necessary for correctness.
- Deferring until OCR or multi-page support is ready would unnecessarily block a working capability.
- The "fail-safe on unrecognized structure" principle is already in place (`RentRollExtractionError`).
  Adding the sub-header filter completes the correctness guarantee for the supported subset.

**Out-of-scope items are explicitly documented and will not be silently included in v0.2.0.**
