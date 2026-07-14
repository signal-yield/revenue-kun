from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".agents" / "skills" / "revenue-kun"
TARGET = ROOT / "plugins" / "revenue-kun" / "skills" / "revenue-kun"


def sync(check: bool = False) -> int:
    if not SOURCE.is_dir():
        raise SystemExit(f"canonical skill not found: {SOURCE}")

    source_files = sorted(p.relative_to(SOURCE) for p in SOURCE.rglob("*") if p.is_file())
    target_files = sorted(p.relative_to(TARGET) for p in TARGET.rglob("*") if p.is_file()) if TARGET.exists() else []

    if check:
        if source_files != target_files:
            print("plugin skill file list is out of sync")
            return 1
        for relative in source_files:
            if (SOURCE / relative).read_bytes() != (TARGET / relative).read_bytes():
                print(f"plugin skill differs from canonical source: {relative}")
                return 1
        print("Codex plugin skill is in sync")
        return 0

    if TARGET.exists():
        shutil.rmtree(TARGET)
    shutil.copytree(SOURCE, TARGET)
    print(f"synced {SOURCE} -> {TARGET}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync the canonical Codex skill into the distributable plugin package.")
    parser.add_argument("--check", action="store_true", help="fail when the generated plugin copy is stale")
    args = parser.parse_args()
    return sync(check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
