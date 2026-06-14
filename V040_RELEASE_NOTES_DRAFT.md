# v0.4.0 — PDF ingestion hardening

## Release Highlights

v0.4.0 は PDF ingestion hardening リリースです。
PDF 抽出スコープ（text-based の単純な表形式 PDF）は v0.3.0 と変わらず、
status column 誤検出と summary row 混入を防ぐフィルタを追加しました。

> **重要**: 本ツールは不動産鑑定評価ではありません。出力される金額は「収益試算値」であり、
> 鑑定評価による「収益価格」ではありません。欠損項目は補完しません。

---

## Changes

### Japanese status column detection hardening（Issue #29 / PR #31–#35）

| 変更 | 詳細 |
|------|------|
| `ステータス` column の認識 | カタカナの `ステータス` ヘッダーを status alias として追加 |
| tenant-name 列の false positive 抑制 | `_PERSON_NAME_DENY = {"者名", "テナント名", "入居者"}` — `入居者名` / `契約者名` / `テナント名` / `入居者` 等が status に誤マッピングされるのを防ぐ |
| date-type 列の false positive 抑制 | `_DATE_HEADER_DENY = {"入居日", "開始日", "満了日", "契約日"}` — `入居日` / `契約開始日` / `契約満了日` 等が status に誤マッピングされるのを防ぐ |
| `入居` alias の保持 | `入居` alias は維持しつつ deny-set でスクリーニング（破壊的変更なし） |

**背景**: `入居者名`（tenant name col）が `入居` alias に先にマッチし、
status column（`ステータス`）が認識されない → 全ユニットの status が `None` → GPI = 0
という silent wrong result が発生していた。

### total / summary row filtering（Issue #30 / PR #37）

| 変更 | 詳細 |
|------|------|
| `_SUMMARY_ROW_LABELS` 追加 | `{"合計", "小計", "総計", "計", "total", "subtotal"}` |
| `_is_non_data_row` 条件3 追加 | room フィールドをスペース除去・小文字化後に完全一致で照合 |
| 除外行の記録 | `ExtractionReport.notes` に記録（`--dry-run` 出力に表示） |

除外対象となるラベル（スペース除去・小文字化後に完全一致）:
`合計`, `合　計`, `小計`, `総計`, `計`, `TOTAL`, `Total`, `total`, `Subtotal`, `SUBTOTAL`, `Sub total`, `subtotal`

部分一致しないため、`計画棟101` 等の正常な部屋番号は除外されません。

**背景**: `合 計` 行が unit row として抽出され、`rows_extracted = 21 / vacant = 4`
と誤カウントされていた。

---

## Verified Behavior

### realistic_anonymized_001（PR #36 / #38）

| 項目 | 値 |
|------|----|
| rows_extracted | 20（`合 計` 行1件除外済み） |
| occupied units | 17 |
| vacant units | 3 |
| monthly GPI | 2,030,000 円 |
| annual GPI | 24,360,000 円 |
| status column | col 13（`ステータス`） |
| column_map | room=0, area=3, rent=7, cam=8, status=13, notes=14 |
| exit code | 0 |
| summary row excluded | Yes — `合 計` を除外、notes に記録 |

### Synthetic samples regression check（PR #39）

| Sample ID | rows | occupied | vacant | monthly GPI | Regression? |
|-----------|------|----------|--------|-------------|-------------|
| sample-private-001 | 8 | 6 | 2 | 632,000 円 | None ✓ |
| sample-private-002 | 7 | 6 | 1 | 678,000 円 | None ✓ |
| sample-private-003 | 6 | 4 | 2 | 508,000 円 | None ✓ |

---

## Evaluation Status

### qualifying real-world PDF 評価: 未完了

- `samples/private/` に qualifying real-world text-based rent roll PDF は存在しない
- すべての評価済みサンプルは synthetic（reportlab 生成）または realistic anonymized
- Issue #21 はオープンのまま

**v0.4.0 では「real-world PDF 検証済み」とは表記しない。**

---

## Known Limitations

| 制限 | 詳細 |
|------|------|
| qualifying real-world PDF 評価未完了 | Issue #21 open — 実務検証済みとは言わない |
| text-based PDF 限定 | pdfplumber でテキスト抽出できる PDF のみ |
| OCR 未対応 | スキャン PDF・画像 PDF は対象外 |
| 単純なレントロール表に限定 | 複数ページ結合・複雑な結合セル・ページをまたぐ表は対象外 |
| vendor-specific heuristics なし | 根拠のない特定フォーマット専用ロジックは実装しない |
| PII マスキングなし | private PDF は `samples/private/`（gitignore 済み）のみで扱う |
| `_PERSON_NAME_DENY` / `_DATE_HEADER_DENY` は既知パターンのみ | 未知の日本語・英語ヘッダーは deny-set 外になる可能性あり |
| 鑑定評価・投資助言・法律助言ではない | 収益試算値を出力するツール。実務意思決定の根拠として単独使用しない |

---

## Open Issues

| Issue | タイトル | 状態 |
|-------|---------|------|
| [#21](https://github.com/signal-yield/revenue-kun/issues/21) | Evaluate additional private rent roll PDF samples | open — qualifying PDF 待ち |
| [#19](https://github.com/signal-yield/revenue-kun/issues/19) | Plan v0.4.0 additional real-world PDF evaluation | open — depends on #21 |
| [#22](https://github.com/signal-yield/revenue-kun/issues/22) | Summarize v0.4.0 PDF evaluation findings and decide next scope | open — depends on #21 |

---

## Release Recommendation

**v0.4.0 を PDF ingestion hardening マイルストーンとしてリリース可能。**

- Issue #29 / #30 の fix chain が完了し、acceptance criteria をすべて満足
- `realistic_anonymized_001` で正しい結果（rows=20 / occupied=17 / vacant=3 / GPI=2,030,000 円/月）を確認
- synthetic 3件でリグレッションなし

**ただし以下を明示すること**:

- qualifying real-world PDF での評価は未完了（Issue #21 open）
- 「real-world PDF 検証済み」とは表記しない
- 実務投入前に `--dry-run` で対象 PDF を事前確認することを推奨

---

## Next Trigger

qualifying real-world text-based rent roll PDF が `samples/private/` に追加された時点で:

1. sample_id を付与（例: `real_world_001`）
2. `PYTHONPATH=src python -m revenue_kun.cli --rent-roll-pdf <path> --assumptions assumptions.sample.yaml --dry-run` を実行
3. sanitized 結果を記録（sample_id・exit code・rows_extracted・column_map・GPI・occupied/vacant 件数・推奨アクションのみ）
4. PDF 本体・実ファイル名・物件名・テナント名・その他 PII はコミットしない
5. Issue #21 クローズ条件を満たせば Issue #21 → #22 → #19 の順でクローズを検討

---

## PRs Included in v0.4.0

| PR | タイトル | Issue |
|----|---------|-------|
| #31 | fix(issue-29): remove 入居 alias, add ステータス alias | #29 |
| #32 | fix(issue-29): restore 入居 alias with _PERSON_NAME_DENY | #29 |
| #33 | fix(issue-29): exclude 入居者 from status matching | #29 |
| #34 | docs(v040): re-evaluation after alias fix — 入居日 false positive found | #29 |
| #35 | fix(issue-29): add _DATE_HEADER_DENY to suppress date-type header false positives | #29 |
| #36 | docs(v040): re-evaluation after date header fix — Issue #29 criteria met | #29 |
| #37 | fix(issue-30): filter total and summary rows from rent roll PDF extraction | #30 |
| #38 | docs(v040): re-evaluation after summary row fix — Issue #30 criteria met | #30 |
| #39 | docs(v040): real-world PDF evaluation after Issue #29/#30 fixes | #21 |
| #40 | docs(v040): status snapshot after PR #39 | — |
| #41 | docs(v040): prepare release readiness notes | #19 #21 #22 |

---

*Draft created: 2026-06-14*
*Target main HEAD at draft creation: 66c9006*