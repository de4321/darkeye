from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtGui import QPainter, QFont, QColor, QFontMetrics, QPen
from PySide6.QtCore import Qt, QRect, QSize
import re
import logging
from .VerticalTextLayout import VerticalTextLayout

class VerticalTextLabel(QWidget):
    '''纯粹的竖向文字类，自绘
    标点符号用法GB/T 15834-2011
    数字用法GB/T 15835-2011
    主要是标点符号，。、！、：；位于相应文件之下偏右
    破折，省略号，连接号位于居中，就是转了90度
    《》〈〉这种也对应转90
    单双引号，括号的的更改
    '''
    def __init__(self, text="", parent=None):
        super().__init__(parent)

        self._font = QFont("Microsoft YaHei", 14)
        fm = QFontMetrics(self._font)
        
        self._text_color = QColor(0, 0, 0)
        self._line_spacing = fm.height()*0.05   # 字之间上下间距
        self._column_spacing = fm.height()*0.1  # 列之间间距
        self._text = ""
        self._layout = VerticalTextLayout(fm, self._line_spacing, self._column_spacing)
        self._text_blocks = []  # 缓存排版结果
        
        self.setText(text)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def setText(self, text):
        text = VerticalTextLayout.replace_ellipsis(text)
        self._text = text
        self._updateLayout()
        self.update()
        self.updateGeometry()  # 重新计算尺寸

    def setFont(self, font):
        self._font = font
        self._layout = VerticalTextLayout(
            QFontMetrics(self._font), 
            self._line_spacing, 
            self._column_spacing
        )
        self._updateLayout()
        self.update()

    def _updateLayout(self):
        """更新文本布局"""
        self._text_blocks = self._layout.calculate_layout(
            self._text,
            self.width(),
            self.height()
        )

    def setTextColor(self, color):
        self._text_color = QColor(color)
        self.update()

    def paintEvent(self, event):
        '''使用预先计算好的布局信息进行绘制'''
        super().paintEvent(event)
        with QPainter(self) as painter:
            pen = QPen(Qt.red, 2)
            painter.setPen(pen)
            painter.drawRect(self.rect().adjusted(1, 1, -1, -1))  # 画个红色边框

            painter.setRenderHint(QPainter.TextAntialiasing)
            painter.setFont(self._font)
            painter.setPen(self._text_color)

            # 使用预先计算好的布局信息绘制
            for block in self._text_blocks:
                if block.is_english:#英文绘制
                    painter.save()
                    # 在矩形中心进行旋转
                    center = block.rect.center()
                    painter.translate(center)
                    painter.rotate(block.rotation)
                    # 计算文本位置，考虑基线
                    text_width = painter.fontMetrics().boundingRect(block.text).width()
                    painter.drawText(-text_width/2, block.ascent/2, block.text)
                    painter.restore()
                else:#中日文绘制
                    painter.drawText(block.rect, Qt.AlignCenter, block.text)

    def sizeHint(self):
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        '''使用排版类计算所需尺寸'''
        return self._layout.calculate_size(self._text, self.height())

    def resizeEvent(self, event):
        """当控件大小改变时，重新计算布局"""
        super().resizeEvent(event)
        self._updateLayout()