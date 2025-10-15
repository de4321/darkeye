import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#---------------------------------------------------------------------------------------------------

import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QScrollArea,
                               QGridLayout, QLabel)
from PySide6.QtCore import Qt, QSize, QRandomGenerator
from PySide6.QtGui import QColor

# ----------------------------------------------------------------------
# QScrollArea 是核心，它需要一个子 Widget 作为其内容。
# 所有的布局都将应用在这个子 Widget 上。
# ----------------------------------------------------------------------

class WaterfallLayoutApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 颜色模拟瀑布流布局")
        self.resize(800, 600)

        # 创建一个主垂直布局
        main_layout = QVBoxLayout(self)

        # ----------------------------------------------------------------------
        # 创建 QScrollArea 和其内部的内容容器
        # ----------------------------------------------------------------------
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True) # 允许内容 Widget 调整大小以适应滚动区域

        # 创建一个 QWidget 作为所有内容的容器
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)

        # 为内容容器设置一个垂直布局
        content_layout = QVBoxLayout(content_widget)
        content_layout.setAlignment(Qt.AlignTop) # 确保内容从顶部开始排列

        # ----------------------------------------------------------------------
        # 添加顶部的固定 Widget
        # ----------------------------------------------------------------------
        top_widget = QLabel("这是一个顶部的固定区域")
        top_widget.setStyleSheet("background-color: lightblue; padding: 20px; font-size: 24px;")
        top_widget.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(top_widget)

        # ----------------------------------------------------------------------
        # 添加模拟的瀑布流布局
        # ----------------------------------------------------------------------
        
        # 瀑布流布局参数
        columns = 3
        
        # 使用 QGridLayout 来模拟瀑布流布局
        waterfall_layout = QGridLayout()
        
        # 将瀑布流布局添加到内容布局中
        content_layout.addLayout(waterfall_layout)

        # 动态添加项目到瀑布流布局中
        
        row_indices = [0] * columns  # 记录每一列的当前行索引
        
        for i in range(50):  # 添加 50 个颜色标签
            # 创建一个 QLabel 来显示颜色和文本
            label = QLabel(f"项目 {i+1}")
            
            # 使用 QRandomGenerator 生成随机高度和颜色
            random_height = QRandomGenerator.global_().bounded(150, 350)
            random_color = QColor(QRandomGenerator.global_().bounded(256),
                                  QRandomGenerator.global_().bounded(256),
                                  QRandomGenerator.global_().bounded(256))
                                  
            # 设置标签的样式
            label.setStyleSheet(f"""
                background-color: {random_color.name()};
                color: white;
                border: 1px solid gray;
                padding: 10px;
            """)
            label.setAlignment(Qt.AlignCenter)
            label.setMinimumSize(QSize(200, random_height)) # 设置最小尺寸

            # 找到当前最短的列
            shortest_col_index = row_indices.index(min(row_indices))
            
            # 将新的标签添加到最短的列
            waterfall_layout.addWidget(label, row_indices[shortest_col_index], shortest_col_index)
            
            # 更新该列的行索引
            row_indices[shortest_col_index] += 1
            
        main_layout.addWidget(scroll_area)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WaterfallLayoutApp()
    ex.show()
    sys.exit(app.exec())

