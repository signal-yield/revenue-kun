# V040 Private Sample Inventory Template

> **Note**: This file is a template only.
> Do not fill this file with real PII.
> Do not commit private PDF paths if they reveal sensitive information.
> Prefer sanitized sample IDs in committed reports.
> Keep actual PDFs under `samples/private/` or another gitignored location.

---

## Purpose

Track the existence and evaluation status of private PDF samples for the v0.4.0 evaluation.
This file documents sample metadata without committing private PDFs or PII.

---

## Sample Inventory

| Sample ID | Local private path | Original filename stored privately | Text-based or scanned | PII risk level | Evaluation status | Notes | Recommended action |
|-----------|-------------------|------------------------------------|----------------------|---------------|-------------------|-------|--------------------|
| sample-private-001 | `samples/private/` | (do not commit) | TBD | TBD | not started | | TBD |
| sample-private-002 | `samples/private/` | (do not commit) | TBD | TBD | not started | | TBD |
| sample-private-003 | `samples/private/` | (do not commit) | TBD | TBD | not started | | TBD |
| sample-private-004 | `samples/private/` | (do not commit) | TBD | TBD | not started | | TBD |
| sample-private-005 | `samples/private/` | (do not commit) | TBD | TBD | not started | | TBD |

---

## PII Risk Levels

| Level | Meaning |
|-------|---------|
| `low` | No tenant names, owner names, addresses, or room-level personal data visible |
| `medium` | Partial personal data present (e.g. room numbers only) |
| `high` | Full tenant names, addresses, or other sensitive PII present |

---

## Evaluation Status Values

| Status | Meaning |
|--------|---------|
| `not started` | Sample has not been evaluated yet |
| `in progress` | Evaluation is underway |
| `complete` | Evaluation is complete and recommended action assigned |
| `skipped` | Sample was skipped (e.g. scanned PDF, inaccessible file) |

---

## Recommended Action Values

| Action | Meaning |
|--------|---------|
| `support_with_current_logic` | Works with current v0.3.0 extraction logic |
| `document_as_unsupported` | Does not work; pattern is not worth supporting |
| `future_issue_candidate` | Fails but may justify a narrow future issue |
| `reject_as_out_of_scope` | Scanned, OCR-required, or otherwise definitively out of scope |

---

## Usage Notes

1. Copy this template to a local working file if needed.
2. Do not commit real private file paths or PII.
3. Transfer sanitized findings to `V040_REAL_WORLD_PDF_EVALUATION_REPORT.md` for the committed evaluation record.
4. Keep all actual PDFs under `samples/private/` (gitignored).
