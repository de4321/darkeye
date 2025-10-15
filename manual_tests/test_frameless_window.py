import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QSizePolicy
from PySide6.QtCore import QPropertyAnimation, QEasingCurve
import sys

from exp.FramelessWindow import FramelessWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FramelessWindow()
    window.show()
    sys.exit(app.exec())
