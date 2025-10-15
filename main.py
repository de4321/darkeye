import sys
from PySide6.QtWidgets import QApplication,QDialog
from ui.main_window import MainWindow
from core.utils import log_config #全局导入一次就可以用logging来打印了
import logging
from PySide6.QtCore import Qt
from core.database.init import init_database,init_private_db
from config import DATABASE,PRIVATE_DATABASE,is_first_lunch,set_first_luch
from core.database.migrations import check_and_upgrade_private_db,check_and_upgrade_public_db

def load_global_style():
    """加载全局样式表"""
    from pathlib import Path
    from config import QSS_PATH
    style = Path(QSS_PATH/"main.qss").read_text(encoding="utf-8")
    return style

if __name__ == "__main__":
    app = QApplication()

    if is_first_lunch():#判断是否是第一次启动
        from ui.dialogs import TermsDialog
        dialog=TermsDialog()
       
        if dialog.exec() == QDialog.Accepted:
            set_first_luch(False)
        else:
            set_first_luch(True)
            sys.exit(0)  # 拒绝则退出

    init_private_db()#先判断有无私库
    check_and_upgrade_private_db()#检查升级私有数据库
    check_and_upgrade_public_db()#检查升级公共数据库

    init_database(DATABASE,PRIVATE_DATABASE)

    logging.info("--------------------加载样式--------------------")
    app.setStyleSheet(load_global_style())
    logging.info("--------------------程序启动--------------------")
    window = MainWindow()
    window.show()
    logging.info("--------------------程序启动完成--------------------")
    sys.exit(app.exec())