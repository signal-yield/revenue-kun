# revenue-kun Codex Plugin

This repository packages the canonical Codex Skill at
`.agents/skills/revenue-kun/` as the skills-only Codex Plugin in
`plugins/revenue-kun/`. The plugin is a distribution wrapper; it does not fork or
replace the revenue-kun engine.

## Synchronize the Skill

Do not edit the plugin copy by hand. Update the canonical Skill, then run:

```bash
python scripts/sync_codex_plugin_skill.py
python scripts/sync_codex_plugin_skill.py --check
```

The check command exits non-zero if files are missing, extra, or different.

## Install from this repository

Add the repository marketplace and install the plugin:

```bash
codex plugin marketplace add signal-yield/revenue-kun
codex plugin add revenue-kun@revenue-kun-local
```

For a local checkout, add its repository root instead:

```bash
codex plugin marketplace add /absolute/path/to/revenue-kun
codex plugin add revenue-kun@revenue-kun-local
```

Restart the ChatGPT desktop app and use a new task after installing or updating
the plugin.

## Runtime and data handling

- revenue-kun is local OSS, not hosted SaaS.
- The Local Web UI binds only to `127.0.0.1`. The Skill checks `/healthz` and
  reuses a healthy existing process instead of starting a duplicate.
- Input files are processed locally and are not sent to an external service by
  revenue-kun.
- Supported inputs are CSV and text-extractable PDFs. OCR, scanned PDFs, and
  smartphone photographs are unsupported.
- Output values are revenue estimates (`収益試算値`), not real-estate appraisal
  values. The plugin does not provide investment, legal, or tax decisions.

The plugin follows the repository's `GUARDRAILS.md`. Installing the plugin does
not install Python dependencies; follow `README.md` for local runtime setup.

## Validate

```bash
python scripts/sync_codex_plugin_skill.py --check
python C:/path/to/plugin-creator/scripts/validate_plugin.py plugins/revenue-kun
python -m pytest -q
```

## Disable or uninstall

Disable the plugin from the ChatGPT desktop app's Plugins settings. Uninstall it
from the plugin details page with **Uninstall plugin**. Remove the marketplace
source separately with:

```bash
codex plugin marketplace remove revenue-kun-local
```

## Public directory readiness

Public submission starts at <https://platform.openai.com/plugins>. A future
submission must supply final public listing copy, a production logo, matching
website/support/privacy/terms URLs, verified publisher identity, release notes,
five positive test cases, three negative test cases, availability, and policy
attestations. These portal materials are not claimed as complete by this local
package.
