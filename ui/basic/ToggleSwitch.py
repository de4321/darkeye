from PySide6.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QSize, Signal, Property, QPropertyAnimation
from PySide6.QtGui import QPainter, QColor, QBrush


class ToggleSwitch(QWidget):
    toggled = Signal(bool)  # 状态改变信号

    def __init__(self, parent=None, width=50, height=28):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self._checked = False

        # 动画属性
        self._offset = 2
        self._bg_color = QColor("#777")  # 初始背景色
        self._circle_color = QColor("#DDD")

        # 动画对象（位置 + 背景色）
        self._anim_offset = QPropertyAnimation(self, b"offset", self)
        self._anim_offset.setDuration(200)

        self._anim_bg = QPropertyAnimation(self, b"bgColor", self)
        self._anim_bg.setDuration(200)

        # 颜色配置
        self._inactive_color = QColor("#777")
        self._active_color = QColor("#00b16a")

    # ---------------- 属性：圆点偏移 ----------------
    def get_offset(self):
        return self._offset

    def set_offset(self, value):
        self._offset = value
        self.update()

    offset = Property(float, get_offset, set_offset)

    # ---------------- 属性：背景颜色 ----------------
    def get_bgColor(self):
        return self._bg_color

    def set_bgColor(self, value):
        self._bg_color = value
        self.update()

    bgColor = Property(QColor, get_bgColor, set_bgColor)

    # ---------------- 绘制 ----------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        radius = rect.height() / 2

        # 背景
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self._bg_color))
        painter.drawRoundedRect(rect, radius, radius)

        # 圆点
        circle_radius = rect.height() - 4
        painter.setBrush(QBrush(self._circle_color))
        painter.drawEllipse(self._offset, 2, circle_radius, circle_radius)

    # ---------------- 点击切换 ----------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setChecked(not self._checked)

    # ---------------- 状态方法 ----------------
    def isChecked(self):
        return self._checked

    def setChecked(self, checked: bool):
        if self._checked == checked:
            return
        self._checked = checked
        self.toggled.emit(self._checked)

        # 圆点动画
        start = self._offset
        end = self.width() - self.height() + 2 if self._checked else 2
        self._anim_offset.stop()
        self._anim_offset.setStartValue(start)
        self._anim_offset.setEndValue(end)
        self._anim_offset.start()

        # 背景颜色动画
        self._anim_bg.stop()
        self._anim_bg.setStartValue(self._bg_color)
        self._anim_bg.setEndValue(self._active_color if self._checked else self._inactive_color)
        self._anim_bg.start()

    checked = Property(bool, isChecked, setChecked)
