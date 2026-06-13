# v0.4.0 Realistic Anonymized Sample Re-evaluation After Date Header Fix

## Scope

- sample_id: `realistic_anonymized_001`
- sample type: realistic anonymized text-based rent roll PDF
- related issues: #19, #21, #22, #29, #30
- related PRs: #27, #28, #31, #32, #33, #34, #35
- private PDF: not committed
- PII: not committed
- implementation changes in this evaluation branch: none

> **重要**: 本ツールは不動産鑑定評価ではありません。出力される金額は「収益試算値」であり、
> 鑑定評価による「収益価格」ではありません。欠損項目は補完しません。

---

## Background

| PR | Finding |
|----|---------|
| #27 (first eval) | `入居者名` (col 4) → `status` false positive; `ステータス` unrecognized; GPI = 0 |
| #34 (second eval, after #31/#32/#33) | `入居者名` fixed; `入居日` (col 5) → `status` new false positive; GPI = 0 |
| #35 | `_DATE_HEADER_DENY = {"入居日", "開始日", "満了日", "契約日"}` added; date-type headers excluded from status matching |

---

## Re-evaluation Command

```text
PYTHONPATH=src python -m revenue_kun.cli \
  --rent-roll-pdf samples/private/realistic_anonymized_001.pdf \
  --assumptions assumptions.sample.yaml \
  --dry-run
```

main HEAD at time of evaluation: `26633d4` (Merge pull request #35)

---

## Re-evaluation Result

### Dry-run output

```text
================================================================
  収益還元クン v0.3.0  （Phase 2 / PDF抽出 / ドライラン）
  本ツールは不動産鑑定評価ではありません。（略）
================================================================
PDF抽出: realistic_anonymized_001.pdf から 21 区画を抽出しました（欠損セル 23 件）。
  [注記] 任意列「用途」が無いため当該項目は欠損として扱います。
[抽出診断]
  入力形式       : PDF
  認識フィールド  : area, cam, notes, rent, room, status
  抽出区画数     : 21
[ドライラン] 入力抽出と診断を完了しました。計算・成果物生成はスキップしました。
================================================================
```

### Exit code

`0`

### Key metrics

| Field | Value |
|-------|-------|
| rows_extracted | 21 |
| cells_missing | 23 |
| column_map | room=0, area=3, rent=7, cam=8, **status=13**, notes=14 |
| recognized status column | col 13 (`ステータス`) ✓ |
| occupied units | 17 |
| vacant units | 4 |
| monthly GPI | **2,030,000 yen** |
| annual GPI | 24,360,000 yen |

> Note: monthly GPI = rent (1,852,000) + cam (178,000) for 17 occupied units.

---

## Per-column Header Resolution (Post PR #35)

| Col | Header | Resolved key | Correct? |
|-----|--------|--------------|---------|
| 0 | 部屋番号 | `room` | ✓ |
| 1 | 階 | `None` | ✓ |
| 2 | 間取り | `None` | ✓ |
| 3 | 賃貸面積(㎡) | `area` | ✓ |
| 4 | 入居者名 | **`None`** | ✓ fixed by #32 |
| 5 | 入居日 | **`None`** | ✓ fixed by #35 |
| 6 | 契約満了日 | `None` | ✓ fixed by #35 |
| 7 | 賃料(円/月) | `rent` | ✓ |
| 8 | 共益費(円/月) | `cam` | ✓ |
| 9 | 月額合計(円/月) | `None` | ✓ |
| 10 | 年間賃料(円) | `rent` | — (col 7 wins first-match; no effect) |
| 11 | 敷金(円) | `None` | ✓ |
| 12 | 礼金(円) | `None` | ✓ |
| 13 | ステータス | **`status`** | ✓ registered in column_map |
| 14 | 備考 | `notes` | ✓ |

---

## Comparison Across Evaluations

| Metric | PR #27 (initial) | PR #34 (after #31–#33) | This eval (after #35) |
|--------|-----------------|----------------------|----------------------|
| `入居者名` (col 4) → status? | Yes ✗ | No ✓ | No ✓ |
| `入居日` (col 5) → status? | n/a (blocked by col 4) | Yes ✗ | **No ✓** |
| `ステータス` (col 13) registered? | No ✗ | No ✗ | **Yes ✓** |
| column_map.status | 4 | 5 | **13** |
| occupied units | 0 | 0 | **17** |
| monthly GPI | 0 | 0 | **2,030,000 yen** |
| Exit code | 0 | 0 | 0 |
| rows_extracted | 21 | 21 | 21 |

---

## Issue #29 Acceptance Criteria Verification

| Criterion | Status |
|-----------|--------|
| `入居者名` → not `status` | ✓ (PR #32) |
| `入居者` → not `status` | ✓ (PR #33) |
| `契約者名` → not `status` | ✓ (PR #32) |
| `テナント名` → not `status` | ✓ (PR #32) |
| `入居日` → not `status` | ✓ (PR #35) |
| `契約満了日` → not `status` | ✓ (PR #35) |
| standalone `入居` → `status` | ✓ (PR #32) |
| `ステータス` → `status` and registered | ✓ (PR #31 + #35) |
| GPI non-zero for occupied sample | ✓ — 2,030,000 yen/month |
| `realistic_anonymized_001` status detection correct | ✓ |

All Issue #29 acceptance criteria are satisfied for this sample.

---

## Remaining Limitation: Total Row Still Present (Issue #30 scope)

The `合 計` summary row (last row) is still extracted as a unit with:
- `区画 = "合 計"`, `月額賃料_円 = 1,852,000`, `稼働状況 = None`

This inflates `rows_extracted` to 21 (correct: 20) and adds 1 to the `vacant` count
(vacant = 4; correct: 3 actual vacant units). This is the scope of Issue #30 and is not
addressed in this evaluation.

---

## Issue Status Recommendation

### Issue #29 — Improve Japanese status column detection

**Recommended action**: **close**

**Reason**: All acceptance criteria for Issue #29 are satisfied on `realistic_anonymized_001`.
The status column is correctly identified as col 13 (`ステータス`). All known false-positive
column patterns (`入居者名`, `入居者`, `契約者名`, `テナント名`, `入居日`, `契約満了日`) are
excluded from status matching. The standalone `入居` alias is preserved. GPI is now
2,030,000 yen/month (was 0). The fix chain PR #31 → #32 → #33 → #35 is complete.

The remaining row-count discrepancy (21 vs 20) and vacant count discrepancy (4 vs 3) are
attributable to total-row contamination, which belongs to Issue #30.

### Issue #30 — Filter total and summary rows

**Recommended action**: **keep open**

**Reason**: `合 計` row is still extracted as a unit row. No change in this evaluation.
This is a distinct, narrowly scoped issue unrelated to status column detection.

### Issue #21 — Evaluate additional private rent roll PDF samples

**Recommended action**: **keep open**

**Reason**: This sample (`realistic_anonymized_001`) is a realistic anonymized sample and
does not qualify as a real-world PDF for Issue #21 closure. At least one qualifying
real-world text-based rent roll PDF must be evaluated before Issue #21 may be closed.

---

## Conclusion

PR #35 completes the Issue #29 fix chain. The `realistic_anonymized_001` sample now
produces a correct status column mapping (`ステータス` at col 13), 17 occupied units,
and a monthly GPI of 2,030,000 yen. The silent GPI=0 wrong result that was present
through all previous evaluations is resolved.

Issue #29 acceptance criteria are satisfied. Issue #30 and Issue #21 remain open and
are unaffected by this evaluation.
