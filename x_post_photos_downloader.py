"""從 twitter 下載照片"""

import json
import re
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

RE_TWEET_ID_PATTERN = r"/status/(\d+)"


class XPostPhotosDownloader:
    def __init__(self, path_dir: str) -> None:
        self.__x_config = ConfigObj(
            "./config/x_config.ini",
            encoding="utf-8",
        )["X_CONFIG"]
        self.__path_dir = path_dir
        # 取得路徑下的檔案路徑的所有照片計算 index
        self.__file_index = get_image_file_index(self.__path_dir)

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

        # 提取貼文 ID
        tweet_id = re.search(RE_TWEET_ID_PATTERN, post_url).group(1)

        logging.info(f"tweet_id: {tweet_id}")

        # 獲取貼文的詳細資訊
        response = requests.get(
            url=self.__get_url(tweet_id),
            headers=self.__get_header(),
            timeout=5,
        )
        assert (
            response.status_code == 200
        ), f"GET response not 200, get response: {response.json()}"
        result = response.json()

        if result["data"]["tweetResult"]["result"]["__typename"] == "TweetUnavailable":
            logging.info("出現 TweetUnavailable，跳過這筆")
            return

        media_url_https = self.__get_media_url_https(result)
        logging.info(f"media_url_https: {media_url_https}")
        hash_tags = self.__get_hash_tag(result)
        logging.info(f"hash tags: {hash_tags}")
        path_prefix = get_path_prefix(path_prefix, hash_tags)
        logging.info(f"path_prefix: {path_prefix}")
        file_timestamp = self.__get_file_timestamp(result)
        logging.info(f"file_timestamp: {file_timestamp}")

        for url in media_url_https:
            local_path = self.__get_local_path(path_prefix, file_timestamp)
            logging.info("Image url: %s", url)
            logging.info("Save To: %s", local_path)
            save_photo(url, local_path)

    def __get_url(self, tweet_id: str) -> str:
        """取得 api 網址"""
        return (
            f"https://twitter.com/i/api/graphql/{self.__x_config["query_id"]}/TweetResultByRestId"
            f'?variables={json.dumps({"tweetId":tweet_id,"includePromotedContent":True,"withBirdwatchNotes":True,"withVoice":True,"withCommunity":True})}'
            f'&features={
                json.dumps(
                    {
                        "creator_subscriptions_tweet_preview_api_enabled":True,
                        "communities_web_enable_tweet_community_results_fetch":True,
                        "c9s_tweet_anatomy_moderator_badge_enabled":True,
                        "tweetypie_unmention_optimization_enabled":True,
                        "responsive_web_edit_tweet_api_enabled":True,
                        "graphql_is_translatable_rweb_tweet_is_translatable_enabled":True,
                        "view_counts_everywhere_api_enabled":True,"longform_notetweets_consumption_enabled":True,
                        "responsive_web_twitter_article_tweet_consumption_enabled":True,
                        "tweet_awards_web_tipping_enabled":False,
                        "freedom_of_speech_not_reach_fetch_enabled":True,
                        "standardized_nudges_misinfo":True,
                        "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":True,
                        "rweb_video_timestamps_enabled":True,
                        "longform_notetweets_rich_text_read_enabled":True,
                        "longform_notetweets_inline_media_enabled":True,
                        "rweb_tipjar_consumption_enabled":False,
                        "responsive_web_graphql_exclude_directive_enabled":True,
                        "verified_phone_label_enabled":False,
                        "responsive_web_graphql_skip_user_profile_image_extensions_enabled":False,
                        "responsive_web_graphql_timeline_navigation_enabled":True,
                        "responsive_web_enhance_cards_enabled":False,
                    }
                )
            }'
        )

    def __get_header(self) -> dict:
        """取得 header"""
        return {
            "Authorization": f"Bearer {self.__x_config["bearer_token"]}",
            "X-Csrf-Token": f"{self.__x_config["csrf_token"]}",
            "Cookie": (
                f"auth_token={self.__x_config["auth_token"]}; "
                f"ct0={self.__x_config["ct0"]}; "
            ),
        }

    def __get_media_url_https(self, result: dict) -> list:
        """解析回傳結果，取得所有 image url"""

        # 根據 __typename 從不同的路徑取得照片位置
        if (
            result["data"]["tweetResult"]["result"]["__typename"]
            == "TweetWithVisibilityResults"
        ):
            media = result["data"]["tweetResult"]["result"]["tweet"]["legacy"][
                "entities"
            ]["media"]

        elif result["data"]["tweetResult"]["result"]["__typename"] == "Tweet":
            media = result["data"]["tweetResult"]["result"]["legacy"]["entities"][
                "media"
            ]
        else:
            raise ValueError(
                f"出現了意料之外的 __typename: {result["data"]["tweetResult"]["result"]["__typename"]}"
            )

        return [f"{r["media_url_https"]}?name=orig" for r in media]

    def __get_hash_tag(self, result: dict) -> list:
        """解析回傳結果，取得所有 hashtag"""
        # 根據 __typename 從不同的路徑取得 hashtag
        if (
            result["data"]["tweetResult"]["result"]["__typename"]
            == "TweetWithVisibilityResults"
        ):
            return [
                r["text"]
                for r in result["data"]["tweetResult"]["result"]["tweet"]["legacy"][
                    "entities"
                ]["hashtags"]
            ]
        elif result["data"]["tweetResult"]["result"]["__typename"] == "Tweet":
            return [
                r["text"]
                for r in result["data"]["tweetResult"]["result"]["legacy"]["entities"][
                    "hashtags"
                ]
            ]
        else:
            raise ValueError(
                f"出現了意料之外的 __typename: {result["data"]["tweetResult"]["result"]["__typename"]}"
            )

    def __get_file_timestamp(self, result: dict) -> str:
        """取得檔案名的 timestamp YYMMDD"""
        if (
            result["data"]["tweetResult"]["result"]["__typename"]
            == "TweetWithVisibilityResults"
        ):
            full_text = result["data"]["tweetResult"]["result"]["tweet"]["legacy"][
                "full_text"
            ]
            created_at = result["data"]["tweetResult"]["result"]["tweet"]["legacy"][
                "created_at"
            ]
        elif result["data"]["tweetResult"]["result"]["__typename"] == "Tweet":
            full_text = result["data"]["tweetResult"]["result"]["legacy"]["full_text"]
            created_at = result["data"]["tweetResult"]["result"]["legacy"]["created_at"]

        else:
            raise ValueError(
                f"出現了意料之外的 __typename: {result["data"]["tweetResult"]["result"]["__typename"]}"
            )

        timestamp = self.__check_full_year(full_text)

        if timestamp:
            return timestamp

        timestamp = self.__check_partial_year(full_text)

        if timestamp:
            return timestamp

        return datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y").strftime(
            "%y%m%d"
        )

    def __check_full_year(self, full_text: str) -> str:
        """re 從 20xxxxxx 取得 xxxxxx"""
        match = re.search(r"\b20(\d{6})\b", full_text)
        return match.group(1) if match else ""

    def __check_partial_year(self, full_text: str) -> str:
        """re 擷取 20xxxxxx"""
        match = re.search(r"\b(\d{6})\b", full_text)
        return match.group(1) if match else ""

    def __get_local_path(
        self,
        path_prefix: str,
        timestamp: int,
    ) -> str:
        """取得本地儲存照片路徑與檔名"""
        # 如果有指定 prefix 就加上 -
        path_prefix = f"{path_prefix}-" if path_prefix else ""
        file_name = f"{path_prefix}{timestamp}"

        # 若資料夾中已經有該照片名，則將 index+1 並做為新的照片 index
        if file_name in self.__file_index:
            self.__file_index[file_name] += 1
            index = self.__file_index[file_name]
        else:
            index = self.__file_index[file_name] = 0

        return f"{self.__path_dir}/{file_name}-{index}.jpg"


if __name__ == "__main__":
    fire.Fire(XPostPhotosDownloader)
