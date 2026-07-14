# revenue-kun — Claude Code Marketplace Submission Checklist

## 事前確認（ローカル）

- [ ] `claude plugin validate ./claude-plugins/revenue-kun --strict` が成功する
- [ ] `claude plugin validate . --strict`（marketplace.json）が成功する
- [ ] `python scripts/sync_claude_plugin_skill.py --check` が終了コード0で成功する
- [ ] `python -m pytest -q` が全件成功する
- [ ] `python -m pytest skill/tests/ -q` が全件成功する
- [ ] `python -m pytest tests/test_claude_plugin_packaging.py -q` が全件成功する
- [ ] `VERSION` / `src/revenue_kun/__init__.py` / `plugin.json` / `marketplace.json` のversionが一致している
- [ ] `claude-plugins/revenue-kun/` 配下に `.pdf` / `.xlsx` / `.xls` / `.csv` が一切含まれていない
- [ ] 「収益価格を算定します」「OCRに対応しています」「hosted SaaSとして利用できます」等の肯定的な禁止表現が含まれていない
- [ ] 「収益価格ではありません」「OCRには対応していません」「hosted SaaSではありません」等の否定文脈の記述が存在する

## Marketplace掲載前の確認

- [ ] `README.md`・`LICENSE` がリポジトリに存在する
- [ ] `docs/claude-code-plugin/SECURITY_AND_PRIVACY.md` が存在する
- [ ] `MARKETPLACE_JA.md` / `MARKETPLACE_EN.md` の内容が最新版（v0.5.2）と整合している
- [ ] Release v0.5.2 のURLが有効
- [ ] 公式LP（GitHub Pages）のURLが有効

## 申請時に人手で入力する項目（公式仕様上、自動化できない、または未確認）

- [ ] コミュニティMarketplace申請フォーム（claude.ai または Console）へのログイン・組織紐付け
  - claude.ai: `claude.ai/admin-settings/directory/submissions/plugins/new`（Team/Enterprise組織かつdirectory management権限が必要）
  - Console: `platform.claude.com/plugins/submit`（個人開発者向け）
- [ ] 提出直前の `claude plugin validate` 実行結果の最終確認（審査パイプラインも同じチェックを実行する）
- [ ] icon／logo：Anthropicの公式公開仕様で必須／任意・形式・寸法が確認できなかったため、要求された場合のみ事後対応
- [ ] publisher verification：制度の詳細が公式公開仕様で確認できなかったため、フォーム側の指示に従う

## 公式Marketplace（`claude-plugins-official`）について

申請フォームは存在しません。Anthropicの裁量による選定のみです。今回のタスクでは対象外とし、コミュニティMarketplaceへの申請導線のみを整備しています。

## 未確認・残課題

- icon/logoの公式要件
- shell実行／local file accessの宣言用の専用フィールド（公式schemaに存在せず）
- publisher verification制度の詳細
- Claude Code Desktop UIでのGUIベースの動作確認（本タスクではCLI経由の確認のみ実施）
