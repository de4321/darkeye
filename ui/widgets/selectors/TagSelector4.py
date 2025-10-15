from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout,QPushButton,QSizePolicy,QTabWidget,QScrollArea,QFrame,QGroupBox,QLineEdit,QLayoutItem
from PySide6.QtCore import Signal,QEasingCurve,QVariantAnimation,Slot,QTimer
from PySide6.QtGui import QPixmap,QCursor
from pathlib import Path
import logging

from config import ICONS_PATH
from core.database.query import getTags
from ui.basic import WaterfallLayout,VLabel,IconPushButton
from ui.widgets.text.VerticalTagLabel2 import VerticalTagLabel2
from controller import MessageBoxService
from ui.widgets.VerticalTabBar import VerticalTabBar
from ui.base import SearchLineBase
from controller.GlobalSignalBus import global_signals

class FloatingPanel(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tag_map={}
        self.mainlayout = QVBoxLayout(self)
        self.mainlayout.setContentsMargins(0, 0, 0, 0)


        self.searchLine=SearchLineBase()
        #search_group=QGroupBox("搜索框")
        #hlayout=QHBoxLayout(search_group)
        #hlayout.setContentsMargins(5,0,5,5)
        #self.searchLine=QLineEdit()
        #self.btn_search=IconPushButton("search.png",iconsize=24,outsize=32)
        #hlayout.addWidget(self.searchLine)
        #hlayout.addWidget(self.btn_search)


        self.tag_emit_tabwidget = QTabWidget()
        self.tag_emit_tabwidget.setTabPosition(QTabWidget.West)
        # 设置自定义的垂直标签栏
        self.tag_emit_tabwidget.setTabBar(VerticalTabBar())

        self.mainlayout.addWidget(self.searchLine)
        self.mainlayout.addWidget(self.tag_emit_tabwidget)

        self.tag_emit_tabwidget.setStyleSheet("""
            QTabWidget::pane {
                border: none;          /* 去掉外边框 */
                background: transparent;
                margin: 0;             /* 防止多余的内边距 */
                padding: 0;
            }
        """)

    def animate_width(self, target_width, duration=300):#现在还在闪
        self.anim = QVariantAnimation(
            startValue=self.width(),
            endValue=target_width,
            duration=duration,
            easingCurve=QEasingCurve.InOutQuad
        )
        self.anim.valueChanged.connect(self.setFixedWidth)
        self.anim.start()


class TagSelector4(QWidget):
    '''选择tag的容器'''
    success=Signal(bool)#定义信号
    selection_changed=Signal()
    def __init__(self,enbale_mutex_check=True):
        super().__init__()
        self.setCursor(QCursor(QPixmap(Path(ICONS_PATH/"mouse_off.png")),hotX=32,hotY=32))  # 手型指针
        #总体布局是横向布局
        self.setStyleSheet("""
            QTabWidget::pane, QScrollArea, QFrame {
                border: none;
                background: transparent;
            }
        """)
        self.enbale_mutex_check=enbale_mutex_check#互斥检查是否开启

        #下面三个数据结构管理数据核心
        self.tag_map:dict[int,VerticalTagLabel2] = {}# tag_id -> label
        self.type_map:dict[str,WaterfallLayout]={} #tag_type -> WaterfallLayout
        self.selected_ids:set[int]=set() #选择的ids
        self.scroll_map:dict[str,QScrollArea]={}

        self.msg=MessageBoxService(self)

        # 左边：绑定的标签容器，FlowLayout

        self.tag_receive_widget = QWidget()
        self.tag_receive_widget.setObjectName("tagReceiveWidget")
        self.tag_receive_widget.setStyleSheet("""
            #tagReceiveWidget {
                border: 3px dashed #000000;     /* 宽度/样式/颜色 */
                border-radius: 8px;             /* 圆角（可选） */
                background: white;
            }
        """)
        
        self.tag_receive_widget.setFixedWidth(150)
        self.tag_receive_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.tag_receive_layout = WaterfallLayout(self.tag_receive_widget,column_width=27,spacing=5)#这个要改

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.tag_receive_widget)

        self.vlabel=VLabel("作品标签",background_color="#00000000",border_color="#000000")
        self.tag_receive_layout.addWidget(self.vlabel)
        
        self.btn_clear=IconPushButton("brush-cleaning.png")
        self.btn_reload_tag=IconPushButton("refresh-cw.png")
        self.btn_expand=IconPushButton("arrow-right.png")

        #self.btn_get_tag_ids=QPushButton("获\n得\nid")
        #self.btn_get_tag_ids.setFixedWidth(30)
        

        v_small_widget=QWidget()
        v_small_widget.setFixedWidth(24)
        left_small_layout=QVBoxLayout(v_small_widget)#布局设置给widget
        left_small_layout.setContentsMargins(0,0,0,0)
        left_small_layout.addWidget(self.btn_clear)
        left_small_layout.addWidget(self.btn_reload_tag)
        left_small_layout.addWidget(self.btn_expand)
        left_small_layout.addStretch()
        #left_small_layout.addWidget(self.btn_get_tag_ids)
        #left_small_layout.addWidget(self.btn_load)

        self.left_widget=QWidget()
        #self.left_widget.setStyleSheet("border: 1px solid red; border-radius: 4px;")
        self.left_widget.setFixedWidth(130)
        left_layout=QHBoxLayout(self.left_widget)
        left_layout.setContentsMargins(0,0,0,0)
        left_layout.setSpacing(0)
        left_layout.addWidget(scroll)
        left_layout.addWidget(v_small_widget)

        self.panel=FloatingPanel()
        self.panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.panel_fix_width=255
        self.panel.setFixedWidth(self.panel_fix_width)

        #self.panel.hide()
        main_layout=QHBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.left_widget,0)
        main_layout.addWidget(self.panel,0)
        main_layout.addStretch(1)

        self.load_tags()
        self.beatutetoolbox()
        self.signal_connect()

        self.panel_visible = False
        self.panel.animate_width(0)

        self.panel.searchLine.set_search_navi(self.search_func,self.navi_func)#让搜索起作用


    def signal_connect(self):
        self.btn_expand.clicked.connect(self.toggle_panel)
        #self.btn_get_tag_ids.clicked.connect(self.get_selected_ids)
        self.btn_reload_tag.clicked.connect(self.reload_tag)
        self.btn_clear.clicked.connect(self.clear_left_tags)
        #self.panel.btn_search.clicked.connect(self.search_tag)
        global_signals.tag_data_changed.connect(self.reload_tag)

    def add_tag(self, tag_id, label:VerticalTagLabel2):
        '''添加一个tag到右侧的容器'''
        label.clicked.connect(lambda:self.handle_tag_click(label))
        self.tag_map[tag_id] = label
        if label.tag_type not in self.type_map:
            # 创建一个 tab + layout
            scroll = QScrollArea()
            scroll.setFrameShape(QFrame.NoFrame)
            scroll.setFrameShadow(QFrame.Plain)
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("""
            QScrollArea {background-color: transparent;    /* 背景色 */
                border: none;       
                border-radius: 6px;}        /* 圆角边框 */
            """)
            page = QWidget()
            page.setObjectName("tagEmitWidget")
            page.setStyleSheet("""
            #tagEmitWidget {background-color: transparent;    /* 背景色 */
                border: none;       
                border-radius: 6px;}        /* 圆角边框 */
            """)
            scroll.setWidget(page)
            layout = WaterfallLayout(page, column_width=27, spacing=5,margin=5)
            self.type_map[label.tag_type] = layout
            self.scroll_map[label.tag_type] = scroll
            self.panel.tag_emit_tabwidget.addTab(scroll, label.tag_type)
        self.type_map[label.tag_type].addWidget(label)

    def move_to_left(self, label:VerticalTagLabel2):
        '''向左移是添加到选区内'''
        if label.tag_id not in self.selected_ids:
            self.type_map[label.tag_type].removeWidget(label)
            label.setParent(self.tag_receive_widget)
            self.tag_receive_layout.addWidget(label)
            self.selected_ids.add(label.tag_id)
            self.selection_changed.emit()
            logging.debug(self.selected_ids)

    def restore_to_right(self, label:VerticalTagLabel2):
        '''向右移是将标签放回待选区'''
        if label.tag_id in self.selected_ids:
            #标签页跳转，这里先跳转页面，后移动就正常了，这和几何刷新是在下一次事件循环，有关系
            self.panel.tag_emit_tabwidget.setCurrentWidget(self.scroll_map[label.tag_type])
            self.tag_receive_layout.removeWidget(label)
            self.type_map[label.tag_type].addWidget(label)
            self.selected_ids.remove(label.tag_id)
            self.selection_changed.emit()
            logging.debug(self.selected_ids)

    def load_with_ids(self, ids: list[int]):
        """根据 id 列表同步 UI"""
        new_ids = set(ids)
        remove_ids = self.selected_ids - new_ids
        add_ids = new_ids - self.selected_ids

        for tag_id in remove_ids:
            self.restore_to_right(self.tag_map[tag_id])
        for tag_id in add_ids:
            self.move_to_left(self.tag_map[tag_id])

    def get_selected_ids(self) -> list[int]:
        """获得已选中的 tag id"""
        return list(self.selected_ids)

    @Slot()
    def search_tag(self):
        '''过滤'''
        logging.debug("搜索")
        keyword = self.panel.searchLine.text().strip()
        logging.debug(keyword)
        if not keyword:
            return
        #通过数据库去搜索
        from core.database.query import get_tagid_by_keyword
        tag_ids=get_tagid_by_keyword(keyword)
        logging.debug(tag_ids)
        if tag_ids is None:
            return
        
        for tag_id in tag_ids:
            # 找到匹配标签，切换 tab
            logging.debug("切换标签")
            label=self.tag_map[tag_id]
            #logging.debug(self.type_map[label.tag_type].parentWidget())
            scroll = self.scroll_map[label.tag_type]
            tab_index = self.panel.tag_emit_tabwidget.indexOf(scroll)

            logging.debug(tab_index)
            if tab_index != -1:
                self.panel.tag_emit_tabwidget.setCurrentIndex(tab_index)
                # 滚动到可见
                scroll_area:QScrollArea = self.panel.tag_emit_tabwidget.currentWidget()
                scroll_area.ensureWidgetVisible(label)
                # 高亮标签（简单边框闪烁）
                original_style = label.styleSheet()
                label.setStyleSheet("border: 4px solid red;")
                QTimer.singleShot(1000, lambda l=label, s=original_style: l.setStyleSheet(s))
            break  # 只跳转到第一个匹配标签

    
    def search_func(self,keyword:str)->list:
        '''过滤'''
        #logging.debug(f"搜索关键词{keyword}")
        if not keyword:
            return []
        #通过数据库去搜索
        from core.database.query import get_tagid_by_keyword
        tag_ids=get_tagid_by_keyword(keyword)
        #logging.debug(tag_ids)
        if tag_ids is None:
            return []
        else:
            return tag_ids
        
    def navi_func(self,results:list,index:int):
        '''导航并显示函数'''
            # 找到匹配标签，切换 tab

        tag_id=results[index]
        #logging.debug("导航搜索结果")
        label=self.tag_map[tag_id]
        #logging.debug(self.type_map[label.tag_type].parentWidget())
        scroll = self.scroll_map[label.tag_type]
        tab_index = self.panel.tag_emit_tabwidget.indexOf(scroll)
        #logging.debug(tab_index)
        if tab_index != -1:
            self.panel.tag_emit_tabwidget.setCurrentIndex(tab_index)
            # 滚动到可见
            scroll_area:QScrollArea = self.panel.tag_emit_tabwidget.currentWidget()
            scroll_area.ensureWidgetVisible(label)
            # 高亮标签
            label.flash_invert(duration=1000, interval=200) 


    def load_tags(self):
        '''加载tag,这个只运行一次，而且是全部加载到右侧的容器里，后面的操作就是实例移来移去'''
        logging.debug("tagselector加载tag数据库")
        tags=getTags()

        for tag_id, name, tag_type, color,detail,tag_mutex in tags:
            label = VerticalTagLabel2(tag_id, name,tag_type, color,detail,tag_mutex)
            self.add_tag(tag_id,label)


    def beatutetoolbox(self):
        '''美化QTabWidget'''
        self.panel.tag_emit_tabwidget.setStyleSheet("""
        QTabWidget::pane {
            border: 1px solid #444;
            border-radius: 6px;
            background: #FFFFFF;
        }
        QTabBar::tab {
            background: #FFFFFF;
            color: #ccc;
            border: 1px solid #444;
            padding: 6px 14px;
            border-top-left-radius: 6px;
            border-bottom-left-radius: 6px;
            margin-right: 2px;
        }
        QTabBar::tab:hover {
            background: #EBE3CE;
            color: white;
        }
        QTabBar::tab:selected {
            background: #FFA500;
            color: white;
            font-weight: bold;
        }
        QTabBar::close-button {
            image: url(:/qt-project.org/styles/commonstyle/images/close-16.png);
            subcontrol-position: right;
        }
        QTabBar::close-button:hover {
            background: red;
            border-radius: 4px;
        }
        """)

    def handle_tag_click(self, label:VerticalTagLabel2):
        """点击切换左右"""
        if label.tag_id in self.selected_ids:
            self.restore_to_right(label)
        else:
            if self.enbale_mutex_check:
                #互斥检查
                self.check_mutex_with_selected(label)
                conflicting_tag = self.check_mutex_with_selected(label)
                if conflicting_tag:
                    self.msg.show_warning(
                        "标签冲突",
                        f"标签 <b>'{label.text()}'</b> 与已选标签 <b>'{conflicting_tag}'</b> 互斥！\n\n"
                        "请先移除冲突标签再添加。"
                    )
                    return  # 阻止移动

            self.move_to_left(label)

#-----------------------------------------------------

    def check_mutex_with_selected(self, label: VerticalTagLabel2) -> str|None:
        """检查当前标签是否与左侧已选标签互斥"""
        if not label.tag_mutex:  # 这个互斥组不能设置为0否则会被认为不是互斥的
            return None
        # 遍历左侧已选标签
        for tag_id in self.selected_ids:
            existing_label = self.tag_map[tag_id]
            if existing_label.tag_mutex == label.tag_mutex:  # 如果属于同一互斥组
                return existing_label.text()
        return None

    def clear_left_tags(self):
        """清除左侧所有标签，恢复到右侧"""
        for tag_id in list(self.selected_ids):  # 转成 list 防止迭代修改
            btn = self.tag_map[tag_id]
            self.restore_to_right(btn)

        self.selected_ids.clear()
        self.selection_changed.emit()

    def reload_tag(self):
        '''重新从数据库里加载tag，本来在上面的东西还是移上去'''
        logging.debug("重新加载tag数据库")
        #记住当前的index
        index=self.panel.tag_emit_tabwidget.currentIndex()
        exist_ids=self.get_selected_ids()
        #这里的清空有些内存泄露
        
        # 1. 清空 tag_map 和 toolbox
        self.tag_map.clear()
        self.type_map.clear()
        self.selected_ids.clear()
        # 清空所有页面
        while self.panel.tag_emit_tabwidget.count():
            widget = self.panel.tag_emit_tabwidget.widget(0)
            #if isinstance(widget,VerticalTagLabel2):
            self.panel.tag_emit_tabwidget.removeTab(0)
            widget.setParent(None)
            widget.deleteLater()

        #清空上面选中的页面
        for i in reversed(range(self.tag_receive_layout.count())):
            item:QLayoutItem = self.tag_receive_layout.itemAt(i)
            widget:VerticalTagLabel2 = item.widget()
            if isinstance(widget,VerticalTagLabel2):
                widget.setParent(None)
                widget.deleteLater()

        self.load_tags()
        self.load_with_ids(exist_ids)
        self.panel.tag_emit_tabwidget.setCurrentIndex(index)

    @Slot()
    def toggle_panel(self):
        if self.panel_visible:
            self.panel.animate_width(0)
            self.btn_expand.set_icon("arrow-right.png")
        else:
            self.panel.animate_width(self.panel_fix_width)
            self.btn_expand.set_icon("arrow-left.png")
        self.panel_visible = not self.panel_visible


    def set_state(self,state:bool):
        '''控制状态，正常状态与修改状态'''
        if state:
            self.tag_receive_widget.setStyleSheet("""
                #tagReceiveWidget {
                    border: 3px dashed #000000;    
                    border-radius: 5px;             
                    background: #ffffff;
                }
            """)
        else:
            self.tag_receive_widget.setStyleSheet("""
                #tagReceiveWidget {
                    border: 3px dashed #FFA500;     
                    border-radius: 5px;            
                    background: #ffffff;
                }
            """)
    
