# GUARDRAILS.md — revenue-kun 横断ガードレール（全エージェント共通の正本）

本ファイルは Claude Code（CLAUDE.md）・OpenAI Codex（AGENTS.md）・各 SKILL.md が参照する単一の正本。
スコープ・用語・禁止表現はここを真とし、各指示ファイルでは複製せず参照する。

## 製品ポジション
revenue-kun は研究・検証用の OSS。直接還元法による不動産「収益試算」CLI / Skill。
商用 SaaS でも、完成した鑑定プロダクトでもない。

## スコープ内
- text-based レントロール PDF / CSV / 構造化入力の読み取り
- GPI / EGI / NOI / 純収益 / 収益試算値の算定（直接還元法）
- Excel ワークブック出力（OER 自己計算モデル）
- 透明性・検証可能性・欠損の明示

## スコープ外
- OCR / スキャン PDF
- 鑑定評価・収益価格（鑑定評価額）の提示
- 投資助言・法律助言・税務助言
- 実物件 PDF の完全自動処理 / qualifying real-world PDF 検証（Issue #21 未完）

## 必須用語
- 出力は常に「収益試算値（direct-capitalization revenue estimate）」。
- 「収益価格（鑑定評価額）」を肯定文脈で使わない。
- 還元利回り・経費率・空室損失率等の数値を提案・例示・初期値設定しない（ユーザー入力に委ねる）。
- 欠損は補完しない（missing_info に記録）。

## 禁止表現
- 「鑑定評価対応」「投資判断支援」「完全自動化」「OCR 対応」
- 「実務検証済み」「qualifying real-world PDF verified」
- 「Claude Skill / Codex Skill リリース済み」（実パッケージ＆検証前）
- 「Claude / Codex 完全互換」「全 AI エージェント対応」「主要エージェント全対応」
- マルチエージェント対応は「整備中」「双方で扱えるよう整備中」に留める（検証完了まで）
