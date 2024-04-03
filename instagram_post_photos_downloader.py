"""從 IG 下載照片"""

import logging
from datetime import datetime

import fire
import requests
from configobj import ConfigObj

from libs.utils.save_photo import save_photo
from libs.utils.get_image_file_index import get_image_file_index
from libs.utils.get_path_prefix import get_path_prefix

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(filename)s %(levelname)s %(message)s"
)

POST_URL = "?__a=1&__d=dis"


class InstagramPostPhotosDownloader:
    def __init__(self, path_dir: str) -> None:
        self.__header = self.__get_header()

        self.__path_dir = path_dir
        # 取得路徑下的檔案路徑的所有照片計算 index
        self.__file_index = get_image_file_index(self.__path_dir)

    def __get_header(self) -> dict:
        """讀取 config 並產出 header"""
        ig_config = ConfigObj("./config/ig_config.ini")["INSTAGRAM_CONFIG"]
        return {
            "Cookie": (
                f"ds_user_id={ig_config["ds_user_id"]}; "
                f'shbid="{ig_config["shbid"]}"'
            )
        }

    def get_file_index(self) -> dict:
        """取得 file_index"""
        return self.__file_index

    def set_file_index(self, file_index: dict) -> None:
        """設定 file_index"""
        self.__file_index = file_index

    def download(
        self,
        post_url: str,
        path_prefix: str = "",
    ) -> None:
        """
        下載貼文的所有照片
        params:
        - post_url: str, 貼文網址
        - path_dir: str, 指定的下載路徑
        - path_prefix(optional): str, 指定的檔名 prefix
        """
        requset_url = f"{post_url}{POST_URL}"
        logging.info("Download from post: %s", requset_url)
        response = requests.get(
            url=requset_url,
            headers=self.__header,
            timeout=60,
        )
        assert (
            response.status_code == 200
        ), f"GET response not 200, get response: {response.json()}"

        # 從回傳中取得最大解析度的照片
        item = response.json()["items"].pop()
        timestamp = item["device_timestamp"]
        carousel_media = item["carousel_media"]
        all_image_url = [
            max(
                c["image_versions2"]["candidates"],
                key=lambda x: x["width"] + x["height"],
            )["url"]
            for c in carousel_media
        ]

        owner = item["owner"]["username"]
        path_prefix = get_path_prefix(path_prefix, [owner])
        logging.info(f"path_prefix: {path_prefix}")

        for url in all_image_url:
            local_path = self.__get_local_path(path_prefix, timestamp)
            logging.info("Image url: %s", url)
            logging.info("Save To: %s", local_path)
            save_photo(url, local_path)

    def __get_local_path(
        self,
        path_prefix: str,
        timestamp: int,
    ) -> str:
        """取得本地儲存照片路徑與檔名"""
        # 如果有指定 prefix 就加上 -
        date = datetime.fromtimestamp(timestamp=timestamp / 1000000).strftime("%y%m%d")
        path_prefix = f"{path_prefix}-" if path_prefix else ""
        file_name = f"{path_prefix}{date}"

        # 若資料夾中已經有該照片名，則將 index+1 並做為新的照片 index
        if file_name in self.__file_index:
            self.__file_index[file_name] += 1
            index = self.__file_index[file_name]
        else:
            index = self.__file_index[file_name] = 0

        return f"{self.__path_dir}/{file_name}-{index}.jpg"


if __name__ == "__main__":
    fire.Fire(InstagramPostPhotosDownloader)
