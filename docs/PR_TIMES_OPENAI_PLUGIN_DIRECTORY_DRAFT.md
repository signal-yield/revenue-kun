# PR TIMES入稿用原稿：revenue-kun v0.5.2 OpenAI Plugins Directory公開

## 1. 推奨タイトル

不動産収益試算OSS「revenue-kun」v0.5.2、OpenAI Plugins Directoryで公開

## 2. タイトル候補比較

- **推奨案：不動産収益試算OSS「revenue-kun」v0.5.2、OpenAI Plugins Directoryで公開**
  製品の用途、名称、バージョン、発表内容が短く明確。誇張がなく、検索語も含む。
- **レントロールから直接還元法Excelを生成するOSS「revenue-kun」、OpenAI Plugins Directoryで公開**
  機能が具体的で検索性も高い一方、推奨案より長い。
- **不動産実務向け白箱OSS「revenue-kun」、ChatGPTのPlugins Directoryで公開**
  設計思想が伝わるが、「白箱」は初見の読者に説明が必要。
- **不動産収益試算を支援する「revenue-kun」、OpenAI Plugins Directoryから追加可能に**
  利用者側の変化が分かりやすい一方、OSSとバージョンがタイトルに出ない。

「AIプラグイン」は機能範囲を広く誤認させる可能性があるため、タイトルでは使用しない。

## 3. サブタイトル

レントロールCSV・テキスト抽出可能PDFから、計算過程を確認できる直接還元法Excelをローカル生成。Codex／Claude Code経由でも利用可能

## 4. リード文

Signal Yield Advisory（代表：松田 幸一）が開発する不動産収益試算OSS「revenue-kun」v0.5.2が、2026年7月15日、OpenAI Plugins Directoryで公開されました。一般ユーザーはChatGPTのプラグイン画面で「revenue-kun」を検索し、追加できます。本ツールはレントロールCSVまたはテキスト抽出可能なPDFから、計算過程を確認できる直接還元法のExcelファイル（`direct_cap.xlsx`）をローカル環境で生成します。Apache-2.0ライセンスで公開するlocal-firstのOSSです。

## 5. 本文

### 1．OpenAI Plugins Directoryで公開

不動産収益試算OSS「revenue-kun」v0.5.2は、2026年7月15日にOpenAI Plugins Directoryで公開されました。掲載カテゴリは「Productivity」、サブタイトルは「Turn rent rolls into Excel」です。ChatGPTのプラグイン画面で「revenue-kun」を検索することで、一般ユーザーがDirectoryから見つけて追加できるようになりました。

- 製品名：revenue-kun
- バージョン：0.5.2
- カテゴリ：Productivity
- サブタイトル：Turn rent rolls into Excel
- 開発者：Koichi Matsuda / Signal Yield Advisory
- OpenAI Plugins Directory：https://chatgpt.com/plugins?q=revenue

OpenAI Plugins Directoryへの掲載は、OpenAIが本ツールの機能を推奨したり、生成される収益試算値の精度を保証したりすることを意味しません。

### 2．revenue-kunとは

revenue-kunは、レントロールPDF／CSVから直接還元法Excelを生成する、Docker対応の不動産収益試算CLIです。レントロールとは、物件の区画、賃料、共益費、入居状況などを一覧にした資料です。

CSVまたはテキスト抽出可能なPDFを読み込み、抽出した行を確認したうえで、直接還元法による収益試算ワークブックを生成します。直接還元法は、物件が生み出す純収益と還元利回りを用いて収益性を検討する方法です。

出力先をExcelとすることで、利用者が元資料、入力値、数式、計算結果を照合できます。計算ロジックや前提を見えない状態にせず、確認可能な「白箱OSS」として公開しています。

### 3．生成されるExcel

生成される`direct_cap.xlsx`は、次の3シートで構成されます。

- **直接還元法_OER**
  OER（Operating Expense Ratio、運営費率）を用いて運営費用を概算するシートです。賃料等の年額収入、空室損失率、OER、資本的支出、還元利回りなどを確認・入力し、収益試算値を算定します。
- **直接還元法‗費用詳細版**
  運営費用を項目別に確認・入力して積み上げるシートです。OER版とは入力値・計算値を参照し合わず、独立して計算します。
- **読み取りレントロール**
  抽出した区画、面積、賃料、共益費、付帯収入、月計、年計を確認するシートです。両計算シートはこのシートの年額収入をそれぞれ参照します。

### 4．v0.5.2の主な機能

- レントロールCSVの読み込み
- テキスト抽出可能なPDFの読み込み
- 抽出行のプレビュー
- `direct_cap.xlsx`の生成
- CLIによる実行
- Dockerによる実行
- `127.0.0.1`限定のLocal Web UI
- 水道代、駐車場、その他収入などの付帯収入の抽出・表示とGPIへの自動算入
- Codex Plugin
- Claude Code Plugin
- OpenAI Plugins Directoryからの追加

v0.5.2では、水道代、駐車場、その他収入などの付帯収入を「読み取りレントロール」に表示し、OER版と費用詳細版の双方のGPI（総潜在収入）へ自動算入します。旧バージョン向けの`optional_income`設定は後方互換のため受理されますが、非推奨であり、Excel生成結果には影響しません。

### 5．3つの利用経路

**A．ChatGPT一般ユーザー**

OpenAI Plugins Directoryで「revenue-kun」を検索し、追加できます。

**B．Codex利用者**

GitHub repositoryをrepo-hosted Marketplaceとして登録し、Codexの`/plugins`から「revenue-kun」をインストールできます。正式な手順はCodex Plugin導入ガイドに掲載しています。

**C．Claude Code利用者**

GitHub Marketplaceを登録し、「revenue-kun」Pluginをインストールできます。正式なコマンドと利用手順はClaude Code Plugin導入ガイドに掲載しています。

### 6．local-firstとプライバシー

revenue-kunはホスティング型のサービスではなく、利用者のローカル環境で動作します。Local Web UIはループバックアドレス`127.0.0.1`のみにbindする設計です。

入力されたCSV／PDFをrevenue-kunが外部処理サービスへ送信することはありません。アプリケーションtelemetry、利用分析、トラッキングピクセル、Cookieは含まず、APIキーも要求しません。なお、依存パッケージの取得、Git操作、Docker buildなど、利用者が開始する通常の外部通信まで否定するものではありません。公開repository内のサンプルは合成データです。

### 7．対応範囲と制約

- 対応するPDFはテキスト抽出可能なものに限ります
- OCR、スキャンPDF、スマートフォン撮影画像の読み取りには対応していません
- 出力は収益試算値であり、不動産鑑定評価ではありません
- 投資判断、法律、税務に関する助言を提供するものではありません
- 抽出結果、元資料、入力する前提条件、生成されたExcelを利用者が照合する必要があります
- 最終的な判断は利用者および必要に応じて各分野の専門家が行います

### 8．開発背景

不動産実務では、計算結果だけでなく、どの資料から何を読み取り、どの前提や数式で算定したかを説明できることが重要です。生成AIを入口として使う場合でも、実務の判断材料をブラックボックスにしない設計が求められます。

revenue-kunは、不動産鑑定・不動産アセットマネジメントの実務と生成AIを接続しながら、元資料、抽出値、計算式を確認できる再現性のある基盤を目指しています。個別企業や実物件の機密情報に依存せず、合成サンプルと公開コードで検証できるOSSとして開発しています。

### 9．今後の展開

今後も白箱OSSとして改善を継続し、不動産実務者や開発者からGitHub Issuesなどを通じてフィードバックを受け付けます。OCRやスキャンPDFは現時点では対応範囲外であり、入力アダプタの拡張は将来の検討対象です。

また、公開可能で再現性のある基盤として、生成AI導入に関するコンサルティングやPoC（概念実証）の設計支援での活用も検討します。具体的な提供時期、形態、価格は未定です。

### 10．関連リンク

- 技術的な一次情報（GitHub Release）：https://github.com/signal-yield/revenue-kun/releases/tag/v0.5.2
- OpenAI Plugins Directory：https://chatgpt.com/plugins?q=revenue
- 公式LP：https://signal-yield.github.io/revenue-kun/
- GitHub Repository：https://github.com/signal-yield/revenue-kun
- Codex Plugin導入ガイド：https://github.com/signal-yield/revenue-kun/blob/main/docs/CODEX_PLUGIN_INSTALL.md
- Claude Code Plugin導入ガイド：https://github.com/signal-yield/revenue-kun/blob/main/docs/CLAUDE_CODE_PLUGIN_INSTALL.md
- Support：https://signal-yield.github.io/revenue-kun/support.html
- Privacy：https://signal-yield.github.io/revenue-kun/privacy.html
- Terms：https://signal-yield.github.io/revenue-kun/terms.html

## 6. 開発者コメント

Signal Yield Advisory 代表 松田 幸一

「不動産の収益試算では、最終的な数字だけでなく、元資料から何を読み取り、どの前提と数式で計算したのかを確認できることが重要です。revenue-kunは、生成AIから使いやすくしつつ、計算過程はExcelで確かめられる形を選びました。OpenAI Plugins Directoryへの公開を機に、不動産実務者や開発者の皆さまから率直なフィードバックをいただき、説明可能な白箱OSSとして改善を続けます。」

## 7. 関連URL

- GitHub Release（技術的な一次情報）：https://github.com/signal-yield/revenue-kun/releases/tag/v0.5.2
- OpenAI Plugins Directory：https://chatgpt.com/plugins?q=revenue
- LP：https://signal-yield.github.io/revenue-kun/
- Repository：https://github.com/signal-yield/revenue-kun
- Support：https://signal-yield.github.io/revenue-kun/support.html
- Privacy：https://signal-yield.github.io/revenue-kun/privacy.html
- Terms：https://signal-yield.github.io/revenue-kun/terms.html

## 8. 会社・開発者情報

- 名称：Signal Yield Advisory
- 代表：松田 幸一
- 英語表記：Koichi Matsuda
- 概要：不動産鑑定・不動産AM・生成AI導入・不動産AI OSS開発を軸に活動
- Website：https://signal-yield.github.io/revenue-kun/
- GitHub：https://github.com/signal-yield
- 問い合わせ：https://signal-yield.github.io/revenue-kun/support.html

個人住所、電話番号、非公開メールアドレスは掲載しない。

## 9. 入稿時の注意

- OpenAI Plugins Directoryへの掲載を事実として記載し、OpenAIによる推奨、認定、精度保証を示唆しない。
- Directoryの検索結果と「revenue-kun」の表示を入稿直前に再確認する。
- PR TIMESの公開日と本文中の「Published date: 2026-07-15」を混同しない。
- コード表記や長いURLがPR TIMESのプレビューで崩れていないか確認する。
- 実物件情報、private PDF、個人情報、非公開メールアドレスを画像や添付に含めない。
- 本文の制約・免責事項を削らない。
- PR TIMES公開後、その公開URLをLinkedInの解説投稿で参照する。

## 10. 画像候補

今回、新規画像は作成しない。

### repository内で利用可能性を確認できる候補

- `plugins/revenue-kun/assets/revenue-kun-logo.png`：revenue-kunロゴ候補。正方形PNG。掲載前にPR TIMES上での見え方を確認する。
- `plugins/revenue-kun/assets/revenue-kun-icon.png`：小サイズ用アイコン候補。正方形PNG。
- `docs/assets/screenshots/workbook-oer.png`：OERシートの画面候補。repository内に存在。掲載前に個人・実物件情報がないことを目視確認する。
- `docs/assets/screenshots/workbook-rent-roll.png`：読み取りレントロールの画面候補。repository内に存在。掲載前に個人・実物件情報がないことを目視確認する。

### 別途取得または作成が必要な候補

- OpenAI Plugins Directoryで「revenue-kun」が表示された検索結果のスクリーンショット
- Local Web UIの合成サンプル画面
- 費用詳細版シートの合成サンプル画面
- 3シート構成を説明する図
- GitHub PagesのDirectory／Codex／Claude Code導入経路カードのスクリーンショット

スクリーンショットではユーザー名、メール、ブラウザの個人情報を必要に応じてトリミングする。OpenAIの名称・ロゴの利用条件を確認し、推奨・協賛と誤認させない。

## 11. 未確定項目

- PR TIMESでの配信日時
- PR TIMES上の企業・団体アカウント表記と問い合わせ欄の最終形式
- 掲載画像と画像キャプション
- OpenAI Plugins Directory検索結果画面のスクリーンショット利用可否
- 将来の入力アダプタ拡張の具体的な内容・時期
- コンサルティング／PoC設計支援の具体的な提供条件

未確定項目は入稿前に確認し、断定表現を追加しない。

## 12. ファクトチェック

### Repositoryで確認済み

- バージョン0.5.2、Apache-2.0
- CSV、テキスト抽出可能PDF、CLI、Docker、Local Web UIへの対応
- `direct_cap.xlsx`と3シートの正確な名称・役割
- OER版と費用詳細版の独立計算
- 付帯収入の表示・自動算入、および旧`optional_income`設定の非推奨化
- Local Web UIの`127.0.0.1`限定bind
- 入力ファイルのローカル処理、telemetry・APIキー不要、合成サンプル
- OCR、スキャンPDF、スマートフォン撮影画像が対応範囲外
- Codex Plugin／Claude Code Pluginの導入経路
- 全pytest 444件、Skill tests 7件、Codex packaging 12件、Claude packaging 17件の成功

### GitHub Releaseで確認済み

- v0.5.2の機能、入力形式、3シート、付帯収入、制約
- OpenAI Plugins Directory公開情報
- Published date、Category、Subtitle、Developer、Directory URL
- Codex Plugin／Claude Code Pluginの導入情報
- 最新の検証件数

### OpenAI portal／Directoryでユーザー確認済み

- Status: Published
- Published date: 2026-07-15
- Version: 0.5.2
- Category: Productivity
- Subtitle: Turn rent rolls into Excel
- Developer: Koichi Matsuda / Signal Yield Advisory

### 公開URLで確認済み

- GitHub Release、LP、Repository、Support、Privacy、Terms

### 開発者コメント

- 「開発者コメント」節は松田 幸一名義の掲載用ドラフト。本人による最終確認が必要。

### 将来方針

- 白箱OSSとして改善を継続し、Issue／feedbackを受け付ける方針。
- 入力アダプタ拡張、コンサルティング／PoC設計支援は検討事項であり、時期・条件は未定。

### 未確認

- PR TIMESの配信日時、掲載画像、Directory画面の利用可否、将来施策の具体条件。
