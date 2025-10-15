#根据数据库中的日文名信息，到https://www.minnano-av.com/网站上去爬女优的数据包括身材，出道年份，等等。

#如何维护女优的名字是一个很麻烦的问题，现用名，曾用名，然后数据与网站上不一致如何更新？
import random
import time
import re
import requests
from bs4 import BeautifulSoup
import sqlite3
import logging
from config import DATABASE,ACTRESSIMAGES_PATH
from core.database.update import update_db_actress,update_actress_image,update_actress_minnano_id
from pathlib import Path
from core.crawler.download import download_image


#测试情况英文名的都有问题，日向なつ，杏奈，高瀬りな,白石もも重名问题
#有年份内的重名问题，这个问题可以通过哪年出道的数据来解决

def isActress(response):
    '''判断是否返回多个搜索结果'''
    soup = BeautifulSoup(response.text, 'html.parser')
    has_section = soup.find("section", class_="main-column list-table") is not None
    return has_section
    
def analyse(resopnse)->dict:
    '''返回标准女优信息页面html后提取信息函数，这个占90%

    这个请求会有几种情况，一个是直接跳转到女优信息页面这个是最好的情况，第二个，搜索不到，0结果，第三个，搜索到了多个结果
    '''
    soup = BeautifulSoup(resopnse.text, 'html.parser')


    meta_tag = soup.find('meta', {'property': 'og:url'})

    if meta_tag:
        url = meta_tag['content']
        # 使用正则表达式提取数字
        match = re.search(r'actress(\d+)\.html', url)
        
        if match:
            minnano_actress_id = match.group(1)
            logging.info("minnano_actress_id:%s",minnano_actress_id)


    #提取图片地址，方便下载
    # 找到 class="thumb" 的 div
    thumb_div = soup.find('div', class_='thumb')
    if thumb_div:
        # 在 thumb_div 中查找 img 标签
        img_tag = thumb_div.find('img')
        
        if img_tag and 'src' in img_tag.attrs:
            img_src = img_tag['src']
            logging.info("提取到的图片路径:%s", img_src)
        else:
            logging.warning("未找到图片标签或图片没有 src 属性")
    else:
        logging.debug("未找到 class='thumb' 的 div")

    full_img_src="https://www.minnano-av.com"+img_src

    section = soup.find('section', class_=['main-column', 'details'])
    if section:
        h1 = section.find('h1')
        jp_name = h1.contents[0].strip()  # <h1> 中最前面的部分是日文名
        # 提取 <span> 中的文字
        span_text = h1.find('span').text.strip()

        # 假名和英文名分开（用斜杠分隔）
        kana, romaji = [s.strip() for s in span_text.split('/')]

        logging.info("日文名:%s", jp_name)
        logging.info("假名:%s", kana)
        logging.info("英文名:%s", romaji)
    else:
        logging.warning("未找到姓名")

    #搜索所有的别名
    aliaschain=[]
    alias_soup = soup.find_all('span', string='別名')
    if alias_soup:
        for a in alias_soup:
            jp=None
            kana_=None
            romaji_=None
            mixalias=a.find_next('p').text
            match = re.match(r'^(.*?)[\(\（【]', mixalias)
            if match:
                jp = match.group(1).strip()
            
            matches = re.findall(r'（([^（）]*)）', mixalias)
            if matches:
                mix=matches[-1].strip()
                print(mix)
                kana_, romaji_ = [s.strip() for s in mix.split('/')]
            alias={"jp":jp,"kana":kana_,"en":romaji_}
            aliaschain.append(alias)
        logging.debug(aliaschain)

    #搜索出生年月
    birth_date=""
    label = soup.find('span', string='生年月日')
    if label:
        # 找到它后面的第一个 <p> 标签
        birthdate = label.find_next('p')
        match = re.search(r'(\d{4})年(\d{2})月(\d{2})日', birthdate.text)
        if match:
            year, month, day = match.groups()
            birth_date = f"{year}-{month}-{day}"
            logging.info("出生日期:%s", birth_date)
        else:
            logging.warning("未找到日期")
    else:
        logging.warning("未找到出生日期")
    #搜索所有的别称
    
    #搜索身材数据
    label = soup.find('span', string='サイズ')
    height=0
    bust=0
    cup=""
    waist=0
    hip=0

    # 找到它后面的第一个 <p> 标签
    body = label.find_next('p')

    pattern = r"T(\d+)\s*/\s*B(\d+)\((\w)カップ\)\s*/\s*W(\d+)\s*/\s*H(\d+)"
    match = re.search(pattern, body.text)

    if match:
        height = match.group(1)  # 身高
        bust = match.group(2)    # 胸围
        cup = match.group(3)     # 罩杯
        waist = match.group(4)   # 腰围
        hip = match.group(5)     # 臀围

        logging.info(f"身高: {height} ")
        logging.info(f"罩杯: {cup} ")
        logging.info(f"胸围: {bust} ")
        logging.info(f"腰围: {waist} ")
        logging.info(f"臀围: {hip} ")
    else:
        logging.warning("匹配失败")


    #搜索出道日期，有的女优没有出道作品，信息不全
    debut_date=""
    label = soup.find('span', string='デビュー作品')
    if label:
        # 找到它后面的第一个 <p> 标签
        debut_date_text = label.find_next('p')

        #match = re.search(r'（(.*?)）', debut_date_text.text)
        match = re.findall(r'（(.*?)）', debut_date_text.text)
        if match:
            #logging.info(match[-1])
            raw_date = match[-1].replace(" ", "")  # 去除空格
            # 替换日文日期格式为标准格式
            match = re.search(r'(\d{4})年(\d{2})月(\d{2})日', raw_date)
            if match:
                year, month, day = match.groups()
                debut_date = f"{year}-{month}-{day}"
                logging.info("出道日期:%s", debut_date)
            else:
                logging.warning("未找到日期")
        else:
            logging.warning("未找到日期")
    else:
        logging.warning("无出道作品未找到日期")

    new_data={
    "日文名":str(jp_name),
    "假名":str(kana),
    "英文名":str(romaji),
    "出生日期": str(birth_date),
    "身高": int(height),
    "罩杯": str(cup),
    "胸围": int(bust),
    "腰围": int(waist),
    "臀围": int(hip),
    "出道日期": str(debut_date),
    "头像地址": full_img_src,
    "minnano_actress_id":minnano_actress_id,
    "alias_chain":aliaschain
    }
    return new_data

def choosehtml(response,name):
    '''遇到多选项页面后需二次点击,大概占10%'''
    soup = BeautifulSoup(response.text, 'html.parser')
    details_tds=soup.find_all('td',class_='details')
    #0.1%遇到重名女优，这时就选作品量大的那个,简单判断需要作品数量>20
    if details_tds:
        for td in details_tds:
            if name==td.find('h2',class_='ttl').text:
                a_tag=td.find('h2',class_='ttl').find('a',href=True)
                href=a_tag['href']
                if int(td.find_next('td').text)>20:
                    return(href)
    else:
        logging.warning("未找到匹配")
        return False
#遇到多选项页面后还是找不出结果的占1%，比如rio
#这个暂时先不写了



def actress_need_update()->bool:
    '''判断女优数据库是否需要更新'''
    conn=sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    query='''
    SELECT "女优ID","日文名",need_update 
    FROM v_actress_all_info
    WHERE need_update=1
    '''
    cursor.execute(query)
    result=cursor.fetchall()

    cursor.close()
    conn.close()
    if not result or all(not item for item in result):
        return False
    else:
        return True
    

def SearchActressInfo()->str:
    '''搜索女优的信息并写入数据库'''   

    url1 = "https://www.minnano-av.com/search_result.php?search_scope=actress&search_word="
    url2="&search=+Go+"

    # 请求头要更改，还要sleep，现在问题不大先不用更改
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
            "Referer":"https://www.minnano-av.com/",
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language":"zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Connection":"keep-alive"
        }

    conn=sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    query='''
    SELECT "女优ID","日文名",need_update 
    FROM v_actress_all_info
    WHERE need_update=1
    '''
    cursor.execute(query)
    tuple_list=cursor.fetchall()
    cursor.close()
    conn.close()

    result = [{'actress_id': a, 'jp_name': b,'need_update':c} for a,b,c in tuple_list]#转成字典
    if not tuple_list or all(not item for item in tuple_list):
        logging.info("不需要更新")
        return "无需要更新数据的女优"
    else:
        #需要更新女优
        data_list_dict=[]
        total_rows = len(result)
        for i,row in enumerate(result):
            #logging.info(row.日文名)
            name=row['jp_name']
            id=row['actress_id']
            logging.info("%s搜索女优信息：%s",str(id),name)
            url=url1+name+url2 #合成的url
            response = requests.get(url, headers=headers)

            if response.status_code == 200:#判断请求成功
                logging.info("--------------------请求成功--------------------")
                if isActress(response):#判断是否是真的女优信息页面
                    logging.info("遇到多搜索结果准备跳转")
                    new_data={"日文名":name}#默认字典
                    #提取页面，点进去
                    urlA="https://www.minnano-av.com/"
                    urlB=choosehtml(response,name)
                    if urlB:
                        url=urlA+urlB
                        response = requests.get(url, headers=headers)
                        if response.status_code == 200:
                            logging.info("--------------------请求成功--------------------")
                            new_data=analyse(response)
                            #更新写入数据库
                            update_db_actress(id,new_data)
                            download_update_profile(id,new_data)
                            update_actress_minnano_id(id,new_data["minnano_actress_id"])
                        else:
                            logging.warning("--------------------请求失败--------------------")
                    else:
                        logging.warning("未找到女优数据")
                else:#遇到直接搜索的界面，还有种情况，遇到搜索不出来的界面
                    new_data=analyse(response)
                    #更新写入数据库
                    update_db_actress(id,new_data)
                    download_update_profile(id,new_data)
                    update_actress_minnano_id(id,new_data["minnano_actress_id"])
            else:
                logging.warning("--------------------请求失败--------------------")
            
            logging.info("---------------------------------------------------------------------------------")
            data_list_dict.append(new_data)
            if i != total_rows - 1:#不是最后一个睡10秒
                time.sleep(random.uniform(8, 12))
        
        logging.info(data_list_dict)
        namelist = ','.join(item['日文名'] for item in data_list_dict)
        return namelist+" 女优数据更新完成"

def download_update_profile(id,data:dict):
    '''下载女优的头像，并更新数据库
    输入的数据是这样的
        new_data={
    "日文名":str(jp_name),
    "假名":str(kana),
    "英文名":str(romaji),
    "出生日期": str(birth_date),
    "身高": int(height),
    "罩杯": str(cup),
    "胸围": int(bust),
    "腰围": int(waist),
    "臀围": int(hip),
    "出道日期": str(debut_date),
    "头像地址": full_img_src
    }
    '''
    
    image_urlA=str(str(id)+"-"+data['日文名']+".jpg")#存数据库里的相对地址
    image_path=Path(ACTRESSIMAGES_PATH/image_urlA)#实际要下载地址
    if download_image(data['头像地址'],image_path):
        update_actress_image(id,image_urlA)#写入数据库

def SearchSingleActressInfo(actress_id,name:str)->bool:
    '''这个是单个的情况'''
    from core.database.insert import InsertAliasName
    from core.database.query import exist_minnao_id
    logging.info("开启minnano单女优信息爬虫")
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
            "Referer":"https://www.minnano-av.com/",
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language":"zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Connection":"keep-alive"
        }
    url1 = "https://www.minnano-av.com/search_result.php?search_scope=actress&search_word="
    url2="&search=+Go+"
    success=False

    minnano_url=exist_minnao_id(actress_id)
    if minnano_url:#存在缓存
        logging.info("存在minnano-av缓存，直接访问页面")
        url="https://www.minnano-av.com/actress"+str(minnano_url)+".html"
    else:#不存在缓存，或者说就就是新添加的
        url=url1+name+url2 #合成的url
    response = requests.get(url, headers=headers)#实际请求在这里

    if response.status_code == 200:#判断请求成功
        logging.info("--------------------请求成功--------------------")
        if isActress(response):#判断是否是真的女优信息页面
            logging.info("遇到多搜索结果准备跳转")
            new_data={"日文名":name}#默认字典
            #提取页面，点进去
            urlA="https://www.minnano-av.com/"
            urlB=choosehtml(response,name)
            if urlB:
                url=urlA+urlB
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    logging.info("--------------------请求成功--------------------")
                    new_data=analyse(response)
                    #更新写入数据库
                    update_db_actress(actress_id,new_data)
                    InsertAliasName(actress_id,new_data['alias_chain'])
                    download_update_profile(actress_id,new_data)
                    update_actress_minnano_id(actress_id,new_data["minnano_actress_id"])
                    success=True
                else:
                    logging.warning("--------------------请求失败--------------------")
                    success=False
            else:
                logging.warning("未找到女优数据")
                success=False
        else:#遇到直接搜索的界面，还有种情况，遇到搜索不出来的界面
            new_data=analyse(response)
            #更新写入数据库
            update_db_actress(actress_id,new_data)
            InsertAliasName(actress_id,new_data['alias_chain'])
            download_update_profile(actress_id,new_data)
            update_actress_minnano_id(actress_id,new_data["minnano_actress_id"])
            success=True
    else:
        logging.warning("--------------------请求失败--------------------")
        success=False
    return success





