# revenue-kun v0.3.0 Release Completion Note

## Summary

- `revenue-kun v0.3.0` release completed
- v0.3.0 is a CLI UX and diagnostics release
- PDF extraction scope was not expanded from v0.2.0

---

## Release Metadata

| Item | Value |
|------|-------|
| Release status | Published |
| Release URL | https://github.com/signal-yield/revenue-kun/releases/tag/v0.3.0 |
| tag | `v0.3.0` |
| target branch | `main` |
| version bump commit | `a1f451d` |
| CHANGELOG commit | `a52a4c8` |
| pytest | 107/107 PASSED |

---

## Completed Scope

- Issue #12: v0.3.0 planning
- Issue #13 / PR #16: extraction diagnostics summary
- Issue #14 / PR #17: `--dry-run` mode
- Issue #15 / PR #18: README usage examples and CLI help test
- CHANGELOG updated for v0.3.0
- package version bumped to `0.3.0`
- tag pushed
- GitHub Release published

---

## v0.3.0 Features

### CLI extraction diagnostics summary

- input type display: CSV / PDF
- recognized canonical fields for PDF inputs
- extracted unit count
- safe failure state display
- existing `failure_reason` display

### `--dry-run` mode

- validates input extraction and diagnostics without running calculations or generating output artifacts

### README usage examples

- CSV normal execution
- CSV dry-run
- text-based PDF normal execution
- text-based PDF dry-run
- diagnostics summary
- safe failure handling
- `extraction_log.json` guide

---

## Not Changed / Out of Scope

- no PDF extraction scope expansion
- no OCR
- no scanned PDF support
- no multi-page table stitching
- no complex merged cell support
- no vendor-specific heuristics
- no PII masking
- no formal valuation
- no investment advice
- no legal advice

---

## Next Candidates

- v0.4.0: additional real-world text-based rent roll PDF evaluation
- v0.4.0 should start as evaluation, not implementation
- possible future v0.5.0: implement only one validated real-world PDF pattern if justified
