
from PySide6.QtWidgets import QHBoxLayout, QWidget, QLabel,QVBoxLayout,QGridLayout,QSizePolicy
from PySide6.QtCore import Qt,Slot
from PySide6.QtGui import QPainter,QPen
from ui.statistics import RadarChartWidget
import logging
from ui.basic import HeartLabel,OctImage
from ui.widgets import ClickableLabel

class SingleActressInfo(QWidget):
    '''单女优的信息数据显示'''
    def __init__(self):
        super().__init__()
        #存的数据
        self._actress_id=None
        self.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Minimum)

        #姓名栏
        self.name_widget=QWidget()
        self.name_widget.setFixedHeight(50)
        self.name_widget_layout=QHBoxLayout(self.name_widget)
        self.cn_name=ClickableLabel("中文名")
        self.jp_name=ClickableLabel("日文名",actress_jump=True)
        self.en_name=ClickableLabel("英文名")
        self.kana_name=ClickableLabel("假名")
        self.heart=HeartLabel()
        self.heart.clicked.connect(self.on_clicked_heart)

        self.name_widget_layout.addWidget(self.cn_name,alignment=Qt.AlignBottom)
        self.name_widget_layout.addWidget(self.jp_name,alignment=Qt.AlignBottom)
        self.name_widget_layout.addWidget(self.kana_name,alignment=Qt.AlignBottom)
        self.name_widget_layout.addWidget(self.en_name,alignment=Qt.AlignBottom)
        self.name_widget_layout.addWidget(self.heart,alignment=Qt.AlignBottom)
        self.name_widget_layout.addStretch()

        self.birthday=QLabel("出生日期xxxx年xx月xx日")
        label_birthday=QLabel("生日")
        #试一下的是动态信息，包括曾用名，等等

        self.pic=OctImage()#这个已经固定大小了
        self.radar=RadarChartWidget()
        self.radar.setFixedSize(250,220)

        self.dyna_layout=QGridLayout()
        self.dyna_layout.addWidget(label_birthday,0,0)
        self.dyna_layout.addWidget(self.birthday,0,1)


        info_layout=QHBoxLayout()
        info_layout.addWidget(self.pic,alignment=Qt.AlignmentFlag.AlignTop)
        info_layout.addLayout(self.dyna_layout)

        left_layout=QVBoxLayout()
        left_layout.addWidget(self.name_widget,alignment=Qt.AlignmentFlag.AlignTop)
        left_layout.addLayout(info_layout)
        left_layout.addStretch()

        #总装
        mainlayout = QHBoxLayout(self)
        mainlayout.setContentsMargins(10, 0, 0, 0)
        mainlayout.addLayout(left_layout)
        mainlayout.addWidget(self.radar,alignment=Qt.AlignmentFlag.AlignTop)
        mainlayout.addStretch()

        self.beaute()
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        pen = QPen(Qt.GlobalColor.darkGray, 2)  # 2像素黑色
        painter.setPen(pen)
        rect = self.rect()
        rect.adjust(1, 1, -1, -1)  # 避免超出控件边缘
        painter.drawRect(rect)

    def beaute(self):
        '''对控件美化'''
        #self.name_widget.setStyleSheet("background-color:#FFFFFF ;")

        self.cn_name.setStyleSheet("""
        font-size:30px;
        font-weight:bold;
""")
        self.jp_name.setStyleSheet("""
        font-size:16px;
        color: #333333; /* 深灰色 */
""")
        self.en_name.setStyleSheet("""
        font-size:16px;
        color: #333333; /* 深灰色 */
""")
        self.kana_name.setStyleSheet("""
        font-size:16px;
        color: #333333; /* 深灰色 */
""")
        self.birthday.setStyleSheet("""
        font-size:16px;
        color: #333333; /* 深灰色 */
""")

    def update(self,actress_id):
        '''传入一个actress_id并更新整个页面'''
        from core.database.query import  get_actress_info,get_all_actress_data,query_actress

        from utils.utils import convert_date

        self._actress_id=actress_id

        actress=get_actress_info(actress_id)
        data=get_all_actress_data()

        #更新基础字段
        self.cn_name.setText(actress['cn'])
        self.jp_name.setText(actress['jp'])
        self.kana_name.setText(actress['kana'])
        self.en_name.setText(actress['en'])
        self.birthday.setText(convert_date(actress['birthday']))

        #更新雷达图
        values=self.calc_radar_value(actress,data)
        categories = ["身高", "罩杯", "胸围", "腰围","臀围"]
        show_values = [actress['height'], actress['cup'], actress['bust'], actress['waist'],actress['hip']]

        self.radar.update_chart(categories,values,show_values)#实际更新

        #更新爱心状态
        if query_actress(actress_id):
            self.heart.set_statue(True)
        else:
            self.heart.set_statue(False)

        #更新头像
        self.pic.update_image(actress["image_urlA"])

        #更新动态的别名
        chain=self.calc_chain(actress_id)
        chain.pop()
        #logging.debug(chain)
        
        while self.dyna_layout.count()>2:#先清除layout中的元素
            item = self.dyna_layout.takeAt(2)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()  # 删除控件
        if chain:
            for name in chain:
                label=QLabel(name)
                label_alias=QLabel("别名")
                self.dyna_layout.addWidget(label_alias)
                self.dyna_layout.addWidget(label)

    def calc_radar_value(self,actress:dict,data:list[dict]):
        '''通过身材数据计算归一化后的身材数据供给雷达图用，回归残差去掉身高对腰围，胸围，臀围的影响
        actress:个体数据
        data:全体女优的数据

        '''
        from utils.utils import get_rank
        import numpy as np
        if actress["bust"] is None or actress["cup"] is None or actress["height"] is None or actress["hip"] is None or actress["waist"] is None or actress["cup"]=="":
            return [0,0,0,0,0]


        #判断是否是空
        height_list=[row["height"] for row in data]
        height_rank=get_rank(actress['height'],height_list)

        #准备数据
        height = np.array(height_list)
        waist = np.array([row["waist"] for row in data])#腰围
        bust = np.array([row["bust"] for row in data])#胸围
        hip = np.array([row["hip"] for row in data])#臀围

        # 回归残差去掉身高对腰围的影响,现在的这个算法还是有问题，没法表现三围的联系，关联数值
        a, b = np.polyfit(height, waist, 1)
        pred = a * height + b
        waist_residual_list = waist - pred

        waist_residual=actress['waist']-(a*actress['height']+b)
        waist_rank=get_rank(waist_residual,waist_residual_list,True)

        a, b = np.polyfit(height, bust, 1)
        pred = a * height + b
        bust_residual_list = bust - pred

        bust_residual=actress['bust']-(a*actress['height']+b)
        bust_rank=get_rank(bust_residual,bust_residual_list)

        a, b = np.polyfit(height, hip, 1)
        pred = a * height + b
        hip_residual_list = hip - pred

        hip_residual=actress['hip']-(a*actress['height']+b)
        hip_rank=get_rank(hip_residual,hip_residual_list)

        
        #这个应该计算视觉突出比例，根据日本罩杯上胸围-下胸围的值为基础计算胸围与下胸围的比例，然后排序，这个越大效果越好
        '''
        日本罩杯 差
        AA      10
        A       12.5
        B       15
        C       17.5
        D       20
        '''
        cup_map = {chr(ord('A')+i): i+1 for i in range(15)}#罩杯的数值映射
        cup_map_jp={#举例A杯是9-11，B杯11.5-13.5  https://www.wacoal.jp/advice/contents/post-15.html
            "AA":7.5,
            "A":10,
            "B":12.5,
            "C":15,
            "D":17.5,
            "E":20,
            "F":22.5,
            "G":25,
            "H":27.5,
            "I":30,
            "J":32.5,
            "L":35,
            "M":37.5,
            "N":40,
            "O":42.5
        }
        cup_map_cn={#B杯是10-12.5
            "A":10,
            "B":12.5,
            "C":15,
            "D":17.5,
            "E":20,
            "F":22.5,
            "G":25,
            "H":27.5,
            "I":30,
            "J":32.5,
            "L":35,
            "M":37.5,
            "N":40
        }
        cup_list:list[str]=[row["cup"] for row in data]
        cup_diff_list=[cup_map_jp.get(cup.upper(), None) for cup in cup_list]
        cup_list
        
        low_bust_list=bust-cup_diff_list
        bust_ratio_list=bust/low_bust_list

        cup_diff=cup_map_jp.get(actress['cup'][0])#转上下胸围差
        #计算的是上胸围与下胸围的比例的排位
        bust_ratio=actress['bust']/(actress['bust']-cup_diff)
        logging.debug(f"胸围与下胸围的比例为{bust_ratio}")
        cup_rank=get_rank(bust_ratio,bust_ratio_list)

        #计算每个值在所有数据中的位次(0-1)

        values=[height_rank, cup_rank, bust_rank, waist_rank,hip_rank]

        arr=np.array(values)
        print(arr)
        result = np.round(np.sqrt(arr), 2)#开根号获得面积感官效果
        values=list(result)

        return values

    def calc_chain(self,actress_id):
        #计算名字链条
        from core.database.query import get_all_actress_name
        nodelist=get_all_actress_name(actress_id)
        all_redirects = {n["redirect"] for n in nodelist if n["redirect"] is not None}
        start_nodes = [n for n in nodelist if n["id"] not in all_redirects]#找到开始的节点，默认只有单链


        if not start_nodes:
            raise ValueError("找不到链条起点，可能存在环路或空列表")
        
        start_node = start_nodes[0]
        # 从起点形成顺序链条
        nodes_dict = {n["id"]: n for n in nodelist}#构建 ID → 节点字典
        chain:list[str] = []
        cur_node = start_node
        while cur_node:
            chain.append(cur_node["name"])
            next_id = cur_node.get("redirect")
            cur_node = nodes_dict.get(next_id)  # 如果 next_id 为 None 或不存在，就结束
        return chain

    def refresh():
        '''刷新'''

    @Slot()
    def on_clicked_heart(self):
        from core.database.insert import insert_liked_actress
        from core.database.delete import delete_favorite_actress
        if self.heart.get_statue():
            '''添加到喜欢'''
            insert_liked_actress(self._actress_id)
        else:
            '''删除'''
            delete_favorite_actress(self._actress_id)
