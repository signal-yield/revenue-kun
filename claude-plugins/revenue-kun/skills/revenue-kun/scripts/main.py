"""revenue-kun エントリポイント。

実行例:
  python src/main.py --assumptions assumptions.sample.yaml --output ./output
  python src/main.py --assumptions assumptions.sample.yaml --rent-roll-pdf data/sample_rentroll.pdf --output ./output
"""
from __future__ import annotations

import sys
from pathlib import Path

# `python src/main.py` で直接起動された場合に src/ を import パスへ追加する
sys.path.insert(0, str(Path(__file__).resolve().parent))

from revenue_kun.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
