# V040 Realistic Anonymized Sample Evaluation

## Purpose

This file records evaluation of a realistic anonymized text-based rent roll PDF
against the revenue-kun v0.3.0 CLI.

This sample is **not treated as a qualifying real-world PDF for Issue #21 closure**.
See "Issue #21 closure qualification" at the end of this document.

> **重要**: 本ツールは不動産鑑定評価ではありません。出力される金額は「収益試算値」であり、
> 鑑定評価による「収益価格」ではありません。欠損項目は補完しません。

---

## Sample Metadata

| Field | Value |
|-------|-------|
| sample_id | `realistic_anonymized_001` |
| sample_type | realistic anonymized text-based rent roll PDF |
| real_world_qualifying | no |
| reason | Placeholder / anonymized address; not confirmed as operational real-world rent roll |
| text_based | yes |
| OCR_required | no |
| pages | 1 |
| pdf_committed | no |
| pii_committed | no |
| issue_21_closure_candidate | no |

---

## PDF Structure (Pre-Evaluation Observation)

Observed by direct inspection with pdfplumber before CLI evaluation.

| Element | Detail |
|---------|--------|
| Tables on page | 2 |
| Table 1 (main rent roll) | 22 rows × 15 columns (1 header + 20 unit rows + 1 summary row) |
| Table 2 (summary) | 7 rows × 2 columns |
| Total units | 20 |
| Occupied units | 17 |
| Vacant units | 3 |
| Occupancy rate | 85.0% |
| Expected full-occupancy monthly rent | 2,147,000 yen |
| Current monthly rent income | 1,852,000 yen |
| Monthly vacancy loss | 295,000 yen |

### Table 1 column structure

| Index | Header | Maps to (revenue-kun) | Note |
|-------|--------|----------------------|------|
| 0 | 部屋番号 | `room` | ✓ correct |
| 1 | 階 | (unrecognized) | — |
| 2 | 間取り | (unrecognized) | — |
| 3 | 賃貸面積(㎡) | `area` | ✓ correct |
| 4 | 入居者名 | **`status` (false positive)** | ⚠ "入居" token matches; all cells empty |
| 5 | 入居日 | (unrecognized; "入居" already consumed by col 4) | — |
| 6 | 契約満了日 | (unrecognized) | — |
| 7 | 賃料(円/月) | `rent` | ✓ correct |
| 8 | 共益費(円/月) | `cam` | ✓ correct |
| 9 | 月額合計(円/月) | (unrecognized) | — |
| 10 | 年間賃料(円) | (unrecognized; "賃料" already consumed by col 7) | — |
| 11 | 敷金(円) | (unrecognized) | — |
| 12 | 礼金(円) | (unrecognized) | — |
| 13 | ステータス | **(unrecognized; no alias for "ステータス")** | ⚠ actual status values here |
| 14 | 備考 | `notes` | ✓ correct |

---

## CLI Evaluation

### Command

```text
PYTHONPATH=src python -m revenue_kun.cli \
  --rent-roll-pdf samples/private/realistic_anonymized_001.pdf \
  --assumptions assumptions.sample.yaml \
  --dry-run
```

### Dry-run output

```text
================================================================
  収益還元クン v0.3.0  （Phase 2 / PDF抽出 / ドライラン）
  本ツールは不動産鑑定評価ではありません。（略）
================================================================
PDF抽出: realistic_anonymized_001.pdf から 21 区画を抽出しました（欠損セル 43 件）。
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

### Full-run diagnostics (extraction_log.json summary)

| Field | Value |
|-------|-------|
| phase | Phase 2 (PDF extraction) |
| extraction_method | pdf |
| pages | 1 |
| rows_extracted | 21 |
| cells_missing | 43 |
| recognized canonical fields | area, cam, notes, rent, room, status |
| column_map | room=0, area=3, status=4, rent=7, cam=8, notes=14 |
| notes | 任意列「用途」が無いため当該項目は欠損として扱います |
| GPI | 0 yen |
| NOI | −7,500,000 yen (operating expenses from assumptions.sample.yaml; no rental income) |
| indicated value | −188,888,889 yen (invalid; GPI=0 is a misdetection artifact) |

> The indicated value above is not meaningful. It reflects GPI=0 caused by status column
> misdetection, not actual vacancy. Do not use this figure.

---

## Observed Limitations

### Limitation 1 — Status column false positive (`入居者名` → `status`)

**Severity**: High (causes GPI=0, silent wrong result)

The header `入居者名` (tenant name) contains the substring `入居`, which is registered as a
`status` alias in `_HEADER_KEYS`. This causes column 4 to be mapped to `status` instead
of the correct column 13 (`ステータス`).

Column 4 (`入居者名`) contains no values in this sample (tenant names are absent/anonymized).
As a result, `稼働状況` is `None` for all 21 extracted units, `is_occupied` returns `False`
for all units, and GPI is calculated as 0 yen.

The correct status values ("入居中" × 17, "空室" × 3) are in column 13 (`ステータス`), which
is not recognized (see Limitation 2).

**Pattern**: `入居者名` (tenant name column) ⊃ `入居` (status alias token).
**Effect**: first-match wins; col 4 consumed as `status` before col 13 is reached.
**Safe failure**: not triggered — Check 3 in `pdf_extract.py` requires `occupied_units`
to be non-empty, but since all `status=None`, `occupied_units=[]` and Check 3 is skipped.
The tool exits 0 with a silently wrong GPI.

### Limitation 2 — `ステータス` column header not recognized

**Severity**: High (root cause of status misdetection going undetected)

The column header `ステータス` (katakana transliteration of "status") is not present in
`_HEADER_KEYS`. None of the registered status aliases (`入居`, `空室`, `稼働`, `occupancy`,
`status`, `状況`) match `ステータス` as a substring.

If `ステータス` were added as an alias, column 13 would be correctly mapped to `status`,
yielding `稼働状況 = "入居"` for 17 units and `"空室"` for 3 units, and GPI ≈ 22,224,000 yen/year.

**Pattern**: `ステータス` (common Japanese column header) not in alias table.
**Effect**: status column at col 13 goes unrecognized; false positive at col 4 wins.

### Limitation 3 — Summary row `合 計` extracted as a unit row

**Severity**: Low (data quality issue; does not affect occupancy or GPI calculation in this case)

The table's last row is a summary total row with `部屋番号 = "合 計"`. The current
`_is_non_data_row()` check does not match this pattern:

- It does not start with `【`, `[`, `(`, or `（` (bracket-prefix check fails)
- It does not contain a room header token such as `部屋`, `号室`, `区画`, `unit`, `room`

As a result, `合 計` is extracted as a unit with `月額賃料_円 = 1,852,000` (the monthly total).
This inflates the extracted row count by 1 (21 instead of 20) and would inflate GPI if
status detection were working correctly.

**Pattern**: summary rows with label text `合 計`, `合計`, `小計`, `計` not filtered.
**Effect**: +1 spurious unit with inflated rent value.

### Limitation 4 — `cells_missing` count breakdown

| Source | Count |
|--------|-------|
| `use` column absent (all 21 rows) | 21 |
| `status` = None (col 4 empty, all 21 rows) | 21 |
| `area` = None for `合 計` row | 1 |
| Total | **43** |

---

## Dry-run Usability Assessment

| Aspect | Result |
|--------|--------|
| Tool completes without error | Yes (exit 0) |
| Diagnostics output readable | Yes |
| Recognized field list matches expected | No — `status` shown as recognized but mapped to wrong column |
| Unit count shown accurately | No — 21 shown; correct is 20 (excluding summary row) |
| GPI=0 surfaced as warning | No — silent wrong result |
| `--dry-run` useful for quick validation | Partially — shows structural success but masks status misdetection |

---

## Missing Cells Summary (extraction_log.json)

- `missing_required_count`: 0
- `missing_optional_count`: 24
  - `建築時期` (assumptions): 1
  - `管理委託費` (assumptions): 1
  - `想定（市場）賃料` (all 21 rows, including summary): 21
  - `専有面積` for `合 計` row: 1

---

## Recommended Action

`future_issue_candidate`

Two narrow, evidence-based follow-up issues are warranted:

| # | Pattern | Suggested fix |
|---|---------|---------------|
| A | `ステータス` alias gap | Add `"ステータス"` (and optionally `"ステータス"` variants) to `_HEADER_KEYS` status aliases |
| B | Summary row `合 計` not filtered | Add keyword-match check in `_is_non_data_row()` for `合計`/`合 計`/`小計`/`計` as room value |

These should be filed as separate, narrowly scoped issues. No implementation should proceed
without the issue being filed and reviewed first.

---

## Issue #21 Closure Qualification

**This sample does not qualify for Issue #21 closure.**

| Criterion | Status |
|-----------|--------|
| Qualifying real-world PDF | No — realistic anonymized sample; not confirmed operational |
| Private evaluation completed | Yes |
| Sanitized result recorded publicly | Yes (this document) |
| No private PDF / PII committed | Yes |
| No implementation change introduced | Yes |

Per `V040_REAL_WORLD_PDF_EVALUATION_REPORT.md` § "Issue #21 Closure Criteria":
synthetic-only and anonymized samples are not sufficient to close Issue #21.
At least 1 qualifying real-world text-based rent roll PDF must be evaluated before Issue #21 may be closed.

---

## Conclusion

The revenue-kun v0.3.0 CLI processes this realistic anonymized rent roll PDF without crashing
(exit 0). However, the evaluation reveals two `future_issue_candidate` patterns:

1. **Status column alias gap**: `ステータス` is not recognized; `入居者名` is a false positive.
   Result: GPI=0 (silent wrong result, no safe failure triggered).
2. **Summary row not filtered**: `合 計` row extracted as a unit row.

These findings are evidence-based and narrow enough to support future issue creation.
No implementation is done in this evaluation branch.

Issue #21 remains open. This evaluation does not satisfy the real-world qualifying condition.
