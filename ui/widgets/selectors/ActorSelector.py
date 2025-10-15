from PySide6.QtWidgets import QPushButton, QHBoxLayout, QWidget, QLabel,QVBoxLayout,QLineEdit,QListView
from PySide6.QtGui import QStandardItemModel,QStandardItem
from PySide6.QtCore import Qt,QItemSelection,Signal,Slot
import sqlite3
from config import DATABASE
from ui.dialogs.AddActorDialog import AddActorDialog
import logging
from controller import MessageBoxService
from ui.basic import IconPushButton
class ActorSelector(QWidget):
    '''男演员选择器'''
    #像这种需要动态从数据库读取的，在添加数据库中的东西改变后这里要接受信号，然后刷新，否则就会有问题
    selection_changed=Signal()#下方被选择的列表改变了
    def __init__(self):
        super().__init__()
        self.setFixedWidth(170)
        self.msg=MessageBoxService(self)
        # 数据初始化
        self.choose_actor_all_items = self.load_actor_from_db()
        self.choose_actor_items = list(self.choose_actor_all_items)
        self.receive_actor_items = []

        # 模型初始化
        self.receive_actor_model = QStandardItemModel()
        self.choose_actor_model = QStandardItemModel()

        self.update_model(self.choose_actor_model, self.choose_actor_items)
        self.update_model(self.receive_actor_model, self.receive_actor_items)

        self.init_ui()
        self.signal_connect()

    def init_ui(self):
        # 右侧搜索框和视图和按钮
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜索中文名或日文名")
        self.search_box.setClearButtonEnabled(True)
        
        self.choose_actor_view = QListView()
        self.choose_actor_view.setModel(self.choose_actor_model)

        self.receive_actor_view = QListView()
        self.receive_actor_view.setModel(self.receive_actor_model)

        self.label_actor=QLabel("参演男优")
        self.label_actor.setAlignment(Qt.AlignCenter)

        # 按钮
        self.btn_to_left = IconPushButton("arrow-down.png")
        self.btn_to_left.setToolTip("选择参演男优")
        self.btn_to_right = IconPushButton("arrow-up.png")
        self.btn_to_right.setToolTip("移除参演男优")
        self.btn_add_actor=IconPushButton("circle-plus.png")
        self.btn_add_actor.setToolTip("添加男优并选择")

        # 男优中间按钮布局
        btn_actor_layout = QHBoxLayout()
        btn_actor_layout.addWidget(self.btn_to_left)
        btn_actor_layout.addWidget(self.label_actor)
        btn_actor_layout.addWidget(self.btn_to_right)

        # 男优搜索布局
        btn_actor_search_layout = QHBoxLayout()
        btn_actor_search_layout.addWidget(self.search_box)
        btn_actor_search_layout.addWidget(self.btn_add_actor)

        # 男优选择列布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addLayout(btn_actor_search_layout)
        main_layout.addWidget(self.choose_actor_view)
        main_layout.addLayout(btn_actor_layout)
        main_layout.addWidget(self.receive_actor_view)

    def signal_connect(self):
        from controller.GlobalSignalBus import global_signals
        global_signals.actor_data_changed.connect(self.refresh_right_list)
        self.search_box.textChanged.connect(self.filter_choose_actor_items)
        # 连接选中信号
        self.receive_actor_view.selectionModel().selectionChanged.connect(
            lambda selected, _: self.clear_other_selection(self.choose_actor_view, selected)
        )

        self.choose_actor_view.selectionModel().selectionChanged.connect(
            lambda selected, _: self.clear_other_selection(self.receive_actor_view, selected)
        )

        self.btn_to_left.clicked.connect(self.move_to_left)
        self.btn_to_right.clicked.connect(self.move_to_right)
        self.btn_add_actor.clicked.connect(self.add_actor_dialog)

    def load_actor_from_db(self,exclude_ids=None):
        exclude_ids=exclude_ids or []
        '''从数据库读数据并加载到viewmodel内,在打开页面的过程中只运行一次
        #数据库有没有被正确的读取是一个问题，数据库的版本与软件的版本要对上
        '''
        query="""
SELECT 
	a.actor_id,
	actor_name.cn AS cn_name,
	actor_name.jp AS jp_name 
FROM actor a
JOIN actor_name ON actor_name.actor_id=a.actor_id
"""
        try:
            logging.info("ActorSelector加载男优数据库")
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
            items=[]
            rows = rows[::-1]
            for actor_id, cn_name, jp_name in rows:
                if actor_id in exclude_ids:
                    continue
                label = f"{cn_name}（{jp_name}）"
                item = QStandardItem(label)

                # 设置附加数据（绑定 ID）
                item.setData(actor_id)
                # 设置只读不可编辑
                item.setEditable(False)
                items.append(item)

            return items
        except Exception as e:
            self.msg.show_critical( "数据库错误", f"无法读取数据：\n{e}")
            logging.warning("读取男优数据库失败%s",e)
            return []

    def move_to_left(self):
        #index = self.choose_actor_view.currentIndex()
        index=self.choose_actor_view.selectionModel().selectedIndexes()
        if not index:
            return
        item = self.choose_actor_model.itemFromIndex(index[0])

        # 移动逻辑
        self.choose_actor_items.remove(item)
        self.choose_actor_all_items.remove(item)
        item_copy=item.clone()
        self.receive_actor_items.append(item_copy)

        self.update_model(self.receive_actor_model, self.receive_actor_items)
        self.filter_choose_actor_items(self.search_box.text())

        self.selection_changed.emit()#发射信号

    def move_to_right(self):
        #index = self.receive_actor_view.currentIndex()
        index=self.receive_actor_view.selectionModel().selectedIndexes()#找到选择的index
        if not index:
            return
        item = self.receive_actor_model.itemFromIndex(index[0])

        self.receive_actor_items.remove(item)
        item_copy=item.clone()
        #self.choose_actor_all_items.append(item_copy)
        self.choose_actor_all_items.insert(0,item_copy)
        self.filter_choose_actor_items(self.search_box.text())
        self.update_model(self.receive_actor_model, self.receive_actor_items)

        self.selection_changed.emit()#发射信号
        
    def refresh_right_list(self):#这个有bug要改，在新添加后就有bug
        '''重新从数据库里加载数据'''
        #刷新待选列表
        # 获取左侧所有已选ID
        left_ids = [self.receive_actor_model.item(i).data() for i in range(self.receive_actor_model.rowCount())]
        # 从数据库重新加载，排除已在左边的
        self.choose_actor_all_items = self.load_actor_from_db(exclude_ids=left_ids)
        self.update_model(self.choose_actor_model, self.choose_actor_all_items)
        # 根据搜索框文本筛选
        self.filter_choose_actor_items(self.search_box.text())
        self.selection_changed.emit()

    def update_model(self, model: QStandardItemModel, items: list):
        model.clear()
        for item in items:
            model.appendRow(item)

    def filter_choose_actor_items(self, keyword):
        keyword = keyword.strip()
        if not keyword:
            self.choose_actor_items = list(self.choose_actor_all_items)
        else:
            self.choose_actor_items = [
                item for item in self.choose_actor_all_items
                if keyword in item.text()
            ]
        self.update_model(self.choose_actor_model, self.choose_actor_items)

    def add_actor_dialog(self):
        dialog = AddActorDialog()
        dialog.success.connect(self.handle_actor_result)
        dialog.exec()  # 模态显示对话框，阻塞主窗口直到关闭

    def handle_actor_result(self,success):
        #接受添加男成功的信号后进行操作
        if success:
            self.refresh_right_list()
            old_text=self.search_box.text()
            self.search_box.clear()
            #选中右侧最上面
            if self.choose_actor_model.rowCount() > 0:
                index = self.choose_actor_model.index(0, 0)  # 第 0 行，第 0 列
                self.choose_actor_view.setCurrentIndex(index)
                self.choose_actor_view.scrollTo(index)       # 可选：自动滚动到该项
            self.move_to_left()
            self.search_box.setText(old_text)#保持输入框的文字

    def clear_other_selection(self,other_list, selected: QItemSelection):
        """当选中状态变化时，清除另一个列表的选中"""
        if selected.count() > 0:  # 如果有选中项
            other_list.selectionModel().clearSelection()
    

    def find_item_by_id(self, target_id:int) -> QStandardItem | None:
        """通过ID在choose_actor_items中查找item"""
        for item in self.choose_actor_items:
            if item.data() == target_id:  # 假设ID存储在默认角色
                return item
            
        logging.warning("根据id: %s  找不到待选区对应的item",target_id)
        return None

    def move_all_to_left(self):
        '''把接收器的部分全部移回去，回到初始状态'''
        self.search_box.setText(None)
        for item in self.receive_actor_items.copy():
            logging.info(item.text())
            self.receive_actor_items.remove(item)#危险操作注意
            item_copy=item.clone()
            self.choose_actor_all_items.insert(0,item_copy)

        self.update_model(self.receive_actor_model, self.receive_actor_items)
        self.filter_choose_actor_items(self.search_box.text())


#---------------------------------------------------
#                 暴露在外面的接口
#---------------------------------------------------

    def get_selected_ids(self)->list:
        '''返回被选中的id'''
        ids = []
        
        for row in range(self.receive_actor_model.rowCount()):
            item = self.receive_actor_model.item(row)
            actor_id = item.data()
            ids.append(actor_id)
        return ids
    
    @Slot('QList<int>')
    def load_with_ids(self,ids:list):
        '''通过ids列表加载到下面的选择器里
        不能重新加载，整个系统只是加载一次，然后就是不断的移动
        '''
        #logging.debug("ActorSelector开始移到上面共:%s",str(len(self.receive_actor_items)))
        self.search_box.setText(None)
        self.move_all_to_left()#先全移回去，回到初始的状态

        self.update_model(self.receive_actor_model, self.receive_actor_items)
        #logging.debug("ActorSelector下面还剩下:%s",str(len(self.receive_actor_items)))

        #logging.debug("ActorSelector开始移到下面共:%s",str(len(ids)))
        for id in ids:
            #移动到下面
            item=self.find_item_by_id(id)
            #logging.info(item.text())#这里有bug在新添加一个男优的时候，这个item就没有了
            self.choose_actor_items.remove(item)
            self.choose_actor_all_items.remove(item)
            item_copy=item.clone()
            self.receive_actor_items.append(item_copy)

            self.update_model(self.receive_actor_model, self.receive_actor_items)
        self.filter_choose_actor_items(self.search_box.text())
        self.selection_changed.emit()
