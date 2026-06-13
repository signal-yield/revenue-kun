# V040 Status After PR #24

## v0.4.0 Current State

As of 2026-06-13, the v0.4.0 evaluation cycle is in progress.

- v0.4.0 theme: additional real-world text-based rent roll PDF evaluation
- v0.4.0 approach: evaluation-first. No implementation is assumed.
- PR #24 (`eval(v040): record synthetic PDF evaluation results for issue-21`) has been merged.
- Issue #21 remains open. Real-world PDF evaluation has not yet been completed.

---

## Issue Status

| Issue | Title | State | Notes |
|-------|-------|-------|-------|
| #19 | Plan v0.4.0 additional real-world text-based PDF evaluation | open | Parent planning issue |
| #20 | Create v0.4.0 real-world PDF evaluation report template | closed | PR #23 merged (`761cb94`) |
| #21 | Evaluate additional private rent roll PDF samples for v0.4.0 | open | Interim only; real-world samples pending |
| #22 | Summarize v0.4.0 PDF evaluation findings and decide next scope | open | Blocked on #21 completion |

---

## PR #24 Summary

| Item | Detail |
|------|--------|
| PR | #24 |
| Title | `eval(v040): record synthetic PDF evaluation results for issue-21` |
| Branch | `eval/issue-21-private-pdf-samples` |
| Commit | `b576c1b` |
| Merge commit | `26e2a2b` |
| Merged | 2026-06-13 |
| Changed file | `V040_REAL_WORLD_PDF_EVALUATION_REPORT.md` |
| Type | documentation-only, evaluation record |

### What PR #24 recorded

- 3 private synthetic PDF samples were evaluated using the v0.3.0 CLI diagnostics and `--dry-run` mode.
- All 3 samples were text-based PDFs (v0.2.0 reportlab-generated synthetic samples).
- All 3 samples were supported by the current v0.3.0 PDF extraction logic without changes.
- `--dry-run` exited 0 for all 3 samples.
- Safe failures: 0.
- Future issue candidates: none identified from these synthetic samples.

### What PR #24 did not record

The 3 samples evaluated were the existing v0.2.0 synthetic PDFs, not additional real-world rent roll PDFs.
Real-world PDF evaluation requires actual real-world samples to be placed under `samples/private/`.

---

## Current Decisions

### PDF extraction scope

- PDF extraction scope is not expanded in v0.4.0.
- The v0.2.0 limited text-based PDF ingestion scope remains unchanged.

### Out of scope — confirmed for v0.4.0

- OCR
- scanned PDF support
- multi-page table stitching
- complex merged cell support
- vendor-specific heuristics
- PII masking implementation
- broad real-world PDF support claims
- formal valuation
- investment advice
- legal advice

### Issue #21 continuation

- Issue #21 remains open.
- PR #24 was an interim evaluation record only.
- Issue #21 will be resumed when additional real-world text-based rent roll PDFs become available.

---

## Next Trigger

Issue #21 evaluation resumes when:

- 3 to 5 additional real-world text-based rent roll PDFs are available under `samples/private/` or another gitignored location.
- All samples must be text-based (not scanned).
- No private PDFs or PII may be committed.
- Sample IDs (`sample-private-001` etc.) must be used in committed reports.

---

## Next Evaluation Steps (when triggered)

1. Place real-world samples under `samples/private/` (gitignored, not committed).
2. Run `--dry-run` for each sample.
3. Record diagnostics summary, exit code, and recognized fields.
4. Record `extraction_log.json` observations if generated.
5. Assign a recommended action per sample:
   - `support_with_current_logic`
   - `document_as_unsupported`
   - `future_issue_candidate`
   - `reject_as_out_of_scope`
6. Update `V040_REAL_WORLD_PDF_EVALUATION_REPORT.md` with sanitized findings only.
7. Proceed to Issue #22 (summarize findings and decide next scope) once evaluation is complete.

---

## Privacy / Safety Reminders

- Do not commit private PDFs.
- Do not commit PII (tenant names, owner names, addresses, room-level personal data).
- Use sample IDs in all committed reports.
- Verify `samples/private/` remains gitignored before every commit.
- `samples/private/` is confirmed gitignored at `.gitignore:19`.
