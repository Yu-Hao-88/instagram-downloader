# instagram-downloader
use to download photo or more from instagram

python version: 3.12

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