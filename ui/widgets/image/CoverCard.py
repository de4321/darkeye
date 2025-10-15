
#用于展示封面一半的图片+标题+番号

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QPainter,QColor,QPainterPath
from PySide6.QtCore import Qt,Signal,Slot
from config import WORKCOVER_PATH
from pathlib import Path
import logging
from ui.widgets.text.ClickableLabel import ClickableLabel
from .CoverImage import CoverImage
from utils.utils import replace_sensitive


class CoverCard(QWidget):
    def __init__(self, title: str,image_path: str,serial_number,work_id,standard:bool,color="#87CEEB",green_mode=False,parent=None):
        super().__init__(parent)
        #self.setStyleSheet("border: 1px solid red; border-radius: 4px;")
        self.setFixedWidth(220)
        self.background_color=color
        self._work_id=work_id
        self.original_title=title
        self._green_mode=green_mode

        if image_path is None:
            #self._path=Path(ICONS_PATH/"none.png")
            self._path=None
        else:
            self._path=Path(WORKCOVER_PATH/image_path)
        #logging.debug(f"卡片的绿色模式{green_mode}")
        self.image_label = CoverImage(self._path,self._work_id,standard,green_mode)
        
        self.title_label = QLabel(title)

        if green_mode:#新创造的修改
            self.title_label.setText(replace_sensitive(title))

        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;           /* 字号 */
                font-family: 'Microsoft YaHei';      /* 字体 */
                font-weight: bold;         /* 粗体，可选 normal、bold、100-900 */
                color: grey;
                background-color: rgba(0, 0, 0, 0);
            }
        """)
        self.serial_number=serial_number
        self.serial_number_label=ClickableLabel(serial_number)


        self.image_label.setAlignment(Qt.AlignCenter)

        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFixedWidth(210)

        self.serial_number_label.setAlignment(Qt.AlignCenter)
        self.serial_number_label.setStyleSheet("""
            QLabel {
                font-size: 16px;           /* 字号 */
                font-family: 'Microsoft YaHei';      /* 字体 */
                font-weight: bold;         /* 粗体，可选 normal、bold、100-900 */
                color: black;
                background-color: rgba(0, 0, 0, 0);
            }
        """)


        layout = QVBoxLayout(self)
        w=self.width()*0.15
        if title !="":
            layout.setContentsMargins(5,10,5,20)
        else:
            layout.setContentsMargins(5,10,5,w)
        layout.addWidget(self.serial_number_label,alignment=Qt.AlignCenter)
        layout.addWidget(self.image_label)
        #if title !="":
        layout.addWidget(self.title_label)
        
        self.signal_connect()

    def signal_connect(self):
        '''信号转接'''
        self.image_label.jump_to_modify_work.connect(lambda:global_signals.modify_work_clicked.emit(self.serial_number))
        from controller.GlobalSignalBus import global_signals
        global_signals.green_mode_changed.connect(self._update_green_mode)
        global_signals.work_data_changed.connect(self._update_card)
        

    @Slot()
    def _update_card(self):
        '''更新卡片信息'''
        #查作品标题
        from core.database.query import get_workcardinfo_by_workid
        data=get_workcardinfo_by_workid(self._work_id)
        self.title_label.setText(data['cn_title'])#更新标题
        #更新图片
        image_path=data['image_url']
        if image_path is None:
            #self._path=Path(ICONS_PATH/"none.png")
            self._path=None
        else:
            self._path=Path(WORKCOVER_PATH/image_path)
        self.image_label._path=self._path
        
        #更框的大小
        self.image_label._standard=data['standard']
        self.image_label._update_image()
        #更新外框颜色
        self.background_color=self.backgroundcolor_from_tagid(data['tag_id'])
        self.update()

    @Slot(bool)
    def _update_green_mode(self,green_mode:bool):
        '''更新绿色模式'''
        self._green_mode=green_mode
        if self._green_mode:
            self.title_label.setText(replace_sensitive(self.original_title))
        else:
            self.title_label.setText(self.original_title)

    '''
    def paintEvent(self, event):
        """绘制方形背景，把 label 全包进去"""
        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QColor("#EC9090"))  # 背景色
            painter.setPen(Qt.NoPen)
            painter.drawRect(self.rect())  # 直接画整个 widget 区域

        # 调用父类 paintEvent 让子控件正常绘制
        super().paintEvent(event)
    '''
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        cut = w*0.15  # 倒角的长度（四角削去的边长）

        path = QPainterPath()
        path.moveTo(cut, 0)
        path.lineTo(w - cut, 0)
        path.lineTo(w, cut)
        path.lineTo(w, h - cut)
        path.lineTo(w - cut, h)
        path.lineTo(cut, h)
        path.lineTo(0, h - cut)
        path.lineTo(0, cut)
        path.closeSubpath()

        painter.fillPath(path, QColor(self.background_color))  # 背景颜色
        super().paintEvent(event)


    @staticmethod
    def backgroundcolor_from_tagid(tag_id:int|None)->str:
        match tag_id:
            case 1:
                return "#80B0F8"
            case 2:
                return "#F88441"
            case 3:  
                return "#FDEB48"
            case None:
                return "#00000000"