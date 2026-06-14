# v0.4.0 Realistic Anonymized Sample Re-evaluation After Summary Row Fix

## Scope

- sample_id: `realistic_anonymized_001`
- sample type: realistic anonymized text-based rent roll PDF
- related issues: #19, #21, #22, #30
- related PRs: #27, #28, #31, #32, #33, #34, #35, #36, #37
- private PDF: not committed
- PII: not committed
- implementation changes in this evaluation branch: none

> **重要**: 本ツールは不動産鑑定評価ではありません。出力される金額は「収益試算値」であり、
> 鑑定評価による「収益価格」ではありません。欠損項目は補完しません。

---

## Background

| Evaluation | Result |
|------------|--------|
| PR #27 (initial) | `入居者名` → `status` false positive; GPI = 0; rows = 21; vacant = 4 |
| PR #34 (after #31–#33) | `入居日` → `status` false positive; GPI = 0; rows = 21; vacant = 4 |
| PR #36 (after #35) | status correctly col 13; GPI = 2,030,000 yen/month; rows = 21; vacant = 4 (summary row still present) |
| **This eval (after #37)** | summary row filtering active |

PR #37 added `_SUMMARY_ROW_LABELS = {"合計", "小計", "総計", "計", "total", "subtotal"}` and
extended `_is_non_data_row` to exclude rows whose room field, after whitespace collapse and
lowercasing, exactly matches a known summary label.

---

## Re-evaluation Command

```text
PYTHONPATH=src python -m revenue_kun.cli \
  --rent-roll-pdf samples/private/realistic_anonymized_001.pdf \
  --assumptions assumptions.sample.yaml \
  --dry-run
```

main HEAD at time of evaluation: `c10ecd3` (Merge pull request #37)

---

## Re-evaluation Result

### Dry-run output

```text
================================================================
  収益還元クン v0.3.0  （Phase 2 / PDF抽出 / ドライラン）
  本ツールは不動産鑑定評価ではありません。（略）
================================================================
PDF抽出: realistic_anonymized_001.pdf から 20 区画を抽出しました（欠損セル 20 件）。
  [注記] 任意列「用途」が無いため当該項目は欠損として扱います。
  [注記] 「合 計」行を小見出し・ヘッダーと判定し除外しました。
[抽出診断]
  入力形式       : PDF
  認識フィールド  : area, cam, notes, rent, room, status
  抽出区画数     : 20
[ドライラン] 入力抽出と診断を完了しました。計算・成果物生成はスキップしました。
================================================================
```

### Exit code

`0`

### Key metrics

| Field | Value |
|-------|-------|
| rows_extracted | **20** |
| cells_missing | 20 |
| column_map | room=0, area=3, rent=7, cam=8, status=13, notes=14 |
| recognized status column | col 13 (`ステータス`) ✓ |
| occupied units | **17** |
| vacant units | **3** |
| monthly GPI | **2,030,000 yen** |
| annual GPI | 24,360,000 yen |
| `合 計` row present? | **No** — excluded, noted in report |

---

## Comparison Across Evaluations

| Metric | PR #27 | PR #34 | PR #36 | **This eval** |
|--------|--------|--------|--------|--------------|
| status column | col 4 ✗ | col 5 ✗ | col 13 ✓ | col 13 ✓ |
| GPI (yen/month) | 0 | 0 | 2,030,000 | 2,030,000 |
| rows_extracted | 21 | 21 | 21 | **20** ✓ |
| occupied | 0 | 0 | 17 | 17 |
| vacant | 4 | 4 | 4 | **3** ✓ |
| `合 計` row excluded? | No | No | No | **Yes** ✓ |

---

## Issue #30 Acceptance Criteria Verification

| Criterion | Status |
|-----------|--------|
| `合 計` row not extracted as unit row | ✓ |
| `合計` label excluded | ✓ (covered by _SUMMARY_ROW_LABELS + whitespace collapse) |
| `小計` label excluded | ✓ |
| `総計` label excluded | ✓ |
| `計` label excluded | ✓ |
| `TOTAL` / `Total` / `total` excluded | ✓ |
| `Subtotal` / `SUBTOTAL` / `Sub total` excluded | ✓ |
| Normal room numbers not accidentally excluded | ✓ (full-string equality, not substring) |
| rows_extracted = 20 (correct unit count) | ✓ |
| vacant = 3 (correct vacant count) | ✓ |
| GPI unaffected (summary row rent not counted) | ✓ — 2,030,000 yen/month |
| Exclusion noted in ExtractionReport.notes | ✓ |

All Issue #30 acceptance criteria are satisfied for this sample.

---

## Issue Status Recommendation

### Issue #30 — Filter total and summary rows

**Recommended action**: **close**

**Reason**: PR #37 correctly filters total and summary rows from rent roll PDF extraction.
For `realistic_anonymized_001`, the `合 計` row is excluded: `rows_extracted` is 20 (correct),
`vacant` is 3 (correct). The fix uses full-string equality after whitespace collapse and
lowercasing, preventing accidental exclusion of normal room numbers. The exclusion is
surfaced in `ExtractionReport.notes`. All Issue #30 acceptance criteria are satisfied.

### Issue #21 — Evaluate additional private rent roll PDF samples

**Recommended action**: **keep open**

**Reason**: This sample (`realistic_anonymized_001`) is a realistic anonymized sample and
does not qualify as a real-world PDF for Issue #21 closure. At least one qualifying
real-world text-based rent roll PDF must be evaluated before Issue #21 may be closed.

### Issue #19 / #22

**Recommended action**: **keep open** unless separately reviewed.

Issue #19 is the v0.4.0 parent issue; Issue #22 is the evaluation findings summary.
Both depend on Issue #21 and remain open.

---

## Conclusion

PR #37 completes the Issue #30 fix. `realistic_anonymized_001` now produces the fully
correct extraction result: 20 unit rows, 17 occupied, 3 vacant, GPI = 2,030,000 yen/month,
status correctly mapped to `ステータス` (col 13), and the `合 計` summary row excluded and
noted in the report.

Together with the Issue #29 fix chain (PR #31–#33, #35), the extraction pipeline now
handles the column misdetection and summary-row contamination patterns observed in the
initial evaluation. Issue #30 acceptance criteria are satisfied. Issue #21 remains open
pending a qualifying real-world PDF evaluation.
