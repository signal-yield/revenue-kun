# revenue-kun Claude Code Plugin Install Guide

This guide is for users who want to install the revenue-kun Claude Code Plugin from the repo-hosted Claude Code Marketplace in this GitHub repository.

Claude Code's official Marketplace (`claude-plugins-official`) and the community Marketplace are separate from this repository distribution path. revenue-kun can be installed directly from this GitHub repository without waiting for official Marketplace listing, community Marketplace review, or verified publisher display.

## Supported Environment

- Claude Code CLI (`claude`), a recent version that supports the `/plugin` command and `claude plugin` subcommands.
- Network access to GitHub for adding the marketplace source.
- A local environment that can run revenue-kun dependencies when using the Local Web UI or CLI workflow.

## Prerequisites

- Claude Code is installed and authenticated. Run `claude --version` to confirm.
- If `claude plugin` or `/plugin` is not recognized, update Claude Code to the latest version first.

## What This Installs

- Marketplace name: `revenue-kun`
- Plugin name: `revenue-kun`
- Plugin package: `claude-plugins/revenue-kun/`
- Marketplace catalog: `.claude-plugin/marketplace.json`
- Bundled Skill: `claude-plugins/revenue-kun/skills/revenue-kun/`

## 1. Add the Marketplace

```bash
claude plugin marketplace add signal-yield/revenue-kun
```

This registers the repository as a Claude Code Marketplace. No plugin is installed yet at this step.

To add from a local checkout instead:

```bash
claude plugin marketplace add ./path/to/revenue-kun
```

To pin a specific branch or tag when adding from GitHub, append `@ref` to the shorthand:

```bash
claude plugin marketplace add signal-yield/revenue-kun@main
```

## 2. Install the Plugin

```bash
claude plugin install revenue-kun@revenue-kun
```

## 3. Confirm with Plugin Details

```bash
claude plugin details revenue-kun@revenue-kun
```

Confirm that:

- The plugin name is `revenue-kun` and the version matches the repository's current release.
- The component inventory shows exactly one Skill.

## Skill Detection

After installation, the `revenue-kun` Skill is available immediately in the current session, and is also listed under `claude plugin list`. If it does not appear, run `/reload-plugins` inside Claude Code.

## Usage Examples

```text
revenue-kunを起動して
revenue-kunのWeb UIを開いて
このレントロールCSVから収益試算Excelを作成して
このテキスト抽出可能PDFからdirect_cap.xlsxを作成して
```

## Local Web UI

When asked to launch revenue-kun, the Skill checks:

```text
http://127.0.0.1:8000/healthz
```

If an existing healthy revenue-kun process responds with `{"status":"ok"}`, it is reused instead of starting a duplicate. If the port is in use by something else or the response is unclear, the existing process is not killed or reused automatically.

If no healthy process exists, the Local Web UI is launched on `127.0.0.1:8000` only:

```bash
python -m uvicorn webui.app:app --host 127.0.0.1 --port 8000
```

The Local Web UI is never exposed on `0.0.0.0`, LAN, or the public internet.

## Generate Excel from a CSV Rent Roll

revenue-kun reads a rent-roll CSV and generates `direct_cap.xlsx` containing:

- `直接還元法_OER`
- `直接還元法‗費用詳細版`
- `読み取りレントロール`

## Generate Excel from a Text-Based PDF Rent Roll

The same `direct_cap.xlsx` output is generated from a text-based (non-scanned) rent-roll PDF. Outputs are income-estimation values (`収益試算値`), not a real-estate appraisal or `収益価格`.

## Disable

```bash
claude plugin disable revenue-kun@revenue-kun
```

## Enable

```bash
claude plugin enable revenue-kun@revenue-kun
```

## Uninstall

```bash
claude plugin uninstall revenue-kun@revenue-kun
```

## Remove the Marketplace

```bash
claude plugin marketplace remove revenue-kun
```

Removing the marketplace also uninstalls any plugin you installed from it.

## Troubleshooting

### `claude` command not found

- Confirm Claude Code CLI is installed. See Anthropic's official installation instructions for your platform.
- Run `claude --version` to confirm the installed version.
- Do not work around a missing installation by copying or modifying an executable manually.

### Adding the Marketplace fails

- Confirm you have network access to GitHub and the repository is reachable.
- Confirm the repository name is `signal-yield/revenue-kun`.
- Confirm the marketplace name is `revenue-kun` — check with `claude plugin marketplace list`.
- If a marketplace with the same name is already registered from a different source, remove it first with `claude plugin marketplace remove revenue-kun`, then re-add.

### Installing the Plugin fails

- Confirm the marketplace is registered: `claude plugin marketplace list`.
- Confirm the plugin name is `revenue-kun`.
- Confirm the install target is exactly `revenue-kun@revenue-kun`.
- Run `claude plugin details revenue-kun@revenue-kun` to check whether it is already installed.

### The Web UI does not start

- Confirm you are running from the repository root and that `webui/` exists there.
- Confirm `requirements-web.txt` dependencies are installed.
- Check `http://127.0.0.1:8000/healthz` before launching.
- Check whether port 8000 is already in use by another process.
- Do not force-terminate an existing process you cannot identify as revenue-kun's own.
- Keep the bind limited to `127.0.0.1`; do not launch on `0.0.0.0`.

### The PDF cannot be read

- Only text-based PDFs are supported.
- OCR is not supported.
- Scanned PDFs are not supported.
- Smartphone-captured photo images are not supported.

### The Marketplace remains after removing the Plugin

```bash
claude plugin marketplace remove revenue-kun
```

## Claude Code Official Marketplace vs. This Repository

Currently available through this repository:

- Add the GitHub repository as a Claude Code Marketplace.
- Install the `revenue-kun` Plugin.
- Confirm the Skill with `claude plugin details`.
- Launch the Local Web UI.
- Generate Excel workbooks from CSV or text-based PDF rent rolls.
- Disable, enable, and uninstall the plugin.
- Remove the marketplace.

Not part of this work:

- Submission to the official Claude Code Marketplace (`claude-plugins-official`).
- Submission to the community Marketplace (`claude-plugins-community`).
- Verified publisher display.
- Listing in any official plugin directory.

## Security / Privacy

- revenue-kun is local-first OSS.
- The Local Web UI binds only to `127.0.0.1`.
- revenue-kun is not a hosted SaaS service.
- revenue-kun does not send uploaded CSV or PDF files to an external server.
- API keys or external account linking are not required to use revenue-kun.
- The public repository contains synthetic samples only.
- OCR, scanned PDFs, and smartphone-captured images are unsupported.
- revenue-kun does not provide real-estate appraisal, investment advice, legal advice, or tax advice.

## Support

- Website: https://signal-yield.github.io/revenue-kun/
- Support: https://signal-yield.github.io/revenue-kun/support.html
- Issues: https://github.com/signal-yield/revenue-kun/issues
- Privacy Policy: https://signal-yield.github.io/revenue-kun/privacy.html
- Terms of Service: https://signal-yield.github.io/revenue-kun/terms.html
