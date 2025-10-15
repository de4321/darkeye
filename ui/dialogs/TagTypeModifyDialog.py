
from PySide6.QtWidgets import QPushButton, QHBoxLayout,QLabel,QVBoxLayout,QDialog,QFormLayout
from PySide6.QtCore import Signal,Qt
from config import ICONS_PATH
from PySide6.QtGui import QIcon
from ui.basic.TagTypeMoveableTableView import TagTypeMoveableTableView

class TagTypeModifyDialog(QDialog):
    #这个窗口最后将不会存在，改成在tag选择器上的更加自然的方式去改变，包括添加，删除，改变位置等。
    success=Signal(bool)#定义信号
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("修改标签类型与排序")
        self.setWindowIcon(QIcon(str(ICONS_PATH / "circle-question-mark.png")))
        self.resize(400,600)

        tagType_table_view=TagTypeMoveableTableView()
        tagType_table_view.update()
        layout=QVBoxLayout(self)
        layout.addWidget(tagType_table_view)

