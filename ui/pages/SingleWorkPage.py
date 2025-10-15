#单部作品详细页面
from PySide6.QtWidgets import QHBoxLayout, QWidget, QLabel,QGraphicsOpacityEffect,QSizePolicy,QVBoxLayout,QLayoutItem
from PySide6.QtGui import QPixmap, QPainter, QLinearGradient, QColor,QFont
from PySide6.QtCore import Qt, QPointF,Signal,Slot
import logging

from ui.basic import VerticalTextLabel,VLabel,VFlowLayout,HeartLabel,IconPushButton
from config import WORKCOVER_PATH,ICONS_PATH
from ui.widgets.text.VerticalTagLabel2 import VerticalActressLabel,VerticalTagLabel,VerticalActorLabel
from ui.base import LazyWidget

#渐变层纯绘图层
class GradientOverlay(QWidget):
    #上面的渐变层
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def resizeEvent(self, event):
        # 始终覆盖父窗口
        if self.parent():
            self.resize(self.parent().size())
        super().resizeEvent(event)


    def paintEvent(self, event):
        painter = QPainter(self)
        window_width = self.width()
        window_height = self.height()

        gradient = QLinearGradient(QPointF(window_width-1.5*window_height, 0), QPointF(window_width, 0))
        gradient.setColorAt(0, QColor(20, 20, 20, 255))
        gradient.setColorAt(1, QColor(0, 0, 0, 0))

        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, window_width, window_height)

        grad_right=QLinearGradient(QPointF(window_width, 0), QPointF(window_width-0.1*window_height, 0))
        grad_right.setColorAt(0, QColor(20, 20, 20, 255))  # 右边黑色
        grad_right.setColorAt(1, QColor(0, 0, 0, 0))    # 中间透明
        painter.setBrush(grad_right)
        painter.drawRect(window_width-0.1*window_height,0,window_width,window_height)

class Cover(QLabel):
    def __init__(self,parent=None):
        super().__init__(parent)
        self._path=None

    def load_cover(self):
        '''加载'''
        if self._path is None:
            path=str(ICONS_PATH / "none.png")
            pixmap=QPixmap(path)
            if pixmap.isNull():
                logging.info(f"加载失败: {path}")
                pixmap = QPixmap(800, 600)
                pixmap.fill(Qt.black)
            self.original_pixmap = pixmap
            return
        
        from PySide6.QtGui import QImage
        imgmap = QImage(str(WORKCOVER_PATH / self._path))
        if imgmap.isNull():
            logging.info(f"加载失败: {path}")
            imgmap = QImage(800, 600)
            imgmap.fill(Qt.black)
        self.original_pixmap = QPixmap.fromImage(imgmap)#现在的问题是这个存的东西会过大，几个逻辑重复
        del imgmap
        #logging.debug("加载封面")

    def update_background_image(self, animate=False):
        '''缩放'''
        #更新背景的图片，包括动画

        window_width = self.width()
        window_height = self.height()
        image_height = self.original_pixmap.height()
        image_width = self.original_pixmap.width()
        scale_factor = window_height / image_height
        scaled_width = int(image_width * scale_factor)
        scaled_height = window_height
        scaled_pixmap = self.original_pixmap.scaled(
            scaled_width, scaled_height,
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        self.setPixmap(scaled_pixmap)#这里才是真正的设置了图片，并显示
        
        target_x = window_width - scaled_pixmap.width()
        target_y = 0
        #logging.debug(f"{target_x}, {target_y}")
        self.move(target_x, target_y)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._path:
            self.update_background_image()
    
    #对外使用
    def set_cover(self,path):
        self._path=path
        self.load_cover()
        self.update_background_image()


class WorkInfo(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        from controller.MessageService import MessageBoxService
        self.msg=MessageBoxService(self)

        self._work_id=None
        #self.setStyleSheet("border: 2px solid red;")
        self.title=VerticalTextLabel()
        self.title.setFixedHeight(550)
        self.title.setTextColor("#FFFFFF")
        self.title.setFont(QFont("Microsoft YaHei", 24))
        self.title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.story=VerticalTextLabel()
        self.story.setFixedHeight(550)
        self.story.setTextColor("#FFFFFF")
        self.story.setFont(QFont("Microsoft YaHei", 12))
        self.story.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.serial_number_label=VLabel("番号",text_color="#FFFFFF",background_color="#00000000",border_color="#FFFFFF")
        self.serial_number=VLabel(" ",text_color="#FFFFFF",background_color="#00000000",border_color="#FFFFFF")
        #self.serial_number.setTextColor("#FFFFFF")

        self.release_date_label=VLabel("发行日期",text_color="#FFFFFF",background_color="#00000000",border_color="#FFFFFF")
        self.release_date=VLabel(" ",text_color="#FFFFFF",background_color="#00000000",border_color="#FFFFFF")
        #self.release_date.setTextColor("#FFFFFF")

        #这些东西都要动态添加，有些是空的就会有大问题
        self.director_label=VLabel("导演",text_color="#FFFFFF",background_color="#00000000",border_color="#FFFFFF")
        self.director=VLabel(" ",text_color="#FFFFFF",background_color="#00000000",border_color="#FFFFFF")#这个有bug，不能是空的

        self.studio_label=VLabel("制作商",text_color="#FFFFFF",background_color="#00000000",border_color="#FFFFFF")
        self.studio=VLabel(" ",text_color="#FFFFFF",background_color="#00000000",border_color="#FFFFFF")#这个有bug，不能是空的
        self.label_tag=VLabel("作品标签",text_color="#FFFFFF",background_color="#00000000",border_color="#FFFFFF")

        self.actress=QWidget()
        self.label=QWidget()
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.actress.setFixedHeight(550)
        self.label.setFixedHeight(550)
        self.actress_layout=VFlowLayout(self.actress,spacing=5)#这个要改
        self.label_layout=VFlowLayout(self.label,spacing=5)#这个要改

        
        self.label_layout.addWidget(self.label_tag)

        self.heart=HeartLabel()

        self.trash=IconPushButton("trash-2.png",24,24)
        
        serialnumber_v_layout=QVBoxLayout()

        serialnumber_v_layout.addWidget(self.serial_number_label,0,Qt.AlignLeft)
        serialnumber_v_layout.addWidget(self.serial_number,0,Qt.AlignLeft)
        serialnumber_v_layout.addWidget(self.release_date_label,0,Qt.AlignLeft)
        serialnumber_v_layout.addWidget(self.release_date,0,Qt.AlignLeft)
        serialnumber_v_layout.addStretch()

        director_v_layout=QVBoxLayout()
        director_v_layout.addWidget(self.director_label)
        director_v_layout.addWidget(self.director)
        director_v_layout.addWidget(self.studio_label)
        director_v_layout.addWidget(self.studio)
        director_v_layout.addStretch()

        #最外侧拼装
        mainlayout=QHBoxLayout(self)
        mainlayout.setSpacing(5)
        mainlayout.setContentsMargins(0,0,0,0)

        mainlayout.addStretch()
        mainlayout.addWidget(self.trash,0,Qt.AlignRight|Qt.AlignTop)
        mainlayout.addWidget(self.heart,0,Qt.AlignRight|Qt.AlignTop)
        mainlayout.addWidget(self.label)
        mainlayout.addWidget(self.actress)
        mainlayout.addLayout(director_v_layout)
        mainlayout.addWidget(self.story, 0, Qt.AlignLeft|Qt.AlignTop)  # stretch改为0，让它根据内容决定宽度
        mainlayout.addLayout(serialnumber_v_layout)
        mainlayout.addWidget(self.title, 0, Qt.AlignLeft|Qt.AlignTop)

        self.signal_connect()
        
    def signal_connect(self):
        self.heart.clicked.connect(self.on_clicked_heart)
        self.trash.clicked.connect(self.on_clicked_delete)
        
    
    def update_actress(self, actress_list:list[dict],actor_list:list[dict]):
        '''更新女优出现的按钮，动态的
        
        Args:
            actress_list:字典列表

        '''
        # actress_list 是 [{"actress_id": ..., "actress_name": ...}, ...]

        # 1. 先清空所有的按钮
        while self.actress_layout.count():
            item:QLayoutItem= self.actress_layout.takeAt(0)
            widget:QWidget = item.widget()
            if widget:
                widget.deleteLater()
        
        if actress_list is None:
            #self.actress.deleteLater()
            return

        label_actress=VLabel("女优",text_color="#FFFFFF",background_color="#00000000",border_color="#FFFFFF")
        self.actress_layout.addWidget(label_actress)
        # 2. 动态创建按钮并添加女优列表
        for actress in actress_list:
            actress_id = actress["actress_id"]
            name = actress["actress_name"]
            label = VerticalActressLabel(actress_id,name,background_color="#FFFFFF")

            self.actress_layout.addWidget(label)

        #处理男优空值的问题
        if actor_list is None:
            return
        #添加男优的标签
        label_actor=VLabel("男优",text_color="#FFFFFF",background_color="#00000000",border_color="#FFFFFF")
        self.actress_layout.addWidget(label_actor)

        for actor in actor_list:
            actor_id = actor["actor_id"]
            name = actor["actor_name"]
            label = VerticalActorLabel(actor_id,name,background_color="#FFFFFF")
            #label.clicked.connect(self.on_actor_clicked)
            self.actress_layout.addWidget(label)


    def update_tag(self, tag_list:list[dict]):
        '''更新tag'''
        # 1. 先清空之前按钮
        while self.label_layout.count()>1:
            item:QLayoutItem = self.label_layout.takeAt(1)
            widget:QWidget = item.widget()
            if widget:
                widget.deleteLater()

        # 2. 动态创建按钮并添加
        #logging.debug(tag_list)
        for tag in tag_list:
            label = VerticalTagLabel(tag["tag_id"], tag["tag_name"],tag["color"],tag["detail"])
            self.label_layout.addWidget(label)

    def set_info(self,info:dict):
        '''更新信息'''
        self.title.setText(info["cn_title"])
        self.story.setText(info["cn_story"])
        self.release_date.setTextDynamic(info["release_date"])
        self.serial_number.setTextDynamic(info["serial_number"])
        self.director.setTextDynamic(info["director"])
        if info["studio_name"] is not None:
            self.studio.setTextDynamic(info["studio_name"])
        else:
            self.studio.setTextDynamic("----")

    @Slot()
    def on_clicked_delete(self):
        from core.database.update import mark_delete
        if self._work_id is None:
            return
        if self.msg.ask_yes_no("确认删除", "确定要删除该作品吗？"):
            if mark_delete(self._work_id):
                self.msg.show_info("成功","已标记删除")

    @Slot()
    def on_clicked_heart(self):
        from core.database.insert import insert_liked_work
        from core.database.delete import delete_favorite_work
        if self.heart.get_statue():
            '''添加到喜欢'''
            insert_liked_work(self._work_id)
        else:
            '''删除'''
            delete_favorite_work(self._work_id)
        from controller.GlobalSignalBus import global_signals
        global_signals.like_work_changed.emit()

    def update(self,work_id):
        from core.database.query import get_workinfo_by_workid,findActressFromWorkID,get_worktaginfo_by_workid,query_work,findActorFromWorkID
        self._work_id=work_id
        self.set_info(get_workinfo_by_workid(work_id))
        self.update_actress(findActressFromWorkID(work_id),findActorFromWorkID(work_id))
        self.update_tag(get_worktaginfo_by_workid(work_id))

        #更新爱心状态
        if query_work(work_id):
            self.heart.set_statue(True)
        else:
            self.heart.set_statue(False)


class SingleWork(QWidget):

    def __init__(self):
        super().__init__()

        self._h=self.height()
        #背景图片层
        self.bg_label = Cover(self)

        # 在 self.bg_label 上添加透明度效果
        self.opacity_effect = QGraphicsOpacityEffect(self.bg_label)
        self.bg_label.setGraphicsEffect(self.opacity_effect)

        #这个是上层阴影效果
        self.gradient_overlay = GradientOverlay(self)
        self.gradient_overlay.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self.work_info=WorkInfo(self)




        self.bg_label.lower()
        self.gradient_overlay.raise_()
        self.work_info.raise_()

        self.hlayout=QHBoxLayout()
        mainlayout=QVBoxLayout(self)
        mainlayout.addStretch()
        mainlayout.addLayout(self.hlayout)
        mainlayout.addStretch()
        self.hlayout.addStretch()
        self.hlayout.addWidget(self.work_info)
        self.hlayout.setContentsMargins(0,0,self._h*0.8,0)#这里的定位使用layout里的margin+stretch定位
        mainlayout.setContentsMargins(0,0,0,0)

        

    def resizeEvent(self, event):
        self._h=self.height()
        self.hlayout.setContentsMargins(0,0,self._h*0.8,0)
        rect = self.rect()
        self.bg_label.setGeometry(rect)
        self.gradient_overlay.setGeometry(rect)



class SingleWorkPage(LazyWidget):
    '''这个才是最主要的，总装在这里'''
    def __init__(self):
        super().__init__()
        
    def _lazy_load(self):
        logging.info("----------加载单独作品界面----------")
        mainlayout = QVBoxLayout(self)
        mainlayout.setContentsMargins(0, 0, 0, 0)
        mainlayout.addSpacing(70)

        self.cover=SingleWork()

        mainlayout.addWidget(self.cover)



    def update(self,work_id):
        '''传入一个work_id并更新整个页面'''
        from core.database.query import get_coveriamgeurl
        self.cover.work_info.update(work_id)
        self.cover.bg_label.set_cover(get_coveriamgeurl(work_id))
