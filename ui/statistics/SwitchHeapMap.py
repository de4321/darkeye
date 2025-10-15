from PySide6.QtWidgets import QHBoxLayout, QWidget, QLabel,QVBoxLayout,QPushButton,QStackedWidget,QScrollArea,QButtonGroup
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt,Signal,Slot
from ui.statistics.CalendarHeatmap import CalendarHeatmap
from core.database.query import get_record_count_by_year,get_record_by_year
from ui.basic import IconPushButton

class SwitchHeapMap(QWidget):
    def __init__(self):
        super().__init__()
        from core.database.query import get_record_early_year
        from datetime import datetime
        early_year=get_record_early_year()
        if not early_year:
            early_year=int(datetime.now().year)
        # 年份列表
        year_list = [str(x) for x in list(range(early_year, datetime.now().year + 1))]
        year_list = year_list[::-1]
        #year_list=[str(x) for x in list(range(2018,2026))]
        self.buttonlist=ButtonList(year_list)
        self.buttonlist.setFixedHeight(200)
        # 左右切换按钮
        self.btn_prev =IconPushButton("arrow-up.png")
        self.btn_next =IconPushButton("arrow-down.png")

        # 绑定按钮点击
        self.btn_prev.clicked.connect(lambda: self.switch(-1))
        self.btn_next.clicked.connect(lambda: self.switch(1))
                # 三个示例 QWidget
        self.calendar_heatmap_masturbation=CalendarHeatmap(year=2025,data=get_record_by_year(2025,0))
        self.calendar_heatmap_sex=CalendarHeatmap(year=2025,data=get_record_by_year(2025,1))
        self.calendar_heatmap_arousal=CalendarHeatmap(year=2025,data=get_record_by_year(2025,2))
        
        
        # QStackedWidget 管理多个 QWidget
        self.stack = QStackedWidget()
        self.stack.addWidget(self.calendar_heatmap_masturbation)
        self.stack.addWidget(self.calendar_heatmap_sex)
        self.stack.addWidget(self.calendar_heatmap_arousal)

        self.heatmap_names = [f"撸管{get_record_count_by_year(2025,0)}次在当年中", f"做爱{get_record_count_by_year(2025,1)}次在当年中", f"晨勃{get_record_count_by_year(2025,2)}次在当年中"]

        self.heatmap_name = QLabel(self.heatmap_names[0])
        # 布局
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.heatmap_name)
        btn_layout.addWidget(self.btn_prev)
        btn_layout.addWidget(self.btn_next)

        left_layout=QVBoxLayout()

        left_layout.addLayout(btn_layout)
        left_layout.addWidget(self.stack)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addLayout(left_layout)
        main_layout.addWidget(self.buttonlist)


        self.buttonlist.switch_year.connect(self.update)

    @Slot()
    def switch(self, step: int):
        """统一切换方法，step=-1 表示上一个，step=1 表示下一个"""
        index = (self.stack.currentIndex() + step) % self.stack.count()
        self.stack.setCurrentIndex(index)
        self.heatmap_name.setText(self.heatmap_names[index])
    
    @Slot(int)
    def update(self,year:int):
        '''根据年份去更新自身'''
        # 2️⃣ 更新三个热力图的数据

        self.calendar_heatmap_masturbation.update_data(year,get_record_by_year(year, 0))
        self.calendar_heatmap_sex.update_data(year,get_record_by_year(year, 1))
        self.calendar_heatmap_arousal.update_data(year,get_record_by_year(year, 2))

        # 3️⃣ 更新热力图名称
        self.heatmap_names = [
            f"撸管{get_record_count_by_year(year,0)}次在当年中",
            f"做爱{get_record_count_by_year(year,1)}次在当年中",
            f"晨勃{get_record_count_by_year(year,2)}次在当年中"
        ]
        # 保持当前 stack index 不变，刷新名字
        index = self.stack.currentIndex()
        self.heatmap_name.setText(self.heatmap_names[index])


class ButtonList(QScrollArea):
    switch_year=Signal(int)
    def __init__(self, items: list[str]):
        super().__init__()
        self.setWidgetResizable(True)  # 关键：内容自动适应
        self.setStyleSheet("""
            QScrollBar:vertical, QScrollBar:horizontal {
                width: 0px;
                height: 0px;
            }
        """)

        self.setFrameShape(QScrollArea.NoFrame)  # 去掉外框
        self.setAttribute(Qt.WA_TranslucentBackground)  # 支持透明

        # 滚动区里的实际内容容器，背景由这个决定
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.container.setAttribute(Qt.WA_TranslucentBackground)#这个透明很关键

        self.vbox = QVBoxLayout(self.container)
        self.vbox.setAlignment(Qt.AlignTop)   # 顶部对齐

        # 把滚动区
        self.setWidget(self.container)

        # 按钮组（保证单选）
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)  # 一次只能选一个
        self.group.idClicked.connect(self.on_button_clicked)

        # 初始化按钮
        self.populate(items)
        if self.group.buttons():
            first_btn = self.group.buttons()[0]
            first_btn.setChecked(True)
            self.on_button_clicked(self.group.id(first_btn))  # 手动触发
        

    def populate(self, items: list[str]):
        # 先清空旧内容（如果需要重复刷新）
        while self.vbox.count():
            item = self.vbox.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        for i, text in enumerate(items):
            btn = QPushButton(text)
            btn.setFixedSize(100,40)
            btn.setCheckable(True)  # 关键：可选中
            self.group.addButton(btn, i)
            self.vbox.addWidget(btn)
            # 应用现代样式
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    color: #333;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QPushButton:checked {
                    background-color: #0078d7;
                    color: white;
                    font-weight: bold;
                }
            """)
        # 撑开（保持紧凑但把多余空间留在底部）
        self.vbox.addStretch(1)

    def on_button_clicked(self, idx: int):
        self.switch_year.emit(int(self.group.button(idx).text()))