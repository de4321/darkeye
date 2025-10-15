from PySide6.QtWidgets import (QApplication, QMainWindow, QTableView, QVBoxLayout, 
                               QHBoxLayout, QWidget, QPushButton, QAbstractItemView)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex,Signal,Slot
from core.database.query import get_actress_allname
import logging
from ui.basic import IconPushButton

class MovableTableModel(QAbstractTableModel):
    data_updated=Signal(list)
    def __init__(self, data=None):
        super().__init__()
        self._headers = []
        
        if data is None:
            self._data = []
            self._headers = []
        else:
            self._data = data
            # 如果是字典列表，获取所有可能的键作为列
            if data and isinstance(data[0], dict):
                self._headers = list(data[0].keys())
            elif data:
                self._data = [dict(enumerate(row)) for row in data]  # 将列表转换为字典
                self._headers = [str(i) for i in range(len(data[0]))]
            else:
                self._headers = []

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            row_data = self._data[index.row()]
            column_key = self._headers[index.column()]
            return row_data.get(column_key, "")
        return None

    def rowCount(self, index=QModelIndex()):
        return len(self._data)

    def columnCount(self, index=QModelIndex()):
        return len(self._headers)

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._headers[section]
            else:
                return str(section + 1)
        return None

    def flags(self, index):
        """设置单元格的标志，使其可编辑"""
        return Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def setData(self, index, value, role):
        """处理数据修改"""
        if role == Qt.ItemDataRole.EditRole:
            if 0 <= index.row() < len(self._data) and 0 <= index.column() < len(self._headers):
                # 获取对应的列键
                column_key = self._headers[index.column()]
                # 如果值为空或None，将其替换为空字符串
                if value is None or value == "":
                    self._data[index.row()][column_key] = ""
                else:
                    self._data[index.row()][column_key] = value
                # 发出数据更改信号
                self.dataChanged.emit(index, index)
                logging.debug("发射修改model信号")
                self.data_updated.emit(self._data)#发出信号
                logging.debug(self._data)
                return True
        return False

    def moveRow(self, sourceRow, destinationRow):
        """移动行数据"""
        if sourceRow == destinationRow:
            return False
        
        if 0 <= sourceRow < len(self._data) and 0 <= destinationRow < len(self._data):
            # 移动数据
            row_data = self._data.pop(sourceRow)
            self._data.insert(destinationRow, row_data)
            
            # 通知视图更新
            self.layoutChanged.emit()
            self.data_updated.emit(self._data)#发出数据改变信号
            return True
        return False

    def addRow(self):
        """添加新行"""
        # 创建一个空字典，包含所有列但值为空
        new_row = {key: "" for key in self._headers}
        # 开始插入行
        self.beginInsertRows(QModelIndex(), len(self._data), len(self._data))
        self._data.append(new_row)
        self.endInsertRows()
        self.data_updated.emit(self._data)#发出数据改变信号
        return True

    def removeRow(self, row, parent=QModelIndex()):
        """删除指定行"""
        if 0 <= row < len(self._data):
            self.beginRemoveRows(parent, row, row)
            self._data.pop(row)
            self.endRemoveRows()
            self.data_updated.emit(self._data)#发出信号
            return True
        return False

    def setNewData(self, data):
        """更新整个数据集"""
        self.beginResetModel()
        
        self._data = data
        logging.debug(data)
        if data:
            if isinstance(data[0], dict):
                self._headers = list(data[0].keys())
            else:
                self._data = [dict(enumerate(row)) for row in data]
                self._headers = [str(i) for i in range(len(data[0]))]
        else:
            self._headers = []
        logging.debug("首次更新数据")
        logging.debug(self._headers)
        self.endResetModel()


class EditableTableView(QWidget):
    def __init__(self):
        super().__init__()
        self._actress_id=None

        # 创建模型和视图
        self.model = MovableTableModel()
        self.tableView = QTableView()
        self.tableView.setModel(self.model)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        # 设置编辑触发方式
        self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked |
                                     QAbstractItemView.EditTrigger.EditKeyPressed |
                                     QAbstractItemView.EditTrigger.AnyKeyPressed)

        # 创建按钮
        self.setup_buttons()
        
        # 设置布局

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addLayout(self.button_layout)
        main_layout.addWidget(self.tableView)
        

    def setup_buttons(self):
        """创建按钮"""
        #self.btn_up = IconPushButton("triangle-up.png")
        #self.btn_down = IconPushButton("triangle-down.png")
        self.btn_add = IconPushButton("list-plus.png")
        self.btn_delete = IconPushButton("list-x.png")
        #self.btn_refresh = QPushButton("刷新")
        #self.btn_save = QPushButton("保存")
        #self.btn_print = QPushButton("打印数据")
        
        
        #self.btn_up.clicked.connect(self.move_up)
        #self.btn_down.clicked.connect(self.move_down)
        self.btn_add.clicked.connect(self.add_row)
        self.btn_delete.clicked.connect(self.delete_row)
        #self.btn_refresh.clicked.connect(self.refresh_data)
        #self.btn_save.clicked.connect(self.save_data)
        #self.btn_print.clicked.connect(self.print_data)

        # 初始状态
#        self.btn_up.setEnabled(False)
#        self.btn_down.setEnabled(False)
        self.btn_delete.setEnabled(False)  # 只有选中行时才能删除

        # 按钮布局
        self.button_layout = QHBoxLayout()
#        self.button_layout.addWidget(self.btn_up)
#        self.button_layout.addWidget(self.btn_down)
        self.button_layout.addWidget(self.btn_add)
        self.button_layout.addWidget(self.btn_delete)
        #self.button_layout.addWidget(self.btn_refresh)
        #self.button_layout.addWidget(self.btn_save)
        #self.button_layout.addWidget(self.btn_print)
        self.button_layout.addStretch()

                # 连接信号
        self.tableView.selectionModel().selectionChanged.connect(self.update_button_state)
        self.update_button_state()

    def add_row(self):
        """添加新行"""
        self.model.addRow()
        # 选中新添加的行
        last_row = self.model.rowCount() - 1
        self.tableView.selectRow(last_row)
        # 滚动到新行
        self.tableView.scrollToBottom()

    def delete_row(self):
        """删除当前选中的行"""
        current_index = self.tableView.currentIndex()
        if current_index.isValid():
            row = current_index.row()
            self.model.removeRow(row)
            # 更新按钮状态
            self.update_button_state()

    def print_data(self):
        """打印当前模型中的所有数据"""
        print("\n当前表格数据:")
        print("-" * 50)
        # 打印每一行数据
        print(self.model._headers)
        for row in self.model._data:
            print(row)
        
        print("-" * 50)

    def update_button_state(self):
        """更新按钮状态"""
        current_index = self.tableView.currentIndex()
        if current_index.isValid():
            current_row = current_index.row()
            #self.btn_up.setEnabled(current_row > 0)
            #self.btn_down.setEnabled(current_row < self.model.rowCount() - 1)
            self.btn_delete.setEnabled(True)  # 有选中行时可以删除
        else:
            #self.btn_up.setEnabled(False)
            #self.btn_down.setEnabled(False)
            self.btn_delete.setEnabled(False)


    
    def update(self,actress_id):
        '''更新数据并刷新'''
        self._actress_id=actress_id

    @Slot(list)
    def updatedata(self,alias_tag:list[dict]):
        #logging.debug(actress_name)#这里字典的顺序会发生变化
        from utils.utils import sort_dict_list_by_keys
        order=['tag_id','tag_name','redirect_tag_id']
        alias_tag=sort_dict_list_by_keys(alias_tag,order)
        
        self.model.setNewData(alias_tag)
        self.tableView.setColumnHidden(0, True)
        self.tableView.setColumnHidden(2, True)

        #for i in range(6):
        #    self.tableView.setColumnWidth(i,125)


