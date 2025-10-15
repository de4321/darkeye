import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#---------------------------------------------------------------------------------------------------
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QScrollArea, QPushButton
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import sys
from PySide6.QtSql import QSqlTableModel
from PySide6.QtWidgets import QApplication, QTableView, QSplitter
from PySide6.QtCore import Qt
from core.database.init import create_connection,init_private_db
#主从模型处理1对N 中的1端的问题

app = QApplication([])
if not create_connection():#连接数据库，连不上直接退出
    sys.exit(-1)
# 主表模型（女优）
actress_model = QSqlTableModel()
actress_model.setTable("actress")
actress_model.select()

# 子表模型（别名）
name_model = QSqlTableModel()
name_model.setTable("actress_name")

# 主表视图
actress_view = QTableView()
actress_view.setModel(actress_model)

# 子表视图
name_view = QTableView()
name_view.setModel(name_model)

# 联动：选中一个女优时，刷新别名表
def on_actress_selected(index):
    if not index.isValid():
        return
    actress_id = actress_model.data(actress_model.index(index.row(), 0))  # 0 列是 id
    name_model.setFilter(f"actress_id = {actress_id}")
    name_model.select()

actress_view.selectionModel().currentRowChanged.connect(on_actress_selected)

# 布局
splitter = QSplitter(Qt.Horizontal)
splitter.addWidget(actress_view)
splitter.addWidget(name_view)
splitter.show()

app.exec()
