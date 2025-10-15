
from PySide6.QtCore import Qt, QPoint, QRect, QSize,QRect
from PySide6.QtWidgets import QLayout


class FlowLayout(QLayout):
    '''流式布局，从左往右横向填充，不够了换行，适合内部widget高度相同的时候使用'''
    def __init__(self, parent=None, margin=0, spacing=10):
        super().__init__(parent)
        self.setSpacing(spacing)
        self.itemList = []
        self.setContentsMargins(margin, margin, margin, margin)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size
    
    def removeWidget(self, widget):
        """完全移除 widget 并清理布局项"""
        for i in reversed(range(len(self.itemList))):
            item = self.itemList[i]
            if item.widget() == widget:
                self.takeAt(i)
                item.widget().setParent(None)  # 解除父级关联
                del item  # 释放内存
                break

    def relayout(self):
        parent = self.parentWidget()
        if parent:
            self.setGeometry(self.geometry())  # 强制触发 _do_layout()
            parent.update()
            parent.repaint()

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        spaceX = self.spacing()
        spaceY = self.spacing()
        for item in self.itemList:
            #这几行代码如果要用需要在使用的时候.show()以及relayout()手动刷新，否则就是会有问题。需要动态隐藏部分控件（如搜索过滤）
            #widget = item.widget()
            #if widget is None or not widget.isVisible():
            #    continue

            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()
