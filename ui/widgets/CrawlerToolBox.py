from PySide6.QtWidgets import QPushButton,QGridLayout,QToolBox,QWidget,QCheckBox
from utils.utils import covert_fanza
from ui.basic import IconPushButton

class CrawlerToolBox(QToolBox):
    '''给addworktabpage使用的部分控件'''
    def __init__(self):
        super().__init__()
        #现在这里只有UI
        self.setFixedHeight(200)

        # 添加页面1
        page1 = QWidget()
        self.addItem(page1, "自动爬虫抓取信息")
        page1_layout=QGridLayout(page1)
        page1_layout.setContentsMargins(0,0,0,0)
        self.cb_release_date=QCheckBox("发布日期")
        self.cb_director=QCheckBox("导演")
        self.cb_cover=QCheckBox("封面")
        self.cb_cn_title=QCheckBox("中文标题")
        self.cb_jp_title=QCheckBox("日文标题")
        self.cb_cn_story=QCheckBox("中文故事")
        self.cb_jp_story=QCheckBox("日文故事")
        self.cb_actress=QCheckBox("女优")
        self.cb_actor=QCheckBox("男优")
        self.btn_get_crawler=IconPushButton("arrow-down-to-line.png",24,32)

        self.cb_release_date.setChecked(True)
        self.cb_director.setChecked(True)
        self.cb_cn_title.setChecked(True)
        self.cb_jp_title.setChecked(True)
        self.cb_cn_story.setChecked(True)
        self.cb_jp_story.setChecked(True)
        self.cb_actress.setChecked(True)
        self.cb_actor.setChecked(True)
        self.cb_cover.setChecked(True)

        self.btn_get_crawler.setToolTip("主要更新男优，发布日期，导演")
        page1_layout.addWidget(self.cb_release_date, 0, 0)
        page1_layout.addWidget(self.cb_director,      0, 1)
        page1_layout.addWidget(self.cb_cover,         0, 2)

        page1_layout.addWidget(self.cb_cn_title,      1, 0)
        page1_layout.addWidget(self.cb_jp_title,      1, 1)
        page1_layout.addWidget(self.cb_cn_story,      2, 0)

        page1_layout.addWidget(self.cb_jp_story,      2, 1)
        page1_layout.addWidget(self.cb_actress,       1, 2)
        page1_layout.addWidget(self.cb_actor,         2, 2)

        page1_layout.addWidget(self.btn_get_crawler,3,1)

        

        # 添加页面2
        page2 = QWidget()
        self.addItem(page2, "手动导航")
        linklayout=QGridLayout(page2)
        
        self.btn_get_javlibrary=QPushButton("javlibrary")
        self.btn_get_javlibrary.setToolTip("获得封面")

        self.btn_get_javdb=QPushButton("javdb")
        self.btn_get_javdb.setToolTip("获得一般信息")

        self.btn_get_javtxt=QPushButton("javtxt")
        self.btn_get_javtxt.setToolTip("获得故事与标题，但是没有封面")

        self.btn_get_minnaoav=QPushButton("minnao-av")
        self.btn_get_minnaoav.setToolTip("女优信息")

        self.btn_get_avdanyuwiki=QPushButton("avdanyuwiki")
        self.btn_get_avdanyuwiki.setToolTip("作品男优信息")

        self.btn_get_missav=QPushButton("missav")
        self.btn_get_missav.setToolTip("在线观看网站")

        self.btn_get_avmoo=QPushButton("avmoo")
        self.btn_get_avmoo.setToolTip("获得封面")

        self.btn_get_fanza=QPushButton("fanza")
        self.btn_get_fanza.setToolTip("fanza售卖网站，非日本本土，需日本vpn且特殊插件才能访问")

        self.btn_get_netflav=QPushButton("netflav")
        self.btn_get_netflav.setToolTip("在线观看网站")

        self.btn_get_123av=QPushButton("123av")
        self.btn_get_123av.setToolTip("在线观看网站")

        self.btn_get_jable=QPushButton("jable")
        self.btn_get_jable.setToolTip("在线观看网站")

        self.btn_get_supjav=QPushButton("supjav")
        self.btn_get_supjav.setToolTip("专门看FC2")

        self.btn_get_mgs=QPushButton("MGS")
        self.btn_get_mgs.setToolTip("PRESTIGE官方的售卖网站，非日本本土，需日本vpn且特殊插件才能访问")

        self.btn_get_jinjier=QPushButton("金鸡儿奖")
        self.btn_get_jinjier.setToolTip("金鸡儿奖网站，挺有意思的")

        self.btn_get_gana=QPushButton("平假名")
        self.btn_get_kana=QPushButton("片假名")

        #上部的辅助网站连接
        linklayout.addWidget(self.btn_get_javlibrary,0,0)
        linklayout.addWidget(self.btn_get_javdb,0,1)
        linklayout.addWidget(self.btn_get_javtxt,0,2)
        linklayout.addWidget(self.btn_get_minnaoav,1,0)
        linklayout.addWidget(self.btn_get_avdanyuwiki,1,1)
        linklayout.addWidget(self.btn_get_missav,2,0)
        linklayout.addWidget(self.btn_get_avmoo,1,2)
        linklayout.addWidget(self.btn_get_fanza,2,2)
        linklayout.addWidget(self.btn_get_netflav,2,1)
        linklayout.addWidget(self.btn_get_123av,3,0)
        linklayout.addWidget(self.btn_get_jable,3,1)
        linklayout.addWidget(self.btn_get_mgs,3,2)
        linklayout.addWidget(self.btn_get_supjav,4,0)
        linklayout.addWidget(self.btn_get_jinjier,4,2)
        linklayout.addWidget(self.btn_get_gana,5,1)
        linklayout.addWidget(self.btn_get_kana,5,2)


