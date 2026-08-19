#!/usr/bin/env python3
"""从 PRTS 干员模组一览补全 App 使用的模组方向图标。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from urllib.parse import quote, urlencode

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from resource_tools.resource_sync import (
    ROOT,
    fetch_json,
    fetch_bytes,
    file_record,
    print_list,
)

EQUIP_DIR = ROOT / "equip"
PAGE_URL = "https://prts.wiki/w/干员模组一览"
API_URL = "https://m.prts.wiki/api.php"
ASSET_BASE = "https://torappu.prts.wiki/assets/uniequip_direction/"


def fetch_type_icons() -> set[str]:
    offset = 0
    result: set[str] = set()
    while True:
        query = urlencode({
            "action": "cargoquery",
            "format": "json",
            "limit": "5000",
            "offset": str(offset),
            "tables": "char_mod",
            "fields": "typeIcon=typeIcon",
        })
        rows = fetch_json(f"{API_URL}?{query}").get("cargoquery", [])
        for row in rows:
            value = str(row.get("title", {}).get("typeIcon", "")).strip().lower()
            if value:
                result.add(value)
        if len(rows) < 5000:
            break
        offset += len(rows)
    if not result:
        raise ValueError("PRTS char_mod 没有返回任何 typeIcon")
    return result


def synchronize(write: bool) -> None:
    type_icons = fetch_type_icons()
    expected = {
        f"{type_icon.upper()}_icon.png": (
            ASSET_BASE + quote(type_icon, safe="-_.") + ".png",
            type_icon,
        )
        for type_icon in type_icons
    }
    local_icons = {path.name for path in EQUIP_DIR.glob("*_icon.png")}
    missing = sorted(expected.keys() - local_icons)
    extra = sorted(local_icons - expected.keys())
    downloaded: dict[str, bytes] = {}
    for file_name in missing:
        url, _ = expected[file_name]
        content = fetch_bytes(url)
        file_record(file_name, url, content)  # 写入前先验证下载内容。
        downloaded[file_name] = content

    for file_name, (url, _) in sorted(expected.items()):
        content = downloaded.get(file_name)
        if content is None:
            content = (EQUIP_DIR / file_name).read_bytes()
        file_record(file_name, url, content)
    print(f"PRTS 模组类型：{len(type_icons)}；本地图标：{len(local_icons)}")
    print_list("待下载", missing)
    print_list("本地多余（不删除）", extra)

    if not write:
        print("当前为预览模式；确认后使用 --write 写入。")
        return
    for file_name, content in downloaded.items():
        (EQUIP_DIR / file_name).write_bytes(content)
    print(f"已下载 {len(downloaded)} 张模组图标。")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    synchronize(args.write)


if __name__ == "__main__":
    main()
