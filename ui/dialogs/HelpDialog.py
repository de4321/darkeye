
from PySide6.QtWidgets import QPushButton, QHBoxLayout,QLabel,QVBoxLayout,QDialog,QFormLayout
from PySide6.QtCore import Signal,Qt
from config import ICONS_PATH
from PySide6.QtGui import QIcon

class HelpDialog(QDialog):
    #帮助窗口
    success=Signal(bool)#定义信号
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("帮助")
        self.setWindowIcon(QIcon(str(ICONS_PATH / "circle-question-mark.png")))
        datas=[
        {"row1":"H","row2":"帮助"},
        {"row1":"C","row2":"截图"},
        {"row1":"M","row2":"快速添加自慰记录"},
        {"row1":"W","row2":"快速添加作品"},
        {"row1":"A","row2":"快速添加晨勃记录"},
        {"row1":"L","row2":"快速添加做爱记录"},
        ]

        mainlayout=QFormLayout(self)
        for data in datas:
            mainlayout.addRow(data["row1"],QLabel(data["row2"]))
        mainlayout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)  
