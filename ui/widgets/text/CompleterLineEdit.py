from PySide6.QtWidgets import QLineEdit, QCompleter
from PySide6.QtCore import Qt,QEvent
from typing import Callable
from controller.GlobalSignalBus import global_signals

# 点击后把补全器list全弹出的类
class CompleterLineEdit(QLineEdit):
    '''支持传入加载函数的QLineEdit，带弹出补全的'''
    def __init__(self, loader_func: Callable[[], list] = None, parent=None):
        """
        初始化
        :param loader_func: 返回项目列表的函数
        :param parent: 父组件
        """
        super().__init__(parent)
        self.items = []  # 存储当前项目列表
        self.loader_func = loader_func  # 存储加载函数
        self.load_items()  # 初始加载项目
        self.installEventFilter(self)
        #self.setClearButtonEnabled(True)
        global_signals.work_data_changed.connect(self.reload_items)#连接全局信号

    def set_loader_func(self, loader_func: Callable[[], list]):
        """设置新的加载函数"""
        self.loader_func = loader_func
        self.reload_items()
    
    def load_items(self):
        """从数据源加载项目"""
        if self.loader_func is not None:
            self.items = self.loader_func()  # 使用传入的函数加载
            self.setup_completer()
    
    def setup_completer(self):
        """设置/重新设置自动完成器"""
        self.completer1 = QCompleter(self.items)
        self.completer1.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer1.setFilterMode(Qt.MatchContains)
        self.completer1.setCompletionMode(QCompleter.PopupCompletion)
        self.setCompleter(self.completer1)
    
    def reload_items(self):
        """重新加载项目并刷新自动完成"""
        self.load_items()
        #self.try_show_completer()
    
    def eventFilter(self, obj, event):
        if obj == self and event.type() == QEvent.FocusIn:
            self.try_show_completer()
        return super().eventFilter(obj, event)
    
    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        self.try_show_completer()
    
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.try_show_completer()
    
    def try_show_completer(self):
        """尝试显示自动完成弹出框"""
        text = self.text()
        self.completer1.setCompletionPrefix(text)
        if not self.completer1.popup().isVisible() and text == "":
            self.completer1.complete(self.rect())  # 显示完整列表