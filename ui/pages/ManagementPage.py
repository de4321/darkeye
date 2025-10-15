from PySide6.QtWidgets import QHBoxLayout, QWidget,QVBoxLayout,QToolButton,QFileDialog,QLabel,QSizePolicy,QTabWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt,Slot
from pathlib import Path
from config import ICONS_PATH,DATABASE,DATABASE_BACKUP_PATH,PRIVATE_DATABASE,PRIVATE_DATABASE_BACKUP_PATH
from ui.pages.TagManagement import TagManagement
from ui.pages.SearchTable import SearchTable
from .AddWorkTabPage3 import AddWorkTabPage3
import logging
from .UpdateManyTabPage import UpdateManyTabPage
from controller.MessageService import MessageBoxService
from .StudioManagementPage import StudioManagementPage
from .ManagementTable import ManagementTable
from .RecycleBinPage import RecycleBinPage

class ManagementPage(QWidget):
    '''管理面板，里面嵌套了其他很多的功能'''
    def __init__(self):
        super().__init__()
        #self.setStyleSheet("border: 2px solid red;")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        mainlayout = QVBoxLayout(self)
        mainlayout.setContentsMargins(0, 0, 0, 0)
        mainlayout.addSpacing(70)

        self.msg=MessageBoxService(self)
        # 工具栏区域
        toolbar = self.create_toolbar()
        mainlayout.addWidget(toolbar)

        # 主内容区域
        #tabwidget
        self.tab_widget=QTabWidget()
        #self.tab_widget.setMovable(True)
        self.worktab=AddWorkTabPage3()
        self.searchtable=SearchTable()
        self.tag_manage=TagManagement()
        self.rubbish=RecycleBinPage()
        self.updatemany=UpdateManyTabPage()
        self.studio_management=StudioManagementPage()
        self.g_management=ManagementTable()

        mainlayout.addWidget(self.tab_widget)
        self.tab_widget.addTab(self.worktab,"添加/修改作品")
        self.tab_widget.addTab(self.tag_manage,"作品标签管理")
        self.tab_widget.addTab(self.updatemany,"批量操作")
        self.tab_widget.addTab(self.studio_management,"制作商管理")
        self.tab_widget.addTab(self.searchtable,"汇总查询表")
        self.tab_widget.addTab(self.g_management,"综合管理")
        self.tab_widget.addTab(self.rubbish,"回收站")

    #工具栏
    def create_toolbar(self):
        #工具栏
        toolbar = QWidget()
        toolbar.setFixedHeight(30)

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(5, 0, 2, 0)
        layout.setSpacing(3)

        # 工具按钮
        btn_backupDB = QToolButton()
        btn_backupDB.setText("备份公共数据库")
        btn_backupDB.setToolTip("将现有的数据库打上时间戳备份")
        btn_backupDB.setIcon(QIcon(str(ICONS_PATH / "database.png")))
        btn_backupDB.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        btn_restoreDB = QToolButton()
        btn_restoreDB.setText("还原公共数据库")
        btn_restoreDB.setToolTip("在备份的数据库里选择一个数据还原，覆盖现有的数据库")
        btn_restoreDB.setIcon(QIcon(str(ICONS_PATH / "database.png")))
        btn_restoreDB.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        btn_backupDB2 = QToolButton()
        btn_backupDB2.setText("备份私有数据库")
        btn_backupDB2.setToolTip("将现有的数据库打上时间戳备份")
        btn_backupDB2.setIcon(QIcon(str(ICONS_PATH / "database.png")))
        btn_backupDB2.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        btn_restoreDB2 = QToolButton()
        btn_restoreDB2.setText("还原私有数据库")
        btn_restoreDB2.setToolTip("在备份的数据库里选择一个数据还原，覆盖现有的数据库")
        btn_restoreDB2.setIcon(QIcon(str(ICONS_PATH / "database.png")))
        btn_restoreDB2.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        btn_shiftDB = QToolButton()
        btn_shiftDB.setEnabled(False)
        btn_shiftDB.setText("切换数据库")
        btn_shiftDB.setToolTip("选择一个数据库切换")
        btn_shiftDB.setIcon(QIcon(str(ICONS_PATH / "database.png")))
        btn_shiftDB.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        btn_addWork = QToolButton()
        btn_addWork.setText("快速记录番号")
        btn_addWork.setToolTip("快速记录番号")
        btn_addWork.setIcon(QIcon(str(ICONS_PATH / "film.png")))
        btn_addWork.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        btn_addAdress=QToolButton()
        btn_addAdress.setText("添加新女优")
        btn_addAdress.setToolTip("手动添加女优，至少需要输入一个准确的中文名与日文名，要求日文名在MinnanoAV能找到")
        btn_addAdress.setIcon(QIcon(str(ICONS_PATH / "venus.png")))
        btn_addAdress.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        btn_reNewAdress=QToolButton()
        btn_reNewAdress.setText("更新女优数据")
        btn_reNewAdress.setToolTip("根据标记自动更新女优的数据，包括身高，三维，罩杯，出生年月，出道日期，照片")
        btn_reNewAdress.setIcon(QIcon(str(ICONS_PATH / "refresh-cw.png")))
        btn_reNewAdress.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        btn_addMasturbate=QToolButton()
        btn_addMasturbate.setText("添加自慰记录(M)")
        btn_addMasturbate.setToolTip("添加自慰记录，包括时间，满意度，以及感受")
        btn_addMasturbate.setIcon(QIcon(str(ICONS_PATH / "masturbate.png")))
        btn_addMasturbate.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        btn_addSex=QToolButton()
        btn_addSex.setText("添加做爱记录(L)")
        btn_addSex.setToolTip("添加做爱记录，包括时间，满意度，以及感受")
        btn_addSex.setIcon(QIcon(str(ICONS_PATH / "sex.png")))
        btn_addSex.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        btn_addGenitalAarousal=QToolButton()
        btn_addGenitalAarousal.setText("添加性器官唤起记录(A)")
        btn_addGenitalAarousal.setToolTip("添加睡眠相关的性器官唤起记录，包括男性的晨勃起，或者女性的阴蒂充血勃起")
        btn_addGenitalAarousal.setIcon(QIcon(str(ICONS_PATH / "erection.png")))
        btn_addGenitalAarousal.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        btn_addActor=QToolButton()
        btn_addActor.setText("添加新男优")
        btn_addActor.setToolTip("手动添加男优，至少需要输入一个准确的中文名与日文名")
        btn_addActor.setIcon(QIcon(str(ICONS_PATH / "mars.png")))
        btn_addActor.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)



        # 事件连接
        btn_addAdress.clicked.connect(self.openAddActressDialog)
        btn_reNewAdress.clicked.connect(self.searchActressinfo)
        btn_addWork.clicked.connect(self.openAddQuickWorkDialog)
        btn_addMasturbate.clicked.connect(self.openAddMasturbationDialog)
        btn_addSex.clicked.connect(self.openAddMakeLoveDialog)
        btn_addGenitalAarousal.clicked.connect(self.openAddSexualArousalDialog)
        btn_addActor.clicked.connect(self.openAddActorDialog)

        btn_backupDB.clicked.connect(lambda:self.backup_db("public"))
        btn_restoreDB.clicked.connect(lambda:self.restoreDB("public"))
        btn_backupDB2.clicked.connect(lambda:self.backup_db("private"))
        btn_restoreDB2.clicked.connect(lambda:self.restoreDB("private"))

        # 右侧空白拉伸
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        #layout.addWidget(btn_shiftDB)
        layout.addWidget(btn_backupDB)
        layout.addWidget(btn_restoreDB)
        layout.addWidget(btn_backupDB2)
        layout.addWidget(btn_restoreDB2)

        layout.addWidget(btn_addWork)
        layout.addWidget(btn_addAdress)
        layout.addWidget(btn_reNewAdress)
        layout.addWidget(btn_addActor)
        layout.addWidget(btn_addMasturbate)
        layout.addWidget(btn_addSex)
        layout.addWidget(btn_addGenitalAarousal)

        layout.addWidget(spacer)

        toolbar.setStyleSheet("""
            QToolButton {
                padding: 0px 0px;
                background: #F0F0F0;
                border: 1px solid #ccc;
                border-radius: 0px;
            }
            QToolButton:hover {
                background: #D8EAF9;
            }
        """)
        return toolbar

    @Slot()
    def openAddActorDialog(self):
        from ui.dialogs import AddActorDialog
        dialog=AddActorDialog()
        dialog.exec()

    @Slot()
    def openAddSexualArousalDialog(self):
        from ui.dialogs import AddSexualArousalDialog
        dialog=AddSexualArousalDialog()
        dialog.exec()

    @Slot()
    def openAddMasturbationDialog(self):
        from ui.dialogs import AddMasturbationDialog
        dialog=AddMasturbationDialog()
        dialog.exec()
    
    @Slot()
    def openAddActressDialog(self):
        from ui.dialogs import AddActressDialog
        dialog = AddActressDialog()
        dialog.success.connect(self.worktab.actressselector.handle_actress_result)
        dialog.exec()  # 模态显示对话框，阻塞主窗口直到关闭

    @Slot()
    def openAddQuickWorkDialog(self):
        from ui.dialogs import AddQuickWork
        dialog=AddQuickWork()
        dialog.exec()

    @Slot()
    def openAddMakeLoveDialog(self):
        from ui.dialogs import AddMakeLoveDialog
        dialog=AddMakeLoveDialog()
        dialog.exec()

    @Slot()
    def searchActressinfo(self):
        #开始后台线程
        from core.crawler.SearchActressInfo import actress_need_update,SearchActressInfo
        from core.crawler.CrawlerThreadResult import CrawlerThreadResult
        if actress_need_update():
            self.thread:CrawlerThreadResult=CrawlerThreadResult(SearchActressInfo)#传一个函数名进去
            self.thread.finished.connect(self.on_result)
            self.thread.start()
            self.msg.show_info("开始更新","开始更新，可能需要一段时间")
        else:
            self.msg.show_info("提示","没有要更新的女优")

    @Slot(object)
    def on_result(self,result:str):#Qsignal回传信息
        self.msg.show_info("提示",result)
        
    @Slot()
    def restoreDB(self,access_level:str):
        #选择一个备份的数据库还原
        #这个目前有，这个是直接覆盖，风险问题，数据库在写入，后面再改全局单例数据库管理器来管理所有的连接
        if access_level=="public":
            backup_path=DATABASE_BACKUP_PATH
            target_path=DATABASE
        elif access_level=="private":
            backup_path=PRIVATE_DATABASE_BACKUP_PATH
            target_path=PRIVATE_DATABASE     
        else:
            logging.info("错误，未选择等级")

        from core.database.backup_utils import restore_database,restore_backup_safely
        file_path, _ = QFileDialog.getOpenFileName(
            self,               # 父组件
            "选择一个数据库",      # 对话框标题
            str(backup_path),                 # 起始路径
            "*.db"  # 文件过滤器
        )

        if not file_path:
            return
    
        if not self.msg.ask_yes_no("确认恢复","是否用该备份覆盖现有数据库？操作不可撤销！"):
            return

        success = restore_backup_safely(Path(file_path), target_path)
        if success:
            self.msg.show_info("恢复成功", "数据库恢复完成。")
        else:
            self.msg.show_critical("恢复失败", "数据库恢复失败，请检查文件是否有效。")

    @Slot()
    def backup_db(self,access_level:str):
        '''备份数据库'''
        if access_level=="public":
            backup_path=DATABASE_BACKUP_PATH
            target_path=DATABASE
        elif access_level=="private":
            backup_path=PRIVATE_DATABASE_BACKUP_PATH
            target_path=PRIVATE_DATABASE     
        else:
            logging.info("错误，未选择等级")

        from core.database.backup_utils import backup_database
        try:
            path=backup_database(target_path,backup_path)
            self.msg.show_info("备份成功",f"备份路径{path}")
        except Exception as e:
            self.msg.show_critical(self,"备份失败",f"{str(e)}")

