
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QLabel,QVBoxLayout,QLineEdit,QTextEdit,QSizePolicy,QFormLayout,QSpinBox,QComboBox,QWidget,QSlider
from PySide6.QtCore import Qt,QObject,Signal,Property,Signal,Slot


import logging,json,asyncio
from pathlib import Path
from enum import Enum

from config import settings,WORKCOVER_PATH
from ui.base import LazyWidget
from controller.MessageService import MessageBoxService,IMessageService
from ui.basic import ToggleSwitch,MovableTableView,IconPushButton
from core.database.query import get_actor_allname
from ui.widgets import ActressAvatarDropWidget


class Model():
    '''纯放要显示数据的model'''
    def __init__(self):
        self._actor_id:int=None

        self._handsome:int=None
        self._fat:int=None
        self._image_url:str= None
        self._actor_name:list[dict] = []

    def to_dict(self):
        return {
            "handsome":self._handsome,
            "fat":self._fat,
            "actor_id": self._actor_id,
            "image_url": self._image_url,
            "actor_name": self._actor_name
        }

class ViewModel(QObject):
    actor_id_Changed=Signal(int)

    need_update_Changed = Signal(bool)
    image_url_Changed = Signal(str)
    actor_name_Changed = Signal(list)  
    fat_Changed=Signal(int)
    handsome_Changed=Signal(int)


    def __init__(self, model:Model=None,message_service:IMessageService=None):
        super().__init__()
        self.model:Model = model
        self.msg:MessageBoxService=message_service

    def get_actor_id(self):
        return self.model._actor_id
    def set_actor_id(self,value:int):
        if self.model._actor_id != value:
            self.model._actor_id = value
            self.actor_id_Changed.emit(value)
    actor_id=Property(int,get_actor_id,set_actor_id,notify=actor_id_Changed)

    def get_fat(self):
        return self.model._fat
    def set_fat(self,value:int):
        if self.model._fat != value:
            self.model._fat = value
            self.fat_Changed.emit(value)
    fat=Property(int,get_fat,set_fat,notify=fat_Changed)

    def get_handsome(self):
        return self.model._handsome
    def set_handsome(self,value:int):
        if self.model._handsome != value:
            self.model._handsome = value
            self.handsome_Changed.emit(value)
    handsome=Property(int,get_handsome,set_handsome,notify=handsome_Changed)

    def get_image_url(self):
        return self.model._image_url
    def set_image_url(self, value:str):
        if self.model._image_url != value:
            self.model._image_url = value
            self.image_url_Changed.emit(value)
    image_urlA = Property(str, get_image_url, set_image_url, notify=image_url_Changed)

    def get_actor_name(self):
        logging.debug("读取actor_name数据")
        return self.model._actor_name
    def set_actor_name(self, value:list[dict]):
        logging.debug("设置viewmodel里的actor_name")
        from utils.utils import sort_dict_list_by_keys
        order=['actor_name_id','cn','jp', 'kana','en']
        value=sort_dict_list_by_keys(value,order)
        if self.model._actor_name != value:
            self.model._actor_name = value
            self.actor_name_Changed.emit(value)

    actor_name = Property(list, get_actor_name, set_actor_name, notify=actor_name_Changed)

    def load(self,actor_id:int):
        '''加载'''
        from core.database.query import get_actor_info
        actor=get_actor_info(actor_id)
        if not actor:
            self.msg.show_warning("错误","未找到该男优信息")
            return
        logging.debug(f"设置actor_id:{actor_id}")
        self.set_handsome(actor.get("handsome" or 0))
        self.set_fat(actor.get("fat" or 0))
        self.set_actor_id(actor_id)
        self.set_image_url(actor.get("image_url") or "")
        self.set_actor_name(get_actor_allname(self.actor_id))

    @Slot()
    def submit(self):
        '''手动修改记录
        '''
        #获得基本数据
        
        logging.debug("添加记录")
        data=self.model.to_dict()#从viewmodel里取

        image_url=str(self.actor_id) +'-'+self.actor_name[0]["jp"]+'.jpg'#图片名字的规则,要保证日文名字一定要有
        if self.get_image_url() is None or self.get_image_url()=="":
            data["image_url"]=None
        else:
            from core.database.insert import rename_save_image
            rename_save_image(data["image_url"],image_url,"actor")
            data["image_url"]=image_url

        self._update_actor_and_handle_result(**data)

    def _update_actor_and_handle_result(self,**data):
        from core.database.update import update_actor_byhand
        actor_name=data["actor_name"][0]["jp"]

        if update_actor_byhand(**data):
            self.msg.show_info("更新男优信息成功",f"男优名字: {actor_name}")
            logging.info("更新男优成功，男优名字：%s",actor_name)
            self.load(data.get("actor_id"))
            return True
        else:
            self.msg.show_warning("更新男优信息失败",f"未知原因")
            logging.warning("更新%s男优信息失败",actor_name)
            return False

    @Slot()
    def print(self):
        logging.debug(self.model.to_dict())

    @Slot()
    def delete_actor(self):
        '''直接删除一个男优，如果有在作品中的就不删除'''
        from core.database.delete import delete_actor
        success,message=delete_actor(self.actor_id)
        if success:
            self.msg.show_info("提示",message)
            #更新男优的界面
        else:
            self.msg.show_warning("提示",message)

class ModifyActorPage(LazyWidget):
    #修改男优信息
    '''
    '''
    def __init__(self):
        super().__init__()

    def _lazy_load(self):
        logging.info("----------修改男优信息页面----------")
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
        self.avatar=ActressAvatarDropWidget("actor")

        self.handsomeSlider = QSlider(Qt.Horizontal)  # 水平滑动条
        self.handsomeSlider.setRange(0, 2)            # 设置范围 0～2
        self.handsomeSlider.setTickPosition(QSlider.TicksBelow)  # 显示刻度线
        self.handsomeSlider.setTickInterval(1)        # 每次一格
        self.handsomeSlider.setSingleStep(1)          # 每次移动步长为1
        self.handsomeSlider.setValue(0)

        self.fatSilder = QSlider(Qt.Horizontal)  # 水平滑动条
        self.fatSilder.setRange(0, 2)            # 设置范围 0～2
        self.fatSilder.setTickPosition(QSlider.TicksBelow)  # 显示刻度线
        self.fatSilder.setTickInterval(1)        # 每次一格
        self.fatSilder.setSingleStep(1)          # 每次移动步长为1
        self.fatSilder.setValue(0)       


        self.basic=QWidget()
        self.basic.setFixedWidth(300)
        vlayout=QVBoxLayout(self.basic)
        vlayout.addWidget(self.avatar)
        formlayout=QFormLayout()
        vlayout.addLayout(formlayout)

        

        self.btn_commit=QPushButton("提交修改")

        #self.btn_printModel=QPushButton("打印数据")

        self.btn_delete=IconPushButton("trash-2.png")
        

        formlayout.addRow("颜值",self.handsomeSlider)
        formlayout.addRow("胖瘦",self.fatSilder)
        formlayout.addRow("",self.btn_commit)
        #formlayout.addRow("",self.btn_printModel)
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

        #self.btn_printModel.clicked.connect(self.vm.print)
        self.btn_commit.clicked.connect(self.vm.submit)
        self.btn_delete.clicked.connect(self.vm.delete_actor)


    def bind_model(self):
        '''双向绑定'''
        #实际上下面都会有循环绑定的问题，后面需要改

        self.handsomeSlider.valueChanged.connect(self.vm.set_handsome)
        self.vm.handsome_Changed.connect(self.handsomeSlider.setValue)

        self.fatSilder.valueChanged.connect(self.vm.set_fat)
        self.vm.fat_Changed.connect(self.fatSilder.setValue)


        #tablemodel与viewmodel的绑定
        # TODO 这里存在循环绑定的问题
        self.moveable_name.model.data_updated.connect(self.vm.set_actor_name)
        self.vm.actor_name_Changed.connect(self.moveable_name.updatedata)#这个实际上有点违反原则，pyside6信号传字典时顺序不可控

        self.vm.image_url_Changed.connect(self.avatar.set_image)#这些绑定实际上都是有点问题的，不过先不管了
        self.avatar.cover_changed.connect( # coverdroplabel 可以在图片改变后发信号更新模型
            lambda: self.vm.set_image_url(self.avatar.get_image())
        )


    def update(self,actor_id:int):
        '''加载'''
        self.vm.load(actor_id)



