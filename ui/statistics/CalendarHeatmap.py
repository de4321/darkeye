from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtCore import Qt, QRectF, QDate,QSize


class CalendarHeatmap(QWidget):
    '''日历热力图仿github那种'''
    def __init__(self, year=2025, data=None, parent=None):
        super().__init__(parent)
        self.setFixedSize(1020,190)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.year = year
        # data: dict of QDate -> bool (是否撸管)
        self.data = data or {}
        
        self.cell_width = 14
        self.cell_height = 14
        self.cell_spacing = 4
        
        self.margin_top = 40
        self.margin_left = 40
        self._compute_basic()
        
    def _compute_basic(self):
        # 计算该年第一天和最后一天
        self.first_date = QDate(self.year, 1, 1)
        self.last_date = QDate(self.year, 12, 31)
        
        # 星期顺序，我们用周一开始排
        #self.week_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        self.week_days = ["一", "二", "三", "四", "五", "六", "日"]

        # 计算该年有多少天
        self.days_count = self.first_date.daysTo(self.last_date) + 1

        # 计算每一天的位置，方便画格子
        self.day_positions = {}  # QDate -> (col, row)
        self._compute_positions()
        
        # 计算总列数（最大列）
        self.columns = max(col for col, row in self.day_positions.values()) + 1

    def sizeHint(self):
        total_width = self.columns * self.cell_width + (self.columns - 1) * self.cell_spacing
        total_height = 7 * self.cell_height + 6 * self.cell_spacing
        return QSize(total_width, total_height)

    def _compute_positions(self):
        # 遍历该年每一天，按周一到周日计算行列
        current = self.first_date
        col = 0
        
        while current <= self.last_date:
            # Qt的dayOfWeek(): 周一=1 ... 周日=7
            weekday = current.dayOfWeek() - 1  # 0-6，周一=0
            
            self.day_positions[current] = (col, weekday)
            
            if weekday == 6:  # 周日，下一列
                col += 1
            current = current.addDays(1)
    
    def paintEvent(self, event): 
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("white"))
        
        # ===== 绘制外框 =====
        margin = 10  # 外边距
        border_radius = 12  # 圆角半径
        border_rect = self.rect().adjusted(
            margin, margin, -margin, -margin
        )
        pen = QPen(QColor(100, 100, 100), 2)  # 灰色边框，线宽2
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(border_rect, border_radius, border_radius)


        # 画星期文字
        painter.setPen(Qt.black)
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        for i, wd in enumerate(self.week_days):
            y = self.margin_top + i * (self.cell_height + self.cell_spacing) + self.cell_height * 0.8
            painter.drawText(15, y, wd)
        
        # 画月份标注（跨多列居中）
        self._draw_month_labels(painter)
        
        # 画日期格子
        for date, (col, row) in self.day_positions.items():
            x = self.margin_left + col * (self.cell_width + self.cell_spacing)
            y = self.margin_top + row * (self.cell_height + self.cell_spacing)
            rect = QRectF(x, y, self.cell_width, self.cell_height)
            
            # 根据数据决定颜色
            value= self.data.get(date, 0)
            match value:
                case 1:
                    color = QColor(100, 255, 100)  # 绿
                case 2:
                    color = QColor(150, 200, 50)   # 黄绿
                case 3:
                    color = QColor(255, 200, 0)    # 黄橙
                case 4:
                    color = QColor(255, 100, 100)  # 红
                case _:            
                    color = QColor(230, 230, 230)
            
            # 设置圆角半径
            radius = 3  # 可以调节，单位像素

            # 画圆角矩形填充
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)  # 不画边框
            painter.drawRoundedRect(rect, radius, radius)#绘制带点圆角的
            #painter.setPen(QPen(Qt.black, 0.5))
            #painter.drawRect(rect)
        
        painter.end()
    
    def _draw_month_labels(self, painter):
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(Qt.black)
        
        current_month = 1
        first_col_of_month = None
        
        # 通过遍历每个日期，判断月份变化，画月份文字居中
        sorted_dates = sorted(self.day_positions.keys())
        for i, date in enumerate(sorted_dates):
            col, row = self.day_positions[date]
            if date.month() != current_month:
                # 上个月份结束，绘制文字
                if first_col_of_month is not None:
                    last_col = col - 1
                    self._draw_month_text(painter, current_month, first_col_of_month, last_col)
                current_month = date.month()
                first_col_of_month = col
            if i == len(sorted_dates) - 1:
                # 年底最后一个月绘制
                self._draw_month_text(painter, current_month, first_col_of_month, col)
            elif first_col_of_month is None:
                first_col_of_month = col
    
    def _draw_month_text(self, painter:QPainter, month, first_col, last_col):
        # 计算月份文字绘制位置（列居中）
        x = self.margin_left + ((first_col + last_col + 1) / 2) * (self.cell_width + self.cell_spacing)
        y = self.margin_top - 10
        #month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
        #               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month_names = ["一月", "二月", "三月", "四月", "五月", "六月", 
                       "七月", "八月", "九月", "十月", "十一月", "十二月"]
        text = month_names[month - 1]
        fm = painter.fontMetrics()
        text_w = fm.horizontalAdvance(text)
        painter.drawText(x - text_w/2, y, text)

    def update_data(self,year:int, data: dict):
        """
        更新热力图的数据，并刷新显示

        data: dict of QDate -> int (0~4) 表示不同强度
        """
        self.year=year
        self.data = data or {}
        self._compute_basic()
        self.update()  # 触发 paintEvent 重绘