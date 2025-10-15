
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import Qt,Signal,QTimer
import logging
from ui.basic import OctImage 

class ActorAvatar(OctImage):
    '''正八边形的头像框，加上发射跳转信号的功能'''

    def __init__(self,image_path: str,actor_id:int, parent=None):
        super().__init__(image_path,parent)
        self._d=150#直径
        #self.setStyleSheet("border: 1px solid red; border-radius: 4px;")
        self._actor_id=actor_id

    def mouseReleaseEvent(self, event: QMouseEvent):
        from controller.GlobalSignalBus import global_signals
        if event.button() == Qt.MouseButton.RightButton:
            QTimer.singleShot(0, lambda: global_signals.modify_actor_clicked.emit(self._actor_id))
        if event.button() == Qt.MouseButton.LeftButton:
            logging.debug(f"准备跳转男优界面：ID:{self._actor_id}")

            QTimer.singleShot(0, lambda: global_signals.actor_clicked.emit(self._actor_id))

