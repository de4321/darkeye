
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QLabel,QVBoxLayout,QLineEdit,QTextEdit,QSizePolicy,QFormLayout,QSpinBox,QComboBox,QWidget
from PySide6.QtCore import Qt,QObject,Signal,Property,Signal,Slot

from ui.widgets.CrawlerToolBox import CrawlerToolBox
import logging,json,asyncio
from pathlib import Path
from enum import Enum

from config import settings,WORKCOVER_PATH
from ui.base import LazyWidget
from controller.MessageService import MessageBoxService,IMessageService
from ui.basic import ToggleSwitch,MovableTableView,IconPushButton
from core.database.query import get_actress_allname
from ui.widgets import ActressAvatarDropWidget


class Model():
    '''纯放要显示数据的model'''
    def __init__(self):
        self._actress_id:int=None

        self._height:int= None
        self._cup:str= None
        self._birthday:str= None
        self._hip:int= None
        self._waist:int= None
        self._bust:int= None
        self._debut_date:str= None
        self._need_update:bool= False

        self._image_urlA:str= None
        self._actress_name:list[dict] = []

    def to_dict(self):
        return {
            "actress_id": self._actress_id,
            "height": self._height,
            "cup": self._cup,
            "birthday": self._birthday,
            "hip": self._hip,
            "waist": self._waist,
            "bust": self._bust,
            "debut_date": self._debut_date,
            "need_update": self._need_update,
            "image_urlA": self._image_urlA,
            "actress_name": self._actress_name
        }

class ViewModel(QObject):
    actress_id_Changed=Signal(int)
    height_Changed = Signal(int)
    cup_Changed = Signal(str)
    birthday_Changed = Signal(str)
    hip_Changed = Signal(int)
    waist_Changed = Signal(int)
    bust_Changed = Signal(int)
    debut_date_Changed = Signal(str)
    need_update_Changed = Signal(bool)
    image_urlA_Changed = Signal(str)
    actress_name_Changed = Signal(list)

    def __init__(self, model:Model=None,message_service:IMessageService=None):
        super().__init__()
        self.model:Model = model
        self.msg:MessageBoxService=message_service

    def get_actress_id(self):
        return self.model._actress_id
    def set_actress_id(self,value:int):
        if self.model._actress_id != value:
            self.model._actress_id = value
            self.actress_id_Changed.emit(value)
    actress_id=Property(int,get_actress_id,set_actress_id,notify=actress_id_Changed)

    def get_height(self):
        return self.model._height
    def set_height(self, value:int):
        if self.model._height != value:
            self.model._height = value
            self.height_Changed.emit(value)
    height = Property(int, get_height, set_height, notify=height_Changed)

    def get_cup(self):
        return self.model._cup
    def set_cup(self, value:str):
        if self.model._cup != value:
            self.model._cup = value
            self.cup_Changed.emit(value)
            logging.debug(f"cup changed to {value}")
    cup = Property(str, get_cup, set_cup, notify=cup_Changed)

    def get_birthday(self):
        return self.model._birthday
    def set_birthday(self, value:str):
        if self.model._birthday != value:
            self.model._birthday = value
            self.birthday_Changed.emit(value)
    birthday = Property(str, get_birthday, set_birthday, notify=birthday_Changed)

    def get_hip(self):
        return self.model._hip
    def set_hip(self, value:int):
        if self.model._hip != value:
            self.model._hip = value
            self.hip_Changed.emit(value)
    hip = Property(int, get_hip, set_hip, notify=hip_Changed)

    def get_waist(self):
        return self.model._waist
    def set_waist(self, value:int):
        if self.model._waist != value:
            self.model._waist = value
            self.waist_Changed.emit(value)
    waist = Property(int, get_waist, set_waist, notify=waist_Changed)

    def get_bust(self):
        return self.model._bust
    def set_bust(self, value:int):
        if self.model._bust != value:
            self.model._bust = value
            self.bust_Changed.emit(value)
    bust = Property(int, get_bust, set_bust, notify=bust_Changed)

    def get_debut_date(self):
        return self.model._debut_date
    def set_debut_date(self, value:str):
        if self.model._debut_date != value:
            self.model._debut_date = value
            self.debut_date_Changed.emit(value)
    debut_date = Property(str, get_debut_date, set_debut_date, notify=debut_date_Changed)

    def get_need_update(self):
        return self.model._need_update
    def set_need_update(self, value:bool):
        if self.model._need_update != value:
            self.model._need_update = value
            self.need_update_Changed.emit(value)
    need_update = Property(bool, get_need_update, set_need_update, notify=need_update_Changed)

    def get_image_urlA(self):
        return self.model._image_urlA
    def set_image_urlA(self, value:str):
        if self.model._image_urlA != value:
            self.model._image_urlA = value
            self.image_urlA_Changed.emit(value)
    image_urlA = Property(str, get_image_urlA, set_image_urlA, notify=image_urlA_Changed)

    def get_actress_name(self):
        logging.debug("读取actress_name数据")
        return self.model._actress_name
    def set_actress_name(self, value:list[dict]):
        logging.debug("设置viewmodel里的actress_name")
        from utils.utils import sort_dict_list_by_keys
        order=['actress_name_id','cn','jp', 'kana','en','level','redirect_actress_name_id']
        value=sort_dict_list_by_keys(value,order)
        if self.model._actress_name != value:
            self.model._actress_name = value
            self.actress_name_Changed.emit(value)

    actress_name = Property(list, get_actress_name, set_actress_name, notify=actress_name_Changed)

    def load(self,actress_id:int):
        '''加载'''
        from core.database.query import get_actress_info
        actress=get_actress_info(actress_id)
        if not actress:
            self.msg.show_warning("错误","未找到该女优信息")
            return
        logging.debug(f"设置actress_id:{actress_id}")
        self.set_actress_id(actress_id)
        self.set_height(actress.get("height") or 0)
        self.set_cup(actress.get("cup") or "")

        self.set_birthday(actress.get("birthday") or "")
        self.set_hip(actress.get("hip") or 0)
        self.set_waist(actress.get("waist") or 0)
        self.set_bust(actress.get("bust") or 0)
        self.set_debut_date(actress.get("debut_date") or "")
        self.set_image_urlA(actress.get("image_urlA") or "")
        self.set_actress_name(get_actress_allname(self.actress_id))
        self.set_need_update(actress.get("need_update")or False)

    @Slot()
    def submit(self):
        '''手动修改记录
        '''
        #获得基本数据
        
        logging.debug("添加记录")
        data=self.model.to_dict()#从viewmodel里取

        image_url=str(self.actress_id) +'-'+self.actress_name[0]["jp"]+'.jpg'#图片名字的规则,要保证日文名字一定要有
        if self.get_image_urlA() is None or self.get_image_urlA()=="":
            data["image_urlA"]=None
        else:
            from core.database.insert import rename_save_image
            rename_save_image(data["image_urlA"],image_url,"actress")
            data["image_urlA"]=image_url

        self._update_actress_and_handle_result(**data)

    def _update_actress_and_handle_result(self,**data):
        from core.database.update import update_actress_byhand
        actress_name=data["actress_name"][0]["jp"]

        if update_actress_byhand(**data):
            self.msg.show_info("更新女优信息成功",f"女优名字: {actress_name}")
            logging.info("更新女优成功，女优名字：%s",actress_name)
            #刷新，重新加载
            self.load(data.get("actress_id"))
            return True
        else:
            self.msg.show_warning("更新女优信息失败",f"未知原因")
            logging.warning("更新%s女优信息失败",actress_name)
            return False

    @Slot()
    def clawer_update(self):
        '''爬虫更新单个女优的数据，是直接更新，而不是写界面后提交'''
        from core.crawler.SearchActressInfo import SearchSingleActressInfo
        from core.crawler.CrawlerThreadResult import CrawlerThreadResult
        logging.info(self.actress_id)
        logging.info(self.actress_name[0]["jp"])
        self.thread:CrawlerThreadResult=CrawlerThreadResult(lambda:SearchSingleActressInfo(self.actress_id,self.actress_name[0]["jp"]))#传一个函数名进去
        self.thread.finished.connect(self.on_result)
        self.thread.start()

    @Slot(bool)
    def on_result(self,result:bool):#Qsignal回传信息
        if result:
            self.msg.show_info("提示消息","查询完成")
        else:
            self.msg.show_warning("提示消息","查询失败")

    @Slot()
    def print(self):
        logging.debug(self.model.to_dict())

    @Slot()
    def delete_actress(self):
        '''直接删除一个女优，如果有在作品中的就不删除'''
        from core.database.delete import  delete_actress
        success,message=delete_actress(self.actress_id)
        if success:
            self.msg.show_info("提示",message)
            from controller.GlobalSignalBus import global_signals
            global_signals.actress_data_changed.emit()
        else:
            self.msg.show_warning("提示",message)

class ModifyActressPage(LazyWidget):
    #修改女优信息
    '''
    '''
    def __init__(self):
        super().__init__()

    def _lazy_load(self):
        logging.info("----------修改女优信息页面----------")
        self.config()
        self.init_ui()
        self.bind_model()
        self.signal_connect()

    def init_ui(self):
        mainlayout = QVBoxLayout(self)
        mainlayout.setContentsMargins(0, 0, 0, 0)
        mainlayout.addSpacing(70)
        
        hlayout=QHBoxLayout()
        mainlayout.addLayout(hlayout)
        self.moveable_name=MovableTableView()
        self.avatar=ActressAvatarDropWidget("actress")

        self.basic=QWidget()
        self.basic.setFixedWidth(300)
        vlayout=QVBoxLayout(self.basic)
        vlayout.addWidget(self.avatar)
        formlayout=QFormLayout()
        vlayout.addLayout(formlayout)
        self.input_height=QSpinBox()
        self.input_height.setRange(0,190)
        self.input_waist=QSpinBox()
        self.input_waist.setRange(0,120)
        self.input_hip=QSpinBox()
        self.input_hip.setRange(0,120)
        self.input_bust=QSpinBox()
        self.input_bust.setRange(0,120)
        self.input_cup=QComboBox()
        self.input_cup.addItems(["A","B","C","D","E","F","G","H","I","J","K","L","M"])
        
        self.input_birthday=QLineEdit()
        self.input_debut_date=QLineEdit()
        self.need_update=ToggleSwitch(width=40,height=20)
        self.btn_commit=QPushButton("提交修改")
        self.btn_claw_update=QPushButton("爬虫直接更新")
        #self.btn_printModel=QPushButton("打印数据")
        self.btn_minnano=QPushButton("minnano-av")
        self.btn_delete=IconPushButton("trash-2.png")
        
        formlayout.addRow("身高(cm)",self.input_height)
        formlayout.addRow("罩杯",self.input_cup)
        formlayout.addRow("胸围(cm)",self.input_bust)        
        formlayout.addRow("腰围(cm)",self.input_waist)
        formlayout.addRow("臀围(cm)",self.input_hip)
        formlayout.addRow("生日(yyyy-mm-dd)",self.input_birthday)
        formlayout.addRow("出道日期(yyyy-mm-dd)",self.input_debut_date)
        formlayout.addRow("需要更新",self.need_update)
        formlayout.addRow("",self.btn_commit)
        formlayout.addRow("",self.btn_claw_update)
        #formlayout.addRow("",self.btn_printModel)
        formlayout.addRow("",self.btn_minnano)
        formlayout.addRow("",self.btn_delete)

        
        hlayout.addWidget(self.basic)
        hlayout.addWidget(self.moveable_name)
        hlayout.addStretch()


    def config(self):
        '''配置model与view'''

        self.msg=MessageBoxService(self)#弹窗服务
        self.model=Model()
        self.vm = ViewModel(self.model,self.msg)#依赖注入

    
    def signal_connect(self):
        self.btn_claw_update.clicked.connect(self.vm.clawer_update)
        #self.btn_printModel.clicked.connect(self.vm.print)
        self.btn_commit.clicked.connect(self.vm.submit)
        self.btn_minnano.clicked.connect(self.jump_minnano)
        self.btn_delete.clicked.connect(self.vm.delete_actress)


    def bind_model(self):
        '''双向绑定'''
        #实际上下面都会有循环绑定的问题，后面需要改
        self.input_height.valueChanged.connect(self.vm.set_height)
        self.vm.height_Changed.connect(self.input_height.setValue)

        self.input_hip.valueChanged.connect(self.vm.set_hip)
        self.vm.hip_Changed.connect(self.input_hip.setValue)

        self.input_waist.valueChanged.connect(self.vm.set_waist)
        self.vm.waist_Changed.connect(self.input_waist.setValue)

        self.input_bust.valueChanged.connect(self.vm.set_bust)
        self.vm.bust_Changed.connect(self.input_bust.setValue)

        self.input_cup.currentTextChanged.connect(self.vm.set_cup)
        self.vm.cup_Changed.connect(self.input_cup.setCurrentText)#这里有问题

        self.input_birthday.textChanged.connect(self.vm.set_birthday)
        self.vm.birthday_Changed.connect(self.input_birthday.setText)

        self.input_debut_date.textChanged.connect(self.vm.set_debut_date)
        self.vm.debut_date_Changed.connect(self.input_debut_date.setText)

        self.need_update.toggled.connect(self.vm.set_need_update)
        self.vm.need_update_Changed.connect(self.need_update.setChecked)

        #tablemodel与viewmodel的绑定
        # TODO 这里存在循环绑定的问题
        self.moveable_name.model.data_updated.connect(self.vm.set_actress_name)
        self.vm.actress_name_Changed.connect(self.moveable_name.updatedata)#这个实际上有点违反原则，pyside6信号传字典时顺序不可控

        self.vm.image_urlA_Changed.connect(self.avatar.set_image)#这些绑定实际上都是有点问题的，不过先不管了
        self.avatar.cover_changed.connect( # coverdroplabel 可以在图片改变后发信号更新模型
            lambda: self.vm.set_image_urlA(self.avatar.get_image())
        )


    def update(self,actress_id:int):
        '''加载'''
        self.vm.load(actress_id)

    @Slot()
    def jump_minnano(self):
        from core.crawler.jump import jump_minnanoav
        
        jp_name=self.vm.get_actress_name()
        jp_name=jp_name[0]["jp"]
        jump_minnanoav(jp_name)

