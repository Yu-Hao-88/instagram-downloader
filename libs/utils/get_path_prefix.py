"""實作共用的 path prefix"""

from pathlib import Path
from configobj import ConfigObj

PREFIX_CONFIG_PATH = "./config/prefix_config.ini"


def get_path_prefix(path_prefix: str, tags: list) -> str:
    """取得 path_prefix，若是 tags 包含在 prefix_accept 中就回傳指定的 prefix"""
    if path_prefix:
        return path_prefix

    if Path(PREFIX_CONFIG_PATH).exists():
        config: dict = ConfigObj(PREFIX_CONFIG_PATH, encoding="utf-8")["PREFIX_CONFIG"]
        for prefix, prefix_accept in config.items():
            if bool(set(prefix_accept) & set(tags)):
                return prefix

    return ""
