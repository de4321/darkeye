#测试QSqlRelationalTableModel+QTableView的例子
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#---------------------------------------------------------------------------------------------------
from PySide6.QtWidgets import (
    QApplication, QTableView, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QMessageBox,QAbstractItemView,QDataWidgetMapper,QFormLayout,QLineEdit,QComboBox,QLabel
)
from PySide6.QtSql import QSqlDatabase,QSqlRelation,QSqlRelationalTableModel,QSqlRelationalDelegate,QSqlQueryModel
from PySide6.QtCore import Qt,Slot
import sys
from config import DATABASE
from ui.basic import ModelSearch

def create_connection():
    """建立数据库连接"""
    db = QSqlDatabase.addDatabase("QSQLITE")#这个是默认的连接
    db.setDatabaseName(str(DATABASE))
    if not db.open():
        QMessageBox.critical(None, "数据库错误", "无法打开数据库")
        return False
    return True


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QSqlRelationalTableModel + QTableView 增删改查")

        # 模型
        self.model = QSqlRelationalTableModel(self)
        self.model.setTable("prefix_maker_relation")  # 绑定表
        self.model.setEditStrategy(QSqlRelationalTableModel.OnManualSubmit)  # 手动提交
        

        # 设置关系字段
        studio_idx = self.model.fieldIndex("maker_id")#这个表中的这个是外键
        self.model.setRelation(studio_idx,QSqlRelation("maker","maker_id","cn_name"))
        self.model.select()

        # 设置表头
        self.model.setHeaderData(0, Qt.Horizontal, "ID")
        self.model.setHeaderData(1, Qt.Horizontal, "番号前缀")
        self.model.setHeaderData(2, Qt.Horizontal, "制作商")


        # 视图
        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setSelectionMode(QAbstractItemView.SingleSelection)#只能选一个
        self.view.setSelectionBehavior(QTableView.SelectRows)
        self.view.setColumnHidden(0, True)  # 隐藏 ID 列（主键）
        self.view.setItemDelegate(QSqlRelationalDelegate(self.view))#这样会产生下拉框


        # 按钮
        self.btn_add = QPushButton("新增行")
        self.btn_delete = QPushButton("删除行")
        self.btn_save = QPushButton("保存修改")
        self.btn_revert = QPushButton("撤销修改")
        self.btn_refresh=QPushButton("刷新数据")

        # 信号连接
        self.btn_add.clicked.connect(self.add_row)
        self.btn_delete.clicked.connect(self.delete_row)
        self.btn_save.clicked.connect(self.save_changes)
        self.btn_revert.clicked.connect(self.revert_changes)

        # 布局
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_add)
        button_layout.addWidget(self.btn_delete)
        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_revert)
        button_layout.addWidget(self.btn_refresh)



        self.serial_number=QLineEdit()
        self.studio=QComboBox()

        # 设置组合框的关系模型（外键关联）
        self.studio.setModel(self.model.relationModel(studio_idx))
        self.studio.setModelColumn(self.model.relationModel(studio_idx).fieldIndex("cn_name"))

        # 创建数据窗口映射器
        mapper = QDataWidgetMapper(self)
        mapper.setModel(self.model)
        mapper.setItemDelegate(QSqlRelationalDelegate(self.view))
        mapper.addMapping(self.serial_number, self.model.fieldIndex("prefix"))
        mapper.addMapping(self.studio, studio_idx)


        selection_model = self.view.selectionModel()
        selection_model.currentRowChanged.connect(mapper.setCurrentModelIndex)

        formlayout=QFormLayout()
        formlayout.addRow("番号前缀",self.serial_number)
        formlayout.addRow("制作商",self.studio)

        self.btn_refresh.clicked.connect(self.refresh_data)

        searchWidget=ModelSearch(self,self.model,self.view)
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        layout.addWidget(searchWidget)
        layout.addLayout(button_layout)
        layout.addLayout(formlayout)


    def add_row(self):
        """新增一行"""
        row = self.model.rowCount()
        self.model.insertRow(row)
        # 可选：初始化部分字段
        self.model.setData(self.model.index(row, 1), "新番号前缀")
        self.model.setData(self.model.index(row, 2), "1")#默认的番号
        self.view.selectRow(row)
        # 滚动到最后一行
        self.view.scrollToBottom()  # 滚动到底

    def delete_row(self):
        """删除选中的行"""
        selected = self.view.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "提示", "请先选择要删除的行")
            return
        for index in selected:
            self.model.removeRow(index.row())

    def save_changes(self):
        """保存修改到数据库"""
        if not self.model.submitAll():
            QMessageBox.critical(self, "错误", f"保存失败: {self.model.lastError().text()}")
        else:
            self.model.select()  # 刷新
            QMessageBox.information(self, "提示", "保存成功")

    def revert_changes(self):
        """撤销未保存的修改"""
        self.model.revertAll()
        QMessageBox.information(self, "提示", "已撤销修改")

    def refresh_data(self):
        """简单的刷新方法"""
        self.model.select()
        self.view.setModel(self.model)
        print("数据已刷新")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    if not create_connection():
        sys.exit(-1)
    w = Window()
    w.show()
    sys.exit(app.exec())
