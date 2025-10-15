



from ..base.BaseMoveableTableModel import BaseMoveableTableModel
from ..base.BaseMoveableTableView import BaseMovableTableView
from core.database.query import get_tag_type
from core.database.update import update_tag_type
from utils.utils import sort_dict_list_by_keys
import logging

class TagTypeMoveableTableView(BaseMovableTableView):
    def __init__(self):
        super().__init__(BaseMoveableTableModel)

    def refresh_data(self):
        '''从数据库读数据并设置在model上'''
        data = get_tag_type()
        logging.debug(data)
        #order = ['actress_name_id','cn','jp','kana','en','level','redirect_actress_name_id']
        #data = sort_dict_list_by_keys(data, order)
        self.model.setNewData(data)
        self._apply_column_settings()

    def _apply_column_settings(self):
        """专属 UI 设置"""
        self.tableView.setColumnHidden(0, True)
        self.tableView.setColumnHidden(2, True)
        #self.tableView.setColumnHidden(6, True)
        #for i in range(6):
        #    self.tableView.setColumnWidth(i, 125)

    def save_data(self):
        '''与数据库交互'''
        logging.debug(self.model._data)
        from core.database.update import update_tag_type
        update_tag_type(self.model._data)


    def update(self):
        '''刷新，从数据库读取'''
        self.refresh_data()
