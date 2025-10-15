from PySide6.QtWidgets import QScrollArea, QWidget,QLayoutItem,QApplication,QVBoxLayout
from PySide6.QtCore import QTimer,Qt
from PySide6.QtWidgets import QScrollBar
import logging

from ui.basic import WaterfallLayout
from controller import MessageBoxService

class LazyScrollArea(QScrollArea):
    def __init__(self, column_width=200,widget=None,hint=True, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                width: 0px;
                height: 0px;
            }
        """)
        self.msg=MessageBoxService(self)
        # 内容容器
        self._hint=hint

        if widget is not None:#在最上部添加一个widget
            content_widget = QWidget()
            vlayout=QVBoxLayout(content_widget)
            waterfall_widget=QWidget()
            self.waterfall_layout = WaterfallLayout(waterfall_widget,column_width=column_width)
            vlayout.setContentsMargins(0,0,0,0)
            vlayout.addWidget(widget,0, Qt.AlignLeft|Qt.AlignmentFlag.AlignTop)
            #vlayout.addWidget(widget)
            vlayout.addWidget(waterfall_widget,0,Qt.AlignmentFlag.AlignTop)
            '''
            waterfall_widget.setStyleSheet("""
    background-color: white;          /* 背景色 */
    /*border: 2px solid black;        边框宽度和颜色 */
""")     '''   
            vlayout.addStretch()
        else:
            content_widget = QWidget()
            self.waterfall_layout = WaterfallLayout(content_widget, column_width=column_width)

        self.waterfall_layout.setContentsMargins(0,5,0,0)
        self.setWidget(content_widget)


        # 分页状态
        self.page_size = 30
        self.current_page = 0
        self.reached_end = False
        self.loading = False
        self._loader_fn = None  # 外部传入的加载函数

        # 监听滚动
        self.verticalScrollBar().valueChanged.connect(self._on_scroll)


    def set_loader(self, loader_fn):
        """设置加载函数，loader_fn(page_index, page_size) -> List[QWidget]"""
        self._loader_fn = loader_fn
        self.reset()

    def reset(self):
        """清空所有内容并重置分页"""
        while self.waterfall_layout.count():
            item:QLayoutItem = self.waterfall_layout.takeAt(0)
            widget:QWidget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()  # 确保销毁，异步
        logging.info("清空所有内容并重置分页")
        self.waterfall_layout.update()

        '''
        from PySide6.QtGui import QPixmapCache
        logging.debug("清空pixmap缓存")
        QPixmapCache.clear()  # 清空 Qt 内部 pixmap 缓存
        '''
        self.current_page = 0
        self.reached_end = False
            # 重置滚动条到顶部
        self.verticalScrollBar().setValue(0)
        self._load_next_page()


    def _on_scroll(self, value):
        '''什么时候加载下一页'''
        sb: QScrollBar = self.verticalScrollBar()
        if not self.loading and not self.reached_end and value >= sb.maximum() - 300:
            self._load_next_page()
        # 如果滚动条还不能滚动（说明没铺满一屏），继续加载下一页

    def _load_next_page(self):
        if self._loader_fn is None:
            return
        self.loading = True
        # 事件循环里的延迟调用，避免阻塞UI
        self._fetch_and_append()

    def _fetch_and_append(self):
        
        widgets:list = self._loader_fn(self.current_page, self.page_size)#这里真正调用了读数据并加载UI的函数
        if not widgets :#没有新数据的情况
            #if self.current_page == 0 and self._hint:
                #self.msg.show_info("提示", "未查询到数据")
                # 第一次加载没有数据，显示提示
            self.reached_end = True      
        else:#有数据
            if len(widgets)< self.page_size:
                self.reached_end = True  
            for w in widgets:
                self.waterfall_layout.addWidget(w)
            self.current_page += 1
        #logging.debug(self.waterfall_layout._items.__len__())
        self.loading = False
    # 延迟到下一轮事件循环再检查滚动条
        if not self.reached_end:
            QTimer.singleShot(0, self._check_scrollable_and_load_next)

    def _check_scrollable_and_load_next(self):
        QApplication.processEvents()
        sb = self.verticalScrollBar()
        # 这一轮事件循环结束后，布局和滚动条已经刷新
        #logging.debug(sb.maximum())
        if sb.maximum() == 0 and not self.reached_end:
            self._load_next_page()


    def showEvent(self, event):
        super().showEvent(event)
        # 页面显示时强制刷新
        #logging.debug("显示页面")
        #self.updateGeometry()
        #self.update()  # 强制重绘
        self.waterfall_layout.invalidate()  # 告诉 layout 重新计算布局