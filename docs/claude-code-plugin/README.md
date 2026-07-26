# revenue-kun — Claude Code Plugin

Claude Code向けに revenue-kun をパッケージ化した Plugin です。対象は **Claude Code のみ**です（Codex向けPluginは `plugins/revenue-kun/` を参照してください。両者は独立しています）。

## 構成

```
.claude-plugin/marketplace.json                 # リポジトリルート。GitHub owner/repo での marketplace 追加に必要
claude-plugins/revenue-kun/
├── .claude-plugin/plugin.json                  # Claude Code 公式 plugin manifest
└── skills/revenue-kun/
    ├── SKILL.md                                # skill/SKILL.md からの同期生成物
    ├── requirements.txt                        # skill/requirements.txt からの同期生成物
    ├── samples/assumptions.sample.yaml         # skill/samples/assumptions.sample.yaml からの同期生成物
    └── scripts/                                # skill/scripts/ からの同期生成物（エンジン本体）
```

**正本は `skill/`（Claude.ai / Cowork 向け Skill）です。** `claude-plugins/revenue-kun/skills/revenue-kun/` は手作業で編集しないでください。同期は次のスクリプトで行います。

```bash
python scripts/sync_claude_plugin_skill.py          # 同期を実行
python scripts/sync_claude_plugin_skill.py --check  # 差分の有無だけ確認（CIでの検証用）
```

`--check` は不一致があれば終了コード1、一致すれば0で終了します。

Pluginパッケージには、私有物件PDF・実物件CSV・生成物Excel等の私有データは一切同梱しません（`.pdf` / `.xlsx` / `.xls` / `.csv` はすべて同期対象から除外されます）。

## インストール

```
/plugin marketplace add signal-yield/revenue-kun
/plugin install revenue-kun@revenue-kun
```

ローカルディレクトリからのテスト:

```
/plugin marketplace add ./
/plugin install revenue-kun@revenue-kun
```

## 有効化・無効化・アンインストール

```
/plugin enable revenue-kun@revenue-kun
/plugin disable revenue-kun@revenue-kun
/plugin uninstall revenue-kun@revenue-kun
```

Marketplaceごと削除する場合:

```
/plugin marketplace remove revenue-kun
```

## Validation

```bash
claude plugin validate ./claude-plugins/revenue-kun --strict
claude plugin validate . --strict
```

## 申請導線

- **公式Marketplace（`claude-plugins-official`）**: Anthropicの裁量選定のみで、申請フォームは存在しません。
- **コミュニティMarketplace（`claude-plugins-community`）**: 申請フォームあり。詳細は [MARKETPLACE_JA.md](./MARKETPLACE_JA.md) を参照してください。

## Security / Privacy

[SECURITY_AND_PRIVACY.md](./SECURITY_AND_PRIVACY.md) を参照してください。

## revenue-kun本体との関係

このPlugin化はパッケージング層のみです。CSV／PDF抽出ロジック・収益試算ロジック・Excel生成ロジック・Local Web UI・CLI・Docker・既存の本体テストには一切変更を加えていません。
