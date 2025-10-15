from PySide6.QtWidgets import QPushButton, QHBoxLayout,QVBoxLayout
import logging
from core.crawler.download import update_title_story_db
from core.crawler.SearchJavtxt import top_actresses
from ui.base import LazyWidget

class UpdateManyTabPage(LazyWidget):
    #软件的设置
    def __init__(self):
        super().__init__()
    def _lazy_load(self):
        logging.info("----------加载批量更新窗口----------")

        #self.btn_search_actor=QPushButton("批量更新男优")
        self.btn_search_story=QPushButton("批量更新所有的故事")
        self.btn_search_story.setEnabled(False)
        self.btn_search_actress=QPushButton("更新热门女优")
        self.btn_search_actress.setToolTip("更新javatext热门女优前50")

        #self.btn_search_actor.clicked.connect(update_actor_db)
        self.btn_search_story.clicked.connect(update_title_story_db)
        self.btn_search_actress.clicked.connect(top_actresses)

        layout1=QHBoxLayout()
        layout1.addWidget(self.btn_search_story)
        #layout1.addWidget(self.btn_search_actor)
        layout1.addWidget(self.btn_search_actress)

        mainlayout=QVBoxLayout(self)
        mainlayout.addLayout(layout1)



