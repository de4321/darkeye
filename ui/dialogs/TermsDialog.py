import sys
import json
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QDialog, QVBoxLayout,
    QLabel, QTextEdit, QPushButton, QHBoxLayout
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from config import ICONS_PATH

class TermsDialog(QDialog):
    """使用条款弹窗"""
    def __init__(self):
        super().__init__()

        self.setWindowTitle("用户使用条款")

        self.setWindowIcon(QIcon(str(ICONS_PATH / "jav.png")))   
        self.setModal(True)
        self.setFixedSize(500, 400)

        layout = QVBoxLayout(self)
        text = QLabel()
        text.setTextFormat(Qt.TextFormat.RichText)  # 启用富文本格式
        text.setWordWrap(True)                      # 自动换行
        text.setText(
            "<h3>欢迎使用 <b>暗之眼</b>！</h3>"
            "<p>—— 帮助你在黑暗界中睁开一只眼，探索广阔的暗黑界。</p>"

            "<p><b>在使用前，请仔细阅读以下使用条款：</b></p>"
            "<ol>"
            "<li>本软件仅供学习与研究用途。</li>"
            "<li>本软件为免费个人使用，未经许可不得用于商业用途。</li>"
            "<li>用户需自行承担使用风险。</li>"
            "<li>本软件不会收集任何数据，所有数据均存储在个人用户电脑上。</li>"
            "<li>开发者不对因使用本软件造成的任何损失负责。</li>"
            "<li>开发者不对数据丢失或损坏负责。</li>"
            "<li>本软件仅供 18 岁以上成年人使用。</li>"
            "<li>请不要在微信里传播软件。</li>"
            "<li>本条款的最终解释权归开发者所有。</li>"
            "</ol>"

            "<p>点击 <b>“我同意”</b> 表示您已阅读并接受以上内容。</p>"
        )

        layout.addWidget(text)

        button_layout = QHBoxLayout()
        self.agree_btn = QPushButton("我同意")
        self.disagree_btn = QPushButton("不同意")
        button_layout.addWidget(self.agree_btn)
        button_layout.addWidget(self.disagree_btn)
        layout.addLayout(button_layout)

        self.agree_btn.clicked.connect(self.accept)
        self.disagree_btn.clicked.connect(self.reject)