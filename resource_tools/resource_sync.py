"""ArkScreenResource 图片同步脚本的公共能力。"""

from __future__ import annotations

import hashlib
import json
import struct
import time
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "ArkScreenResource-updater/1.0"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def fetch_bytes(url: str, attempts: int = 3) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            with urlopen(request, timeout=60) as response:
                return response.read()
        except Exception as error:
            last_error = error
            if attempt + 1 < attempts:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"下载失败：{url}") from last_error


def fetch_json(url: str) -> dict:
    return json.loads(fetch_bytes(url).decode("utf-8"))


def png_info(content: bytes, source: str) -> tuple[int, int]:
    if len(content) < 24 or content[:8] != PNG_SIGNATURE or content[12:16] != b"IHDR":
        raise ValueError(f"不是有效 PNG：{source}")
    width, height = struct.unpack(">II", content[16:24])
    if width <= 0 or height <= 0 or width > 4096 or height > 4096:
        raise ValueError(f"PNG 尺寸异常：{source} -> {width}x{height}")
    return width, height


def file_record(file_name: str, source_url: str, content: bytes) -> dict:
    width, height = png_info(content, file_name)
    return {
        "file": file_name,
        "sourceUrl": source_url,
        "sha256": hashlib.sha256(content).hexdigest(),
        "width": width,
        "height": height,
        "bytes": len(content),
    }


def print_list(title: str, values: list[str]) -> None:
    print(f"{title}（{len(values)}）：{', '.join(values) if values else '无'}")
