
import time
from bs4 import BeautifulSoup

import cloudscraper
#这个非常的不好弄，clouldflare基本上过不去，不弄了



url="https://www.javlibrary.com/cn/vl_searchbyid.php?keyword=IPX-182"

scraper = cloudscraper.create_scraper(browser={
    "browser": "chrome",
    "platform": "windows",
    "mobile": False
})


for i in range(5):
    resp = scraper.get(url)
    html = resp.text
    if "Just a moment" not in resp.text:
        break
    time.sleep(2)

soup = BeautifulSoup(html, "html.parser")
# 1️⃣ 找到 img 元素
img_tag = soup.find("img", id="video_jacket_img")

if img_tag:
    # 2️⃣ 取出 src 属性
    cover_url = img_tag.get("src")
    print("封面 URL:", cover_url)

    # 如果你想备用图（onerror里的第二个URL）
    onerror = img_tag.get("onerror", "")
    print("onerror内容:", onerror)
else:
    print("未找到封面图片")