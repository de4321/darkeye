import requests
import sqlite3,logging
from config import DATABASE
from .SearchJavtxt import fetch_javtxt_movie_info
import time
import random
from core.database.update import update_titlestory

def download_image(url, save_path)->tuple[bool,str]:
    '''下载图片'''
    try:
        # 发送 HTTP GET 请求
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功
        
        # 以二进制写入模式打开文件
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"图片已保存到: {save_path}")
        return True,"成功下载"
    except Exception as e:
        print(f"下载失败: {e}")
        return False,str(e)

def update_title_story_db():
    '''更新整个数据库中的story'''

    query = f'''
        SELECT serial_number
        FROM work
        WHERE jp_title is NULL
        '''
    with sqlite3.connect(DATABASE) as conn:
        #返回所有需要更新的番号
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        serial_number_list=[row[0] for row in rows]
    
    for serial_number in serial_number_list:
        print(serial_number)
        data=fetch_javtxt_movie_info(serial_number)
        if data is not None:
            update_titlestory(serial_number,data["cn_title"],data["jp_title"],data["cn_story"],data["jp_story"])
        time.sleep(random.uniform(8, 15))

    