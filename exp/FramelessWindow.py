import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QCursor

MARGIN = 8  # 可拉伸边缘范围

#自定义的无边框项目
class FramelessWindow(QMainWindow):
    #无边框窗口
    #可拉伸
    #可移动方案
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setMinimumSize(400,300)
        #self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)  # 使 mouseMoveEvent 在不按键时也能响应

        # 内部状态

        self._is_resizing = False
        self._resize_dir = None
        self._drag_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            self._resize_dir = self._get_resize_direction(event.position())
            self._is_resizing = self._resize_dir is not None

    def mouseMoveEvent(self, event):
        pos = event.position()#获得在窗体内的相对位置
        global_pos = event.globalPosition().toPoint()#获得在屏幕的相对位置
        
        if self._is_resizing:
            self._resize_window(global_pos)
        elif event.buttons() == Qt.LeftButton:
            # 拖动窗口
            delta = global_pos - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = global_pos
        else:
            # 鼠标移动改变光标
            self._update_cursor(pos)

    def mouseReleaseEvent(self, event):
        self._is_resizing = False
        self._resize_dir = None
        #松开鼠标后改变鼠标的图形
        pos = event.position()
        self._update_cursor(pos)
        if event.button() == Qt.LeftButton:
            self._handleSnap(event.globalPosition().toPoint())
            event.accept()

    def _get_resize_direction(self, pos: QPoint):
        x, y, w, h = pos.x(), pos.y(), self.width(), self.height()
        directions = {
            (True, True): 'top_left',
            (False, True): 'top_right',
            (True, False): 'bottom_left',
            (False, False): 'bottom_right',
        }
        # 四角判断
        if x <= MARGIN and y <= MARGIN:
            return 'top_left'
        elif x >= w - MARGIN and y <= MARGIN:
            return 'top_right'
        elif x <= MARGIN and y >= h - MARGIN:
            return 'bottom_left'
        elif x >= w - MARGIN and y >= h - MARGIN:
            return 'bottom_right'
        elif x <= MARGIN:
            return 'left'
        elif x >= w - MARGIN:
            return 'right'
        elif y <= MARGIN:
            return 'top'
        elif y >= h - MARGIN:
            return 'bottom'
        else:
            return None

    def _update_cursor(self, pos: QPoint):
        direction = self._get_resize_direction(pos)
        cursor_map = {
            'left': Qt.SizeHorCursor,
            'right': Qt.SizeHorCursor,
            'top': Qt.SizeVerCursor,
            'bottom': Qt.SizeVerCursor,
            'top_left': Qt.SizeFDiagCursor,
            'bottom_right': Qt.SizeFDiagCursor,
            'top_right': Qt.SizeBDiagCursor,
            'bottom_left': Qt.SizeBDiagCursor,
        }
        self.setCursor(cursor_map.get(direction, Qt.ArrowCursor))

    def _resize_window(self, global_mouse_pos: QPoint):
        if not self._resize_dir:
            return

        rect = self.geometry()#当前的窗体
        diff = global_mouse_pos - self._drag_pos
        new_rect = QRect(rect)

        min_width = self.minimumWidth()
        min_height = self.minimumHeight()

        updated=False

        if 'left' in self._resize_dir:
            new_left = new_rect.left() + diff.x()
            if new_rect.right() - new_left >= min_width:
                new_rect.setLeft(new_left)
                updated=True
            else:
                new_rect.setLeft(new_rect.right() - min_width)

        if 'right' in self._resize_dir:
            new_right = new_rect.right() + diff.x()
            if new_right - new_rect.left() >= min_width:
                new_rect.setRight(new_right)
                updated=True
            else:
                new_rect.setRight(new_rect.left() + min_width)

        if 'top' in self._resize_dir:
            new_top = new_rect.top() + diff.y()
            if new_rect.bottom() - new_top >= min_height:
                new_rect.setTop(new_top)
                updated=True
            else:
                new_rect.setTop(new_rect.bottom() - min_height)

        if 'bottom' in self._resize_dir:
            new_bottom = new_rect.bottom() + diff.y()
            if new_bottom - new_rect.top() >= min_height:
                new_rect.setBottom(new_bottom)
                updated=True
            else:
                new_rect.setBottom(new_rect.top() + min_height)
        if updated:
            self.setGeometry(new_rect)
            self._drag_pos = global_mouse_pos

    def _handleSnap(self, global_pos):
        screen = QApplication.primaryScreen()
        geometry = screen.geometry()
        x, y = global_pos.x(), global_pos.y()
        margin = 10  # 判定靠边的范围（单位：像素）

        if y <= geometry.y() + margin:
            # 顶部 → 最大化
            if self.isMaximized():
                self.showNormal()
            self.showMaximized()
            print("最大化")
        elif x <= geometry.x() + margin:
            # 左侧 → 左半屏
            self.setGeometry(
                geometry.x(),
                geometry.y(),
                geometry.width() // 2,
                geometry.height()
            )
            print("左半屏")
        elif x >= geometry.x() + geometry.width() - margin:
            # 右侧 → 右半屏
            self.setGeometry(
                geometry.x() + geometry.width() // 2,
                geometry.y(),
                geometry.width() // 2,
                geometry.height()
            )
            print("右半屏")
        else:
            # 不靠边 → 恢复常规
            self.showNormal()
            print("正常")

