# V040 Real-World PDF Evaluation Report

## Summary

This report documents the evaluation of additional real-world text-based rent roll PDFs for `revenue-kun v0.4.0`.

- **v0.4.0 goal**: Evaluate additional real-world text-based rent roll PDFs to determine whether PDF support should be expanded in a future release.
- **Approach**: evaluation-first. No new PDF extraction heuristics are implemented in v0.4.0.
- **Baseline**: v0.2.0 introduced limited text-based PDF ingestion for simple rent roll tables. v0.3.0 added CLI diagnostics summary and `--dry-run` mode.
- **Evaluation tools**: v0.3.0 `--dry-run` and diagnostics summary are the primary evaluation commands.
- **PDF extraction scope**: not expanded during this evaluation. Scope decisions are deferred until findings are documented.

> **重要**: 本ツールは不動産鑑定評価ではありません。出力される金額は「収益試算値」であり、鑑定評価による「収益価格」ではありません。欠損項目は補完しません。

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
| sample-private-001 | `samples/private/` | real-world | TBD | TBD | not started | |
| sample-private-002 | `samples/private/` | real-world | TBD | TBD | not started | |
| sample-private-003 | `samples/private/` | real-world | TBD | TBD | not started | |
| sample-private-004 | `samples/private/` | real-world | TBD | TBD | not started | |
| sample-private-005 | `samples/private/` | real-world | TBD | TBD | not started | |

> Private file names and paths that reveal sensitive information should not be committed. Use sample IDs in this report.

---

## Per-Sample Evaluation Matrix

| Sample ID | text-based / scanned | pdfplumber table extraction | detected table count | recognized canonical fields | extracted unit count | excluded non-data rows | malformed monthly rent fields | safe failure behavior | `--dry-run` usefulness | `extraction_log.json` usefulness | PII / privacy notes | recommended action |
|-----------|---------------------|---------------------------|---------------------|---------------------------|---------------------|----------------------|------------------------------|----------------------|----------------------|--------------------------------|--------------------|--------------------|
| sample-private-001 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| sample-private-002 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| sample-private-003 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| sample-private-004 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| sample-private-005 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

---

## Extraction Diagnostics Results

Record the CLI diagnostics summary for each sample. Run with the v0.3.0 `--dry-run` mode or normal execution.

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
(fill after evaluation)
```

#### sample-private-002

```text
(fill after evaluation)
```

#### sample-private-003

```text
(fill after evaluation)
```

#### sample-private-004

```text
(fill after evaluation)
```

#### sample-private-005

```text
(fill after evaluation)
```

---

## Dry-Run Results

Record the result of running `revenue-kun --dry-run <pdf>` for each sample.

| Field | Detail |
|-------|--------|
| command used | `revenue-kun --dry-run samples/private/<sample>.pdf assumptions.yaml` |
| exit code | TBD |
| diagnostics summary | TBD |
| generated artifacts | TBD |
| calculation skipped | TBD |
| output understandable | TBD |

### sample-private-001

| Field | Detail |
|-------|--------|
| command used | |
| exit code | |
| diagnostics summary | |
| generated artifacts | |
| calculation skipped | |
| output understandable | |

### sample-private-002

| Field | Detail |
|-------|--------|
| command used | |
| exit code | |
| diagnostics summary | |
| generated artifacts | |
| calculation skipped | |
| output understandable | |

### sample-private-003

| Field | Detail |
|-------|--------|
| command used | |
| exit code | |
| diagnostics summary | |
| generated artifacts | |
| calculation skipped | |
| output understandable | |

### sample-private-004

| Field | Detail |
|-------|--------|
| command used | |
| exit code | |
| diagnostics summary | |
| generated artifacts | |
| calculation skipped | |
| output understandable | |

### sample-private-005

| Field | Detail |
|-------|--------|
| command used | |
| exit code | |
| diagnostics summary | |
| generated artifacts | |
| calculation skipped | |
| output understandable | |

---

## extraction_log.json Observations

For each sample, record observations from `extraction_log.json` if generated.

| Field | sample-private-001 | sample-private-002 | sample-private-003 | sample-private-004 | sample-private-005 |
|-------|-------------------|--------------------|-------------------|-------------------|-------------------|
| generated | TBD | TBD | TBD | TBD | TBD |
| failure flag | TBD | TBD | TBD | TBD | TBD |
| failure_reason | TBD | TBD | TBD | TBD | TBD |
| extracted_units_count | TBD | TBD | TBD | TBD | TBD |
| missing_cells_count | TBD | TBD | TBD | TBD | TBD |
| usefulness | TBD | TBD | TBD | TBD | TBD |
| issues found | TBD | TBD | TBD | TBD | TBD |

---

## PII / Privacy Notes

- Private PDFs must not be committed.
- Do not paste raw tenant names, room-level personal names, owner names, addresses, or other sensitive details into committed files.
- Use sample IDs (`sample-private-001` etc.) instead of real file names where possible.
- Only sanitized summaries may be committed to this report.
- `samples/private/` is gitignored and must remain so.
- Verify with `git check-ignore -v samples/private/` before any commit.

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

Fill after evaluation is complete.

- **header alias gaps**: TBD
- **rent format issues**: TBD
- **sub-header patterns**: TBD
- **repeated header patterns**: TBD
- **layout problems**: TBD
- **safe failure adequacy**: TBD
- **diagnostics usability**: TBD

---

## Scope Decision for Future Versions

Fill after evaluation is complete. Select one or more outcomes.

- [ ] no implementation needed — document current support boundaries
- [ ] documentation-only update
- [ ] one narrow implementation issue for v0.5.0
- [ ] keep unsupported
- [ ] defer broader PDF support indefinitely

**Decision rationale**: (fill after evaluation)

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

- [ ] At least 3 samples evaluated if available
- [ ] No private PDFs committed
- [ ] No PII committed
- [ ] `samples/private/` remains gitignored
- [ ] Each sample has a recommended action
- [ ] Dry-run results recorded
- [ ] Extraction diagnostics recorded
- [ ] Future implementation issues are narrow and evidence-based
- [ ] No extraction logic changed
