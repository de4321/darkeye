import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#---------------------------------------------------------------------------------------------------
from PySide6.QtWidgets import (
    QApplication, QWidget, QScrollArea, QVBoxLayout,
    QPushButton, QButtonGroup, QLabel
)
from PySide6.QtCore import Qt
import sys
from ui.statistics.SwitchHeapMap import ButtonList


if __name__ == "__main__":
    app = QApplication(sys.argv)
    data = [f"{i}" for i in range(1, 21)]
    w = ButtonList(data)
    w.resize(320, 480)
    w.setWindowTitle("单选高亮按钮列表示例")
    w.show()
    sys.exit(app.exec())
