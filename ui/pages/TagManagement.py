
from PySide6.QtWidgets import  QVBoxLayout, QLabel,QWidget,QHBoxLayout,QLineEdit,QTextEdit,QPushButton,QComboBox,QFormLayout,QLayout,QGroupBox,QTableView,QSizePolicy,QDialog
from PySide6.QtCore import Qt,QObject,Signal,Property,Slot,SignalInstance
from PySide6.QtSql import QSqlRelation,QSqlRelationalTableModel,QSqlTableModel,QSqlRelationalDelegate,QSqlQueryModel,QSqlQuery,QSqlDatabase

from ui.widgets.selectors.TagSelector4 import TagSelector4
from ..widgets.text.CompleterLineEdit import CompleterLineEdit
from core.database.query import get_tag_name,get_tag_type_dict,get_unique_tag_type
from ..basic.ColorPicker import ColorPicker
import logging
from ui.base import LazyWidget
from controller.MessageService import MessageBoxService,IMessageService
from ui.widgets.text.VerticalTagLabel2 import VerticalTagLabel,VShowTagLabel
from ui.basic import EditableTableView
from ui.dialogs import TagTypeModifyDialog
from controller.GlobalSignalBus import global_signals

class SignalTagView(QWidget):
    '''展示标签的容器'''
    def __init__(self):
        super().__init__()
        
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedWidth(60)
        self.setMinimumHeight(100)
        self.setObjectName("SignalTagView")  # 给外层起名字
        self.setStyleSheet("""
            #SignalTagView {
                border-radius: 12px;
                background-color: white;
                border: 3px dashed #cccccc;
            }
        """)
        self.mainlayout=QHBoxLayout(self)

class Model():
    '''纯放数据的model'''
    def __init__(self):
        self._tag_id:int =None
        self._tag_name:str= ""
        self._tag_color:str = ""
        self._tag_detail:str = ""
        self._tag_redirect_tag_id:int =None
        self._tag_type_id:int = None
        self._tag_alias:list[dict]=[]

    def to_dict(self):
        return {
            "tag_id": self._tag_id,
            "tag_name":self._tag_name,
            "tag_type_id":self._tag_type_id,
            "tag_color":self._tag_color,
            "tag_detail":self._tag_detail,
            "tag_redirect_tag_id":self._tag_redirect_tag_id,
            "tag_alias":self._tag_alias
        }

class ViewModel(QObject):
    tag_id_changed=Signal(int)
    tag_name_changed=Signal(str)
    tag_type_id_changed=Signal(int)
    tag_color_changed=Signal(str)
    tag_detail_changed=Signal(str)
    tag_redirect_tag_id=Signal(int|None)
    tag_alias_changed=Signal(list)
    after_delete=Signal()
    load_tag_selector=Signal(list)#发射要加载的信号

    def __init__(self, model=None,message_service:IMessageService=None):
        super().__init__()
        self.model:Model = model
        self.msg=message_service
        #self.tag_name_changed.connect(self.on_tag_name_changed)
        #tag_name与tag_name_id的映射关系存在这里面
        self.tag_type_map=get_tag_type_dict()

    def _noop(self):
        return None
    def get_tag_id(self)->int: return self.model._tag_id
    def set_tag_id(self,value:int):
        if self.model._tag_id != value:
            self.model._tag_id = value
            self.tag_id_changed.emit(value)

    tag_id=Property(int,get_tag_id,set_tag_id,notify=tag_id_changed)

    def get_tag_name(self)->str: return self.model._tag_name
    def set_tag_name(self,value:str):
        if self.model._tag_name != value.strip():
            self.model._tag_name = value.strip()
            self.tag_name_changed.emit(value)
    tag_name=Property(str,get_tag_name,set_tag_name,notify=tag_name_changed)   

    # --- tag_type property ---
    def get_tag_type_id(self) -> int:
        return self.model._tag_type_id
    def set_tag_type_id(self, value: int):
        clean_value = value
        if self.model._tag_type_id != clean_value:
            self.model._tag_type_id = clean_value
            logging.debug("设置model中的tag_type_id")
            self.tag_type_id_changed.emit(clean_value)

    tag_type_id = Property(int, get_tag_type_id, set_tag_type_id, notify=tag_type_id_changed)

    # --- tag_color property ---
    def get_tag_color(self) -> str:
        return self.model._tag_color
    def set_tag_color(self, value: str):
        clean_value = value.strip()
        if self.model._tag_color != clean_value:
            self.model._tag_color = clean_value
            self.tag_color_changed.emit(clean_value)

    tag_color = Property(str, get_tag_color, set_tag_color, notify=tag_color_changed)

    # --- tag_detail property ---
    def get_tag_detail(self) -> str:
        return self.model._tag_detail
    def set_tag_detail(self, value: str):
        clean_value = value.strip()
        if self.model._tag_detail != clean_value:
            self.model._tag_detail = clean_value
            self.tag_detail_changed.emit(clean_value)

    tag_detail = Property(str, get_tag_detail, set_tag_detail, notify=tag_detail_changed)

    # --- tag_redirect_tag_id property ---
    def get_tag_redirect_tag_id(self) -> int | None:
        return self.model._tag_redirect_tag_id
    def set_tag_redirect_tag_id(self, value: int | None):
        if self.model._tag_redirect_tag_id != value:
            self.model._tag_redirect_tag_id = value
            self.tag_redirect_tag_id.emit(value)

    # Corrected Property declaration
    tag_redirect_tag_id = Property(int, get_tag_redirect_tag_id, set_tag_redirect_tag_id, notify=tag_redirect_tag_id)

    def get_tag_alias(self)->list[dict]:
        return self.model._tag_alias
    def set_tag_alias(self,value:list[dict]):
        from utils.utils import sort_dict_list_by_keys
        order=['tag_id','tag_name','redirect_tag_id']
        value=sort_dict_list_by_keys(value,order)
        if self.model._tag_alias!=value:
            self.model._tag_alias=value
            self.tag_alias_changed.emit(value)
    tag_alias=Property(list,get_tag_alias,set_tag_alias,notify=tag_alias_changed)


    def load_tag_by_id(self,tag_id):
        '''通过tag_id加载tag的信息'''
        from core.database.query import get_taginfo_by_id,get_alias_tag
        data=get_taginfo_by_id(tag_id)
        alias_tag=get_alias_tag(tag_id)
        logging.debug(alias_tag)
        #logging.debug(data)
        self.set_tag_id(data["tag_id"])
        self.set_tag_name(data["tag_name"])
        self.set_tag_type_id(data["tag_type_id"])
        self.set_tag_color(data["color"])
        data["detail"] = data["detail"] or ""
        self.set_tag_detail(data["detail"])
        self.set_tag_redirect_tag_id(data["redirect_tag_id"])
        self.set_tag_alias(alias_tag)


    @Slot()
    def commit(self):
        '''提交'''
        if self.get_tag_name()=="":
            self.msg.show_info("提示","标签名字不能为空")
            return
        if self.get_tag_id() is not None:#修改状态
            self._update_tag()
        else:
            self._insert_new_tag()
        
    def _update_tag(self):
        '''更新状态'''
        data:dict=self.model.to_dict()
        from core.database.update import update_tag
        if update_tag(**data):
            self.msg.show_info("更新Tag信息成功",f"tag_id: {data["tag_id"]}")
            global_signals.tag_data_changed.emit()#发射标签数据变更信号
            return True
        else:
            self.msg.show_warning("更新tag信息失败",f"未知原因")
            return False

    def _insert_new_tag(self):
        '''插入新的tag'''
        logging.debug("插入新tag")
        data:dict=self.model.to_dict()
        del data["tag_id"]
        from core.database.insert import insert_tag
        from core.database.query import get_tagid_by_keyword
        success,message=insert_tag(**data)
        if success:
            self.msg.show_info(f"添加新tag成功",f"tag_name: {data["tag_name"]}")
            global_signals.tag_data_changed.emit()#发射标签数据变更信号
            #这里要重新加载新的tag
            tag_id_list=get_tagid_by_keyword(data["tag_name"],match_hole_word=True)
            if tag_id_list:
                tag_id=tag_id_list[0]
                self.load_tag_selector.emit([tag_id])#发射要加载的信号
            return True
        else:
            self.msg.show_warning("插入新tag失败",f"{message}")
            return False


    @Slot()
    def delete(self):
        '''删除当前选中的tag'''
        if self.get_tag_id() is not None:
            from core.database.delete import delete_tag
            success,message=delete_tag(self.get_tag_id())
            if success:
                self.msg.show_info("删除成功",message)
                self.after_delete.emit()
                self._clear_all_info()

            else:
                self.msg.show_warning("删除失败",message)


    def _clear_all_info(self):
        '''清空所有的信息'''
        self.set_tag_name("")
        self.set_tag_color("#cccccc")
        self.set_tag_detail("")
        self.set_tag_id(None)
        self.set_tag_redirect_tag_id(None)
        self.set_tag_type_id(self.find_tag_type_id_by_value("默认分类"))
        self.set_tag_alias([])
        
    def find_tag_type_id_by_value(self,target_value):
        """根据值查找第一个对应的键"""
        return next((key for key, value in self.tag_type_map.items() if value == target_value), None)


class TagManagement(LazyWidget):
    '''tag 管理的page'''
    def __init__(self, parent=None):
        super().__init__(parent)

    def _lazy_load(self):
        logging.info("----------加载Tag管理界面----------")
        self.model=Model()
        self.vm = ViewModel(self.model,MessageBoxService(self))

        #第一列
        self.leftwidget=QWidget()
        self.leftwidget.setMaximumWidth(400)
        leftlayout=QVBoxLayout(self.leftwidget)

        #self.tag_show=SignalTagView()
        self.tag_liveshow=SignalTagView()

        self.taglabel=None#默认的展示的
        self.livetaglabel=None

        self.alias_view=EditableTableView()

        show_group = QGroupBox("标签展示")
        layout0=QHBoxLayout(show_group)
        #layout0.addWidget(self.tag_show)
        layout0.addWidget(self.tag_liveshow)

        self.tag_name=QLineEdit()
        self.tag_type=QComboBox()
        self.tag_type.addItems(get_unique_tag_type())


        self.color=ColorPicker()
        self.color.setMaximumHeight(40)
        self.detail=QLineEdit()
        self.btn_commit=QPushButton("提交")
        self.btn_delete=QPushButton("删除")

        self.btn_print=QPushButton("打印Model")
        
        detail_group = QGroupBox("标签详情")
        formlayout=QFormLayout(detail_group)
        formlayout.addRow("标签名字",self.tag_name)
        formlayout.addRow("标签类型",self.tag_type)
        formlayout.addRow("颜色",self.color)
        formlayout.addRow("细节",self.detail)
        #formlayout.addRow("打印",self.btn_print)
        formlayout.addRow("重定向",self.alias_view)
        

        self.m_group = QGroupBox("多选操作")
        self.m_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        vlayout=QVBoxLayout(self.m_group)

        self.m_color=ColorPicker()
        self.m_color.setMaximumHeight(40)
        self.btn_change=QPushButton("批量改变标签颜色")

        self.btn_mutex=QPushButton("批量标签编成一个互斥组")
        self.btn_tag_type=QPushButton("修改标签类型")

        color_group=QGroupBox("改多个标签颜色")
        color_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        vlayout1=QVBoxLayout(color_group)
        vlayout1.addWidget(self.m_color)
        vlayout1.addWidget(self.btn_change)

        vlayout.addWidget(color_group)
        vlayout.addWidget(self.btn_mutex)


        self.m_group.setEnabled(False)
        #左侧总装
        leftlayout.addWidget(show_group)
        leftlayout.addWidget(detail_group)
        leftlayout.addWidget(self.btn_commit)
        leftlayout.addWidget(self.btn_delete)
        leftlayout.addWidget(self.btn_tag_type)
        #leftlayout.addWidget(self.m_group)

        #第三列
        self.tag_selector=TagSelector4(enbale_mutex_check=False)#这个有个问题，复用这个会有组检查
        self.tag_selector.tag_receive_widget.setFixedWidth(180)
        self.tag_selector.panel_fix_width=400
        self.tag_selector.btn_expand.click()



        #总装
        mainlayout = QHBoxLayout(self)
        mainlayout.addWidget(self.leftwidget)
        mainlayout.addWidget(self.tag_selector)
        mainlayout.addWidget(self.m_group)



        self.bind_model()
        self.createlivetag()
        self.signal_connect()

        self.vm._clear_all_info()#刷新一下界面

    def bind_model(self):
        # UI->model
        self.color_updating=False
        self.color.colorChanged.connect(self.colorpick_ui_to_model)
        self.tag_type.currentTextChanged.connect(lambda tag_type:self.vm.set_tag_type_id(self.vm.find_tag_type_id_by_value(tag_type)))#改变model

        # model-UI
        self.vm.tag_color_changed.connect(self.colorpick_model_to_ui)
        self.vm.tag_type_id_changed.connect(lambda key:self.tag_type.setCurrentText(self.vm.tag_type_map.get(key)))

        bindings_map2 = {
            "tag_name": self.tag_name,
            "tag_detail": self.detail
        }
        self._updating_flags={}
        for prop_name,widget in bindings_map2.items():
            self._updating_flags[prop_name] = False
            widget.textChanged.connect(lambda text,p=prop_name:self.lineedit_ui_to_model(p,text))#这里匿名函数作为槽函数
            vm_signal:SignalInstance=getattr(self.vm,f"{prop_name}_changed")
            vm_signal.connect(lambda text, w=widget,p=prop_name:self.lineedit_model_to_ui(w,p,text))#这里匿名函数作为槽函数
        
        #model-> tablemodel
        self.vm.tag_alias_changed.connect(self.alias_view.updatedata)
        self.alias_view.model.data_updated.connect(self.vm.set_tag_alias)

        self.vm.tag_name_changed.connect(self.updatelivetag_name)
        self.vm.tag_color_changed.connect(self.updatelivetag_color)
        self.vm.tag_detail_changed.connect(self.updatelivetag_detail)

    def signal_connect(self):
        self.tag_selector.selection_changed.connect(self.on_tag_change)
        self.btn_commit.clicked.connect(self.vm.commit)
        self.btn_change.clicked.connect(self.change_tag_color)
        self.btn_print.clicked.connect(lambda:print(self.vm.model.to_dict()))
        self.btn_delete.clicked.connect(self.vm.delete)
        self.vm.after_delete.connect(self.after_delete)
        self.vm.load_tag_selector.connect(self.tag_selector.load_with_ids)
        self.btn_tag_type.clicked.connect(self.modify_tag_type)
        
    def modify_tag_type(self):
        '''打开一个QDialog'''
        dialog=TagTypeModifyDialog(self)
        dialog.exec()

    def createlivetag(self):
        '''创建一个实时的跟着动的tag'''
        if not self.livetaglabel:
            self.livetaglabel = VShowTagLabel(self.vm.get_tag_id(),self.vm.get_tag_name(),self.vm.get_tag_color(),self.vm.get_tag_detail())
            self.tag_liveshow.mainlayout.addWidget(self.livetaglabel)
    
    @Slot(str)
    def updatelivetag_name(self,tag_name:str):
        if self.livetaglabel:
            self.livetaglabel.setTextDynamic(tag_name)

    @Slot(str)
    def updatelivetag_color(self,tag_color:str):
        if self.livetaglabel:
            self.livetaglabel.set_color(tag_color)
    
    @Slot(str)
    def updatelivetag_detail(self,detail:str):
        if self.livetaglabel:
            self.livetaglabel.setToolTip(detail)

    @Slot()
    def after_delete(self):
        '''删除后的界面反应'''

        self.tag_selector.load_with_ids([])
        self.tag_selector.reload_tag()

    @Slot(str)
    def colorpick_ui_to_model(self,color:str):
        '''双向绑定颜色'''
        if self.color_updating:
            return
        self.color_updating=True
        self.vm.set_tag_color(color)
        self.color_updating=False

    @Slot(str)
    def colorpick_model_to_ui(self,color:str):
        if self.color_updating:
            return
        self.color_updating=True
        self.color.set_color(color)
        self.color_updating=False


    def lineedit_ui_to_model(self,prop_name:str,text:str):
        if self._updating_flags.get(prop_name, False):
            return
        self._updating_flags[prop_name] = True
        setter_method=getattr(self.vm,f"set_{prop_name}")
        setter_method(text)
        self._updating_flags[prop_name] = False


    def lineedit_model_to_ui(self,widget:QLineEdit,prop_name:str,text):
        if self._updating_flags.get(prop_name, False):
            return
        self._updating_flags[prop_name] = True
        widget.setText(text)
        self._updating_flags[prop_name] = False

    @Slot()
    def on_tag_change(self):
        '''tag选择器的数量改变'''
        ids=self.tag_selector.get_selected_ids()
        if len(ids)==0:
            self.m_group.setEnabled(False)
            self.vm._clear_all_info()
            #清除选择器
            #self.clear_layout(self.tag_show.mainlayout)
            self.taglabel=None
            self.m_color.set_color("#cccccc")
        elif len(ids)==1:#删除到一个时候也添加了，这就不对了
            self.m_group.setEnabled(False)
            self.vm.load_tag_by_id(ids[0])
            #拷贝一个添加到视图中
            from core.database.query import get_taginfo_by_id
            data=get_taginfo_by_id(ids[0])
            if not self.taglabel:
                self.taglabel = VerticalTagLabel(ids[0],data["tag_name"],data["color"],data.get("detail",""))
                #self.tag_show.mainlayout.addWidget(self.taglabel)
                self.m_color.set_color(data["color"])
        else:
            self.m_group.setEnabled(True)
            return
        
    def clear_layout(self,layout:QLayout):
        """清空布局中的所有widget"""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()  # 安全删除widget
            # 删除item本身以释放内存
            del item

    @Slot()
    def change_tag_color(self):
        '''批量改变tag的颜色'''
        from core.database.update import update_tag_color
        ids:list=self.tag_selector.get_selected_ids()

        color=self.m_color._color.name()
        update_tag_color(ids,color)
        self.tag_selector.reload_tag()

