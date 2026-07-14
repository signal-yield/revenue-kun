# revenue-kun — Security and Privacy / セキュリティとプライバシー

## 日本語

revenue-kunはユーザーのローカル環境で動作します。Local Web UIは127.0.0.1に限定して起動し、ホスティング型SaaSとして外部公開しません。入力されたCSVやPDFをrevenue-kunが外部サーバーへ送信することはありません。公開リポジトリには合成サンプルのみを含め、非公開PDF、実物件情報、APIキー、秘密情報を含めません。

### ネットワーク利用の説明

revenue-kun本体（CLI・Local Web UI・Excel生成ロジック）は、通常動作において外部APIや外部サーバーへ接続しません。この点は `src/revenue_kun/` のコードレベルでも確認しています（ネットワークリクエストを発行する処理は含まれていません）。

一方で、以下は「入力データの外部送信」とは区別される、導入時・開発時に通常発生するネットワーク通信です。
- 依存パッケージのインストール（`pip install`）
- Git clone / Plugin・Marketplaceの取得
- Dockerイメージのbuild

これらは開発ツールチェーンが必要とする通常の通信であり、revenue-kunがユーザーの入力データ（レントロールPDF・CSV）を外部へ送信する経路ではありません。

外部送信が一切ないことを完全に断定できるわけではなく、確認できた範囲（`src/revenue_kun/` 本体コードにネットワーク送信処理が存在しないこと）を報告します。

### 免責事項

本ツールの出力は収益試算値であり、不動産鑑定評価による収益価格ではありません。投資判断、法律判断、税務判断を提供するものではありません。

---

## English

revenue-kun runs in the user's local environment. Its Local Web UI binds only to 127.0.0.1 and is not exposed as a hosted SaaS. revenue-kun does not transmit uploaded CSV or PDF files to an external server. The public repository contains synthetic samples only and must not include private PDFs, real property data, API keys, or other secrets.

### Network usage

In normal operation, revenue-kun's core (CLI, Local Web UI, and Excel-generation logic) does not connect to any external API or server. This was confirmed at the code level (`src/revenue_kun/`) — no network-request code is present there.

The following are ordinary network activity that occurs at install/development time and is distinct from transmission of input data:
- Installing dependencies (`pip install`)
- Cloning the Git repository / fetching the plugin or marketplace
- Building the Docker image

These are normal toolchain operations, not a pathway by which revenue-kun sends a user's input data (rent-roll PDF/CSV) externally.

We cannot assert with absolute certainty that no external transmission ever occurs; this report is limited to what could be confirmed — namely, that no network-transmission code exists in `src/revenue_kun/` itself.

### Disclaimer

The output of this tool is a revenue estimate (収益試算値), not an appraised value (収益価格) under a formal real estate appraisal. It does not provide investment, legal, or tax advice.
