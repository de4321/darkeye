from PySide6.QtGui import QColor

class ShadowEffectMixin:
    def set_shadow(self, blur_radius=10, x_offset=0, y_offset=2, color=QColor(0, 0, 0, 80)):
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(blur_radius)
        shadow.setXOffset(x_offset)
        shadow.setYOffset(y_offset)
        shadow.setColor(color)
        self.setGraphicsEffect(shadow)