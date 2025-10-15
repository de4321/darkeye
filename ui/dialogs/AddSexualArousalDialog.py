from PySide6.QtWidgets import QPushButton,QLabel,QGridLayout,QDialog,QDateTimeEdit,QTextEdit
from PySide6.QtCore import Qt,QDateTime,QTime
from PySide6.QtGui import QIcon


from config import ICONS_PATH
from core.database.insert import insert_sexual_arousal_record
from controller import MessageBoxService

class AddSexualArousalDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("添加无意识性器官唤醒记录")
        self.setWindowIcon(QIcon(str(ICONS_PATH / "erection.png")))
        self.resize(300, 300)
        self.msg=MessageBoxService(self)

        #设置评价的控件
        label_comment=QLabel("事后评价")
        self.input_comment=QTextEdit()

        label_time=QLabel("时间")
        self.datetime_edit = QDateTimeEdit(self)
        self.datetime_edit.setDisplayFormat("yy-MM-dd HH:mm")  # 设置显示格式
        six_am_today = QDateTime.currentDateTime()
        six_am_today.setTime(QTime(6, 0))  # 设置为6:00:00
        self.datetime_edit.setDateTime(six_am_today)  # 设置初始时间为当天早上的6点
        self.datetime_edit.setCalendarPopup(True)  # 启用日历下拉
        self.datetime_edit.setMinimumTime(QTime(0, 0))       # 设置最小时间为 00:00
        self.datetime_edit.setMaximumTime(QTime(23, 59))     # 设置最大时间为 23:59
        self.datetime_edit.setTimeSpec(Qt.LocalTime)

        #提交
        btn_commit=QPushButton("提交记录")
        btn_commit.clicked.connect(self.commit)

        #分布
        main_layout=QGridLayout(self)
        main_layout.addWidget(label_time,0,0,Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(self.datetime_edit,0,1)
        main_layout.addWidget(label_comment,1,0,Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(self.input_comment,1,1)
        main_layout.addWidget(btn_commit,2,1)

    def commit(self):
        #提交数据，写入数据库内
        time=self.datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm")
        comment=self.input_comment.toPlainText()
        
        #非空检测后插入数据
        if insert_sexual_arousal_record(time,comment):
            self.msg.show_info("提示","成功提交一次记录")
            from controller.GlobalSignalBus import global_signals
            global_signals.sexarousal_changed.emit()
            self.accept()  # 关闭对话框
        else:
            self.msg.show_info("提示","提交失败")
        