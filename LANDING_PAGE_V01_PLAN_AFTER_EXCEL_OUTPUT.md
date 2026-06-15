# Landing Page v0.1 Plan — After Excel Output Implementation

## 1. Purpose

Define the scope, messaging, constraints, and page structure for the first public-facing
landing page (LP) of revenue-kun, to be built after the Excel output feature is confirmed
as functional.

This is a **planning document only**. No LP has been built or deployed.
No commercial SaaS, no completed Claude Skill release, no paid tier.

> **重要**: revenue-kun は不動産鑑定評価ではありません。出力される金額は「収益試算値」であり、
> 鑑定評価による「収益価格」ではありません。欠損項目は補完しません。
> qualifying real-world text-based PDF の評価は未完了（Issue #21 open）。
> 実務検証済みとは表記しません。

---

## 2. Current Product Status

| Item | State |
|------|-------|
| Latest main commit | `c4b32f5` (PR #56 merged) |
| Excel workbook generation | ✅ Implemented (`src/revenue_kun/excel_output.py`) |
| CLI `--excel-output` flag | ✅ Implemented and documented |
| README documentation | ✅ Updated (PR #55) |
| Synthetic sample inspection | ✅ Documented (`SAMPLE_EXCEL_OUTPUT_AFTER_V041.md`) |
| Test suite | ✅ 186 passed, 0 failed |
| Real-world PDF evaluation | ❌ Not complete (Issue #21 open) |
| OCR / scanned PDF | ❌ Not implemented |
| Claude Skill release | ❌ Not released |
| Commercial SaaS | ❌ Not available |
| Formal appraisal output | ❌ Out of scope by design |

---

## 3. Target Audience

**Primary**
- 不動産仲介担当者・PM（物件収益の前段確認を行う人）
- 不動産投資家・オーナー（収支試算を自分で行いたい人）
- 不動産鑑定士・税理士（計算補助ツールを探している専門家）

**Secondary**
- 宅建業者（重説前の収益確認フロー）
- テック系不動産スタートアップ（OSS ツールとして組み込み検討）
- 不動産系研究者・学生（直接還元法の学習・演習ツール）

**Not primary target**
- 一般消費者（本ツールは CLI ツールであり、技術的な操作を伴う）
- 非技術者（v0.1 は CLI のみ。GUI 未実装）

---

## 4. Core Message

**日本語（メインコピー案）**

> レントロールから直接還元法 Excel ワークブックを、コマンド一行で。

**English tagline (sub)**

> revenue-kun: open-source direct-capitalization CLI for rent roll verification.  
> Generate a structured Excel workbook — OER / expense detail / rent roll — in one command.

**補足ポジショニング**

- OSS の研究・検証支援 CLI である（商用 SaaS ではない）
- 出力は「収益試算値」であり「収益価格（鑑定評価額）」ではない
- 欠損を補完しない — ユーザーが確認・編集する前提の設計
- 専門家によるレビューの前段階ツールとして位置づける

---

## 5. What the LP May Claim

| Claim | Basis |
|-------|-------|
| Excel workbook generation implemented | ✅ PR #53 merged |
| CLI `--excel-output` flag available | ✅ PR #54 merged |
| 3-sheet workbook: OER / 費用詳細版 / レントロール | ✅ Verified in SAMPLE_EXCEL_OUTPUT_AFTER_V041.md |
| OER E2/E3/E5/E6/E7 auto-linked to annual totals | ✅ Verified |
| Monthly and annual total rows auto-computed | ✅ Verified |
| Vacant-unit 備考 normalized | ✅ Verified |
| Users can edit assumptions in Excel | ✅ By design |
| OSS — source available on GitHub | ✅ |
| Tests pass (186 passed, 0 failed) | ✅ Verified at time of writing |
| Synthetic sample regeneration documented | ✅ SAMPLE_EXCEL_OUTPUT_AFTER_V041.md |
| Input: text-based rent roll PDF (pdfplumber) | ✅ v0.4.1 parser scope |
| Input: CSV rent roll | ✅ Phase 1 feature |

---

## 6. What the LP Must Not Claim

| Prohibited claim | Reason |
|-----------------|--------|
| 実務検証済み / qualifying real-world PDF verified | Issue #21 open; not complete |
| OCR・スキャン PDF 対応 | Not implemented |
| 鑑定評価 / appraisal | Out of scope by design |
| 収益価格（鑑定評価額） | Output is 収益試算値 only |
| 投資助言 / investment advice | Out of scope |
| 法律助言 / legal advice | Out of scope |
| 税務助言 / tax advice | Out of scope |
| 完全自動査定 / fully automated valuation | Not provided; user verification required |
| Claude Skill リリース済み / completed Claude Skill release | Not released |
| 商用 SaaS 提供中 / commercial SaaS | Not available |
| 欠損の自動補完 | Not implemented by design |
| 複数ページ PDF・結合セル対応 | Not implemented |

---

## 7. Page Structure

### Section 1 — Hero

**Content**
- Headline: レントロールから直接還元法 Excel ワークブックを、コマンド一行で。
- Sub: OSS 研究・検証支援 CLI — 収益試算値の算出と Excel 出力
- CTA ボタン: 「GitHub で見る」「合成サンプルを試す」
- Hero image / screenshot: 生成された Excel ワークブックの3シート概観（合成データ）

**Constraints**
- 鑑定評価・投資助言への言及なし
- 実務検証済みの表記なし

---

### Section 2 — Problem（課題提起）

**Content**
- 収益物件の簡易試算を、Excel で手作業で行っている
- レントロールのデータ入力・月計・年計・OER へのリンクを毎回手で作る
- 前提（空室率・還元利回り等）を変えるたびに手修正が発生する
- PDF のレントロールをそのまま読み込む仕組みがない（一般ユーザー向け）

---

### Section 3 — What revenue-kun Does

**Content**
- レントロール（CSV または text-based PDF）を読み込む
- 直接還元法の計算（NOI・収益試算値・感応度分析）を実行
- `--excel-output` で直接還元法 Excel ワークブック（3シート）を生成
- 欠損項目は補完せず `missing_info.md` に記録

**Feature table**

| 機能 | 内容 |
|------|------|
| レントロール読み込み | CSV または text-based PDF（pdfplumber） |
| NOI 計算 | GPI / EGI / NOI / 純収益（還元対象） |
| 収益試算値 | 直接還元法（cap rate ÷ 純収益） |
| 感応度分析 | NOI × 還元利回りのマトリクス |
| Excel 出力 | `--excel-output` で3シート .xlsx を生成 |
| 欠損の扱い | 補完しない。欠損は明示して記録 |

---

### Section 4 — Excel Output Demo

**Content**
- Section headline: ワークブックを開くとこうなる（合成データ）
- 3シートの説明と画面キャプチャ（合成データのみ）

| シート | 説明 |
|--------|------|
| `直接還元法_OER` | 年額収入セル（E2/E3/E5/E6/E7）が `読み取りレントロール` を自動参照 |
| `直接還元法‗費用詳細版` | 管理費・修繕費等をユーザーが手入力 |
| `読み取りレントロール` | 抽出した区画データ・月計・年計 |

- コードスニペット（CLI 実行例）:

```powershell
python src/main.py \
  --assumptions assumptions.sample.yaml \
  --rent-roll-pdf data/sample_rentroll_simple.pdf \
  --output ./output \
  --excel-output ./output/direct_cap.xlsx
```

**Asset requirement**: 合成データのみ使用。私有 PDF・PII・物件名・住所を含まない。

---

### Section 5 — Workflow

**Content**

```
1. CLIで --excel-output を実行
      ↓
2. 読み取りレントロールシートで抽出値を確認
      ↓
3. 空室区画の想定賃料等を手入力
      ↓
4. 費用詳細版シートに費用明細を入力
      ↓
5. OERシートで空室損失率・還元利回り等の仮定を入力
      ↓
6. 収益試算値を確認・専門家にレビュー依頼
```

---

### Section 6 — What Users Can Edit in Excel

**Content**
- `読み取りレントロール`: 空室区画の賃料・共益費・その他収入を手入力
- `直接還元法‗費用詳細版`: 管理費・修繕費・損害保険料・固定資産税等
- `直接還元法_OER`: 空室損失率・貸倒損失・経費率・資本的支出・還元利回り

---

### Section 7 — Limitations（制限事項）

**Content** — この section は省略不可

| 制限 | 内容 |
|------|------|
| OCR / スキャン PDF | 対象外 |
| qualifying real-world PDF | 評価未完了（Issue #21 open）。実務検証済みとは表記しません |
| 複数ページ PDF・複雑な結合セル | 対象外 |
| 鑑定評価 | 対象外。出力は「収益試算値」 |
| 投資助言・法律助言・税務助言 | 対象外 |
| 欠損の自動補完 | 実施しない |
| GUI / Web UI | 未実装（CLI のみ） |

---

### Section 8 — GitHub / Sample / Contact CTA

**Content**

| CTA | 説明 |
|-----|------|
| GitHubリポジトリを見る | ソースコード・README・ライセンス確認 |
| 合成サンプルを試す | `data/sample_rentroll_simple.pdf` + `assumptions.sample.yaml` で動作確認 |
| 検証に参加する / フィードバックを送る | qualifying real-world text-based PDF をお持ちの方との協力を募る（Issue #21） |
| 問い合わせ | 協調検証・業務活用検討の連絡先 |

---

### Section 9 — Disclaimer（必須・省略不可）

免責文言（日本語 + English）を必ず掲載する。

**日本語（案）**

> 本ツールは不動産鑑定評価ではありません。出力される金額は「収益試算値」であり、
> 鑑定評価による「収益価格」ではありません。欠損項目は推測補完しません。
> 正式な鑑定評価・価格判断・投資判断・法律的判断が必要な場合は、
> 不動産鑑定士・弁護士・税理士その他の専門家に確認してください。
> qualifying real-world text-based rent roll PDF の評価は未完了です。
> 実務検証済みとは表記しません。

**English（案）**

> This tool is not a real estate appraisal. All output values are revenue estimates
> (収益試算値) and do not constitute appraised values (鑑定評価額).
> Missing items are not automatically filled in.
> For formal appraisal, pricing decisions, investment decisions, or legal / tax advice,
> consult a qualified professional.
> Evaluation against qualifying real-world text-based rent roll PDFs is not yet complete.

---

## 8. Demo / Screenshot Assets

| Asset | Source | Status |
|-------|--------|--------|
| `直接還元法_OER` シートのキャプチャ | `output/sample_direct_cap_simple.xlsx`（合成データ） | 未作成 |
| `読み取りレントロール` シートのキャプチャ（空室あり） | `output/sample_direct_cap_missing_values.xlsx`（合成データ） | 未作成 |
| `direct_cap.xlsx` サンプルファイル | 生成コマンドは `SAMPLE_EXCEL_OUTPUT_AFTER_V041.md` に記録済み | 未コミット（output/ は .gitignore） |
| CLI 実行動画 / GIF | 未作成 | 未作成 |

**Asset constraints**
- 合成データのみ使用（`data/sample_rentroll_simple.pdf`、`data/sample_rentroll_missing_values.pdf`）
- 私有 PDF・PII・テナント名・物件名・住所を含まない
- キャプチャ内に実際の数値が映る場合は合成データであることを明示する

---

## 9. CTA Options

| CTA | 優先度 | 実装難度 | 備考 |
|-----|--------|---------|------|
| GitHub リポジトリリンク | 高 | 低 | 即実装可能 |
| 合成サンプル試用（README リンク） | 高 | 低 | README の使い方セクションへ誘導 |
| 検証協力の募集（Issue #21 リンク） | 中 | 低 | qualifying real-world PDF 提供を募る |
| フィードバック・お問い合わせ（メール / フォーム） | 中 | 中 | メールアドレスまたは Google フォーム |
| PR TIMES プレスリリース（予定） | 低 | 高 | 後述の PR TIMES 準備状況を参照 |

---

## 10. Disclaimer / Risk Wording

### LP に必須の免責表記

1. **収益試算値 ≠ 鑑定評価額**: 出力が正式な鑑定評価ではないことを明記
2. **専門家への確認推奨**: 最終判断は専門家によることを明記
3. **欠損補完なし**: 欠損項目は補完しない設計であることを明記
4. **OCR 非対応**: スキャン PDF には対応していないことを明記
5. **実務未検証**: qualifying real-world PDF 評価未完了であることを明記
6. **投資助言・法律助言・税務助言 非提供**: 明示的に対象外と記載

### 禁止表記（LP に含めてはいけない表現）

| 禁止表現 | 理由 |
|---------|------|
| 「実務検証済み」「実物件での動作確認済み」 | Issue #21 未完了 |
| 「OCR 対応」「スキャン PDF 対応」 | 未実装 |
| 「鑑定評価」「収益価格」（肯定文脈） | 対象外 |
| 「投資助言」「推奨物件」 | 対象外 |
| 「法律的判断」「税務上の判断」 | 対象外 |
| 「完全自動」「AI が査定」 | 補完なし・ユーザー判断前提 |
| 「Claude Skill リリース済み」 | 未リリース |
| 「SaaS」「月額料金」「プロプラン」 | 商用化未実施 |

---

## 11. PR TIMES Readiness Check

| 項目 | 状態 | 備考 |
|------|------|------|
| ツール名・ブランド確定 | ✅ | revenue-kun / 収益還元クン |
| OSS リポジトリ公開 | ✅ | GitHub |
| Excel 出力機能実装済み | ✅ | PR #53/#54 merged |
| README 整備済み | ✅ | PR #55 merged |
| 合成サンプル検証済み | ✅ | SAMPLE_EXCEL_OUTPUT_AFTER_V041.md |
| LP 公開 | ❌ | 本プランの実装後 |
| qualifying real-world PDF 評価 | ❌ | Issue #21 open |
| OCR / 複雑 PDF 対応 | ❌ | 未実装（対象外） |
| 免責・コンプライアンス確認 | ⚠️ | LP 作成時に弁護士等への確認を推奨 |
| CTA（問い合わせ先）の準備 | ⚠️ | メールアドレスまたはフォーム設置が必要 |

**PR TIMES 配信の推奨タイミング**:
- LP 公開後（Section 7 の Limitations を LP に掲載した上で）
- CTA（問い合わせ先）が機能する状態になってから
- qualifying real-world PDF 評価の完了は PR TIMES 配信の必須条件ではないが、
  配信文中に「実務検証済み」を含めてはならない

---

## 12. Next Implementation Steps

| # | タスク | 優先度 | 依存 |
|---|--------|--------|------|
| 1 | LP ページ構造の HTML/CSS 実装 | 高 | 本プラン承認後 |
| 2 | 合成サンプルのスクリーンショット取得（合成データのみ） | 高 | — |
| 3 | Disclaimer セクションの文言最終確認（弁護士等への確認推奨） | 高 | — |
| 4 | CTA（GitHub / フォーム / メール）の設置 | 高 | — |
| 5 | GA4 / Search Console の設置 | 中 | LP 公開後 |
| 6 | PR TIMES プレスリリース原稿作成 | 中 | LP 公開後 |
| 7 | note / LinkedIn / X 告知コンテンツ作成 | 中 | LP 公開後 |
| 8 | qualifying real-world PDF 評価（Issue #21） | 中 | サンプル PDF 入手次第 |
| 9 | OCR / 複数ページ対応（Issue #19 以降） | 低 | Issue #21 完了後 |
| 10 | Claude Skill 統合リリース | 低 | 別途検討 |

---

*Created: 2026-06-16*  
*Based on: main HEAD `c4b32f5` (PR #56 merged)*  
*No implementation code modified. Doc planning only.*  
*#19 remains open  #21 remains open  Issue #22 is completed  #48 remains open*
