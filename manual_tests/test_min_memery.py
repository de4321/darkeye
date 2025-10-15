import sys
import numpy as np
import psutil
import matplotlib
matplotlib.use("QtAgg")  # 使用 PySide6 兼容的后端

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 + NumPy + Matplotlib + Memory")

        # 布局
        layout = QVBoxLayout(self)

        # matplotlib 画布
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # 内存标签
        self.mem_label = QLabel("Memory usage: ")
        layout.addWidget(self.mem_label)

        # 按钮：刷新数据 & 内存用量
        btn = QPushButton("生成随机数据并更新")
        btn.clicked.connect(self.update_plot)
        layout.addWidget(btn)

        self.update_plot()

    def update_plot(self):
        # 使用 numpy 生成数据
        x = np.linspace(0, 10, 200)
        y = np.sin(x) + np.random.normal(0, 0.1, x.shape)

        # 绘图
        ax = self.figure.clear()
        ax=self.figure.add_subplot(111)
        ax.plot(x, y, label="随机数据")
        ax.legend()
        self.canvas.draw()

        # 获取内存用量 (MB)
        process = psutil.Process()
        mem_mb = process.memory_info().rss / 1024 / 1024
        self.mem_label.setText(f"Memory usage: {mem_mb:.2f} MB")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.resize(600, 500)
    w.show()
    sys.exit(app.exec())
