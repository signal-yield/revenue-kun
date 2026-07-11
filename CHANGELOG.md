# CHANGELOG

## [v0.5.1] — 2026-07-11

- Align internal version metadata (`src/revenue_kun/__init__.py`, `VERSION`) with the published release line.
- Update README and GitHub Pages to identify v0.5.1 as the current release.
- Update Docker Web UI verification status based on successful Docker Desktop build/run smoke tests.
- No functional changes to extraction, calculation, CLI, or Local Web UI behavior.

> Note: this entry covers only the v0.5.1 version/documentation alignment patch. Detailed changelog entries for v0.4.0 through v0.5.0 are not yet backfilled here and are tracked as separate follow-up work.

## [v0.3.0] — 2026-06-13

### 基本方針（変更なし）

- **本ツールは不動産鑑定評価ではありません。**
- 出力される金額はすべて **「収益試算値」** です。鑑定評価による **「収益価格」ではありません。**
- 欠損項目は推測補完しません。
- 本バージョンは **text-based PDF の単純なレントロール表への限定対応** です。実物PDF全面対応ではありません。
- **PDF抽出範囲は v0.2.0 から拡張していません。**

---

### Added

- CLI extraction diagnostics summary for CSV and limited text-based PDF inputs（Issue #13 / PR #16）
  - 入力形式（CSV / PDF）を表示
  - PDF 入力の場合、認識した canonical fields を表示
  - 抽出区画数を表示
  - safe failure 時は `[抽出診断]` を stderr に出力し、`failure_reason` を表示
- `--dry-run` mode：入力抽出と診断のみを実行し、計算・成果物生成を行わない（Issue #14 / PR #17）
  - CSV / text-based PDF 成功時: exit 0、output files を生成しない
  - PDF safe failure 時: failure_reason を表示し exit 2、`extraction_log.json` を生成しない
- CLI help test：`--dry-run` が `--help` 出力に含まれることを検証（Issue #15 / PR #18）

### Changed

- README を v0.3.0 向けに更新（Issue #15 / PR #18）：
  - v0.3.0 追加機能テーブルを追加
  - CSV / PDF 通常実行・dry-run の usage examples を追加
  - diagnostics summary の見方、safe failure の見方、`extraction_log.json` の見方を追加
  - 出荷前チェックリストに dry-run ステップを追加
- README の `failure_reason` 説明を実態に合わせて修正：短縮コード（`"no_table_found"` 等）ではなく日本語説明文であることを明記

### Not Changed / Out of Scope

- PDF抽出範囲の拡張なし
- OCR・スキャンPDF対応なし
- 複数ページテーブル結合なし
- 複雑な結合セル対応なし
- vendor-specific heuristics なし
- PII マスキングなし
- 鑑定評価・投資助言・法律助言ではない

### Test Results

| タイミング | テスト数 | 結果 |
|-----------|---------|------|
| PR #16 merge 時点 | 91 | 91/91 PASSED |
| PR #17 merge 時点 | 105 | 105/105 PASSED |
| PR #18 merge 時点 | 107 | 107/107 PASSED |

### References

- Issue #13 / PR #16 / SHA `df2ef0c`
- Issue #14 / PR #17 / SHA `8f37350`
- Issue #15 / PR #18 / SHA `4ef6381`

---

## [v0.2.0] — 2026-06-12

### 基本方針（変更なし）

- **本ツールは不動産鑑定評価ではありません。**
- 出力される金額はすべて **「収益試算値」** です。鑑定評価による **「収益価格」ではありません。**
- 欠損項目は推測補完しません。
- 本バージョンは **text-based PDF の単純なレントロール表への限定対応** です。実物PDF全面対応ではありません。

---

### Added

- text-based PDF（PyMuPDF で直接テキスト抽出可能なもの）の単純なレントロール表への ingestion 対応（Issue #5 評価結果に基づく限定対応）
- 列名エイリアス mapping の拡充：`_resolve_header_key()` を独立化し、`room` / `rent` / `cam` / `status` / `area` / `use` / `notes` 各 canonical key に対して日英の多様な表記を認識（Issue #7 / PR #10）
- `extraction_log.json` に safe failure 状態を記録：`failure: true` と machine-readable な `failure_reason` を出力（Issue #8 / PR #11）

### Changed

- PDF 抽出時に小見出し行（`【1F区画】` 等）および繰り返しヘッダー行を除外するよう変更（Issue #6 / PR #9）
- Sample C の `extracted_units_count` が 8 → 6 に改善（小見出し行・繰り返しヘッダー行の除外が正常に機能）
- README を v0.2.0 向けに更新：PDF ingestion 対応範囲・非対応範囲・safe failure conditions を明記

### Fixed

- 信頼性の低い PDF 抽出が silent failure になっていた問題を修正。以下3条件で `RentRollExtractionError`（exit 2）と `failure_reason` を記録する safe failure に変更（Issue #8 / PR #11）：
  - 全ページで `extract_table()` が `None` を返す場合（`"no_table_found"`）
  - ヘッダーは認識できるがデータ行がゼロの場合（`"no_data_rows"`）
  - 稼働区画が存在するが月額賃料がすべて非数値形式の場合（`"all_rent_non_numeric"`）

### Test Results

| タイミング | テスト数 | 結果 |
|-----------|---------|------|
| PR #9 merge 時点 | 42 | 42/42 PASSED |
| PR #10 merge 時点 | 80 | 80/80 PASSED |
| PR #11 merge 時点 | 84 | 84/84 PASSED |

### Limitations

以下は v0.2.0 においても意図的にスコープ外です。

- OCR（スキャン画像PDF）
- スキャンPDF全般
- 複数ページのテーブル結合
- 複雑な結合セルを含むPDF表
- ベンダー固有ヒューリスティック
- PII マスキングの自動化
- 鑑定評価・投資助言・法律助言（本ツールは収益試算値の算出補助であり、正式な価格判断・投資判断を代替しません）

### References

- Acceptance report: `V020_PDF_INGESTION_ACCEPTANCE_REPORT.md`
- Issue #6 / PR #9 / SHA `878a0a5`
- Issue #7 / PR #10 / SHA `5c83ad5`
- Issue #8 / PR #11 / SHA `5babb80`

---

## [v0.1.0] — 2026-06-10

### 基本方針

- **本ツールは不動産鑑定評価ではありません。**
- 出力される金額はすべて **「収益試算値」** です。鑑定評価による **「収益価格」ではありません。**
- 欠損項目は推測補完しません。欠損は `missing_info.md` と `extraction_log.json` に明記し、計算からは除外します。

---

### Phase 1 — 計算エンジンとCSV経路

- 直接還元法（NOI ÷ 還元利回り）による収益試算値の算出
- `assumptions.sample.yaml` からの前提条件読み込み
- ダミーCSV（`data/dummy_rent_roll.csv`）によるレントロール入力
- `missing_info.md` / `revenue_analysis.xlsx` / `extraction_log.json` の3出力
- 感応度分析（NOI 変動率 × 還元利回りマトリクス）
- 免責文言の全出力への組み込み

### Phase 2 — 合成PDFからの賃料抽出

- `reportlab` による完全合成レントロールPDF生成（`scripts/make_sample_pdf.py`）
- `pdfplumber` によるPDF表抽出 → NOI計算への接続
- `extraction_log.json` に抽出件数・欠損件数・PDF名を記録

### Phase 2.1 — PDF抽出の堅牢化

- 合成PDFを **3パターン** に拡充（simple / missing_values / different_columns）
- 列名ゆれへの対応（号室/unit/room、賃料/rent、共益費/common_fee 等）
- 欠損の3層分類を整備：必須列なし→計算停止 / 必須セル欠損→行除外・継続 / 任意欠損→0扱い・記録
- `extraction_log.json` の固定スキーマ化（12キー）と `schemas/extraction_log.schema.json` (JSON Schema draft-07) による検証

### Phase 2.2 — 出荷ハードニング

- `assumptions.yaml` 入力バリデーション（`cap_rate`・`vacancy_rate` の必須・範囲チェック、負値チェック）
- バリデーションエラーは全件まとめて報告し、計算を中止（終了コード 3）
- `requirements.txt` への上限バージョン追加と ASCII 化（Windows cp932 対応）
- `.gitignore` 追加
- `pytest` テスト 40件（入力検証・スキーマ適合・PDF抽出・E2E含む）

### Phase 2.3-a — CI

- GitHub Actions workflow（`.github/workflows/tests.yml`）を追加
- `push` / `pull_request` で Python 3.11 + `pytest -q` を自動実行

---

### v0.1.0 未対応（今後の候補）

以下は意図的にスコープ外です。

- DCF法（割引キャッシュフロー）
- OCR（スキャン画像PDF）
- 本物PDF（実在する物件・賃料データ）への対応
- 複数ページPDF
- 結合セルを含む複雑なPDF表
- 個人情報マスキングの自動化
- CI 以外の公開インフラ（Docker、パッケージ配布等）
