# crawler_thread.py
from PySide6.QtCore import QThread, Signal
import logging

class CrawlerThreadResult(QThread):
    #把爬虫操作全部放到后台线程
    #这个是带返回值的
    #这个东西怎么设计，让最底层的信号传到用户界面上
    finished = Signal(object)
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result=None
        

    def run(self):
        try:
            logging.info("开启一个后台线程")
            self.result = self.func(*self.args, **self.kwargs)
            self.finished.emit(self.result)#把爬虫后返回结果传回去
        except Exception as e:
            logging.warning(f"出错误:{e}")
            self.finished.emit(None)
