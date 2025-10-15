import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QStackedWidget, QHBoxLayout, QLabel

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.stacked_widget = QStackedWidget()
        # 添加几个页面
        self.stacked_widget.addWidget(QLabel("页面 1"))
        self.stacked_widget.addWidget(QLabel("页面 2"))
        self.stacked_widget.addWidget(QLabel("页面 3"))

        # 左右按钮
        self.btn_prev = QPushButton("←")
        self.btn_next = QPushButton("→")

        self.btn_prev.clicked.connect(self.show_prev)
        self.btn_next.clicked.connect(self.show_next)

        # 布局
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_prev)
        btn_layout.addWidget(self.btn_next)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.stacked_widget)
        main_layout.addLayout(btn_layout)

    def show_prev(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index > 0:
            self.stacked_widget.setCurrentIndex(current_index - 1)

    def show_next(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index < self.stacked_widget.count() - 1:
            self.stacked_widget.setCurrentIndex(current_index + 1)


if __name__ == "__main__":
    app = QApplication([])
    w = MainWidget()
    w.show()
    app.exec()