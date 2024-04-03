"""讀取本地 chrome 書籤，並下載整個資料夾網頁的照片"""

import json
import logging

import fire
from configobj import ConfigObj

from x_post_photos_downloader import XPostPhotosDownloader
from instagram_post_photos_downloader import InstagramPostPhotosDownloader

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(filename)s %(levelname)s %(message)s"
)

BOOKMARK_CONFIG_PATH = "./config/bookmark.ini"


class DownloadThroughBookmark:
    def __init__(self, path_dir: str) -> None:
        config = ConfigObj(BOOKMARK_CONFIG_PATH, encoding="utf-8")["BOOKMARK"]

        with open(config["path"], "r", encoding="utf-8") as f:
            bookmarks: dict = json.loads(f.read())["roots"]

        folder = self.__get_folder(
            bookmarks, bookmark_dir=config["bookmark_dir"].split("/")
        )

        self.__urls = [item["url"] for item in folder]

        self.__x_post_photos_downloader = XPostPhotosDownloader(path_dir)
        self.__ig_post_photos_downloader = InstagramPostPhotosDownloader(path_dir)

    def __get_folder(self, bookmarks: dict, bookmark_dir: list):
        """根據給定的 bookmark_dir 取得指定的資料夾"""
        # 找到指定資料夾
        current_bookmark = list(bookmarks.values())
        for dir in bookmark_dir:
            tmp_current_bookmark = current_bookmark.copy()
            for bookmark in current_bookmark:
                if bookmark["name"] == dir:
                    current_bookmark = bookmark["children"]
                    break
            assert (
                tmp_current_bookmark != current_bookmark
            ), f"沒有找到指定的資料夾: {bookmark_dir}"
        return current_bookmark

    def download(self) -> None:
        """下載資料夾下所有網址的照片"""
        file_index = self.__x_post_photos_downloader.get_file_index()
        for url in self.__urls:
            if "instagram" in url:
                self.__ig_post_photos_downloader.set_file_index(file_index)
                self.__ig_post_photos_downloader.download(url)
                file_index = self.__ig_post_photos_downloader.get_file_index()
            elif "twitter" in url:
                self.__x_post_photos_downloader.set_file_index(file_index)
                self.__x_post_photos_downloader.download(url)
                file_index = self.__x_post_photos_downloader.get_file_index()
            else:
                logging.info(f"未知的網址: {url}")


if __name__ == "__main__":
    fire.Fire(DownloadThroughBookmark)
