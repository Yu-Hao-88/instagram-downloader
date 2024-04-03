"""取得指定資料夾中的照片名稱，並分類各有幾張"""

import os
import re
from collections import defaultdict

FILE_NAME_PATTERN = r"(.*)\..*"


def get_image_file_index(path_dir: str) -> dict:
    """讀取資料夾並根據 prefix 分類"""
    image_file_index = defaultdict(int)

    for file_name in os.listdir(path_dir):
        file_name = re.search(FILE_NAME_PATTERN, file_name).group(1)
        split_file_name = file_name.split("-")
        # 如果最後一個是 1~4 個數字組成的代表是有幾張
        if re.search(r"\b\d{1,4}\b", split_file_name[-1]):
            image_name = "-".join(split_file_name[:-1])
            # 判斷最大的值
            image_file_index[image_name] = max(
                image_file_index[image_name], int(split_file_name[-1])
            )
        else:
            image_name = "-".join(split_file_name)
            # 如果沒有 index 就設為 0
            image_file_index[image_name] = max(image_file_index[image_name], 0)

    return image_file_index
