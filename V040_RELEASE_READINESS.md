# v0.4.0 Release Readiness

## Overview

`revenue-kun v0.4.0` は PDF ingestion hardening リリースです。
PDF 抽出範囲（text-based の単純な表形式 PDF）は v0.3.0 と変わらず、
status column の誤検出と summary row の混入を防ぐフィルタを追加しました。

> **重要**: 本ツールは不動産鑑定評価ではありません。出力される金額は「収益試算値」であり、
> 鑑定評価による「収益価格」ではありません。欠損項目は補完しません。

---

## What Is Ready

### Issue #29 — Japanese status column detection 強化（PR #31–#35）

- `_PERSON_NAME_DENY` により tenant-name 系列（`入居者名`, `テナント名`, `入居者` 等）を status から除外
- `_DATE_HEADER_DENY` により date-type 系列（`入居日`, `契約開始日`, `契約満了日` 等）を status から除外
- `ステータス` を status alias として認識（PR #31）
- `入居` alias は保持し deny-set で制御（PR #32–#33）

**受入確認**: `realistic_anonymized_001` — status col 13 (`ステータス`) ✓ / GPI 2,030,000 円/月 ✓

### Issue #30 — Total / summary row filtering（PR #37）

- `_SUMMARY_ROW_LABELS = {"合計", "小計", "総計", "計", "total", "subtotal"}` を追加
- `_is_non_data_row` の条件3: room フィールドをスペース除去・小文字化後に完全一致で照合
- 除外対象行は `ExtractionReport.notes` に記録

**受入確認**: `realistic_anonymized_001` — rows=20 / occupied=17 / vacant=3 / GPI=2,030,000 円/月 ✓

### Regression check — Synthetic samples 3件（PR #39）

| Sample ID | rows | occupied | vacant | monthly GPI | Regression? |
|-----------|------|----------|--------|-------------|-------------|
| sample-private-001 | 8 | 6 | 2 | 632,000 円 | None ✓ |
| sample-private-002 | 7 | 6 | 1 | 678,000 円 | None ✓ |
| sample-private-003 | 6 | 4 | 2 | 508,000 円 | None ✓ |

---

## What Is Not Ready

### Issue #21 — Qualifying real-world PDF evaluation（未完了）

v0.4.0 の時点で、qualifying real-world text-based rent roll PDF の評価が完了していません。

- `samples/private/` に存在する PDF はすべて synthetic（reportlab 生成）または realistic anonymized（非 qualifying）
- Issue #21 クローズ条件: 少なくとも1件の qualifying real-world PDF を `--dry-run` で私的に評価し、sanitized 結果を公開記録に残すこと
- この条件は v0.4.0 リリース時点で満たされていない

**Issue #21 はオープンのまま。**

---

## Known Limitations

### PDF 抽出スコープ（v0.2.0 以降変わらず）

| 制限 | 詳細 |
|------|------|
| text-based PDF 限定 | pdfplumber でテキスト抽出できる PDF のみ対応 |
| OCR 未対応 | スキャン PDF・画像 PDF は対象外 |
| 単純なレントロール表 | 複数ページ結合・複雑な結合セル・ページをまたぐ表は対象外 |
| vendor-specific heuristics なし | 根拠のない特定フォーマット専用ロジックは実装しない |
| PII マスキングなし | 実装しない。private PDF は `samples/private/`（gitignore 済み）のみで扱う |

### status column 検出の限界

- `_PERSON_NAME_DENY` / `_DATE_HEADER_DENY` は既知パターンのみカバー
- 日本語以外の未知ヘッダーは deny-set 外になる可能性がある
- 事前に `--dry-run` で column_map を確認することを推奨

### summary row 検出の限界

- 完全一致（スペース除去・小文字化後）のみ。未知ラベルは除外されない
- 除外されなかった集計行は通常の unit row として計算に入る

---

## Open Issues

| Issue | タイトル | 状態 | 依存 |
|-------|---------|------|------|
| #21 | Evaluate additional private rent roll PDF samples | open — qualifying PDF 待ち | — |
| #19 | Plan v0.4.0 additional real-world PDF evaluation | open | #21 |
| #22 | Summarize v0.4.0 PDF evaluation findings and decide next scope | open | #21 |

---

## Release Recommendation

**v0.4.0 を現在の状態でリリースすることを推奨します。**

- Issue #29 および Issue #30 の fix chain が完了し、acceptance criteria をすべて満足している
- `realistic_anonymized_001`（rows=20 / occupied=17 / vacant=3 / GPI=2,030,000 円/月）で正しい結果を確認
- synthetic 3件でリグレッションなし
- 残存する Issue #21 は real-world PDF の外部インプット待ちであり、実装上のブロッカーではない
- `V0.4.0 はデプロイ可能。ただし qualifying real-world PDF 評価は未完了` として扱う

**ただし以下を明示すること**:

- real-world PDF での実務検証は未完了（Issue #21 open）
- 実務投入前に `--dry-run` での事前確認を推奨
- 本ツールは鑑定評価ではなく収益試算ツールである

---

## Next Trigger

qualifying real-world text-based rent roll PDF が利用可能になった時点で:

1. `samples/private/` に配置（gitignore 済み）
2. sample_id を付与（例: `real_world_001`）
3. `PYTHONPATH=src python -m revenue_kun.cli --rent-roll-pdf <path> --assumptions assumptions.sample.yaml --dry-run` を実行
4. sanitized 結果を記録（sample_id・exit code・rows_extracted・column_map・GPI・occupied/vacant 件数・推奨アクションのみ）
5. PDF 本体・実ファイル名・物件名・テナント名・その他 PII はコミットしない
6. Issue #21 クローズ条件を満たせば Issue #21 → #22 → #19 の順でクローズを検討する

---

*作成: 2026-06-14 / 対象 main HEAD: 7f627ce (Merge PR #40)*