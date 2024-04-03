# instagram-downloader
use to download photo or more from instagram

python version: 3.12

## instagram_post_photos_downloader
使用教學:
- 透過 `pip install -r requirements.txt` 安裝所需套件
- 將 config/ig_config.ini.example 複製成 config/ig_config.ini
- 打開網頁版 IG 透過 F12 的 Request 取得 header 中的 ds_user_id 與 shbid 並填上 ini
- 執行 `python instagram_post_photos_downloader.py download --post_url=https://www.instagram.com/p/{貼文後綴}/ --path_prefix="{檔案前綴}" --path_dir="{儲存路徑}"`
- 檔案會儲存在指定的資料夾下並以檔名: `{path_prefix}-YYMMDD-{index}.jpg`

參數說明:
- post_url: str, 貼文網址
- path_dir: str, 指定的下載路徑
- path_prefix(optional): str, 指定的檔名 prefix


## x_post_photos_downloader
使用教學:
- 透過 `pip install -r requirements.txt` 安裝所需套件
- 將 config/x_config.ini.example 複製成 config/x_config.ini
- 打開網頁版 X 的某個貼文的某張照片，透過 F12 的 Request: /TweetResultByRestId 取得 header 中的以下資訊:
    - query_id: 在 url 中: `https://twitter.com/i/api/graphql/{query_id}/TweetResultByRestId`
    - bearer_token: 在 header 的 Authorization: `Bearer {bearer_token}`
    - csrf_token: 在 header 的 X-Csrf-Token:
    - auth_token: 在 header 的 Cookie: 
    - ct0: 在 header 的 Cookie:
- 執行 `python x_post_photos_downloader.py download --post_url=""https://twitter.com/silky_ls/status/{貼文後綴}" --path_prefix="{檔案前綴}" --path_dir="{儲存路徑}"`
- 檔案會儲存在指定的資料夾下並以檔名: `{path_prefix}-YYMMDD-{index}.jpg`

參數說明:
- post_url: str, 貼文網址
- path_dir: str, 指定的下載路徑
- path_prefix(optional): str, 指定的檔名 prefix

## download_through_bookmark
使用教學:
- 透過 `pip install -r requirements.txt` 安裝所需套件
- 將 config/bookmark.ini.example 複製成 config/bookmark.ini
- 在 Chrome 網頁上打 chrome://version/ 查看設定檔路徑，此路徑下會有一個 Bookmark，將其路徑填到 path 中
- 執行 `python download_through_bookmark.py download --path_dir="{儲存路徑}"`
- 檔案會儲存在指定的資料夾下並以檔名: `{path_prefix}-YYMMDD-{index}.jpg`

參數說明:
- path_dir: str, 指定的下載路徑

## 額外 config 說明
`prefix_config.ini.example`
若有設定 prefix_config 則會自動判斷 hash tag 有沒有包含後面的字，自動帶入檔案前綴，用逗號分隔每個字串

python instagram_post_photos_downloader.py download --post_url=https://www.instagram.com/p/C5S1tLLPQT6/ --path_prefix="WonYoung" --path_dir="C:\Users\UHao\Downloads\IVE\OFFICIAL"

python x_post_photos_downloader.py download --post_url="https://twitter.com/silky_ls/status/1774811559317147911" --path_dir="C:\Users\UHao\Downloads\IVE\test"
python x_post_photos_downloader.py download --post_url="https://twitter.com/silky_ls/status/1775025332007125281" --path_dir="C:\Users\UHao\Downloads\IVE\test"

python download_through_bookmark.py download --path_dir="C:\Users\UHao\Downloads\IVE\test"