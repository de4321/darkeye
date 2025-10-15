from PySide6.QtWidgets import QTableView, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox,QAbstractItemView,QDataWidgetMapper,QFormLayout,QLineEdit,QComboBox,QLabel,QFileDialog
from PySide6.QtCore import Slot,Qt
from PySide6.QtSql import QSqlRelation,QSqlRelationalTableModel,QSqlRelationalDelegate,QSqlQueryModel,QSqlQuery,QSqlDatabase
import logging


from config import BASE_DIR,DATABASE,INI_FILE
from ui.basic import ModelSearch
from ui.base import LazyWidget
from controller import MessageBoxService



class RecycleBinPage(LazyWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.msg=MessageBoxService(self)


    def _lazy_load(self):
        logging.info("----------作品回收站页面----------")
        self.init_ui()

        self.signal_connect()

        self.config()

    def config(self):
        '''配置model与view'''
        # 获取数据库连接
        db_public = QSqlDatabase.database("public")
        if not db_public.isValid():
            self.msg.show_critical("错误", "无法获取数据库连接")
            return

        # 创建模型
        self.model = QSqlQueryModel(self)

        # 创建带有数据库连接的查询
        query_sql = "SELECT * FROM work WHERE is_deleted=1"
        self.query = QSqlQuery(db_public)  # 使用指定的数据库连接
        self.query.prepare(query_sql)
        
        # 执行查询并设置到模型
        if not self.query.exec():
            self.msg.show_critical("查询错误", f"执行查询失败: {self.query.lastError().text()}")
            return
            
        self.model.setQuery(self.query)

        # 设置表头
        self.model.setHeaderData(0, Qt.Horizontal, "ID")

        # 视图设置
        self.view.setModel(self.model)
        self.view.setColumnHidden(0, True)  # 隐藏 ID 列（主键）
        self.view.setSelectionBehavior(QAbstractItemView.SelectRows)  # 整行选择

        self.searchWidget.set_model_view(self.model,self.view)#搜索框连接功能

    def init_ui(self):
        self.view = QTableView()
        # 按钮
        self.btn_refresh=QPushButton("刷新数据")
        self.btn_delete=QPushButton("彻底删除")
        self.btn_restore=QPushButton("恢复数据")


        # 布局
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_refresh)
        button_layout.addWidget(self.btn_delete)
        button_layout.addWidget(self.btn_restore)


        self.serial_number=QLineEdit()
        self.studio=QComboBox()

        self.searchWidget=ModelSearch()

        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        layout.addWidget(self.searchWidget)
        layout.addLayout(button_layout)
        
    def signal_connect(self):
        # 信号连接
        self.btn_refresh.clicked.connect(self.refresh_data)
        self.btn_delete.clicked.connect(self.delete)
        self.btn_restore.clicked.connect(self.recover)

    @Slot()
    def refresh_data(self):
        """刷新数据方法"""
        if not self.query.exec():
            self.msg.show_critical("查询错误", f"刷新数据失败: {self.query.lastError().text()}")
            return
            
        self.model.setQuery(self.query)
        self.view.setModel(self.model)
        logging.info("数据已刷新")



    @Slot()
    def delete(self):
        """彻底删除数据"""
        selected_indexes = self.view.selectionModel().selectedRows()
        if not selected_indexes:
            self.msg.show_warning("警告", "请先选择要删除的行")
            return

        if not self.msg.ask_yes_no("确认删除", f"确定要彻底删除选中的 {len(selected_indexes)} 行吗？此操作不可撤销。"):
            return

        from core.database.delete import delete_work
        for index in selected_indexes:
            work_id = self.model.data(self.model.index(index.row(), 0))
            if not delete_work(work_id):
                self.msg.show_critical("错误", f"删除失败:")
                return
        self.refresh_data()
        self.msg.show_info("成功", f"已删除 {len(selected_indexes)} 行数据")

    @Slot()
    def recover(self):
        '''恢复数据'''
        selected_indexes = self.view.selectionModel().selectedRows()
        if not selected_indexes:
            self.msg.show_critical("警告", "请先选择要恢复的行")
            return
        if not self.msg.ask_yes_no("确认恢复", f"确定要恢复选中的 {len(selected_indexes)} 行吗？"):
            return
        from core.database.update import mark_undelete
        for index in selected_indexes:
            work_id = self.model.data(self.model.index(index.row(), 0))
            if not mark_undelete(work_id):
                self.msg.show_critical("错误", f"恢复失败: {self.query.lastError().text()}")
                return
        # 更新模型，刷新界面
        self.refresh_data()
        self.msg.show_info("成功", f"已恢复 {len(selected_indexes)} 行数据")