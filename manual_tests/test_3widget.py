import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QSizePolicy
from PySide6.QtCore import QPropertyAnimation, QEasingCurve
import sys

#测试三个控件，左边的不动，中间消失，右边扩展
class Demo(QWidget):
    def __init__(self):
        super().__init__()

        self.left_btn = QPushButton("左控件")
        self.middle_btn = QPushButton("中间控件")
        self.right_btn = QPushButton("右控件")

        self.left_btn.setFixedWidth(100)
        self.right_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout = QHBoxLayout(self)
        layout.addWidget(self.left_btn)
        layout.addWidget(self.middle_btn)
        layout.addWidget(self.right_btn)


        # 中间控件的初始宽度，用于动画目标值
        self.middle_btn_width = self.middle_btn.sizeHint().width()
        self.middle_btn.setMaximumWidth(self.middle_btn_width)
        # 创建动画对象，作用在中间控件的 maximumWidth 属性上
        self.anim = QPropertyAnimation(self.middle_btn, b"maximumWidth")
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)

        self.left_btn.clicked.connect(self.toggle_middle)

    def toggle_middle(self):
        if self.middle_btn.maximumWidth() > 0:
            # 动画收缩宽度到0
            self.anim.setStartValue(self.middle_btn.maximumWidth())
            self.anim.setEndValue(0)
        else:
            # 动画展开宽度到正常宽度
            self.anim.setStartValue(self.middle_btn.maximumWidth())
            self.anim.setEndValue(self.middle_btn_width)
        self.anim.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Demo()
    w.resize(500, 100)
    w.show()
    sys.exit(app.exec())
