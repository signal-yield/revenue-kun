# Issue #5 Sample Requirements

## Date
2026-06-12

## Purpose
Define synthetic-realistic rent roll PDF samples for evaluating real-world PDF ingestion in revenue-kun v0.2.0+.

---

## Privacy rule

Do not commit real rent roll PDFs or documents containing tenant names, company names,
room-level personal information, or confidential rent data.

Specifically prohibited from committing:
- Actual rent roll PDFs from any property
- Tenant names or corporate names (even partial)
- Room-level personally identifiable information
- Contract rents from real properties

---

## Local-only folder

Use `samples/private/` for local test PDFs.
This folder is listed in `.gitignore` and must never be committed.

```
samples/
└── private/          ← git-ignored, local only
    ├── sample_a_simple.pdf
    ├── sample_b_realistic.pdf
    └── sample_c_hard.pdf
```

Verify before any commit:
```powershell
git status   # samples/private/ must not appear
```

---

## Sample A: Simple text-based rent roll

- **Pages**: 1
- **Layout**: Single clean table with standard headers, no surrounding text decoration
- **Column names**: 部屋番号, 用途, 専有面積（㎡）, 月額賃料（円）, 月額共益費（円）, 入居状況
- **Content**: 5–8 units, mix of occupied and vacant, no blank cells
- **Font**: Standard Japanese text (not scanned / not image)
- **Purpose**: Establish baseline. Should behave identically to v0.1.0 synthetic PDFs.
- **Expected**: `pdfplumber` detects table. All required columns map via existing alias logic. **PASS**

---

## Sample B: Realistic layout variation

- **Pages**: 1
- **Layout**: Title block ("○○ビル レントロール 2026年6月") above the table; table starts at row 3+
- **Column names**: 号室, 用途区分, 面積, 賃料（税抜）, 管理費, 空室 / 入居
  - Note: "管理費" maps to `cam`, "号室" maps to `room`, "空室 / 入居" maps to `status` — all require alias matching
- **Content**: 6–10 units, 1–2 blank cells in optional columns (管理費 or 面積)
- **Font**: Standard Japanese text
- **Purpose**: Test alias coverage for real-world column name variants. Evaluate whether title rows confuse `extract_table()`.
- **Expected**: Table detected. Required columns map via alias logic (may need 1–2 alias additions). Optional blank cells logged. **PASS or PARTIAL**

---

## Sample C: Hard case

- **Pages**: 1
- **Layout**: Property summary block on the left, rent roll table on the right (two visual sections on one page); or table with a sub-header row ("1F区画" / "2F区画") that breaks column alignment
- **Column names**: Standard, but preceded by a merged-looking sub-header row
- **Content**: 4–6 units split across two groups with a blank separator row between them
- **Font**: Standard Japanese text (not scanned)
- **Purpose**: Determine whether `extract_table()` handles sub-headers, blank separator rows, or side-by-side layouts. Expected to expose limitations.
- **Expected**: Table may be partially detected or return misaligned rows. Required column mapping may fail on sub-header rows. **PARTIAL or FAIL**

---

## Evaluation output to record

For each sample, record the following in a local evaluation log (not committed):

| Check | Sample A | Sample B | Sample C |
|-------|:--------:|:--------:|:--------:|
| Table detected by `pdfplumber`? | | | |
| Required columns mapped? (room / status / rent) | | | |
| Optional columns mapped? (cam / area / use) | | | |
| Rents extracted with correct values? | | | |
| Missing fields logged in `missing_info.md`? | | | |
| Output (`missing_info.md`, xlsx) explainable? | | | |
| **Overall: PASS / PARTIAL / FAIL** | | | |

Additional notes to capture:
- Unrecognized column names (for alias addition candidates)
- Row count mismatch between PDF and extraction result
- Any `RentRollExtractionError` messages and their exact text
- Whether blank separator rows produce spurious unit entries

---

## Next step

1. Commit this document and the `.gitignore` update.
2. Create `samples/private/` locally (not committed).
3. Generate or place synthetic-realistic PDFs for Sample A, B, C under `samples/private/`.
4. Run `pdfplumber` extraction via CLI for each sample.
5. Fill in the evaluation table above locally.
6. Report results and update Issue #5 with findings.
7. Decide v0.2.0 scope based on results (see `ISSUE_5_REAL_WORLD_PDF_EVAL_PLAN.md` decision criteria).
