
from PySide6.QtWidgets import QWidget,QVBoxLayout,QTabWidget
from .PlotTabPage import PlotTabPage
from .PersonalDataPage import PersonalDataPage
class StatisticsPage(QWidget):
    def __init__(self):
        super().__init__()
        
        mainlayout = QVBoxLayout(self)
        mainlayout.setContentsMargins(0, 0, 0, 0)
        
        mainlayout.addSpacing(70)
        
        self.tab_widget=QTabWidget()
        plot_tabpage=PlotTabPage()
        p_datapage=PersonalDataPage()
        self.tab_widget.addTab(p_datapage,"信息面版")
        self.tab_widget.addTab(plot_tabpage,"统计")

        mainlayout.addWidget(self.tab_widget)


