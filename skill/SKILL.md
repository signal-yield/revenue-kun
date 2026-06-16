---
name: revenue-kun
description: <収益還元（直接還元法）の一次試算スキル。レントロール（賃料表）PDFを入力に、
  収入側を自動集計し、空室・経費率・還元利回り等の判断値はユーザーがExcelで手入力する前提の
  収益試算ワークブック（xlsx）を出力する。ユーザーが「白箱」「NOI」等と言わなくても、以下の
  局面では必ず本Skillを使う。トリガー語例：「収益還元」「収益還元クン」「収益試算」「収益試算値」
  「レントロールから収益」「賃料表から収益」「直接還元法」「NOI出して」「運営純収益」「還元利回りで」
  「キャップレートで試算」「レントロール読んで」「収益還元クンで」。
  出力は「収益試算値」であり鑑定評価による「収益価格」ではない。鑑定評価・投資判断・法的判断は対象外。
  非対象：DCF法、土地査定（→土地査定クン）、重要事項説明調査（→重調クン）、口頭の簡易見積り。>
---

# revenue-kun（収益還元クン）Skill

> **免責・用語ガード**
> 本Skillの出力は「収益試算値」であり、鑑定評価による「収益価格」ではありません。
> 合成サンプルPDFで動作確認済み。qualifying real-world text-based PDF の評価は未完了（Issue #21 open）。
> 実物件PDFはサンプル検証の範囲外であり、実務検証済みとは表記しません。
> 正式な鑑定評価・価格判断・投資判断・法的判断は専門家にご確認ください。
> 欠損値は補完しません（空欄のまま提示します）。

---

## 起動時の絶対命令

本Skill起動時は必ず `python scripts/main.py --excel-output <出力先>` を実行する。
openpyxl を直接呼んで xlsx を生成すること、数式を手書きで再現することは禁止。
エンジン（scripts/）が唯一の計算・出力経路である。

初回実行前に依存ライブラリを導入する：
```
pip install -r requirements.txt --break-system-packages
```

末尾途切れ確認（サンドボックスの誤検知防止）：
```
tail -3 scripts/main.py
tail -3 scripts/revenue_kun/excel_output.py
tail -3 scripts/revenue_kun/pdf_extract.py
```
末尾が正常（`if __name__`／関数の return 等）ならファイルは完全。
独自実装で代替せず、そのまま `python scripts/main.py ...` を実行する。

---

## 入力処理

1. アップロードされたレントロール PDF を検出する。
   - claude.ai: `/mnt/user-data/uploads/`
   - Cowork: 指定パス
2. **まず `--dry-run`** を実行し、抽出診断（ユニット数・カラムマップ・必須欠損・欠損セル数）をユーザーに提示する。
3. ユーザーの確認後、本実行で xlsx を生成する。
4. **欠損は補完しない**。`missing_info.md` の要点（どのセルが欠損か）を会話内に要約提示する。

### dry-run コマンド

```bash
python scripts/main.py \
  --assumptions samples/assumptions.sample.yaml \
  --rent-roll-pdf <PDF パス> \
  --output ./out \
  --dry-run
```

### 本実行コマンド

```bash
python scripts/main.py \
  --assumptions samples/assumptions.sample.yaml \
  --rent-roll-pdf <PDF パス> \
  --output ./out \
  --excel-output "./out/収益試算_<物件名>_<YYYYMMDD>.xlsx"
```

---

## assumptions の扱い（確定仕様）

- 同梱の `samples/assumptions.sample.yaml` を既定として実行する（収入側を自動集計するため）。
- **収益試算 Excel の判断値（空室損失率・貸倒損失率・経費率・資本的支出・還元利回り＝OER E13:E17）は空欄のまま出力**し、ユーザーが Excel 上で手入力する。
- **会話側で還元利回り等を聞き出さない。提案・例示・初期値設定もしない**（CLAUDE.md §13 厳守）。
  「相場は」「ざっくりで」等を求められても数値を出さず、ユーザー入力に委ねる旨だけ伝える。
- 結果として E24 収益試算値は、ユーザーが利回りを入れるまで空欄（`IFERROR(.., "")`）。これは仕様。

---

## 出力

成果物: `収益試算_<物件名またはレントロール名>_<YYYYMMDD>.xlsx`

- claude.ai: `/mnt/user-data/outputs/` に置き **present_files で提示**
- Cowork: デスクトップへコピー（MAX_PATH 回避）も可

xlsx には OER 自己計算モデルが入る：
- 収入側（E5:E9）: レントロールから自動集計
- 判断値（E13:E17）: 空欄（ユーザーが手入力）
- 収益試算値（E24）: `=IFERROR(E23/E17,"")` — 利回り入力まで空欄

---

## 免責・用語ガード（出力提示時に毎回表示）

```
> 本Skillの出力は「収益試算値」であり、鑑定評価による「収益価格」ではありません。
> 合成サンプルPDFで動作確認済み。qualifying real-world text-based PDF の評価は未完了（Issue #21 open）。
> 実物件PDFはサンプル検証の範囲外であり、実務検証済みとは表記しません。
> 正式な鑑定評価・価格判断・投資判断・法的判断は専門家にご確認ください。
> 欠損値は補完しません（空欄のまま提示します）。
```

実物件 PDF でもユーザー要求があれば実行するが、上記キャプションを必ず併記する。

---

## 禁止事項

- 還元利回り・空室損失率・経費率・資本的支出の値を提案・例示・初期値設定すること
- openpyxl を直接呼んで xlsx を独自生成すること
- エラー時に OCR を回避策として提案すること（スキャン PDF は対象外）
- 「収益価格」を肯定文脈で使うこと
- 「実務検証済み」「OCR対応」「投資助言」「法律助言」「税務助言」「完全自動査定」と表記すること

---

*revenue-kun v0.4.1 — Package Skill*
*#19 remains open  #21 remains open  Issue #22 is completed  #48 remains open*
