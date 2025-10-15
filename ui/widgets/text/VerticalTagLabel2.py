"""
垂直标签标签组件 - VerticalTagLabel，都是继承并加上业务数据

该组件是一个自定义的垂直标签控件，支持点击事件、悬停效果和自定义样式。
用于显示带有背景色和文字颜色的标签，通常用于标签云或分类显示。


"""

from PySide6.QtGui import QColor,QPixmap,QCursor
from PySide6.QtCore import Signal,Qt
import logging
from config import ICONS_PATH
from pathlib import Path
from utils.utils import get_text_color_from_background,get_hover_color_from_background
from ui.basic.VLabel import VLabel

class VerticalTagLabel2(VLabel):
    """垂直标签组件，支持点击事件和悬停效果
    特性:
    - 自定义背景色和文字颜色
    - 根据背景颜色自动计算合适的文字颜色
    - 悬停状态颜色变化
    - 自定义鼠标指针
    - 点击信号发射
    
    Args:
        tag_id: 标签的唯一标识符
        text: 显示的文本内容
        tag_type: 标签类型
        background_color: 背景颜色
        detail: 标签详细信息
        tag_mutex: 标签互斥锁
        parent: 父组件
    """
    clicked = Signal()  # 自定义clicked信号
    def __init__(self,tag_id:int,text="",tag_type="",background_color="#cccccc",detail="",tag_mutex=None,parent=None):
        text_color = get_text_color_from_background(QColor(background_color))
        hover_color=get_hover_color_from_background(QColor(background_color))
        super().__init__(text,background_color,text_color,hover_color=hover_color)
        self.setCursor(QCursor(QPixmap(Path(ICONS_PATH/"mouse_on.png")),hotX=32,hotY=32))  # 手型指针
        self.setMouseTracking(True) # 允许追踪鼠标移动，不然只有按键才触发鼠标事件

        #业务数据
        self.tag_id:int= tag_id
        self.tag_mutex:int=tag_mutex
        self.tag_type:str=tag_type
        self.setToolTip(detail)

        #模拟hover
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()  # 发射clicked信号
        super().mousePressEvent(event)  # 保留默认行为

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)
    


class VerticalTagLabel(VLabel):
    '''仅展示功能不需要多的业务数据,但是这个还是带跳转的功能'''
    def __init__(self,tag_id,text="",background_color="#cccccc",detail="",parent=None):
        text_color = get_text_color_from_background(QColor(background_color))
        hover_color=get_hover_color_from_background(QColor(background_color))
        super().__init__(text,background_color,text_color,hover_color=hover_color)
        self.setCursor(QCursor(QPixmap(Path(ICONS_PATH/"mouse_on.png")),hotX=32,hotY=32))  # 手型指针
        self.setMouseTracking(True) # 允许追踪鼠标移动，不然只有按键才触发鼠标事件

        #业务数据
        self.tag_id = tag_id
        self.setToolTip(detail)

        #模拟hover
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            from controller.GlobalSignalBus import global_signals
            global_signals.tag_clicked.emit(self.tag_id)#跳转信号

        super().mousePressEvent(event)  # 保留默认行为

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def set_color(self,background_color):
        '''动态设置颜色'''
        text_color = get_text_color_from_background(QColor(background_color))
        hover_color=get_hover_color_from_background(QColor(background_color))
        self.setColors(background_color,text_color,hover_color)


class VShowTagLabel(VLabel):
    '''仅展示功能不需要多的业务数据'''
    def __init__(self,tag_id,text="",background_color="#cccccc",detail="",parent=None):
        text_color = get_text_color_from_background(QColor(background_color))
        hover_color=get_hover_color_from_background(QColor(background_color))
        super().__init__(text,background_color,text_color,hover_color=hover_color)
        self.setCursor(QCursor(QPixmap(Path(ICONS_PATH/"mouse_on.png")),hotX=32,hotY=32))  # 手型指针
        self.setMouseTracking(True) # 允许追踪鼠标移动，不然只有按键才触发鼠标事件

        #业务数据
        self.tag_id = tag_id
        self.setToolTip(detail)

    def set_color(self,background_color):
        '''动态设置颜色'''
        text_color = get_text_color_from_background(QColor(background_color))
        hover_color=get_hover_color_from_background(QColor(background_color))
        self.setColors(background_color,text_color,hover_color)


class VerticalActressLabel(VLabel):
    '''女演员的标签，跳转到女演员详细页'''

    def __init__(self,actress_id,name,background_color,parent=None):
        text_color = get_text_color_from_background(QColor(background_color))
        hover_color=get_hover_color_from_background(QColor(background_color))
        super().__init__(name,background_color,text_color,hover_color=hover_color)
        self.setCursor(QCursor(QPixmap(Path(ICONS_PATH/"mouse_on.png")),hotX=32,hotY=32))  # 手型指针
        self.setMouseTracking(True) # 允许追踪鼠标移动，不然只有按键才触发鼠标事件

        #业务数据
        self._actress_id=actress_id

        #模拟hover
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            from controller.GlobalSignalBus import global_signals
            global_signals.actress_clicked.emit(self._actress_id)
        super().mousePressEvent(event)  # 保留默认行为

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

class VerticalActorLabel(VLabel):
    '''男演员的标签，跳转到男演员的页面'''

    def __init__(self,actor_id,name,background_color,parent=None):
        text_color = get_text_color_from_background(QColor(background_color))
        hover_color=get_hover_color_from_background(QColor(background_color))
        super().__init__(name,background_color,text_color,hover_color=hover_color)
        self.setCursor(QCursor(QPixmap(Path(ICONS_PATH/"mouse_on.png")),hotX=32,hotY=32))  # 手型指针
        self.setMouseTracking(True) # 允许追踪鼠标移动，不然只有按键才触发鼠标事件

        #业务数据
        self._actor_id=actor_id

        #模拟hover
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            from controller.GlobalSignalBus import global_signals
            global_signals.actor_clicked.emit(self._actor_id)
        super().mousePressEvent(event)  # 保留默认行为

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)