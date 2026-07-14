# revenue-kun（収益還元クン） v0.5.2

**revenue-kun** は、不動産のレントロール（賃料一覧表）から、直接還元法による収益試算Excelを生成するOSSです。

CSVまたはテキスト抽出可能なPDFのレントロールをアップロードすると、抽出結果をプレビューしたうえで、直接還元法の収益試算ワークブック（`direct_cap.xlsx`）を生成・ダウンロードできます。判断が必要な前提条件（空室損失率・還元利回り等）はアプリ側では入力させず、生成後のExcel上で利用者が入力します。

利用形態は **Local Web UI**・**CLI**・**Docker** の3通りで、いずれもローカル実行専用です。ホスティング型SaaSではありません。Claude Code / Codex のSkillからLocal Web UIを起動することもできます。

ライセンスは Apache License 2.0 です。

---

## 主な機能

- レントロールPDF／CSVのアップロード
- 抽出結果のプレビュー（区画数・稼働／空室・欠損情報）
- 賃料・共益費・水道代収入・駐車場収入・その他収入のGPI（潜在総収入）への自動反映
- `直接還元法_OER` と `直接還元法‗費用詳細版` の同時出力
- `読み取りレントロール` シートの出力
- 前提条件（空室損失率・還元利回り等）はExcel上で利用者が入力
- 計算過程をセル単位で確認可能（数式は隠蔽しない）

## 出力Excel

生成される `direct_cap.xlsx` は次の3シート構成です。

| シート名 | 内容 |
|---|---|
| `直接還元法_OER` | 運営費用をOER（運営費用率）で概算する方式 |
| `直接還元法‗費用詳細版` | 個別運営費用を積み上げる方式 |
| `読み取りレントロール` | 抽出したレントロール（区画・賃料・付帯収入・月計・年計） |

`直接還元法_OER` と `直接還元法‗費用詳細版` は完全に独立して計算されます。一方の入力値・計算結果を他方が参照することはありません。どちらを使うか（あるいは両方使うか）は、Excelを受け取った利用者が判断します。

空室損失率・貸倒損失率・採用OER（または個別運営費用）・資本的支出・還元利回りは、アプリでは入力させず、Excel出力後に利用者が各シートへ入力します。出力される金額は「**収益試算値**」であり、鑑定評価による「収益価格」ではありません。

## 対応入力／非対応入力

**対応**

- CSV
- テキスト抽出可能なPDF

**非対応**

- OCR
- スキャンPDF
- スマートフォン撮影画像
- 複雑な結合セル
- 複数ページにまたがる複雑な表
- ホスティング型SaaS

OCR・スキャンPDF・スマホ撮影には対応していません。

## Quick Start

### 1. Local Web UI（Docker）

```bash
docker build -f Dockerfile.web -t revenue-kun-web .
docker run --rm -p 127.0.0.1:8000:8000 revenue-kun-web
```

ブラウザで `http://127.0.0.1:8000/` を開きます。ホスト側は `127.0.0.1`（ループバック）のみにbindされます。インターネットへの公開は想定していません。

### 2. Local Web UI（Dockerなし）

```powershell
python -m pip install -r requirements-web.txt
python -m uvicorn webui.app:app --host 127.0.0.1 --port 8000
```

### 3. CLI

```powershell
python -m pip install -r requirements.txt
python src/main.py --assumptions assumptions.sample.yaml --rent-roll-pdf data/sample_rentroll_simple.pdf --output ./output --excel-output ./output/direct_cap.xlsx
```

CLIの詳細なオプション・入出力仕様は `python src/main.py --help` を参照してください。

## Claude Code / Codex

revenue-kun は、Claude Code と Codex の両方に向けたSkillを提供しています。

Claude CodeまたはCodex上で「revenue-kunを起動して」「Web UIを開いて」等と依頼すると、Local Web UIが起動します。起動先は `127.0.0.1` 上のローカル実行のみで、ホスティング型SaaSではありません。

## Codex Plugin

revenue-kunはCodex Pluginとして、repo-hosted Codex Marketplace経由で導入できます。OpenAI公式Directoryへの掲載状況とは独立して、`signal-yield/revenue-kun` リポジトリをMarketplaceとして登録して利用できます。

インストールは2段階です。

1. Marketplace登録
2. Codexで `/plugins` を開き、`signal-yield` Marketplaceから `revenue-kun` をインストール

```bash
codex plugin marketplace add signal-yield/revenue-kun
```

その後、Codex CLIで `codex` を起動して `/plugins` を開き、`signal-yield` Marketplaceを選択し、`revenue-kun` をInstallしてください。

公式manualでは、Marketplace登録は `codex plugin marketplace add owner/repo`、Marketplace一覧確認は `codex plugin marketplace list`、Marketplace削除は `codex plugin marketplace remove marketplace-name` と案内されています。Pluginのinstall、uninstall、enable、disableは、Codex CLIの `/plugins` 画面またはChatGPT DesktopのPlugins画面から操作できます。

利用例:

```text
revenue-kunを起動して
Web UIを開いて
このレントロールCSVから収益試算Excelを作成して
このテキスト抽出可能PDFからdirect_cap.xlsxを作成して
```

制約:

- Local Web UIは `127.0.0.1` 限定で起動します。
- hosted SaaSではありません。
- 入力CSV/PDFをrevenue-kunが外部サービスへ送信することはありません。
- OCR、スキャンPDF、スマートフォン撮影画像には対応していません。
- 出力は「収益試算値」であり、不動産鑑定評価ではありません。
- 投資判断、法律判断、税務判断は提供しません。

管理:

```bash
codex plugin marketplace list
codex plugin marketplace upgrade signal-yield
codex plugin marketplace remove signal-yield
```

Pluginのdisable/enableは、Codex CLIで `codex` を起動して `/plugins` を開き、インストール済みPlugin上でSpaceキーを押して切り替えます。uninstallは同じPluginブラウザでPlugin詳細を開き、利用可能な場合に **Uninstall plugin** を選択します。

詳しい導入手順とtroubleshootingは [docs/CODEX_PLUGIN_INSTALL.md](docs/CODEX_PLUGIN_INSTALL.md) を参照してください。

## ライセンス

Apache License 2.0

## リンク

- 公式サイト: https://signal-yield.github.io/revenue-kun/
- 最新リリース（v0.5.2）: https://github.com/signal-yield/revenue-kun/releases/tag/v0.5.2
- Issues: https://github.com/signal-yield/revenue-kun/issues
- License: [LICENSE](LICENSE)

過去のリリース履歴は [GitHub Releases](https://github.com/signal-yield/revenue-kun/releases) を参照してください。

## 免責事項

- 本ツールは不動産鑑定評価ではありません。
- 出力される金額は「収益試算値」であり、鑑定評価による「収益価格」ではありません。
- 投資判断・法律判断・税務判断は提供しません。
- 正式な鑑定評価・価格判断・投資判断・法律的判断が必要な場合は、不動産鑑定士・弁護士・税理士その他の専門家に確認してください。
