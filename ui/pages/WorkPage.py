
from PySide6.QtWidgets import QHBoxLayout, QWidget, QLabel,QSizePolicy,QVBoxLayout,QLineEdit,QComboBox,QScrollArea
from PySide6.QtCore import Signal,QThreadPool,Slot,Qt,QTimer
import sqlite3,logging
from ui.widgets import CompleterLineEdit,CoverCard,TagSelector4
from ui.basic import LazyScrollArea,IconPushButton,HorizontalScrollArea
from config import DATABASE
from core.database.query import get_actressname,getUniqueDirector,get_actorname,get_serial_number,get_maker_name
from core.database.db_utils import attach_private_db,detach_private_db
from utils.utils import timeit
from ui.base import LazyWidget


class WorkPage(LazyWidget):
    '''主要是展示作品的页面，包括筛选的装置，比如标签筛选'''
    def __init__(self):
        super().__init__()
        
    def _lazy_load(self):
        logging.info("----------加载作品界面----------")

        pool = QThreadPool.globalInstance()
        cpu_count = pool.maxThreadCount()
        pool.setMaxThreadCount(cpu_count*3)  # 例如 I/O 密集型任务，3倍 CPU 核心

        self.last_scroll_value = 0  # 上一次滚动位置
        self.keyword=None
        self.tag_ids=None
        self.actress=None
        self.director=None
        self.actor=None
        self.title=None
        self.serial_number=None
        self.studio=None
        self._green_mode=False#安全模式

        self.order="添加逆序"#排序的内在的值
        self.scope="公共库范围"

        self.spacer_widget = QWidget()
        self.spacer_widget.setFixedHeight(70)


        #横向的区域
        scroll=HorizontalScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFixedHeight(26)
        scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        filterwidget=QWidget()
        filterlayout=QHBoxLayout(filterwidget)
        filterlayout.setContentsMargins(0,0,0,0)
        filterwidget.setFixedHeight(26)
        filterwidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        scroll.setWidget(filterwidget)
        scroll.setStyleSheet("""
    QScrollArea {
        border: none;
        background: transparent;
    }
    QScrollBar {
        background: transparent;
    }
""")
        
        self.story_input = QLineEdit()
        self.title_input=QLineEdit()
        self.serial_number_input=CompleterLineEdit(get_serial_number)
        self.actress_input = CompleterLineEdit(get_actressname)
        self.director_input = CompleterLineEdit(getUniqueDirector)
        self.actor_input=CompleterLineEdit(get_actorname)
        self.maker_input=CompleterLineEdit(get_maker_name)

        self.story_input.setFixedWidth(100)
        self.title_input.setFixedWidth(100)
        self.serial_number_input.setFixedWidth(150)
        self.actress_input.setFixedWidth(120)
        self.director_input.setFixedWidth(150)
        self.actor_input.setFixedWidth(120)
        self.maker_input.setFixedWidth(150)

        filterlayout.addWidget(QLabel("番号："))
        filterlayout.addWidget(self.serial_number_input)
        filterlayout.addWidget(QLabel("女优"))
        filterlayout.addWidget(self.actress_input)
        filterlayout.addWidget(QLabel("标题包含："))
        filterlayout.addWidget(self.title_input)
        filterlayout.addWidget(QLabel("简短故事包含："))
        filterlayout.addWidget(self.story_input)
        filterlayout.addWidget(QLabel("导演"))
        filterlayout.addWidget(self.director_input)
        filterlayout.addWidget(QLabel("男优"))
        filterlayout.addWidget(self.actor_input)
        filterlayout.addWidget(QLabel("片商"))
        filterlayout.addWidget(self.maker_input)



        self.info=QLabel()#用来显示信息
        self.info.setFixedWidth(100)

        #self.filter_btn =IconPushButton("search.png")
        self.btn_reload=IconPushButton("refresh-cw.png")
        self.btn_eraser=IconPushButton("eraser.png")

        #排序选择器
        self.order_combo = QComboBox()
        self.order_combo.addItems(["添加逆序","添加顺序","更新时间顺序","更新时间逆序","发布时间逆序", "发布时间顺序", "拍摄年龄顺序","拍摄年龄逆序"])
        self.order_combo.setCurrentText(self.order)


        self.scope_combo = QComboBox()
        self.scope_combo.addItems(["公共库范围","收藏库范围","收藏未观看"])
        self.scope_combo.setCurrentText(self.scope)

        self.filter_widget = QWidget()
        self.filter_widget.setFixedHeight(26)
        self.filter_layout = QHBoxLayout(self.filter_widget)  # 直接传入 widget
        self.filter_layout.setContentsMargins(10, 0, 10,0)

        self.filter_layout.addWidget(scroll)

        #self.filter_layout.addWidget(self.filter_btn)
        self.filter_layout.addWidget(self.btn_reload)
        self.filter_layout.addWidget(self.btn_eraser)
        self.filter_layout.addWidget(self.info)
        self.filter_layout.addWidget(self.scope_combo)
        self.filter_layout.addWidget(self.order_combo)

        #加载影片的区域
        self.lazy_area = LazyScrollArea(column_width=220)
        self.lazy_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        #self.lazy_area.verticalScrollBar().valueChanged.connect(self.handle_scroll)

        self.tagselector=TagSelector4()
        self.tagselector.tag_receive_widget.setFixedWidth(84)
        self.tagselector.left_widget.setFixedWidth(108)
        self.hlayout=QHBoxLayout()#细分的layout
        self.hlayout.addWidget(self.tagselector,0)
        self.hlayout.addWidget(self.lazy_area,1)

        #总体布局
        mainlayout = QVBoxLayout(self)
        mainlayout.setContentsMargins(0, 0, 0, 0)
        mainlayout.addWidget(self.spacer_widget)
        mainlayout.addWidget(self.filter_widget)
        mainlayout.addLayout(self.hlayout)

        self.singal_connect()

        self.update_info()
        '''懒加载'''
        #这个如果要优化的话就是异步加载数据，然后加载UI

        self.lazy_area.set_loader(self.load_page)#这个最消耗时间
        
        self.filter_timer = QTimer(self)#防抖动
        self.filter_timer.setSingleShot(True)
        self.filter_timer.timeout.connect(self.apply_filter_real)


    def singal_connect(self):
        '''信号连接'''
        #self.filter_btn.clicked.connect(self.apply_filter)
        self.btn_reload.clicked.connect(self.refresh)

        #self.title_input.returnPressed.connect(self.apply_filter)
        #self.story_input.returnPressed.connect(self.apply_filter)
        #self.serial_number_input.returnPressed.connect(self.apply_filter)
        #self.actress_input.returnPressed.connect(self.apply_filter)
        #self.actor_input.returnPressed.connect(self.apply_filter)
        #self.director_input.returnPressed.connect(self.apply_filter)
        #self.maker_input.returnPressed.connect(self.apply_filter)

        self.title_input.textChanged.connect(self.apply_filter)
        self.story_input.textChanged.connect(self.apply_filter)
        self.serial_number_input.textChanged.connect(self.apply_filter)
        self.actress_input.textChanged.connect(self.apply_filter)
        self.actor_input.textChanged.connect(self.apply_filter)
        self.director_input.textChanged.connect(self.apply_filter)
        self.maker_input.textChanged.connect(self.apply_filter)

        self.order_combo.currentTextChanged.connect(self.apply_filter)
        self.scope_combo.currentTextChanged.connect(self.apply_filter)
        self.tagselector.selection_changed.connect(self.apply_filter)

        from controller.GlobalSignalBus import global_signals
        global_signals.green_mode_changed.connect(self.update_green_mode)#全局转发
        global_signals.work_data_changed.connect(self.reload_input)
        global_signals.actress_data_changed.connect(self.actress_input.reload_items)
        global_signals.actor_data_changed.connect(self.actor_input.reload_items)

        self.btn_eraser.clicked.connect(self._clear_all_search)

    @Slot()
    def _clear_all_search(self):
        self.actor_input.setText("")
        self.actress_input.setText("")
        self.director_input.setText("")
        self.title_input.setText("")
        self.story_input.setText("")
        self.serial_number_input.setText("")
        self.maker_input.setText("")
        self.tagselector.load_with_ids([])
        self.apply_filter()

    @Slot()
    def reload_input(self):
        self.serial_number_input.reload_items()
        self.director_input.reload_items()
        self.maker_input.reload_items()

    @Slot(bool)
    def update_green_mode(self,green_mode:bool):
        self._green_mode=green_mode
        logging.debug(f"workpage的绿色模式{green_mode}")


    @Slot()
    def apply_filter(self):
        """防抖：用户操作后延迟执行真正的查询"""
        self.filter_timer.start(50)  # 停 50ms 才真正执行

    @Slot()
    def apply_filter_real(self):
        self.keyword = self.story_input.text().strip()
        self.actress = self.actress_input.text().strip()
        self.director=self.director_input.text().strip()
        self.actor=self.actor_input.text().strip()
        self.title=self.title_input.text().strip()
        self.serial_number=self.serial_number_input.text().strip()
        self.studio=self.maker_input.text().strip()

        self.tag_ids=self.tagselector.get_selected_ids()

        self.scope=self.scope_combo.currentText()
        self.order=self.order_combo.currentText()

        self.lazy_area.reset()
        self.update_info()

    def update_info(self):
        '''更新查询到几条数据'''
        if self.load_data(0,0,True) is None:
            self.info.setText("没有查询到数据")
        else:
            self.info.setText("过滤总数:"+str(len(self.load_data(0,0,True))))

    def load_data(self, page_index: int, page_size: int,count:bool=False)->tuple:
        """返回一个页面的 CoverCard 所需要的数据,这个是非常的快的，不消耗时间"""
        offset = page_index * page_size

        # 动态拼接 SQL,要怎么筛逻辑都在这里改
        params=[]
        query=f'''
SELECT 
    work.serial_number, 
    cn_title, 
    image_url,
    wtr.tag_id,
    work.work_id,
    CASE 
        WHEN (SELECT cn_name FROM maker WHERE maker_id =p.maker_id) IS NULL
        THEN 0
        ELSE 1
    END AS standard
FROM work
LEFT JOIN work_tag_relation wtr ON work.work_id = wtr.work_id AND wtr.tag_id IN (1, 2, 3)
LEFT JOIN 
    prefix_maker_relation p ON p.prefix = SUBSTR(work.serial_number, 1, INSTR(work.serial_number, '-') - 1)
        '''
        cte_parts = []

        # 拼with-----------------------------------------------------------------
        if self.actress:
            withsql=f'''
filtered_actresses AS (--先筛选名字中的actress_id,单独的
SELECT 
    DISTINCT actress_id
FROM 
    actress_name
WHERE cn LIKE ? OR jp LIKE ?
)
'''
            cte_parts.append(withsql)
            params.extend([f"%{self.actress}%", f"%{self.actress}%"])

        if self.actor:
            withsql=f'''
filtered_actors AS (
SELECT 
    DISTINCT actor_id
FROM 
    actor_name
WHERE cn LIKE ? OR jp LIKE ?
)
'''
            cte_parts.append(withsql)
            params.extend([f"%{self.actor}%", f"%{self.actor}%"])           
        if self.studio:
            withsql=f'''
filter_maker AS(
SELECT 
    DISTINCT maker_id
FROM 
    maker
WHERE cn_name LIKE ? OR jp_name LIKE ?
)
'''
            cte_parts.append(withsql)
            params.extend([f"%{self.studio}%", f"%{self.studio}%"])  
            # 最终 SQL
        
        cte_sql = ""
        if cte_parts:  # 如果有任何一个 CTE
            cte_sql = "WITH " + ",\n".join(cte_parts) + "\n"

        query=cte_sql+query

        # 拼join----------------------------------------------------------------
        if self.scope=="收藏库范围"or self.scope=="收藏未观看":
            join="JOIN priv.favorite_work fav ON fav.work_id=work.work_id\n"
            query+=join

        if self.order=="拍摄年龄顺序"or self.order=="拍摄年龄逆序":
            join="JOIN v_work_all_info v ON work.work_id = v.work_id\n"
            query+=join

        if self.actress:
            join='''
JOIN work_actress_relation ON work_actress_relation.work_id=work.work_id
JOIN actress ON actress.actress_id=work_actress_relation.actress_id
JOIN filtered_actresses f ON actress.actress_id = f.actress_id
'''
            query+=join
        if self.actor:
            join='''
JOIN work_actor_relation ON work_actor_relation.work_id=work.work_id
JOIN filtered_actors fa ON fa.actor_id = work_actor_relation.actor_id
'''
            query+=join
        if self.studio:
            join='''
--JOIN prefix_maker_relation p ON p.prefix = SUBSTR(work.serial_number, 1, INSTR(work.serial_number, '-') - 1)
JOIN filter_maker ON filter_maker.maker_id=p.maker_id
'''
            query+=join

        if self.tag_ids:
            placeholders = ','.join('?' for _ in self.tag_ids)
            join=f'''LEFT JOIN work_tag_relation wtr2 ON work.work_id =wtr2.work_id AND wtr2.tag_id IN ({placeholders})\n'''
            query+=join
            params.extend(self.tag_ids)
        
        # 拼where-----------------------------------------------------------------
        where="WHERE is_deleted=0\n"#占位
        query+=where
        if self.keyword:
            where="AND work.story LIKE ?\n"
            params.append(f"%{self.keyword}%")
            query+=where

        if self.order=="拍摄年龄顺序"or self.order=="拍摄年龄逆序":
            where="AND v.avg_age IS NOT NULL\n"
            query+=where

        if self.order=="发布时间顺序"or self.order=="发布时间逆序":
            where="AND work.release_date IS NOT NULL AND work.release_date!=''\n"
            query+=where

        if self.director:
            where="AND work.director LIKE ?\n"
            query+=where
            params.append(f"%{self.director}%")

        if self.actor:
            pass

        if self.serial_number:
            where="AND work.serial_number LIKE ?\n"
            query+=where
            params.append(f"%{self.serial_number}%")

        if self.studio:
            pass

        if self.title:
            where="AND work.cn_title LIKE ?\n"
            query+=where
            params.append(f"%{self.title}%")

        if self.scope=="收藏未观看":
            where="AND work.work_id NOT IN (SELECT work_id FROM priv.masturbation WHERE work_id IS NOT NULL)\n"
            query+=where
        # 拼groupby-------------------------------------------------------
        if self.tag_ids:
            num_tags = len(self.tag_ids)
            groupby=f"""
GROUP BY work.work_id
HAVING COUNT(DISTINCT wtr2.tag_id) = ?
            """
            query+=groupby
            params.append(num_tags)

        # 拼order------------------------------------------------------------
        match self.order:
            case "发布时间顺序":
                order="ORDER BY work.release_date\n"
            case "发布时间逆序":
                order="ORDER BY work.release_date DESC\n"
            case "拍摄年龄顺序":
                order="ORDER BY (SELECT avg_age FROM v_work_all_info WHERE work_id=work.work_id)\n"
            case "拍摄年龄逆序":
                order="ORDER BY (SELECT avg_age FROM v_work_all_info WHERE work_id=work.work_id) DESC\n"
            case "添加逆序":
                order="ORDER BY work.create_time DESC\n"
            case "添加顺序":
                order="ORDER BY work.create_time\n"
            case "更新时间逆序":
                order="ORDER BY work.update_time DESC\n"
            case "更新时间顺序":
                order="ORDER BY work.update_time\n"
        if not count:
            query +=f"{order} LIMIT ? OFFSET ?"#最后拼这个
            params.extend([page_size, offset])
        #logging.debug(f"WorkPageExecute SQL\n{query}")
        #logging.debug(f"{params}")

        with sqlite3.connect(f"file:{DATABASE}?mode=ro",uri=True) as conn:
            cursor = conn.cursor()
            if self.scope=="收藏库范围"or self.scope=="收藏未观看": attach_private_db(cursor)
            cursor.execute(query,params)
            results=cursor.fetchall()
            if self.scope=="收藏库范围"or self.scope=="收藏未观看": detach_private_db(cursor)

        return results


    def load_page(self, page_index: int, page_size: int) -> list[CoverCard]:
        """返回一个页面的 CoverCard 列表，在这里进行实际的构造"""
        data=self.load_data(page_index,page_size)
        if not data:
            return None
        result = []
        for serial_number, title, cover_path,tag_id,work_id,standard in data:
            color=CoverCard.backgroundcolor_from_tagid(tag_id)

            card = CoverCard(title, cover_path, serial_number,work_id,bool(standard),color=color,green_mode=self._green_mode)#这里实际上创造出了信号，安全模式要从这里开始弄

            result.append(card)
        return result
    


    @Slot()
    def refresh(self):
        self.lazy_area.reset()
        self.update_info()



    @Slot()
    def handle_scroll(self, value):
        direction = value - self.last_scroll_value

        if direction > 5:
            # 向下滚动，隐藏顶部
            if self.filter_widget.isVisible():
                self.filter_widget.hide()
                self.spacer_widget.hide()
                self.tagselector.hide()

        elif direction < -5:
            # 向上滚动，显示顶部
            if not self.filter_widget.isVisible():
                self.filter_widget.show()
                self.spacer_widget.show()
                self.tagselector.show()

        self.last_scroll_value = value

