from PySide6.QtWidgets import QLabel,QSizePolicy,QFileDialog,QMenu
from PySide6.QtGui import QPixmap,QImage, QDragEnterEvent, QDropEvent,QMouseEvent,QAction
from PySide6.QtCore import Qt,Signal,QRect,Slot
import shutil,logging,os,subprocess
from datetime import datetime
from pathlib import Path

from config import WORKCOVER_PATH,TEMP_PATH
from controller import MessageBoxService


def is_temp_path(path: str | Path) -> bool:
    """判断路径是否是临时路径（检查路径中包含'temp'）"""
    path_obj = Path(path) if isinstance(path, str) else path
    return "temp" in path_obj.parts  # 检查路径各部分是否包含'temp'

class CoverDropWidget(QLabel):
    '''可拖动式添加封面的QLabel'''
    
    cover_changed=Signal()
    def __init__(self):
        super().__init__()
        self._aspect_ratio = 0.7 # 宽高比 
        self.setMaximumHeight(800)
        self.setScaledContents(False)  # 关闭默认拉伸
        self.setAcceptDrops(True)  # 允许拖放
        self.setText("把JAV封面拖进来")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 2px dashed gray; font-size: 16px; padding: 0px;margin: 0px;")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) 
        self._original_pixmap = None  # 保存原始图像,这个是个QPixmap对象
        self._path=None #这个是核心，这是一个绝对的地址，可以是临时的，可以是正式数据库里的
        #这个要实现双向绑定的状态，传进来图片地址,数据驱动，而不是手动去设置
        self.msg=MessageBoxService(self)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择封面图片",
                "",
                "图片文件 (*.jpg *.jpeg *.png *.bmp *.gif *.webp)"
            )
            if file_path:
                if self.is_image(file_path):
                    self._path = self.temp_save_image(file_path)
                    self._show_right_harf()
                    self.cover_changed.emit()
                else:
                    self.msg.show_info("文件类型错误", f"不是图片文件：{file_path}")
        else:
            super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        open_folder_action = QAction("打开图片所在位置", self)
        open_folder_action.triggered.connect(self.open_image_folder)

        #clear_action = QAction("清除封面", self)
        #clear_action.triggered.connect(lambda: self.set_image(None))

        menu.addAction(open_folder_action)
        #menu.addAction(clear_action)

        menu.exec(event.globalPos())

    # ✅ 新增：打开图片所在文件夹
    def open_image_folder(self):
        if not self._path or not os.path.exists(self._path):
            self.msg.show_info("错误", "当前没有可打开的图片。")
            return

        folder = os.path.dirname(self._path)

        try:
            if os.name == "nt":  # Windows
                subprocess.run(["explorer", "/select,", self._path])
            elif os.name == "posix":  # macOS / Linux
                subprocess.run(["xdg-open", folder])
        except Exception as e:
            logging.error("无法打开文件夹: %s", e)
            self.msg.show_info("错误", f"无法打开文件夹: {e}")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        '''拖进来的函数'''
        urls = event.mimeData().urls()
        for url in urls:
            file_path = url.toLocalFile()
            if self.is_image(file_path):
                self._path=self.temp_save_image(file_path)
                self._show_right_harf()#拖入后显示，实现绑定
                self.cover_changed.emit()
            else:
                self.msg.show_info("文件类型错误", f"不是图片文件：{file_path}")

    def temp_save_image(self, src_path: str) -> str:
        """使用pathlib保存图片到临时目录，返回一个绝对路径"""
        src = Path(src_path)  # 将源路径转为Path对象
        
        # 生成带时间戳的新文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dst_name = f"image_{timestamp}{src.suffix.lower()}"  # 直接获取后缀
        
        TEMP_PATH.mkdir(parents=True, exist_ok=True)#若不存在临时目录，自动创建
        # 构建目标路径（自动处理跨平台路径分隔符）
        dst_path = Path(TEMP_PATH) / dst_name
        
        # 拷贝文件
        shutil.copy(src, dst_path)  # Path对象可直接用于shutil.copy
        logging.info("图片已临时保存到%s",dst_path)
        
        # 返回字符串路径（兼容旧代码）
        return str(dst_path)

    def is_image(self, path: str | Path) -> bool:
        """使用 pathlib 判断文件是否是图片（支持传入字符串或Path对象）"""
        # 统一转为 Path 对象处理
        file_path = Path(path) if isinstance(path, str) else path
        # 获取后缀并判断（更简洁的写法）
        return file_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

    def _show_right_harf(self):
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

        # 3. 将处理后的 QImage 转换为 QPixmap 并缩放
        # 直接在 QPixmap 上进行缩放，因为显示性能更优

        self._original_pixmap= QPixmap.fromImage(cropped_image)
        scaled_pixmap = self._original_pixmap.scaled(
            self.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        
        # 4. 将最终的 QPixmap 设置到 QLabel 上
        self.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        '''改变大小的事件'''
        #w = self.width()
        h = self.height()
        w = int(h * self._aspect_ratio)
        self.setFixedWidth(w)  # 或者你想 setFixedWidth(int(h * aspect_ratio))
        if self._original_pixmap:
            scaled = self._original_pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            super().setPixmap(scaled)
        super().resizeEvent(event)

    @Slot(str)
    def set_image(self,relative_image_path:str|None):
        '''这是提供给外部的接口
        这个是输入相对地址给外面的界面用的，set后立刻显示，实现绑定
        '''
        #todo
        #现在这个被重复加载两次，有bug
        #logging.debug("设置的相对路径是:%s",relative_image_path)
        if relative_image_path is None or relative_image_path=="":
            #if self._path is not None and is_temp_path(self._path):#这个临时保存后再次切换就有问题了
            #    self.delete_image()#现在有个问题就是这个临时文件夹会变大，不清理的话，找个函数清理
            #先删除临时路径的文件
            self._path=None
            self._original_pixmap=None #清空原始图像
            self.setPixmap(QPixmap()) 
            self.setText("把JAV封面拖进来")
            return
        #logging.debug(str(WORKCOVER_PATH))
        self._path=str(WORKCOVER_PATH / relative_image_path)#这里拼接的规则A/B当B是绝对路径时返回B否则拼接,这个非常的神奇，虽然会运行两次，但是靠bug然后完成了需求，因为这个可能会传进来临时的绝对路径
        logging.debug("图片路径是:%s",self._path)
        self._show_right_harf()
        self.cover_changed.emit()

    def get_image(self)->str:
        '''返回现在的URL'''
        return self._path


