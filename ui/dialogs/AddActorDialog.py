
from PySide6.QtWidgets import QPushButton,QLabel,QDialog,QLineEdit,QGridLayout
from PySide6.QtCore import Signal
from core.database.insert import InsertNewActor
from config import ICONS_PATH
from PySide6.QtGui import QIcon
from core.crawler.jump import jump_avdanyuwiki
from controller.MessageService import MessageBoxService

class AddActorDialog(QDialog):
    #添加新男优的输入对画框
    success=Signal(bool)#定义信号
    def __init__(self):
        super().__init__()
        self.setWindowTitle("添加新男优")
        self.setWindowIcon(QIcon(str(ICONS_PATH / "mars.png")))        
        self.resize(300, 150)
        self.msg=MessageBoxService(self)

        self.label1 = QLabel("男优中文名：")
        self.input1 = QLineEdit()
        self.label2 = QLabel("男优日文名：")
        self.input2 = QLineEdit()

        btn_commit = QPushButton("添加")
        btn_commit.clicked.connect(self.submit)

        btn_search = QPushButton("日文名搜索")
        btn_search.clicked.connect(lambda:jump_avdanyuwiki(self.input2.text()))

        layout = QGridLayout(self)
        layout.addWidget(self.label1,0,0)
        layout.addWidget(self.input1,0,1)
        layout.addWidget(self.label2,1,0)
        layout.addWidget(self.input2,1,1)
        layout.addWidget(btn_search)
        layout.addWidget(btn_commit)

    def submit(self):
        cnName = self.input1.text()
        jpName = self.input2.text()
        if jpName=="":
            self.msg.show_info("提示", "日文名禁止为空")
        else:
            if InsertNewActor(cnName,jpName):
                self.msg.show_info("添加新男优成功", f"中文名: {cnName}\n日文名: {jpName}")
                self.success.emit(True)
                from controller.GlobalSignalBus import global_signals
                global_signals.actor_data_changed.emit()
            else:
                self.msg.show_warning("添加新男优失败", f"重复男优")
                self.success.emit(False)#发出信号
            self.accept()  # 关闭对话框

