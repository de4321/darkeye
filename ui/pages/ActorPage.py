from PySide6.QtWidgets import QPushButton, QHBoxLayout, QWidget, QLabel,QVBoxLayout,QLineEdit,QComboBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt,Signal,Slot,QTimer
import sqlite3,logging

from config import DATABASE
from core.database.query import get_actorname
from core.database.db_utils import attach_private_db,detach_private_db
from ui.widgets import ActorCard,CompleterLineEdit
from ui.basic import LazyScrollArea,IconPushButton
from ui.base import LazyWidget
from utils.utils import timeit

class ActorPage(LazyWidget):
    def __init__(self):
        super().__init__()
        
    def _lazy_load(self):
        logging.info("----------加载男优界面----------")
        self.last_scroll_value = 0  # 上一次滚动位置
        self.actor_name=None

        self.order="添加逆序"#排序默认值
        self.cup=None

        self.spacer_widget = QWidget()
        self.spacer_widget.setFixedHeight(70)

        self.filter_widget = QWidget()
        self.filter_widget.setFixedHeight(26)
        self.filter_layout = QHBoxLayout(self.filter_widget)  # 直接传入 widget
        self.filter_layout.setContentsMargins(10,0,10,0)

        self.actorname_input = CompleterLineEdit(get_actorname)


        self.info=QLabel()#用来显示信息
        self.info.setFixedWidth(100)

        self.actor_input = QLineEdit()

        self.btn_eraser=IconPushButton("eraser.png")
        self.btn_reload=IconPushButton("refresh-cw.png")
        #排序选择器
        self.order_combo = QComboBox()
        self.order_combo.addItems(["添加顺序","添加逆序"])
        self.order_combo.setCurrentText(self.order)


        self.filter_layout.addWidget(QLabel("男优"))
        self.filter_layout.addWidget(self.actorname_input)


        self.filter_layout.addWidget(self.btn_reload)
        self.filter_layout.addWidget(self.btn_eraser)
        self.filter_layout.addWidget(self.info)

        self.filter_layout.addWidget(self.order_combo)

        #加载男优的区域
        self.lazy_area = LazyScrollArea(column_width=150)

        #总体布局
        mainlayout = QVBoxLayout(self)
        mainlayout.setContentsMargins(0, 0, 0, 0)
        mainlayout.addWidget(self.spacer_widget)
        mainlayout.addWidget(self.filter_widget)
        mainlayout.addWidget(self.lazy_area)
        
        self.singal_connect()

        self.lazy_area.set_loader(self.load_page)#这个最费时
        self.info.setText("过滤总数:"+str(self.load_data(0,0,True)[0][0]))

        self.filter_timer = QTimer(self)#防抖动
        self.filter_timer.setSingleShot(True)
        self.filter_timer.timeout.connect(self.apply_filter_real)


    def singal_connect(self):
        self.btn_reload.clicked.connect(self.refresh)
        self.order_combo.activated.connect(self.apply_filter)
        self.actorname_input.textChanged.connect(self.apply_filter)
        from controller.GlobalSignalBus import global_signals
        global_signals.actor_data_changed.connect(self.actorname_input.reload_items)
        self.btn_eraser.clicked.connect(self._clear_all_search)

    @Slot()
    def _clear_all_search(self):
        self.actorname_input.setText("")
        self.apply_filter()

    @Slot()
    def apply_filter(self):
        """防抖：用户操作后延迟执行真正的查询"""
        self.filter_timer.start(50)  # 停 50ms 才真正执行

    @Slot()
    def apply_filter_real(self):
        self.actor_name = self.actorname_input.text().strip()
        self.order=self.order_combo.currentText()


        self.lazy_area.reset()
        self.update_info()


    def update_info(self):
        '''更新查询到几条数据'''
        if self.load_data(0,0,True) is None:
            self.info.setText("没有查询到数据")
        else:
            self.info.setText("过滤总数:"+str(self.load_data(0,0,True)[0][0]))


    def load_data(self, page_index: int, page_size: int,count:bool=False)->tuple:
        '''返回查询的数据'''
        offset = page_index * page_size
        # 动态拼接 SQL,要怎么筛逻辑都在这里改
        params=[]
        #基础查询
        if count:#查询总数
            query=f"""
SELECT 
    count(*) AS count
FROM actor
        """
        else:
            query=f"""
SELECT 
    (SELECT cn FROM actor_name WHERE actor_id = actor.actor_id AND(name_type=1))AS name,
    image_url,
    actor.actor_id
FROM actor
        """
        
        # 拼withsql
        if self.actor_name:
            withsql=f'''
WITH filtered_actores AS (--先筛选名字中的actor_id,单独的
SELECT 
    DISTINCT actor_id
FROM 
    actor_name
WHERE cn LIKE ? OR jp LIKE ? OR en LIKE ? OR kana LIKE ?
)
            '''
            query=withsql+query
            params.extend([f"%{self.actor_name}%", f"%{self.actor_name}%", f"%{self.actor_name}%", f"%{self.actor_name}%"])

        # 拼join
        if self.actor_name:
            join="JOIN filtered_actores f ON actor.actor_id = f.actor_id \n"
            query+=join

        # 拼where
        where="WHERE 1=1\n"#占位
        match self.order:
            case "年龄顺序":
                where="WHERE actor.birthday !=''AND actor.birthday is NOT NULL\n"
            case "年龄逆序":
                where="WHERE actor.birthday !=''AND actor.birthday is NOT NULL\n"

        query+=where#比拼


        # 拼order
        match self.order:
            case "添加顺序":
                order="ORDER BY actor.create_time \n"
            case "添加逆序":
                order="ORDER BY actor.create_time DESC\n"

        if not count:
            query +=f"{order} LIMIT ? OFFSET ?"#最后拼这个
            params.extend([page_size, offset])

        #logging.debug(f"actorPage Execute SQL\n{query}")
        with sqlite3.connect(f"file:{DATABASE}?mode=ro",uri=True) as conn:
            cursor = conn.cursor()
            cursor.execute(query,params) #这里面不能orderby random 会重复
            results=cursor.fetchall()
        return results

    def load_page(self, page_index: int, page_size: int) -> list[ActorCard]:
        """返回一个页面的 actorCard 列表"""
        result:list[ActorCard] = []
        data=self.load_data(page_index,page_size)
        if not data:
            return None
        for name, image_url,actor_id in data:
            card = ActorCard(name,image_url,actor_id)

            result.append(card)
        return result
    
    def refresh(self):
        '''刷新'''
        self.lazy_area.reset()
        self.update_info()

    @Slot(int)
    def handle_scroll(self, value):
        direction = value - self.last_scroll_value

        if direction > 5:
            # 向下滚动，隐藏顶部
            if self.filter_widget.isVisible():
                self.filter_widget.hide()
                self.spacer_widget.hide()

        elif direction < -5:
            # 向上滚动，显示顶部
            if not self.filter_widget.isVisible():
                self.filter_widget.show()
                self.spacer_widget.show()

        self.last_scroll_value = value


