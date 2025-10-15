from PySide6.QtWidgets import QTableView, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox,QAbstractItemView,QDataWidgetMapper,QFormLayout,QLineEdit,QComboBox,QLabel,QSplitter
from PySide6.QtCore import Slot,Qt
from PySide6.QtSql import QSqlRelation,QSqlRelationalTableModel,QSqlRelationalDelegate,QSqlQueryModel,QSqlTableModel,QSqlDatabase
import logging

from config import BASE_DIR,DATABASE,INI_FILE
from ui.basic import ModelSearch
from ui.base import LazyWidget

class StudioManagementPage(LazyWidget):
    #StudioManagementPage
    def __init__(self):
        super().__init__()

    def _lazy_load(self):
        logging.info("----------制作商管理页面----------")
        self.init_ui()

        self.signal_connect()

        self.config()

        self.current_active_view=self.view1#默认选择

    def config(self):
        '''配置model与view'''
        # 模型
        db_public = QSqlDatabase.database("public")
        self.model1 = QSqlRelationalTableModel(self,db_public)
        self.model1.setTable("prefix_maker_relation")  # 绑定表
        self.model1.setEditStrategy(QSqlRelationalTableModel.OnManualSubmit)  # 手动提交

        # 设置关系字段
        studio_idx = self.model1.fieldIndex("maker_id")#这个表中的这个是外键

        self.model1.setRelation(studio_idx,QSqlRelation("maker","maker_id","cn_name"))
        self.model1.select()#这个后就会锁库
        self.model1.submitAll()
        # 设置表头
        self.model1.setHeaderData(0, Qt.Horizontal, "ID")
        self.model1.setHeaderData(1, Qt.Horizontal, "番号前缀")
        self.model1.setHeaderData(2, Qt.Horizontal, "制作商")

        # 视图设置
        self.view1.setModel(self.model1)
        self.view1.setSelectionMode(QAbstractItemView.SingleSelection)#只能选一个
        self.view1.setSelectionBehavior(QTableView.SelectRows)
        self.view1.setColumnHidden(0, True)  # 隐藏 ID 列（主键）
        self.view1.setItemDelegate(QSqlRelationalDelegate(self.view1))#这样会产生下拉框

        # 设置组合框的关系模型（外键关联）
        self.studio.setModel(self.model1.relationModel(studio_idx))
        self.studio.setModelColumn(self.model1.relationModel(studio_idx).fieldIndex("cn_name"))

        # 创建数据窗口映射器
        self.mapper1 = QDataWidgetMapper(self)
        self.mapper1.setModel(self.model1)
        self.mapper1.setItemDelegate(QSqlRelationalDelegate(self.view1))
        self.mapper1.addMapping(self.serial_number, self.model1.fieldIndex("prefix"))
        self.mapper1.addMapping(self.studio, studio_idx)

        selection_model1 = self.view1.selectionModel()
        selection_model1.currentRowChanged.connect(self.mapper1.setCurrentModelIndex)#模型映射


        # 配置表2
        self.model2 = QSqlTableModel(self,db_public)
        self.model2.setTable("maker")  # 绑定表
        self.model2.setEditStrategy(QSqlRelationalTableModel.OnManualSubmit)  # 手动提交

        # 设置关系字段
        self.model2.select()
        self.model2.submitAll()
        # 设置表头
        self.model2.setHeaderData(0, Qt.Horizontal, "ID")
        self.model2.setHeaderData(1, Qt.Horizontal, "中文名")
        self.model2.setHeaderData(2, Qt.Horizontal, "日文名")
        self.model2.setHeaderData(3, Qt.Horizontal, "别名")

        # 视图设置
        self.view2.setModel(self.model2)
        self.view2.setSelectionMode(QAbstractItemView.SingleSelection)#只能选一个
        self.view2.setSelectionBehavior(QTableView.SelectRows)
        self.view2.setColumnHidden(0, True)  # 隐藏 ID 列（主键）

        self.mapper2 = QDataWidgetMapper(self)
        self.mapper2.setModel(self.model2)
        self.mapper2.addMapping(self.cn_name, self.model2.fieldIndex("cn_name"))
        self.mapper2.addMapping(self.jp_name, self.model2.fieldIndex("jp_name"))
        self.mapper2.addMapping(self.alias, self.model2.fieldIndex("aliases"))

        selection_model2 = self.view2.selectionModel()
        selection_model2.currentRowChanged.connect(self.mapper2.setCurrentModelIndex)#模型映射

        self.searchWidget.set_model_view(self.model1,self.view1)#搜索框连接功能

        # 安装事件过滤器
        self.view1.installEventFilter(self)
        self.view2.installEventFilter(self)

    def init_ui(self):
        self.view1 = QTableView()
        self.view2 =QTableView()

        self.status_label=QLabel("")
        # 表格区域 - 使用分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.view1)
        splitter.addWidget(self.view2)
        splitter.setMinimumHeight(400)

        # 按钮
        self.btn_add = QPushButton("新增行")
        self.btn_delete = QPushButton("删除行")
        self.btn_save = QPushButton("保存修改")
        self.btn_revert = QPushButton("撤销修改")
        self.btn_refresh=QPushButton("读数据库数据")

        # 布局
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_add)
        button_layout.addWidget(self.btn_delete)
        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_revert)
        button_layout.addWidget(self.btn_refresh)
        button_layout.addWidget(self.status_label)

        self.serial_number=QLineEdit()
        self.studio=QComboBox()

        formlayout1=QFormLayout()
        formlayout1.addRow("番号前缀",self.serial_number)
        formlayout1.addRow("制作商",self.studio)

        self.cn_name=QLineEdit()
        self.jp_name=QLineEdit()
        self.alias=QLineEdit()
        formlayout2=QFormLayout()
        formlayout2.addRow("中文名",self.cn_name)
        formlayout2.addRow("日文名",self.jp_name)
        formlayout2.addRow("别名",self.alias)

        self.searchWidget=ModelSearch()
        hlayout=QHBoxLayout()
        hlayout.addLayout(formlayout1)
        hlayout.addLayout(formlayout2)

        layout = QVBoxLayout(self)
        layout.addWidget(splitter)
        layout.addWidget(self.searchWidget)
        layout.addLayout(button_layout)
        layout.addLayout(hlayout)

    def signal_connect(self):
        # 信号连接
        self.btn_add.clicked.connect(self.add_row)
        self.btn_delete.clicked.connect(self.delete_row)
        self.btn_save.clicked.connect(self.save_changes)
        self.btn_revert.clicked.connect(self.revert_changes)
        self.btn_refresh.clicked.connect(self.refresh_data)


    def eventFilter(self, obj, event):
        """事件过滤器，用于跟踪焦点变化"""
        if event.type() == event.Type.FocusIn:
            if obj in [self.view1, self.view2]:
                self.set_active_view(obj)
        return super().eventFilter(obj, event)

    def set_active_view(self, view:QTableView):
        """设置当前活动视图"""
        self.current_active_view = view
        view_name = "前缀表格" if view == self.view1 else "制作商表"
        self.status_label.setText(f"当前焦点: {view_name}")
        
        # 可选：高亮当前活动视图
        self.view1.setStyleSheet("")
        self.view2.setStyleSheet("")
        #view.setStyleSheet("border: 2px solid blue;")
        view.setStyleSheet("""
        QTableView{
            border: 2px solid orange;
        }
        """)
        model,view=self.get_current_model_and_view()
        self.searchWidget.set_model_view(model,view)


    def get_current_model_and_view(self):
        """获取当前活动的模型和视图"""
        if self.current_active_view == self.view1:
            return self.model1, self.view1
        elif self.current_active_view == self.view2:
            return self.model2, self.view2
        return None, None


    @Slot()
    def add_row(self):
        """新增一行"""
        model, view = self.get_current_model_and_view()
        if view==self.view1:
            default=["番号前缀",1]
        else:
            default=[]
        if model and view:
            row = model.rowCount()
            model.insertRow(row)
            # 可选：初始化部分字段
            for i, value in enumerate(default):
                model.setData(model.index(row, i+1), value)
            view.selectRow(row)
            # 滚动到最后一行
            view.scrollToBottom()  # 滚动到底

    @Slot()
    def delete_row(self):
        """删除选中的行"""
        model, view = self.get_current_model_and_view()
        if model and view:
            selected = view.selectionModel().selectedRows()
            if not selected:
                QMessageBox.warning(self, "提示", "请先选择要删除的行")
                return
            for index in selected:
                model.removeRow(index.row())

    @Slot()
    def save_changes(self):
        """保存修改到数据库,这个要改成sqlite3写"""
        model, view = self.get_current_model_and_view()
        if model and view:
            if not model.submitAll():
                QMessageBox.critical(self, "错误", f"保存失败: {model.lastError().text()}")
            else:
                QMessageBox.information(self, "提示", "保存成功")
                from controller.GlobalSignalBus import global_signals
                global_signals.work_data_changed.emit()#发信号让

    @Slot()
    def revert_changes(self):
        """撤销未保存的修改"""
        model, view = self.get_current_model_and_view()
        if model and view:
            model.revertAll()
            QMessageBox.information(self, "提示", "已撤销修改")

    @Slot()
    def refresh_data(self):
        """简单的刷新方法"""
        """刷新方法"""

        self.model1.select()
        self.model2.select()
        # 刷新 relationModel（关键一步）
        #studio_idx = self.model1.fieldIndex("maker_id")#这个找不到index
        #relation_model=self.model1.relationModel(studio_idx)

        relation_model=self.model1.relationModel(2)#这样手工弄列就有用了,这个以后要改

        if relation_model:
            relation_model.select()
            self.studio.setModel(relation_model)
            self.studio.setModelColumn(relation_model.fieldIndex("cn_name"))
            logging.debug("刷新")

        # 保持 mapper 正常
                # 刷新 model1, model2

        self.mapper1.toFirst()
        self.mapper2.toFirst()

        logging.info("数据已刷新，关联下拉框已更新")
