# Product Positioning After v0.4.1

## 1. Purpose

This document defines the product positioning for `revenue-kun` after the v0.4.1 PDF ingestion hardening release.

The key correction after review is that the user-facing deliverable is not a Markdown report. The intended product flow is:

```text
rent roll PDF input
↓
Excel workbook output
↓
user reviews and edits assumptions directly in Excel
↓
Direct Capitalization Method calculation is updated through Excel formulas
```

This document should guide the next phase: Excel-output specification, workbook generation, and GitHub Pages LP v0.1 preparation.

## 2. Current state

`revenue-kun` is currently published as GitHub OSS.

v0.4.1 is the current stable PDF ingestion hardening point. It should be treated as a regression hardening milestone, not as proof of broad real-world PDF support.

Current state summary:

- v0.4.1 released
- tests: 161 passed, 0 failed
- PDF ingestion regression hardening completed for known text-based cases
- Japanese status-column false-positive handling improved
- summary row filtering improved
- stale CLI wording cleaned up
- repository closeout completed after v0.4.1
- additional parser expansion paused until qualifying real-world text-based rent roll PDFs are available

Issue state:

- #19 remains open for additional real-world text-based PDF evaluation
- #21 remains open for additional private rent roll PDF sample evaluation
- Issue #22 is completed
- #48 remains open for next product scope planning

## 3. Primary target users

Primary target users are real estate professionals who already understand rent rolls, income estimation, due diligence, and review workflows.

Primary audience:

- real estate asset managers
- property managers
- corporate real estate teams
- appraisal and due diligence professionals
- investment management professionals who review rent roll and income assumptions

The tool should be positioned as an Excel-output review-assistance workflow, not as a replacement for professional judgment.

## 4. Secondary target users

Secondary target users are teams and individuals interested in PropTech, real estate AI, and workflow automation.

Secondary audience:

- PropTech operators
- real estate AI builders
- workflow automation teams
- developers evaluating structured rent roll processing
- business owners exploring AI-assisted real estate operations

For this audience, the emphasis should be on transparent OSS validation, reproducibility, Excel formula traceability, and clearly stated support boundaries.

## 5. Product definition

`revenue-kun` is an OSS validation project for assisting real estate income estimation and rent roll review, designed with future Claude Skill packaging in mind.

The intended user-facing output is an Excel workbook based on a Direct Capitalization Method template.

The current product definition is:

> `revenue-kun` reads a rent roll PDF and outputs an Excel workbook that contains both a Direct Capitalization Method calculation sheet and a parsed rent roll sheet. The workbook allows the user to review the parsed rent roll, edit vacant-unit assumptions or revenue items directly in Excel, and see the Direct Capitalization Method calculation update through formulas.

It is not:

- a completed SaaS
- a completed Claude Skill
- a formal appraisal tool
- an investment advice tool
- a legal advice tool
- a tax advice tool
- a universal PDF extraction engine
- an OCR or scanned-PDF solution
- a replacement for practitioner review

## 6. Confirmed Excel output structure

The output workbook should contain the following sheets:

1. `直接還元法_OER`
2. `直接還元法‗費用詳細版`
3. `読み取りレントロール`

The first implementation focus should be the OER version. The detailed expense version may remain available for user-side refinement.

## 7. Confirmed auto-filled cells in OER sheet

Only the following OER input cells should be auto-filled from the parsed rent roll at this stage:

| Sheet | Cell | Meaning |
|---|---:|---|
| `直接還元法_OER` | `E2` | 年額貸室賃料収入 |
| `直接還元法_OER` | `E3` | 年額共益費収入 |
| `直接還元法_OER` | `E5` | 年額水道光熱費収入 |
| `直接還元法_OER` | `E6` | 年額駐車場収入 |
| `直接還元法_OER` | `E7` | その他収入 |

Other inputs such as vacancy loss rates, bad debt loss, OER, capital expenditure, cap rate, and detailed expense assumptions should be edited by the user directly in the output workbook.

This is intentional. It keeps the automated extraction narrow while preserving user control over valuation assumptions.

## 8. Confirmed parsed rent roll sheet behavior

The `読み取りレントロール` sheet should contain the parsed rent roll in an editable format.

Confirmed requirements:

- Do not split columns into `PDF読み取り` and `ユーザー入力` variants.
- The parsed cells themselves should be editable by the user.
- Vacant rows should show the note `ユーザーが賃料等を入力可能` in the remarks column.
- The sheet should include a `月額合計` row at the bottom.
- The sheet should include a `年額合計` row below the monthly total row.
- The annual total row should calculate each revenue category as monthly total multiplied by 12.
- The annual total row should have borders.
- Amount cells should use comma-separated number formatting.
- No unnecessary borders should be drawn below the annual total row.

The rent roll sheet should calculate totals by revenue category, not by unit-level total columns.

Revenue categories currently expected:

- 賃料
- 共益費
- 水道光熱費
- 駐車場
- その他収入

## 9. Formula flow

The OER sheet should reference the annual total row in `読み取りレントロール`.

The OER sheet should not multiply these linked cells by 12, because annualization is already done in the `読み取りレントロール` sheet.

Expected formula concept:

```text
読み取りレントロール monthly totals
↓
読み取りレントロール annual totals = monthly totals × 12
↓
直接還元法_OER E2/E3/E5/E6/E7 reference annual totals directly
↓
existing Direct Capitalization Method formulas calculate income, NOI, net income, and estimated value
```

Excel formulas should be preserved and made inspectable by the user.

## 10. Claude Skill positioning

Claude Skill packaging is a future-facing product direction, not a completed release claim.

The correct positioning is:

- designed with future Claude Skill packaging in mind
- suitable for exploration as a Claude Skill workflow
- not yet released as a completed Claude Skill version
- currently available as GitHub OSS
- next public-facing materials may describe the intended Claude Skill direction if clearly framed as future packaging or validation direction

Acceptable wording:

- `Claude Skill化を想定`
- `future Claude Skill packaging in mind`
- `Claude Skill workflow candidate`
- `currently published as GitHub OSS`

Unacceptable wording:

- `Claude Skill版リリース済み`
- `completed Claude Skill`
- `available as a production Claude Skill`

## 11. What may be claimed publicly

The following claims are acceptable for LP, README-adjacent copy, note, LinkedIn, Qiita, and consultation materials:

- GitHub OSSとして公開済み
- v0.4.1 released
- PDF ingestion regression hardening済み
- tests: 161 passed, 0 failed
- research and validation CLI
- rent roll PDF input is intended to produce an Excel workbook output
- output workbook includes Direct Capitalization Method sheets and a parsed rent roll sheet
- the parsed rent roll sheet is editable by the user
- vacant-unit assumptions can be edited in Excel
- OER version auto-fills annual rent, common area fees, utilities income, parking income, and other income
- Excel formulas remain inspectable
- joint validation / consultation is welcome
- Claude Skill packaging is a future-oriented direction

These claims should remain narrow and evidence-based.

## 12. What must not be claimed

The following claims must not be used as positive public claims:

- 実務PDF検証済み
- real-world PDF verified
- OCR対応
- scanned PDF対応
- fully automated rent roll understanding
- arbitrary PDF support
- production SaaS
- commercial SaaS now available
- investment recommendation support
- formal appraisal support
- legal advice support
- tax advice support
- replacement for professional judgment
- completed Claude Skill release

Do not imply that v0.4.1 proves broad field readiness. It is a stable hardening point with clearly bounded regression coverage.

## 13. Why the CTA should be joint validation / consultation

The CTA should be joint validation / consultation rather than immediate purchase or SaaS signup.

Reasons:

1. The project is currently an OSS validation project, not a completed SaaS.
2. Real rent roll PDF formats vary, and support boundaries must be validated carefully.
3. The current value is strongest when paired with practitioner review in Excel.
4. A consultation CTA avoids overstating readiness while still creating a business development path.
5. Joint validation can collect qualifying text-based rent roll examples without claiming broad real-world coverage.
6. Practitioner feedback is needed before deciding whether the next phase should be Claude Skill packaging, v0.5.0 product work, or both.

Recommended CTA direction:

- `共同検証について相談する`
- `レントロールPDFから直接還元法Excelへの出力について相談する`
- `GitHub OSSを確認する`
- `Excel出力サンプルを見る`

Avoid CTA language that suggests automated investment decisions or finished commercial deployment.

## 14. How this positioning informs the LP

The GitHub Pages LP v0.1 should be a credibility-building page, not a hard-selling SaaS landing page.

LP structure should follow this positioning:

1. First view: explain rent roll PDF input and Direct Capitalization Method Excel output.
2. What it is: GitHub OSS validation project for rent roll review and income estimation assistance.
3. Problem: rent roll preprocessing errors can affect annual income, NOI, and estimated value calculations.
4. What it outputs: editable Excel workbook with OER sheet, detailed expense sheet, and parsed rent roll sheet.
5. What v0.4.1 hardened: status-column handling, summary row filtering, stale wording cleanup, regression tests.
6. Excel output sample: show the actual workbook structure.
7. What it cannot do: explicitly state support boundaries.
8. Intended users: practitioners and PropTech / real estate AI builders.
9. Links: GitHub, note, Qiita, LinkedIn.
10. CTA: joint validation / consultation.
11. Disclaimer: not appraisal, investment advice, legal advice, tax advice, or judgment replacement.

The LP should make the project feel credible because it shows the actual Excel output and is honest about boundaries.

## 15. Next artifacts to create

The next artifacts should be created in this order:

1. Lock the Excel output sample workbook as the reference artifact.
2. Create an Excel output specification document.
3. Update implementation tasks so the CLI writes the confirmed workbook format.
4. Create GitHub Pages LP v0.1 using the Excel output sample as the main visual proof.
5. Add CTA wiring and minimum public links.

Do not return to parser expansion until qualifying real-world text-based rent roll PDFs are available and the scope is narrowed by evidence.
