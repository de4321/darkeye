from PySide6.QtWidgets import QLayout
from PySide6.QtCore import QSize, QPoint, QRect, Qt
import logging

class WaterfallLayout(QLayout):
    def __init__(self, parent=None, margin=10, spacing=10, column_width=220):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.column_width = column_width
        self._items = []

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def expandingDirections(self):
        return Qt.Orientations(0)

    def hasHeightForWidth(self):
        return False

    def sizeHint(self):#这个估算也是有问题的
        #现在就是外部需要时默认撑开三列
        return QSize(self.column_width * 4 + self.spacing() * 3,
                     self.minimumHeight())

    def minimumHeight(self):
        # 最低列高
        return max((item.sizeHint().height() for item in self._items), default=0)

    def clearItems(self):
        for i in reversed(range(len(self._items))):
            item = self.takeAt(i)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
        self._items.clear()
        
    def setGeometry(self, rect):
        super().setGeometry(rect)
        if not self._items:
            return
        spacing = self.spacing()
        left, top, right, bottom = self.getContentsMargins()
        max_width = rect.width() - left - right
        column_count = max(1, max_width // (self.column_width + spacing))
        heights = [top] * column_count

        total_layout_width = column_count * self.column_width + (column_count - 1) * spacing
        offset_x = left + (max_width - total_layout_width) // 2  # << 居中偏移

        for item in self._items:
            col = heights.index(min(heights))
            x = offset_x + col * (self.column_width + spacing)
            y = heights[col]

            hint = item.sizeHint()
            h = hint.height()

            item.setGeometry(QRect(QPoint(x, y),
                                   QSize(self.column_width, h)))
            heights[col] += h + spacing

        # 如果放在 scroll area，要撑开内容区高度
        parent = self.parentWidget()
        if parent:
            total_h = max(heights) + bottom
            total_w = column_count * (self.column_width + spacing) - spacing + left + right
            parent.setMinimumSize(QSize(total_w, total_h))
