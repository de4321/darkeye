from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QMouseEvent,QPixmap,QImage
from PySide6.QtCore import Qt,Signal,QRect,QThreadPool,QRunnable,SignalInstance,Slot,QTimer
import logging
from utils.utils import mosaic_qimage
from controller.GlobalSignalBus import global_signals

class ImageLoaderRunnable(QRunnable):
    '''QImage异步加载图片并裁剪，回到UI线程后显示'''
    def __init__(self, path: str, aspect_ratio: float, target_size, callback_signal:SignalInstance):
        super().__init__()
        self.path = path
        self.aspect_ratio = aspect_ratio
        self.target_size = target_size
        self.callback_signal = callback_signal  # 信号，发回 UI 线程

    def run(self):
        img = QImage(str(self.path))
        if not img.isNull():
            w, h = img.width(), img.height()
            crop_x = w - h * self.aspect_ratio
            crop_w = h * self.aspect_ratio
            img = img.copy(crop_x, 0, crop_w, h)#裁剪
            img = img.scaled(
                self.target_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        self.callback_signal.emit(img)  # 发信号回 UI 线程

class ImageLoaderRunnable2(QRunnable):
    '''QImage异步加载图片并裁剪，回到UI线程后显示'''
    def __init__(self, path: str, aspect_ratio: float, target_size, callback_signal: Signal):
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

class CoverImage(QLabel):
    '''正常的显示半封面的qlabel，加上发射跳转信号的功能
    异步加载图片
    '''

    jump_to_modify_work=Signal()#发射修改作品的信号
    image_ready = Signal(QImage)  # 用信号回到 UI 线程

    def __init__(self,image_path: str,work_id:int,standard:bool,green_mode=False, parent=None):
        super().__init__(parent)
        from core.database.query import query_studio
        self._aspect_ratio=0.7
        self._path=image_path
        self._work_id=work_id
        self._masaic=green_mode
        self._standard=standard
        #self.setStyleSheet("border: 1px solid red; border-radius: 4px;")
        # 绑定信号
        self.image_ready.connect(self._set_pixmap)
        self._update_image()

        global_signals.green_mode_changed.connect(self._update_masaic)#这个东西要管得到新创建的和老的



    @Slot(bool)
    def _update_masaic(self,is_masaic:bool):
        self._masaic=is_masaic
        #logging.debug(f"图片切换绿色模式{self._masaic}")
        self._update_image()
    
    def _update_image(self):
        if self._standard:#正规
            self.setFixedSize(210,300)
            self._show_right_half_async()
        else:#非正规
            self.setFixedSize(210,120)
            self._show_all_async()

    def _show_right_half_async(self):
        if not self._path:
            self.setText("无封面")
            return
        runnable = ImageLoaderRunnable(self._path, self._aspect_ratio, self.size(), self.image_ready)
        QThreadPool.globalInstance().start(runnable)

    def _show_all_async(self):
        if not self._path:
            self.setText("无封面")
            return
        runnable = ImageLoaderRunnable2(self._path, self._aspect_ratio, self.size(), self.image_ready)
        QThreadPool.globalInstance().start(runnable)
        
    def _set_pixmap(self, img: QImage):
        if img.isNull():
            self.setText("无封面")
        else:
            #logging.debug(f"图片的绿色模式是{self._masaic}")
            if self._masaic:
                img=mosaic_qimage(img)
            pixmap=QPixmap.fromImage(img)
            self.setPixmap(pixmap)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.RightButton:

            QTimer.singleShot(0, lambda: self.jump_to_modify_work.emit())
            logging.debug(f"跳转到修改作品界面")
            event.accept()  # 消费掉右键事件
        if event.button() == Qt.MouseButton.LeftButton:
            from controller.GlobalSignalBus import global_signals
            QTimer.singleShot(0, lambda: global_signals.work_clicked.emit(self._work_id))
            logging.debug(f"跳转单个作品界面：ID:{self._work_id}")
            event.accept()  # 消费掉左键事件



# 废弃代码

    def _show_all(self):
        '''这个是给非标准的显示全部图片使用的'''
        if self._path is None:
            self.setText("无封面")
            return

        # 1. 使用 QImage 读取图片
        original_image = QImage(str(self._path))
        if original_image.isNull():
            logging.warning("图片加载失败,可能是不存在图片")
            self.setText("无封面")
            return
        cropped_pixmap = QPixmap.fromImage(original_image)
        scaled_pixmap = cropped_pixmap.scaled(
            self.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled_pixmap)

    def _show_right_half(self):
        '''
        内部函数，显示一半的图片
        使用 QImage 处理，用 QPixmap 显示
        '''
        if self._path is None:
            self.setText("无封面")
            return

        # 1. 使用 QImage 读取图片
        original_image = QImage(str(self._path))
        if original_image.isNull():
            logging.warning("图片加载失败,可能是不存在图片")
            self.setText("无封面")
            return

        # 2. 对 QImage 进行处理（裁剪）
        width = original_image.width()
        height = original_image.height()
        
        # 计算裁剪区域，并对 QImage 进行裁剪
        crop_x = width - height * self._aspect_ratio
        crop_width = height * self._aspect_ratio
        
        cropped_image = original_image.copy(QRect(crop_x, 0, crop_width, height))
        del original_image #释放对象
        # 3. 将处理后的 QImage 转换为 QPixmap 并缩放
        # 直接在 QPixmap 上进行缩放，因为显示性能更优
        cropped_pixmap = QPixmap.fromImage(cropped_image)
        del cropped_image#释放对象
        scaled_pixmap = cropped_pixmap.scaled(
            self.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        del cropped_pixmap#释放对象
        '''
        final_pixmap = QPixmap(scaled_pixmap.size())
        final_pixmap.fill(Qt.GlobalColor.transparent)  # 透明背景
        painter = QPainter(final_pixmap)
        painter.drawPixmap(0, 0, scaled_pixmap)

        borderpath=Path(ICONS_PATH/"frame.png")
        border = QPixmap(borderpath)  # 你的边框文件路径
        # 边框缩放到和目标图像一致
        border = border.scaled(
            scaled_pixmap.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        painter.drawPixmap(0, 0, border)
        painter.end()
        '''
        # 4. 将最终的 QPixmap 设置到 QLabel 上
        self.setPixmap(scaled_pixmap)

