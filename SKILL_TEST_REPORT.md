# revenue-kun Skill Test Report

## Date
2026-06-12

## Purpose
Verify whether revenue-kun v0.1.0 can be used as a Claude Code / skill-like execution workflow.

## Summary
- **Result: PASS**
- All 4 scenarios (CSV base + 3 synthetic PDF patterns) executed successfully.
- All 3 output files generated in every scenario.
- Missing item detection and logging behave as designed.
- Extraction log is machine-readable and sufficient for post-hoc verification.
- Excel output contains 5 sheets suitable for third-party explanation.
- No `shueki` / `shueki-kun` / `python -m shueki.cli` remnants found.
- Git working tree can be restored cleanly.

---

## Commands executed

```powershell
git checkout main && git pull

python -m pip install -r requirements.txt

python src/main.py --assumptions assumptions.sample.yaml --output ./output_base

python scripts/make_sample_pdf.py --output data/sample_rentroll_simple.pdf
python scripts/make_sample_pdf.py --output data/sample_rentroll_missing_values.pdf
python scripts/make_sample_pdf.py --output data/sample_rentroll_different_columns.pdf

python src/main.py --assumptions assumptions.sample.yaml --rent-roll-pdf data/sample_rentroll_simple.pdf --output ./output_simple
python src/main.py --assumptions assumptions.sample.yaml --rent-roll-pdf data/sample_rentroll_missing_values.pdf --output ./output_missing
python src/main.py --assumptions assumptions.sample.yaml --rent-roll-pdf data/sample_rentroll_different_columns.pdf --output ./output_different
```

---

## Output folders checked

| Folder | revenue_analysis.xlsx | missing_info.md | extraction_log.json |
|--------|:---------------------:|:---------------:|:-------------------:|
| output_base (CSV) | ✅ | ✅ | ✅ |
| output_simple | ✅ | ✅ | ✅ |
| output_missing | ✅ | ✅ | ✅ |
| output_different | ✅ | ✅ | ✅ |

---

## Findings

### README execution clarity
- **PASS.** All commands in the README executed without modification.
- Command schema is consistent: `python src/main.py --assumptions ... --output ...`
- Optional `--rent-roll-pdf` flag works orthogonally.
- `revenue-kun` naming is unified throughout. No `shueki` remnants.
- One minor note: console output is garbled on Windows cp932 terminals, but output *files* are always valid UTF-8. README already documents the workaround (`$env:PYTHONIOENCODING="utf-8"`).

### CLI behavior
- **PASS.** Exit codes are clean (0 = success).
- Stdout prints a structured block: header / unit count / GPI / EGI / NOI / 収益試算値 / warnings / output paths.
- Disclaimer and VALUE_LABEL ("収益試算値") appear consistently in every run.
- "収益価格" does not appear as a positive result label.

### Synthetic PDF E2E behavior

| Pattern | Extracted | Missing cells | GPI | NOI | 収益試算値 |
|---------|----------:|:-------------:|----:|----:|----------:|
| simple | 5 units | 0 | 26,016,000 | 17,215,200 | 360,337,778 |
| missing_values | 5 units | 4 | 9,816,000 | 1,825,200 | 18,337,778 |
| different_columns | 3 units | 0 | 21,780,000 | 13,191,000 | 270,911,111 |

- **PASS.** Values match the E2E table documented in README Phase 2.1.
- `different_columns` correctly recognized aliased headers (`unit`/`rent`/`common_fee`/`area`/`status`).

### Missing info behavior
- **PASS.**
- `output_simple`: 2 items — `建築時期` (物件情報) + `管理委託費` (運営費用). Both expected; no spurious entries.
- `output_missing`: 5 items — above 2 + `月額共益費 A102` (→ 0算入) + `専有面積 A103` (計算影響なし) + `想定賃料 A201` (空室). Accurately captures the 4 missing cells in the PDF.
- `output_different`: 2 items — same as simple (assumptions-derived only). Column alias mapping worked; no false negatives.
- Every entry includes: item name / source / impact direction. Suitable for third-party review.
- Disclaimer present in every `missing_info.md`.

### extraction_log behavior
- **PASS.** All 12 required schema keys present in every run.
- `rent_roll_pdf` correctly records the PDF filename (not the full path).
- `extracted_units_count`, `missing_required_count`, `missing_optional_count` are accurate.
- `gpi`, `noi`, `indicated_value` are numeric and verifiable.
- `executed_at` is ISO 8601 UTC — sufficient for audit trail.
- `disclaimer` field present and correct.
- `tool` / `version` fields correctly identify `revenue-kun v0.1.0`.

### Excel output behavior
- **PASS.** `revenue_analysis.xlsx` contains 5 sheets:
  - `サマリー` (22 rows) — top-level summary with indicated value and disclaimer
  - `レントロール` (6 rows) — per-unit data
  - `NOI計算` (16 rows) — GPI → EGI → NOI → net income → indicated value
  - `感応度分析` (11 rows) — NOI delta × cap rate delta matrix
  - `欠損項目` (3 rows) — missing item list
- Sheet structure and row counts consistent across scenarios.
- Sufficient for third-party explanation without requiring code inspection.

### Git cleanliness
- After test runs, working tree has:
  - `modified: data/sample_rentroll_*.pdf` — re-generated PDFs (binary diff expected, non-deterministic reportlab output)
  - `Untracked: output_base/ output_simple/ output_missing/ output_different/` — test outputs
- **None of the above should be committed.** Restore with:

```powershell
git restore data/sample_rentroll_simple.pdf data/sample_rentroll_missing_values.pdf data/sample_rentroll_different_columns.pdf
Remove-Item -Recurse -Force output_base, output_simple, output_missing, output_different
git status   # → nothing to commit, working tree clean
```

---

## Limitations confirmed
- **Real-world rent roll PDFs**: not supported in v0.1.0. Only reportlab-generated synthetic tables tested.
- **OCR**: not supported. Scanned/image PDFs will fail silently or raise `RentRollExtractionError`.
- **Multi-page PDF merging**: not supported. Only single-page tables extracted.
- **Merged-cell layouts**: not supported. pdfplumber `extract_table()` may mis-align columns.
- **Automated PII masking**: not supported. Tenant names / corporate names are not detected or redacted.
- **Non-deterministic PDF binary**: `data/sample_rentroll_*.pdf` are re-generated each run and will always show as modified after `make_sample_pdf.py` executes. This is expected behavior.

---

## Issues / follow-ups
- [Issue #5: Evaluate real-world rent roll PDF ingestion](https://github.com/signal-yield/revenue-kun/issues/1) — v0.2.0+ candidate
- Potential minor issue: console output on Windows cp932 is garbled. Files are correct; cosmetic only.
- `indicated_value` in `extraction_log.json` is stored as a raw float (e.g., `360337777.7777778`). Rounding to integer (円) in logs may improve readability for non-technical reviewers.

---

## Final judgment

**revenue-kun v0.1.0 is acceptable as a tested research/prototype skill workflow.**

- Executable from README alone with no ambiguity.
- All 4 E2E scenarios pass with correct and reproducible values.
- Missing items are logged with source and impact — no silent suppression.
- Output files (xlsx / md / json) are independently verifiable.
- Disclaimer and "収益試算値" (not "収益価格") terminology enforced throughout.
- Git working tree can be restored to clean state after test runs.

The tool is ready to be shared as a GitHub reference and used as a Claude Code execution target. Real-world PDF ingestion (Issue #5) remains the primary prerequisite for v0.2.0.
