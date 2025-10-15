import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QLayout, QSizePolicy,QHBoxLayout
from PySide6.QtCore import Qt, QRect, QPoint, QSize
from PySide6.QtGui import QColor, QPalette
from ui.basic import VFlowLayout
from ui.widgets.text.VerticalTagLabel2 import VerticalTagLabel,VerticalActressLabel,VerticalTagLabel2

class DemoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FlowLayout 竖向流布局示例")
        

        self.mainlayout = QHBoxLayout(self)
        self.mainlayout.setContentsMargins(0,0,0,0)
        self.mainlayout.setSpacing(0)
        widget1=QWidget()
        widget2=QWidget()
        widget1.setFixedHeight(300)
        widget2.setFixedHeight(300)
        layout1=VFlowLayout(widget1,spacing=8,margin=0)
        layout2=VFlowLayout(widget2,spacing=8,margin=0)

        from core.database.query import get_worktaginfo_by_workid

        self.update_tag(get_worktaginfo_by_workid(3),layout1)
        self.update_tag(get_worktaginfo_by_workid(336),layout2)
        self.mainlayout.addStretch(1)
        self.mainlayout.addWidget(widget1)
        self.mainlayout.addWidget(widget2)


    def update_tag(self, tag_list:list[dict],layout:QLayout):

        '''更新tag'''
        # 1. 先清空之前按钮
        while layout.count():
            item = layout.takeAt(0)
            widget:QWidget = item.widget()
            if widget:
                widget.deleteLater()

        # 2. 动态创建按钮并添加
        #logging.debug(tag_list)
        for tag in tag_list:
            label = VerticalTagLabel(tag["tag_id"], tag["tag_name"],tag["color"],tag["detail"])
            layout.addWidget(label)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()
    sys.exit(app.exec())