# AGENTS.md

OpenAI Codex 等のエージェントは、作業前に本ファイルを読むこと。

## Project
revenue-kun: research/validation OSS CLI & Skill for real-estate direct-capitalization
income estimation. Parses rent-roll inputs (CSV / text-based PDF) and generates an
inspectable Excel workbook. Not a commercial SaaS, not a completed appraisal product.

## Guardrails（正本）
スコープ・必須用語・禁止表現は GUARDRAILS.md を参照し、それに従う。要点：
- 出力は「収益試算値」。鑑定評価・収益価格ではない。
- OCR / 投資助言 / 法律助言 / 完全自動化 は対象外。
- 実物件 PDF 検証は未完（Issue #21）。「実務検証済み」と表記しない。
- 数値（還元利回り等）を提案しない。欠損は補完しない。

## How to run
Entrypoint: `python src/main.py`. 検証用サンプル：
    python src/main.py \
      --assumptions assumptions.sample.yaml \
      --rent-roll-pdf data/sample_rentroll_simple.pdf \
      --output ./output \
      --excel-output ./output/direct_cap.xlsx

## Tests
挙動を主張する前に必ず `python -m pytest -q` を実行し、緑であることを確認する。

## Workflow rules
1. 変更前に branch / status / 関連 issue を確認。
2. README と現行リリースノートを読む。
3. CLI エントリポイントを確認してからコマンドを提案。
4. テストを通してから挙動を主張。
5. 検証範囲を超える公開クレームをしない。

## Distribution（混同しないこと）
- claude.ai / Cowork 向け：`skill/`（パッケージ Skill。エンジンを vendor し SKILL.md から起動）。
- Codex 向け：`.agents/skills/revenue-kun/`（repo 内で `src/` を直接呼ぶ。エンジンを複製しない）。
- `.claude/skills/` は作らない（旧 Option C・DEC-04 で撤回済み）。
