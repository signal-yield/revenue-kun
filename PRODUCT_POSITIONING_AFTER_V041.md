# Product Positioning After v0.4.1

## 1. Purpose

This document defines the product positioning for `revenue-kun` after the v0.4.1 PDF ingestion hardening release.

The purpose is to prevent the next phase from drifting into premature parser expansion, SaaS claims, appraisal claims, investment advice claims, or completed Claude Skill claims.

This positioning should be used as the source of truth for the next public-facing artifacts:

- demo scenario
- sample output report
- GitHub Pages LP v0.1
- note / LinkedIn / Qiita drafts
- consultation and joint validation CTA copy

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

The tool should be positioned as a review-assistance and validation-oriented workflow aid for practitioners, not as a replacement for professional judgment.

## 4. Secondary target users

Secondary target users are teams and individuals interested in PropTech, real estate AI, and workflow automation.

Secondary audience:

- PropTech operators
- real estate AI builders
- workflow automation teams
- developers evaluating structured rent roll processing
- business owners exploring AI-assisted real estate operations

For this audience, the emphasis should be on transparent OSS validation, reproducibility, logs, and clearly stated support boundaries.

## 5. Out-of-scope audiences

The project should not be aimed at general real estate investors or individuals seeking a buy/sell decision.

Out-of-scope audiences:

- general real estate investors
- individual investors expecting investment recommendations
- users asking whether a specific property should be bought or sold
- users expecting formal appraisal output
- users expecting legal, tax, or investment advice
- users expecting fully automated PDF understanding across arbitrary documents

This boundary is important because broad investor-facing messaging can make the project look like investment advice or appraisal work.

## 6. Product definition

`revenue-kun` is an OSS validation project for real estate income estimation and rent roll review assistance, designed with future Claude Skill packaging in mind.

It helps review the pre-estimation workflow around rent roll reading, GPI calculation, NOI calculation, and direct-capitalization-based estimated value calculation under explicit assumptions.

The product definition is:

> `revenue-kun` is a research and validation CLI for assisting real estate income estimation and rent roll review. It is intended to make assumptions, parsed values, excluded rows, warnings, and calculation outputs easier to inspect before a practitioner makes their own judgment.

It is not:

- a completed SaaS
- a completed Claude Skill
- a formal appraisal tool
- an investment advice tool
- a legal advice tool
- a tax advice tool
- a universal PDF extraction engine
- an OCR or scanned-PDF solution

## 7. Claude Skill positioning

Claude Skill packaging is a future-facing product direction, not a completed release claim.

The correct positioning is:

- designed with future Claude Skill packaging in mind
- suitable for exploration as a Claude Skill workflow
- not yet released as a completed Claude Skill version
- currently available as GitHub OSS
- next public-facing materials may describe the intended Claude Skill direction if clearly framed as future packaging or validation direction

Public copy should avoid wording that implies a completed Claude Skill release.

Acceptable wording:

- "Claude Skill化を想定"
- "future Claude Skill packaging in mind"
- "Claude Skill workflow candidate"
- "currently published as GitHub OSS"

Unacceptable wording:

- "Claude Skill版リリース済み"
- "completed Claude Skill"
- "available as a production Claude Skill"

## 8. What may be claimed publicly

The following claims are acceptable for LP, README-adjacent copy, note, LinkedIn, Qiita, and consultation materials:

- GitHub OSSとして公開済み
- v0.4.1 released
- PDF ingestion regression hardening済み
- tests: 161 passed, 0 failed
- research and validation CLI
- real estate income estimation assistance
- rent roll review assistance
- direct-capitalization-based calculation under explicit assumptions
- summary row filtering is covered by regression tests
- Japanese status-column false-positive handling has been hardened
- assumptions, warnings, and calculation outputs are intended to be inspectable
- joint validation / consultation is welcome
- Claude Skill packaging is a future-oriented direction

These claims should remain narrow and evidence-based.

## 9. What must not be claimed

The following claims must not be used in public copy, LP, release notes, PR material, note, LinkedIn, Qiita, or consultation copy:

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

## 10. Why the CTA should be joint validation / consultation

The CTA should be joint validation / consultation rather than immediate purchase or SaaS signup.

Reasons:

1. The project is currently an OSS validation project, not a completed SaaS.
2. Real rent roll PDF formats vary, and support boundaries must be validated carefully.
3. The current value is strongest for expert review, workflow discussion, and controlled validation.
4. A consultation CTA avoids overstating readiness while still creating a business development path.
5. Joint validation can collect qualifying text-based rent roll examples without claiming broad real-world coverage.
6. Practitioner feedback is needed before deciding whether the next phase should be Claude Skill packaging, v0.5.0 product work, or both.

Recommended CTA direction:

- "共同検証について相談する"
- "収益試算・レントロール確認ワークフローについて相談する"
- "GitHub OSSを確認する"
- "デモ出力を見る"

Avoid CTA language that suggests automated investment decisions or finished commercial deployment.

## 11. How this positioning informs the LP

The GitHub Pages LP v0.1 should be a credibility-building page, not a hard-selling SaaS landing page.

LP structure should follow this positioning:

1. First view: explain the review-assistance problem in rent roll and income estimation workflows.
2. What it is: GitHub OSS validation project for income estimation and rent roll review assistance.
3. Problem: PDF rent roll preprocessing errors can affect GPI, NOI, and estimated value calculations.
4. What it can do: show narrow, test-backed capabilities from v0.4.1.
5. What v0.4.1 hardened: status-column handling, summary row filtering, stale wording cleanup, regression tests.
6. Demo output: show input, output, assumptions, warnings, and excluded rows.
7. What it cannot do: explicitly state support boundaries.
8. Intended users: practitioners and PropTech / real estate AI builders.
9. Links: GitHub, note, Qiita, LinkedIn.
10. CTA: joint validation / consultation.
11. Disclaimer: not appraisal, investment advice, legal advice, or judgment replacement.

The LP should make the project feel credible because it is honest about boundaries.

## 12. Next artifacts to create

The next artifacts should be created in this order:

1. `DEMO_SCENARIO_V041.md`
2. `sample_output_report.md`
3. `sample_assumptions_and_warnings.md`
4. GitHub Pages LP v0.1 draft
5. CTA wiring and minimum public links

Do not return to parser expansion until qualifying real-world text-based rent roll PDFs are available and the scope is narrowed by evidence.
