# CHANGELOG

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
