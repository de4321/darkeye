from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import Qt,Signal
from config import ACTRESSIMAGES_PATH,ICONS_PATH
from pathlib import Path
import logging
from ui.widgets.text.ClickableLabel import ClickableLabel
from ui.widgets.image.ActressAvatar import ActressAvatar

class ActressCard(QWidget):
    '''女优的照片+名字的组合'''
    def __init__(self, name: str="xxxx",image_path:str="anonymous.jpg",actress_id:int=1, parent=None):
        super().__init__(parent)
        self._d=150#直径
        #self.setStyleSheet("border: 1px solid red; border-radius: 4px;")
        self.setFixedWidth(150)
        self._actress_id=actress_id
        if image_path is None:
            self._path=Path(ICONS_PATH/"anonymous.jpg")
            #self._path=None
        else:
            self._path=Path(ACTRESSIMAGES_PATH/image_path)
        
        self.image_label = ActressAvatar(self._path,self._actress_id)
        self.name_label = ClickableLabel(name)
        self.name_label.setStyleSheet("""
            QLabel {
                font-size: 14px;           /* 字号 */
                font-family: 'Microsoft YaHei';      /* 字体 */
                font-weight: bold;         /* 粗体，可选 normal、bold、100-900 */
                color: grey;
                background-color: rgba(0, 0, 0, 0);
            }                      
        """)

        self.image_label.setFixedSize(self._d, self._d)  # 封面尺寸
        self.image_label.setAlignment(Qt.AlignCenter)

        self.name_label.setAlignment(Qt.AlignCenter)
        #self.name_label.setFixedWidth(150)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.image_label)
        layout.addWidget(self.name_label,alignment=Qt.AlignCenter)

    def update_data(self,name: str,image_path: str,actress_id:int):
        '''外部控制的更新数据'''
        self.name_label.setText(name)
        self.image_label._actress_id=actress_id
        self.image_label.update_image(image_path)