from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPainter, QFontMetrics, QFont, QPainterPath, QColor
from PySide6.QtCore import QSize,QTimer,QDateTime
import logging

class VLabel(QLabel):
    '''这个没有任何的交互功能的垂直排版的Label'''

    def __init__(self,text,background_color="#cccccc",text_color="#000000", fixed_width=None,fixed_height=None,border_color="#00000000",hover_color="#000000",parent=None):
        super().__init__(text, parent)

        self.setWordWrap(False)
        self.setMouseTracking(True) # 允许追踪鼠标移动，不然只有按键才触发鼠标事件
        self._hovered=False#带悬浮文字变色的功能
        self.chinese_font = QFont("KaiTi", 12)
        self.chinese_font.setBold(True)
        self.english_font = QFont("Courier New", 14)
        self.english_font.setBold(True)
        
        self.setFont(self.english_font)
        # 固定比例
        self.corner_cut_ratio = 0.2
        self.hole_radius_ratio = 0.1

        self.hover_color =QColor(hover_color)   # 悬浮时字体颜色
        self.border_color = QColor(border_color)
        self.text_color = QColor(text_color)
        self.background_color = QColor(background_color)

        # 初始化时计算一次固定大小
        self._fixed_size = self._calculate_size(fixed_width, fixed_height)
        self.setFixedSize(self._fixed_size)

        self._flash_timer = QTimer(self)
        self._flash_timer.timeout.connect(self._flash_toggle)
        self._flash_running = False
        self._flash_end_time = None
        self._flash_interval = 300
        self._flash_inverted = False

    def setTextDynamic(self, new_text):
        """动态设置文本，重新计算尺寸并重绘"""
        new_text = new_text or ""
        super().setText(new_text)  # 设置 QLabel 文本
        # 重新计算尺寸
        self._fixed_size = self._calculate_size(None, None)
        self.setFixedSize(self._fixed_size)
        self.update()  # 触发重绘

    def setColors(self, background_color, text_color, hover_color=None):
        """动态设置颜色"""
        self.background_color = QColor(background_color)
        self.text_color = QColor(text_color)
        if hover_color:
            self.hover_color = QColor(hover_color)
        self.update()  # 触发重绘

    def _calculate_size(self, fixed_width, fixed_height):
        """宽度按中文计算，高度按每个字符实际字体计算"""
        if fixed_width and fixed_height:
            return QSize(fixed_width, fixed_height)

        
        # 中文宽度（全角字符）
        metrics_cn = QFontMetrics(self.chinese_font)
        standard_char_width = metrics_cn.horizontalAdvance("中")
        width = standard_char_width * 1.7  # 稍微留边 

        if self.text()=="":#避免空字符下标越界
            return QSize(width, width*2)

        # 高度逐字符累加
        total_height = 0
        for ch in self.text():
            if ch == '\n':
                continue
            fm = QFontMetrics(self._select_font(ch))
            if self.is_chinese(ch):
                char_height=fm.height()#中文就是正常
            else:
                char_height=fm.ascent()+fm.descent()*0.3#英文不加leading,缩短下距离，这个与实际绘制是同步的
            total_height += char_height

        #第一个字符视觉修正
        font = self._select_font(self.text()[0])#选择第一个字符的语言,这里如果传入的字符是空的，就会下标越界
        fm = QFontMetrics(font)
        char_width = fm.horizontalAdvance(self.text()[0])
        if self.is_chinese(self.text()[0]):
            fmodify=char_width*0.1# 第一个字符视觉修正
        else:
            fmodify=char_width*0.4
        
        height = total_height + width * self.corner_cut_ratio * 3+width *self.hole_radius_ratio*2-fm.descent()*0.3-fmodify
        #logging.debug(f"计算文字高度{total_height}")
        #logging.debug(f"计算宽高({width},{height})")
        return QSize(int(width), int(height))

    def is_chinese(self, char):
        return 0x4E00 <= ord(char) <= 0x9FFF or '\u3040' <= char <= '\u30ff'

    def _select_font(self, char):
        """根据字符选择字体：中文/日文用中文字体，其它用英文字体"""
        if '\u4e00' <= char <= '\u9fff' or '\u3040' <= char <= '\u30ff':
            return self.chinese_font
        else:
            return self.english_font

    def sizeHint(self):
        # 直接返回初始化时计算好的固定值
        return self._fixed_size

    def paintEvent(self, event):
        #super().paintEvent(event)#不要继承，否则就会调用QLabel的绘图功能了
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        cut = rect.width() * self.corner_cut_ratio
        hole_radius = rect.width() * self.hole_radius_ratio
        #logging.debug(f"外框大小,({rect.width()},{rect.height()})")
        #logging.debug(f"倒角半径{cut}")
        #logging.debug(f"打孔半径{hole_radius}")
        # 外层
        outer_path = QPainterPath()
        outer_path.moveTo(cut, 0)
        outer_path.lineTo(rect.width() - cut, 0)
        outer_path.lineTo(rect.width(), cut)
        outer_path.lineTo(rect.width(), rect.height() - cut)
        outer_path.lineTo(rect.width() - cut, rect.height())
        outer_path.lineTo(cut, rect.height())
        outer_path.lineTo(0, rect.height() - cut)
        outer_path.lineTo(0, cut)
        outer_path.closeSubpath()

        # 孔
        hole_path = QPainterPath()
        hole_center_x = rect.width() // 2
        hole_center_y = cut + hole_radius
        hole_path.addEllipse(hole_center_x - hole_radius, hole_center_y - hole_radius,
                             hole_radius * 2, hole_radius * 2)


        outer_path2 = outer_path.subtracted(hole_path)#最重要的扣洞函数，但是也导致了一个问题，内外框一体了

        # 画背景
        painter.setClipPath(outer_path2)
        painter.fillRect(rect, self.background_color)
        painter.setClipping(False)

        if self._hovered:
            self.out_color=QColor("#FF0000")
        else:
            self.out_color=self.border_color

        # 外框
        painter.setPen(self.border_color)
        painter.drawPath(outer_path)

        # 孔边框
        painter.setPen(self.out_color)
        painter.drawPath(hole_path)

        # 中文格宽度
        metrics_cn = QFontMetrics(self.chinese_font)
        max_char_width = metrics_cn.horizontalAdvance("中")  

        # 总文本高度（逐字符）
        #total_height = sum(QFontMetrics(self._select_font(ch)).height() for ch in self.text() if ch != '\n')
        #logging.debug(f"文本总高度{total_height}")
        fmodify=0
        if self.text()!="":
            font = self._select_font(self.text()[0])#选择第一个字符的语言
            fm = QFontMetrics(font)
            char_width = fm.horizontalAdvance(self.text()[0])
            if self.is_chinese(self.text()[0]):
                fmodify=char_width*0.1# 第一个字符视觉修正
            else:
                fmodify=char_width*0.4
        y = cut*2+hole_radius*2-fmodify
        #logging.debug(f"起步高度{y}")

        # 绘制字符
        for char in self.text():
            if char == '\n':
                continue
            font = self._select_font(char)
            painter.setFont(font)
            #painter.setPen(self.text_color)
            if self._hovered:
                painter.setPen(self.hover_color)
            else:
                painter.setPen(self.text_color)

            # 该字符的宽度
            fm = QFontMetrics(font)
            char_width = fm.horizontalAdvance(char)

            if self.is_chinese(char):
                char_height=fm.height()#中文就是正常
            else:
                char_height=fm.ascent()+fm.descent()*0.3#英文不加leading
            
            # 水平居中在中文格
            char_x = (rect.width() - max_char_width) // 2 + (max_char_width - char_width) // 2

            # 绘制
            painter.drawText(char_x, y + fm.ascent(), char)

            # 向下移动
            y += char_height

        #logging.debug(f"尾部高度{y}")
        painter.end()

    def flash_invert(self, duration=3000, interval=300, flash_bg_color=None, flash_text_color=None):
        from utils.utils import invert_color

        if not hasattr(self, "_original_bg"):
            self._original_bg = self.background_color
            self._original_text = self.text_color

        self._flash_bg_color = flash_bg_color or invert_color(self._original_bg)
        self._flash_text_color = flash_text_color or invert_color(self._original_text)

        self._flash_interval = interval
        now = QDateTime.currentMSecsSinceEpoch()
        self._flash_end_time = now + duration

        if not self._flash_timer.isActive():
            self._flash_timer.start(self._flash_interval)
        self._flash_running = True

    def _flash_toggle(self):
        now = QDateTime.currentMSecsSinceEpoch()
        if now >= self._flash_end_time:
            # 恢复原色
            self.background_color = self._original_bg
            self.text_color = self._original_text
            self.update()
            self._flash_timer.stop()
            self._flash_running = False
            self._flash_inverted = False
            return

        # 切换颜色
        if self._flash_inverted:
            self.background_color = self._original_bg
            self.text_color = self._original_text
        else:
            self.background_color = self._flash_bg_color
            self.text_color = self._flash_text_color

        self._flash_inverted = not self._flash_inverted
        self.update()