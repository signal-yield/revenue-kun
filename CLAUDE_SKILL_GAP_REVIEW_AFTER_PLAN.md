# Claude Skill Gap Review — After Plan v0.1

Reviewed document: `CLAUDE_SKILL_V01_PLAN_AFTER_LP.md`  
Review perspective: Claude Skill / Claude Code custom command author  
Scope: identify what is missing before implementation can begin

This review document does **not** implement anything.  
No Python code is modified. No release or tag is created.  
Claude Skill リリース済みとは表記しません。

---

## 1. What the Plan Gets Right

Before listing gaps, items that are correct and must be preserved:

| Section | Strength |
|---------|---------|
| §10 Prohibited Claims | Well-specified. Covers appraisal, OCR, SaaS, investment/legal/tax advice, Skill release wording. |
| §11 Error Handling | Correct instinct: surface error, stop, do not retry with modified inputs, no synthetic fill. |
| §12 Human Checkpoints | Correct names (A/B/C) and correct ordering. |
| §6 Intended Workflow | Step sequence is correct; "Claude does not" list is accurate. |
| §16 External Messaging | Allowed vs. prohibited external wording is clearly separated. |

These must be preserved exactly during implementation. The gaps below are additive, not corrections.

---

## 2. Critical Gap: Three Distinct Mechanisms Conflated as One

The plan uses "Claude Skill" to mean all of the following simultaneously:

| Mechanism | What it is | How Claude uses it |
|-----------|-----------|-------------------|
| **`CLAUDE.md`** | Operator-level system instruction read at every session start | Always-on; Claude sees it before the user types anything |
| **`.claude/commands/<name>.md`** | Custom slash command invoked by the user (e.g., `/revenue-kun`) | On-demand; triggered by user command |
| **Marketplace Skill** | Packaged, distributable Skill descriptor (not yet publicly available infrastructure) | Installed from registry; runs in separate context |

These have different: scope, trigger model, distribution model, and capability requirements.

**Why it matters for implementation**: CLAUDE.md and a custom command file have different content structures and serve different purposes. Writing one as if it is the other will produce a nonfunctional result.

**Resolution required**: Pick the v0.1 packaging target before writing any content. Based on what already exists in this repo, the correct choice for v0.1 is:

- **Primary**: `CLAUDE.md` (operator instructions — always active when Claude works in this repo)
- **Optional**: `.claude/commands/revenue-kun.md` (explicit trigger for the full workflow)

These two are not the same file. Both must be designed separately.

---

## 3. Required File Structure — What Is Missing

The plan mentions files but does not define their required content structure.
The following files must be created (not yet present):

```
revenue-kun/
├── CLAUDE.md                           ← NEW: operator instructions (always-on)
├── .claude/
│   ├── settings.json                   ← NEW: tool permission allowlist
│   └── commands/
│       └── revenue-kun.md              ← NEW: /revenue-kun slash command
├── src/revenue_kun/                    (existing — no changes)
├── data/                               (existing)
├── docs/                               (existing — LP)
└── assumptions.sample.yaml             (existing)
```

None of these three new files exist. The plan acknowledges absence but does not define their internal structure. Each is described in the sections below.

---

## 4. CLAUDE.md — Content Structure Not Defined

The plan lists CLAUDE.md as a packaging option but does not specify what must be in it.

A `CLAUDE.md` for revenue-kun must contain at minimum:

### 4.1 Role declaration (required opening)

An unambiguous statement of what Claude's role is in this repo:

```
Claude's role in this repository is to assist in running the revenue-kun CLI,
reviewing its structured output files, and guiding the user through filling in
user-editable Excel fields. Claude does not perform appraisal, provide investment
advice, provide legal advice, or provide tax advice.
```

Without an explicit role declaration, Claude may infer a broader role from context.

### 4.2 DISCLAIMER visibility rule (required)

The CLI emits a DISCLAIMER constant on every run. CLAUDE.md must specify:
- Claude must reproduce the DISCLAIMER text in its response when it runs the CLI
- Claude must not summarize or abbreviate the DISCLAIMER
- Claude must not proceed past the DISCLAIMER output without surfacing it to the user

The current plan says DISCLAIMER "must remain visible" but does not bind this to Claude's behavior.

### 4.3 "Do not infer values" rule (required)

The plan says Claude must not recommend cap rates or fill in missing fields.  
CLAUDE.md must make this specific — not just "do not recommend" but also:

- Do not provide ranges, examples, or typical values for cap rates, vacancy rates, or expense ratios
- Do not say "typical Tokyo residential cap rates are X%" or equivalent
- If the user asks "what should I enter for 還元利回り?", respond with the deflection protocol (see §9 below)

This rule is absent from the plan entirely.

### 4.4 Checkpoint enforcement rule (required)

CLAUDE.md must specify that Claude must explicitly pause at checkpoints A, B, and C
and wait for an unambiguous user confirmation before continuing. The current plan
defines what the checkpoints are but does not define:
- What Claude must output to initiate each checkpoint
- What constitutes valid confirmation
- Whether Claude may continue if the user ignores the checkpoint

### 4.5 Scope restriction (required)

CLAUDE.md must state which files Claude may read and which it must not modify:

| Allowed reads | Prohibited modifications |
|--------------|-------------------------|
| `output/missing_info.md` | Any file in `src/` |
| `output/extraction_log.json` | Any `.py` file anywhere |
| `assumptions.sample.yaml` | Any `.pdf` in `data/` |
| `output/*.xlsx` (structural check only) | Any `.yaml` file (unless user explicitly asks) |

---

## 5. `.claude/commands/revenue-kun.md` — Content Structure Not Defined

A Claude Code custom command file must define:

### 5.1 What arguments the command accepts

The plan does not define whether `/revenue-kun` accepts arguments or asks interactively.
The command must specify one of these patterns:

```
/revenue-kun                            ← asks user for PDF path, assumptions path
/revenue-kun <pdf-path>                 ← PDF path as arg; uses assumptions.sample.yaml default
/revenue-kun <pdf-path> <yaml-path>     ← both paths as args
```

Each pattern has different input validation requirements.

### 5.2 What Claude does when invoked

The command file must enumerate each step Claude will take, in order — not as a prose workflow
(which exists in §6 of the plan) but as explicit Claude instructions. The plan's §6 workflow
describes the desired behavior but is written as documentation, not as an instruction to Claude.

### 5.3 How it handles sample-only mode

There is no definition of whether `/revenue-kun` accepts a `--sample` flag or equivalent
that restricts the command to using only synthetic bundled PDFs. This is needed because
until Issue #21 is complete, use with real-world PDFs should be treated as unsupported.

---

## 6. `.claude/settings.json` — Permission Entries Not Defined

Claude Code enforces a tool permission allowlist via `.claude/settings.json`.
The plan identifies which commands are allowed but does not translate them to settings entries.

### 6.1 What entries are required

The `allow` list must match the commands in §9 of the plan, expressed as glob patterns:

```json
{
  "permissions": {
    "allow": [
      "Bash(python src/main.py --dry-run*)",
      "Bash(python src/main.py --excel-output*)",
      "Bash(python src/main.py --version)",
      "Bash(python -m pytest tests/)"
    ],
    "deny": [
      "Bash(pip*)",
      "Bash(pip install*)",
      "Bash(*rm *)",
      "Bash(git push*)",
      "Bash(git commit*)"
    ]
  }
}
```

Without `settings.json`, each Bash invocation triggers a user permission prompt.
With it, allowed commands run without interruption, and denied commands are blocked.

### 6.2 What the plan gets wrong about "prohibited operations"

The plan lists prohibited operations in prose but they are not enforceable without settings.json.
"Claude must not run pip install" is a policy statement; settings.json makes it a hard constraint.

---

## 7. Allowed Commands — Gaps in the Current List

The plan's §9 allowed command list has the following gaps:

| Gap | Detail |
|-----|--------|
| Missing `--rent-roll` (CSV path) | Plan lists `--rent-roll-pdf` but not the CSV input flag |
| No default for `--output` | Plan does not specify what `--output` defaults to if the user omits it |
| `python -m pytest` too broad | Should be `python -m pytest tests/` to avoid running any script in scope |
| `python src/main.py --help` not listed | Should be explicitly allowed (read-only, safe) |
| Read operations not distinguished from Bash | Reading `output/missing_info.md` via the file read tool is different from running Bash to `cat` it; the plan conflates them |
| No maximum on `--output` directory | The plan should specify that `--output` must be within the project working directory, not an absolute system path |

### 7.1 Exact flag combinations that must be specified

For `--dry-run` (required to come before the full run):

```
python src/main.py \
  --assumptions <yaml-path> \
  --rent-roll-pdf <pdf-path> \
  --output <output-dir> \
  --dry-run
```

All four flags are required. The plan does not state this.

For the full run (only after checkpoint A passes):

```
python src/main.py \
  --assumptions <yaml-path> \
  --rent-roll-pdf <pdf-path> \
  --output <output-dir> \
  --excel-output <xlsx-path>
```

All five flags are required. The plan does not state this.

---

## 8. Prohibited Commands — Gaps

The plan's §9 prohibited list is correct but incomplete:

| Missing prohibition | Why it matters |
|--------------------|---------------|
| `python scripts/make_sample_pdf.py` | Claude must not regenerate synthetic PDFs during a live workflow without user instruction |
| Any command reading files outside the project directory | Prevents Claude from accessing user system files |
| `python src/main.py` without `--dry-run` as the first invocation | The first CLI call must always be `--dry-run` |
| Shell pipeline operators (`\|`, `>`, `>>`) | Prevents output redirection to unexpected locations |
| Background execution (`&`, `Start-Job`) | Prevents detached processes |

---

## 9. Human Review Checkpoints — Protocol Gaps

The plan names checkpoints A, B, C but does not define the interaction protocol.

### 9.1 What Claude must output at each checkpoint

**Checkpoint A — Extraction review:**

Claude must output a structured summary of extraction results and then explicitly wait.
The summary must include:
- Number of units extracted
- Column map fields recognized
- Number of missing cells
- Whether any required fields are absent
- A clear question asking the user to confirm or report discrepancies

Claude must not proceed to the full run until the user responds affirmatively.

**Checkpoint B — Excel cell review:**

After the full run and after listing missing cells from `missing_info.md`, Claude must:
- List each cell the user must fill in, grouped by sheet
- Explicitly state it cannot fill these in on the user's behalf
- Ask the user to confirm when they have completed their edits

Claude must not treat silence as confirmation.

**Checkpoint C — Professional review reminder:**

Every response that references a 収益試算値 figure must include a statement equivalent to:

> 「出力値は収益試算値です。正式な価格判断・投資判断・法律的判断が必要な場合は専門家に確認してください。」

This is not a one-time statement. It must be repeated whenever a value is referenced.
The plan states this in §12 but does not make it an explicit instruction to Claude.

### 9.2 What constitutes valid confirmation

The plan does not define this. Required:
- Checkpoint A: user must explicitly state that the extracted data looks correct, or describe a discrepancy
- Checkpoint B: user must explicitly state they have filled in the required cells
- Checkpoint C: no confirmation required — it is a required disclosure, not a gate

---

## 10. Response Templates — Not Defined

The plan describes what Claude should do but does not define what Claude should say.
Without response templates, implementation decisions about tone, completeness, and disclaimer
placement will be made inconsistently. The following response templates are missing:

| Template needed | Trigger |
|----------------|---------|
| Extraction success summary | After `--dry-run` completes with exit 0 |
| Extraction failure summary | After `RentRollExtractionError` or exit ≠ 0 |
| Missing fields list | After reading `missing_info.md` |
| Checkpoint A prompt | After extraction success summary |
| Checkpoint B prompt | After listing missing fields |
| Checkpoint C disclosure | Each time a 収益試算値 value is referenced |
| Value recommendation deflection | When user asks Claude to suggest a cap rate or vacancy rate |
| OCR inquiry deflection | When user asks whether their scanned PDF will work |

---

## 11. Value Recommendation Deflection Protocol — Not Defined

The plan says Claude must not recommend cap rates. What happens when the user directly asks?

Example user messages requiring deflection:
- 「還元利回りは何パーセントにすればいいですか？」
- 「東京の住居系物件の空室率の相場は？」
- 「経費率の目安を教えてください」

The plan has no deflection protocol. Required:

Claude must respond to these questions with:
1. An explicit statement that it does not provide cap rate, vacancy rate, or expense ratio recommendations
2. A reference to where the user can find authoritative sources (e.g., 鑑定士、不動産専門家、公的統計)
3. No examples, ranges, or "typical values" even framed as educational

This applies even if the user frames it as "just give me a ballpark" or "just for the sample data."

---

## 12. Path Injection Risk — Not Addressed

The plan does not address what happens when Claude constructs a CLI command using a user-provided path.

If Claude builds:
```
python src/main.py --rent-roll-pdf <user-input> --output ./output
```

...a malicious or mistaken user input of `; rm -rf ./output` or a path containing spaces
and shell metacharacters could cause unintended behavior.

Required additions to the Skill's operator instructions:
- Claude must validate that the user-provided path exists before constructing the command
- Claude must validate that the path has a `.pdf` or `.csv` extension
- Claude must validate that the path is within or adjacent to the project working directory
- Claude must use the Bash tool's argument passing mechanism (not string interpolation) to pass paths
- Claude must not accept paths that begin with `-` (shell option injection)

---

## 13. Windows / PowerShell Portability — Not Addressed

This project runs on Windows (confirmed by working directory `C:\Users\pinot\`).
The plan's §13 sample-only validation flow uses PowerShell backtick syntax (`` ` ``).
No other section addresses platform differences.

Gaps:
- PowerShell line continuation is `` ` ``; bash is `\`. The command file must specify the correct syntax for the target shell.
- Output paths: `output\missing_info.md` on Windows, `output/missing_info.md` on Unix. File read operations must handle both.
- Console encoding: Python printing Japanese on Windows may produce encoding errors unless `PYTHONUTF8=1` or `chcp 65001` is set. The Skill should specify this.
- `.claude/commands/revenue-kun.md` must specify which shell is assumed, or include both variants.

---

## 14. DISCLAIMER Visibility Requirement — Underspecified

The plan states the DISCLAIMER "must remain visible to user" but does not bind this to a Claude action.

The DISCLAIMER is emitted as part of CLI stdout. If Claude summarizes the CLI output,
it may omit the DISCLAIMER text. Required rule:

> When Claude runs the CLI and surfaces the output, it must reproduce the DISCLAIMER
> text verbatim in its response before summarizing any numerical results.
> Claude must not paraphrase, shorten, or omit the DISCLAIMER.

This rule is absent from the plan and must appear in CLAUDE.md explicitly.

---

## 15. "Sample-Only Skill Candidate" Concept — Missing

Section 15 of the plan sets qualifying real-world PDF evaluation (Issue #21) as a mandatory
release criterion. This creates a high bar that blocks any Skill release until #21 is complete.

Missing concept: a **sample-only Skill candidate** — a Skill release that:
- Works only with `data/sample_rentroll_simple.pdf` and `data/sample_rentroll_missing_values.pdf`
- Explicitly refuses to process user-provided PDFs until Issue #21 is complete
- Is described externally as "sample-only demonstration mode — not validated for real-world use"

This would allow the Skill packaging, CLAUDE.md, and command file to be tested and refined
before qualifying PDFs are available, without making any claims about real-world readiness.

Whether to create this intermediate release is a decision the plan defers to "Skill authoring begins"
but should be decided before authoring begins, since it changes the content of CLAUDE.md.

---

## 16. Skill Testing Strategy — Not Defined

The plan mentions `python -m pytest` as an allowed command but this tests the Python CLI,
not the Skill's behavior. Skill-level testing requires a different approach:

| What needs to be tested | How |
|------------------------|-----|
| CLAUDE.md operator instructions are parsed correctly | Manual review checklist |
| Command file triggers the correct workflow | End-to-end session test |
| Checkpoint A fires before the full run | Session test with deliberate extraction failure |
| Checkpoint C appears in every response with a value | Content review of session transcript |
| Prohibited wording does not appear in Claude's responses | Automated string scan on session transcripts |
| Value recommendation deflection fires correctly | Session test with explicit user request |

None of these are defined in the plan. A Skill testing checklist parallel to the risky wording scan
used for LP content must be created before the Skill is released.

---

## 17. Skill Versioning Strategy — Not Defined

The CLI is versioned (currently v0.4.1). The plan does not define:

| Question | Answer required |
|----------|----------------|
| Does the Skill version track the CLI version? | Not defined |
| Is Skill version stored in a file? Where? | Not defined |
| Who increments the Skill version on update? | Not defined |
| Does CLAUDE.md include a version header? | Not defined |

Minimum required: CLAUDE.md should include a version comment at the top that is updated
when the Skill instructions change, independent of CLI version bumps.

---

## 18. Required Instructions for Claude — Summary

Combining all gaps above, CLAUDE.md must contain the following instruction categories
(none of which are currently drafted):

| Category | Minimum content |
|----------|----------------|
| Role declaration | Claude's role is workflow assistant, not appraiser or advisor |
| DISCLAIMER rule | Reproduce verbatim before any numerical summary |
| First-call rule | Always `--dry-run` before full run |
| Checkpoint A protocol | What to output; what constitutes confirmation |
| Checkpoint B protocol | What to output; explicit list of cells; must not fill in |
| Checkpoint C protocol | Required disclosure text; must appear with every value reference |
| Value deflection rule | Do not provide ranges, examples, or typical values for cap rates / vacancy / expenses |
| OCR deflection rule | If user asks about scanned PDF, state it is out of scope; do not suggest workarounds |
| Path validation rule | Validate path exists, has correct extension, is within project directory |
| Scope restriction | Which files Claude may read; which it must not modify |
| Error stop rule | Surface error message; do not silently retry; do not generate synthetic values |
| Prohibited wording list | Full list from §10 of the plan; must appear in CLAUDE.md verbatim |

---

## 19. Allowed Commands — Definitive List (Revised)

| Command | Conditions |
|---------|-----------|
| `python src/main.py --version` | Any time |
| `python src/main.py --help` | Any time |
| `python src/main.py --assumptions <yaml> --rent-roll-pdf <pdf> --output <dir> --dry-run` | First call only; all 4 flags required |
| `python src/main.py --assumptions <yaml> --rent-roll-pdf <pdf> --output <dir> --excel-output <xlsx>` | Only after Checkpoint A confirmed; all 5 flags required |
| `python src/main.py --assumptions <yaml> --rent-roll <csv> --output <dir> --dry-run` | CSV variant; same conditions |
| `python src/main.py --assumptions <yaml> --rent-roll <csv> --output <dir> --excel-output <xlsx>` | CSV variant; only after Checkpoint A |
| `python -m pytest tests/` | At user request only |
| File read: `output/missing_info.md` | After full run; for Checkpoint B |
| File read: `output/extraction_log.json` | After dry run; for Checkpoint A |
| File read: `assumptions.sample.yaml` | To show user which fields are configurable |

---

## 20. Prohibited Commands — Definitive List (Revised)

In addition to the plan's §9 list, the following must be explicitly prohibited:

| Prohibited | Reason |
|-----------|--------|
| `python src/main.py` without `--dry-run` as first call | Extraction must be verified before full run |
| `python scripts/make_sample_pdf.py` | Must not regenerate sample PDFs mid-workflow |
| Any shell pipeline (`\|`, `>`, `>>`, `2>`) | Prevents output redirection to unexpected destinations |
| Background execution (`&`, `Start-Job`, `nohup`) | Prevents detached processes |
| Any path outside the project working directory in `--output` or `--excel-output` | Scope restriction |
| `pip`, `pip install`, `pip upgrade` | Package modification |
| `git push`, `git commit`, `git reset`, `git checkout` | Repository modification |
| Any Bash command that deletes or overwrites files (except the designated output paths) | Data preservation |
| Any OCR command or library invocation (`tesseract`, `pytesseract`, `easyocr`) | OCR is out of scope |
| Editing any file in `src/`, `tests/`, `docs/`, `data/` | Source and asset preservation |

---

## 21. Human Review Checkpoints — Definitive Protocol

| Checkpoint | Trigger | Claude's required output | Required user action before continuing |
|-----------|---------|------------------------|--------------------------------------|
| **A — Extraction review** | After `--dry-run` exits 0 | (1) DISCLAIMER verbatim, (2) units extracted count, (3) column map fields, (4) missing cell count, (5) explicit confirmation question | Explicit written confirmation or description of discrepancy |
| **B — Excel cell review** | After full run, after reading `missing_info.md` | (1) List of cells requiring user input by sheet, (2) statement that Claude cannot fill these in, (3) explicit question asking user to confirm completion | Explicit written confirmation that cells have been filled |
| **C — Professional review disclosure** | Every response referencing a 収益試算値 figure | Required disclosure: 「出力値は収益試算値です。正式な価格判断・投資判断・法律的判断が必要な場合は専門家に確認してください。」 | No confirmation required — disclosure only |

Checkpoint C is **not a gate** — it does not stop the workflow. It is a mandatory disclosure
that must appear in every response referencing a numerical estimate.

---

## 22. Prohibited Wording — Confirmed and Additional Items

The plan's §10 list is correct. The following items are confirmed and must be preserved:

> 実務検証済み / OCR対応 / スキャンPDF対応 / 鑑定評価（肯定文脈） / 収益価格 /
> 投資助言 / 推奨物件 / 法律的判断 / 税務上の判断 / 完全自動 / AIが査定 / AIが評価 /
> Claude Skillリリース済み / Claude Skill対応済み / Claude Skill版を公開しました /
> SaaS / 月額料金 / 欠損を自動補完

The following items are **missing from the plan's §10** and must be added:

| Missing prohibition | Why |
|--------------------|-----|
| Cap rate / vacancy rate / expense ratio examples or ranges | Prevents indirect advisory claims (e.g., "typical values are...") |
| 「AIが評価した収益試算値」 | Implies AI judgment; user and professional judgment are required |
| 「この物件は買いです」「この物件は割安」 | Investment recommendation |
| 「このツールで査定してみましょう」 | Framing revenue-kun as an appraisal tool |
| 「スキャンPDFも試してみてください」 | Implies OCR workaround |
| Any wording suggesting the Skill works for real-world PDFs until Issue #21 is complete | Premature real-world claim |

---

## 23. Gap Priority Table

| # | Gap | Severity | Blocks implementation? |
|---|-----|----------|----------------------|
| 1 | Conceptual conflation of three packaging mechanisms | High | Yes — wrong file structure will result |
| 2 | CLAUDE.md content not defined | High | Yes — primary packaging file |
| 3 | `.claude/commands/revenue-kun.md` content not defined | High | Yes — command file |
| 4 | `.claude/settings.json` not defined | High | Yes — permissions not enforced without it |
| 5 | Checkpoint protocol (what to output, what counts as confirmation) | High | Yes — checkpoints will not be enforceable |
| 6 | Value recommendation deflection protocol | High | Yes — safety-critical missing rule |
| 7 | DISCLAIMER visibility rule not bound to Claude action | High | Yes — DISCLAIMER can be silently omitted |
| 8 | Path injection risk | Medium | No — but necessary before real-world use |
| 9 | Response templates not defined | Medium | No — but inconsistency without them |
| 10 | Windows/PowerShell portability | Medium | No — but current platform is Windows |
| 11 | Sample-only Skill candidate concept not defined | Medium | No — but blocks sequencing decision |
| 12 | Allowed commands list incomplete | Medium | No — but incomplete permission grants |
| 13 | Prohibited commands list incomplete | Medium | No — but gaps in safety boundary |
| 14 | Skill testing strategy not defined | Medium | No — but no way to validate the Skill |
| 15 | Skill versioning not defined | Low | No — can be deferred |

---

## 24. Summary: What Is Missing Before Implementation Can Begin

The following seven items must be resolved before any Skill file can be written:

1. **Decide which packaging mechanism is v0.1** — CLAUDE.md only, or CLAUDE.md + `.claude/commands/revenue-kun.md`
2. **Draft CLAUDE.md content** — role declaration, DISCLAIMER rule, checkpoint protocols, value deflection rule, prohibited wording list
3. **Draft `.claude/commands/revenue-kun.md`** — arguments, step-by-step Claude instructions, sample-only mode handling
4. **Draft `.claude/settings.json`** — `allow` and `deny` glob patterns for Bash tool
5. **Define response templates** — at minimum: extraction success, extraction failure, missing fields list, checkpoint prompts, value deflection
6. **Decide sample-only Skill candidate vs. full release path** — this determines the scope of CLAUDE.md and the external messaging
7. **Write Skill testing checklist** — parallel to risky wording scan, covers Skill behavior not CLI behavior

Items 8–15 above can be resolved during drafting rather than before it.

---

*Created: 2026-06-16*
*Review source: `CLAUDE_SKILL_V01_PLAN_AFTER_LP.md` (main HEAD `59fea0c`)*
*No implementation code modified. Review document only.*
*Claude Skill リリース済みとは表記しません。*
*#19 remains open  #21 remains open  Issue #22 is completed  #48 remains open*
