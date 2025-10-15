import psutil, os
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print("空 Python 进程:", psutil.Process(os.getpid()).memory_info().rss/1024/1024, "MB")


from PySide6.QtWidgets import QWidget, QStackedWidget,QPushButton, QLabel, QHBoxLayout, QVBoxLayout,QLineEdit,QApplication
from PySide6.QtCore import Qt,Signal,QTimer
from PySide6.QtGui import QIcon,QPixmap,QKeySequence,QShortcut,QPainter,QColor
print("导入 PySide6 后:", psutil.Process(os.getpid()).memory_info().rss/1024/1024, "MB")


#from ui.page import WorkPage,ManagementPage,StatisticsPage,ActressPage,ActorPage,AvPage,SingleActressPage,SingleWorkPage
#from config import ICONS_PATH,set_size_pos,get_size_pos,is_max_window,set_max_window
from ui.widgets import CoverBrowser
#from core.recommendation.Recommend import recommendStart,randomRec
#import logging
#from qframelesswindow import FramelessWindow, TitleBar, StandardTitleBar

print("导入 一堆东西 后:", psutil.Process(os.getpid()).memory_info().rss/1024/1024, "MB")

from ui.main_window import MainWindow
app = QApplication([])
w = MainWindow()
w.show()
print("创建空窗口后:", psutil.Process(os.getpid()).memory_info().rss/1024/1024, "MB")