# revenue-kun Codex Plugin Install Guide

This guide is for users who want to install the revenue-kun Codex Plugin from the repo-hosted Codex Marketplace in this GitHub repository.

The OpenAI official Plugin Directory submission is separate from this repository distribution path. revenue-kun can be installed from this GitHub repository without waiting for official Directory listing, one-click Directory install, or verified publisher display.

## Supported Environment

- Codex CLI, ChatGPT Desktop with Codex, or another Codex environment that supports Plugins.
- Network access to GitHub for adding the marketplace source.
- A local environment that can run revenue-kun dependencies when using the Local Web UI or CLI workflow.

## What This Installs

- Marketplace name: `signal-yield`
- Plugin name: `revenue-kun`
- Plugin package: `plugins/revenue-kun/`
- Marketplace catalog: `.agents/plugins/marketplace.json`
- Bundled Skill: `plugins/revenue-kun/skills/revenue-kun/`

## Install

Install in two steps.

### 1. Add the repo-hosted Codex Marketplace

```bash
codex plugin marketplace add signal-yield/revenue-kun
```

OpenAI's Codex manual documents GitHub shorthand sources such as `owner/repo`, ref pinning with `--ref`, Git URLs, SSH Git URLs, and local marketplace roots.

To pin a branch or ref:

```bash
codex plugin marketplace add signal-yield/revenue-kun --ref main
```

To add from a local checkout instead:

```bash
codex plugin marketplace add ./local-marketplace-root
```

### 2. Install the Plugin from `/plugins`

Start Codex and open the plugin browser:

```text
codex
/plugins
```

Choose the `signal-yield` marketplace, open `revenue-kun`, and install it from the plugin browser.

After installation, start a new Codex session so the bundled `revenue-kun` Skill is detected.

## Verify

List configured marketplaces:

```bash
codex plugin marketplace list
```

In Codex CLI, open the plugin browser:

```text
codex
/plugins
```

Confirm that:

- Marketplace `signal-yield` is available.
- Plugin `revenue-kun` is installed and enabled.
- Skill `revenue-kun` appears in a new Codex session.

## Usage Examples

```text
revenue-kunを起動して
Web UIを開いて
このレントロールCSVから収益試算Excelを作成して
このテキスト抽出可能PDFからdirect_cap.xlsxを作成して
```

## Local Web UI

When asked to launch revenue-kun, the Skill checks:

```text
http://127.0.0.1:8000/healthz
```

If an existing healthy revenue-kun process responds with `{"status":"ok"}`, reuse it instead of starting a duplicate. If no healthy process exists, launch the Local Web UI on `127.0.0.1:8000` only.

Do not expose the Local Web UI on `0.0.0.0`, LAN, or the public internet.

## Excel Generation

revenue-kun supports:

- Rent-roll CSV
- Text-based rent-roll PDF

It generates `direct_cap.xlsx` with:

- `直接還元法_OER`
- `直接還元法‗費用詳細版`
- `読み取りレントロール`

Outputs are income-estimation values (`収益試算値`), not a real-estate appraisal or `収益価格`.

## Manage the Plugin

Refresh configured marketplaces:

```bash
codex plugin marketplace upgrade
codex plugin marketplace upgrade signal-yield
```

Open the Codex CLI plugin browser:

```text
codex
/plugins
```

From the plugin browser:

- Press Space on an installed plugin to turn it on or off.
- Open the plugin details page and select **Uninstall plugin** when that action is available.

Remove the marketplace source:

```bash
codex plugin marketplace remove signal-yield
```

## Directory Listing vs GitHub Repository Distribution

Currently available through this repository:

- Add the GitHub repository as a Codex Marketplace.
- Install the `revenue-kun` Plugin.
- Use the bundled `revenue-kun` Skill in Codex.
- Launch the Local Web UI.
- Generate Excel workbooks from CSV or text-based PDFs.

Separate from this repository distribution:

- OpenAI official Plugin Directory listing.
- One-click install from the public Directory search listing.
- Verified publisher display in the official Directory.

Do not describe the plugin as already listed in the OpenAI official Directory.

## Security and Privacy

- revenue-kun is local-first OSS.
- The Local Web UI binds only to `127.0.0.1`.
- revenue-kun is not a hosted SaaS service.
- Input CSV/PDF files are processed locally.
- revenue-kun itself does not send input files to external services.
- API keys and external account linking are not required.
- Public repository samples must be synthetic or safely redacted.
- OCR, scanned PDFs, and smartphone-captured images are unsupported.
- revenue-kun does not provide real-estate appraisal, investment advice, legal advice, or tax advice.

## Troubleshooting

### `codex` cannot run

- Confirm that Codex CLI or ChatGPT Desktop with Codex is installed and available in the environment.
- On Windows, some environments may hit a WindowsApps access-denied error when launching `codex.exe`.
- Check the official Codex installation or update path for your environment.
- Do not work around the issue by copying or modifying the executable.
- Do not use administrator privileges broadly unless your organization explicitly requires and approves that path.

### Plugin is not visible after adding the Marketplace

- Restart Codex or ChatGPT Desktop.
- Run `codex plugin marketplace list`.
- Open `/plugins` and choose the `signal-yield` marketplace.
- Confirm the marketplace name is `signal-yield`.
- Confirm the plugin name is `revenue-kun`.
- Start a new Codex session after installation so bundled skills are detected.

### Port 8000 is already in use

- Check `http://127.0.0.1:8000/healthz`.
- If it returns `{"status":"ok"}`, reuse the existing revenue-kun process.
- If another service is using the port or the response is unclear, do not kill the process automatically.
- Ask the user before using a different port.

### PDF cannot be read

- Confirm the PDF is text-based.
- OCR is unsupported.
- Scanned PDFs are unsupported.
- Smartphone-captured images are unsupported.

## Support

- Website: https://signal-yield.github.io/revenue-kun/
- Support: https://signal-yield.github.io/revenue-kun/support.html
- Issues: https://github.com/signal-yield/revenue-kun/issues
- Privacy Policy: https://signal-yield.github.io/revenue-kun/privacy.html
- Terms of Service: https://signal-yield.github.io/revenue-kun/terms.html
