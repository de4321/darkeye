from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import QSize,Qt
from PySide6.QtGui import QIcon
import logging
from config import ICONS_PATH


class IconPushButton(QPushButton):
    '''专门的只有icon的PushButton'''

    def __init__(self,iconpath:str="arrow-up.png",iconsize=20,outsize=24,hoverable=True):
        super().__init__()
        self.setIcon(QIcon(str(ICONS_PATH / iconpath)))
        self.setCursor(Qt.PointingHandCursor)
        self.setFlat(True)
        self.setIconSize(QSize(iconsize,iconsize))
        self.setFixedSize(outsize,outsize)

        if hoverable:
            self.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                border-radius: 6px;   /* 圆角半径 */
            }
            QPushButton:hover {
                background-color: lightgray; /* 悬停时灰色背景 */
            }
            """)
        else:
                        self.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                border-radius: 6px;   /* 圆角半径 */
            }
            """)
                        
    def set_icon(self,iconpath:str="arrow-up.png"):
        self.setIcon(QIcon(str(ICONS_PATH / iconpath)))
