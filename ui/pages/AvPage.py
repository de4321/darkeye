
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QWidget, QLabel,QVBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from ui.base import LazyWidget

class AvPage(LazyWidget):
    def __init__(self):
        super().__init__()
        
    def _lazy_load(self):
        mainlayout = QVBoxLayout(self)
        mainlayout.setContentsMargins(0, 0, 0, 0)

        mainlayout.addSpacing(70)

        self.label = QLabel("AV知识科普页面")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(f"background-color: grey; color: white; font-size: 28px;")
        mainlayout.addWidget(self.label)

