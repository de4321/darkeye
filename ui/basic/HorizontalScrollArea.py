from PySide6.QtWidgets import QScrollArea
from PySide6.QtCore import Qt

class HorizontalScrollArea(QScrollArea):
    def wheelEvent(self, event):
        """使用滚轮进行水平滚动"""
        if event.angleDelta().y() != 0:  # 垂直滚轮
            # 改成水平滚动
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - event.angleDelta().y()
            )
            event.accept()
        else:
            super().wheelEvent(event)