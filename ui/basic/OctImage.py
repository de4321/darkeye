
#用于展示封面一半的图片+标题+番号

from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap,QPainter,QPolygonF,QPainterPath,QRegion,QImage
from PySide6.QtCore import Qt,Signal,QPointF,QThreadPool,QRunnable
from config import ACTRESSIMAGES_PATH
from pathlib import Path
import logging
import math
from ui.basic.Effect import ShadowEffectMixin

class ImageLoaderRunnable(QRunnable):
    '''QImage异步加载图片并裁剪，回到UI线程后显示'''
    def __init__(self, path: str, target_size, callback_signal: Signal):
        super().__init__()
        self.path = path
        self.target_size = target_size
        self.callback_signal = callback_signal  # 信号，发回 UI 线程

    def run(self):
        img = QImage(str(self.path))
        if not img.isNull():
            img = img.scaled(
                self.target_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        self.callback_signal.emit(img)  # 发信号回 UI 线程


class OctImage(QLabel,ShadowEffectMixin):
    '''正八边形的显示图片的工具，无其他功能'''
    image_ready = Signal(QImage)  # 用信号回到 UI 线程

    def __init__(self,image_path:str=None, parent=None):
        super().__init__(parent)
        self._d=150#直径
        self.set_shadow()
        #self.setStyleSheet("border: 1px solid red; border-radius: 4px;")
        self.setFixedSize(self._d,self._d)
        if image_path is None:
            #self._path=Path(ICONS_PATH/"none.png")
            self._path=None
        else:
            self._path=Path(ACTRESSIMAGES_PATH/image_path)
        
        self.setFixedSize(self._d, self._d)  # 封面尺寸
        self.setAlignment(Qt.AlignCenter)
        #self._show_image()
        self.image_ready.connect(self._set_pixmap)
        self._show_image_async()

    def _show_image_async(self):
        if not self._path:
            self.setText("无封面")
            return
        runnable = ImageLoaderRunnable(self._path,self.size(), self.image_ready)
        QThreadPool.globalInstance().start(runnable)

    def _set_pixmap(self, img: QImage):
        '''回到UI线程开始绘图'''
        if img.isNull():
            self.setText("无封面")
            return

        # 构造正八边形
        d = self._d
        c = d / (2 + math.sqrt(2))
        polygon = QPolygonF()
        points = [
            (c, 0), (d - c, 0), (d, c), (d, d - c),
            (d - c, d), (c, d), (0, d - c), (0, c),
        ]
        for x, y in points:
            polygon.append(QPointF(x, y))

        # 4. 将处理后的 QImage 转换为 QPixmap 并显示
        self.setPixmap(QPixmap.fromImage(img))

        # 设置八边形掩码
        region = QRegion(polygon.toPolygon())
        self.setMask(region)

    def update_image(self, image_path: str):
        """
        更新图片并重绘，提供给外部使用
        """
        if image_path is None:
            self._path = None
            self.setText("无封面")
            self.clearMask()
        else:
            self._path = Path(ACTRESSIMAGES_PATH / image_path)
            self._show_image_async()