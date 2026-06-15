# Repo Closeout After v0.4.1

## 1. Current Repo State

| Item | Value |
|------|-------|
| Latest release | v0.4.1 — PDF ingestion regression hardening |
| Latest tag | `v0.4.1` |
| Latest main commit | `625d655` docs: summarize v0.4.x PDF ingestion evaluation |
| Test result | **161 passed, 0 failed** |
| Git status | On branch `main`, up to date with `origin/main`, nothing to commit, working tree clean |

> **重要**: 本ツールは不動産鑑定評価ではありません。出力される金額は「収益試算値」であり、
> 鑑定評価による「収益価格」ではありません。欠損項目は補完しません。

---

## 2. Completed Milestones

| Milestone | Detail |
|-----------|--------|
| v0.4.0 released | PDF ingestion hardening: Japanese status column detection and summary row filtering. |
| v0.4.1 released | PDF ingestion regression hardening: 13 new regression tests, stale CLI wording cleanup. 161 passed, 0 failed. |
| V040_V041_EVALUATION_SUMMARY.md merged | Summarized v0.4.0 / v0.4.1 PDF ingestion evaluation findings. Merged in PR #47. |
| Issue #22 completed | Findings summary written and merged. Issue #22 set to completed. |
| Next product scope issue created | Issue #48 — Plan next product scope after v0.4.x PDF ingestion hardening. |

---

## 3. Remaining Open Issues

| Issue | State | Reason remaining open |
|-------|-------|----------------------|
| [#19](https://github.com/signal-yield/revenue-kun/issues/19) | open | Additional qualifying real-world text-based PDF evaluation not yet complete. Depends on #21. |
| [#21](https://github.com/signal-yield/revenue-kun/issues/21) | open | No qualifying real-world text-based rent roll PDF available in `samples/private/`. Waiting state. |
| [#48](https://github.com/signal-yield/revenue-kun/issues/48) | open | Next product scope planning. Active. |

#19 and #21 remain open until qualifying real-world text-based rent roll PDFs become available.
#48 is the active next-phase planning issue.

---

## 4. Stable Stopping Point

- **v0.4.1 is the current stable PDF ingestion hardening point.**
- The parser covers Japanese status column detection, summary row filtering (12 label variants including full-width-space `合　計`), false-positive guard for `計` in non-summary fields, and GPI impact regression.
- Additional PDF parser expansion should pause until qualifying real-world text-based rent roll PDFs are available (Issue #21).
- No vendor-specific heuristics or broad layout redesign is planned.

---

## 5. Guardrails

| Guardrail | Status |
|-----------|--------|
| Real-world PDF verified | Not claimed. Must not be added. |
| 実務PDF検証済み | Not claimed. Must not be added. |
| OCR / scanned PDF support | Not implemented. Out of scope. |
| Investment advice | Not provided. Output is a revenue estimate only. |
| Legal advice | Not provided. |
| Appraisal / valuation opinion | Not provided. Output is 収益試算値, not 鑑定評価額. |
| Replacement of professional judgment | Not intended. Verify with qualified professionals before any real-world decision. |
| Private PDF / PII / local path disclosure | Not included. No private PDFs, tenant names, property names, or local paths are committed. |

---

## 6. Recommended Next Phase

- **Shift from parser hardening to product-scope planning** (Issue #48).
- Evaluate the following as v0.5.0 scope candidates:
  - LP (landing page) design and content
  - GA4 / Search Console integration and analytics setup
  - CTA (call-to-action) strategy
  - PR TIMES or equivalent press distribution
  - note / LinkedIn / X routing and content strategy
  - v0.5.0 feature scope definition
- **Keep PDF parser work gated** by availability of qualifying real-world text-based rent roll PDFs (Issue #21).
- Resume PDF evaluation work when qualifying samples become available.

---

*Created: 2026-06-15*
*Based on: v0.4.1 (tag/release), main HEAD 625d655*
*Key PRs: #43 (planning), #45 (implementation), #46 (release readiness), #47 (evaluation summary)*
