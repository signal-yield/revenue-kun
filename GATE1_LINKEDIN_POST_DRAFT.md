# Gate 1 — LinkedIn 投稿文草稿 v0.4.2

投稿タイミング：v0.4.2 公開後
Release URL: https://github.com/signal-yield/revenue-kun/releases/tag/v0.4.2
ライセンス: Apache License 2.0（Apache 2.0）

---

## 確定版（初回投稿・ChatGPT修正済み・投稿推奨）

案Aをベースに、技術説明を初回投稿向けに柔らかくした最終版。

```text
収益物件の試算作業で、こんな手間は発生していませんか？

・レントロールをPDFからExcelに転記する
・GPI → EGI → NOI の計算式を毎回組み直す
・水道代収入や駐車場収入をどこに入れるか悩む

revenue-kun v0.4.2 を公開しました。

レントロール（CSVまたはテキスト抽出可能なPDF）を入力すると、直接還元法の収益試算Excelワークブックを生成するOSS CLIです。

今回の v0.4.2 では、水道代収入・駐車場収入・その他収入を optional income として扱えるようにしました。

ポイントは、「読み取った金額を表示すること」と「GPIに算入すること」を分けた点です。

たとえば水道代収入は、レントロール上には表示されていても、常に賃料収入として扱うべきとは限りません。そのため、デフォルトではGPIに含めず、明示的に opt-in した場合のみ算入する設計にしています。

また、今回はDockerにも対応しました。

Python環境を個別に構築しなくても、再現可能なCLI実行環境として動かせます。ローカル環境・Docker環境の双方で pytest 246 passed、Docker内でのExcel出力も確認済みです。

重要な点として、本ツールの出力は「収益試算値」であり、鑑定評価による「収益価格」ではありません。

現時点ではCLI版であり、OCR・スキャンPDF・スマホ撮影・SaaS化は未実装です。これらは今後の検討対象です。

GitHub Release:
https://github.com/signal-yield/revenue-kun/releases/tag/v0.4.2

#不動産 #不動産テック #PropTech #収益物件 #OSS
```

---

## 案A（不動産実務寄り）

対象：不動産AM・仲介・鑑定士・収益物件実務者

---

収益物件の試算作業で、こんな手間は発生していませんか？

- レントロールをPDFからExcelに手入力する
- GPI → EGI → NOI の計算式を毎回組み直す
- 水道代収入や駐車場収入をどこに入れるか毎回悩む

**revenue-kun v0.4.2 を公開しました。**

レントロール（CSVまたはtext-based PDF）を入力すると、直接還元法の収益試算Excelワークブックを自動生成するOSSです。

**出力されるExcel（3シート構成）：**
- 直接還元法_OER：GPI / EGI / NOI / 収益試算値を自動計算。空室損失率・還元利回りはユーザーが手入力
- 費用詳細版：管理費・修繕費・損害保険料等を入力する補助シート
- 読み取りレントロール：PDFから抽出した区画データ・月計・年計

**v0.4.2 の追加点：**
- 水道代収入・駐車場収入・その他収入を optional income として管理（デフォルトはGPIに含めない。明示的にopt-inした場合のみGPIに算入）
- レントロールシートでは opt-out 時も抽出値を表示（「表示」と「GPI算入」を分離した設計）
- Dockerで再現可能なCLI実行環境

**重要なご注意：**
出力される金額は「収益試算値」であり、鑑定評価による「収益価格」ではありません。OCR・スキャンPDF・スマホ撮影には対応していません（text-based PDFのみ）。正式な価格判断・投資判断には不動産鑑定士等の専門家にご確認ください。

OSS（Apache 2.0）
GitHub: https://github.com/signal-yield/revenue-kun/releases/tag/v0.4.2

#不動産 #不動産テック #PropTech #収益物件 #OSS

---

## 案B（技術寄り）

対象：AIエンジニア・OSS関係者・不動産テック関係者

---

**revenue-kun v0.4.2 を公開しました。**

レントロールPDF/CSVから直接還元法Excelを生成する、Docker対応OSS CLIです。

**技術的な設計ポイント：**

**1. 「表示」と「GPI算入」の分離**
optional income（水道代収入・駐車場収入・その他収入）は、抽出された場合は常にレントロールシートに表示します。ただし、GPIへの算入は `assumptions.yaml` の `include_in_gpi: true` + `columns` 指定がある場合のみ。

```yaml
optional_income:
  include_in_gpi: true
  columns:
    - water
```

opt-out 時は OER シートの該当行が `=0`（「算入対象外」ラベル付き）になります。

**2. Docker対応**
```bash
docker build -t revenue-kun .
docker run --rm revenue-kun python src/main.py --version
# → revenue-kun 0.4.2

docker run --rm \
  -v "$(pwd)/output:/app/output" \
  revenue-kun \
  python src/main.py \
    --assumptions assumptions.sample.yaml \
    --rent-roll-pdf data/sample_rentroll_simple.pdf \
    --output /app/output \
    --excel-output /app/output/direct_cap.xlsx
```

**3. テスト体制**
pytest 246 passed（ホスト Python 3.11 + Docker python:3.12-slim の両方で確認済み）。optional income 用に 32+ テストを追加（A〜Fカテゴリ：後方互換・opt-in/out・表示分離・PDF抽出・Excel出力）。

**制限事項：**
OCR・スキャンPDF・スマホ撮影は対象外（text-based PDFのみ）。qualifying real-world PDF評価は未完了（Issue #21 open）。出力は収益試算値であり鑑定評価ではありません。

OSS（Apache 2.0）
GitHub: https://github.com/signal-yield/revenue-kun/releases/tag/v0.4.2

#Python #Docker #OSS #不動産テック #PropTech

---

## 案C（事業構想寄り）

対象：経営者・AI導入支援候補・不動産テック関係者

---

**収益試算エンジンの第一歩として、revenue-kun v0.4.2 を公開しました。**

不動産収益物件の簡易試算は、現場では今もExcelの手作業が中心です。レントロールの転記、GPI/EGI/NOIの計算式組み、还元利回りの変更ごとの手修正。

revenue-kun はこの「転記と計算式組み」をOSSとして自動化したCLIツールです。

**v0.4.2 の到達点：**

✅ レントロールCSV・text-based PDF → 直接還元法Excelを自動生成
✅ Dockerで再現可能なCLI実行環境（`docker build -t revenue-kun .` で即起動）
✅ 水道代収入・駐車場収入など付帯収入の optional income 対応
✅ pytest 246 passed（ホスト・Docker両環境で確認済み）

**設計思想：**
判断はユーザーが行います。空室損失率・還元利回り・費用率等の仮定値はユーザーが手入力し、ツールはその計算を補助するだけです。「AI が判断する」ツールではなく、「人間の判断を支援する」ツールを目指しています。

**今後の構想：**
現時点ではCLI版です。将来的にはWeb UI化、OCR対応、スマホ撮影ワークフローへの拡張も検討しています。ただし現時点ではスコープ外です。

出力は収益試算値であり、鑑定評価・投資助言ではありません。

OSS（Apache 2.0）
GitHub: https://github.com/signal-yield/revenue-kun/releases/tag/v0.4.2

#不動産テック #PropTech #AI #OSS #DX

---

## 投稿前確認

- 「AI が査定」「完全自動」「鑑定評価」「投資助言」の表現なし ✅
- 「実務検証済み」「OCR対応済み」「スキャンPDF対応済み」「スマホ撮影対応済み」なし ✅
- 「Claude Skill リリース済み」「SaaS提供中」なし ✅
- OCR / Web UI は「将来の検討対象」としてのみ言及 ✅
