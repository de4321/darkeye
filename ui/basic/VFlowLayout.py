
from PySide6.QtCore import Qt, QPoint, QRect, QSize,QRect
from PySide6.QtWidgets import QLayout,QLayoutItem
import logging

class VFlowLayout(QLayout):
    '''流式布局，从上往下竖向填充，不够了向左换行，适合内部widget宽度相同的时候使用'''
    def __init__(self, parent=None, margin=0, spacing=10):
        super().__init__(parent)
        self.setSpacing(spacing)
        self.itemList:list[QLayoutItem]= []
        self.setContentsMargins(margin, margin, margin, margin)

    #---基本接口---
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
        '''告诉 Qt 你的布局是否会扩展（水平/垂直）'''
        return Qt.Horizontal

    #---关键---
    def hasHeightForWidth(self):
        '''有高度后计算宽度'''
        return False  # 关闭这个

    def hasWidthForHeight(self):
        '''宽度依赖高度，或者说是有高度后计算宽度'''
        return True   

    def widthForHeight(self, height: int) -> int:
        '''给定height计算宽度，只有当使用layout的qwidget使用setfixedHight时会调用'''
        calc_width=self.doLayout(QRect(0, 0, 0, height), testOnly=True)
        #logging.debug(calc_width)
        return calc_width


    def setGeometry(self, rect:QRect):
        '''布局的核心，决定每个子项在父 widget 里的位置和大小'''
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        '''理想大小的尺寸估计'''
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        """布局的最小尺寸，如果高度固定，会由 widthForHeight 计算宽度"""
        margins = self.contentsMargins()
        #找最高的子项
        maxItemHeight=0
        for item in self.itemList:
            itemHeight = item.sizeHint().height()
            maxItemHeight=max(maxItemHeight,itemHeight)
        
        parent = self.parentWidget()
        if parent is not None and parent.height() > 0:
            height = parent.height()  # 已固定的高度
        else:
            height=100

        # 根据高度计算宽度
        width = self.widthForHeight(height)
        return QSize(width,maxItemHeight+margins.bottom()+margins.top())
    

    
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

    def doLayout(self, rect:QRect, testOnly:bool):
        '''这个是个非常好的方法，包括虚拟排列，可复用在计算尺寸的时候'''
        # 从最右边开始布局
        margins = self.contentsMargins()
        x = rect.right() - margins.right()  # 右边起点减去右边距
        y = rect.y() + margins.top()       # 顶部边距
        columnWidth = 0
        spaceX = self.spacing()
        spaceY = self.spacing()
        lastColumnWidth=0 #最后一列最大宽度的子项目的列宽

        for item in self.itemList:
            itemSize = item.sizeHint()
            nextY = y + itemSize.height() + spaceY

            # 超出底部，高度不够则换列
            if nextY - spaceY > rect.bottom() - margins.bottom() and columnWidth > 0:
                y = rect.y() + margins.top()
                x = x - (columnWidth + spaceX)
                nextY = y + itemSize.height() + spaceY
                columnWidth = 0
                lastColumnWidth=itemSize.width()

            if not testOnly:
                item.setGeometry(QRect(QPoint(x - itemSize.width(), y), itemSize))

            y = nextY
            lastColumnWidth=max(lastColumnWidth,itemSize.width())
            columnWidth = max(columnWidth, itemSize.width())

        totalWidth = rect.right() - x + margins.left()+lastColumnWidth # 带margin的总宽度
        return totalWidth