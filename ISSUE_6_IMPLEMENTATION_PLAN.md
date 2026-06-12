# Issue #6 Implementation Plan

## Date
2026-06-12

## Purpose
Plan limited text-based PDF ingestion for simple rent roll tables in v0.2.0.
Issue #5 evaluation confirmed that Sample A / B class PDFs already pass with zero code changes.
This plan identifies what remains, what already works, and the minimum change required for v0.2.0.

---

## Current PDF flow

### Relevant files

| File | Role |
|------|------|
| `src/main.py` | Entrypoint; delegates to `cli.run()` |
| `src/revenue_kun/cli.py` | Orchestration: branches on `--rent-roll-pdf`; calls `extract_rent_roll_from_pdf()` |
| `src/revenue_kun/pdf_extract.py` | pdfplumber extraction → `list[RentRollUnit]` + `ExtractionReport` |
| `src/revenue_kun/rent_roll.py` | `RentRollUnit` dataclass (shared by CSV and PDF paths) |
| `src/revenue_kun/noi.py` | Consumes `list[RentRollUnit]` — no PDF-specific logic |
| `src/revenue_kun/missing.py` | Consumes `list[RentRollUnit]` — no PDF-specific logic |
| `src/revenue_kun/outputs.py` | Consumes `list[RentRollUnit]` — no PDF-specific logic |
| `tests/test_pdf_extract.py` | Unit tests for extraction; 3 patterns + column variant + required-column-missing |
| `tests/test_e2e_pdf.py` | E2E test with synthetic PDF via `make_sample_pdf.py` |
| `scripts/make_sample_pdf.py` / `src/revenue_kun/sample_pdf.py` | Synthetic PDF generation for CI |

### Current data flow

```
--rent-roll-pdf → pdf_extract.extract_rent_roll_from_pdf()
                      └─ pdfplumber.open()
                      └─ page.extract_table()         (single page only)
                      └─ _build_column_map(header)    (alias matching via _HEADER_KEYS)
                      └─ required column check         (RentRollExtractionError exit 2)
                      └─ row loop → RentRollUnit × N
                  → (units: list[RentRollUnit], report: ExtractionReport)

--rent-roll     → rent_roll.load_rent_roll()
                  → (units: list[RentRollUnit])

                  → detect_missing(assumptions, units)
                  → compute_noi(units, assumptions)
                  → direct_capitalization(noi, assumptions)
                  → build_sensitivity(noi, assumptions)
                  → write_missing_info / write_excel / write_extraction_log
```

The downstream pipeline (`noi`, `missing`, `outputs`) is **already PDF-agnostic**. It consumes
`list[RentRollUnit]` regardless of whether the source was CSV or PDF. The interface is already
defined and stable.

### Current behavior

- `--rent-roll-pdf` flag is already wired in `cli.py:run()` (line 62–95).
- Column alias matching via `_HEADER_KEYS` already handles real-world Japanese column name variants
  (号室, 管理費, 空室/入居, 賃料（税抜）, 用途区分) without modification.
- Required column check (`_REQUIRED_KEYS = {"room", "rent", "status"}`) raises
  `RentRollExtractionError` (exit code 2) if any required column is absent.
- Optional columns (area, cam, use) generate `ExtractionReport.notes` when absent.
- Blank cells are preserved as `None` — not auto-completed.
- `ExtractionReport` metadata is written to `extraction_log.json`.
- E2E CI already runs the PDF path (`E2E - PDF run` step in `.github/workflows/tests.yml`).

### Current limitation — sub-header row pollution (Sample C)

In `pdf_extract.py` lines 168–170, rows are skipped only when `room` is `None`:

```python
room = _clean(get("room"))
if room is None:
    continue
```

`_clean("【1F区画】")` returns `"【1F区画】"` (not `None`), so sub-header rows pass this check
and are treated as vacant units. This inflates `extracted_units_count` and generates spurious
`missing_info` entries — a **silent miscounting failure** that violates the "no silent suppression"
design principle.

---

## Proposed v0.2.0 scope

- Support text-based PDFs where pdfplumber can extract table-like structures (Sample A / B class).
- Convert extracted rows into the existing rent roll data flow (already implemented).
- Log missing fields explicitly (already implemented via `missing.py` + `ExtractionReport`).
- Fail safely for unreliable extraction (already implemented via `RentRollExtractionError`).
- **Add: sub-header row filter** to prevent silent unit-count inflation (Sample C fix).

---

## Out of scope

- OCR / scanned PDFs
- Multi-page PDF merging
- Complex merged-cell layout recovery
- Vendor-specific layout heuristics
- Automated PII masking
- User-configurable column alias file (`column_map.yaml`)

---

## Files likely to change

### Required for v0.2.0

| File | Change | Scope |
|------|--------|-------|
| `src/revenue_kun/pdf_extract.py` | Add sub-header row skip predicate (~5 lines) | Small, localized |
| `tests/test_pdf_extract.py` | Add test for sub-header row skip | 1 test function |
| `CHANGELOG.md` | Document the fix | 1–2 lines |

### No change needed

| File | Reason |
|------|--------|
| `src/revenue_kun/cli.py` | PDF branch already wired; flag already exists |
| `src/revenue_kun/rent_roll.py` | `RentRollUnit` is already the shared interface |
| `src/revenue_kun/noi.py` | No PDF-specific logic; consumes `list[RentRollUnit]` |
| `src/revenue_kun/missing.py` | Same — PDF-agnostic |
| `src/revenue_kun/outputs.py` | Same — PDF-agnostic |
| `src/revenue_kun/sample_pdf.py` | Synthetic PDF generation is independent |
| `scripts/make_sample_pdf.py` | Same |
| `.github/workflows/tests.yml` | E2E PDF check already present |

---

## Design notes

### Sub-header row filter (the only required code change)

Add a predicate in `pdf_extract.py` after `room = _clean(get("room"))`:

```python
# Skip rows where room field is a section header (e.g. 【1F区画】, [1F])
if room is None or re.match(r'^[【\[]', room):
    continue
```

Alternatively, a stricter predicate that also skips rows with no data in rent or status columns
would be more conservative. The exact predicate should be decided during implementation (#6 issue).
A note entry should be added to `ExtractionReport.notes` when a row is skipped this way.

### Logging skipped rows

When a sub-header row is skipped, add to `report.notes`:
```
「【1F区画】」行をセクション見出しとして除外しました（データ行ではないと判断）。
```

This makes the skip transparent without crashing, consistent with the existing notes convention.

### The extraction-to-flow connection is already complete

The full pipeline from PDF extraction to `indicated_value` output is already functional for
Sample A / B class PDFs. This issue is **not** building new plumbing — it is fixing the one
silent failure mode that prevents v0.2.0 from being declared safe for text-based PDFs.

---

## Dependency on #7

**#7: Column alias mapping** — `_HEADER_KEYS` in `pdf_extract.py` is the current alias mechanism.
Issue #7 may extend this list or refactor it for configurability.

- #6 can proceed independently: `_HEADER_KEYS` already covers the real-world variants seen in
  Issue #5 evaluation (号室, 管理費, 空室/入居, 賃料（税抜）, 用途区分) without modification.
- If #7 refactors `_HEADER_KEYS` into a configurable structure, it will touch the same part of
  `pdf_extract.py`. Coordinate merge order: complete #6 first, then rebase or merge #7 on top,
  since the sub-header filter and alias mapping are adjacent but logically independent changes.

---

## Dependency on #8

**#8: Safe failure handling** — `RentRollExtractionError` (exit code 2) is the current mechanism.
Issue #8 may extend failure modes: e.g., warn (not stop) when unit count seems inconsistent with
page content, or add a dry-run mode that reports what would be extracted without producing output.

- #6 can proceed independently: the existing `RentRollExtractionError` already handles required
  column absence correctly (exit code 2).
- The sub-header filter in #6 is itself a safe-failure improvement (converts silent miscount into
  a logged skip). It does not conflict with #8 but it makes #8's scope slightly smaller.
- Implement #6 and #8 in parallel on separate branches; they touch the same file (`pdf_extract.py`)
  but different lines — the sub-header filter is in the row loop, #8 extensions are likely at the
  column-mapping or page-detection level.

---

## Test plan

| Scenario | Source | Expected result |
|----------|--------|-----------------|
| CSV base | `data/dummy_rent_roll.csv` | Unchanged — must remain PASS |
| Synthetic PDF (simple) | CI-generated via `make_sample_pdf.py` | Unchanged — must remain PASS |
| Synthetic PDF (missing_values) | CI-generated | Unchanged — must remain PASS |
| Synthetic PDF (different_columns) | CI-generated | Unchanged — must remain PASS |
| Local Sample A (simple text) | `samples/private/` — NOT committed | PASS — unit count correct |
| Local Sample B (layout variation) | `samples/private/` — NOT committed | PASS — alias mapping correct |
| Local Sample C (sub-header rows) | `samples/private/` — NOT committed | PASS after filter fix — no spurious units |
| Missing required column | Synthetic — `test_missing_required_column_raises` | `RentRollExtractionError` exit 2 |
| Sub-header row skip | New unit test — no `samples/private/` dependency | Skip logged in `report.notes` |

---

## Implementation recommendation

**Proceed.** The scope is minimal:

1. Add sub-header row skip predicate to `pdf_extract.py` (~5 lines).
2. Add 1 unit test to `test_pdf_extract.py`.
3. Update `CHANGELOG.md`.

The rest of the pipeline is already functional and tested. No new dependencies, no architectural
changes, no new flags.

---

## Next steps

1. Commit `ISSUE_5_V020_SCOPE_DECISION.md` + `ISSUE_6_IMPLEMENTATION_PLAN.md`.
2. Open GitHub Issue #6 with a summary referencing this document.
3. Create branch `fix/issue-6-subheader-row-filter`.
4. Implement sub-header row predicate in `pdf_extract.py`.
5. Add unit test in `test_pdf_extract.py`.
6. Verify locally with Sample C (`samples/private/sample_c_hard_case_layout.pdf`).
7. Update `CHANGELOG.md` and submit PR targeting `main`.
