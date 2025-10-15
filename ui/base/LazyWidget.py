from PySide6.QtWidgets import QWidget

class LazyWidget(QWidget):
    '''惰性初始化'''
    def __init__(self, parent=None):
        super().__init__(parent)
        self._initialized = False

    def showEvent(self, event):
        if not self._initialized:
            self._lazy_load()
            self._initialized = True
        super().showEvent(event)


    def _lazy_load(self):
        """子类必须实现：初始化 UI"""
        raise NotImplementedError("子类必须实现 _init_ui()")