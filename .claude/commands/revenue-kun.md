---
description: revenue-kun 収益試算ワークフロー（dry-run → Checkpoint A → full run → Checkpoint B）
---

# /revenue-kun — 収益試算ワークフロー

このコマンドは revenue-kun CLI を使って収益試算ワークフローを実行します。
CLAUDE.md のすべてのルール（§4–§16）が本コマンド実行中も適用されます。

---

## 引数

`$ARGUMENTS` にレントロール PDF（または CSV）のパスを指定します。

```
/revenue-kun data/sample_rentroll_simple.pdf
```

引数が空の場合は、以下の 3 つをユーザーに確認してください：
1. レントロールファイルのパス（`.pdf` または `.csv`）
2. 仮定値 YAML のパス（デフォルト: `assumptions.sample.yaml`）
3. 出力ディレクトリのパス（デフォルト: `./output`）

---

## サンプル限定モード（Issue #21 open の間）

ユーザーが合成サンプル以外の PDF を指定した場合は、実行前に以下を必ず明示してください：

> 「qualifying real-world text-based PDF の評価は未完了です（Issue #21 open）。
> 実務検証済みとは表記しません。
> 以下は合成サンプルデータによる出力です。実物件・実テナント情報は含みません。」

合成サンプル（リポジトリ同梱）：
- `data/sample_rentroll_simple.pdf`（5 戸、全室稼働）
- `data/sample_rentroll_missing_values.pdf`（5 戸、1 戸空室）

---

## パス検証（コマンド構築前に必須）

以下をすべて確認してから CLI コマンドを構築してください：
1. ファイルが指定パスに存在すること
2. 拡張子が `.pdf`・`.csv`（レントロール）または `.yaml`（仮定値）であること
3. パスが `-` で始まっていないこと（オプションインジェクション防止）
4. パスがプロジェクト作業ディレクトリ以内であること

いずれかが失敗した場合はコマンドを構築せず、ユーザーに有効なパスを確認してください。

---

## Step 1 — ドライラン（--dry-run）

**フルランより先に必ず実行してください。**

PDF の場合：
```powershell
python src/main.py `
  --assumptions <assumptions_path> `
  --rent-roll-pdf <pdf_path> `
  --output <output_dir> `
  --dry-run
```

CSV の場合：
```powershell
python src/main.py `
  --assumptions <assumptions_path> `
  --rent-roll <csv_path> `
  --output <output_dir> `
  --dry-run
```

ドライラン完了後、`output/extraction_log.json` を読み取り Checkpoint A を実行してください。

---

## Checkpoint A — 抽出結果レビュー（フルランをブロックするゲート）

ドライラン exit code 0 の後、以下をすべてユーザーに提示してください：

1. **DISCLAIMER テキストを一字一句そのまま出力する**（`src/revenue_kun/__init__.py` の DISCLAIMER 定数）
2. 抽出されたユニット数
3. 認識されたカラムマップフィールド（`extraction_log.json` より）
4. 欠損セルの数
5. 必須フィールド（賃料、ステータス）が欠損していないか
6. 以下の質問を明示する：

> 「抽出結果を確認してください。正しければ続行します。問題があれば教えてください。」

**ユーザーの明示的な確認を受けるまで Step 2 に進まないでください。**

---

## Step 2 — フルラン（--excel-output）

Checkpoint A 確認後のみ実行：

PDF の場合：
```powershell
python src/main.py `
  --assumptions <assumptions_path> `
  --rent-roll-pdf <pdf_path> `
  --output <output_dir> `
  --excel-output <output_dir>/direct_cap.xlsx
```

CSV の場合：
```powershell
python src/main.py `
  --assumptions <assumptions_path> `
  --rent-roll <csv_path> `
  --output <output_dir> `
  --excel-output <output_dir>/direct_cap.xlsx
```

フルラン完了後、`output/missing_info.md` を読み取り Checkpoint B を実行してください。

---

## Checkpoint B — Excel セルレビュー（収益試算値の参照をブロックするゲート）

フルラン完了 + `missing_info.md` 読み取り後、以下をすべてユーザーに提示してください：

### ユーザーが手入力するセル一覧

**シート: 読み取りレントロール**
- 空室ユニット行：賃料・共益費・水道光熱費・駐車場・その他（`missing_info.md` 参照）

**シート: 直接還元法‗費用詳細版**
- 管理費、修繕費、損害保険料、固定資産税、その他（全費用行）

**シート: 直接還元法_OER**
- E13: 空室損失率
- E14: 貸倒損失率
- E15: 経費率（運営費用率）
- E16: 資本的支出（年額）
- E17: 還元利回り

以下を明示してください：

> 「これらのセルはユーザーが手入力してください。Claudeは代わりに入力しません。」

以下の質問を明示してください：

> 「必要なセルへの入力が完了したら教えてください。」

**ユーザーの明示的な確認を受けるまで収益試算値を参照しないでください。**

---

## Checkpoint C — 専門家レビュー開示（毎回必須、ゲートなし）

収益試算値（数値）を参照するたびに、毎回以下を出力してください：

> 「出力値は収益試算値（direct-capitalization revenue estimate）です。
> 鑑定評価による収益価格ではありません。
> 正式な価格判断・投資判断・法律的判断・税務上の判断が必要な場合は、
> 不動産鑑定士・弁護士・税理士その他の専門家に確認してください。」

一度開示すれば十分ではありません。数値が登場するたびに繰り返してください。

---

## 仮定値の入力先案内（値の提案禁止）

ユーザーが以下の数値を尋ねた場合は、値を提案せず以下を返してください：

対象: 還元利回り・空室損失率・貸倒損失・経費率・資本的支出・管理費率

> 「revenue-kun は還元利回り・空室損失率・経費率等の数値を提案しません。
> これらの仮定値は、担当の不動産鑑定士・ブローカー・税理士等の専門家、
> または公的統計・市場調査に基づいてユーザー自身がご判断ください。
> 数値の入力先は Excel ワークブックの各シートにあります（Checkpoint B 参照）。」

入力先（どのシートのどのセルか）の案内は行っても構いません。値の提案は禁止です。

---

## エラー処理

CLI が非ゼロ終了コードを返した場合、または例外が発生した場合：

1. エラーメッセージをそのまま（verbatim）ユーザーに提示する
2. 次のステップに進まない
3. 自動的に入力を変えてリトライしない
4. 欠損値を補う合成値を生成しない
5. OCR をエラーの回避策として提案しない

| エラー種別 | 対応 |
|-----------|------|
| `RentRollExtractionError` | `failure_reason` を提示。PDF がテキストベースか確認。停止。 |
| `AssumptionsError` | バリデーションメッセージを提示。`assumptions.sample.yaml` を確認するよう案内。停止。 |
| `OSError` | OS エラーメッセージを提示。`--force` 相当で再実行しない。停止。 |
| exit code 1 / 2 / 3 | stderr を提示。エラークラスを特定。停止。 |
| 0 ユニット抽出 | 結果を提示。PDF がスキャン PDF でないか確認。停止。 |

エラー停止後は、ユーザーが修正済み入力または明示的な次の指示を提供するまで待機してください。

---

*revenue-kun v0.4.1 — Claude Code project workflow*
*Claude Skill リリース済みとは表記しません。*
*#19 remains open  #21 remains open  Issue #22 is completed  #48 remains open*
