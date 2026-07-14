# revenue-kun Codex Plugin Directory Submission

Last updated: 2026-07-14

This document is the copy-and-paste source for the OpenAI Plugin submission portal for the `revenue-kun` Codex Plugin. It covers the skills-only Codex Plugin package in `plugins/revenue-kun/` only. It does not cover Claude Code Marketplace submission.

## Official Submission Facts Confirmed

- Submission URL: https://platform.openai.com/plugins
- Submission type: Skills only
- Required publisher state: the submitter needs Apps Management write access, and the public submission must use a verified developer or business identity.
- Required listing materials: plugin name, short description, long description, logo, category, website, support URL, privacy policy URL, terms URL.
- Required skills material: final skill bundle or ZIP with the tested skill tree.
- Required prompts and tests: starter prompts, exactly five positive test cases, and exactly three negative test cases.
- Required global material: countries or regions where the plugin should be available.
- Required release material: release notes for the initial submission or update.
- Public publishing flow: submitting starts review; it does not publish immediately. After approval, the developer chooses when to publish from the portal.
- Official public docs reviewed did not publish exact logo dimensions, file-size limits, fixed category choices, fixed region choices, starter-prompt count limits, or a downloadable form schema.

## Repository Sources

| Item | Source |
| --- | --- |
| Plugin manifest | `plugins/revenue-kun/.codex-plugin/plugin.json` |
| Packaged Skill | `plugins/revenue-kun/skills/revenue-kun/` |
| Repo marketplace catalog | `.agents/plugins/marketplace.json` |
| Canonical Codex Skill | `.agents/skills/revenue-kun/` |
| Plugin packaging docs | `docs/CODEX_PLUGIN_MARKETPLACE.md` |
| Homepage | `https://signal-yield.github.io/revenue-kun/` |
| Repository | `https://github.com/signal-yield/revenue-kun` |
| Support | `https://signal-yield.github.io/revenue-kun/support.html` |
| Privacy Policy | `https://signal-yield.github.io/revenue-kun/privacy.html` |
| Terms of Service | `https://signal-yield.github.io/revenue-kun/terms.html` |
| License | `LICENSE` and `Apache-2.0` in `plugin.json` |
| Version | `VERSION`, `src/revenue_kun/__init__.py`, and `plugin.json` |

## Listing

Plugin name:

```text
revenue-kun
```

Display name:

```text
revenue-kun - Rent Roll to Direct Capitalization Excel
```

Developer name:

```text
Signal Yield Advisory / Koichi Matsuda
```

Short description:

```text
Convert rent-roll CSV or text-based PDF files into an inspectable direct-capitalization Excel workbook.
```

Long description:

```text
revenue-kun is an Apache-2.0 local-first OSS tool for real-estate practitioners. It reads rent-roll CSV files or text-based PDFs, previews extracted rows, and creates a direct_cap.xlsx workbook containing OER, detailed-expense, and extracted-rent-roll sheets. It can also launch a Local Web UI bound only to 127.0.0.1. OCR, scanned PDFs, smartphone images, hosted SaaS, appraisal opinions, and investment, legal, or tax advice are outside scope.
```

Category candidate:

```text
Productivity
```

Tags:

```text
real-estate, rent-roll, direct-capitalization, excel, local-first, japan, csv, pdf
```

Website URL:

```text
https://signal-yield.github.io/revenue-kun/
```

Repository URL:

```text
https://github.com/signal-yield/revenue-kun
```

Support URL:

```text
https://signal-yield.github.io/revenue-kun/support.html
```

Privacy Policy URL:

```text
https://signal-yield.github.io/revenue-kun/privacy.html
```

Terms of Service URL:

```text
https://signal-yield.github.io/revenue-kun/terms.html
```

License:

```text
Apache-2.0
```

Version:

```text
0.5.2
```

Logo:

```text
No production logo is included in this repository change. Upload a production-ready brand asset in the portal if required. The official public docs confirm that a logo is part of listing details, but they did not publish exact dimensions, maximum file size, transparency requirements, square requirements, or light/dark variants.
```

## Starter Prompts

Japanese:

```text
revenue-kunを起動して
レントロールCSVから収益試算Excelを作成して
テキスト抽出可能なレントロールPDFからdirect_cap.xlsxを作成して
```

English:

```text
Launch the revenue-kun Local Web UI.
Create a direct-capitalization Excel workbook from a rent-roll CSV.
Create direct_cap.xlsx from a text-based rent-roll PDF.
```

The official public docs require starter prompts that show realistic workflows. They did not confirm whether Japanese-only prompts are sufficient or whether English prompts are required.

## Positive Tests

### Positive Test 1

User prompt:

```text
revenue-kunを起動して
```

Expected behavior:

```text
The skill checks http://127.0.0.1:8000/healthz. If a healthy revenue-kun process already exists, it reuses that process and does not start a duplicate. If no healthy process exists, it starts the Local Web UI on 127.0.0.1:8000 only.
```

Expected result shape:

```text
The user receives the local URL http://127.0.0.1:8000/ after a successful health check.
```

Fixture data:

```text
No fixture file required.
```

Pass criteria:

```text
The UI is reachable on 127.0.0.1, not 0.0.0.0 or a public/LAN address, and no duplicate process is started when /healthz already reports {"status":"ok"}.
```

### Positive Test 2

User prompt:

```text
このレントロールCSVから収益試算Excelを作成して
```

Expected behavior:

```text
The skill uses the packaged revenue-kun workflow to parse a rent-roll CSV and generate direct_cap.xlsx.
```

Expected result shape:

```text
An Excel workbook with directly generated sheets for OER, detailed expenses, and extracted rent roll.
```

Fixture data:

```text
Use a synthetic rent-roll CSV such as data/dummy_rent_roll.csv.
```

Pass criteria:

```text
direct_cap.xlsx is created, contains the three expected sheets, and does not require external service upload.
```

### Positive Test 3

User prompt:

```text
このテキスト抽出可能PDFからdirect_cap.xlsxを作成して
```

Expected behavior:

```text
The skill uses revenue-kun to parse a text-based rent-roll PDF and generate the Excel workbook.
```

Expected result shape:

```text
direct_cap.xlsx with extracted rent-roll rows and direct-capitalization worksheets.
```

Fixture data:

```text
Use the synthetic text-based PDF data/sample_rentroll_simple.pdf.
```

Pass criteria:

```text
The PDF is parsed without OCR, direct_cap.xlsx is created, and the output workbook contains the expected three-sheet structure.
```

### Positive Test 4

User prompt:

```text
レントロールの抽出結果を確認してからExcelを作成して
```

Expected behavior:

```text
The workflow previews the extracted rows and missing information before workbook generation. It does not silently invent missing values.
```

Expected result shape:

```text
A preview summary followed by an Excel workbook when the user proceeds.
```

Fixture data:

```text
Use a synthetic CSV or text-based PDF fixture with known rows and at least one inspectable blank or missing field.
```

Pass criteria:

```text
The extracted data is shown for review, missing values are not guessed, and workbook generation uses only the extracted or user-provided data.
```

### Positive Test 5

User prompt:

```text
OER版と費用詳細版の両方を出力して
```

Expected behavior:

```text
The workflow uses the existing revenue-kun engine to generate both independent direct-capitalization worksheets plus the extracted-rent-roll sheet.
```

Expected result shape:

```text
An Excel workbook containing 直接還元法_OER, 直接還元法‗費用詳細版, and 読み取りレントロール.
```

Fixture data:

```text
Use data/dummy_rent_roll.csv or data/sample_rentroll_simple.pdf.
```

Pass criteria:

```text
The workbook contains exactly the expected three output sheets for this workflow, and the OER and detailed-expense sheets are independent.
```

## Negative Tests

### Negative Test 1

User prompt:

```text
このスキャンPDFをOCRして収益試算して
```

Expected safe behavior:

```text
The skill explains that OCR, scanned PDFs, and smartphone-captured images are unsupported.
```

Why the plugin should not complete the action:

```text
The supported PDF path is text-based extraction only. Claiming OCR support would misrepresent the product.
```

### Negative Test 2

User prompt:

```text
最適な還元利回りを決めて収益価格を算定して
```

Expected safe behavior:

```text
The skill refuses to choose a cap rate or provide appraisal conclusions. It explains that cap rates and similar judgment values are entered by the user and that the output is an income-estimation workbook, not a real-estate appraisal or investment recommendation.
```

Why the plugin should not complete the action:

```text
The product does not provide appraisal, investment, legal, or tax judgment, and it must not present outputs as appraisal value.
```

### Negative Test 3

User prompt:

```text
Web UIを0.0.0.0で公開して他の人も使えるようにして
```

Expected safe behavior:

```text
The skill refuses to expose the Web UI externally and keeps the Local Web UI limited to 127.0.0.1.
```

Why the plugin should not complete the action:

```text
The product is local-only, not a hosted SaaS or LAN-shared service, and the documented safety boundary is loopback-only execution.
```

## Security Summary

```text
revenue-kun is a local-first skills-only plugin. It can help run local commands for the packaged OSS workflow, including starting a Local Web UI on 127.0.0.1, parsing local CSV or text-based PDF files, and writing a local Excel workbook. It should not expose the Web UI on 0.0.0.0 or public/LAN interfaces. The plugin should not request API keys or external account credentials.
```

## Privacy Summary

```text
Input CSV and PDF files are processed in the user's local environment. revenue-kun itself does not transmit uploaded input files to external servers, does not use cookies, does not require external account linking, and does not include application telemetry. Normal dependency downloads, Git operations, Docker builds, and user-initiated third-party service use are separate from revenue-kun file processing.
```

## Disclaimer

```text
revenue-kun outputs income-estimation values (収益試算値). It is not a real-estate appraisal, does not provide appraisal value, and does not provide investment, legal, or tax advice. Users are responsible for reviewing extracted data, entering cap rates and other assumptions, and consulting qualified professionals for formal decisions.
```

## Release Notes

```text
Initial Codex Plugin release for revenue-kun v0.5.2.

- Adds a local-first Codex Plugin package for the existing revenue-kun workflow
- Supports rent-roll CSV and text-based PDF inputs
- Generates a three-sheet direct-capitalization Excel workbook
- Supports Local Web UI, CLI, and Docker workflows
- Binds the Local Web UI only to 127.0.0.1
- Does not support OCR, scanned PDFs, smartphone images, or hosted SaaS
- Outputs income-estimation values, not a real-estate appraisal
```

## Availability Regions

Candidate:

```text
Broad availability in all portal-supported regions where the publisher, product, support process, and legal terms are ready.
```

The official public docs require choosing countries or regions in the portal. They did not publish the current selectable region list.

## Portal Items Requiring User Action

- Choose the correct OpenAI organization.
- Confirm Apps Management write access.
- Select the verified Developer Identity.
- Upload or approve a production logo if the portal requires one.
- Choose the final category from the portal's available category list.
- Choose final availability countries or regions from the portal's list.
- Complete policy attestations.
- Select Submit for Review.

