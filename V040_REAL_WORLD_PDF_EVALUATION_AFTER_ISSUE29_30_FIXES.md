# v0.4.0 Real-World PDF Evaluation After Issue #29 / #30 Fixes

## Scope

- related issues: #19, #21, #22
- related PRs: #31, #32, #33, #34, #35, #36, #37, #38
- private PDF: not committed
- PII: not committed
- implementation changes in this evaluation branch: none

> **重要**: 本ツールは不動産鑑定評価ではありません。出力される金額は「収益試算値」であり、
> 鑑定評価による「収益価格」ではありません。欠損項目は補完しません。

---

## Purpose

After the Issue #29 and Issue #30 fix chain (PR #31–#38), this document records:

1. Whether a qualifying real-world text-based rent roll PDF is available in `samples/private/`
   for the first time, enabling Issue #21 closure.
2. A regression-check re-evaluation of the three existing synthetic samples against the
   updated main (post-PR #38) to confirm no regressions from the fixes.

---

## Real-World PDF Availability Check

main HEAD at time of evaluation: `c09ef65` (Merge pull request #38)

### Files present in `samples/private/`

| File | Classification | Qualifies for Issue #21 | Notes |
|------|---------------|------------------------|-------|
| `realistic_anonymized_001.pdf` | realistic anonymized | No | Evaluated in PR #27/#34/#36 |
| `sample_a_simple_text_rentroll.pdf` | synthetic (reportlab) = sample-private-001 | No | Synthetic v0.2.0 test PDF |
| `sample_b_japanese_layout_variation.pdf` | synthetic (reportlab) = sample-private-002 | No | Synthetic v0.2.0 test PDF |
| `sample_c_hard_case_layout.pdf` | synthetic (reportlab) = sample-private-003 | No | Synthetic v0.2.0 test PDF |

**No qualifying real-world text-based rent roll PDF is present in `samples/private/`.**

All currently available PDFs are either synthetic (reportlab-generated for testing) or
realistic anonymized (non-qualifying per `V040_REAL_WORLD_PDF_EVALUATION_REPORT.md`
§ "Real-World PDF Definition"). Neither category satisfies the Issue #21 closure condition.

---

## Regression Check: Synthetic Samples Against Post-PR #38 Main

The three synthetic samples (sample-private-001/002/003) were re-evaluated against main
after the Issue #29 and Issue #30 fix chain to confirm no regressions.

Command pattern:

```text
PYTHONPATH=src python -m revenue_kun.cli \
  --rent-roll-pdf samples/private/<sample> \
  --assumptions assumptions.sample.yaml \
  --dry-run
```

### Results

| Sample ID | rows_extracted | column_map (status col) | occupied | vacant | monthly GPI | notes |
|-----------|---------------|------------------------|----------|--------|-------------|-------|
| sample-private-001 | 8 | status=5 (`入居状況`) | 6 | 2 | 632,000 yen | — |
| sample-private-002 | 7 | status=5 (`空室/入居`) | 6 | 1 | 678,000 yen | — |
| sample-private-003 | 6 | status=5 (`状況`) | 4 | 2 | 508,000 yen | 【1F区画】, 【2F区画】 excluded |

### Comparison with original evaluation (PR #24)

| Sample ID | Prev rows | Current rows | Prev status col | Current status col | Regression? |
|-----------|-----------|-------------|-----------------|-------------------|-------------|
| sample-private-001 | 8 | 8 | 5 | 5 | None ✓ |
| sample-private-002 | 7 | 7 | 5 | 5 | None ✓ |
| sample-private-003 | 6 | 6 | 5 | 5 | None ✓ |

No regressions detected. All three synthetic samples continue to produce the same
extraction results after the Issue #29 (status column detection) and Issue #30
(summary row filtering) fixes.

**Why no regression**: the `入居状況`, `空室/入居`, and `状況` headers in these samples are
unambiguous status aliases that are not affected by `_PERSON_NAME_DENY`,
`_DATE_HEADER_DENY`, or `_SUMMARY_ROW_LABELS`. The subheader rows in sample-private-003
use `【…】` bracket prefix detection (condition 1 in `_is_non_data_row`), which is
unaffected by the new summary-label condition 3.

---

## Issue #21 Status

**No qualifying real-world text-based rent roll PDF is available at this time.**

Per `V040_REAL_WORLD_PDF_EVALUATION_REPORT.md` § "Issue #21 Closure Criteria",
Issue #21 must remain open until at least one qualifying real-world text-based rent roll
PDF has been evaluated privately and the sanitized result recorded publicly.

This evaluation confirms the waiting state: no new real-world samples are available.
No implementation work is required or performed in this waiting state.

---

## Issue Status Recommendation

### Issue #21 — Evaluate additional private rent roll PDF samples

**Recommended action**: **keep open**

**Reason**: No qualifying real-world text-based rent roll PDF is present in `samples/private/`
at the time of this evaluation. The minimum closure condition (at least 1 qualifying real-world
PDF evaluated) is not met. Issue #21 remains open pending real-world sample availability.

**Re-open trigger**: When at least 1 qualifying real-world text-based rent roll PDF is
placed in `samples/private/`, evaluate it using `--dry-run` and record the sanitized result
in `V040_REAL_WORLD_PDF_EVALUATION_REPORT.md` or a new evaluation file.

### Issue #19 — Plan v0.4.0 additional real-world PDF evaluation

**Recommended action**: **keep open** — depends on Issue #21.

### Issue #22 — Summarize v0.4.0 findings and decide next scope

**Recommended action**: **keep open** — depends on Issue #21.

---

## Conclusion

The Issue #29 and Issue #30 fix chain is complete and verified (PRs #31–#38). All three
existing synthetic samples pass without regression on the updated main. The `realistic_anonymized_001`
sample produces correct results (rows=20, occupied=17, vacant=3, GPI=2,030,000 yen/month).

However, no qualifying real-world text-based rent roll PDF is available in `samples/private/`.
Issue #21 remains open in the waiting state. No implementation changes are made in this branch.
