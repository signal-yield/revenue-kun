# V0.2.0 PDF Ingestion Acceptance Report

**Project**: revenue-kun  
**Repository**: signal-yield/revenue-kun  
**Version**: v0.2.0  
**Report Date**: 2026-06-12  
**Branch**: main  
**Merge Commit**: 5babb80  

---

## 1. Summary

revenue-kun v0.2.0 は、text-based PDF 形式のレントロール表を対象とした PDF ingestion の限定対応を実施した。

本バージョンでは、PyMuPDF（`fitz`）による text-based PDF のテーブル抽出を前提とし、単純なレントロール表（1ページ、結合セルなし）の読み取りに限定して対応した。スキャンPDF・OCR・複数ページ結合・複雑な結合セル・ベンダー固有ヒューリスティック・PII マスキングは対象外とする。

本ツールの出力はすべて**収益試算値**であり、不動産鑑定評価・投資助言・法律助言ではない。

---

## 2. Scope

### 2.1 対応範囲

| 項目 | 内容 |
|------|------|
| 入力形式 | text-based PDF（PyMuPDF で直接テキスト抽出可能なもの） |
| テーブル構造 | 単純なレントロール表（1ページ、結合セルなし） |
| フィールド | canonical fields（room / rent / cam / status / area / use / notes）および alias mapping |
| 欠損処理 | 3層欠損処理（必須列不在→停止 / 必須セル不在→行除外 / 任意不在→0または記録） |
| 異常検知 | safe failure handling（silent failure の排除） |
| 出力 | `extraction_log.json`（`failure` / `failure_reason` 含む）、`missing_info.md`、xlsx |

### 2.2 非対応範囲（実装しない）

| 項目 | 理由・方針 |
|------|-----------|
| OCR | 対象外。将来 Issue 化 |
| スキャンPDF | 対象外。text-based に限定 |
| 複数ページテーブル結合 | 対象外。将来 Issue 化 |
| 複雑な結合セル | 対象外。将来 Issue 化 |
| ベンダー固有ヒューリスティック | 対象外。汎用実装に限定 |
| PII マスキング | 対象外。入力段階で除去済みを前提 |
| 鑑定評価・投資助言・法律助言 | 本ツールの提供範囲外 |

---

## 3. Issue / PR Summary

| Issue | PR | SHA | 内容 |
|-------|----|-----|------|
| #5 | — | — | Evaluate real-world rent roll PDF ingestion：実物PDF対応の可否評価・スコープ決定 |
| #6 | #9 | `878a0a5` | sub-header and repeated-header row exclusion：【1F区画】等の小見出し行・繰り返しヘッダー行を除外 |
| #7 | #10 | `5c83ad5` | column alias mapping：`_resolve_header_key()` 独立化 + 列名エイリアス拡充 |
| #8 | #11 | `5babb80` | safe failure handling for unreliable PDF extraction：3条件での safe failure + `failure_reason` + `extraction_log` on failure |

---

## 4. Acceptance Criteria

| # | Criterion | Status |
|---|-----------|--------|
| AC-1 | PDF 抽出時に小見出し行・繰り返しヘッダー行が除外される | PASS |
| AC-2 | column alias mapping により多様な列名表記を canonical key に正規化できる | PASS |
| AC-3 | unsafe PDF extraction が silent failure にならず safe failure（exit 2 + `failure_reason`）になる | PASS |
| AC-4 | CSV path が PDF ingestion の変更によって影響を受けていない | PASS |
| AC-5 | `failure_reason` が machine-readable な形式で `extraction_log.json` に記録される | PASS |
| AC-6 | `extraction_log.json` に `failure=true` および `failure_reason` が出力される | PASS |

---

## 5. Verification Results

### 5.1 pytest 結果

| タイミング | テスト数 | 結果 |
|-----------|---------|------|
| PR #9 merge 時点 | 42 | 42/42 PASSED |
| PR #10 merge 時点 | 80 | 80/80 PASSED |
| PR #11 merge 時点 | 84 | 84/84 PASSED |

### 5.2 Sample PDF 改善確認

| Sample | 項目 | 変更前 | 変更後 | 備考 |
|--------|------|--------|--------|------|
| Sample C | `extracted_units_count` | 8 | 6 | 小見出し行・繰り返しヘッダー行を正しく除外 |

### 5.3 main クリーン確認

```
Branch: main
HEAD: 5babb80
Status: nothing to commit, working tree clean
```

---

## 6. Safe Failure Conditions

以下の3条件のいずれかに該当する場合、`RentRollExtractionError` を発生させ exit 2 で終了する（silent failure を排除）。

| # | 条件 | `failure_reason` |
|---|------|-----------------|
| SF-1 | 全ページで `extract_table()` が `None` を返す | `"no_table_found"` |
| SF-2 | ヘッダーは認識できるがデータ行ゼロ | `"no_data_rows"` |
| SF-3 | 稼働区画が存在するが月額賃料がすべて非数値形式 | `"all_rent_non_numeric"` |

いずれの場合も `extraction_log.json` に `failure: true` と `failure_reason` が machine-readable な形式で記録される。

---

## 7. Release Judgment

| 項目 | 判定 |
|------|------|
| v0.2.0 core acceptance | **PASS** |
| リリース可否 | 保留（下記 Remaining Work 完了後にリリース可） |

**注意事項**

- 本バージョンを「実物PDF全面対応」と表現してはならない
- text-based PDF の単純なレントロール表に限定した対応であることを明示すること
- 出力は「収益試算値」であり、鑑定評価・投資助言・法律助言ではない

リリース前に以下の完了が必要：

1. README 更新（PDF ingestion の限定対応範囲・非対応範囲を明記）
2. CHANGELOG 更新（v0.2.0 変更内容）
3. version bump（`pyproject.toml` 等）
4. GitHub Release draft 作成
5. 必要に応じた追加サンプルでの確認

---

## 8. Remaining Work

| # | 作業 | 優先度 |
|---|------|--------|
| RW-1 | README 更新（PDF ingestion 対応範囲・非対応範囲の明記） | 高 |
| RW-2 | CHANGELOG 更新（v0.2.0 変更内容） | 高 |
| RW-3 | version bump（`pyproject.toml` 等） | 高 |
| RW-4 | GitHub Release draft 作成 | 高 |
| RW-5 | 追加サンプル（実物近似合成PDF）での確認 | 中 |
| RW-6 | OCR 対応を将来 Issue として登録 | 低 |
| RW-7 | 複数ページテーブル結合を将来 Issue として登録 | 低 |
| RW-8 | PII マスキングを将来 Issue として登録 | 低 |

---

## Appendix: Glossary

| 用語 | 定義 |
|------|------|
| 収益試算値 | 本ツールが直接還元法で算出する参考値。不動産鑑定評価額ではない |
| text-based PDF | PyMuPDF（fitz）でテキストを直接抽出可能なPDF。スキャンPDFは含まない |
| canonical key | 内部正規化後のフィールド名（room / rent / cam / status / area / use / notes） |
| safe failure | `RentRollExtractionError` を発生させ exit 2 + `failure_reason` を記録する異常終了 |
| silent failure | 空データや誤データを正常として返す望ましくない挙動 |
