import os,psutil,logging
from PySide6.QtWidgets import QWidget,QStackedWidget,QPushButton,QHBoxLayout, QVBoxLayout,QLineEdit,QLabel
from PySide6.QtCore import Qt,Signal,QTimer,Slot,QSize
from PySide6.QtGui import QIcon,QKeySequence,QShortcut,QPainter,QColor
from config import ICONS_PATH,set_size_pos,get_size_pos,is_max_window,set_max_window,is_first_lunch
from ui.pages import WorkPage,ManagementPage,StatisticsPage,ActressPage,AvPage,SingleActressPage,SingleWorkPage,ModifyActressPage,ActorPage,ModifyActorPage
from ui.pages import CoverBrowser
from core.recommendation.Recommend import recommendStart,randomRec
from qframelesswindow import FramelessWindow,StandardTitleBar
from ui.basic import IconPushButton,ToggleSwitch


class CustomTitleBar(StandardTitleBar):
    """ Custom title bar 这个titlebar要求空32个像素的空间出来"""
    help_signal=Signal()
    setting_signal=Signal()
    search_signal=Signal(str)#传递搜索信号

    def __init__(self, parent):
        super().__init__(parent)

        # customize the style of title bar button
        self.minBtn.setHoverColor(Qt.white)
        self.minBtn.setHoverBackgroundColor(QColor(0, 100, 182))
        self.minBtn.setPressedColor(Qt.white)
        self.minBtn.setPressedBackgroundColor(QColor(54, 57, 65))
        self.memlabel=QLabel()
        self.hBoxLayout.insertWidget(3, self.memlabel, 0, Qt.AlignLeft)
        self.hBoxLayout.insertStretch(4,1)
        self.search=QLineEdit()
        self.search.setFixedWidth(200)

        self.search.returnPressed.connect(lambda:self.search_signal.emit(self.search.text().strip()))

        self.hBoxLayout.insertWidget(5, self.search, 0, Qt.AlignLeft)
        
        self.greenbutton=ToggleSwitch(width=40,height=20)
        self.hBoxLayout.insertWidget(7,self.greenbutton,0,Qt.AlignLeft)
        self.greenbutton.setToolTip("切换安全模式")
        self.greenbutton.setChecked(False)
        from controller.GlobalSignalBus import global_signals

        self.greenbutton.toggled.connect(global_signals.green_mode_changed.emit)#转发信号

        

        self.btn_help=IconPushButton("circle-question-mark.png",iconsize=20,outsize=24)
        
        self.hBoxLayout.insertWidget(7,self.btn_help,0,Qt.AlignRight)
        self.btn_help.clicked.connect(self.help_signal.emit)

        self.btn_setting=IconPushButton("settings.png",iconsize=20,outsize=24)
        self.hBoxLayout.insertWidget(7,self.btn_setting,0,Qt.AlignRight)
        self.btn_setting.clicked.connect(self.setting_signal.emit)

        # use qss to customize title bar button
        self.maxBtn.setStyleSheet("""
            TitleBarButton {
                qproperty-hoverColor: white;
                qproperty-hoverBackgroundColor: rgb(0, 100, 182);
                qproperty-pressedColor: white;
                qproperty-pressedBackgroundColor: rgb(54, 57, 65);
            }
        """)
        
        #内存显示每秒刷新
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_memory)
        self.timer.start(1000)  # 每秒更新

    def update_memory(self):
        '''更新内存'''
        process = psutil.Process(os.getpid())
        mem = process.memory_info().rss / 1024 ** 2  # 转换为MB
        self.memlabel.setText(f"MEMORY: {mem:.2f} MB")

class MainWindow(FramelessWindow):
    '''主程序'''
    def __init__(self):
        super().__init__()
        self.setTitleBar(CustomTitleBar(self))
        self.titleBar:CustomTitleBar
        from config import APP_VERSION
        self.setWindowTitle("暗之眼 "+"V"+APP_VERSION)
        self.setWindowIcon(QIcon(str(ICONS_PATH / "jav.png"))) 
        
        self.setMinimumSize(1200,800)

        self.resize(1200,800)
        self.center()




        # 恢复上次打开时的窗口大小
        #QTimer.singleShot(0, self.restore_window_settings)
        # === 主容器 ===
        #self.central = QWidget()
        #self.setCentralWidget(self.central)

        # === 页面堆叠区域 ===
        self.stack = QStackedWidget()
        #self.stack.setStyleSheet("QStackedWidget {background-color: #181818;}")
        #self.stack.setStyleSheet("border: 2px solid red;")#测试框
        self.page_home=CoverBrowser(randomRec())
        self.page_management=ManagementPage()
        self.page_statistics=StatisticsPage()
        self.page_work=WorkPage()
        self.page_actress=ActressPage()
        self.page_actor=ActorPage()
        self.page_av=AvPage()
        self.page_single_actress=SingleActressPage()
        self.page_single_work=SingleWorkPage()
        self.page_modify_actress=ModifyActressPage()
        self.page_modify_actor=ModifyActorPage()

        self.stack.addWidget(self.page_home)
        self.stack.addWidget(self.page_management)
        self.stack.addWidget(self.page_statistics)
        self.stack.addWidget(self.page_work)
        self.stack.addWidget(self.page_actress)
        self.stack.addWidget(self.page_actor)
        self.stack.addWidget(self.page_av)
        self.stack.addWidget(self.page_single_actress)
        self.stack.addWidget(self.page_single_work)
        self.stack.addWidget(self.page_modify_actress)
        self.stack.addWidget(self.page_modify_actor)

        # 让 QStackedWidget 自动填满整个 self.central
        central_layout = QVBoxLayout(self)
        central_layout.setContentsMargins(0, 32, 0, 0)
        central_layout.setSpacing(0)
        central_layout.addWidget(self.stack)

        # 悬浮菜单栏
        self.MenuBar()

        #快捷键设置
        self.ShoutcutSetting()

        #集中跳转设置
        self.jump_connect()

    def center(self):
        """一个通用的居中方法"""
        # 获取代表屏幕的矩形（考虑多显示器情况，获取当前窗口所在的屏幕）
        screen_geometry = self.screen().availableGeometry()
        # 获取窗口自身的矩形
        window_geometry = self.frameGeometry()
        #print(window_geometry)
        # 将窗口矩形的中心点移动到屏幕矩形的中心点
        window_geometry.moveCenter(screen_geometry.center())
        # 将窗口的左上角移动到窗口矩形的左上角，实现居中
        self.move(window_geometry.topLeft())

    def paintEvent(self, event):
        painter = QPainter(self)
        #painter.fillRect(self.rect(), QColor("#ffffff"))  # 深灰色背景

    def MenuBar(self):
        # === 悬浮菜单栏 ===
        self.menu_bar = QWidget(self)
        #self.menu_bar.setGeometry(0, 0, self.width(), 50)
        
        self.menu_bar.setStyleSheet("""
                                    QWidget {
                                        background-color: rgba(0, 0, 0, 0);
                                        padding: 0px 0px;
                                        border-radius: 20px;
                                    }
                                    QWidget:hover {
                                        background-color: rgba(05, 0, 0, 200);
                                    }
                                    """)

        menu_layout = QHBoxLayout(self.menu_bar)
        menu_layout.setContentsMargins(10, 5, 10, 5)


        self.ql_logo=IconPushButton("jav_w.png",iconsize=40,outsize=40,hoverable=False)


        self.ql_logo.clicked.connect(lambda:self.switch_page(0))
        

        menu_layout.addWidget(self.ql_logo)

        # 定义菜单项（你可以轻松修改名称或添加图标、样式等）
        menu_items = [
            {"name": "管理"},
            {"name": "统计"},
            {"name": "影片"},
            {"name": "女优"},
            {"name": "男优"},
            {"name": "暗黑界"}
        ]
        self.buttons = []

        for idx, item in enumerate(menu_items):
            btn = QPushButton(item["name"])
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: transparent;
                    border: none;
                    padding: 0px 0px;
                    font-weight: bold; 
                    font-size: 16px; 
                    font-family: 'Microsoft YaHei';
                    text-align: center; /* 水平居中 */
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 40);
                }
                QPushButton:checked {
                background-color: rgba(255, 0, 0, 150);  /* 选中状态变红色 */
                }
            """)
            btn.clicked.connect(lambda _, i=idx: self.on_menu_button_clicked(i))
            btn.setFixedSize(80,50)
            self.buttons.append(btn)
            menu_layout.addWidget(btn)

        menu_layout.addStretch()
        #定义搜索框
        self.QLE=QLineEdit()
        self.QLE.setClearButtonEnabled(True)
        self.QLE.setMaximumWidth(200)
        self.QLE.setStyleSheet("""
            QLineEdit {
                color: white;  
                background-color: transparent;  /* 可选：背景透明或其他颜色 */
                border: 1px solid white;        /* 白色边框 */ 
            }
        """)
        #定义搜索按钮
        self.btn_search=QPushButton("搜索")
        self.btn_search.setCursor(Qt.PointingHandCursor)
        self.btn_search.setFixedSize(60,30)
        self.btn_search.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: red;
                border: none;
                font-weight: bold; 
                padding: 0px 0px;
                font-size: 13px; 
                border-radius: 10px;  
                text-align: center; /* 水平居中 */     
            }
        """)
        
        #menu_layout.addWidget(self.QLE)
        #menu_layout.addWidget(self.btn_search)
        self.menu_bar.raise_()# 确保悬浮在最上层

    def on_menu_button_clicked(self, index):
        # 取消其他按钮的选中状态
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)
        
        # 切换页面
        self.switch_page(index + 1)    

    def switch_page(self, index):
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index - 1)  # index-1，因为 index=0 是 logo，不对应按钮
        if index==0:
            self.menu_bar.setStyleSheet("""
                                QWidget {
                                    background-color: rgba(0, 0, 0, 0);  /* 半透明黑色背景 */
                                    padding: 0px 0px;
                                    border-radius: 20px;
                                }
                                QWidget:hover {
                                    background-color: rgba(0, 0, 0, 200);
                                }
                                """)
        else:
            self.menu_bar.setStyleSheet("""
                    QWidget {
                        background-color: rgba(0, 0, 0, 150);  /* 半透明黑色背景 */
                        padding: 0px 0px;
                        border-radius: 20px;
                    }
                    """)
        self.stack.setCurrentIndex(index)

    def resizeEvent(self, event):
        """菜单栏始终靠左上角，宽度为窗口一半"""
        super().resizeEvent(event)
        #self.stack.setGeometry(0, 0, self.width(), self.height())
        self.menu_bar.setGeometry(20, 42, self.width()-40, 60)

    def restore_window_settings(self):
        '''这个现在不需要了'''
        logging.debug("还原上次打开的窗口大小")
        if is_max_window():
            self.showMaximized()
        else:
            pass
            #还原窗口状态
            #size,pos=get_size_pos()
            #self.resize(size)
            #self.move(pos)

    def closeEvent(self, event):
        logging.info("--------------------程序关闭--------------------")
        set_max_window(self.isMaximized())
        #if not self.isMaximized():
            #set_size_pos(self.size(), self.pos())
        super().closeEvent(event)
        #数据库
        from core.database.connection import QSqlDatabaseManager
        #这个QSqlDatabase是长连接，最后关闭
        db_manager = QSqlDatabaseManager()
        db_manager.close_all()
        from core.database.db_utils import clear_temp_folder
        clear_temp_folder()#退出时清理临时数据


    def ShoutcutSetting(self):
        #快捷键设置
        logging.info("---快捷键设置---")
        self.shortcutM = QShortcut(QKeySequence("M"), self)
        self.shortcutM.activated.connect(self.page_management.openAddMasturbationDialog)

        self.shortcutW = QShortcut(QKeySequence("W"), self)
        self.shortcutW.activated.connect(self.page_management.openAddQuickWorkDialog)   

        self.shortcutA = QShortcut(QKeySequence("A"), self)
        self.shortcutA.activated.connect(self.page_management.openAddSexualArousalDialog) 

        self.shortcutL = QShortcut(QKeySequence("L"), self)
        self.shortcutL.activated.connect(self.page_management.openAddMakeLoveDialog) 

        self.shortcutH = QShortcut(QKeySequence("H"), self)
        self.shortcutH.activated.connect(self.on_help)

        self.shortcutC = QShortcut(QKeySequence("C"), self)
        self.shortcutC.activated.connect(self.handle_capture) 

        self.titleBar.help_signal.connect(self.on_help)#这个为什么没有提示
        self.titleBar.setting_signal.connect(self.on_setting)
        self.titleBar.search_signal.connect(self.search)

    @Slot(str)
    def search(self,serial_number):
        '''跳转并搜索'''
        logging.debug("跳转到作品页面")
        self.stack.setCurrentWidget(self.page_work)
        self.update_menu_highlight("影片")
        self.page_work.serial_number_input.setText(serial_number)



    def jump_connect(self):
        '''转发信号'''
        from controller.GlobalSignalBus import global_signals

        global_signals.modify_actress_clicked.connect(self.show_modify_actress)
        global_signals.modify_work_clicked.connect(self.show_modify_work_page)
        global_signals.work_clicked.connect(self.show_single_work_page)
        global_signals.actress_clicked.connect(self.show_single_actress)
        global_signals.tag_clicked.connect(self.search_work_by_tag)
        global_signals.modify_actor_clicked.connect(self.show_modify_actor)
        global_signals.actor_clicked.connect(self.show_single_actor)

    @Slot(int)
    def show_single_actor(self,actor_id:int):
        logging.debug("跳转到男优过滤页")
        self.stack.setCurrentWidget(self.page_work)
        self.update_menu_highlight("影片")
        from core.database.query import get_actor_allname
        namelist=get_actor_allname(actor_id)
        name=namelist[0].get("cn")
        self.page_work.actor_input.setText(name)

    @Slot(int)
    def show_modify_actor(self,actor_id:int):
        logging.debug("跳转到修改男优信息页")
        self.stack.setCurrentWidget(self.page_modify_actor)
        self.page_modify_actor.update(actor_id)
        self.update_menu_highlight("男优")

    @Slot(int)
    def search_work_by_tag(self,tag_id:int):
        '''跳转到作品搜索页面并添加tag_id'''
        logging.debug("跳转到作品页面")
        self.stack.setCurrentWidget(self.page_work)
        self.update_menu_highlight("影片")
        self.page_work.tagselector.load_with_ids([tag_id])

    @Slot(int)
    def show_modify_actress(self,actress_id:int):
        '''跳转到编辑女优界面'''
        self.stack.setCurrentWidget(self.page_modify_actress)
        self.page_modify_actress.update(actress_id)
        self.update_menu_highlight("女优")

    @Slot(int)
    def show_single_work_page(self,work_id:int):
        '''跳转到单个作品的界面'''
        self.stack.setCurrentWidget(self.page_single_work)
        self.page_single_work.update(work_id)
        self.update_menu_highlight("影片")

    @Slot(str)
    def show_modify_work_page(self,serial_number:str):#跳转到编辑界面
        '''跳转到管理的界面，然后展示出来'''
        self.stack.setCurrentWidget(self.page_management)
        self.page_management.tab_widget.setCurrentWidget(self.page_management.worktab)
        self.page_management.worktab.input_serial_number.setText(serial_number)
        self.page_management.worktab.btn_load_form_db.click()
        self.update_menu_highlight("管理")  

    @Slot(int)
    def show_single_actress(self,actress_id:int):
        '''跳转到单独的女优界面'''
        self.stack.setCurrentWidget(self.page_single_actress)
        self.page_single_actress.update(actress_id)
        self.update_menu_highlight("女优")  

    def update_menu_highlight(self, target_name: str):
        '''跳转后应的菜单栏也要更改状态'''
        for btn in self.menu_bar.findChildren(QPushButton):  # 或 QToolButton
            # 根据按钮的 objectName 或 text 来判断
            if btn.text() == target_name or btn.property("page") == target_name:
                btn.setChecked(True)
            else:
                btn.setChecked(False)

        self.menu_bar.setStyleSheet("""
        QWidget {
            background-color: rgba(0, 0, 0, 200);  /* 半透明黑色背景 */
            padding: 0px 0px;
            border-radius: 20px;
        }
        QWidget:hover {
            background-color: rgba(0, 0, 0, 200);
        }
        """)

    def handle_capture(self):
        logging.debug("触发快捷键C")
        cur_page=self.stack.currentWidget()
        from utils.utils import capture_full
        match cur_page:
            case self.page_home:
                capture_full(self.page_home)
            case self.page_work:  
                capture_full(self.page_work.lazy_area.widget())
            case self.page_actress:
                capture_full(self.page_actress.lazy_area.widget())
            case self.page_single_actress:
                capture_full(self.page_single_actress.single_actress_info)

    @Slot()
    def on_help(self):
        from ui.dialogs.HelpDialog import HelpDialog
        dialog=HelpDialog(self)
        dialog.exec()

    @Slot()
    def on_setting(self):
        from ui.dialogs import SettingDialog
        dialog=SettingDialog(self)
        dialog.exec()