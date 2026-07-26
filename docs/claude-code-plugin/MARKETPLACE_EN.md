# revenue-kun — Claude Code Marketplace Listing Copy (English)

## Plugin name
`revenue-kun`

## Display name
revenue-kun — Rent Roll to Direct Capitalization Excel

## One-line description
An Apache-2.0 local-first OSS tool that converts rent-roll CSV or text-based PDF files into a direct-capitalization Excel workbook.

## Description (100–200 characters)
revenue-kun reads a rent roll (CSV or text-based PDF) and generates a direct-capitalization Excel workbook (direct_cap.xlsx). Local Web UI, CLI, and Docker supported. Output is a revenue estimate, not an appraisal.

## Detailed description
revenue-kun is a local-first tool for real-estate practitioners that performs a direct-capitalization revenue estimate from a rent roll. It reads CSV or text-based PDF rent rolls, lets you preview the extracted rows, and generates an Excel workbook (`direct_cap.xlsx`) that always contains two independent calculation sheets (an OER-based sheet and a detailed-expense sheet) alongside the extracted rent-roll sheet. Judgment inputs that require professional discretion — vacancy loss rate, bad-debt rate, OER (or itemized operating expenses), capital expenditures, and the capitalization rate — are never collected by the app; the user enters them directly in the generated Excel file. Formulas are never hidden, so every calculation can be inspected cell by cell.

As a Claude Code Skill, asking "start revenue-kun" or "open the Web UI" launches a Local Web UI bound only to `127.0.0.1`. If an existing process is already running, it is detected via `/healthz` and reused rather than duplicated.

## Key features
- Read CSV or text-based PDF rent rolls
- Preview extracted results (unit count, occupied/vacant, missing fields)
- Automatic inclusion of rent, common fee, water, parking, and other income into GPI
- Simultaneous output of OER-based and expense-detail sheets (fully independent of each other)
- Extracted rent-roll sheet output
- Local Web UI (127.0.0.1 only)
- CLI support
- Docker support
- Excel output with visible, uneditable-formula-free calculation logic

## Example prompts
- "Start revenue-kun"
- "Open the revenue-kun Web UI"
- "I want to use revenue-kun in my browser"
- "Generate a revenue-estimate Excel from this rent-roll PDF"
- "Generate direct_cap.xlsx from this CSV"

## Supported input
- CSV
- Text-based PDF

## Unsupported input
- OCR-required PDFs
- Scanned PDFs
- Smartphone photo images
- Complex merged cells
- Complex tables spanning multiple pages
- Hosted SaaS usage (this tool is local-execution only)

## Local Web UI
Launch with `python -m uvicorn webui.app:app --host 127.0.0.1 --port 8000`. Binds only to `127.0.0.1`; never exposed to the internet or LAN. Before launching, `/healthz` is checked; if it returns `{"status":"ok"}`, the existing process is reused instead of starting a duplicate.

## CLI
`python src/main.py --assumptions <yaml> --rent-roll-pdf <pdf> --output <dir> --excel-output <path>` generates the Excel workbook.

## Docker
Build with `docker build -f Dockerfile.web -t revenue-kun-web .` and run with `docker run --rm -p 127.0.0.1:8000:8000 revenue-kun-web`. The host side binds only to `127.0.0.1`.

## Security
See [SECURITY_AND_PRIVACY.md](./SECURITY_AND_PRIVACY.md). Runs in the user's local environment; uploaded files are never transmitted to an external server.

## Privacy
The public repository contains synthetic samples only and does not include private PDFs, real property data, API keys, or other secrets.

## Disclaimer
The output of this tool is a revenue estimate (収益試算値), not an appraised value (収益価格) under a formal real estate appraisal. It does not provide investment, legal, or tax advice. For formal appraisal, pricing decisions, investment decisions, or legal/tax advice, consult a qualified real estate appraiser, attorney, tax advisor, or other relevant professional.

## Installation
```
/plugin marketplace add signal-yield/revenue-kun
/plugin install revenue-kun@revenue-kun
```

## Enable
```
/plugin enable revenue-kun@revenue-kun
```

## Disable
```
/plugin disable revenue-kun@revenue-kun
```

## Uninstall
```
/plugin uninstall revenue-kun@revenue-kun
```

## Remove the marketplace
```
/plugin marketplace remove revenue-kun
```

## Support
GitHub Issues: https://github.com/signal-yield/revenue-kun/issues

## Category candidate
Productivity

## Tag candidates
real-estate, rent-roll, direct-capitalization, excel, local-first, japan

## Starter prompts
- Start revenue-kun
- Generate a revenue-estimate Excel from this rent-roll PDF
- Generate direct_cap.xlsx from this CSV

## Release notes
Latest: v0.5.2. Independent OER and expense-detail calculation sheets; recurring income (water, parking, and other income) is now automatically included in GPI. See [Release v0.5.2](https://github.com/signal-yield/revenue-kun/releases/tag/v0.5.2).

## Submission checklist
See [SUBMISSION_CHECKLIST.md](./SUBMISSION_CHECKLIST.md).

## Fields to fill in manually at submission time
- Account linkage for the community-marketplace submission form (claude.ai or Console)
- Publisher/organization information (as required by the form)
- Confirmation of the final `claude plugin validate` run before submitting

## Unconfirmed official requirements
- Icon/logo requirements (whether required, file format, dimensions, etc.) could not be confirmed in Anthropic's official public specification
- No dedicated field for declaring shell-execution or local-file-access capability exists in the official plugin.json or marketplace.json schema; this could not be confirmed
- Details of the publisher verification program could not be confirmed in Anthropic's official public specification
