# v0.4.0 Realistic Anonymized Sample Re-evaluation After Status Fix

## Scope

- sample_id: `realistic_anonymized_001`
- sample type: realistic anonymized text-based rent roll PDF
- related issues: #19, #21, #22, #29, #30
- related PRs: #27, #28, #31, #32, #33
- private PDF: not committed
- PII: not committed
- implementation changes in this evaluation branch: none

> **重要**: 本ツールは不動産鑑定評価ではありません。出力される金額は「収益試算値」であり、
> 鑑定評価による「収益価格」ではありません。欠損項目は補完しません。

---

## Background

The previous evaluation (PR #27 / PR #28) against v0.3.0-pre-fix showed:

| Field | Previous result |
|-------|----------------|
| exit code | 0 |
| extracted rows | 21 |
| column_map (status) | col 4 (`入居者名`) — false positive |
| GPI | 0 yen |
| Root cause | `入居者名` matched `("入居", "status")` alias via substring; `ステータス` not recognized |

PR #31, #32, and #33 addressed Japanese status column detection:

| PR | Change |
|----|--------|
| #31 | Removed `("入居", "status")` alias; added `("ステータス", "status")` |
| #32 | Restored `("入居", "status")` alias; added `_PERSON_NAME_DENY = {"者名", "テナント名"}` to block person-name columns |
| #33 | Extended `_PERSON_NAME_DENY` to `{"者名", "テナント名", "入居者"}` to also block standalone `入居者` |

---

## Re-evaluation Command

```text
PYTHONPATH=src python -m revenue_kun.cli \
  --rent-roll-pdf samples/private/realistic_anonymized_001.pdf \
  --assumptions assumptions.sample.yaml \
  --dry-run
```

main HEAD at time of evaluation: `6561623` (Merge pull request #33)

---

## Re-evaluation Result

### Dry-run output

```text
================================================================
  収益還元クン v0.3.0  （Phase 2 / PDF抽出 / ドライラン）
  本ツールは不動産鑑定評価ではありません。（略）
================================================================
PDF抽出: realistic_anonymized_001.pdf から 21 区画を抽出しました（欠損セル 26 件）。
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

### extraction_log.json (key fields)

| Field | Value |
|-------|-------|
| rows_extracted | 21 |
| cells_missing | 26 |
| column_map | room=0, area=3, **status=5**, rent=7, cam=8, notes=14 |
| GPI | 0 yen |
| NOI | −7,500,000 yen |
| indicated_value | −188,888,889 yen (invalid) |

---

## Per-column Header Resolution (Post-fix)

| Col | Header (raw) | Resolved key | Expected | Correct? |
|-----|-------------|--------------|----------|---------|
| 0 | 部屋番号 | `room` | `room` | ✓ |
| 1 | 階 | `None` | `None` | ✓ |
| 2 | 間取り | `None` | `None` | ✓ |
| 3 | 賃貸面積(㎡) | `area` | `area` | ✓ |
| 4 | 入居者名 | **`None`** | `None` | ✓ **fixed by #32** |
| 5 | 入居日 | **`status`** | `None` | ✗ **new false positive** |
| 6 | 契約満了日 | `None` | `None` | ✓ |
| 7 | 賃料(円/月) | `rent` | `rent` | ✓ |
| 8 | 共益費(円/月) | `cam` | `cam` | ✓ |
| 9 | 月額合計(円/月) | `None` | `None` | ✓ |
| 10 | 年間賃料(円) | `rent` | `None` | — (first-match at col 7 wins; no effect) |
| 11 | 敷金(円) | `None` | `None` | ✓ |
| 12 | 礼金(円) | `None` | `None` | ✓ |
| 13 | ステータス | `status` | `status` | — (col 5 already consumed; never registered) |
| 14 | 備考 | `notes` | `notes` | ✓ |

---

## Root Cause of Remaining GPI=0

### What changed

`入居者名` (col 4) is now correctly resolved to `None` — the PR #32 fix works as intended.

`ステータス` is now recognized as the `status` key by `_resolve_header_key` — the PR #31 fix works.

### New false positive: `入居日` → `status`

`入居日` (move-in date, col 5) contains the substring `入居`, which matches the
`("入居", "status")` alias restored in PR #32. `入居日` is **not** in `_PERSON_NAME_DENY`
(which only blocks `者名`, `テナント名`, `入居者`) because it is a date column, not a
person/tenant-name column.

Since `_build_column_map` uses first-match semantics, col 5 (`入居日`) is registered as
`status` before col 13 (`ステータス`) is reached. Col 13 is never registered.

### Effect

The status column (col 5) contains move-in date strings such as `2024/04/01`. These do not
match any recognized status vocabulary in `_normalize_status` (`入居`, `稼働`, `賃貸中`,
`使用中`, `空室`, `空き`, `募集`). The raw date strings are returned as-is. `is_occupied`
then checks `稼働状況 in ("稼働", "入居", "賃貸中", "使用中")`, which is `False` for all date
values. Three units with no `入居日` (vacant units 103, 205, 208) have `status=None`, also
`is_occupied=False`.

Result: all 21 extracted units (20 actual + 1 summary row) are treated as vacant.
GPI = 0 yen. Same incorrect outcome as before the fix, but with a different root cause.

### Previous vs current false positive chain

| Step | Previous (pre-fix) | Current (post-fix) |
|------|-------------------|-------------------|
| Col 4 (`入居者名`) | → `status` (false positive; first-match wins) | → `None` ✓ |
| Col 5 (`入居日`) | → consumed as 2nd `status` candidate, discarded | → `status` (**new** false positive; first-match wins) |
| Col 13 (`ステータス`) | → unrecognized (no alias) | → recognized by `_resolve_header_key`, but never registered (col 5 already consumed `status`) |
| status values seen | `None` (all — col 4 cells were empty) | date strings (e.g. `2024/04/01`) — not status vocabulary |
| GPI | 0 | 0 |

---

## Comparison: Previous vs Re-evaluation

| Metric | Previous (PR #27) | Re-evaluation |
|--------|-------------------|---------------|
| exit code | 0 | 0 |
| extracted rows | 21 | 21 |
| `入居者名` → status? | Yes (false positive) | **No** ✓ |
| `ステータス` recognized by `_resolve_header_key`? | No | **Yes** ✓ |
| `ステータス` registered in column_map? | No | **No** — col 5 consumes first |
| status mapped column | col 4 (`入居者名`) | col 5 (`入居日`) |
| status values | all `None` | date strings / `None` |
| occupied units | 0 | 0 |
| GPI | 0 yen | 0 yen |
| Root cause | `入居者名` false positive + `ステータス` no alias | `入居日` false positive + first-match blocks `ステータス` |

---

## Progress Assessment for Issue #29

| Acceptance criterion | Status |
|----------------------|--------|
| `入居者名` → not `status` | ✓ Fixed (PR #32) |
| `入居者` → not `status` | ✓ Fixed (PR #33) |
| `契約者名` → not `status` | ✓ Fixed (PR #32) |
| `テナント名` → not `status` | ✓ Fixed (PR #32) |
| standalone `入居` → `status` | ✓ Preserved (PR #32) |
| `ステータス` recognized as `status` key | ✓ Fixed (PR #31) |
| `ステータス` registered in column_map for this sample | ✗ Blocked by `入居日` false positive |
| GPI correct (non-zero) for occupied sample | ✗ Still 0 |

---

## Remaining Limitation: Date Columns Containing `入居`

**Severity**: High (GPI=0 persists; same silent wrong result as before fix)

Column headers that are date fields and contain `入居` as a substring — such as `入居日`
(move-in date) — are not excluded by `_PERSON_NAME_DENY`, which only targets person/tenant-name
suffixes. These date-type columns match the `("入居", "status")` alias and can consume the
`status` slot before the correct column is reached.

Known date-type headers with this pattern:

| Header | Meaning | Contains alias token |
|--------|---------|---------------------|
| `入居日` | move-in date | `入居` |
| `入居開始日` | tenancy start date | `入居` |

Other date columns that do not currently conflict (`退去日`, `契約満了日`, `契約日`) do not
contain any registered status alias token and are not affected.

**Pattern**: date column header ⊃ status alias token → first-match consumes `status` slot.
**Effect**: correct `ステータス` column at later column index is never registered.
**Safe failure**: not triggered — same reason as previous evaluation (Check 3 requires
`occupied_units` non-empty, but all `is_occupied=False` → Check 3 skipped; exit 0).

---

## Limitation from Previous Evaluation Still Present

### Summary row `合 計` still extracted as a unit row

The `合 計` row (last row) is still extracted as a data unit with `月額賃料_円 = 1,852,000`.
This is the Issue #30 scope and is not addressed in this re-evaluation.

---

## Issue Status Recommendation

### Issue #29 — Improve Japanese status column detection

**Recommendation**: **keep open**

**Reason**: PR #31 / #32 / #33 successfully resolved the original `入居者名` false positive and
added `ステータス` recognition. However, a new false positive on `入居日` (date column)
prevents `ステータス` from being registered in this sample's column_map. GPI remains 0 for
`realistic_anonymized_001`. Issue #29 acceptance criteria are not fully met.

A further fix is needed to exclude date-type column headers (e.g., `入居日`) from status
matching, analogous to how `_PERSON_NAME_DENY` excludes person-name headers.

### Issue #30 — Filter total and summary rows

**Recommendation**: **keep open**

**Reason**: `合 計` row remains extracted as a unit. Unrelated to status fix; no change in
this re-evaluation.

### Issue #21 — Evaluate additional private rent roll PDF samples

**Recommendation**: **keep open**

**Reason**: qualifying real-world text-based rent roll PDF evaluation is not complete. This
re-evaluation uses the same realistic anonymized sample (`realistic_anonymized_001`) that
was already established as non-qualifying for Issue #21 closure.

---

## Conclusion

PR #31 / #32 / #33 correctly fixed the `入居者名` false positive and enabled `ステータス`
recognition in `_resolve_header_key`. These are genuine, verifiable improvements.

However, for `realistic_anonymized_001`, GPI remains 0 because `入居日` (col 5) now
consumes the `status` slot via the `入居` alias before `ステータス` (col 13) is reached.
This is a pre-existing issue not covered by the Issue #29 fix scope.

A follow-up is warranted to extend the deny mechanism to date-type column headers
containing `入居` (such as `入居日`, `入居開始日`). This should be scoped as a continuation
of Issue #29 or a new narrowly-scoped follow-up issue.
