# V0.2.0 Release Completion Note

**Project**: revenue-kun  
**Version**: v0.2.0  
**Date**: 2026-06-12  
**Status**: Released  

---

## Release Information

| 項目 | 内容 |
|------|------|
| Release URL | https://github.com/signal-yield/revenue-kun/releases/tag/v0.2.0 |
| tag | `v0.2.0` |
| Target branch | `main` |
| Target commit | `de61ee5` (`chore: bump version to v0.2.0`) |
| draft | `false` |
| prerelease | `false` |

---

## 完了済み作業

| # | 作業 | commit / SHA | 状態 |
|---|------|-------------|------|
| 1 | Acceptance report 作成 (`V020_PDF_INGESTION_ACCEPTANCE_REPORT.md`) | `c7cc2bf` | ✅ |
| 2 | README 更新（PDF ingestion 対応範囲・非対応範囲・safe failure 明記） | `d9d7ebf` | ✅ |
| 3 | CHANGELOG 更新（v0.2.0 Added / Changed / Fixed / Limitations） | `63361c3` | ✅ |
| 4 | Version bump（`VERSION` → `v0.2.0`、`__init__.py` → `"0.2.0"`） | `de61ee5` | ✅ |
| 5 | git tag `v0.2.0` 作成・push | `v0.2.0` | ✅ |
| 6 | GitHub Release v0.2.0 publish | release id `338470293` | ✅ |

---

## v0.2.0 対応範囲

本バージョンは **text-based PDF の単純なレントロール表への限定対応** です。実物PDF全面対応ではありません。

### 対応（Supported）

- text-based PDF（PyMuPDF で直接テキスト抽出可能なもの）の単純なレントロール表
- canonical key / 列名エイリアス mapping（Issue #7 / PR #10）
- 小見出し行・繰り返しヘッダー行の除外（Issue #6 / PR #9）
- safe failure handling（silent failure の排除、`failure_reason` の machine-readable 記録）（Issue #8 / PR #11）

### 非対応（Not Supported）

- OCR
- スキャンPDF
- 複数ページのテーブル結合
- 複雑な結合セル
- ベンダー固有ヒューリスティック
- PII マスキング
- 鑑定評価・投資助言・法律助言

---

## Version 整合性確認

| ファイル | version |
|---------|---------|
| `VERSION` | `v0.2.0` |
| `src/revenue_kun/__init__.py` | `"0.2.0"` |
| `README.md` | `v0.2.0` |
| `CHANGELOG.md` | `[v0.2.0] — 2026-06-12` |

---

## Test Results（v0.2.0 時点）

| タイミング | テスト数 | 結果 |
|-----------|---------|------|
| PR #9 merge 時点 | 42 | 42/42 PASSED |
| PR #10 merge 時点 | 80 | 80/80 PASSED |
| PR #11 merge 時点 | 84 | 84/84 PASSED |
| version bump 後 | 84 | 84/84 PASSED |

---

## 次バージョン候補

| バージョン | 方針 |
|-----------|------|
| **v0.2.1** | bugfix only（v0.2.0 で判明した不具合があれば対応） |
| **v0.3.0** | 追加の実物PDF評価 / CLI UX 改善 / サンプル戦略の見直し |

将来 Issue 候補（v0.2.0 でスコープ外とした項目）：

- OCR / スキャンPDF対応
- 複数ページテーブル結合
- PII マスキング自動化
