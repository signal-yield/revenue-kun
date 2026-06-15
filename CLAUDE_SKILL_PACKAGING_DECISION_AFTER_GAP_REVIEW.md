# Claude Skill Packaging Target Decision — After Gap Review

## 1. Purpose

Record the v0.1 packaging target decision for the Claude-assisted workflow version of
revenue-kun, made after reviewing `CLAUDE_SKILL_GAP_REVIEW_AFTER_PLAN.md`.

This document records **one decision**: which packaging mechanism to use for v0.1.
It does not implement any files. It does not modify Python code. It does not modify
`docs/index.html`, `README.md`, or any existing source file.

Claude Skill リリース済みとは表記しません。

---

## 2. Background

| Document | Status |
|----------|--------|
| `CLAUDE_SKILL_V01_PLAN_AFTER_LP.md` | Merged (PR #61) — defined scope, constraints, 17 sections |
| `CLAUDE_SKILL_GAP_REVIEW_AFTER_PLAN.md` | Merged (PR #62) — identified 15 gaps, 24 sections |
| This document | Records packaging target decision before implementation begins |

The gap review identified a critical blocker in §2 (Critical Gap):

> "The plan uses 'Claude Skill' to mean all of the following simultaneously:
> CLAUDE.md, `.claude/commands/<name>.md`, and a marketplace Skill.
> These have different scope, trigger model, distribution model, and capability
> requirements. Writing one as if it is the other will produce a nonfunctional result."

This document resolves that blocker by naming the v0.1 target.

---

## 3. Problem: Packaging Mechanism Conflation

The planning document treated four distinct mechanisms as a single concept:

| Mechanism | Trigger model | Scope | Distribution |
|-----------|--------------|-------|-------------|
| **`CLAUDE.md`** | Always-on; read at every session start | Project-local | Committed to repo |
| **`.claude/commands/<name>.md`** | User-invoked; `/revenue-kun` in chat | Project-local | Committed to repo |
| **`.claude/settings.json`** | Always-on; enforces tool permissions | Project-local | Committed to repo |
| **Marketplace Claude Skill** | Installed from Skill registry | Cross-project | Published to external registry |

Each mechanism has different:
- Authoring format and required content structure
- When Claude sees and acts on it
- How users invoke it
- How it is distributed to other users

Using one mechanism's authoring conventions for another produces a nonfunctional result.
Before any file can be written, one mechanism (or a specific combination) must be chosen.

---

## 4. Options Considered

### Option A — CLAUDE.md only (operator instructions, always-on)

**What it is**: A `CLAUDE.md` file in the repo root that Claude reads at session start.
Defines Claude's role, permitted operations, checkpoint protocols, and prohibited wording.
Active for any Claude Code session opened in this repository.

**Pros**:
- Simplest to author and test
- Always active; user does not need to invoke a special command
- Well-supported in Claude Code
- Low authoring effort; appropriate for v0.1

**Cons**:
- No user-facing command trigger (cannot type `/revenue-kun`)
- Applies to every Claude Code session in this repo, not only revenue-kun workflow sessions
- Does not package cleanly for distribution outside the repo

---

### Option B — `.claude/commands/revenue-kun.md` only (slash command)

**What it is**: A custom slash command file that the user triggers with `/revenue-kun`.
Contains step-by-step workflow instructions Claude follows when invoked.

**Pros**:
- Explicit user intent signal (user types `/revenue-kun` to start)
- Workflow steps are contained in one file
- Possible to version independently of CLAUDE.md

**Cons**:
- Does not enforce baseline safety constraints for ad-hoc Claude interactions in the repo
- Without CLAUDE.md, Claude has no always-on role declaration or prohibited-wording enforcement
- A user working outside `/revenue-kun` receives no safety constraints

---

### Option C — CLAUDE.md + `.claude/commands/revenue-kun.md` + `.claude/settings.json`

**What it is**: All three project-local files together.

- `CLAUDE.md`: always-on role declaration, DISCLAIMER rule, prohibited wording enforcement,
  baseline safety constraints for any Claude session in this repo
- `.claude/commands/revenue-kun.md`: explicit step-by-step workflow triggered by `/revenue-kun`
- `.claude/settings.json`: Bash tool permission allowlist / denylist (hard enforcement)

**Pros**:
- Comprehensive: safety constraints always on (CLAUDE.md), workflow on demand (command file),
  permissions enforced in settings (not just policy)
- Gap review §4 and §6 both require settings.json for permission enforcement
- Gap review §4 requires CLAUDE.md for role declaration and DISCLAIMER binding
- Mirrors the "recommended" choice in plan §14

**Cons**:
- Three files to author instead of one
- More surface area for errors
- Slightly higher authoring effort

---

### Option D — Marketplace Claude Skill packaging

**What it is**: A packaged, distributable Skill descriptor published to an external registry.

**Pros**:
- Widest potential distribution
- User-friendly installation

**Cons**:
- Requires Skill marketplace infrastructure that is not publicly available at this stage
- Requires qualifying real-world PDF evaluation to be complete before honest external claims
  (Issue #21 open)
- Highest authoring and release management effort
- Not appropriate until Options A–C are stable and tested

---

## 5. Decision

**v0.1 packaging target: Claude Code project workflow (Option C)**

> revenue-kun v0.1 Claude-assisted workflow will be packaged as three project-local files:
> `CLAUDE.md`, `.claude/settings.json`, and `.claude/commands/revenue-kun.md`.

This combination is called a **Claude Code project workflow** in external messaging.
It is **not** called a "Claude Skill release" or "marketplace Claude Skill."

Option D (marketplace Skill) is explicitly deferred. It is not the v0.1 target.

---

## 6. Rationale

### Why Option C over A or B alone

`CLAUDE.md` alone (Option A) enforces safety constraints but provides no explicit
user-facing workflow. A user would have to know to ask Claude to "run the revenue-kun
workflow" in natural language — no reliable trigger.

`.claude/commands/revenue-kun.md` alone (Option B) provides the trigger but leaves
Claude with no always-on safety constraints for ad-hoc interactions. A user who asks
Claude a question about the repo outside the `/revenue-kun` flow receives no role
declaration or prohibited-wording enforcement.

Option C provides both: always-on safety baseline and explicit workflow trigger.
The gap review §4 (CLAUDE.md requirements) and §6 (settings.json requirements)
both identify needs that can only be satisfied by their respective files.

### Why not Option D

The gap review §15 (Release Criteria) and plan §15 both require qualifying real-world
PDF evaluation (Issue #21) before the project can be described as a Claude Skill release.
Issue #21 remains open. Option D cannot be chosen until it is complete.

Additionally, marketplace Skill infrastructure is not confirmed publicly available at this stage.
Committing to marketplace packaging now would require claims that cannot yet be substantiated.

### Why "Claude Code project workflow" as the external label

This label:
- Accurately describes what the three files are (project-local, Claude Code context)
- Does not imply marketplace distribution or Skill registry listing
- Does not imply real-world PDF verification or appraisal
- Allows honest communication about what is implemented

---

## 7. Scope of v0.1

The v0.1 Claude Code project workflow will cover:

| In scope | Notes |
|----------|-------|
| `CLAUDE.md` — always-on role declaration | Defines Claude's role, DISCLAIMER rule, prohibited wording, baseline constraints |
| `.claude/settings.json` — permission enforcement | Bash tool allowlist / denylist; maps allowed commands from gap review §19 |
| `.claude/commands/revenue-kun.md` — `/revenue-kun` command | Step-by-step workflow; dry-run → Checkpoint A → full run → Checkpoint B |
| Sample-only operation | Uses `data/sample_rentroll_simple.pdf` and `data/sample_rentroll_missing_values.pdf` |
| Checkpoint A / B / C protocols | As defined in gap review §21 |
| Value deflection protocol | As defined in gap review §11 |
| DISCLAIMER reproduction rule | As defined in gap review §4.2 |
| Prohibited wording enforcement | Full list from gap review §22 |

---

## 8. Out of Scope for v0.1

| Out of scope | Reason |
|-------------|--------|
| Marketplace Claude Skill packaging | Requires Issue #21 completion and registry infrastructure |
| qualifying real-world PDF operation | Issue #21 open |
| OCR / scanned PDF support | Not implemented; explicitly out of scope |
| Claude filling in missing values | By design: user must fill in Excel manually |
| Claude recommending cap rates, vacancy rates, or expense ratios | Prohibited; value deflection rule applies |
| GUI / Web UI integration | Not implemented |
| Changes to `src/` Python code | No Python code is modified by Skill packaging |
| Changes to `docs/index.html` | LP is not modified by this decision |
| Changes to `README.md` | README update may follow separately after files are authored |
| Claude Skill marketplace listing | Deferred; not v0.1 |

---

## 9. Planned Future Files

The following three files are **planned** for implementation in subsequent PRs.
They are **not created in this PR**.

### 9.1 `CLAUDE.md`

Location: repo root  
Trigger: automatically read at every Claude Code session start  
Required content per gap review §4:

- Role declaration (Claude's role is workflow assistant, not appraiser or advisor)
- DISCLAIMER verbatim reproduction rule (must reproduce before any numerical summary)
- First-call rule (always `--dry-run` before full run)
- Checkpoint A protocol (what to output; what constitutes confirmation)
- Checkpoint B protocol (what to output; list of cells; must not fill in)
- Checkpoint C protocol (required disclosure text; appears with every value reference)
- Value deflection rule (no ranges, examples, or typical values for cap rate / vacancy / expenses)
- OCR deflection rule (state out of scope; do not suggest workarounds)
- Path validation rule (validate path exists, correct extension, within project directory)
- File scope restriction (which files Claude may read; which it must not modify)
- Error stop rule (surface message; do not retry; do not generate synthetic values)
- Prohibited wording list verbatim (from gap review §22)

### 9.2 `.claude/settings.json`

Location: `.claude/settings.json`  
Trigger: read by Claude Code at session start; enforces tool permissions  
Required content per gap review §6:

```json
{
  "permissions": {
    "allow": [
      "Bash(python src/main.py --dry-run*)",
      "Bash(python src/main.py --excel-output*)",
      "Bash(python src/main.py --version)",
      "Bash(python src/main.py --help)",
      "Bash(python -m pytest tests/)"
    ],
    "deny": [
      "Bash(pip*)",
      "Bash(*rm *)",
      "Bash(git push*)",
      "Bash(git commit*)",
      "Bash(git reset*)",
      "Bash(git checkout*)"
    ]
  }
}
```

Exact patterns to be finalized during authoring. The above is illustrative.

### 9.3 `.claude/commands/revenue-kun.md`

Location: `.claude/commands/revenue-kun.md`  
Trigger: user types `/revenue-kun` in Claude Code  
Required content per gap review §5:

- Argument specification (PDF path, assumptions path, output path)
- Step-by-step Claude instructions (not prose workflow — explicit directives)
- Sample-only mode behavior until Issue #21 is complete
- Checkpoint A trigger and required output
- Checkpoint B trigger and required output
- Checkpoint C disclosure trigger
- Value deflection trigger
- Error handling steps

---

## 10. Safety Implications of This Decision

### What Option C adds that the current repo does not have

Currently, any Claude Code session in this repo operates with no role declaration,
no prohibited-wording enforcement, and no Bash permission constraints.
After Option C files are authored and committed:

- `CLAUDE.md` constrains every Claude session in this repo from session start
- `.claude/settings.json` enforces Bash command permissions at the tool level (not just policy)
- `.claude/commands/revenue-kun.md` provides a structured, checkpoint-gated workflow

### What Option C does not change

- Python CLI behavior is unchanged
- Excel output logic is unchanged
- No appraisal or investment advice is added
- No OCR support is added
- No real-world PDF verification is claimed

### Sample-only constraint

Until Issue #21 is complete, the command file (`revenue-kun.md`) must refuse to process
user-provided PDFs that are not among the two synthetic bundled samples. This constraint
must be stated explicitly in the command file and enforced by Claude's response logic.
It is not enforced at the Bash level (the CLI accepts any valid PDF path);
enforcement is in the Claude instruction layer.

---

## 11. External Messaging Rules

### Allowed wording after v0.1 files are authored and committed

| Context | Allowed wording |
|---------|----------------|
| README badge / LP | `Claude Code project workflow` |
| SNS / PR TIMES | 「revenue-kun: Claude Code project workflow として動作する研究・検証支援 CLI」 |
| Presentations | "Claude-assisted workflow — Claude Code project workflow packaging" |
| Issue / PR descriptions | "Claude Code project workflow (CLAUDE.md + settings.json + custom command)" |

### Prohibited wording (at all times, including after v0.1 is authored)

| Prohibited | Reason |
|-----------|--------|
| Claude Skill released / Claude Skill対応済み | Marketplace Skill not released |
| Claude Skill版を公開しました | Not published to any Skill registry |
| marketplace Claude Skill | Not a marketplace artifact |
| fully automated valuation / 完全自動査定 | User must fill in Excel and consult professionals |
| appraisal / 鑑定評価（肯定文脈） | Out of scope |
| investment advice / 投資助言 | Out of scope |
| legal advice / 法律助言 | Out of scope |
| tax advice / 税務助言 | Out of scope |
| OCR / scanned PDF support | Not implemented |
| real-world PDF verified | Issue #21 not complete |
| 実務検証済み | Issue #21 not complete |

### Status badge on `docs/index.html`

The current LP badge reads `main`. This badge must not be changed to `Claude Skill`
or `Claude Code workflow` until the three files (§9.1–§9.3) are authored, reviewed,
tested, and confirmed to comply with all checkpoint and prohibited-wording requirements.

---

## 12. Release Criteria Before Using "Claude Skill version"

This section replaces plan §15 with updated criteria reflecting the Option C decision:

| Criterion | Status |
|-----------|--------|
| Packaging mechanism decided (this document) | ✅ Decided — Option C (Claude Code project workflow) |
| `CLAUDE.md` authored with all §9.1 required content | ❌ Not started |
| `.claude/settings.json` authored with allow/deny patterns | ❌ Not started |
| `.claude/commands/revenue-kun.md` authored with arguments, steps, checkpoints | ❌ Not started |
| Sample-only validation flow passes end-to-end (§13 of plan) | ❌ Not validated |
| All prohibited wording absent from all three files | ❌ Not authored yet |
| Human review checkpoints A/B/C present and protocol-compliant | ❌ Not authored yet |
| Value deflection protocol tested in session | ❌ Not tested |
| DISCLAIMER verbatim reproduction tested in session | ❌ Not tested |
| Risky wording scan passes on all three new files | ❌ Not authored yet |
| Test suite passes at time of workflow release | ❌ (pending authoring) |
| External messaging reviewed against §11 of this document | ❌ Not reviewed |

**No criteria above are met for the three planned files.**
Packaging mechanism is decided (criterion 1 complete). Twelve criteria remain.

Note: qualifying real-world PDF evaluation (Issue #21) is **not** a prerequisite for
committing the three files. It **is** a prerequisite for:
- Removing the sample-only constraint from `.claude/commands/revenue-kun.md`
- External messaging claiming real-world PDF support
- Using the label "Claude Skill version" in external communications

---

## 13. Next Implementation PRs

| PR | Content | Prerequisite |
|----|---------|-------------|
| PR A | `CLAUDE.md` draft (role declaration, DISCLAIMER rule, checkpoint protocols, prohibited wording) | This document merged |
| PR B | `.claude/settings.json` (allow/deny patterns matching gap review §19–20) | PR A merged |
| PR C | `.claude/commands/revenue-kun.md` (arguments, steps, Checkpoint A/B/C, value deflection) | PR A and PR B merged |
| PR D | Sample-only end-to-end validation (session test, wording scan of session transcript) | PR C merged |
| PR E | README update acknowledging Claude Code project workflow (no Skill release claim) | PR D complete |
| (future) | Remove sample-only constraint + qualifying real-world PDF claim | Issue #21 complete |
| (future) | Marketplace Claude Skill packaging | Option C stable + Issue #21 complete |

Each PR in the sequence above produces a reviewable diff of exactly one new file
(plus tests or documentation as appropriate). No PR combines CLAUDE.md and settings.json.

---

*Created: 2026-06-16*
*Based on: main HEAD `894eebe` (PR #62 merged — Claude Skill gap review)*
*References: `CLAUDE_SKILL_V01_PLAN_AFTER_LP.md`, `CLAUDE_SKILL_GAP_REVIEW_AFTER_PLAN.md`*
*No implementation code modified. Decision document only.*
*Claude Skill リリース済みとは表記しません。*
*#19 remains open  #21 remains open  Issue #22 is completed  #48 remains open*
