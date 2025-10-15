from PySide6.QtWidgets import QPushButton,QLabel,QGridLayout,QDialog,QLineEdit
from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon
from config import ICONS_PATH
import logging
from controller import MessageBoxService
from core.database.update import update_work_byhand_

class AddQuickWork(QDialog):
    #快速记录作品番号的窗口，能在局外响应
    def __init__(self):
        super().__init__()
        logging.info("----------快速记录作品番号窗口----------")
        self.setWindowTitle("快速记录作品番号(W)")
        self.setWindowIcon(QIcon(str(ICONS_PATH / "film.png")))
        self.setFixedSize(200,100)
        self.msg=MessageBoxService(self)
        self._threads = []
        
        self.label_serial_number = QLabel("番号：")
        self.input_serial_number=QLineEdit()
        self.input_serial_number.setPlaceholderText("例如：IPX-247")


        self.btn_commit=QPushButton("快速添加")
        self.btn_commit.clicked.connect(self.submit)
        #self.btn_commit.setMaximumWidth(100)

        layout=QGridLayout(self)
        layout.addWidget(self.label_serial_number,0,0)
        layout.addWidget(self.input_serial_number,0,1)
        layout.addWidget(self.btn_commit,1,1)

    def submit(self):
        #获得基本数据
        serialNumber = self.input_serial_number.text().strip()#去除前后的空格
        from utils.utils import is_valid_serialnumber
        if not is_valid_serialnumber(serialNumber):
            self.msg.show_warning("警告","请输入正常的番号")
            return
        #检查该番号是否在数据库里
        logging.debug("快速添加番号")
        from core.database.insert import InsertNewWork
        work_id=InsertNewWork(serialNumber)
        if work_id:
            self.msg.show_info("成功","添加新作品成功")
            self.accept()
            #尝试自动化的写入，能写的就写

            #查找中英文标题信息写入
            from core.crawler.SearchAvdanyuwiki import SearchInfoDanyukiwi
            from core.crawler.SearchJavtxt import fetch_javtxt_movie_info
            from core.crawler import CrawlerThreadResult
            logging.info(f"查询的番号：{self.input_serial_number.text()}")
            thread1=CrawlerThreadResult(lambda:fetch_javtxt_movie_info(self.input_serial_number.text()))#传一个函数名进去
            thread1.finished.connect(lambda result:self._on_javtxt_result(result,work_id))
            thread1.start()
            self._threads.append(thread1)

            thread2=CrawlerThreadResult(lambda:SearchInfoDanyukiwi(self.input_serial_number.text()))#传一个函数名进去
            thread2.finished.connect(lambda result:self._on_danyuwiki_result(result,work_id))
            thread2.start()
            self._threads.append(thread2)

        else:#work_id为None表示插入失败
            self.msg.show_warning("失败","添加新作品失败")
            self.reject()


    @Slot(dict, int)
    def _on_danyuwiki_result(self,data:dict,work_id:int):
        '''返回的数据更新到面板上
            data={
        "director":director,
        "release_date":date,
        "actor_list":actor_list,
        "actress_list":actress_list,  
        "cover":img_src
    }
        '''
        if data is None:
            logging.warning("爬danyuwiki产生错误信息")
            return
        #写入封面url,导演，拍摄时间
        update_work_byhand_(work_id,director=data.get("director"),release_date=data.get("release_date"),fcover_url=data.get("cover"))

        #下载图片并写入
        from core.crawler.download import download_image
        from core.database.update import update_fanza_cover_url
        from datetime import datetime
        from config import WORKCOVER_PATH
        from core.crawler import CrawlerThreadResult
        from pathlib import Path
        #这个要开全局访问才能下载图片

        image_url=self.input_serial_number.text().strip().lower().replace('-', '') + 'pl.jpg'#默认的替换规则

        dst_path = WORKCOVER_PATH / image_url#这个是个绝对地址
        imageurl=data.get("cover")

        self.thread2=CrawlerThreadResult(lambda:download_image(imageurl,dst_path))#下载图片放后台线程
        self.thread2.finished.connect(lambda result:self._on_download_image(result,work_id,image_url))#现在不需要回调了
        self.thread2.start()

        #直接写入女优
        actress_list=data.get("actress_list",[])
        from core.database.query import exist_actress
        from core.database.insert import InsertNewActress
        actress_ids=[]#存放女优id
        for actress in actress_list:
            #新的女优直接添加
            id=exist_actress(actress)
            if id is None:
                #添加新女优
                if InsertNewActress(actress,actress):
                    logging.info("添加女优成功:%s",actress)
                    id=exist_actress(actress)
                    actress_ids.append(id)
                    from controller.GlobalSignalBus import global_signals
                    global_signals.actress_data_changed.emit()
                    #这里要刷新女优选择器
            else:
                actress_ids.append(id)
        update_work_byhand_(work_id,actress_ids=actress_ids)

        #直接写入男优
        actor_list=data.get("actor_list",[])
        from core.database.query import exist_actor
        from core.database.insert import InsertNewActor
        actor_ids=[]#存放男优id
        for actor in actor_list:
            #新的男优直接添加
            id=exist_actor(actor)
            if id is None:
                #添加新男优
                if InsertNewActor(actor,actor):
                    logging.info("添加男优成功:%s",actor)
                    id=exist_actor(actor)
                    actor_ids.append(id)
                    #这里要刷新男优选择器，否则会出现无法加载的bug
                    from controller.GlobalSignalBus import global_signals
                    global_signals.actor_data_changed.emit()
            else:
                actor_ids.append(id)
        update_work_byhand_(work_id,actor_ids=actor_ids)

        if len(actor_list)==1 and len(actress_list)==1:
            #目前这个有bug
            #只有一个男优和一个女优，直接写入1V1的这个标签
            logging.info("自动写入1V1标签")
            from core.database.query import get_tagid_by_keyword
            from core.database.insert import add_tag2work
            tag_id_list=get_tagid_by_keyword("1V1",match_hole_word=True)
            logging.debug("1V1标签id:%s",tag_id_list)
            if add_tag2work(work_id,tag_ids=tag_id_list):
                logging.info("写入1V1标签成功")

    @Slot(tuple,int,str)
    def _on_download_image(self,result:tuple,work_id:int,image_url:str):
        '''下载图片的结果回调'''
        success, msg = result
        if success:
            logging.info("封面图片下载成功")
            #写入数据库
            update_work_byhand_(work_id,image_url=image_url)#这个要在图片下载后写入,否则会出现无法更改图片后无法提交的bug
        else:
            logging.warning("封面图片下载失败:%s",msg)
            #不写入数据库

    @Slot(dict, int)
    def _on_javtxt_result(self,data:dict,work_id:int):
        '''返回的数据更新到面板上'''
        if data is None:
            logging.warning("爬javtxt产生错误信息")
            return
        #写入中英文标题

        update_work_byhand_(work_id,cn_title=data.get("cn_title"),jp_title=data.get("jp_title"),cn_story=data.get("cn_story"),jp_story=data.get("jp_story"))

        #常试性分解tag然后写入
        from core.database.query import get_tagid_by_keyword
        from core.database.insert import add_tag2work
        import json
        from config import TAG_MAP_PATH
        with open(TAG_MAP_PATH, "r", encoding="utf-8") as f:
            tag_map:dict= json.load(f)

        for key,value in tag_map.items():
            if '|' in key:
                #有多个关键字
                match=True
                for k in key.split('|'):
                    if k not in data.get("jp_title"):
                        match=False
                if match:#全匹配后写入
                    for v in (value if isinstance(value,list) else [value]):
                        tag_id_list=get_tagid_by_keyword(v,match_hole_word=True)
                        if tag_id_list:
                            add_tag2work(work_id,tag_ids=tag_id_list)

            else:#单个关键字
                if key in data.get("jp_title"):
                    #找到了，写入
                    for v in (value if isinstance(value,list) else [value]):
                        tag_id_list=get_tagid_by_keyword(v,match_hole_word=True)
                        if tag_id_list:
                            add_tag2work(work_id,tag_ids=tag_id_list)

