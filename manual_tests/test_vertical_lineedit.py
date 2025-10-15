# vertical_line_edit.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sys
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import QPainter, QFont, QColor, QKeyEvent, QGuiApplication, QClipboard
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from ui.basic.VerticalLineEdit import VerticalLineEdit

if __name__ == "__main__":
    from PySide6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QSizePolicy
    from PySide6.QtCore import QSize

    app = QApplication(sys.argv)
    main = QWidget()
    layout = QVBoxLayout(main)

    vline = VerticalLineEdit(placeholder="请输入")
    vline.setFixedWidth(40)
    layout.addWidget(QLabel("竖向输入示例："))
    layout.addWidget(vline)

    btn = QPushButton("打印内容")
    btn.clicked.connect(lambda: print("内容:", vline.text()))
    layout.addWidget(btn)

    main.resize(300, 500)
    main.show()
    sys.exit(app.exec())