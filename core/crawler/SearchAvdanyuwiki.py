

'''爬https://avdanyuwiki.com这个网站，这个网站没有clouldflare很好爬'''

'''这个图片需要日本ip才能爬，其他的都行，而且日本ip可以访问'''

import re
import requests
from bs4 import BeautifulSoup
from utils.utils import covert_fanza
import logging

def search_work(serial_number:str)->BeautifulSoup|None:
    base="https://avdanyuwiki.com/?s="
    headers={"Host": "avdanyuwiki.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
    if serial_number.startswith(tuple(["ABF","FFT","ABW","BGN","GNI"])):
        url_list=[base+serial_number,base+covert_fanza(serial_number)]
    else:
        url_list=[base+covert_fanza(serial_number),base+serial_number]#这个要判断好像是ABF等蚊香社开头的就不需要转换直接上,现在问题是有的BGN是大写的，有的是小写的，这个非常的坑
    
    success=False#要跑两次，小写失败了跑大写，大写失败了跑小写，成功某次就返回，全失败了就返回空

    for url in url_list:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:#判断请求成功
            logging.info("-----avdanyuwiki请求成功-----")
            soup = BeautifulSoup(response.text, 'html.parser')
            article = soup.find('article', {
                'id': re.compile(r'^post-\d+'),
                'class': lambda x: x and 'entry-card' in x and 'e-card' in x
            })
            if article:
                logging.debug("查找到此作品")
                return article
            else:
                logging.debug("查不到此作品")
        elif response.status_code == 403:
            logging.info("-----avdanyuwiki服务器拒绝访问，请联系开发者更改爬虫策略或者等一会儿再爬-----")
        else:
            logging.info("-----avdanyuwiki请求失败-----")

    if not success:
        return None
    
def SearchInfoDanyukiwi(serial_number)->dict|None:
    """
    根据番号从网页中提取影片信息（导演、发布日期、男优列表、女优列表等）。
    
    Args:
        serial_number (str): 影片的唯一序列号，用于搜索对应网页内容。
        
    Returns:
        dict: 包含影片信息的字典，结构为：
    data={
        "director":director,
        "release_date":date,
        "actor_list":actor_list,
        "actress_list":actress_list,  
        "cover":img_src
    }
    """
    article=search_work(serial_number)
    if article is None:
        logging.warning("爬danyukiwi结果为空")
        return None
    # 1.提取图片
    img_src=""
    img_tag = article.find('img')  # 找到第一个 <img> 标签
    if img_tag:  # 确保找到标签
        img_src = img_tag.get('src')  #这个相当于是直接爬fanza的的地址了，这个也是可以缓存的
        logging.debug(img_src)
        #现在的问题是这个网址是没有问题的，但是由于你个是fanza的地址，直接下载是不行的

    # 2. 提取男优列表（匹配 "出演男優：" 后的内容）
    match = re.search(r'出演男優：(.+)', article.getText())
    actor_list=[]
    if match:
        actor_text = match.group(1)
        # 使用正则分割，支持中文逗号、英文逗号、空格、顿号等多种分隔符
        actor_list = re.split(r'[,、\s.]+', actor_text.strip())
        # 清理空白项和可能的分隔符残留
        actor_list = [actor.strip() for actor in actor_list if actor.strip()]
        logging.debug(set(actor_list))

    # 3. 提取导演（匹配 "監督：" 后的内容）
    director="----"#默认值
    match = re.search(r'監督：(.+)', article.getText())
    if match:
        director = match.group(1).strip()
        logging.debug("导演为：%s",director)

    # 4. 提取发布日期（优先匹配 "配信開始日："，其次 "商品発売日："）
    match = re.search(r'配信開始日：(.+)', article.getText())
    date=""
    if match:
        date = match.group(1).strip()
        logging.debug("发布日期为：%s",date)
    else:
        match = re.search(r'商品発売日：(.+)', article.getText())
        if match:
            date = match.group(1).strip()
            logging.debug("发布日期为：%s",date)   
        else:
            date=""
            logging.debug("找不到发布日期") 

    # 5. 提取女优列表（匹配 "出演者：" 后的内容）,这里要过滤所有()内的内容，全部消失
    match = re.search(r'出演者?：(.+)', article.getText())#这里也可能匹配 出演 出演者
    actress_list=[]
    if match:
        actress_text = match.group(1).strip().replace('—-', '')#删除—-
        clean_text = re.sub(r'（.*?）|\(.*?\)', '', actress_text)#删除括号内的内容，防止多个名字
        actress_list = re.split(r'[,、\s.]+', clean_text.strip())
        # 清理空白项和可能的分隔符残留
        actress_list = [actress.strip() for actress in actress_list if actress.strip()]
        logging.debug(set(actress_list)) 

    # 6. 格式化日期（如 "2023/01/01" → "2023-01-01"）
    if date != "":
        from datetime import datetime
        date=datetime.strptime(date, "%Y/%m/%d").strftime("%Y-%m-%d")

    # 7. 处理导演名称的特殊情况
    if director=="—-":
        director="----"

    # 8. 导演名称映射（可选，如标准化别名）
    directormap={
        "さもあり":"SamoAri"
    }
    if director in directormap:
        director = directormap[director]
    
    # 9. 返回结构化数据
    data={
        "director":director,
        "release_date":date,
        "actor_list":actor_list,
        "actress_list":actress_list,  
        "cover":img_src
    }
    logging.info(data)
    return data
