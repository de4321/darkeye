from PySide6.QtWidgets import QWidget,QHBoxLayout,QLabel
from PySide6.QtCore import Qt, Signal

class HeartLabel(QLabel):

    clicked = Signal(int)
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        self.setText("🤍")
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(40, 40)
        self.setStyleSheet("font-size: 24px;")
        self.setAttribute(Qt.WA_Hover, True)
        self.setCursor(Qt.PointingHandCursor)

    def enterEvent(self, event):
        self.parent().hover_index = self.index
        self.parent().update_hearts()
        return super().enterEvent(event)

    def leaveEvent(self, event):
        self.parent().hover_index = -1
        self.parent().update_hearts()
        return super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent().rating = self.index
            self.parent().update_hearts()
            self.clicked.emit(self.index)


class HeartRatingWidget(QWidget):
    '''爱心打分控件'''
    rating_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rating = 0
        self.hover_index = -1
        self.setMouseTracking(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)  # 去掉控件之间的空隙
        self.hearts = []
        for i in range(1, 6):
            heart = HeartLabel(i, self)
            heart.clicked.connect(self.emit_rating)
            self.hearts.append(heart)
            layout.addWidget(heart)

    def get_rating(self):
        return self.rating
    
    def emit_rating(self, value):
        self.rating_changed.emit(value)

    def update_hearts(self):
        active = self.hover_index if self.hover_index != -1 else self.rating
        for heart in self.hearts:
            heart.setText("❤️" if heart.index <= active else "🤍")

