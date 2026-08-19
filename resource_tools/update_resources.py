#!/usr/bin/env python3
"""预览或更新 ArkScreenResource 的模组与副职业图标。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from resource_tools.update_equip import synchronize as synchronize_equip
from resource_tools.update_subprofession import synchronize as synchronize_subprofession


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    print(f"ArkScreenResource：{'写入' if args.write else '预览'}模式\n")
    print("[1/2] 模组图标")
    synchronize_equip(args.write)
    print("\n[2/2] 副职业图标")
    synchronize_subprofession(args.write)


if __name__ == "__main__":
    main()
