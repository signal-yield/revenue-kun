# v0.4.0 Status After PR #39

## Summary

This document records the state of `revenue-kun` v0.4.0 PDF ingestion hardening
after the completion of Issue #29 and Issue #30 fix chains (PR #31–#39).

| Item | State |
|------|-------|
| Issue #29 — Japanese status column detection | **closed** (PR #31–#35) |
| Issue #30 — Total / summary row filtering | **closed** (PR #37) |
| Issue #21 — Real-world PDF evaluation | **open** — qualifying PDF not yet available |
| Issue #19 — Plan v0.4.0 evaluation | **open** — depends on Issue #21 |
| Issue #22 — Summarize v0.4.0 findings | **open** — depends on Issue #21 |

main HEAD at time of snapshot: `54eee54` (Merge pull request #39)

---

## Completed Work

### Issue #29 — Japanese status column detection (PR #31–#35)

**Root problem** (observed in `realistic_anonymized_001`):
- `入居者名` (tenant name, col 4) was matched by the `入居` alias → `status` false positive
- `ステータス` (col 13, actual status column) had no alias → unrecognized
- All status values were `None`; GPI = 0 (silent wrong result)

**Fix chain**:

| PR | Change |
|----|--------|
| #31 | Removed `("入居", "status")` alias; added `("ステータス", "status")` |
| #32 | Restored `("入居", "status")`; added `_PERSON_NAME_DENY = {"者名", "テナント名"}` |
| #33 | Extended `_PERSON_NAME_DENY` to include `"入居者"` |
| #34 | Docs: re-evaluation revealed `入居日` (col 5) as new false positive |
| #35 | Added `_DATE_HEADER_DENY = {"入居日", "開始日", "満了日", "契約日"}` |

**Headers now excluded from status matching**:

| Header pattern | Deny mechanism | Example |
|---------------|---------------|---------|
| Person/tenant-name columns | `_PERSON_NAME_DENY` (tokens: `者名`, `テナント名`, `入居者`) | `入居者名`, `契約者名`, `テナント名`, `入居者` |
| Date-type columns | `_DATE_HEADER_DENY` (tokens: `入居日`, `開始日`, `満了日`, `契約日`) | `入居日`, `入居開始日`, `契約開始日`, `契約満了日`, `契約日` |

**Status aliases preserved**:
`入居`, `入居状況`, `入居/空室`, `稼働状況`, `ステータス`, `空室`, `稼働`, `状況`, `occupancy`, `status`

### Issue #30 — Total / summary row filtering (PR #37)

**Root problem**: `合 計` summary row was extracted as a unit row, inflating
`rows_extracted` to 21 and `vacant` count to 4.

**Fix**: Added `_SUMMARY_ROW_LABELS = {"合計", "小計", "総計", "計", "total", "subtotal"}`
and condition 3 in `_is_non_data_row`: if the room field, after collapsing all whitespace
and lowercasing, exactly matches a known summary label, the row is excluded.

Full-string equality (not substring) prevents accidental exclusion of room numbers that
contain these strings as substrings (e.g., `計画棟101`, `合計算`).

Excluded rows are noted in `ExtractionReport.notes`.

**Labels now filtered**:
`合計`, `合 計`, `合　計`, `小計`, `総計`, `計`, `TOTAL`, `Total`, `total`,
`Subtotal`, `SUBTOTAL`, `Sub total`, `subtotal`

### Re-evaluation records

| Evaluation PR | Finding |
|--------------|---------|
| #27 (initial) | `入居者名` → status; GPI = 0; rows = 21; vacant = 4 |
| #34 (after #31–#33) | `入居日` → status (new false positive); GPI = 0; rows = 21; vacant = 4 |
| #36 (after #35) | status → col 13 ✓; GPI = 2,030,000 yen/month ✓; rows = 21; vacant = 4 |
| #38 (after #37) | rows = 20 ✓; occupied = 17 ✓; vacant = 3 ✓; GPI = 2,030,000 yen/month ✓ |
| #39 | No qualifying real-world PDF in `samples/private/`; synthetic regression check: no regressions |

---

## Current Verified Behavior

### realistic_anonymized_001 (post-PR #38 main)

| Metric | Value |
|--------|-------|
| rows_extracted | 20 |
| occupied units | 17 |
| vacant units | 3 |
| monthly GPI | 2,030,000 yen |
| annual GPI | 24,360,000 yen |
| status column | col 13 (`ステータス`) |
| column_map | room=0, area=3, rent=7, cam=8, status=13, notes=14 |
| summary row contamination | resolved — `合 計` excluded, noted in report |
| exit code | 0 |

### Synthetic samples regression check (PR #39)

| Sample ID | rows | occupied | vacant | GPI (yen/month) | Regression? |
|-----------|------|----------|--------|-----------------|-------------|
| sample-private-001 | 8 | 6 | 2 | 632,000 | None ✓ |
| sample-private-002 | 7 | 6 | 1 | 678,000 | None ✓ |
| sample-private-003 | 6 | 4 | 2 | 508,000 | None ✓ |

---

## Open Issues

### Issue #21 — Evaluate additional private rent roll PDF samples

**State**: open — waiting for qualifying real-world PDF

**Reason**: No qualifying real-world text-based rent roll PDF is present in
`samples/private/`. All currently available PDFs are synthetic (reportlab-generated)
or realistic anonymized, neither of which satisfies the Issue #21 closure condition.

**Closure condition** (per `V040_REAL_WORLD_PDF_EVALUATION_REPORT.md`):
At least 1 qualifying real-world text-based rent roll PDF must be evaluated privately
and the sanitized result recorded publicly. Synthetic-only evaluation is not sufficient.

**Re-open trigger**: When at least 1 qualifying real-world text-based rent roll PDF
is placed in `samples/private/`, evaluate it with `--dry-run`, record the sanitized
result (sample_id, aggregate metrics, recommended action only — no PDF, no PII),
and close Issue #21 if the minimum closure conditions are satisfied.

### Issue #19 — Plan v0.4.0 additional real-world PDF evaluation

**State**: open — parent issue; depends on Issue #21.

### Issue #22 — Summarize v0.4.0 PDF evaluation findings and decide next scope

**State**: open — depends on Issue #21 completion.

---

## Explicitly Not Implemented

The following are confirmed out of scope for v0.4.0 and will not be implemented:

- OCR support
- Scanned PDF support
- Multi-page table stitching
- Complex merged cell handling
- Vendor-specific heuristics without repeated evidence
- PII masking or anonymization
- Committing private PDFs or tenant/property data
- Formal valuation or investment advice

---

## Next Trigger

When a qualifying real-world text-based rent roll PDF becomes available:

1. Place it in `samples/private/` (gitignored).
2. Assign a sample_id (e.g., `real_world_001`).
3. Run `PYTHONPATH=src python -m revenue_kun.cli --rent-roll-pdf <path> --assumptions assumptions.sample.yaml --dry-run`.
4. Record sanitized results (sample_id, exit code, rows_extracted, column_map,
   recognized fields, GPI, occupied/vacant counts, recommended action).
5. Do not commit PDF, real filename, local path, property name, tenant names, or any PII.
6. Update `V040_REAL_WORLD_PDF_EVALUATION_REPORT.md` and close Issue #21 if
   minimum closure conditions are met.
