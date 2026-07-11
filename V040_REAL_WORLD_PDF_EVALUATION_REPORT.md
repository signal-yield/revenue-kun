# Real-world text-based PDF evaluation report

> **Note on scope and history**
> - This evaluation was originally planned for `v0.4.0` as part of Issue #19 / Issue #21.
> - The final re-evaluation documented in this report was actually carried out on the current `main` branch, after the `v0.5.0` (Local Web UI MVP) release.
> - The internal version metadata in the current codebase (`src/revenue_kun/__init__.py`) still reads `0.4.2`. This PR does not change that version metadata.
> - This report is an **evaluation record**. It does not change extraction logic, tests, README, the landing page, or any release/tag.

> 本ツールは不動産鑑定評価ではありません。出力される金額は「収益試算値」であり、鑑定評価による「収益価格」ではありません。欠損項目は補完していません。

---

## 1. Purpose

- Evaluate whether the current extraction and calculation logic can safely process **real-world text-based rent roll PDFs** (not synthetic samples).
- Confirm not only extraction *success*, but also:
  - no erroneous inclusion of non-income figures (deposits, guarantee money, running-cost tables, aggregate rows) into GPI,
  - correct handling of missing/optional fields (no guessed values),
  - safe failure behavior when extraction cannot proceed.
- This evaluation is **not** an evaluation of OCR or scanned-PDF support. All samples in scope are text-based PDFs.

---

## 2. Evaluation scope

- 3 real-world text-based rent roll PDFs (private documents, not committed to this repository).
- All PDF processing was performed only in a gitignored private location (`samples/private/`), never in a tracked path.
- The PDF files themselves, PII, and any property-identifying information were not made public and are not included in this report.
- Each sample was evaluated through **both** the CLI (`python src/main.py`) and the **Local Web UI** (`webui/app.py`, run locally, not via Docker — see §3).
- `direct_cap.xlsx` generation was confirmed for each sample, via both `--excel-output` (CLI) and `/api/generate` (Web UI).
- Optional income (where present in a sample) was evaluated under both the default opt-out configuration and an explicit opt-in configuration.

---

## 3. Environment

The following reflects the actual environment used for this evaluation, factually:

| Item | Detail |
|---|---|
| `main` commit at evaluation time | `292243c` ("docs: update landing page for v0.5.0 (#92)") |
| Python version | 3.11.15 |
| Existing test suite (`pytest -q`) | 375 passed (existing suite, run for environment confirmation; not modified by this evaluation) |
| CLI | Used directly (`python src/main.py`) for `--dry-run`, normal run, and `--excel-output` |
| Local Web UI | Used directly via a local `uvicorn` process bound to `127.0.0.1` (not exposed externally); `/api/preview` and `/api/generate` were exercised |
| pdfplumber | Used both through the CLI/Web UI extraction path and directly (ad hoc scripts) to inspect raw page/table structure for verification purposes |
| Excel generation | Verified via both CLI `--excel-output` and Web UI `/api/generate` |
| Docker | **Not used in this evaluation.** `Dockerfile.web` / containerized Web UI was not exercised here; only a directly-run local Web UI process was tested. This report does not claim Docker verification for these 3 samples. |

---

## 4. Evaluation criteria

Each sample was evaluated against the following criteria:

- text-based vs. scanned
- page count
- pdfplumber detected table count
- rent-roll table selection (which page/table was treated as the rent roll)
- extracted row count
- status recognition (occupied / vacant / other)
- rent (monthly / annual aggregate, compared against the source document's own printed totals where available)
- common fee (monthly / annual aggregate, same comparison)
- optional income (presence, aggregate, and whether it is excluded by default)
- default GPI (opt-out)
- opt-in GPI (explicit optional-income selection)
- aggregate-row exclusion (monthly/annual total rows must not be treated as a unit)
- deposits / guarantee money exclusion (security deposits, key money, etc. must not enter GPI)
- adjacent running-cost table exclusion (a building-wide running-cost breakdown adjacent to the rent roll must not be treated as income)
- missing fields (recorded, not guessed)
- `extraction_log.json` generation
- `missing_info.md` generation
- `direct_cap.xlsx` generation (3-sheet structure)
- `/api/preview` (Local Web UI)
- `/api/generate` (Local Web UI)
- `failure_reason` (if any failure occurred)
- recommended action

---

## 5. Results

Sample identifiers used below (`Sample A`, `Sample B`, `Sample C`) are arbitrary and carry no ordering significance. No property name, address, price, tenant information, filename, company name, or exact monetary figure is included. Where a numeric comparison is relevant, this report states only whether the tool's output **matched** the source document's own printed aggregate or an expected value — not the figures themselves.

| Criterion | Sample A | Sample B | Sample C |
|---|---|---|---|
| Input type | text-based | text-based | text-based |
| Approximate unit scale | 10–20 units | 20+ units | 10–20 units |
| Parking rows present | no | yes (2 rows) | yes (1 row) |
| Optional income column present | yes (one utility-type column) | yes (one utility-type column) | no |
| Extracted row count vs. expected | matched | matched | matched |
| Occupied/vacant status count vs. expected | matched | matched | matched |
| Rent aggregate vs. source document | matched monthly and annual totals printed in the source | matched monthly and annual totals printed in the source | matched monthly and annual totals printed in the source |
| Common fee aggregate vs. source document | matched | matched | matched |
| Optional income aggregate vs. source document | matched | matched | not applicable (no optional income column) |
| Default GPI vs. expected | matched | matched | matched |
| Opt-in GPI vs. expected | matched | matched | not applicable (no optional income column) |
| Non-income columns (deposits / guarantee money / running-cost table) erroneously included | none observed | none observed | none observed |
| CLI `--dry-run` | success (exit 0) | success (exit 0) | success (exit 0) |
| CLI workbook (`--excel-output`) | success, 3 sheets | success, 3 sheets | success, 3 sheets |
| Web UI `/api/preview` | success (HTTP 200), matched CLI output | success (HTTP 200), matched CLI output | success (HTTP 200), matched CLI output |
| Web UI `/api/generate` | success (HTTP 200) | success (HTTP 200) | success (HTTP 200) |
| `failure_reason` | none | none | none |
| Recommended action | support with current logic | support with current logic | support with current logic |

---

## 6. Confirmed behavior

Across all 3 samples, the following was confirmed:

- The expected number of rent-roll rows was extracted in every case.
- Monthly and annual aggregates (rent, common fee, and — where present — optional income) matched the totals printed in the source document itself.
- Optional income columns, where present, were displayed in the extracted rent-roll output.
- Optional income is **not** included in GPI by default (opt-out is the default behavior).
- Only the optional-income category explicitly selected by the user was added to GPI (opt-in).
- The difference between opt-out GPI and opt-in GPI matched the annual total of the selected optional-income category exactly, with no double-counting of rent or common fee.
- Monthly/annual aggregate rows present in the source table were **not** extracted as rent-roll units.
- Deposit-type figures (security deposits, key money / guarantee money, or similar one-off amounts appearing in non-income columns) were **not** included in GPI.
- An adjacent running-cost breakdown table (present in the same physical table region as the rent roll, due to page layout) was **not** treated as income.
- Missing values were recorded (`missing_info.md`) rather than guessed or filled in.
- CLI and Local Web UI results were consistent with each other for every sample (unit counts, aggregates, and GPI figures matched between the two interfaces).
- A 3-sheet `direct_cap.xlsx` workbook (`直接還元法_OER`, `直接還元法‗費用詳細版`, `読み取りレントロール`) was generated successfully for every sample, via both the CLI and the Web UI.

---

## 7. Template limitation

**This is an important limitation and must not be understated.**

All 3 samples show strong structural similarity — matching title-row format, matching merged rent-roll/running-cost table layout, and matching column ordering — consistent with originating from the same vendor family, or a closely related template.

**Usable conclusion**:

> 現行mainで、同一ベンダー系テンプレートとみられるreal-world text-based PDF 3件について、CLIおよびLocal Web UIで抽出・Excel生成を確認した。
>
> On current `main`, 3 real-world text-based PDFs believed to originate from the same vendor-family template were evaluated for extraction and Excel generation via both the CLI and the Local Web UI.

**The following characterizations are explicitly not supported by this evaluation and must not be used**:

- 多様な実務PDFに広く対応済み
- 実務PDF全般で検証済み
- 一般的なレントロールPDFに対応済み
- あらゆるレントロールPDFに対応
- "real-world PDF support completed"
- "production-ready for arbitrary PDFs"

**Issue #21 cannot be closed on the basis of this evaluation alone.** All 3 samples share a closely related template/layout family. PDFs from different vendors, different column layouts, or different table-merging behavior have not been evaluated. Template diversity remains unconfirmed, and Issue #21 should remain open until PDFs from a materially different layout/vendor have been evaluated.

---

## 8. notes mapping observation

All 3 samples exhibited the same structural pattern in `column_map`: the `notes` field's detected column index corresponds, in the raw pdfplumber table, to the remarks column of an **adjacent, unrelated running-cost breakdown table** that pdfplumber merges into the same wide table as the rent roll (due to the two tables being laid out side-by-side on the page).

**Confirmed**:
- The same `notes`-column mapping pattern (pointing at an adjacent table's remarks column) was observed in all 3 samples.
- In all 3 samples, no unrelated string from the adjacent table actually leaked into any extracted unit's output field in this evaluation.
- No impact on any calculated value (GPI, NOI, or the direct-capitalization estimate) was observed in any of the 3 samples.

**Not confirmed**:
- That this behavior is safe for all PDFs with a similar layout.
- That a different layout variation could not cause an unrelated string to leak into an extracted unit's notes field.
- That the current filtering behavior that avoided leakage in these 3 samples is a permanent, intentional guarantee rather than a coincidence of these particular inputs.

**Recommendation**: Treat this as a candidate for a single, narrowly-scoped future issue (hardening the `notes` field so it cannot reference an unrelated table's column under any layout). No code change is made in this PR. This is not an urgent fix, but it has now been observed consistently across 3 samples and is worth tracking.

---

## 9. Recommended actions

1. **These 3 samples**: `support with current logic`. No extraction or calculation logic change is needed for the layout family observed.
2. **Scope of applicability**: Limited to the same template/vendor family observed in these 3 samples. Not generalized to other layouts.
3. **Issue #21**: Keep open. This evaluation does not provide sufficient template diversity to justify closure.
4. **Next evaluation**: Prioritize text-based PDFs from a different vendor and/or a materially different column layout.
5. **`notes` mapping**: Candidate for one narrow future issue (see §8). Not addressed in this PR.
6. **OCR / scanned PDFs**: Remain out of scope, unchanged from prior decisions.

---

## 10. Disclaimer

**日本語**:
本ツールは不動産鑑定評価ではありません。出力される金額は「収益試算値」であり、鑑定評価による「収益価格」ではありません。本ツールは投資判断・法律的判断・税務上の判断を提供しません。正式な価格判断・投資判断・法律的判断・税務上の判断が必要な場合は、不動産鑑定士・弁護士・税理士その他の専門家に確認してください。欠損項目は推測補完していません。

**English**:
This tool is not a real estate appraisal. All output values are revenue estimates (収益試算値) produced by direct capitalization and do not constitute appraised values (鑑定評価額). This tool does not provide investment advice, legal advice, or tax advice. For formal valuation, investment decisions, legal judgment, or tax determinations, consult a licensed real estate appraiser, attorney, or tax professional. Missing values are not filled in by inference or guesswork.
