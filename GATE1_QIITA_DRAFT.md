# Gate 1 — Qiita 記事草稿 v0.4.2

対象読者：不動産実務に関わるエンジニア・デベロッパー
キーワード：OSS, Python, Docker, 直接還元法, 収益還元, レントロール, Excel自動化

---

# レントロールPDF/CSVから直接還元法Excelを生成するDocker対応OSSを作った話

## はじめに

収益物件の簡易試算をするとき、こんな手作業が毎回発生していませんか？

- レントロール（賃料一覧）をPDFからExcelに転記する
- GPI（潜在総収入）→ EGI → NOI の計算式を毎回手組みする
- 水道代収入・駐車場収入をどこに入れるか毎回判断する
- 空室損失率や還元利回りを変えるたびにセルを手修正する

**revenue-kun（収益還元クン）** はこの転記・計算式組みを自動化するOSSです。  
レントロール（CSV または text-based PDF）を入力すると、直接還元法の収益試算Excelワークブックを出力します。

v0.4.2 では **Docker対応** と **optional income（水道代収入・駐車場収入・その他収入）対応** を追加しました。

> ⚠ 出力値は「収益試算値」であり、鑑定評価による「収益価格」ではありません。  
> 正式な価格判断・投資判断には不動産鑑定士等の専門家にご確認ください。

- GitHub: https://github.com/signal-yield/revenue-kun
- Release: https://github.com/signal-yield/revenue-kun/releases/tag/v0.4.2
- ライセンス: Apache 2.0

---

## revenue-kun とは

レントロールを入力とし、直接還元法に基づく収益試算Excelを出力するOSS CLIツールです。

**入力：**
- CSV（ダミーまたは自前のレントロール）
- text-based PDF（pdfplumber でテキスト抽出可能なもの）

**出力：**
- 直接還元法3シートExcel（`.xlsx`）
- `missing_info.md`（欠損項目一覧）
- `extraction_log.json`（抽出サマリー）

**設計方針：**
- 欠損は推測補完しない。不明な入力は `missing_info.md` に記録してユーザーに委ねる
- 空室損失率・還元利回り・費用率等の仮定値はユーザーが手入力。Claudeは値を提案しない
- 収益試算値（direct-capitalization revenue estimate）を出力するのみ。鑑定評価ではない

---

## v0.4.2 の更新点

### Docker対応

Python環境を構築せずにDockerで再現可能なCLI実行環境を提供します。

```bash
docker build -t revenue-kun .
docker run --rm revenue-kun  # → help 表示
```

**変更内容：**
- `Dockerfile`（python:3.12-slim, WORKDIR `/app`, デフォルトCMD `--help`）を追加
- `.dockerignore` を追加（`.git`, `.claude`, `output/`, `docs/`, `*.md` 等を除外）
- README に Docker使用例（bash + PowerShell）を追記

### optional income 対応

水道代収入・駐車場収入・その他収入を **optional income** として管理する仕組みを追加しました。

**設計の核心：「表示」と「GPI算入」を分離する**

| 動作 | 読み取りレントロールシート | 直接還元法_OER シート |
|------|----------------------|-----------------|
| opt-out（デフォルト） | 抽出値を**常時表示** | `=0`（「算入対象外」ラベル付き） |
| opt-in | 抽出値を表示 | レントロール年計をクロスシート参照 |

**assumptions.yaml の設定例：**

```yaml
# デフォルト（GPI に含めない）
optional_income:
  include_in_gpi: false
  columns: []

# 水道代収入を GPI に算入する場合
optional_income:
  include_in_gpi: true
  columns:
    - water   # 水道代収入
    # - parking      # 駐車場収入
    # - other_income # その他収入
```

**列名の設計：**
OERシートの列ラベルは「**水道代収入**」（収入サイド）。費用サイドの「水道光熱費」と混同しないよう明示的に分けています。

### ヘッダー行検出・サマリー行フィルタ改善

- ヘッダー行が1行目以外（2行目以降）にあるPDFに対応
- 「月額」「年額合計」「合　計」等のサマリー行をデータ行から除外

---

## Docker で動かす

### セットアップ

```bash
git clone https://github.com/signal-yield/revenue-kun.git
cd revenue-kun
docker build -t revenue-kun .
```

### バージョン確認

```bash
docker run --rm revenue-kun python src/main.py --version
# revenue-kun 0.4.2
```

### dry-run（抽出診断のみ・成果物生成なし）

```bash
# bash / macOS / Linux
docker run --rm \
  -v "$(pwd)/output:/app/output" \
  revenue-kun \
  python src/main.py \
    --assumptions assumptions.sample.yaml \
    --rent-roll-pdf data/sample_rentroll_simple.pdf \
    --output /app/output \
    --dry-run
```

```powershell
# PowerShell (Windows)
docker run --rm `
  -v "${PWD}/output:/app/output" `
  revenue-kun `
  python src/main.py `
    --assumptions assumptions.sample.yaml `
    --rent-roll-pdf data/sample_rentroll_simple.pdf `
    --output /app/output `
    --dry-run
```

**dry-run 出力例：**
```
================================================================
  収益還元クン v0.4.2  （Phase 2 / PDF抽出 / ドライラン）
  本ツールは不動産鑑定評価ではありません。...
================================================================
PDF抽出: sample_rentroll_simple.pdf から 5 区画を抽出しました（欠損セル 0 件）。
[抽出診断]
  入力形式       : PDF
  認識フィールド  : area, cam, rent, room, status, use
  抽出区画数     : 5
[ドライラン] 入力抽出と診断を完了しました。計算・成果物生成はスキップしました。
================================================================
```

### 通常実行（Excel出力）

```bash
docker run --rm \
  -v "$(pwd)/output:/app/output" \
  revenue-kun \
  python src/main.py \
    --assumptions assumptions.sample.yaml \
    --rent-roll-pdf data/sample_rentroll_simple.pdf \
    --output /app/output \
    --excel-output /app/output/direct_cap.xlsx
```

生成ファイルはホスト側の `./output/` に書き出されます。

### コンテナ内でテストを実行

```bash
docker run --rm revenue-kun python -m pytest -q
# 246 passed in 3.75s
```

---

## optional income の考え方

### なぜ opt-in 設計か

水道代収入・駐車場収入は物件によって扱いが異なります。

- 電気・水道代を実費精算する物件では「収入」として計上する
- 賃料に含めて管理する物件では別立て不要

デフォルト (`include_in_gpi: false`) では v0.4.1 以前と完全に後方互換。オプトインした場合のみ GPI に算入します。

### 内部モデルでの分離

```
RentRollUnit.月額水道代_円      ← 収入サイド（optional income）
Assumptions.opex["水道光熱費"]  ← 費用サイド（operating expense）
```

この2つは完全に別のフィールドで管理されており、内部計算でも混同しません。

### OER シートでの表示

opt-out 時の OER シート（直接還元法_OER）：

| セル | ラベル | 値 |
|------|--------|-----|
| D5 | 貸室賃料収入 | レントロール年計を参照 |
| D6 | 共益費収入 | レントロール年計を参照 |
| D7 | 水道代収入（算入対象外） | `=0` |
| D8 | 駐車場収入（算入対象外） | `=0` |
| D9 | その他収入（算入対象外） | `=0` |
| D10 | 総収入（年額） | `=SUM(E5:E9)` |

opt-in 時は D7〜D9 のラベルから「算入対象外」が消え、対応するセルがレントロール年計を参照します。

---

## テスト・検証結果

### テスト件数

```bash
python -m pytest -q
# 246 passed in 7.90s
```

### optional income テストカテゴリ（32件以上）

| カテゴリ | 内容 |
|---------|------|
| A. 後方互換 | opt-out 時のGPI不変・既存テスト通過 |
| B. opt-in | water/parking/other_income が正しくGPIに算入 |
| C. opt-out | デフォルトでGPIに含まれないこと |
| D. 収入・費用分離 | `月額水道代_円` と opex の水道光熱費が混同されないこと |
| E. PDF抽出 | ヘッダートークン認識・ExtractionReport への記録 |
| F. Excel出力 | 読み取りレントロールへの常時表示・OER formulaの切り替え |

### Docker検証結果

| ステップ | 結果 |
|---------|------|
| `docker build` | ✅ |
| `--version` | ✅ `revenue-kun 0.4.2` |
| `--dry-run` | ✅ 5区画・欠損0件 |
| `pytest -q` in container | ✅ 246 passed |
| `--excel-output` bind-mount | ✅ `direct_cap.xlsx` 生成確認 |

---

## 何を出力するか（Excelシート構成）

### シート① 直接還元法_OER

| セル | 項目 | 説明 |
|------|------|------|
| E5〜E9 | 各収入年額 | レントロールシートの年計を自動参照（or `=0`） |
| E10 | GPI | `=SUM(E5:E9)` |
| E13〜E17 | 仮定値 | **ユーザーが手入力**（空室損失率・貸倒損失率・経費率・資本的支出・還元利回り） |
| E20 | EGI | `=E10*(1-N(E13)-N(E14))` |
| E21 | 運営費用 | `=E20*N(E15)` |
| E22 | NOI | `=E20-E21` |
| E23 | 純収益 | `=E22-N(E16)` |
| E24 | 収益試算値 | `=IFERROR(E23/E17,"")` — 還元利回り未入力時は空白 |

`N()` 関数で空白をゼロとして扱うことで、仮定値の一部が未入力でも中間値まで自動表示されます。

### シート② 直接還元法‗費用詳細版

管理費・修繕費・損害保険料・固定資産税等を年額で入力する補助シート。経費率の妥当性確認用で、OERシートのNOIには直接連動しません。

### シート③ 読み取りレントロール

PDFから抽出した区画データ・月計・年計。空室区画には「ユーザーが賃料等を入力可能」と表示。optional income（水道代収入等）は opt-in/out に関わらず常時表示。

---

## 主要ライブラリ・構成

```
revenue-kun/
├── Dockerfile
├── .dockerignore
├── src/
│   ├── main.py                    # CLIエントリポイント
│   └── revenue_kun/
│       ├── pdf_extract.py         # pdfplumber でレントロール抽出
│       ├── noi.py                 # GPI / EGI / NOI 計算
│       ├── excel_output.py        # openpyxl で3シート生成
│       ├── config.py              # Assumptions + OptionalIncomeConfig
│       └── rent_roll.py           # RentRollUnit（optional income フィールド含む）
├── data/
│   ├── sample_rentroll_simple.pdf         # 合成サンプル（5区画・全入居）
│   ├── sample_rentroll_missing_values.pdf # 合成サンプル（5区画・1空室）
│   └── sample_rentroll_different_columns.pdf # 列名ゆれパターン
└── assumptions.sample.yaml        # 前提条件サンプル（optional_income 含む）
```

主要ライブラリ：
- **pdfplumber** — text-based PDFからテーブルを抽出
- **openpyxl** — Excelワークブック生成・数式埋め込み
- **PyYAML** — 前提条件ファイルの読み込み

---

## できないこと

| 制限 | 内容 |
|------|------|
| OCR・スキャンPDF | 対象外。text-based PDFのみ（pdfplumber）。将来の検討対象 |
| スマホ撮影PDF | 対象外。将来の検討対象 |
| qualifying real-world PDF評価 | 未完了（Issue #21 open）。**実務検証済みとは表記しません** |
| 欠損の自動補完 | 実施しません。欠損は `missing_info.md` に明記 |
| 鑑定評価・投資助言・税務助言 | 提供しません |
| Web UI | 現時点ではCLI版のみ |
| SaaS | 提供していません |

---

## 今後の構想

- **Issue #21**: qualifying real-world text-based PDFでの評価（open）
- **Issue #19**: OCR対応の検討（スコープ外・将来構想）
- Web UI化・スマホ撮影ワークフロー・SaaS化は将来の検討対象（現時点では未着手）

---

## 免責

> 本ツールは不動産鑑定評価ではありません。  
> 出力される金額は「収益試算値（direct-capitalization revenue estimate）」であり、鑑定評価による「収益価格」ではありません。  
> 欠損項目は推測補完せず、結果は前提条件に強く依存します。  
> 正式な価格判断・投資判断・法律的判断・税務上の判断が必要な場合は、不動産鑑定士・弁護士・税理士その他の専門家に確認してください。

---

フィードバック・Pull Request歓迎です。

https://github.com/signal-yield/revenue-kun
