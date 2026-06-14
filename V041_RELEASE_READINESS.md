# v0.4.1 Release Readiness

## 1. Summary

v0.4.1 is proposed as a **minor hardening release** after v0.4.0.

- It is not a feature release.
- It does not expand PDF ingestion scope.
- It does not add OCR or scanned PDF support.
- It does not claim real-world PDF verification.
- It does not redesign valuation logic or CLI behavior.

> **重要**: 本ツールは不動産鑑定評価ではありません。出力される金額は「収益試算値」であり、
> 鑑定評価による「収益価格」ではありません。欠損項目は補完しません。

---

## 2. Changes Included in v0.4.1

All changes were implemented in PR #45 (Issue #44). Planning scope documented in PR #43.

| Change | Detail |
|--------|--------|
| Stale CLI wording updated | Removed `v0.1` from `cli.py` module docstring and `--help` description (`build_parser`). Version string in `--version` output was already correct via `__version__`. |
| Summary row filtering regression coverage | Added `test_summary_row_fullwidth_space_variant` confirming `合　計` (full-width space) is excluded. All 12 existing label variants already covered by parametrized test. |
| False-positive guard for `計` in non-room fields | Added `test_kei_in_non_room_field_does_not_exclude_row` confirming a unit row is not excluded merely because a non-room field (e.g., notes/備考) contains `計` or `合計`. |
| GPI impact regression | Added `test_summary_row_does_not_inflate_gpi` confirming summary row rent values are not counted in the GPI sum of occupied unit rents. |
| Status column detection regression coverage | `test_resolve_header_key` parametrize already covered `入居者名`, `入居者`, `入居日`, `契約満了日` → `None`. Confirmed in scope review. |
| Status normalization regression coverage | Added `test_normalize_status` (9 parametrized cases): `入居中`/`稼働中`/`賃貸中`/`使用中` → `"入居"`; `空室`/`空き室`/`募集中` → `"空室"`; `満室` → raw passthrough; `None` → `None`. |
| `募集中` integration test | Added `test_status_value_boshuchuu_is_vacant` confirming `募集中` is not counted as occupied in the full extraction pipeline. |

---

## 3. Validation

| Item | Value |
|------|-------|
| Test result | **161 passed, 0 failed** |
| Previous baseline (v0.4.0 / main before PR #45) | 148 passed, 0 failed |
| Tests added in v0.4.1 | 13 new tests |
| Implementation PR | [#45](https://github.com/signal-yield/revenue-kun/pull/45) |
| Planning PR | [#43](https://github.com/signal-yield/revenue-kun/pull/43) |
| Issue | [#44](https://github.com/signal-yield/revenue-kun/issues/44) (closed as completed) |
| main latest commit at readiness check | `e4774a6` |

### Files changed in PR #45

| File | Change |
|------|--------|
| `src/revenue_kun/cli.py` | +2 -2 (stale `v0.1` removed from docstring and `--help` description) |
| `tests/test_pdf_extract.py` | +88 -0 (13 new regression tests added) |

### Summary row label coverage (after v0.4.1)

| Label | Test |
|-------|------|
| `合 計` (half-width space) | `test_summary_row_label_is_non_data_row` |
| `合計` | `test_summary_row_label_is_non_data_row` |
| `合　計` (full-width space) | `test_summary_row_fullwidth_space_variant` ← new |
| `小計` | `test_summary_row_label_is_non_data_row` |
| `総計` | `test_summary_row_label_is_non_data_row` |
| `計` | `test_summary_row_label_is_non_data_row` |
| `TOTAL` / `Total` / `total` | `test_summary_row_label_is_non_data_row` |
| `Subtotal` / `SUBTOTAL` / `Sub total` / `subtotal` | `test_summary_row_label_is_non_data_row` |

---

## 4. Explicit Non-Claims

The following are **not** claimed or implemented in v0.4.1:

| Non-claim | Status |
|-----------|--------|
| real-world PDF verified | Not claimed. qualifying real-world PDF evaluation is incomplete (Issue #21 open). |
| 実務PDF検証済み | Not claimed. |
| OCR / scanned PDF support | Not implemented. Scanned PDFs remain out of scope. |
| investment advice | Not provided. Output is a revenue estimate only. |
| legal advice | Not provided. |
| appraisal / valuation opinion | Not provided. Output is 収益試算値, not 鑑定評価額. |
| replacement of professional judgment | Not intended. Verify with qualified professionals before any real-world decision. |

---

## 5. Open Issues After v0.4.1 Readiness

| Issue | State | Reason remaining open |
|-------|-------|----------------------|
| [#19](https://github.com/signal-yield/revenue-kun/issues/19) | open | Depends on #21. Additional qualifying real-world PDF evaluation not yet complete. |
| [#21](https://github.com/signal-yield/revenue-kun/issues/21) | open | No qualifying real-world text-based rent roll PDF available in `samples/private/`. Waiting state. |
| [#22](https://github.com/signal-yield/revenue-kun/issues/22) | open | Depends on #21. Findings summary cannot be written until #21 is complete. |

v0.4.1 does not resolve #19, #21, or #22. These issues remain open pending real-world PDF availability.

---

## 6. Release Recommendation

**v0.4.1 is ready to tag and release if maintainers agree.**

| Item | Value |
|------|-------|
| Recommended release title | `v0.4.1 — PDF ingestion regression hardening` |
| Recommended tag | `v0.4.1` |
| Target commit | `e4774a6` (main HEAD at readiness check) |
| Release type | patch / minor hardening release |
| Draft | No |
| Prerelease | No |

Caveat: qualifying real-world PDF evaluation remains incomplete (Issue #21 open).
Do not describe this release as "real-world PDF verified" or "実務PDF検証済み".

---

## 7. Pre-Release Checklist

- [x] `git status` clean on main
- [x] Full test suite passes: 161 passed, 0 failed
- [x] No private PDF or PII committed
- [x] No risky wording in committed files (real-world PDF verified / 実務PDF検証済み / OCR対応 as positive claim)
- [x] Issue #19 open
- [x] Issue #21 open
- [x] Issue #22 open
- [ ] Tag `v0.4.1` not yet created
- [ ] GitHub Release not yet created

---

*Created: 2026-06-14*
*Branch: docs/v041-release-readiness*
*Based on main HEAD: e4774a6*