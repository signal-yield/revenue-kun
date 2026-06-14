# v0.4.0 / v0.4.1 PDF Ingestion Evaluation Summary

## 1. Summary

v0.4.0 and v0.4.1 collectively represent the current PDF ingestion hardening point for revenue-kun.

- v0.4.0 fixed Japanese status column detection and summary row filtering.
- v0.4.1 added regression coverage and stale CLI wording cleanup.
- This document is not a real-world PDF verification report.
- Qualifying real-world text-based rent roll PDF evaluation remains incomplete (Issue #21 open).

> **重要**: 本ツールは不動産鑑定評価ではありません。出力される金額は「収益試算値」であり、
> 鑑定評価による「収益価格」ではありません。欠損項目は補完しません。

---

## 2. v0.4.0 Findings

### Japanese status column detection hardening

The following column headers are **not** treated as status columns:

| Header | Reason |
|--------|--------|
| `入居者名` | Tenant name column — denied as status |
| `入居者` | Tenant name (short form) — denied as status |
| `入居日` | Move-in date column — denied as status |
| `契約満了日` | Contract expiry date column — denied as status |

The `ステータス` column header is correctly recognized as the status column.

### Summary row filtering

The following row labels are filtered and excluded from unit row counts and GPI calculation:

| Label |
|-------|
| `合計` |
| `合 計` (half-width space) |
| `小計` |
| `総計` |
| `計` |
| `TOTAL` / `Total` / `total` |
| `Subtotal` / `SUBTOTAL` / `Sub total` / `subtotal` |

### realistic_anonymized_001 result

| Item | Value |
|------|-------|
| Rows extracted | 20 |
| Occupied units | 17 |
| Vacant units | 3 |
| Monthly GPI | 2,030,000 yen |
| Status column detected | col13 / `ステータス` |

### Synthetic private samples

synthetic private samples 001, 002, and 003 showed no regression against v0.4.0 behavior.

---

## 3. v0.4.1 Findings

| Change | Detail |
|--------|--------|
| Stale CLI wording updated | Removed `v0.1` from `cli.py` module docstring and `--help` description. Version string in `--version` was already correct. |
| Full-width-space summary label covered | `合　計` (full-width space) confirmed excluded by `test_summary_row_fullwidth_space_variant`. |
| Summary row filtering regression tests | Added/confirmed all 12 label variants in parametrized test. |
| False-positive guard for `計` | Ordinary rows containing `計` in non-room fields (e.g., notes/備考) are not excluded. `test_kei_in_non_room_field_does_not_exclude_row` added. |
| GPI impact regression | `test_summary_row_does_not_inflate_gpi` confirms summary row rent values are not counted in monthly GPI. |
| Status column detection regression coverage | `test_resolve_header_key` parametrize confirmed: `入居者名`, `入居者`, `入居日`, `契約満了日` → `None`. |
| Status normalization regression coverage | `test_normalize_status` (9 parametrized cases): `入居中`/`稼働中`/`賃貸中`/`使用中` → `"入居"`; `空室`/`空き室`/`募集中` → `"空室"`; `満室` → raw passthrough; `None` → `None`. |
| `募集中` integration test | `test_status_value_boshuchuu_is_vacant` confirms `募集中` is not counted as occupied in the full extraction pipeline. |

### Full test suite result

| Item | Value |
|------|-------|
| Result | **161 passed, 0 failed** |
| Previous baseline (v0.4.0) | 148 passed, 0 failed |
| Tests added in v0.4.1 | 13 new tests |

---

## 4. Confirmed Behavior

| Behavior | Status |
|----------|--------|
| Summary rows are not counted as unit rows | Confirmed |
| Summary rows do not inflate monthly GPI | Confirmed |
| Japanese non-status columns (`入居者名`, `入居者`, `入居日`, `契約満了日`) are denied as status columns | Confirmed |
| Status values `入居中` / `空室` / `募集中` / `満室` are covered | Confirmed |
| CLI wording no longer contains stale `v0.1` references | Confirmed |

---

## 5. Remaining Limitations

| Limitation | Detail |
|------------|--------|
| Qualifying real-world text-based rent roll PDF evaluation not complete | Issue #21 open. No qualifying real-world private sample is available in `samples/private/`. |
| OCR / scanned PDF support not implemented | Scanned PDFs remain out of scope. |
| Vendor-specific heuristics intentionally avoided | The parser targets general table structure, not format-specific logic. |
| Broad layout redesign out of scope | Column reordering and radically different layouts are not covered. |
| Real-world PDF verified not claimed | This is not claimed and must not be added. |

---

## 6. Open Issues

| Issue | State | Role in this summary |
|-------|-------|---------------------|
| [#19](https://github.com/signal-yield/revenue-kun/issues/19) | open | Depends on #21. Additional qualifying real-world PDF evaluation not yet complete. |
| [#21](https://github.com/signal-yield/revenue-kun/issues/21) | open | No qualifying real-world text-based rent roll PDF available. Waiting state. |
| [#22](https://github.com/signal-yield/revenue-kun/issues/22) | open | This summary is the deliverable intended to support #22. |

#19 and #21 remain open because additional qualifying real-world/private PDF evaluation is not complete.
#22 is the issue this summary is meant to support. It remains open during this summary step.

---

## 7. Next-Scope Options

**A. Continue v0.4.x PDF ingestion hardening**
- Expand parser coverage for additional column layouts or status value variants.
- Requires qualifying real-world text-based samples to target meaningfully.

**B. Pause parser expansion until qualifying real-world text-based samples are available**
- Hold v0.4.1 as the stable PDF ingestion hardening point.
- Keep #19 and #21 open.
- Resume when a qualifying real-world text-based rent roll PDF is available.

**C. Start separate v0.5.0 product-scope planning outside parser expansion**
- Define next product-level milestone independently of PDF ingestion.
- Allows project progress while #21 is in waiting state.

---

## 8. Recommendation

- **Use v0.4.1 as the current stable PDF ingestion hardening point.**
- **Pause additional PDF parser expansion** until qualifying real-world text-based rent roll PDFs are available.
- **Keep #19 and #21 open** pending real-world PDF availability.
- After this summary is merged and commented on #22, **consider closing #22 as completed** (the findings summary it requested is now written).
- **Create a separate issue for next product scope / v0.5.0 planning** so project progress is not blocked by #21.

---

## 9. Non-Claims / Guardrails

| Non-claim | Status |
|-----------|--------|
| Real-world PDF verified | Not claimed. Must not be added. |
| 実務PDF検証済み | Not claimed. Must not be added. |
| OCR / scanned PDF support | Not implemented. Out of scope. |
| Investment advice | Not provided. Output is a revenue estimate only. |
| Legal advice | Not provided. |
| Appraisal / valuation opinion | Not provided. Output is 収益試算値, not 鑑定評価額. |
| Replacement of professional judgment | Not intended. Verify with qualified professionals before any real-world decision. |
| Private PDF / PII / local path disclosure | Not included. No private PDFs, tenant names, property names, or local paths are committed. |

---

*Created: 2026-06-15*
*Based on: v0.4.0 (tag), v0.4.1 (tag), main HEAD 32571ad*
*Planning PR: #43 | Implementation PR: #45 | Release readiness PR: #46*
