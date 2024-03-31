"""從 IG 下載照片"""

import logging
from datetime import datetime

import fire
import requests
from configobj import ConfigObj

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(filename)s %(levelname)s %(message)s"
)

POST_URL = "?__a=1&__d=dis"


class InstagramPostPhotosDownloader:
    def __init__(self) -> None:
        self.__header = self.__get_header()

    def __get_header(self) -> dict:
        """讀取 config 並產出 header"""
        ig_config = ConfigObj("./config/ig_config.ini")["INSTAGRAM_CONFIG"]
        return {
            "Cookie": (
                f"ds_user_id={ig_config["ds_user_id"]}; "
                f'shbid="{ig_config["shbid"]}"'
            )
        }

    def download(
        self,
        post_url: str,
        path_dir: str,
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

        for i, url in enumerate(all_image_url):
            local_path = self.__get_local_path(
                path_dir, path_prefix, timestamp, index=i
            )
            logging.info("Image url: %s", url)
            logging.info("Save To: %s", local_path)
            self.__save_photo(url, local_path)

    def __get_local_path(
        self,
        path_dir: str,
        path_prefix: str,
        timestamp: int,
        index: int,
    ) -> str:
        """取得本地儲存照片路徑與檔名"""
        # 如果有指定 prefix 就加上 -
        path_prefix = f"{path_prefix}-" if path_prefix else ""
        date = datetime.fromtimestamp(timestamp=timestamp / 1000000).strftime("%y%m%d")
        return f"{path_dir}/{path_prefix}{date}-{index}.jpg"

    def __save_photo(self, image_url: str, local_path: str) -> None:
        """將單一張照片儲存到本地"""
        img_data = requests.get(image_url).content
        with open(local_path, "wb") as handler:
            handler.write(img_data)


if __name__ == "__main__":
    fire.Fire(InstagramPostPhotosDownloader)
