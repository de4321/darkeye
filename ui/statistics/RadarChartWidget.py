import sys
import math
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsTextItem, QGraphicsPolygonItem, QGraphicsLineItem,QFrame
from PySide6.QtGui import QPen, QBrush, QColor, QPolygonF, QPainter,QFont
from PySide6.QtCore import Qt, QPointF

class RadarChartWidget(QGraphicsView):
    '''这个自绘的，似乎会更加的自由的简单的一点
    传进来的值一定是[0,1]归一化后的数据
    categories:这个是标签列表
    values:这个是归一化后的列表
    show_values:这个是原始列表，可能会有""
    '''
    def __init__(self, categories=None, values=None,show_values=None, num_layers=5, parent=None):
        super().__init__(parent)
        self.categories = categories
        self.values = values

        if show_values is None:
            self.show_values=values
        else:
            self.show_values=show_values

        self.setFrameStyle(QFrame.NoFrame)
        self.num_layers = num_layers
        self.max_value = 1

        # 创建场景和视图
        self.myscene = QGraphicsScene(self)
        self.setScene(self.myscene)
        self.setRenderHints(QPainter.Antialiasing)

        # 设置背景透明
        self.setStyleSheet("background: transparent; border: none;")
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        
        # 设置场景背景透明
        self.myscene.setBackgroundBrush(QBrush(Qt.transparent))
        # 设置视口属性
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)#关闭滚轮
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.center_x, self.center_y = 100, 100
        self.max_radius = 80
        self.angle_offset = math.pi / 2  # 第一条轴朝上

        self.pen_grid = QPen(QColor("gray"), 1)
        self.pen_axis = QPen(QColor("gray"), 1)
        self.pen_data = QPen(QColor("blue"), 2)
        self.brush_data = QBrush(QColor(0, 100, 255, 100))

        # 创建字体对象
        '''
        self.categories_font = QFont()
        self.categories_font.setPointSize(10)  # 设置字体大小
        self.categories_font.setBold(True)     # 设置粗体
        self.categories_font.setFamily("SimHei")  # 设置字体家族
        '''


    def draw_grid(self):
        num_categories = len(self.categories)
        for i in range(1, self.num_layers + 1):
            radius = self.max_radius * i / self.num_layers
            points = []
            for j in range(num_categories):
                angle = -2 * math.pi * j / num_categories + self.angle_offset
                x = self.center_x + radius * math.cos(angle)
                y = self.center_y - radius * math.sin(angle)
                points.append(QPointF(x, y))
            points.append(points[0])
            polygon = QPolygonF(points)
            poly_item = QGraphicsPolygonItem(polygon)
            poly_item.setPen(self.pen_grid)
            poly_item.setBrush(Qt.NoBrush)
            self.myscene.addItem(poly_item)

    def draw_axes(self):
        num_categories = len(self.categories)
        for i in range(num_categories):
            angle = -2 * math.pi * i / num_categories + self.angle_offset
            x = self.center_x + self.max_radius * math.cos(angle)
            y = self.center_y - self.max_radius * math.sin(angle)
            line = QGraphicsLineItem(self.center_x, self.center_y, x, y)
            line.setPen(self.pen_axis)
            self.myscene.addItem(line)

    def draw_labels(self):
        '''绘制类型标签'''
        num_categories = len(self.categories)
        for i, label in enumerate(self.categories):
            angle = -2 * math.pi * i / num_categories + self.angle_offset
            x = self.center_x + (self.max_radius + 20) * math.cos(angle)
            y = self.center_y - (self.max_radius + 20) * math.sin(angle)
            text_item = QGraphicsTextItem(label)
            # 设置字体
            #text_item.setFont(self.categories_font)
            # 设置文本颜色
            #text_item.setDefaultTextColor(QColor("darkblue"))
            text_item.setPos(x - text_item.boundingRect().width()/2,
                             y - text_item.boundingRect().height()/2)
            self.myscene.addItem(text_item)

    def draw_data(self):
        num_categories = len(self.categories)
        points = []
        for i, value in enumerate(self.values):
            angle = -2 * math.pi * i / num_categories + self.angle_offset
            radius = self.max_radius * value / self.max_value
            x = self.center_x + radius * math.cos(angle)
            y = self.center_y - radius * math.sin(angle)
            points.append(QPointF(x, y))

            # 数据标签
            label_text = QGraphicsTextItem(str(self.show_values[i]))
            label_text.setPos(x + 10 * math.cos(angle) - label_text.boundingRect().width()/2,
                              y - 10 * math.sin(angle) - label_text.boundingRect().height()/2)
            self.myscene.addItem(label_text)
            label_text.setDefaultTextColor(QColor("red"))

        points.append(points[0])  # 闭合
        polygon = QPolygonF(points)
        poly_item = QGraphicsPolygonItem(polygon)
        poly_item.setPen(self.pen_data)
        poly_item.setBrush(self.brush_data)
        self.myscene.addItem(poly_item)
    
    def update_chart(self, categories=None, values=None, show_values=None):
        """更新数据并重绘"""
        if categories is not None:
            self.categories = categories
        if values is not None:
            self.values = values
        if show_values is not None:
            self.show_values = show_values
        else:
            self.show_values = self.values

        # 清空场景
        self.myscene.clear()

        # 重新绘制
        self.draw_grid()
        self.draw_axes()
        self.draw_labels()
        self.draw_data()