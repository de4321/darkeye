from PySide6.QtWidgets import QPushButton, QHBoxLayout, QWidget, QLabel,QVBoxLayout,QLineEdit,QListView
from PySide6.QtGui import QStandardItemModel,QStandardItem
from PySide6.QtCore import Qt,QItemSelection,Signal,Slot
import sqlite3,logging

from config import DATABASE
from controller import MessageBoxService
from ui.basic import IconPushButton

class ActressSelector(QWidget):
    selection_changed=Signal()#下方被选择的列表改变了
    #弹出添加作品的窗口
    
    def __init__(self):
        super().__init__()
        self.setFixedWidth(170)
        # 主要逻辑是实例化后的Item移来移去
        # 数据初始化
        self.choose_actress_all_items = self.load_actress_from_db()
        self.choose_actress_items = list(self.choose_actress_all_items)
        self.receive_actress_items = []
        self.msg=MessageBoxService(self)

        # 模型初始化
        self.receive_actress_model = QStandardItemModel()
        self.choose_actress_model = QStandardItemModel()

        self.update_model(self.choose_actress_model, self.choose_actress_items)
        self.update_model(self.receive_actress_model, self.receive_actress_items)

        # 右侧搜索框和视图和按钮

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜索中文名或日文名")
        self.search_box.setClearButtonEnabled(True)
        self.search_box.textChanged.connect(self.filter_choose_actress_items)

        self.choose_actress_view = QListView()
        self.choose_actress_view.setModel(self.choose_actress_model)

        self.label_actress=QLabel("参演女优")
        self.label_actress.setAlignment(Qt.AlignCenter)

        self.receive_actress_view = QListView()
        self.receive_actress_view.setModel(self.receive_actress_model)
        
        # 连接选中信号
        self.receive_actress_view.selectionModel().selectionChanged.connect(
            lambda selected, _: self.clear_other_selection(self.choose_actress_view, selected)
        )
        self.choose_actress_view.selectionModel().selectionChanged.connect(
            lambda selected, _: self.clear_other_selection(self.receive_actress_view, selected)
        )

        # 按钮
        self.btn_to_left = IconPushButton("arrow-down.png")
        self.btn_to_left.setToolTip("选择参演女优")
        self.btn_to_right = IconPushButton("arrow-up.png")
        self.btn_to_right.setToolTip("移除参演女优")
        self.btn_add_actress=IconPushButton("circle-plus.png")
        self.btn_add_actress.setToolTip("添加女优并选择")

        self.btn_to_left.clicked.connect(self.move_to_left)
        self.btn_to_right.clicked.connect(self.move_to_right)
        self.btn_add_actress.clicked.connect(self.add_actress_dialog)

                # 女优中间按钮布局
        btn_actress_layout = QHBoxLayout()
        btn_actress_layout.addWidget(self.btn_to_left)
        btn_actress_layout.addWidget(self.label_actress)
        btn_actress_layout.addWidget(self.btn_to_right)


        # 女优搜索布局
        btn_actress_search_layout = QHBoxLayout()
        btn_actress_search_layout.addWidget(self.search_box)
        btn_actress_search_layout.addWidget(self.btn_add_actress)
        # 女优选择列布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addLayout(btn_actress_search_layout)
        main_layout.addWidget(self.choose_actress_view)
        main_layout.addLayout(btn_actress_layout)
        main_layout.addWidget(self.receive_actress_view)

        from controller.GlobalSignalBus import global_signals
        global_signals.actress_data_changed.connect(self.refresh_right_list)


    def load_actress_from_db(self,exclude_ids=None):
        exclude_ids=exclude_ids or []
        #数据库有没有被正确的读取是一个问题，数据库的版本与软件的版本要对上
        try:
            logging.info("ActressSelector加载女优数据库")
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 女优ID,中文名,日文名 FROM v_actress_all_info WHERE 中文名 IS NOT NULL AND 日文名 IS NOT NULL")
                rows = cursor.fetchall()
            items=[]
            rows = rows[::-1]
            for 女优ID, 中文名, 日文名 in rows:
                if 女优ID in exclude_ids:
                    continue
                label = f"{中文名}（{日文名}）"
                item = QStandardItem(label)
                # 设置附加数据（绑定 ID）
                item.setData(女优ID)
                # 设置只读不可编辑
                item.setEditable(False)
                items.append(item)
            return items

        except Exception as e:
            self.msg.show_critical("数据库错误", f"无法读取数据：\n{e}")
            return []

    @Slot()
    def move_to_left(self):
        '''移动到选择侧'''
        index=self.choose_actress_view.selectionModel().selectedIndexes()
        if not index:
            return
        item = self.choose_actress_model.itemFromIndex(index[0])

        # 移动逻辑
        self.choose_actress_items.remove(item)
        self.choose_actress_all_items.remove(item)
        item_copy=item.clone()
        self.receive_actress_items.append(item_copy)

        self.update_model(self.receive_actress_model, self.receive_actress_items)
        self.filter_choose_actress_items(self.search_box.text())

        self.selection_changed.emit()#发射信号

    @Slot()
    def move_to_right(self):
        '''移动到待选侧'''
        index=self.receive_actress_view.selectionModel().selectedIndexes()#找到选择的index
        if not index:
            return
        item = self.receive_actress_model.itemFromIndex(index[0])

        self.receive_actress_items.remove(item)
        item_copy=item.clone()
        self.choose_actress_all_items.insert(0,item_copy)

        self.update_model(self.receive_actress_model, self.receive_actress_items)
        self.filter_choose_actress_items(self.search_box.text())

        self.selection_changed.emit()#发射信号

    def refresh_right_list(self):
        '''这个是新添加女优后才刷新已选择侧列表'''
        # 获取左侧所有已选ID
        left_ids = [self.receive_actress_model.item(i).data() for i in range(self.receive_actress_model.rowCount())]

        # 从数据库重新加载，排除已在左边的
        self.choose_actress_all_items = self.load_actress_from_db(exclude_ids=left_ids)
        self.update_model(self.choose_actress_model, self.choose_actress_all_items)
        # 根据搜索框文本筛选
        self.filter_choose_actress_items(self.search_box.text())
        self.selection_changed.emit()

    def update_model(self, model: QStandardItemModel, items: list):
        model.clear()
        for item in items:
            model.appendRow(item)

    def filter_choose_actress_items(self, keyword):
        '''
        搜索框筛选女优
        优化点当女优的数量非常的庞大的时候需要优化就比如说每年的女优数量在15000+积累的量基本上是百万的数量级，当然我这个是个人的收藏，没有必要弄的很的大
        '''
        keyword = keyword.strip()
        if not keyword:
            self.choose_actress_items = list(self.choose_actress_all_items)
        else:
            self.choose_actress_items = [
                item for item in self.choose_actress_all_items
                if keyword in item.text()
            ]
        self.update_model(self.choose_actress_model, self.choose_actress_items)

    @Slot()
    def add_actress_dialog(self):
        from ui.dialogs.AddActressDialog import AddActressDialog
        dialog = AddActressDialog()
        dialog.success.connect(self.handle_actress_result)
        dialog.exec()  # 模态显示对话框，阻塞主窗口直到关闭

    @Slot()
    def handle_actress_result(self):
        #接受添加女优成功的信号后进行操作
        self.refresh_right_list()
        old_text=self.search_box.text()
        self.search_box.clear()
        #选中右侧最上面
        if self.choose_actress_model.rowCount() > 0:
            index = self.choose_actress_model.index(0, 0)  # 第 0 行，第 0 列
            self.choose_actress_view.setCurrentIndex(index)
            self.choose_actress_view.scrollTo(index)       # 可选：自动滚动到该项
        self.move_to_left()
        self.search_box.setText(old_text)#保持输入框的文字

    def clear_other_selection(self,other_list, selected: QItemSelection):
        """当选中状态变化时，清除另一个列表的选中"""
        if selected.count() > 0:  # 如果有选中项
            other_list.selectionModel().clearSelection()

    def find_item_by_id(self, target_id) -> QStandardItem | None:
        """通过ID在choose_actress_items中查找item"""
        for item in self.choose_actress_items:
            if item.data() == target_id:  # 假设ID存储在默认角色
                return item
        logging.warning("根据id: %s  找不到待选区对应的item",target_id)
        return None

    def move_all_to_left(self):
        '''把所有的全部移到上面去'''
        #logging.info("开始移到上面共"+str(len(self.receive_actress_items)))
        self.search_box.setText(None)
        for item in self.receive_actress_items.copy():#把接收器的部分全部移回去
            #logging.info(item.text())
            self.receive_actress_items.remove(item)#危险操作注意
            item_copy=item.clone()
            self.choose_actress_all_items.insert(0,item_copy)

        self.update_model(self.receive_actress_model, self.receive_actress_items)
        self.filter_choose_actress_items(self.search_box.text())

        #logging.info("下面还剩下"+str(len(self.receive_actress_items)))

    def get_selection_actress_name(self)->str:
        '''获得当前选择的女优的姓名，这个后面在实现'''

        index=self.choose_actress_view.selectionModel().selectedIndexes()
        if not index:
            return
        item = self.choose_actress_model.itemFromIndex(index[0])
        return item.text()
    
#---------------------------------------------------
#                 暴露在外面的接口
#---------------------------------------------------

    def get_selected_ids(self)->list:
        '''返回被选中的id'''
        ids = []
        for row in range(self.receive_actress_model.rowCount()):
            item = self.receive_actress_model.item(row)
            actress_id = item.data()
            ids.append(actress_id)
        return ids
    
    @Slot('QList<int>')
    def load_with_ids(self,ids:list[int]):
        '''通过ids列表加载到下面的选择器里
        不能重新加载，整个系统只是加载一次，然后就是不断的移动
        '''
        self.search_box.setText(None)
        #logging.info("ActressSelector开始移到上面共:%s",str(len(self.receive_actress_items)))
        self.move_all_to_left()

        #logging.info("ActressSelector下面还剩下:%s",str(len(self.receive_actress_items)))
        #logging.info("ActressSelector开始移到下面共:%s",str(len(ids)))

        for id in ids:#移动到下面
            item=self.find_item_by_id(id)
            #logging.info(item.text())
            self.choose_actress_items.remove(item)
            self.choose_actress_all_items.remove(item)
            item_copy=item.clone()
            self.receive_actress_items.append(item_copy)

        self.update_model(self.receive_actress_model, self.receive_actress_items)
        self.filter_choose_actress_items(self.search_box.text())
        self.selection_changed.emit()
