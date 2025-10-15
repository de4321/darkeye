
from PySide6.QtCore import QObject, Signal

class GlobalSignalBus(QObject):
    """全局信号总线"""
    work_data_changed = Signal()  # 作品数据变更信号
    actress_data_changed = Signal()  # 女优数据变更信号,主要是刷新女优选择器
    actor_data_changed = Signal()  # 男优数据变更信号，主要是刷新男优选择器
    tag_data_changed=Signal()#标签数据变更信号，主要是刷新标签选择器

    masterbation_changed=Signal() # 撸管记录变更信号
    lovemaking_changed=Signal() #做爱记录变更信号
    sexarousal_changed=Signal() #晨勃记录变更信号
    green_mode_changed=Signal(bool) #绿色模式切换信号，参数是当前状态
    like_work_changed=Signal()#喜欢作品的信号修改


    tag_clicked=Signal(int)#点击tag后的信号，就是跳转到work界面里搜索用的
    actress_clicked=Signal(int)#点击后跳转到单女优的详细页面
    actor_clicked=Signal(int)#点击后跳转到筛选男优的界面
    work_clicked=Signal(int)#点击后跳转到单作品详细页
    modify_work_clicked=Signal(str)#点击后跳转到修改作品页面
    modify_actress_clicked=Signal(int)#点击后跳转到修改女优页面
    modify_actor_clicked=Signal(int)


global_signals = GlobalSignalBus()