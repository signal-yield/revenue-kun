# DECISIONS

Design and scope decisions for revenue-kun.

---

## 2026-06-11 revenue-kun v0.1.0 close

- revenue-kun v0.1.0 is closed as a research/prototype CLI verified with synthetic PDF E2E checks.
- v0.1.0 does not support real-world rent roll PDFs, OCR, multi-page PDF merging, merged-cell layouts, or automated PII masking.
- Real-world rent roll PDF ingestion will be evaluated independently in Issue #5 for v0.2.0+.
- The v0.2.0 investigation should start from available or anonymized samples and should not wait for public reaction to v0.1.0.
- PR TIMES / note full launch timing will be decided around 2026-06-20, with 2026-06-25 as a target window if go.

---

## DEC-01: Claude Code project workflow — packaging mechanism

**Date**: 2026-06-16  
**Status**: Decided (PR #63 merged)  
**Supersedes**: conflated "Claude Skill" references in `CLAUDE_SKILL_V01_PLAN_AFTER_LP.md`

### Context

Planning (PR #61) and gap review (PR #62) both used "Claude Skill" to simultaneously
mean four distinct mechanisms: `CLAUDE.md`, `.claude/commands/`, `.claude/settings.json`,
and marketplace Skill. These have incompatible trigger models, scope, and authoring
conventions. Resolving this conflation was a blocking prerequisite for any implementation.

### Decision

**v0.1 target: Option C — Claude Code project workflow**

| File | Role | Trigger |
|------|------|---------|
| `CLAUDE.md` | Always-on operator instructions | Read at every Claude Code session start |
| `.claude/settings.json` | Bash permission allowlist / denylist | Enforced by Claude Code tool layer |
| `.claude/commands/revenue-kun.md` | `/revenue-kun` slash command | User-invoked explicitly |

External label: **「Claude Code project workflow」**  
Not: "Claude Skill released", "marketplace Claude Skill", "Claude Skill対応済み".

### Assumptions

- All three files are committed to the same repo as the CLI.
- Users access the workflow via Claude Code opened in this repo.
- Distribution is via `git clone`, not a Skill registry.

### Rejected alternatives

| Option | Reason |
|--------|--------|
| `CLAUDE.md` only | No user-facing trigger; ad-hoc sessions have no checkpoint enforcement |
| `.claude/commands/` only | No always-on safety baseline outside `/revenue-kun` flow |
| Marketplace Skill (Option D) | Registry infrastructure not confirmed; requires Issue #21 for honest claims |

### Exit conditions

- Marketplace Skill infrastructure confirmed publicly available AND Issue #21 complete
  → evaluate Option D as additive layer on top of Option C.
- Option C files prove insufficient during PR D validation
  → extend `.claude/settings.json` deny patterns; do not collapse files.

---

## DEC-02: Assumptions / cap-rate input pathway

**Date**: 2026-06-16  
**Status**: Decided  
**Required before**: PR B (`.claude/settings.json`) and PR C (`.claude/commands/revenue-kun.md`)

### Context

The CLI extracts unit-level rent data from PDFs but cannot extract cap rate, vacancy
rate, or expense ratio. These require professional judgment. A decision was needed on
where users enter these values and whether Claude may assist in choosing them.

### Decision

**Pathway: `直接還元法_OER` sheet, rows E9–E14 — user manual entry only**

- Cells E9–E14 are always empty in CLI output. The CLI does not fill them.
- Claude must **not** fill, suggest, estimate, or provide ranges or market norms
  for 還元利回り / 空室損失率 / 貸倒損失 / 経費率 / 資本的支出 / 管理費率,
  even framed as "rough estimate", "Tokyo market norm", or "sample data only".
- Claude may explain **which sheet, which rows** to fill. Claude must not imply
  **what value** to enter.

**Verbatim deflection response** (per CLAUDE.md §13):

> 「revenue-kun は還元利回り・空室損失率・経費率等の数値を提案しません。
> これらの仮定値は、担当の不動産鑑定士・ブローカー・税理士等の専門家、
> または公的統計・市場調査に基づいてユーザー自身がご判断ください。
> 数値の入力先は Excel ワークブックの各シートにあります（CLAUDE.md §12 Checkpoint B 参照）。」

**Completion criterion for PR C**: command file must include this deflection verbatim
and a Checkpoint B step listing E9–E14 as user-editable cells.

### Assumptions

- User has Excel or compatible software to open `.xlsx` output.
- Cap rate / vacancy inputs are determined by the user or their professional advisor,
  independently of revenue-kun and Claude.
- `assumptions.sample.yaml` defaults are used for CLI stdout calculations only;
  Claude does not assist users in choosing them.

### Rejected alternatives

| Alternative | Reason |
|-------------|--------|
| Claude suggests typical ranges (e.g., cap rate 4–6% for Tokyo) | Investment advice risk; users may treat suggestions as professional guidance |
| CLI auto-fills E9–E14 from `assumptions.sample.yaml` | Users may not notice default values; creates false appearance of validated assumptions |
| Claude enters values via Excel automation | Automates a judgment that must belong to the user or professional advisor |

### Exit conditions

- A qualified professional co-authors a public assumptions guide that revenue-kun
  links to as an external reference → Claude may link to that resource without
  itself providing values. (Providing values: never.)

---

## DEC-03: Release gate structure

**Date**: 2026-06-16  
**Status**: Decided

### Context

The original plan sequenced all external communication after Issue #21 (qualifying
real-world PDF evaluation), which blocks on PDF sample acquisition — an external
dependency that can take days or weeks. Meanwhile, D0 smoke test confirmed the full
synthetic-sample workflow runs correctly today. A sample-verified early release is
factually supportable without claims that depend on Issue #21.

### Decision

**Two-gate release model**

```
Gate 1 ── PR D (E2E sample validation) complete
│          ↓
│     Publish: GitHub repo, Cowork, README (if added)
│     Label:  "Claude Code project workflow — 合成サンプルで動作確認済み"
│     Claim:  sample-verified only; no real-world PDF claim
│
│     [Issue #21 / F runs in background — sample procurement Day 1]
│
Gate 2 ── Issue #21 (F) complete
           ↓
      Publish: PR TIMES / note / LinkedIn
      Claim:  boundary determined by F results; CLAUDE.md §16 applies
```

**Gate 1 allowed claims** (no Issue #21 required):
- Claude Code project workflow
- Claude-assisted workflow
- 合成サンプルデータで動作確認済み
- future Claude Skill candidate

**Gate 1 prohibited claims** (prohibited regardless of Issue #21):
- 実務検証済み / qualifying real-world PDF verified
- Claude Skill リリース済み / marketplace Claude Skill
- 鑑定評価 / 投資助言 / 法律助言 / 税務助言
- OCR 対応 / スキャン PDF 対応

**Gate 2 claim boundary** is determined by Issue #21 results and must not be
pre-announced before F completes.

### Assumptions

- Gate 1 is achievable after PR C + PR D without any Issue #21 dependency.
- Issue #21 sample PDF procurement runs in parallel from Day 1, not sequenced
  after Gate 1.
- Gate 2 claim scope may be narrower or broader than currently assumed.

### Rejected alternatives

| Alternative | Reason |
|-------------|--------|
| Single gate — all comms after Issue #21 | Sample procurement blocks all external comms; unnecessary opportunity cost |
| No gate — publish immediately | PR C + PR D must be authored and validated first |
| Gate 1 includes real-world PDF claims | Factually false while Issue #21 is open |

### Exit conditions

- Issue #21 completes before Gate 1 → collapse to single gate; no loss.
- Gate 1 reaction creates real-world PDF expectations → respond with explicit
  Issue #21 status; do not accelerate claims.

---

## D0: Dependency smoke test

**Date**: 2026-06-16  
**Status**: Passed (verified fact, not a decision)  
**Duration**: ~3 minutes (threshold was 60 minutes)

| Check | Result |
|-------|--------|
| `pdfplumber` 0.11.9 import | ✅ |
| `openpyxl` 3.1.5 import | ✅ |
| `--dry-run` × `sample_rentroll_simple.pdf` | ✅ exit 0 — 5 units, 0 missing |
| `--dry-run` × `sample_rentroll_missing_values.pdf` | ✅ exit 0 — 5 units, 4 missing |
| `--excel-output` full run × `sample_rentroll_simple.pdf` | ✅ exit 0 — 360,337,778円 |
| Excel: 3 sheets in correct order | ✅ |
| OER E2 formula (`=読み取りレントロール!C8`) | ✅ |
| OER E9 空室損失率 (user input cell) | ✅ None (correctly empty) |
| `pytest tests/` | ✅ 186 passed in 5.77s |

Fork condition not triggered. DEC-01 Option C proceeds without architectural change.

---

## Implementation sequence (current)

| Step | Artifact | Status |
|------|----------|--------|
| D0 | Dependency smoke test | ✅ Passed |
| A | `DECISIONS.md` entries DEC-01 / DEC-02 / DEC-03 + D0 | ✅ This PR |
| PR #64 | `CLAUDE.md` (always-on operator instructions) | ✅ Merged |
| PR B | `.claude/settings.json` (permission allowlist / denylist) | ⬜ Next |
| PR C | `.claude/commands/revenue-kun.md` (`/revenue-kun` command) | ⬜ After PR B |
| PR D | E2E sample validation (Gate 1 prerequisite) | ⬜ After PR C |
| **Gate 1** | Early publish — "Claude Code project workflow" | ⬜ After PR D |
| [parallel] | Issue #21 sample PDF procurement | ⬜ Day 1 background |
| F | Issue #21 — qualifying real-world PDF evaluation | ⬜ After procurement |
| **Gate 2** | PR TIMES / note / LinkedIn | ⬜ After F |
