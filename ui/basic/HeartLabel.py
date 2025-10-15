
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QPropertyAnimation, Property,Signal
from PySide6.QtGui import QImage,QPainter
from config import ICONS_PATH
from pathlib import Path

class HeartLabel(QLabel):
    '''单个爱心控件，用来表示喜欢或者不喜欢'''
    clicked = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(32,32)
        self._img_off = QImage(Path(ICONS_PATH/"love_off.png"))
        self._img_on = QImage(Path(ICONS_PATH/"love_on.png"))
        self._checked = False

        #self.setPixmap(self._pix_off)
        self.setAlignment(Qt.AlignCenter)

        # 动画用的 scale 属性
        self._scale = 1.0
        self._anim = QPropertyAnimation(self, b"scale", self)


    # --- scale 属性 ---
    def getScale(self):
        return self._scale

    def setScale(self, value: float):
        self._scale = value
        self.update()

    scale = Property(float, getScale, setScale)

    def paintEvent(self, event):
        """
        核心绘制函数，使用 QImage 的 scaled() 方法进行高质量缩放。
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 获取当前要绘制的 QImage
        img = self._img_on if self._checked else self._img_off

        # 使用 QImage 的 scaled() 方法进行高质量缩放
        scaled_img = img.scaled(
            img.width() * self._scale,
            img.height() * self._scale,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation  # 使用平滑缩放模式
        )

        # 计算绘制位置，确保缩放后的图片在 QLabel 的中间
        draw_x = (self.width() - scaled_img.width()) / 2
        draw_y = (self.height() - scaled_img.height()) / 2
        
        # 将缩放后的 QImage 绘制到控件上
        painter.drawImage(draw_x, draw_y, scaled_img)


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._checked = not self._checked
            #self.setPixmap(self._pix_on if self._checked else self._pix_off)
                        # 播放动画：先缩小，再放大
            self._playAnimation()
            self.clicked.emit(self._checked)

    def _playAnimation(self):
        """播放缩小-放大动画"""
        self._anim.stop()
        self._anim.setDuration(350)  # 毫秒
        self._anim.setKeyValueAt(0, 1.0)
        self._anim.setKeyValueAt(0.3, 0.7)  # 先缩小
        self._anim.setKeyValueAt(0.6, 1.2)  # 再放大
        self._anim.setKeyValueAt(1, 1.0)    # 回归正常
        self._anim.start()
        # 仅在喜欢时生成粒子

    def isChecked(self):
        return self._checked
    
    def get_statue(self):
        return self._checked
    
    def set_statue(self,statue):
        self._checked=statue
        self.update()