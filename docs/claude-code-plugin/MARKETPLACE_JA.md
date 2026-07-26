# revenue-kun — Claude Code Marketplace 掲載文案（日本語）

## Plugin名
`revenue-kun`

## 表示名
revenue-kun — Rent Roll to Direct Capitalization Excel

## 1行説明
レントロールPDF／CSVから、直接還元法による収益試算Excelを生成する不動産実務向けOSS。

## 説明（100〜200文字程度）
revenue-kunは、レントロール（CSVまたはテキスト抽出可能なPDF）を読み取り、直接還元法による収益試算Excel（direct_cap.xlsx）を生成するApache-2.0のOSSです。Local Web UI・CLI・Dockerに対応し、Claude Code上で「revenue-kunを起動して」と依頼するとLocal Web UIが起動します。出力は収益試算値であり、不動産鑑定評価ではありません。

## 詳細説明
revenue-kunは、賃貸不動産のレントロールから直接還元法による収益試算を行うローカル実行専用のツールです。CSVまたはテキスト抽出可能なPDFを読み取り、抽出結果をプレビューしたうえで、OER版・費用詳細版の2方式を同時に出力するExcelワークブック（`direct_cap.xlsx`）を生成します。空室損失率・貸倒損失率・OER（または個別運営費用）・資本的支出・還元利回りといった判断が必要な前提条件は、アプリ側では入力させず、生成後のExcel上でユーザー自身が入力します。数式は隠蔽せず、セル単位で計算過程を確認できます。

Claude Code向けSkillとして、「revenue-kunを起動して」「Web UIを開いて」等と依頼すると、Local Web UIが127.0.0.1限定で起動します。既存プロセスがある場合は`/healthz`で確認し、重複起動しません。

## 主な機能
- CSVまたはテキスト抽出可能なPDFの読み取り
- 抽出結果のプレビュー（区画数・稼働／空室・欠損情報）
- 賃料・共益費・水道代・駐車場収入・その他収入のGPIへの自動反映
- OER版・費用詳細版の同時出力（両シートは独立計算）
- 読み取りレントロールシートの出力
- Local Web UI（127.0.0.1限定）
- CLI対応
- Docker対応
- 数式を隠さないExcel生成

## 使用例
- 「revenue-kunを起動して」
- 「revenue-kunのWeb UIを開いて」
- 「ブラウザでrevenue-kunを使いたい」
- 「レントロールPDFから収益試算Excelを作成して」
- 「CSVからdirect_cap.xlsxを生成して」

## 対応入力
- CSV
- テキスト抽出可能なPDF

## 非対応入力
- OCRが必要なPDF
- スキャンPDF
- スマートフォン撮影画像
- 複雑な結合セル
- 複数ページにまたがる複雑な表
- hosted SaaS利用（本ツールはローカル実行専用です）

## Local Web UI
`python -m uvicorn webui.app:app --host 127.0.0.1 --port 8000` で起動します。`127.0.0.1`限定でbindされ、インターネットやLANには公開されません。起動前に`/healthz`で既存プロセスの有無を確認し、`{"status":"ok"}`が返る場合は重複起動しません。

## CLI
`python src/main.py --assumptions <yaml> --rent-roll-pdf <pdf> --output <dir> --excel-output <path>` の形式でExcelワークブックを生成します。

## Docker
`docker build -f Dockerfile.web -t revenue-kun-web .` でイメージをビルドし、`docker run --rm -p 127.0.0.1:8000:8000 revenue-kun-web` で起動します。ホスト側は`127.0.0.1`限定でbindされます。

## Security
[SECURITY_AND_PRIVACY.md](./SECURITY_AND_PRIVACY.md) を参照してください。ローカル環境で動作し、アップロードされたファイルを外部サーバーへ送信しません。

## Privacy
公開リポジトリには合成サンプルのみを含み、非公開PDF・実物件情報・APIキー・秘密情報は含めません。

## 免責事項
本ツールの出力は収益試算値であり、不動産鑑定評価による収益価格ではありません。投資判断、法律判断、税務判断を提供するものではありません。正式な鑑定評価・価格判断・投資判断・法律的判断が必要な場合は、不動産鑑定士・弁護士・税理士その他の専門家に確認してください。

## インストール
```
/plugin marketplace add signal-yield/revenue-kun
/plugin install revenue-kun@revenue-kun
```

## enable方法
```
/plugin enable revenue-kun@revenue-kun
```

## disable方法
```
/plugin disable revenue-kun@revenue-kun
```

## uninstall方法
```
/plugin uninstall revenue-kun@revenue-kun
```

## Marketplace削除方法
```
/plugin marketplace remove revenue-kun
```

## サポート窓口
GitHub Issues: https://github.com/signal-yield/revenue-kun/issues

## category候補
Productivity

## tags候補
real-estate, rent-roll, direct-capitalization, excel, local-first, japan

## starter prompts
- revenue-kunを起動して
- レントロールPDFから収益試算Excelを作成して
- CSVからdirect_cap.xlsxを生成して

## release notes
最新版 v0.5.2。OER版・費用詳細版の独立計算化、経常的な付帯収入（水道代・駐車場・その他収入）の自動算入。詳細は [Release v0.5.2](https://github.com/signal-yield/revenue-kun/releases/tag/v0.5.2) を参照してください。

## submission checklist
[SUBMISSION_CHECKLIST.md](./SUBMISSION_CHECKLIST.md) を参照してください。

## 申請時に人手で入力する項目
- コミュニティMarketplace申請フォーム（claude.aiまたはConsole）へのアカウント紐付け
- publisher/organization情報の入力（フォーム側の要求次第）
- 提出前の最終`claude plugin validate`実行結果の確認

## 未確認の公式要件
- icon／logoの要件（必須か任意か、ファイル形式、寸法等）はAnthropicの公式公開仕様では確認できませんでした
- shell実行の有無・local file accessの有無を宣言する専用フィールドは、plugin.json／marketplace.jsonの公式schemaに存在せず、確認できませんでした
- publisher verification制度の詳細はAnthropicの公式公開仕様では確認できませんでした
