from PySide6.QtWidgets import QTabBar, QStylePainter, QStyleOptionTab, QStyle
from PySide6.QtCore import QRect, Qt, QSize
from PySide6.QtGui import QFontMetrics, QPainter, QColor,QFont
import re

class VerticalTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("VerticalTabBar")
        # 设置标签栏为垂直方向
        self.setShape(QTabBar.RoundedWest)
        self._line_spacing = self.fontMetrics().height() * 0.05  # 字之间上下间距
        self._column_spacing = self.fontMetrics().height() * 0.1  # 列之间间距
        self.setFont(QFont("Microsoft YaHei", 12))

    def _replace_ellipsis(self, text: str) -> str:
        """替换标点符号为竖排专用符号"""
        if text == "" or text is None:
            return ""
        text = text.replace("，", "\uFE10")
        text = text.replace("、", "\uFE11")
        text = text.replace("。", "\uFE12")
        text = text.replace("：", "\uFE13")
        text = text.replace("；", "\uFE14")
        text = text.replace("！", "\uFE15")
        text = text.replace("？", "\uFE16")
        text = text.replace("……", "\uFE19")     # 中文全角省略号
        text = text.replace("\u2026", "\uFE19")  # 单个 U+2026
        text = text.replace("\u22EF", "\uFE19")  # ⋯
        text = text.replace("（", "\uFE35")       
        text = text.replace("）", "\uFE36")
        text = text.replace("【", "\uFE3B")
        text = text.replace("】", "\uFE3C")        
        text = text.replace("《", "\uFE3D")
        text = text.replace("》", "\uFE3E")
        text = text.replace("〈", "\uFE3F")
        text = text.replace("〉", "\uFE40")
        text = text.replace("'", "\uFE41")
        text = text.replace("'", "\uFE42")
        text = text.replace("「", "\uFE41")
        text = text.replace("」", "\uFE42")
        text = text.replace("『", "\uFE43")
        text = text.replace("』", "\uFE44")
        return text

    def split_text_blocks(self, text: str):
        """把字符串分成 [中文/标点, 英文数字串, 中文/标点, ...] 这样的块"""
        blocks = []
        buffer = ""
        is_english = None

        for ch in text:
            if re.match(r"[A-Za-z0-9\-()]", ch):
                # 当前是英文/数字
                if is_english is False:  # 前一个是中文 → 先保存
                    blocks.append(buffer)
                    buffer = ""
                buffer += ch
                is_english = True
            else:
                # 当前是中文/标点
                if is_english is True:  # 前一个是英文 → 先保存
                    blocks.append(buffer)
                    buffer = ""
                buffer += ch
                is_english = False

        if buffer:
            blocks.append(buffer)
        return blocks

    def paintEvent(self, event):
        painter = QStylePainter(self)
        opt = QStyleOptionTab()

        try:
            for i in range(self.count()):
                self.initStyleOption(opt, i)
                rect = self.tabRect(i)
                
                # 绘制标签背景
                painter.drawControl(QStyle.CE_TabBarTabShape, opt)
                
                # 设置字体和对齐方式
                painter.setFont(self.font())
                painter.setRenderHint(QPainter.TextAntialiasing)
                
                # 获取文本并处理标点符号
                text = self._replace_ellipsis(self.tabText(i))
                
                fm = painter.fontMetrics()
                char_height = fm.height() + self._line_spacing
                char_width = fm.maxWidth()
                
                # 计算起始位置，使文本在标签中居中
                x = rect.right() - char_width  # 从右往左开始
                y = rect.top()
                
                # 遍历文本块并绘制
                for block in self.split_text_blocks(text):
                    if re.match(r"[A-Za-z0-9\-()]+$", block):
                        # 英文数字块：整体旋转90度
                        br = fm.boundingRect(block)
                        block_w = br.width()
                        block_h = br.height()
                        
                        painter.save()
                        painter.translate(x + char_width/2, y + block_w/2)
                        painter.rotate(90)
                        painter.drawText(-block_w/2, fm.ascent() - block_h/2, block)
                        painter.restore()
                        
                        y += block_w + self._line_spacing
                    else:
                        # 中文和标点：逐字绘制
                        for ch in block:
                            painter.drawText(QRect(x, y, char_width, char_height),
                                          Qt.AlignCenter, ch)
                            y += char_height
        finally:
            painter.end()

    def tabSizeHint(self, index):
        # 获取文本并处理标点符号
        text = self._replace_ellipsis(self.tabText(index))
        fm = self.fontMetrics()
        
        # 基础测量
        char_height = fm.height()
        char_width = fm.maxWidth()
        
        # 计算padding（和绘制时保持一致）
        padding_vertical = int(char_height * 0.2)  # 上下padding
        padding_horizontal = int(char_width * 0.3)  # 左右padding
        
        # 计算总高度
        total_height = padding_vertical * 2  # 初始值为上下padding
        
        # 遍历文本块计算实际高度
        for block in self.split_text_blocks(text):
            if re.match(r"[A-Za-z0-9\-()]+$", block):
                # 英文数字块：整体旋转90度后的高度
                block_width = fm.boundingRect(block).width()
                total_height += block_width + self._line_spacing
            else:
                # 中文和标点：逐字计算
                total_height += (char_height + self._line_spacing) * len(block)
        
        # 设置宽度限制
        max_single_width = max(fm.horizontalAdvance(c) for c in text if c.strip())
        min_width = int(max_single_width * 1.5)
        ideal_width = max_single_width + padding_horizontal * 2
        max_width = int(max_single_width * 2.5)
        
        # 确保宽度在限制范围内
        width = max(min_width, min(ideal_width, max_width))
        
        return QSize(width, total_height)
