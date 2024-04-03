"""共用的 save photo"""

import requests
from pathlib import Path


def save_photo(image_url: str, local_path: str) -> None:
    """將單一張照片儲存到本地"""
    img_data = requests.get(image_url).content

    assert not Path(local_path).exists(), f"此路徑已有照片: {local_path}"
    with open(local_path, "wb") as handler:
        handler.write(img_data)
