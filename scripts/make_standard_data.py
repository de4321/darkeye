import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#运行后制作标准数据集

from core.database.db_utils import generate_standard_db,clear_actor,clear_actress

#制作前请备份public与private
#这个会改变私库的
generate_standard_db()
clear_actor()
clear_actress()