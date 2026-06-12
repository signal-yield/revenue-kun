# CHANGELOG

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
