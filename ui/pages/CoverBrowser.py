
import os
import logging
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QWidget, QLabel,QGraphicsOpacityEffect,QSizePolicy,QVBoxLayout,QFileDialog
from PySide6.QtGui import QPixmap, QPainter, QLinearGradient, QColor,QIcon
from PySide6.QtCore import Qt, QPointF, QPropertyAnimation, QEasingCurve,QParallelAnimationGroup,QSize,Signal,QTimer
from config import WORKCOVER_PATH,ICONS_PATH,VIDEO_PATH

from ..basic.FlowLayout import FlowLayout


#渐变层纯绘图层
class GradientOverlay(QWidget):
    #上面的渐变层
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._scaled_width = 800  # 默认值，防止空值

    def set_scaled_width(self, width):
        self._scaled_width = width
        self.update()

    def resizeEvent(self, event):
        # 始终覆盖父窗口
        if self.parent():
            self.resize(self.parent().size())
        super().resizeEvent(event)


    def paintEvent(self, event):
        painter = QPainter(self)
        window_width = self.width()
        window_height = self.height()

        gradient = QLinearGradient(QPointF(window_width-0.8*self._scaled_width, 0), QPointF(window_width, 0))
        gradient.setColorAt(0, QColor(20, 20, 20, 255))
        gradient.setColorAt(1, QColor(0, 0, 0, 0))

        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, window_width, window_height)

        grad_right=QLinearGradient(QPointF(window_width, 0), QPointF(window_width-0.1*self._scaled_width, 0))
        grad_right.setColorAt(0, QColor(20, 20, 20, 255))  # 右边黑色
        grad_right.setColorAt(1, QColor(0, 0, 0, 0))    # 中间透明
        painter.setBrush(grad_right)
        painter.drawRect(window_width-0.1*self._scaled_width,0,window_width,window_height)

#信息层
class InfoOverlay(QWidget):
    #左侧封面推荐av的信息
    def __init__(self, parent=None):
        super().__init__(parent)
        #self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._scaled_width = 800  # 默认值，防止空值
        self.resize(self.parent().size())

        self.w = self.width()
        self.h = self.height()
        
        
        # 创建一个“浮层”控件
        self.work_name = QLabel("夫妻交换，仅限周末，妻子被其他人插入")
        self.work_name.setStyleSheet("""
            QLabel {
                font-size: 32px;           /* 字号 */
                font-family: 'Microsoft YaHei';      /* 字体 */
                font-weight: bold;         /* 粗体，可选 normal、bold、100-900 */
                color: white;
                background-color: rgba(0, 0, 0, 0);
            }
        """)
        self.work_name.setWordWrap(True) 
        
        self.FANHAO=QLabel("番号:")
        self.FANHAO.setStyleSheet("""
            QLabel {
                font-size: 18px;           /* 字号 */
                font-family: 'Microsoft YaHei';      /* 字体 */
                font-weight: bold;         /* 粗体，可选 normal、bold、100-900 */
                color: grey;
                background-color: rgba(0, 0, 0, 0);
            }
        """)

        self.serial_number=QLabel("番号:IPX-247")
        self.serial_number.setStyleSheet("""
            QLabel {
                font-size: 18px;           /* 字号 */
                font-family: 'Microsoft YaHei';      /* 字体 */
                font-weight: normal;         /* 粗体，可选 normal、bold、100-900 */
                color: grey;
                background-color: rgba(0, 0, 0, 0);
            }
        """)


        self.story=QLabel("夫妻交换，仅限周末，妻子被其他人插入的夜晚，因为矛盾等等的因素")
        self.story.setStyleSheet("""
            QLabel {
                font-size: 16px;           /* 字号 */
                font-family: 'Microsoft YaHei';      /* 字体 */
                font-weight: bold;         /* 粗体，可选 normal、bold、100-900 */
                color: white;
                background-color: rgba(0, 0, 0, 0);
            }
        """)
        self.story.setWordWrap(True)
        self.story.setMaximumHeight(200)

        self.TIME=QLabel("发行日期:")
        self.TIME.setStyleSheet("""
            QLabel {
                font-size: 18px;           /* 字号 */
                font-family: 'Arial';      /* 字体 */
                font-weight: bold;         /* 粗体，可选 normal、bold、100-900 */
                color: grey;
                background-color: rgba(0, 0, 0, 0);
            }
        """)

        self.time=QLabel("发行日期:2020-05-20")
        self.time.setStyleSheet("""
            QLabel {
                font-size: 18px;           /* 字号 */
                font-family: 'Arial';      /* 字体 */
                font-weight: bold;         /* 粗体，可选 normal、bold、100-900 */
                color: grey;
                background-color: rgba(0, 0, 0, 0);
            }
        """)
        self.actress=QLabel("女优:")
        self.actress.setStyleSheet("""
            QLabel {
                font-size: 18px;           /* 字号 */
                font-family: 'Arial';      /* 字体 */
                font-weight: bold;         /* 粗体，可选 normal、bold、100-900 */
                color: grey;
                background-color: rgba(0, 0, 0, 0);
            }
        """)

        self.btn_start=QPushButton("开始观看")
        self.btn_start.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: red;
                border: none;
                padding: 0px 0px;
                text-align: left;
                border-radius: 10px;  
                text-align: center; /* 水平居中 */     
            }
        """)
        self.btn_start.setFixedSize(60,30)
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_start.clicked.connect(self.play_video_with_default_player)




        self.h_layout=QHBoxLayout()
        self.h_layout.setContentsMargins(0,0,self.h*0.3,0)#这些都要在resize中重写
        self.h_layout.setSpacing(0)


        # 中间承载控件的 widget
        self.center_widget = QWidget()
        self.center_widget.setFixedWidth(self.h*0.9)#这些都要在resize中重写

        self.innerlayout = QVBoxLayout(self.center_widget)#整体垂直布局
        self.innerlayout.setContentsMargins(0, 0, 0, 0)
        self.innerlayout.setSpacing(10)  # 控件间距可调
        
        self.serial_number_layout=QHBoxLayout()#番号那行的layout
        self.serial_number_layout.setContentsMargins(0, 0, 0, 0)
        self.time_layout=QHBoxLayout()#时间那行的layout
        self.time_layout.setContentsMargins(0, 0, 0, 0)
        self.actress_layout=QHBoxLayout()#女优那行的layout
        self.actress_layout.setContentsMargins(0, 0, 0, 0)
        self.actress_in_layout=QHBoxLayout()#女优排列的layout
        self.actress_in_layout.setContentsMargins(0, 0, 0, 0)
        self.tag_widget=QWidget()#tag的widget
        self.tag_layout=FlowLayout(self.tag_widget)#tag的流动式layout

        #大布局组装
        self.innerlayout.addWidget(self.work_name)
        self.innerlayout.addLayout(self.serial_number_layout)
        self.innerlayout.addWidget(self.story)
        self.innerlayout.addLayout(self.time_layout)
        self.innerlayout.addLayout(self.actress_layout)
        self.innerlayout.addWidget(self.tag_widget)
        #self.innerlayout.addWidget(self.btn_start)

        self.serial_number_layout.addWidget(self.FANHAO)
        self.serial_number_layout.addWidget(self.serial_number)
        self.serial_number_layout.addStretch()

        self.time_layout.addWidget(self.TIME)
        self.time_layout.addWidget(self.time)
        self.time_layout.addStretch()

        self.actress_layout.addWidget(self.actress)
        self.actress_layout.addLayout(self.actress_in_layout)
        self.actress_layout.addStretch()


        # 添加 stretch 实现垂直居中
        mainlayout=QVBoxLayout(self)
        mainlayout.setContentsMargins(0, 0, 0, 0)
        mainlayout.setSpacing(0)
        mainlayout.addStretch(3)
        mainlayout.addLayout(self.h_layout)
        mainlayout.addStretch(2)

        # 添加 stretch 实现右侧固定距离
        self.h_layout.addStretch()
        self.h_layout.addWidget(self.center_widget)

    def update_actress_buttons(self, actress_list:list[dict]):
        '''更新女优出现的按钮，动态的
        
        Args:
            actress_list:字典列表

        '''
        # actress_list 是 [{"actress_id": ..., "actress_name": ...}, ...]

        # 1. 先清空之前按钮
        while self.actress_in_layout.count():
            item = self.actress_in_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        if actress_list is None:
            return

        # 2. 动态创建按钮并添加
        for actress in actress_list:
            actress_id = actress["actress_id"]
            name = actress["actress_name"]
            btn = ActressButton(actress_id, name)
            self.actress_in_layout.addWidget(btn)
            btn.raise_()

    def update_tag_buttons(self, tag_list:list[dict]):
        '''更新tag按钮'''
        # 1. 先清空之前按钮
        while self.tag_layout.count():
            item = self.tag_layout.takeAt(0)
            widget:QWidget = item.widget()
            if widget:
                widget.deleteLater()

        self.tag=QLabel("标签:")
        self.tag.setStyleSheet("""
            QLabel {
                font-size: 18px;           /* 字号 */
                font-family: 'Arial';      /* 字体 */
                font-weight: bold;         /* 粗体，可选 normal、bold、100-900 */
                color: grey;
                background-color: rgba(0, 0, 0, 0);
            }
        """)
        self.tag_layout.addWidget(self.tag)
        # 2. 动态创建按钮并添加
        #logging.debug(tag_list)
        for tag in tag_list:
            btn = CoverTagButton(tag["tag_id"], tag["tag_name"],tag["color"],tag["detail"])
            #btn.clickedWithId.connect(self.on_tag_clicked)
            self.tag_layout.addWidget(btn)
            btn.raise_()

    def play_video_with_default_player(self):
        '''打开指定的地址选择一个文件，开始用默认的播放器播放视频'''
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("视频文件 (*.mp4 *.avi *.mkv *.mov)")
        
        file_dialog.setDirectory(str(VIDEO_PATH))
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            video_path = selected_files[0]
            os.startfile(video_path)


    def resizeEvent(self, event):
        '''手动更新一些尺寸'''
        self.resize(self.parent().size())
        self.w = self.width()
        self.h = self.height()
        self.center_widget.setFixedWidth(self.h*0.75)#这些都要在resize中重写
        self.h_layout.setContentsMargins(0,0,self.h*0.8,0)#这些都要在resize中重写

class CoverBrowser(QWidget):
    '''封面浏览器+信息层+可切换+定时切换

    封面控件一共三层
    底层渐变层
    中间图片层
    上层交互信息层，#qt有拦截机制

    mide537这个图片有问题，需要测试

    输入字典列表初始化
    '''
    def __init__(self, works: list[dict]):
        super().__init__()

        self.works = works
        self.current_index = 0

        #背景图片层
        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(True)
        self.bg_label.lower()

        # 在 self.bg_label 上添加透明度效果
        self.opacity_effect = QGraphicsOpacityEffect(self.bg_label)
        self.bg_label.setGraphicsEffect(self.opacity_effect)

        #这个是上层阴影效果
        self.gradient_overlay = GradientOverlay(self)
        self.gradient_overlay.raise_()
        self.gradient_overlay.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        #这个是上层可交互的布局
        self.createbuttons()

        #自动加载图片
        self.load_current_image(animate=False)
        self.update_baseInfo()
        self.update_actress()
        self.update_tag()
        
        #启动定时器，每20秒切换一次封面
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_image)
        self.timer.start(20000)


    def createbuttons(self):
        '''这个是按钮层'''
        self.prev_button = QPushButton()
        self.next_button = QPushButton()

        #这个是信息层
        self.info_overlay=InfoOverlay(self)

        #self.info_overlay.raise_()
        #self.info_overlay.setGeometry(0, 0, self.width(), self.height())

        #按钮的外观设置
        self.next_button.setSizePolicy(
            self.next_button.sizePolicy().horizontalPolicy(),
            QSizePolicy.Expanding
        )
        self.next_button.setCursor(Qt.PointingHandCursor) 
        
        self.next_button.setIcon(QIcon(str(ICONS_PATH / "chevron-right.png")))
        self.next_button.setIconSize(QSize(48,48))
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding-left: 0px;
            }
        """)

        #按钮的外观设置
        self.prev_button.setSizePolicy(
            self.prev_button.sizePolicy().horizontalPolicy(),
            QSizePolicy.Expanding
        )
        self.prev_button.setCursor(Qt.PointingHandCursor) 
        self.prev_button.setIcon(QIcon(str(ICONS_PATH / "chevron-left.png")))
        self.prev_button.setIconSize(QSize(48,48))
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding-left: 0px;
            }
        """)

        self.prev_button.clicked.connect(self.prev_image)
        self.next_button.clicked.connect(self.next_image)

        btn_refresh=QPushButton("刷新")
        btn_refresh.clicked.connect(self.refresh_CoverBroswer)

        #两边按钮夹着中间可交互的信息层
        mainlayout = QHBoxLayout(self)
        mainlayout.setContentsMargins(0, 0, 0, 0)#完美贴边
        mainlayout.setSpacing(0)
        mainlayout.addWidget(self.prev_button)
        mainlayout.addWidget(self.info_overlay)
        mainlayout.addWidget(self.next_button)



    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_background_image(animate=False)
        self.info_overlay.setGeometry(self.rect()) #更新覆盖层的大小,使用覆盖层的时候需要重写这个函数去更新大小
        self.gradient_overlay.setGeometry(self.rect())

    def update_baseInfo(self):
        '''更新基础信息在这里'''
        work = self.works[self.current_index]
        self.info_overlay.serial_number.setText(work["serial_number"])
        self.info_overlay.time.setText(work["release_date"])
        self.info_overlay.story.setText(work["cn_story"][:150])
        self.info_overlay.work_name.setText(work["cn_title"][:50])

    def update_actress(self):
        '''更新女优的信息'''
        from core.database.query import findActressFromWorkID
        work_id = self.works[self.current_index]["work_id"]
        self.info_overlay.update_actress_buttons(findActressFromWorkID(work_id))
        #根据这个id去找女优

    def update_tag(self):
        '''更新tag信息'''
        from core.database.query import get_worktaginfo_by_workid
        work_id = self.works[self.current_index]["work_id"]
        self.info_overlay.update_tag_buttons(get_worktaginfo_by_workid(work_id))

    def load_current_image(self, animate=True):
        '''加载当前的图片'''
        from utils.utils import AlternativeQPixmap#这个目前还是有点问题
        work = self.works[self.current_index]
        path=str(WORKCOVER_PATH / work["image_url"])
        #pixmap = AlternativeQPixmap(path)
        from PySide6.QtGui import QImage
        imgmap = QImage(path)
        if imgmap.isNull():
            logging.info(f"加载失败: {path}")
            imgmap = QImage(800, 600)
            imgmap.fill(Qt.black)
        self.original_pixmap = QPixmap.fromImage(imgmap)
        del imgmap
        self.update_background_image(animate)

    def update_background_image(self, animate=True):
        #更新背景的图片，包括动画
        if not hasattr(self, "original_pixmap"):
            return

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

        self.gradient_overlay.set_scaled_width(scaled_width)#传值

        target_x = window_width - scaled_pixmap.width()
        target_y = 0

        self.bg_label.setPixmap(scaled_pixmap)#这里才是真正的设置了图片，并显示
        self.bg_label.resize(scaled_pixmap.width(), scaled_pixmap.height())

        if animate:
            start_x = window_width-scaled_width*0.9
            self.bg_label.move(start_x, target_y)

            # 动画1：位置动画（从右边滑入）
            pos_anim = QPropertyAnimation(self.bg_label, b"pos", self)
            pos_anim.setDuration(800)
            pos_anim.setStartValue(QPointF(start_x, target_y))
            pos_anim.setEndValue(QPointF(target_x, target_y))
            pos_anim.setEasingCurve(QEasingCurve.OutCubic)

            # 动画2：透明度动画（从 0 到 1）
            self.opacity_effect.setOpacity(0.0)
            opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity", self)
            opacity_anim.setDuration(800)
            opacity_anim.setStartValue(0.0)
            opacity_anim.setEndValue(1.0)
            opacity_anim.setEasingCurve(QEasingCurve.OutCubic)

            # 并行动画组
            self.anim_group = QParallelAnimationGroup(self)
            self.anim_group.addAnimation(pos_anim)
            self.anim_group.addAnimation(opacity_anim)
            self.anim_group.start()
            

        else:
            self.bg_label.move(target_x, target_y)

        self.gradient_overlay.resize(self.size())
        self.gradient_overlay.update()

    def prev_image(self):
        #timer负责在手动后重新开始计时器
        self.timer.stop()
        self.current_index = (self.current_index - 1) % len(self.works)
        self.update_baseInfo()
        self.update_actress()
        self.update_tag()
        self.load_current_image(animate=True)
        self.timer.start(20000)#重新设置一个计时

    def next_image(self):
        self.timer.stop()
        self.current_index = (self.current_index + 1) % len(self.works)
        self.update_baseInfo()
        self.update_actress()
        self.update_tag()
        self.load_current_image(animate=True)
        self.timer.start(20000)#重新设置一个计时

    def update_works(self, new_works: list[dict]):
        """接收新作品数据，重置状态并刷新界面"""
        self.works = new_works
        self.current_index = 0
        self.load_current_image()
        self.update_baseInfo()
        self.update_actress()
        self.update_tag()

    def refresh_CoverBroswer(self):
        from core.recommendation.Recommend import randomRec
        self.update_works(randomRec())


class CoverTagButton(QPushButton):
    '''给封面的tag使用'''
    clickedWithId = Signal(int)

    def __init__(self, tag_id:int, tag_name:str, color:str,detail:str):
        super().__init__(tag_name)
        self.tag_id = tag_id
        self.setStyleSheet(f"background-color: {color}; padding: 4px; border-radius: 6px;border: none; outline: none;")
        self.setToolTip(detail)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setCursor(Qt.PointingHandCursor)  # 手型指针
        self.clicked.connect(self.emit_with_id)
        
    def emit_with_id(self):
        from controller.GlobalSignalBus import global_signals
        global_signals.tag_clicked.emit(self.tag_id)#发送给那些需要重新加载的东西

# 自定义按钮，带演员id和名字
class ActressButton(QPushButton):
    '''给封面使用的'''
    def __init__(self, actress_id: int, name: str, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.actress_id = actress_id
        # 连接点击信号到内部槽，发出带id的信号
        self.clicked.connect(self.emit_with_id)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border-radius: 12px;
                font-weight: bold;
                font-size: 16px;
                padding: 4px; 
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
            QPushButton:pressed {
                background-color: #2e7d32;
            }
        """)

    def emit_with_id(self):
        from controller.GlobalSignalBus import global_signals
        global_signals.actress_clicked.emit(self.actress_id)
        #跳转到单个女优的页面