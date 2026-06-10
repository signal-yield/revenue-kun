# revenue-kun（収益還元クン） v0.1

直接還元法による**収益試算ツール**（CLI）。レントロールと前提条件から
NOI（運営純収益）を算出し、**収益試算値**と感応度分析を出力します。

> ## ⚠️ 重要な注意
> - **本ツールは不動産鑑定評価ではありません。**
> - 出力される金額は **「収益試算値」** であり、鑑定評価による **「収益価格」ではありません。**
> - **欠損項目は推測補完しません。** 不明な入力は `missing_info.md` に記録され、計算からは除外されます（その旨が警告されます）。

---

## Phase 1（本バージョン）でできること

| # | 機能 | 実装 |
|---|------|------|
| 1 | ディレクトリ構成 | ✅ |
| 2 | `assumptions.sample.yaml` の読み込み | ✅ |
| 3 | ダミーのレントロールデータ | ✅ `data/dummy_rent_roll.csv` |
| 4 | NOI（運営純収益）計算 | ✅ |
| 5 | 直接還元法による収益試算値 | ✅ |
| 6 | 感応度分析（NOI × 還元利回り） | ✅ |
| 7 | `missing_info.md` 出力 | ✅ |
| 8 | `revenue_analysis.xlsx` 出力 | ✅ |
| 9 | `extraction_log.json` 出力 | ✅ |
| 10 | README 初稿 | ✅（本ファイル） |

## Phase 2（追加）でできること

完全合成データのレントロールPDFを入力し、賃料情報を抽出して NOI 計算に接続します。

| # | 機能 | 実装 |
|---|------|------|
| 1 | `sample_rentroll.pdf`（完全合成データ）の生成 | ✅ `scripts/make_sample_pdf.py` |
| 2 | PDFから抽出（部屋番号・用途・面積・月額賃料・共益費・入居/空室） | ✅ `src/revenue_kun/pdf_extract.py` |
| 3 | 抽出結果を Excel「レントロール」シートへ出力 | ✅ |
| 4 | 抽出できない項目を欠損として `missing_info.md` に出力 | ✅ |
| 5 | 欠損項目は推測補完しない | ✅ |
| 6 | `extraction_log.json` に抽出件数・欠損・使用PDF名を記録 | ✅ |
| 7 | 既存のNOI計算・感応度分析・免責・テストを壊さない | ✅（CSV経路は不変、13テスト緑） |

> **合成データの明示**：合成PDFの物件名・部屋・賃料・面積はすべて架空です。
> 実在の物件・借主・賃料とは一切関係ありません。一部セルは欠損検出の確認のため意図的に空欄です。

## Phase 2.1（追加）— PDF抽出の堅牢化

完全合成PDFを **3パターン** 用意し、抽出→NOI整理→収益試算値→`missing_info`/`extraction_log` のE2Eを安定化しました。

| パターン | ファイル | 内容 |
|---|---|---|
| simple | `sample_rentroll_simple.pdf` | 全区画稼働・全項目あり（欠損なしの基準） |
| missing_values | `sample_rentroll_missing_values.pdf` | 共益費・面積の欠損＋空室を含む |
| different_columns | `sample_rentroll_different_columns.pdf` | 列名ゆれ（`unit`/`rent`/`common_fee`/`area`/`status` 等） |

### E2E検算（`assumptions.sample.yaml` 前提）

| パターン | 抽出件数 | 欠損セル | missing_info件数 | GPI | NOI | 収益試算値 |
|---|--:|--:|--:|--:|--:|--:|
| simple | 5 | 0 | 2 | 26,016,000 | 17,215,200 | 360,337,778 |
| missing_values | 5 | 4 | 5 | 9,816,000 | 1,825,200 | 18,337,778 |
| different_columns | 3 | 0 | 2 | 21,780,000 | 13,191,000 | 270,911,111 |

> missing_info件数の内訳：いずれも assumptions 由来 2件（`建築時期`・`管理委託費`）を含みます。

### 欠損の扱い（補完しない方針）
欠損は3層で挙動が分かれます。**いずれの層でも推測補完は行いません。**

| 層 | 例 | 挙動 |
|---|---|---|
| **必須列が無い** | `部屋番号`/`月額賃料`/`入居状況` の列自体が無い | **計算停止**（`RentRollExtractionError`、終了コード 2） |
| **必須セルの値が欠損** | 稼働区画だが `月額賃料` が空欄 | **該当行を GPI から除外して計算継続**。`missing_info.md` と `extraction_log.json`（`missing_required_*`）に明記 |
| **任意項目の欠損** | `共益費`（→**0として算入**）/ `面積` / `用途` / 空室の想定賃料 | **0扱い or 記録のみで継続**。`missing_optional_*` に明記 |

> **必須セル欠損の設計判断（要件3）**：壊れた数字を避けるため、計算停止ではなく
> **「該当行を除外して継続し、欠損を明示」** を採用しています。
> （例：ダミーCSVの区画302は稼働だが賃料欄が空欄 → GPI から除外し、`missing_required_items` に記録。）

### extraction_log.json の固定スキーマ
毎回、以下のトップレベルキーを必ず出力します（Phase 2.1で固定）。

| キー | 内容 |
|---|---|
| `input_files` | 入力ファイル（assumptions / rent_roll） |
| `rent_roll_pdf` | 使用したレントロールPDF名（CSV経路では `null`） |
| `extracted_units_count` | 抽出した区画数 |
| `missing_required_count` / `missing_required_items` | 必須欠損の件数と明細 |
| `missing_optional_count` / `missing_optional_items` | 任意欠損の件数と明細 |
| `gpi` / `noi` / `indicated_value` | 潜在総収入 / 運営純収益 / 収益試算値（鑑定評価ではない） |
| `output_files` | 出力ファイル（missing_info / revenue_analysis / extraction_log） |
| `executed_at` | 実行時刻（ISO8601 / UTC） |

### 列名ゆれの最小対応
| 内部項目 | 認識する表記 |
|---|---|
| 部屋番号 | 部屋番号 / 号室 / 区画 / unit / room |
| 月額賃料 | 月額賃料 / 賃料 / rent |
| 共益費 | 共益費 / 管理費 / common_fee |
| 入居状況 | 入居状況 / 入居 / 空室 / 稼働 / status |
| 面積 | 面積 / area |

### スコープ外（今後）
- **複雑なPDF**：単純な罫線付き表（1ページ）のみ対象。複数ページ・結合セル・スキャン画像（OCR）は後回し。
- **Docker / DCF法 / 本物PDF対応 / 個人情報マスキング自動化**：未実装。

---

## ディレクトリ構成

```
revenue-kun/
├── README.md                  # 本ファイル
├── requirements.txt           # 依存ライブラリ（PyYAML, openpyxl, pdfplumber, reportlab）
├── pyproject.toml             # pytest 設定（src/ を import パスに追加）
├── assumptions.sample.yaml    # 前提条件（還元利回り・空室率・運営費用など）
├── data/
│   ├── dummy_rent_roll.csv               # ダミーのレントロール（CSV／Phase 1）
│   ├── sample_rentroll_simple.pdf            # 合成PDF: 欠損なし
│   ├── sample_rentroll_missing_values.pdf    # 合成PDF: 欠損あり
│   └── sample_rentroll_different_columns.pdf # 合成PDF: 列名ゆれ
├── .gitignore
├── schemas/
│   └── extraction_log.schema.json  # extraction_log.json の固定スキーマ（JSON Schema draft-07）
├── scripts/
│   └── make_sample_pdf.py     # 合成レントロールPDF生成スクリプト（--pattern 対応）
├── src/
│   ├── main.py                # エントリポイント（python src/main.py）
│   └── revenue_kun/           # 本体パッケージ
│       ├── __init__.py        # バージョン・免責文言・用語定義
│       ├── cli.py             # CLI ロジック
│       ├── config.py          # assumptions 読み込み＋入力バリデーション
│       ├── rent_roll.py       # レントロール読み込み（CSV）
│       ├── pdf_extract.py     # レントロールPDF抽出（Phase 2）
│       ├── sample_pdf.py      # 合成レントロールPDF生成（Phase 2）
│       ├── noi.py             # NOI 計算
│       ├── valuation.py       # 直接還元法（収益試算値）
│       ├── sensitivity.py     # 感応度分析
│       ├── missing.py         # 欠損検出（補完しない）
│       └── outputs.py         # md / xlsx / json 出力
├── tests/                     # pytest テスト（NOI / PDF抽出 / 免責 / 入力検証 / スキーマ）
└── output/                    # 実行時に生成される出力先（.gitignore 対象）
    ├── missing_info.md
    ├── revenue_analysis.xlsx
    └── extraction_log.json
```

---

## セットアップ

```powershell
# Python 3.11+ を想定
python -m pip install -r requirements.txt
```

## 実行（PowerShell）

```powershell
# Phase 1: ダミーCSVで実行
python src/main.py --assumptions assumptions.sample.yaml --output ./output

# Phase 2.1(1): 合成レントロールPDFを生成（3パターン。pattern はファイル名から自動推測）
python scripts/make_sample_pdf.py --output data/sample_rentroll_simple.pdf
python scripts/make_sample_pdf.py --output data/sample_rentroll_missing_values.pdf
python scripts/make_sample_pdf.py --output data/sample_rentroll_different_columns.pdf

# Phase 2.1(2): PDFから抽出して計算
python src/main.py --assumptions assumptions.sample.yaml --rent-roll-pdf data/sample_rentroll_simple.pdf --output ./output
python src/main.py --assumptions assumptions.sample.yaml --rent-roll-pdf data/sample_rentroll_missing_values.pdf --output ./output
python src/main.py --assumptions assumptions.sample.yaml --rent-roll-pdf data/sample_rentroll_different_columns.pdf --output ./output
```

> Windows のコンソールが文字化けする場合は `$env:PYTHONIOENCODING="utf-8"` を設定してください
> （出力ファイル自体は常に UTF-8 で正しく書き出されます）。

## テスト

```powershell
python -m pytest -q
```

---

## 出荷前チェックリスト（PowerShell）

GitHub公開・PR前に、以下が順に成功することを確認します。

```powershell
# 1. セットアップ
python -m pip install -r requirements.txt

# 2. CSV実行（Phase 1）
python src/main.py --assumptions assumptions.sample.yaml --output ./output

# 3. PDF生成（Phase 2.1）
python scripts/make_sample_pdf.py --output data/sample_rentroll_simple.pdf

# 4. PDF実行（Phase 2.1）
python src/main.py --assumptions assumptions.sample.yaml --rent-roll-pdf data/sample_rentroll_simple.pdf --output ./output

# 5. テスト
python -m pytest -q

# 6. 免責確認（出力に免責が入っていること）
Select-String -Path output/missing_info.md -Pattern "鑑定評価ではありません"

# 7. 「収益価格」が否定文脈以外に無いこと（ヒットは「収益価格ではありません」等のみ）
Get-ChildItem -Recurse -Include *.py,*.md,*.yaml,*.json |
  Select-String -Pattern "収益価格" |
  Where-Object { $_.Line -notmatch "収益価格.{0,4}ではありません|とは表記しない|収益価格.{0,2}ではない" }
# ↑ 何も出力されなければ OK（試算結果名として『収益価格』を使っていない）
```

| 確認項目 | 合格基準 |
|---|---|
| セットアップ | `pip install` がエラーなく完了 |
| CSV実行 | 収益試算値が表示され、3出力が生成される |
| PDF生成 | `data/sample_rentroll_simple.pdf` が生成される |
| PDF実行 | PDF抽出→収益試算値が表示される |
| pytest | 全件 passed |
| 免責確認 | 「不動産鑑定評価ではありません」が出力に含まれる |
| 用語確認 | 「収益価格」は否定文脈のみ（試算結果名は「収益試算値」） |

### 入力バリデーション（壊れた計算を継続しない）
`assumptions` は読み込み後に検証され、問題があれば**計算を中止**して `[前提条件エラー]`（終了コード 3）を返します。

| 項目 | 規則 |
|---|---|
| `還元利回り` (cap_rate) | 必須・**0 より大きい** |
| `空室損失率` (vacancy_rate) | 必須・**0〜1 の範囲** |
| `資本的支出` (capex) | 任意・指定時は **0 以上** |
| `運営費用` 各項目 | 任意（`null` 可）・指定時は **0 以上**（負の値は不可） |

> エラーは1件ずつではなく**すべてまとめて報告**します。`null`（任意項目の欠損）は補完せず許容し、`missing_info` に記録します。

### extraction_log のスキーマ検証
`schemas/extraction_log.schema.json`（JSON Schema draft-07）で固定スキーマを明文化し、
`tests/test_schema.py` が CSV/PDF 両経路の出力スキーマ適合を検証します。

---

## 計算ロジック

```
GPI（潜在総収入）   = Σ 稼働区画の (月額賃料 + 月額共益費) × 12
                      ※ 賃料が欠損した稼働区画・空室区画は補完せず除外（警告）
空室損失            = GPI × 空室損失率
EGI（有効総収入）   = GPI − 空室損失
運営費用合計        = Σ assumptions の運営費用（null 項目は算入せず警告）
NOI（運営純収益）   = EGI − 運営費用合計
純収益（還元対象）  = NOI − 資本的支出(CAPEX)
─────────────────────────────────────────────
収益試算値          = 純収益 ÷ 還元利回り
```

**感応度分析**は、NOI 変動率（行）× 還元利回りの増減（列）で
収益試算値のマトリクスを生成します。設定は `assumptions.sample.yaml` の `感応度分析` 節。

---

## 欠損の扱い（補完しない方針）

入力に存在しない項目は、**一切推測補完しません**。代わりに：

1. `missing_info.md` にカテゴリ別・出所付きで列挙
2. `extraction_log.json` の `missing_items` / 各フィールドの `status: "missing"` に記録
3. `revenue_analysis.xlsx` の「欠損項目」シート、および各計算の警告に反映

欠損が収益試算値を**過大/過小**に振らせうる場合は、その方向も併記します。

---

## 出力ファイル

| ファイル | 内容 |
|----------|------|
| `missing_info.md` | 欠損項目の一覧（区分・出所・計算への影響） |
| `revenue_analysis.xlsx` | サマリー / レントロール / NOI計算 / 感応度分析 / 欠損項目 の5シート |
| `extraction_log.json` | 固定スキーマのログ（入力/出力ファイル・PDF名・抽出件数・必須/任意欠損・GPI/NOI/収益試算値・実行時刻） |

---

## バージョン・ライセンス

**v0.1.0** — Apache License 2.0（Copyright 2026 km）

変更履歴は [CHANGELOG.md](CHANGELOG.md) を参照してください。
