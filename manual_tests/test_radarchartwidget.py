import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#---------------------------------------------------------------------------------------------------



from PySide6.QtWidgets import QApplication

from ui.statistics import RadarChartWidget

if __name__ == "__main__":
    app = QApplication(sys.argv)

    categories = ["身高", "罩杯", "胸围", "腰围", "臀围"]
    values = [0.5, 0.8, 0.3, 0.5, 0.6]
    show_values=[160,"F",90,60,90]

    widget = RadarChartWidget()
    widget.resize(600, 600)
    widget.update_chart(categories,values,show_values)
    
    widget.show()

    sys.exit(app.exec())
