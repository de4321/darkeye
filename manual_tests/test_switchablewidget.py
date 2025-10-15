from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette

class ColorWidget(QWidget):
    """简单颜色背景 QWidget"""
    def __init__(self, color: str):
        super().__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("可切换 QWidget 示例")
        self.resize(400, 300)

        # 左右切换按钮
        self.btn_prev = QPushButton("⬅ 上一个")
        self.btn_next = QPushButton("下一个 ➡")

        # 绑定按钮点击
        self.btn_prev.clicked.connect(self.show_prev)
        self.btn_next.clicked.connect(self.show_next)

        # 三个示例 QWidget
        self.widget1 = ColorWidget("lightblue")
        self.widget2 = ColorWidget("lightgreen")
        self.widget3 = ColorWidget("lightyellow")

        # QStackedWidget 管理多个 QWidget
        self.stack = QStackedWidget()
        self.stack.addWidget(self.widget1)
        self.stack.addWidget(self.widget2)
        self.stack.addWidget(self.widget3)

        # 布局
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_prev)
        btn_layout.addWidget(self.btn_next)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.stack)

    def show_prev(self):
        index = self.stack.currentIndex()
        index = (index - 1) % self.stack.count()  # 循环切换
        self.stack.setCurrentIndex(index)

    def show_next(self):
        index = self.stack.currentIndex()
        index = (index + 1) % self.stack.count()  # 循环切换
        self.stack.setCurrentIndex(index)

if __name__ == "__main__":
    app = QApplication([])
    w = MainWindow()
    w.show()
    app.exec()