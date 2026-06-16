"""build_skill.py — skill/ バンドルを src/ から生成する。

使い方:
  python build_skill.py

src/revenue_kun/ -> skill/scripts/revenue_kun/
src/main.py      -> skill/scripts/main.py

ロジックには触れない。import パスは src/main.py の sys.path.insert が
skill/scripts/ でもそのまま動くため変更不要。
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC_PKG = ROOT / "src" / "revenue_kun"
SRC_MAIN = ROOT / "src" / "main.py"
DST_SCRIPTS = ROOT / "skill" / "scripts"
DST_PKG = DST_SCRIPTS / "revenue_kun"
DST_MAIN = DST_SCRIPTS / "main.py"


def build() -> None:
    if DST_PKG.exists():
        shutil.rmtree(DST_PKG)
    shutil.copytree(SRC_PKG, DST_PKG)
    shutil.copy2(SRC_MAIN, DST_MAIN)
    print(f"skill/scripts/revenue_kun/ <- src/revenue_kun/ ({len(list(DST_PKG.rglob('*.py')))} .py files)")
    print(f"skill/scripts/main.py     <- src/main.py")
    print("build OK")


if __name__ == "__main__":
    build()
    sys.exit(0)
