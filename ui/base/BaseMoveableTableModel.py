from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from typing import List, Dict, Any
import logging

class BaseMoveableTableModel(QAbstractTableModel):
    """通用表格模型，支持加载/保存/移动/增删"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._headers = []
        self._data = []

    # ========== 必须实现 ==========
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
                #self.data_updated.emit(self._data)#发出信号
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
            #self.data_updated.emit(self._data)#发出数据改变信号
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
        #self.data_updated.emit(self._data)#发出数据改变信号
        return True

    def removeRow(self, row, parent=QModelIndex()):
        """删除指定行"""
        if 0 <= row < len(self._data):
            self.beginRemoveRows(parent, row, row)
            self._data.pop(row)
            self.endRemoveRows()
            #self.data_updated.emit(self._data)#发出信号
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


    # ========== 抽象方法 ==========
    def loadData(self, *args, **kwargs):
        """子类实现：从数据库/API/文件加载数据"""
        raise NotImplementedError

    def saveData(self, *args, **kwargs):
        """子类实现：保存到数据库/API/文件"""
        raise NotImplementedError
