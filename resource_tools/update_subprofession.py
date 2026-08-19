#!/usr/bin/env python3
"""从 PRTS 分支一览补全副职业图标。"""

from __future__ import annotations

import argparse
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from resource_tools.resource_sync import (
    ROOT,
    fetch_bytes,
    file_record,
    print_list,
)

SUBPROFESSION_DIR = ROOT / "subprofession"
PAGE_URL = "https://m.prts.wiki/w/%E5%88%86%E6%94%AF%E4%B8%80%E8%A7%88"


class BranchIconParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.icons: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "img":
            return
        data = dict(attrs)
        name = (data.get("alt") or "").strip()
        source = (data.get("src") or "").strip()
        if not name or "职业分支图标_" not in unquote(source):
            return
        parts = urlsplit(source)
        clean_source = urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
        previous = self.icons.get(name)
        if previous and previous != clean_source:
            raise ValueError(f"分支 {name} 出现多个不同图标 URL")
        self.icons[name] = clean_source


def parse_branch_icons(html: str) -> dict[str, str]:
    parser = BranchIconParser()
    parser.feed(html)
    if not parser.icons:
        raise ValueError("PRTS 分支一览没有解析出图标")
    return parser.icons


def synchronize(write: bool) -> None:
    icons = parse_branch_icons(fetch_bytes(PAGE_URL).decode("utf-8"))
    expected_names = {f"{name}.png" for name in icons}
    existing = {path.name for path in SUBPROFESSION_DIR.glob("*.png")}
    missing = sorted(expected_names - existing)
    downloaded: dict[str, bytes] = {}
    for file_name in missing:
        name = Path(file_name).stem
        content = fetch_bytes(icons[name])
        file_record(file_name, icons[name], content)
        downloaded[file_name] = content

    for name, url in sorted(icons.items()):
        file_name = f"{name}.png"
        content = downloaded.get(file_name)
        if content is None:
            content = (SUBPROFESSION_DIR / file_name).read_bytes()
        file_record(file_name, url, content)

    extra = sorted(existing - expected_names)
    print(f"PRTS 职业分支：{len(icons)}；本地图标：{len(existing)}")
    print_list("待下载", missing)
    print_list("本地多余（不删除）", extra)

    if not write:
        print("当前为预览模式；确认后使用 --write 写入。")
        return
    for file_name, content in downloaded.items():
        (SUBPROFESSION_DIR / file_name).write_bytes(content)
    print(f"已下载 {len(downloaded)} 张副职业图标。")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    synchronize(args.write)


if __name__ == "__main__":
    main()
