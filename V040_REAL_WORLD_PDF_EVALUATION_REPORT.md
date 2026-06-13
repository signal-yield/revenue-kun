# V040 Real-World PDF Evaluation Report

## Summary

This report documents the evaluation of additional real-world text-based rent roll PDFs for `revenue-kun v0.4.0`.

- **v0.4.0 goal**: Evaluate additional real-world text-based rent roll PDFs to determine whether PDF support should be expanded in a future release.
- **Approach**: evaluation-first. No new PDF extraction heuristics are implemented in v0.4.0.
- **Baseline**: v0.2.0 introduced limited text-based PDF ingestion for simple rent roll tables. v0.3.0 added CLI diagnostics summary and `--dry-run` mode.
- **Evaluation tools**: v0.3.0 `--dry-run` and diagnostics summary are the primary evaluation commands.
- **PDF extraction scope**: not expanded during this evaluation. Scope decisions are deferred until findings are documented.
- **Evaluation date**: 2026-06-13

> **重要**: 本ツールは不動産鑑定評価ではありません。出力される金額は「収益試算値」であり、鑑定評価による「収益価格」ではありません。欠損項目は補完しません。

### Evaluation result note

The 3 samples evaluated are the existing v0.2.0 synthetic reportlab-generated PDFs, not additional real-world PDFs.
`samples/private/` did not contain additional real-world rent roll PDFs at the time of this evaluation.
v0.4.0 real-world evaluation is pending additional real-world samples being made available.

---

## Evaluation Policy

- Evaluate 3 to 5 additional private rent roll PDF samples where available.
- Private PDFs must be stored only under `samples/private/` or another gitignored location.
- Private PDFs and PII must not be committed.
- OCR, scanned PDFs, and vendor-specific heuristics are not implemented during this evaluation.
- Each sample receives one of the following recommended actions based on observed behavior:
  - `support_with_current_logic`
  - `document_as_unsupported`
  - `future_issue_candidate`
  - `reject_as_out_of_scope`
- Future implementation issues are created only if evaluation findings justify a narrow, evidence-based scope.

---

## Sample Inventory

| Sample ID | Private location | Source type | Text-based or scanned | PII risk | Evaluation status | Notes |
|-----------|-----------------|-------------|----------------------|----------|-------------------|-------|
| sample-private-001 | `samples/private/` | synthetic (v0.2.0 reportlab) | text-based | none | complete | Simple layout, 1 page |
| sample-private-002 | `samples/private/` | synthetic (v0.2.0 reportlab) | text-based | none | complete | Japanese column name variation, 2 missing cells |
| sample-private-003 | `samples/private/` | synthetic (v0.2.0 reportlab) | text-based | none | complete | Sub-header rows (floor zone headers), 2 excluded |
| sample-private-004 | n/a | n/a | n/a | n/a | not available | No additional real-world PDF available |
| sample-private-005 | n/a | n/a | n/a | n/a | not available | No additional real-world PDF available |

> Private file names and paths that reveal sensitive information should not be committed. Use sample IDs in this report.

---

## Per-Sample Evaluation Matrix

| Sample ID | text-based / scanned | pdfplumber table extraction | detected table count | recognized canonical fields | extracted unit count | excluded non-data rows | malformed monthly rent fields | safe failure behavior | `--dry-run` usefulness | `extraction_log.json` usefulness | PII / privacy notes | recommended action |
|-----------|---------------------|---------------------------|---------------------|---------------------------|---------------------|----------------------|------------------------------|----------------------|----------------------|--------------------------------|--------------------|--------------------|
| sample-private-001 | text-based | success | 1 | area, cam, rent, room, status, use | 8 | 0 | none observed | not triggered (exit 0) | useful — shows fields + unit count, no artifacts | generated (normal run); extracted_units_count=8; some optional fields null | none (synthetic) | `support_with_current_logic` |
| sample-private-002 | text-based | success | 1 | area, cam, rent, room, status, use | 7 | 0 | 2 missing cells (not malformed rent format) | not triggered (exit 0) | useful | not checked in normal run | none (synthetic) | `support_with_current_logic` |
| sample-private-003 | text-based | success | 1 | area, cam, rent, room, status, use | 6 | 2 (floor zone sub-header rows) | none observed | not triggered (exit 0) | useful — sub-header exclusion notes visible | not checked in normal run | none (synthetic) | `support_with_current_logic` |

---

## Extraction Diagnostics Results

### Success example

```text
[抽出診断]
  入力形式       : PDF
  認識フィールド  : room, status, rent, area
  抽出区画数     : 12
```

### Failure example

```text
[抽出診断]
  入力形式       : PDF
  抽出結果       : 失敗
  failure_reason : ...
```

### Per-sample records

#### sample-private-001

```text
[抽出診断]
  入力形式       : PDF
  認識フィールド  : area, cam, rent, room, status, use
  抽出区画数     : 8
[ドライラン] 入力抽出と診断を完了しました。計算・成果物生成はスキップしました。
```

#### sample-private-002

```text
[抽出診断]
  入力形式       : PDF
  認識フィールド  : area, cam, rent, room, status, use
  抽出区画数     : 7
[ドライラン] 入力抽出と診断を完了しました。計算・成果物生成はスキップしました。
```

#### sample-private-003

```text
(注記) 【1F区画】行を小見出し・ヘッダーと判定し除外しました。
(注記) 【2F区画】行を小見出し・ヘッダーと判定し除外しました。
[抽出診断]
  入力形式       : PDF
  認識フィールド  : area, cam, rent, room, status, use
  抽出区画数     : 6
[ドライラン] 入力抽出と診断を完了しました。計算・成果物生成はスキップしました。
```

---

## Dry-Run Results

Command pattern used: `python -m revenue_kun.cli --rent-roll-pdf <private-pdf> --assumptions assumptions.sample.yaml --dry-run`

### sample-private-001

| Field | Detail |
|-------|--------|
| command used | `--rent-roll-pdf <sample-private-001> --assumptions assumptions.sample.yaml --dry-run` |
| exit code | 0 |
| diagnostics summary | input type PDF / 6 canonical fields recognized / 8 units extracted |
| generated artifacts | none |
| calculation skipped | yes |
| output understandable | yes |

### sample-private-002

| Field | Detail |
|-------|--------|
| command used | `--rent-roll-pdf <sample-private-002> --assumptions assumptions.sample.yaml --dry-run` |
| exit code | 0 |
| diagnostics summary | input type PDF / 6 canonical fields recognized / 7 units extracted |
| generated artifacts | none |
| calculation skipped | yes |
| output understandable | yes |

### sample-private-003

| Field | Detail |
|-------|--------|
| command used | `--rent-roll-pdf <sample-private-003> --assumptions assumptions.sample.yaml --dry-run` |
| exit code | 0 |
| diagnostics summary | input type PDF / 6 canonical fields recognized / 6 units extracted / 2 sub-header rows excluded |
| generated artifacts | none |
| calculation skipped | yes |
| output understandable | yes — sub-header exclusion notes clearly visible |

---

## extraction_log.json Observations

`extraction_log.json` is not generated during `--dry-run`. Checked via normal execution on sample-private-001 only.

| Field | sample-private-001 | sample-private-002 | sample-private-003 |
|-------|-------------------|--------------------|-------------------|
| generated | yes (normal run) | not checked | not checked |
| failure flag | None (not False; expected False for success) | — | — |
| failure_reason | None | — | — |
| extracted_units_count | 8 | — | — |
| missing_cells_count | None (not populated for PDF path) | — | — |
| input_type | None (not populated for PDF path) | — | — |
| column_map keys | [] (empty for PDF path) | — | — |
| usefulness | partial — unit count useful; several optional fields null | — | — |
| issues found | Some optional fields (`input_type`, `column_map`, `missing_cells_count`) not populated in PDF path | — | — |

> Note: Optional field population gaps in the PDF path may be a candidate for a narrow future issue, but do not block current functionality.

---

## PII / Privacy Notes

- Private PDFs must not be committed.
- Do not paste raw tenant names, room-level personal names, owner names, addresses, or other sensitive details into committed files.
- Use sample IDs (`sample-private-001` etc.) instead of real file names where possible.
- Only sanitized summaries may be committed to this report.
- `samples/private/` is gitignored and must remain so.
- Verified with `git check-ignore -v samples/private/` — confirmed at `.gitignore:19`.
- All 3 evaluated samples are synthetic (reportlab-generated). No real PII was present.

---

## Recommended Action Categories

| Category | Meaning |
|----------|---------|
| `support_with_current_logic` | The sample works acceptably with the current v0.3.0 extraction logic. No new heuristics are needed. |
| `document_as_unsupported` | The sample does not work and the pattern is not worth supporting. Document the boundary clearly. |
| `future_issue_candidate` | The sample fails but represents a repeated pattern that may justify a narrow future implementation issue. Do not implement without clear evidence. |
| `reject_as_out_of_scope` | The sample is scanned, requires OCR, has complex merged cells, or is otherwise definitively out of scope. |

---

## Patterns Observed

- **header alias gaps**: None observed in evaluated samples. All 6 canonical fields (area, cam, rent, room, status, use) were recognized across all 3 samples.
- **rent format issues**: None observed. Monthly rent fields were numeric and parseable in all samples.
- **sub-header patterns**: Observed in sample-private-003. Floor zone sub-headers (【1F区画】, 【2F区画】) were correctly detected and excluded by existing logic.
- **repeated header patterns**: Not observed in evaluated samples.
- **layout problems**: None observed. All samples use simple single-table layouts.
- **safe failure adequacy**: Not triggered in any sample. All 3 succeeded (exit 0). Safe failure behavior was not directly tested with failing samples in this evaluation.
- **diagnostics usability**: High. `--dry-run` output clearly shows input type, recognized fields, unit count, and any exclusion notes. Useful for quick validation without generating output artifacts.
- **extraction_log.json optional field gaps**: Some fields (`input_type`, `column_map`, `missing_cells_count`) are null in the PDF path. Not blocking, but worth noting for a potential narrow future issue.

---

## Scope Decision for Future Versions

**Caveat**: All 3 evaluated samples are existing v0.2.0 synthetic PDFs. Real-world PDF evaluation has not yet been completed. The decisions below apply only to the synthetic samples evaluated.

- [x] no implementation needed — current v0.3.0 logic handles all 3 synthetic samples correctly
- [ ] documentation-only update
- [ ] one narrow implementation issue for v0.5.0
- [ ] keep unsupported
- [x] defer broader PDF support — pending real-world sample availability

**Decision rationale**: Current v0.3.0 logic handles the 3 available synthetic samples without any changes. Real-world PDF evaluation is deferred until actual real-world rent roll PDFs are made available under `samples/private/`. A narrow future issue for `extraction_log.json` optional field population in the PDF path may be warranted, but this is not blocking.

---

## Out-of-Scope Confirmations

The following are confirmed out of scope for v0.4.0:

- OCR
- scanned PDFs
- multi-page table stitching
- complex merged cells
- vendor-specific heuristics without repeated evidence
- PII masking implementation
- broad real-world PDF support claims
- formal valuation
- investment advice
- legal advice

---

## Acceptance Checklist

- [x] At least 3 samples evaluated if available (3 synthetic samples evaluated; real-world samples not yet available)
- [x] No private PDFs committed
- [x] No PII committed
- [x] `samples/private/` remains gitignored (confirmed at `.gitignore:19`)
- [x] Each evaluated sample has a recommended action
- [x] Dry-run results recorded
- [x] Extraction diagnostics recorded
- [x] Future implementation issues are narrow and evidence-based
- [x] No extraction logic changed
