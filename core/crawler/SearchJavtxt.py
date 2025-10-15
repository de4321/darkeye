import re
import requests
from bs4 import BeautifulSoup
from utils.utils import covert_fanza,serial_number_equal
import logging
from core.database.update import update_work_javtxt
from core.database.query import get_workid_by_serialnumber,get_javtxt_id_by_serialnumber


'''需要非日本ip才能爬'''
def search_work(serial_number)->str|None:
    '''返回真实目标页面'''
    base="https://javtxt.com/search?type=id&q="


    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
    url=base+serial_number #这里要调成标准模式
    response = requests.get(url, headers=headers)
    if response.status_code == 200:#判断请求成功
        logging.info("-----请求成功-----")
        soup = BeautifulSoup(response.text, 'html.parser')
        work_link = soup.find('a', class_='work')
        if work_link:  # 确保找到元素
            href_value = work_link.get('href')  # 提取 href 属性
            logging.info(href_value)  
        else:
            logging.info("未找到符合条件的元素")
        #验证元素
        work_id_link = soup.find('h4', class_='work-id')
        if work_id_link:
            target_work_id=work_id_link.text
            if serial_number_equal(target_work_id,serial_number):#验证是一个番号
                return href_value
        return None
    else:
        logging.info("-----请求失败-----")
        logging.info(response.status_code)
        return None

def scrape_javtxt_movie_details(url: str) -> dict | None:
    """
    从 JAVTXT 网站抓取电影详细信息（中日文标题和剧情简介）。
    
    Args:
        url (str): 要抓取的 JAVTXT 电影详情页 URL
        
    Returns:
        dict | None: 包含电影信息的字典，结构为:
            {
                "cn_title": str,    # 中文标题
                "jp_title": str,    # 日文标题
                "cn_story": str,    # 中文剧情简介
                "jp_story": str      # 日文剧情简介
            }
            如果请求失败则返回 None
    """

    #设置请求头
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:#判断请求成功
        logging.info("-----javtxt请求成功-----")
        #解析页面
        soup = BeautifulSoup(response.text, 'html.parser')
        jp_title=""
        cn_title=""
        cn_story=""
        jp_story=""
        jp_title_link = soup.find('h1', class_='title is-4 text-jp')
        cn_title_link = soup.find('h2', class_='title is-4 text-zh')

        if jp_title_link:
            jp_title=jp_title_link.text
            logging.debug(jp_title)
        if cn_title_link:
            cn_title=cn_title_link.text
            logging.debug(cn_title)
        
        jp_story_link=soup.find('p',class_='text-jp')
        if jp_story_link:
            jp_story=jp_story_link.text
            logging.debug(jp_story)
        cn_story_link=soup.find('div',class_='text-zh')
        if cn_story_link:
            cn_p=cn_story_link.find('p')
            if cn_p:
                cn_story=cn_p.text
                logging.debug(cn_story)
        data={
            "cn_title":cn_title,
            "jp_title":jp_title,
            "cn_story":cn_story,
            "jp_story":jp_story
        }
        return data
    else:
        logging.warning("-----javtxt请求失败,状态码%s-----",response.status_code)
        return None

def fetch_javtxt_movie_info(serial_number: str) -> dict | None:
    """
    根据番号获取JAVTXT网站上的电影详细信息（带缓存机制）。
        #标记非正规作品，非正规作品是没有封面，导演，故事等等的
    流程：
    1. 先检查本地是否有该番号对应的JAVTXT ID缓存
    2. 若无缓存则进行搜索获取ID
    3. 使用ID构建最终URL并抓取详细信息
    
    Args:
        serial_number (str): 影片番号(如ABP-123)
        
    Returns:
        dict | None: 包含电影信息的字典，结构同scrape_javtxt_movie_details()
                    如果获取失败则返回None

    """
    javtxt_id=get_javtxt_id_by_serialnumber(serial_number)
    if javtxt_id is None:#先查有无缓存
        truepage=search_work(serial_number)
        if truepage is None:
            logging.info("Javtxt_id无缓而且搜不到,结束")
            return
        else:
            #无缓搜索到
            javtxt_id = truepage.split("/")[-1]#这个存到数据库里面缓存，后面的时候就不需要一级查找
            work_id=get_workid_by_serialnumber(serial_number)
            logging.info(f"获取到新JAVTXT ID: {javtxt_id}并写入本地缓存，work_id:{work_id}")
            if work_id is not None:
                update_work_javtxt(work_id,javtxt_id)
    else:
        logging.info(f"番号 {serial_number} 使用缓存JAVTXT ID: {javtxt_id}")
        truepage="/v/"+str(javtxt_id)
    
    base="https://javtxt.com"
    url=base+truepage

    # 7. 调用详情页抓取函数
    return scrape_javtxt_movie_details(url)


def top_actresses():
    '''获得javtxt的最受欢迎女优'''
    url="https://javtxt.com/top-actresses"
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
    response = requests.get(url, headers=headers)
    result:list[str]=[]
    if response.status_code == 200:#判断请求成功
        logging.info("-----请求成功-----")
        soup = BeautifulSoup(response.text, 'html.parser')
        actress_links = soup.find_all('p', class_='actress-name')
        for actress in actress_links:
            result.append(actress.text)
    else:
        logging.info("-----请求失败-----")
        logging.info(response.status_code)
        return None
    logging.info(f"获取到热门女优{result}")
    from core.database.query import exist_actress
    for actress in result[:50]:#只取前50个
        actress= actress.replace("卜", "ト")
        if not exist_actress(actress):
            from core.database.insert import InsertNewActress
            InsertNewActress(actress,actress)
            logging.info(f"添加热门女优{actress}")
            from controller.GlobalSignalBus import global_signals
            global_signals.actress_data_changed.emit()
        else:
            logging.info(f"热门女优{actress}已存在")
    return result

