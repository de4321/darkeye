from PySide6.QtWidgets import QPushButton,QLabel,QDialog,QLineEdit,QGridLayout
from PySide6.QtCore import Signal
from core.database.insert import InsertNewActress
from config import ICONS_PATH
from PySide6.QtGui import QIcon
from core.crawler.jump import jump_minnanoav
from controller.MessageService import MessageBoxService

class AddActressDialog(QDialog):
    #添加新女优的输入对画框
    success=Signal()#定义信号，很重要，在任何的时候添加后要对actressSelector进行更改
    def __init__(self):
        super().__init__()
        self.setWindowTitle("添加新女优")
        self.setWindowIcon(QIcon(str(ICONS_PATH / "venus.png")))
        self.resize(300, 150)
        self.msg=MessageBoxService(self)

        self.label1 = QLabel("女优中文名：")
        self.input1 = QLineEdit()

        self.label2 = QLabel("女优日文名：")
        self.input2 = QLineEdit()

        btn_commit = QPushButton("添加")
        btn_commit.clicked.connect(self.submit)

        btn_search = QPushButton("日文名搜索")
        btn_search.clicked.connect(lambda:jump_minnanoav(self.input2.text()))

        layout = QGridLayout(self)
        layout.addWidget(self.label1,0,0)
        layout.addWidget(self.input1,0,1)
        layout.addWidget(self.label2,1,0)
        layout.addWidget(self.input2,1,1)
        layout.addWidget(btn_search)
        layout.addWidget(btn_commit)

    def submit(self):
        cnName = self.input1.text().strip()
        jpName = self.input2.text().strip()
        if jpName=="":
            self.msg.show_info("提示", "日文名禁止为空，爬虫会根据日文名爬取信息")
        #重复女优的测试
        #包括读取所有的重名，看一下有没有重名的，还有问题，如果两个女优的名字相同，这个怎么添加，在大量数据前这个一定会是一个问题，必然有两个女优的名字是相同的，虽然这些都是艺名
        else:
            if InsertNewActress(cnName,jpName):
                self.msg.show_info("添加新女优成功", f"中文名: {cnName}\n日文名: {jpName}")
                self.success.emit()
                from controller.GlobalSignalBus import global_signals
                global_signals.actress_data_changed.emit()
            else:
                self.msg.show_warning("添加新女优失败", f"重复女优")
            self.accept()  # 关闭对话框
