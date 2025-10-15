
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableView, QVBoxLayout, 
                               QHBoxLayout, QWidget, QPushButton, QAbstractItemView)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex,Signal,Slot

import logging
from ui.basic import IconPushButton
from .BaseMoveableTableModel import BaseMoveableTableModel

class BaseMovableTableView(QWidget):
    '''这个东西要抽象出通用的东西，而不是现在这个耦合非常的严重的'''
    def __init__(self,model_class:BaseMoveableTableModel):
        super().__init__()
        #self.setFixedWidth(550)
        # 创建模型和视图
        self.model:BaseMoveableTableModel = model_class()
        self.tableView = QTableView()
        self.tableView.setModel(self.model)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        # 设置编辑触发方式
        self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked |
                                     QAbstractItemView.EditTrigger.EditKeyPressed |
                                     QAbstractItemView.EditTrigger.AnyKeyPressed)

        # 创建按钮
        self.setup_buttons()
        
        # 设置布局

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(self.button_layout)
        main_layout.addWidget(self.tableView)
        
        # 连接信号
        self.tableView.selectionModel().selectionChanged.connect(self.update_button_state)
        self.update_button_state()

    def setup_buttons(self):
        """创建按钮"""
        self.btn_up = IconPushButton("triangle-up.png")
        self.btn_down = IconPushButton("triangle-down.png")
        self.btn_add = IconPushButton("list-plus.png")
        self.btn_delete = IconPushButton("list-x.png")
        self.btn_refresh = QPushButton("刷新")
        self.btn_save = QPushButton("保存")
        #self.btn_print = QPushButton("打印数据")
        
        
        self.btn_up.clicked.connect(self.move_up)
        self.btn_down.clicked.connect(self.move_down)
        self.btn_add.clicked.connect(self.add_row)
        self.btn_delete.clicked.connect(self.delete_row)
        self.btn_refresh.clicked.connect(self.refresh_data)
        self.btn_save.clicked.connect(self.save_data)
        #self.btn_print.clicked.connect(self.print_data)

        # 初始状态
        self.btn_up.setEnabled(False)
        self.btn_down.setEnabled(False)
        self.btn_delete.setEnabled(False)  # 只有选中行时才能删除

        # 按钮布局
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.btn_up)
        self.button_layout.addWidget(self.btn_down)
        self.button_layout.addWidget(self.btn_add)
        self.button_layout.addWidget(self.btn_delete)

        self.button_layout.addWidget(self.btn_refresh)
        self.button_layout.addWidget(self.btn_save)
        #self.button_layout.addWidget(self.btn_print)
        self.button_layout.addStretch()

    def move_up(self):
        """上移当前选中的行"""
        current_index = self.tableView.currentIndex()
        if current_index.isValid():
            current_row = current_index.row()
            if current_row > 0:  # 不是第一行才能上移
                self.model.moveRow(current_row, current_row - 1)
                # 更新选中行
                new_index = self.model.index(current_row - 1, 0)
                self.tableView.setCurrentIndex(new_index)

    def move_down(self):
        """下移当前选中的行"""
        current_index = self.tableView.currentIndex()
        if current_index.isValid():
            current_row = current_index.row()
            if current_row < self.model.rowCount() - 1:  # 不是最后一行才能下移
                self.model.moveRow(current_row, current_row + 1)
                # 更新选中行
                new_index = self.model.index(current_row + 1, 0)
                self.tableView.setCurrentIndex(new_index)


    def update_button_state(self):
        """更新按钮状态"""
        current_index = self.tableView.currentIndex()
        if current_index.isValid():
            current_row = current_index.row()
            self.btn_up.setEnabled(current_row > 0)
            self.btn_down.setEnabled(current_row < self.model.rowCount() - 1)
            self.btn_delete.setEnabled(True)  # 有选中行时可以删除
        else:
            self.btn_up.setEnabled(False)
            self.btn_down.setEnabled(False)
            self.btn_delete.setEnabled(False)

    def add_row(self):
        """添加新行"""
        self.model.addRow()
        # 选中新添加的行
        last_row = self.model.rowCount() - 1
        self.tableView.selectRow(last_row)
        # 滚动到新行
        self.tableView.scrollToBottom()

    def delete_row(self):
        """删除当前选中的行"""
        current_index = self.tableView.currentIndex()
        if current_index.isValid():
            row = current_index.row()
            self.model.removeRow(row)
            # 更新按钮状态
            self.update_button_state()

    def print_data(self):
        """打印当前模型中的所有数据"""
        print("\n当前表格数据:")
        print("-" * 50)
        # 打印每一行数据
        print(self.model._headers)
        for row in self.model._data:
            print(row)
        
        print("-" * 50)
