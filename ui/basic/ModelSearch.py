#专门给 Model 和QTableView 用的搜索器
from PySide6.QtWidgets import QTableView, QPushButton,QWidget,QHBoxLayout,QMessageBox,QLineEdit,QLabel
from PySide6.QtSql import QSqlRelationalTableModel
from PySide6.QtCore import Qt,Slot,QSize,Signal
from PySide6.QtGui import QIcon,QKeyEvent
from config import ICONS_PATH
from ui.basic.IconPushButton import IconPushButton


class MyLineEdit(QLineEdit):
    # 自定义信号
    shiftReturnPressed = Signal()
    returnPressedEx = Signal()  # 和普通 Enter 区分开的版本

    def keyPressEvent(self, event:QKeyEvent):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):  # 捕获回车键
            if event.modifiers() == Qt.ShiftModifier:
                self.shiftReturnPressed.emit()  # 触发 Shift+Enter 信号
                event.accept()     # 阻止继续冒泡,这个好像没有什么用
            elif event.modifiers() == Qt.NoModifier:
                self.returnPressedEx.emit()     # 触发普通 Enter 信号
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

class ModelSearch(QWidget):
    def __init__(self, parent=None,model:QSqlRelationalTableModel=None,view:QTableView=None):
        super().__init__(parent)
        self.model=model
        self.view=view
        self.init_ui()
        self.signal_connect()
        self.search_results=[]

    def init_ui(self):
        searchlayout=QHBoxLayout(self)
        self.search_input=MyLineEdit()
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setFixedWidth(200)
        self.search_input.setPlaceholderText("搜索")

        self.btn_prev=IconPushButton("arrow-up.png")
        self.btn_prev.setWhatsThis("向前搜索")
        self.btn_prev.setToolTip("向前搜索(Shift+Enter)")

        self.btn_next=IconPushButton("arrow-down.png")
        self.btn_next.setWhatsThis("向后搜索")
        self.btn_next.setToolTip("向后搜索(Enter)")

        self.btn_prev.setEnabled(False)
        self.btn_next.setEnabled(False)

        self.result_label = QLabel("无搜索结果")
        self.result_label.setFixedWidth(70)

        searchlayout.addWidget(self.search_input)
        searchlayout.addWidget(self.result_label)
        searchlayout.addWidget(self.btn_prev)
        searchlayout.addWidget(self.btn_next)
        searchlayout.addStretch()

        
    def signal_connect(self):
        self.btn_prev.clicked.connect(self.search_previous)
        self.btn_next.clicked.connect(self.search_next)
        self.search_input.textChanged.connect(self.perform_search)
        self.search_input.shiftReturnPressed.connect(self.search_previous)
        self.search_input.returnPressedEx.connect(self.search_next)

    @Slot()
    def perform_search(self):
        """执行搜索操作"""
        search_text = self.search_input.text().strip().lower()
        
        self.search_results=[]
        self.search_results.clear()
        if not search_text:
            #QMessageBox.information(self, "提示", "请输入搜索关键词")
            self.result_label.setText("无搜索结果")
            self.btn_prev.setEnabled(False)
            self.btn_next.setEnabled(False)
            return

        self.current_search_index = -1
        
        # 在所有列中搜索
        for row in range(self.model.rowCount()):
            for column in range(self.model.columnCount()):
                index = self.model.index(row, column)
                cell_data = self.model.data(index, Qt.DisplayRole)
                if cell_data and search_text in str(cell_data).lower():
                    self.search_results.append((row, column))
                    break  # 避免同一行重复添加
        
        if self.search_results:
            self.result_label.setText(f"找到 {len(self.search_results)} 个结果")
            self.btn_next.setEnabled(True)
            self.btn_prev.setEnabled(True)
            self.search_next()  # 自动定位到第一个结果
        else:
            self.result_label.setText("无搜索结果")
            self.btn_next.setEnabled(False)
            self.btn_prev.setEnabled(False)
            self.result_label.setText("无匹配结果")
            #QMessageBox.information(self, "搜索结果", "未找到匹配项")

    @Slot()
    def search_next(self):
        """定位到下一个搜索结果"""
        if not self.search_results:
            return
            
        self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
        self.navigate_to_search_result()

    @Slot()
    def search_previous(self):
        """定位到上一个搜索结果"""
        if not self.search_results:
            return
            
        self.current_search_index = (self.current_search_index - 1) % len(self.search_results)
        self.navigate_to_search_result()

    def navigate_to_search_result(self):
        """导航到当前搜索结果"""
        if not self.search_results or self.current_search_index < 0:
            return
            
        row, column = self.search_results[self.current_search_index]
        
        # 选择整行
        self.view.selectRow(row)
        
        # 滚动到可见区域
        self.view.scrollTo(self.model.index(row, 0), QTableView.PositionAtCenter)
        
        # 更新结果标签
        self.result_label.setText(f"结果 {self.current_search_index + 1}/{len(self.search_results)}")


    def set_model_view(self, model: QSqlRelationalTableModel, view: QTableView):
        self.model = model
        self.view = view

        '''
        # 设置父控件为 view 的父窗口，这样它可以覆盖在 view 上
        self.setParent(view.parentWidget())
        
        # 设置为无边框浮动小部件
        self.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint)
        
        # 将搜索框移动到 view 的右上角
        geo = view.geometry()  # 获取 view 在父控件中的几何位置
        x = geo.x() + geo.width() - self.width() - 10  # 右上角，留 10px 边距
        y = geo.y() + 10  # 上方 10px 边距
        self.move(x, y)
        
        self.show()
        '''