"""sync_claude_plugin_skill.py — Claude Code Plugin 内の Skill を skill/ から同期生成する。

正本は skill/（Claude.ai / Cowork 向け Skill）。
Claude Code Plugin 側の Skill（claude-plugins/revenue-kun/skills/revenue-kun/）は
本スクリプトによる一方向の同期生成物であり、手作業で編集しない。

使い方:
    python scripts/sync_claude_plugin_skill.py            # 同期を実行
    python scripts/sync_claude_plugin_skill.py --check    # 差分の有無だけ確認（書き込みしない）

同期対象（skill/ 配下のうち、以下のみ）:
    SKILL.md
    requirements.txt
    scripts/            （__pycache__・*.pyc は除外）
    samples/assumptions.sample.yaml

同期しないもの:
    skill/out/                      （生成物・.gitignore 対象）
    skill/tests/                    （開発用テスト、配布物ではない）
    skill/samples/*.pdf             （合成サンプルPDFであっても、Pluginパッケージには一切同梱しない）
    __pycache__ / *.pyc             （キャッシュ）

--check は生成先の内容を正本と比較し、一致しなければ終了コード 1、一致すれば 0 で終了する。
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_SRC = ROOT / "skill"
PLUGIN_SKILL_DST = ROOT / "claude-plugins" / "revenue-kun" / "skills" / "revenue-kun"

# 同梱を禁止する拡張子（private data / 生成物混入防止）
FORBIDDEN_SUFFIXES = {".pdf", ".xlsx", ".xls", ".csv"}

# skill/ 配下からコピーするファイル（相対パス）
FILES_TO_SYNC = [
    "SKILL.md",
    "requirements.txt",
    "samples/assumptions.sample.yaml",
]

# skill/ 配下からコピーするディレクトリ（相対パス、再帰的）
DIRS_TO_SYNC = [
    "scripts",
]


def _should_skip(path: Path) -> bool:
    if path.suffix.lower() in FORBIDDEN_SUFFIXES:
        return True
    if "__pycache__" in path.parts:
        return True
    if path.suffix == ".pyc":
        return True
    return False


def _collect_source_files() -> dict[str, Path]:
    """正本 (skill/) からコピーすべき相対パス -> 実ファイルパス の辞書を作る。"""
    mapping: dict[str, Path] = {}

    for rel in FILES_TO_SYNC:
        src = SKILL_SRC / rel
        if not src.exists():
            raise FileNotFoundError(f"正本に存在しません: {src}")
        mapping[rel] = src

    for rel_dir in DIRS_TO_SYNC:
        src_dir = SKILL_SRC / rel_dir
        if not src_dir.exists():
            raise FileNotFoundError(f"正本に存在しません: {src_dir}")
        for src_file in src_dir.rglob("*"):
            if src_file.is_dir():
                continue
            if _should_skip(src_file):
                continue
            rel = src_file.relative_to(SKILL_SRC).as_posix()
            mapping[rel] = src_file

    return mapping


def _collect_dest_files() -> dict[str, Path]:
    """現在の生成先にある相対パス -> 実ファイルパス の辞書を作る。"""
    mapping: dict[str, Path] = {}
    if not PLUGIN_SKILL_DST.exists():
        return mapping
    for dst_file in PLUGIN_SKILL_DST.rglob("*"):
        if dst_file.is_dir():
            continue
        if _should_skip(dst_file):
            continue
        rel = dst_file.relative_to(PLUGIN_SKILL_DST).as_posix()
        mapping[rel] = dst_file
    return mapping


def check() -> bool:
    """正本と生成先を比較する。一致すれば True、不一致なら False。差分を stdout に表示する。"""
    source_map = _collect_source_files()
    dest_map = _collect_dest_files()

    source_keys = set(source_map)
    dest_keys = set(dest_map)

    missing = sorted(source_keys - dest_keys)
    extra = sorted(dest_keys - source_keys)
    changed = sorted(
        rel for rel in (source_keys & dest_keys)
        if source_map[rel].read_bytes() != dest_map[rel].read_bytes()
    )

    ok = not missing and not extra and not changed

    if missing:
        print("[missing] 生成先に存在しないファイル:")
        for rel in missing:
            print(f"  - {rel}")
    if extra:
        print("[extra] 生成先にのみ存在する不要なファイル:")
        for rel in extra:
            print(f"  - {rel}")
    if changed:
        print("[changed] 内容が正本と一致しないファイル:")
        for rel in changed:
            print(f"  - {rel}")

    if ok:
        print(f"OK: {PLUGIN_SKILL_DST} は skill/ と一致しています（{len(source_keys)} ファイル）。")
    else:
        print("NG: skill/ と一致していません。python scripts/sync_claude_plugin_skill.py を実行してください。")

    return ok


def sync() -> None:
    """正本を生成先へコピーし、生成先だけに残っている不要なファイルを削除する。"""
    source_map = _collect_source_files()

    if PLUGIN_SKILL_DST.exists():
        shutil.rmtree(PLUGIN_SKILL_DST)

    for rel, src in source_map.items():
        dst = PLUGIN_SKILL_DST / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    print(f"synced {len(source_map)} files: skill/ -> {PLUGIN_SKILL_DST}")


def main() -> int:
    if "--check" in sys.argv[1:]:
        return 0 if check() else 1
    sync()
    return 0


if __name__ == "__main__":
    sys.exit(main())
