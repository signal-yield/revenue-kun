# revenue-kun Codex Plugin / Marketplace package

## Status

This repository packages the existing Codex Agent Skill as a repo-local Codex Plugin using the OpenAI-published structure available at implementation time:

- Plugin manifest: `plugins/revenue-kun/.codex-plugin/plugin.json`
- Marketplace catalog: `.agents/plugins/marketplace.json`
- Canonical Skill: `.agents/skills/revenue-kun/`
- Generated distributable Skill copy: `plugins/revenue-kun/skills/revenue-kun/`

The generated copy must remain byte-for-byte synchronized with the canonical Skill:

```bash
python scripts/sync_codex_plugin_skill.py
python scripts/sync_codex_plugin_skill.py --check
```

## Installation

### Repository-local Marketplace

Clone the repository, keep the checked-out repository as the Codex workspace, and use the repo-local marketplace catalog at `.agents/plugins/marketplace.json`. The catalog points to `./plugins/revenue-kun`.

OpenAI's current Codex plugin CLI accepts a GitHub repository shorthand or a
local marketplace root:

```bash
codex plugin marketplace add signal-yield/revenue-kun
codex plugin add revenue-kun@signal-yield
```

For a local checkout, replace the GitHub shorthand with the repository root.
After installation, start a new Codex session so the bundled Skill is detected.

### Home-local Marketplace

Copy the plugin directory to `~/plugins/revenue-kun` and merge the catalog entry into `~/.agents/plugins/marketplace.json`:

```json
{
  "name": "revenue-kun",
  "source": {
    "source": "local",
    "path": "./plugins/revenue-kun"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Productivity"
}
```

In Codex CLI, open `/plugins` to install or uninstall the plugin and press Space
to disable or enable an installed plugin. The ChatGPT desktop plugin details
page also exposes **Uninstall plugin** when the installation policy permits it.
Remove the configured marketplace source with:

```bash
codex plugin marketplace remove signal-yield
```

## Marketplace copy — 日本語

### Plugin名

revenue-kun

### 1行説明

レントロールPDF／CSVから、直接還元法による収益試算Excelを生成するローカル実行型OSS。

### 説明（100〜200文字）

revenue-kunは、CSVまたはテキスト抽出可能なレントロールPDFを読み取り、抽出内容を確認したうえで、OER版・費用詳細版・読み取りレントロールを含む`direct_cap.xlsx`を生成するApache-2.0のローカル実行型OSSです。

### 詳細説明

revenue-kunは、不動産実務で利用するレントロールをCSVまたはテキスト抽出可能PDFから読み取り、直接還元法による収益試算Excelを生成します。Local Web UI、CLI、Dockerに対応し、処理は利用者のローカル環境で実行されます。出力される金額は収益試算値であり、不動産鑑定評価、収益価格、投資判断、法律判断、税務判断を提供するものではありません。

### 主な機能

- CSVまたはテキスト抽出可能PDFの読み取り
- 抽出結果のプレビュー
- OER版と費用詳細版の同時出力
- 読み取りレントロールシートの出力
- 付帯収入のGPIへの反映
- `127.0.0.1`限定のLocal Web UI起動
- CLI／Docker対応

### 使用例

- `revenue-kunを起動して`
- `Web UIを開いて`
- `レントロールPDFから収益試算Excelを作成して`
- `CSVからdirect_cap.xlsxを生成して`

### 対応入力

- CSV
- テキスト抽出可能なPDF

### 非対応入力

- OCR
- スキャンPDF
- スマートフォン撮影画像
- hosted SaaS経由の入力

### サポート窓口

Support page: https://signal-yield.github.io/revenue-kun/support.html
GitHub Issues: https://github.com/signal-yield/revenue-kun/issues
Privacy Policy: https://signal-yield.github.io/revenue-kun/privacy.html
Terms of Service: https://signal-yield.github.io/revenue-kun/terms.html

### category／tags候補

- Category: Productivity
- Tags: real-estate, rent-roll, direct-capitalization, excel, local-first, japan

## Marketplace copy — English

### Plugin name

revenue-kun

### One-line description

A local-first OSS tool that converts rent-roll CSV or text-based PDF files into a direct-capitalization Excel workbook.

### Short description

revenue-kun reads rent-roll CSV files or text-based PDFs, previews the extracted data, and generates `direct_cap.xlsx` with OER, detailed-expense, and extracted-rent-roll sheets. It is an Apache-2.0 local-first OSS tool.

### Detailed description

revenue-kun is a local-first open-source tool for real-estate practitioners. It reads rent-roll CSV files or text-based PDFs and generates an inspectable direct-capitalization Excel workbook. It supports a Local Web UI, CLI, and Docker. All processing runs in the user's local environment. The output is an income-estimation worksheet, not a real-estate appraisal, appraisal value, investment recommendation, legal opinion, or tax opinion.

### Key features

- Read CSV or text-based PDF rent rolls
- Preview extracted rows and missing information
- Generate OER and detailed-expense sheets together
- Generate an extracted-rent-roll sheet
- Include ancillary income in GPI
- Launch a Local Web UI bound to `127.0.0.1`
- Use through CLI or Docker

### Example prompts

- `Start revenue-kun`
- `Open the Local Web UI`
- `Create an income-estimation Excel workbook from this rent-roll PDF`
- `Generate direct_cap.xlsx from this CSV`

### Supported inputs

- CSV
- Text-based PDF

### Unsupported inputs

- OCR
- Scanned PDF
- Smartphone-captured images
- Hosted SaaS uploads

### Support

Support page: https://signal-yield.github.io/revenue-kun/support.html
GitHub Issues: https://github.com/signal-yield/revenue-kun/issues
Privacy Policy: https://signal-yield.github.io/revenue-kun/privacy.html
Terms of Service: https://signal-yield.github.io/revenue-kun/terms.html

### Suggested category and tags

- Category: Productivity
- Tags: real-estate, rent-roll, direct-capitalization, excel, local-first, japan

## Privacy and security

- Processing runs in the user's local environment.
- The Local Web UI binds only to `127.0.0.1`.
- revenue-kun is not a hosted SaaS product.
- Input files are not sent to an external service by revenue-kun.
- Private PDFs, real property data, secrets, and API keys must not be committed.
- Only synthetic samples may be published.
- OCR and scanned PDFs are unsupported.

## Disclaimer

- Output values are `収益試算値` (income-estimation values), not appraisal conclusions or `収益価格`.
- revenue-kun does not provide a real-estate appraisal, investment advice, legal advice, or tax advice.
- Users must independently review extracted data, assumptions, formulas, and results.

## Submission checklist

- [x] Plugin name matches the plugin folder and manifest name.
- [x] Semantic version matches repository version `0.5.2`.
- [x] Apache-2.0 license is declared and `LICENSE` exists.
- [x] Repository and homepage are public.
- [x] Skill path exists in the packaged plugin.
- [x] Canonical Skill remains `.agents/skills/revenue-kun/`.
- [x] Local-only and non-SaaS scope is explicit.
- [x] OCR and scanned-PDF limitations are explicit.
- [x] Appraisal and investment-advice disclaimers are explicit.
- [x] Public Privacy Policy, Terms of Service, and Support URLs are prepared for GitHub Pages.
- [ ] Upload or approve a production logo in the OpenAI submission portal if required.
- [ ] Confirm install/enable/disable/uninstall behavior in a compatible Codex CLI or desktop build. Current local Codex CLI validation is blocked by a WindowsApps access-denied error.
- [ ] Complete the public submission at https://platform.openai.com/plugins with
      verified publisher identity, production logo, public support/privacy/terms
      URLs, five positive tests, three negative tests, availability, release
      notes, and policy attestations.
