from PySide6.QtWidgets import  QLabel, QColorDialog
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt,Signal
from ui.basic.Effect import ShadowEffectMixin
import logging

class ColorPicker(QLabel,ShadowEffectMixin):
    colorChanged=Signal(str)
    def __init__(self, color: QColor = QColor("white")):
        # 初始化父类，并设置初始文本
        super().__init__(color.name())
        self._color = color

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 初始时设置颜色和文本
        self._update_color(self._color)

        # 直接点击 label 触发选色
        self.mousePressEvent = self.pick_color
        self.set_shadow()
    
    def get_color(self)->str:
        return self._color

    def set_color(self,color:str):
        self._update_color(QColor(color))

    def _update_color(self, new_color: QColor):
        from utils.utils import get_text_color_from_background
        """
        根据新颜色更新背景、文本和样式。
        """
        self._color = new_color
        #logging.debug(new_color)
        self.setText(self._color.name())
        text_color=get_text_color_from_background(new_color)
        
        # 使用单一的setStyleSheet调用，确保所有样式都生效
        self.setStyleSheet(
            f"background-color: {self._color.name()};"
            f"border-radius: 12px;"
            f"color: {text_color};"
            f"font-size: 24px;"
        )
        
        self.colorChanged.emit(new_color.name())
    
    def pick_color(self, event):
        # 弹出颜色选择对话框，使用当前颜色作为初始值
        selected_color = QColorDialog.getColor(self._color,None, "选择颜色")
        
        # 检查用户是否选择了有效的颜色
        if selected_color.isValid():
            # 调用更新方法
            self._update_color(selected_color)
            
