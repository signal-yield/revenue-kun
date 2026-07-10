# Gate 1 — note 短文草稿 v0.4.2

タイトル：レントロールPDF/CSVから直接還元法Excelを生成する revenue-kun v0.4.2 を公開しました

---

収益物件の簡易試算では、レントロールの転記作業と計算式の組み直しが毎回の手間になりがちです。PDFから賃料を手入力し、GPI・EGI・NOIの計算式をExcelで組み直し、還元利回りを変えるたびにセルを修正する。

**revenue-kun（収益還元クン）** は、この転記・計算式組みを自動化するOSSです。

レントロール（CSVまたはtext-based PDF）を入力すると、直接還元法の収益試算Excelワークブックを出力します。

---

**v0.4.2 では2つの機能を追加しました。**

ひとつ目は **Docker対応** です。Pythonの環境構築をしなくても、Dockerがあればすぐに動かせます。

```
docker build -t revenue-kun .
docker run --rm revenue-kun python src/main.py --version
```

ふたつ目は **optional income（付帯収入）対応** です。水道代収入・駐車場収入・その他収入を、assumptions.yamlで設定することでGPIに算入できるようになりました。デフォルトはGPIに含めないため、v0.4.1 以前と完全に後方互換です。

出力されるExcelは3シート構成です。直接還元法_OERシートでは、GPI・EGI・NOI・収益試算値が自動計算されます。空室損失率や還元利回りはユーザーが手入力します。ツールが値を提案することはありません。

---

**できないことも明確にしています。**

スキャンPDFや手書きPDF、スマホ撮影にはいまのところ対応していません（text-based PDFのみ）。qualifying real-world PDFでの評価も現在進行中のため、実務検証済みとは表記しません。出力はあくまで収益試算値であり、鑑定評価による収益価格ではありません。正式な価格判断・投資判断には不動産鑑定士等の専門家にご相談ください。

---

pytest は host・Docker ともに 246 passed。OSS（Apache 2.0）で公開しています。

GitHub: https://github.com/signal-yield/revenue-kun/releases/tag/v0.4.2
