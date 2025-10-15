#个人女优详细的面板

from PySide6.QtWidgets import QWidget,QVBoxLayout,QSizePolicy
from PySide6.QtCore import Qt,Slot,Signal
import logging,sqlite3
from ui.basic import LazyScrollArea
from ui.widgets import SingleActressInfo
from ui.widgets import CoverCard
from config import DATABASE
from ui.base import LazyWidget

class SingleActressPage(LazyWidget):
    def __init__(self):
        super().__init__()

    def _lazy_load(self):
        logging.info("----------加载单独女优界面----------")
        self._actress_id=None
        self.actress=True
        self.order="按发布时间顺序"
        self.scope="全库"

        self.single_actress_info=SingleActressInfo()
        
        spacer_widget = QWidget()
        spacer_widget.setFixedHeight(70)

        self.lazy_area = LazyScrollArea(column_width=220,widget=self.single_actress_info,hint=False)
        self.lazy_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        mainlayout = QVBoxLayout(self)
        mainlayout.setContentsMargins(0, 0, 0, 0)
        mainlayout.addWidget(spacer_widget)
        mainlayout.addWidget(self.lazy_area)



    def update(self,actress_id):
        self.single_actress_info.update(actress_id)
        self._actress_id=actress_id
        self.lazy_area.set_loader(self.load_page)


    def load_data(self, page_index: int, page_size: int)->tuple:
        """返回一个页面的 CoverCard 所需要的数据,这个是非常的快的，不消耗时间"""
        offset = page_index * page_size

        # 动态拼接 SQL,要怎么筛逻辑都在这里改
        params=[]
        query=f'''
SELECT 
    work.serial_number, 
    cn_title, 
    image_url,
    wtr.tag_id,
    work.work_id,
    CASE 
        WHEN (SELECT cn_name FROM maker WHERE maker_id =p.maker_id) IS NULL
        THEN 0
        ELSE 1
    END AS standard
FROM work
JOIN work_actress_relation war ON war.work_id=work.work_id

LEFT JOIN work_tag_relation wtr ON work.work_id = wtr.work_id AND wtr.tag_id IN (1, 2, 3)
LEFT JOIN 
    prefix_maker_relation p ON p.prefix = SUBSTR(work.serial_number, 1, INSTR(work.serial_number, '-') - 1)
WHERE war.actress_id=?
ORDER BY work.release_date DESC
        '''
        params.extend([self._actress_id])

        query +=f"LIMIT ? OFFSET ?"#最后拼这个
        params.extend([page_size, offset])
        #logging.debug(f"WorkPageExecute SQL\n{query}")

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(query,params)
            results=cursor.fetchall()
        return results

    def load_page(self, page_index: int, page_size: int) -> list[CoverCard]:
        """返回一个页面的 CoverCard 列表，在这里进行实际的构造"""
        data=self.load_data(page_index,page_size)
        if not data:
            return None
        result = []
        for serial_number, title, cover_path,tag_id,work_id,standard in data:
            match tag_id:
                case 1:
                    color="#80B0F8"
                case 2:
                    color="#F88441"
                case 3:  
                    color="#FDEB48"
                case None:
                    color="#00000000"
            card = CoverCard(title, cover_path, serial_number,work_id,bool(standard),color=color)

            result.append(card)
        return result

