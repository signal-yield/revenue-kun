# Gate 1 — X 投稿文草稿 v0.4.2

投稿タイミング：v0.4.2 公開後（GitHub Release 確認後）
Release URL: https://github.com/signal-yield/revenue-kun/releases/tag/v0.4.2

---

## 確定版（同日投稿・ChatGPT修正済み・投稿推奨）

```text
レントロール（CSV/テキスト抽出可能なPDF）から直接還元法Excelを生成する収益試算CLI、revenue-kun v0.4.2 を公開しました。

水道代収入などのoptional income対応、Docker対応、ローカル/Docker双方でpytest 246 passed。

出力は収益試算値であり、鑑定評価ではありません。
https://github.com/signal-yield/revenue-kun/releases/tag/v0.4.2

#不動産テック #OSS
```

---

## 投稿案 A（技術者向け）

```
revenue-kun v0.4.2 を公開しました。

レントロールPDF/CSVから直接還元法Excelを生成する、Docker対応OSS CLI。

🐳 Docker build / run / pytest すべて通過
💧 水道代収入など optional income の GPI opt-in 設計
✅ host / Docker ともに pytest 246 passed
📊 直接還元法3シートExcel（OER・費用詳細・レントロール）を自動生成

⚠ 収益試算値であり鑑定評価ではありません

→ https://github.com/signal-yield/revenue-kun/releases/tag/v0.4.2

#不動産テック #OSS #Docker #Python #PropTech
```

---

## 投稿案 B（不動産実務者向け）

```
レントロールの転記・計算式組みを自動化するOSS、revenue-kun v0.4.2 を公開しました。

CSV・text-based PDFを入力 → 直接還元法Excelを出力
・賃料・共益費・水道代収入などを自動集計
・GPI / EGI / NOI の計算式を3シートExcelに自動生成
・空室損失率・還元利回りはユーザーが手入力（Claudeは値を提案しません）

⚠ 出力は収益試算値。鑑定評価・投資助言ではありません

→ https://github.com/signal-yield/revenue-kun/releases/tag/v0.4.2

#不動産 #収益物件 #不動産テック #PropTech #OSS
```

---

## 投稿案 C（事業構想向け）

```
収益試算エンジンの基礎として revenue-kun v0.4.2 を公開しました。

今回の到達点：
・レントロールPDF/CSV → 直接還元法Excel生成
・Docker対応（再現可能なCLI実行環境）
・water / parking など optional income の opt-in 設計

現時点ではCLI版です。将来的にはWeb UI化、OCR対応、スマホ撮影ワークフローへの拡張も検討しています。

OSS（Apache 2.0）→ https://github.com/signal-yield/revenue-kun/releases/tag/v0.4.2

#不動産テック #PropTech #OSS #AI
```

---

## 注意事項（投稿前確認）

- 「AI が査定」「完全自動」「鑑定評価」「投資助言」の表現を含まないこと
- 「Claude Skill リリース済み」「Claude Skill 対応済み」は使わない
- 「実務検証済み」は使わない（#21 open）
- 「OCR対応済み」「スキャンPDF対応済み」「スマホ撮影対応済み」は使わない
- GitHub Release URL が正しいこと（v0.4.2）
