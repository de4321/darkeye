from PySide6.QtWidgets import QPushButton, QHBoxLayout, QLabel,QVBoxLayout,QTextEdit,QDialog
from PySide6.QtGui import QIcon
from PySide6.QtCore import Slot
import logging
from ui.base import LazyWidget
from config import BASE_DIR,DATABASE,INI_FILE,ICONS_PATH
from controller import MessageBoxService

class SettingDialog(QDialog):
    #软件的设置
    def __init__(self,parent=None):
        super().__init__(parent)
        logging.info("----------软件设置窗口----------")
        self.setWindowTitle("软件设置")
        self.setWindowIcon(QIcon(str(ICONS_PATH / "settings.png")))
        self.resize(400,400)
        self.msg=MessageBoxService(self)
        path_label=QLabel(f"软件的工作文件夹{str(BASE_DIR)}")
        path_label2=QLabel(f"软件的公共数据库文件位置{str(DATABASE)}")
        path_label3=QLabel(f"ini文件的位置{INI_FILE}")

        self.btn_vacuum=QPushButton("数据库清理碎片")#包括清理两个数据库
        self.btn_cover_check=QPushButton("图片数据一致性检查")

        self.btn_commit=QPushButton("保存设置")
        self.btn_commit.setVisible(False)
        


        layout1=QHBoxLayout()

        layout1.addWidget(self.btn_vacuum)
        layout1.addWidget(self.btn_cover_check)

        #总装
        layout=QVBoxLayout(self)
        layout.addLayout(layout1)
        layout.addWidget(self.btn_commit)
        layout.addWidget(path_label)
        layout.addWidget(path_label2)
        layout.addWidget(path_label3)

        self.signal_connect()


    def signal_connect(self):
        from core.database.db_utils import sqlite_vaccum
        self.btn_cover_check.clicked.connect(self.check_image_consistency)
        self.btn_vacuum.clicked.connect(sqlite_vaccum)
        self.btn_commit.clicked.connect(self.submit)


    @Slot()
    def check_image_consistency(self):
        '''检查数据库中的图片一致性的问题'''
        from core.database.db_utils import image_consistency
        image_consistency(True,"cover")
        image_consistency(True,"actress")
        image_consistency(True,"actor")
        self.msg.show_info("提示","处理好图片一致性问题，删除多余图片")
        
    @Slot()
    def submit(self):
        #获得基本数据
        logging.debug("保存设置")
