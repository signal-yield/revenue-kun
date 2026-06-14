# V041 Minor Hardening Scope

## 1. Purpose

v0.4.1 is a **minor hardening release** following v0.4.0.

The scope is limited to:
- Regression test coverage gaps identified after reviewing the v0.4.0 test suite
- Docs and CLI wording audit

This is **not** a feature release. It does not expand PDF support, add OCR, add
vendor-specific heuristics, or redesign any valuation logic.

---

## 2. v0.4.0 Baseline

v0.4.0 was released as the PDF ingestion hardening milestone (tag `v0.4.0`, commit `48e4551`).

### What v0.4.0 addressed

**Japanese status column detection hardening (Issue #29 / PR #31–#35)**

- Added `ステータス` as a status column alias (PR #31)
- Added `_PERSON_NAME_DENY = {"者名", "テナント名", "入居者"}` to block:
  - `入居者名`, `契約者名`, `テナント名`, `入居者`
- Added `_DATE_HEADER_DENY = {"入居日", "開始日", "満了日", "契約日"}` to block:
  - `入居日`, `入居開始日`, `契約開始日`, `契約満了日`, `契約日`
- `入居` alias retained; screened by deny-sets before alias lookup

**Total / summary row filtering (Issue #30 / PR #37)**

`_SUMMARY_ROW_LABELS` excludes rows whose `room` field, after collapsing all whitespace
and lowercasing, exactly matches any of:

`合計`, `合 計`, `小計`, `総計`, `計`, `TOTAL`, `Total`, `total`, `Subtotal`, `SUBTOTAL`, `Sub total`, `subtotal`

Full-string equality prevents accidental exclusion of room numbers containing these
characters as substrings (e.g. `計画棟101`, `合計算`).

**Verified behavior on `realistic_anonymized_001`**

| Metric | Value |
|--------|-------|
| rows_extracted | 20 |
| occupied units | 17 |
| vacant units | 3 |
| monthly GPI | 2,030,000 yen |
| status column | col 13 (`ステータス`) |

**Synthetic samples regression check (PR #39)**

| Sample ID | Regression? |
|-----------|-------------|
| sample-private-001 | None ✓ |
| sample-private-002 | None ✓ |
| sample-private-003 | None ✓ |

---

## 3. Proposed v0.4.1 Candidates

### A. Summary row filtering — regression test gaps

**Current coverage (v0.4.0):**
- Parametrized unit test (`test_summary_row_label_is_non_data_row`) covers all 12 variants:
  `合 計`, `合計`, `小計`, `総計`, `計`, `TOTAL`, `Total`, `total`, `Subtotal`, `SUBTOTAL`, `Sub total`, `subtotal`
- False-positive protection parametrized test (`test_normal_room_label_is_not_non_data_row`)
  covers: `101`, `201`, `A-101`, `1F-01`, `計画棟101`, `合計算`
- Integration tests: `test_summary_row_excluded_from_extraction`, `test_multiple_summary_variants_excluded`

**Gaps to address in v0.4.1:**

| Gap | Detail |
|-----|--------|
| 全角スペース variant explicit test | `合　計` (全角スペース) — the whitespace-collapse regex `[\s　]+` should handle it, but no parametrized test entry exists for the full-width-space form |
| GPI impact verification | No test explicitly checks that the summary row's rent value is **not** counted in GPI (i.e., extraction + NOI pipeline integration for the summary row case) |

**Implementation guidance:**
- Add `"合　計"` (full-width space) to the `test_summary_row_label_is_non_data_row` parametrize list
- Add a test that builds a PDF with a summary row containing a rent figure, extracts it,
  and asserts that GPI does not include the summary row's value
- Do not add vendor-specific heuristics
- Do not use substring matching — keep full-string equality

### B. Status column detection — regression test gaps

**Current coverage (v0.4.0):**
- `test_resolve_header_key` parametrized: all deny-set headers → `None`, known aliases → correct key
- Integration tests: all major scenarios covered (standalone `入居`, `入居者名`, `入居者`,
  `入居日`, `ステータス` priority)

**Gaps to address in v0.4.1:**

| Gap | Detail |
|-----|--------|
| Status value normalization breadth | `_normalize_status` handles `入居中`, `募集` (→ `空室`), but no parametrized test for less common values in extraction context: `募集中`, `満室`, `賃貸中`, `使用中` |
| Date deny-set integration tests | `開始日`, `満了日`, `契約日` are tested via `test_resolve_header_key` unit test but not via full integration (build_pdf + extract) tests |

**Implementation guidance:**
- Add parametrized value-side tests for `_normalize_status` covering:
  `入居中`, `賃貸中`, `使用中` → `"入居"`; `空室`, `空き室`, `募集中` → `"空室"`; `満室` → raw passthrough (no alias)
- Add an integration test for `契約開始日` and `満了日` headers being blocked from status detection
- Keep tests layout-agnostic (no vendor-specific header assumptions)

### C. Docs / CLI wording audit

**Findings from v0.4.0 code review:**

| Location | Finding | Risk |
|----------|---------|------|
| `src/revenue_kun/cli.py` module docstring (line 1) | `"収益還元クン (revenue-kun) v0.1 CLI ロジック"` — version is stale | Low — internal docstring, not user-facing |
| `build_parser()` `description=` (cli.py) | `"直接還元法による収益試算ツール v0.1（鑑定評価ではありません）"` — version is stale | Low — shown in `--help` output |
| `--version` output | Reads from `__version__` (correct) | None |
| README | v0.4.0 note correctly caveats real-world PDF evaluation as incomplete | None |
| `V040_RELEASE_NOTES_DRAFT.md` | Caveat present: "real-world PDF verified とは表記しない" | None |
| `V040_RELEASE_READINESS.md` | Caveat present: Issue #21 open, real-world evaluation未完了 | None |

**Wording patterns to confirm absent across all committed docs:**

- `real-world PDF verified` / `実務PDF検証済み` — must not appear
- `鑑定評価`, `appraisal`, `valuation opinion` as output claim — must not appear
- `投資助言`, `investment advice` — must not appear
- `法律助言`, `legal advice` — must not appear
- `OCR対応`, `スキャンPDF対応`, `OCR supported` — must not appear as a positive claim

**Proposed fix for v0.4.1:**
- Update the stale `v0.1` version string in `cli.py` docstring and `build_parser` description
  to reflect `v0.4.x` or remove the inline version from the description (version flag already correct)
- Confirm no risky wording added during v0.4.0 PRs

---

## 4. Explicit Non-Goals

The following are **out of scope** for v0.4.1 and must not be implemented:

- OCR / scanned PDF support
- Vendor-specific parser or layout heuristics
- Broad PDF layout redesign
- Valuation logic redesign or new financial calculations
- Committing private PDFs, tenant names, property names, local paths, or any PII
- Claiming "real-world PDF verified" / "実務PDF検証済み"
- Closing Issue #19, #21, or #22
- New CLI features or new output formats

---

## 5. Suggested Implementation Order

1. **Add summary row regression test for 全角スペース variant** (`合　計`)
2. **Add GPI-impact integration test** (summary row rent not counted)
3. **Add `_normalize_status` value-side parametrized tests**
4. **Add integration tests for date-deny headers** (`契約開始日`, `満了日`)
5. **Run full test suite** (`PYTHONPATH=src python -m pytest -q`) — must be 148+ pass, 0 fail
6. **Audit and fix stale version string in `cli.py`** (docstring + `build_parser` description)
7. **Scan committed docs for risky wording** (grep for `verified`, `鑑定`, `OCR`, etc.)
8. **Create PR** — no `Closes` / `Fixes` / `Resolves` keywords

---

## 6. PR Guidance

**Suggested PR title:**
```
test(v041): add regression tests for summary row and status column detection
```
or for the wording-only PR:
```
docs(v041): fix stale version string in CLI help text
```

**PR body must include:**
```
This PR adds regression test coverage for v0.4.0 hardening (summary row
filtering and status column detection).

It does not implement OCR support.
It does not claim real-world PDF verification.
It does not close #19, #21, or #22.

Refs #19. Refs #21. Refs #22.
```

**Do not use:** `Closes`, `Fixes`, `Resolves`

---

## 7. Current Test Suite Baseline (v0.4.0)

| Test file | Count |
|-----------|-------|
| `tests/test_pdf_extract.py` | 93 tests |
| All tests combined | 148 tests |

All 148 tests pass on main at commit `48e4551`.

v0.4.1 must maintain 148+ passing tests with 0 failures after additions.

---

*Created: 2026-06-14*
*Branch: docs/v041-minor-hardening-scope*
*Based on main HEAD: 48e4551*