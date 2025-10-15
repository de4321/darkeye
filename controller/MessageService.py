
from PySide6.QtWidgets import QMessageBox
from abc import ABC, abstractmethod

class IMessageService(ABC):
    @abstractmethod
    def show_info(self, title, message): ...

    @abstractmethod
    def show_warning(self,title,message):...

    @abstractmethod
    def show_critical(self,title,message):...

    @abstractmethod
    def ask_yes_no(self, title, message) -> bool: ...

class MessageBoxService(IMessageService):
    def __init__(self, parent=None):
        self.parent = parent
    def show_info(self, title, message):
        QMessageBox.information(self.parent, title, message)
        #logging.info(f"{title}: {message}")
    
    def show_warning(self,title,message):
        QMessageBox.warning(self.parent,title, message)
        #logging.warning(f"{title}: {message}")

    def show_critical(self,title,message):
        QMessageBox.critical(self.parent,title, message)

    def ask_yes_no(self, title, message)->bool:
        return QMessageBox.question(
            self.parent, title, message,
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes