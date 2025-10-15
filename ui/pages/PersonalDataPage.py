#个人女优详细的面板
from PySide6.QtWidgets import QHBoxLayout, QWidget, QLabel,QVBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt,Slot
from core.database.query import get_record_count_in_days,get_top_actress_by_masturbation_count
import logging
from ui.widgets import ActressCard
from ui.basic.Effect import ShadowEffectMixin
from ui.base import LazyWidget
from ui.statistics import SwitchHeapMap
from controller.GlobalSignalBus import global_signals

class PersonalDataPage(LazyWidget):
    def __init__(self):
        super().__init__()


    def _lazy_load(self):
        logging.info("----------个人数据界面----------")
        mainlayout = QVBoxLayout(self)
        mainlayout.setContentsMargins(0, 0, 0, 0)
        
        self.hlayout=QHBoxLayout()
        
        most_like_actress30=MostLikeActress(30)
        most_like_actress180=MostLikeActress(180)
        most_like_actress365=MostLikeActress(365)

        work_sale_cycle=WorkSaleCycle()
        self.hlayout.addWidget(most_like_actress30)
        self.hlayout.addWidget(most_like_actress180)
        self.hlayout.addWidget(most_like_actress365)

        self.hlayout.addWidget(work_sale_cycle)

        mainlayout.addLayout(self.hlayout)

        calendar_heatmap=SwitchHeapMap()
        mainlayout.addWidget(calendar_heatmap,alignment=Qt.AlignCenter)

        
        #全局信号总线触发
        global_signals.masterbation_changed.connect(work_sale_cycle.update_day)
        global_signals.like_work_changed.connect(work_sale_cycle.update_day)
        global_signals.masterbation_changed.connect(most_like_actress30.update_actress)
        global_signals.masterbation_changed.connect(most_like_actress180.update_actress)
        global_signals.masterbation_changed.connect(most_like_actress365.update_actress)
        from datetime import datetime
        global_signals.masterbation_changed.connect(lambda:calendar_heatmap.update(datetime.now().year))
        global_signals.lovemaking_changed.connect(lambda:calendar_heatmap.update(datetime.now().year))
        global_signals.sexarousal_changed.connect(lambda:calendar_heatmap.update(datetime.now().year))

class WorkSaleCycle(QWidget,ShadowEffectMixin):
    '''去化周期显示'''
    def __init__(self):
        super().__init__()
        self.setFixedSize(170,250)
        self.setAttribute(Qt.WA_StyledBackground, True)
        mainlayout=QVBoxLayout(self)
        mainlayout.setContentsMargins(0,0,0,0)
        label1=QLabel(f"收藏作品中未观看去化周期")
        label1.setAlignment(Qt.AlignCenter)

        self.label2=QLabel()
        self.label2.setAlignment(Qt.AlignCenter)   
        self.update_day()

        mainlayout.addWidget(label1)
        mainlayout.addWidget(self.label2)


        self.setObjectName("WorkSaleCycle")  # 给外层起名字
        self.setStyleSheet("""
            #WorkSaleCycle {
                border-radius: 12px;
                background-color: white;
            }
        """)
        self.set_shadow()

    def work_not_watch(self):
        '''#按过去3个月平均的撸管频率去计算去化周期并显示,当去化周期大于14天时就进入选择模式'''
        from core.database.query import get_unmasturbated_work_count
        un_mas_num=get_unmasturbated_work_count()
        count=get_record_count_in_days(90,0)
        if not count==0:
            Sales_cycleun=int(un_mas_num/count*90)
        else:
            Sales_cycleun=114514
        return Sales_cycleun
    
    @Slot()
    def update_day(self):
        logging.debug("更新去化周期")
        day=self.work_not_watch()
        self.label2.setText(str(day)+"天")
        if day>30:
            self.label2.setStyleSheet("font-size: 30pt; color: #FF0000;")  # 纯红
        else:
            self.label2.setStyleSheet("font-size: 30pt; color: #000000;")  # 纯红

class MostLikeActress(QWidget,ShadowEffectMixin):
    '''最喜欢的女优卡片'''
    def __init__(self,beforeday):
        super().__init__()
        self._bday=beforeday
        
                # 加圆角边框的样式
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("mostLikeActress")  # 给外层起名字
        self.setStyleSheet("""
            #mostLikeActress {
                border-radius: 12px;
                background-color: white;
            }
        """)
        self.set_shadow()
        self.setFixedSize(170,250)

        label1=QLabel(f"过去{beforeday}天最喜欢的女优")
        actress=get_top_actress_by_masturbation_count(beforeday)
        if actress:
            self.actress_card=ActressCard(actress['actress_name'],actress['image_urlA'],actress['actress_id'])
        else:
            self.actress_card=ActressCard()

        #总装
        mainlayout=QVBoxLayout(self)
        mainlayout.setContentsMargins(10,0,10,10)
        mainlayout.addWidget(label1,alignment=Qt.AlignCenter)
        mainlayout.addWidget(self.actress_card)

    
    @Slot()
    def update_actress(self):
        '''初始化或者更新'''
        actress=get_top_actress_by_masturbation_count(self._bday)
        if actress:
            self.actress_card.update_data(actress['actress_name'],actress['image_urlA'],actress['actress_id'])


