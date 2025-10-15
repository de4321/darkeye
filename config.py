# config.py
import sys
import configparser
from pathlib import Path
from PySide6.QtCore import QSettings,QSize,QPoint
import logging
#所有的配置文件都在这里，包括资源的地址等等


#==========================================================
APP_VERSION = "1.0.0"
REQUIRED_PUBLIC_DB_VERSION = "1.0"#软件所需要的公共数据库版本
REQUIRED_PRIVATE_DB_VERSION = "1.0"#软件所需要的私有数据库版本
#==========================================================


# ==========  路径适配打包 ==========
def resource_path(relative_path):
    """获取资源的绝对路径，兼容 PyInstaller 和 Nuitka 打包"""
    
    if getattr(sys, 'frozen', False):# 检查程序是否为打包版本（通用标记）
        if hasattr(sys, "_MEIPASS"):# 兼容 PyInstaller 的 _MEIPASS 模式 这个是给--onefile模式使用的
            base_path = Path(sys._MEIPASS)
        else:# 兼容 Nuitka 和其他打包器，它们通常使用可执行文件的路径
            base_path = Path(sys.executable).parent
    else:
        base_path = Path(__file__).parent # 如果是未打包的开发环境，使用脚本所在路径

    return base_path / relative_path

# ==========  加载 settings.ini ==========
INI_FILE = resource_path("settings.ini")
parser = configparser.ConfigParser()
parser.read(INI_FILE, encoding="utf-8")

settings = QSettings(str(INI_FILE), QSettings.Format.IniFormat)#QSettings管理



BASE_DIR = resource_path("")

#这里后面还有绝对路径与相对路径的切换的问题

def get_PATH(key:str,default_value:str)->Path:
    '''用于通用从.ini中读取相对路径地址的函数'''
    path=settings.value(key)

    if path==None:#配置中无地址，写入默认地址，结束函数
        logging.info(f"Settings.ini文件中不存在{key}地址配置,写入默认地址")
        settings.setValue(key, default_value)
        settings.sync()
        path = default_value
        return resource_path(path)

    if not Path(path).exists():#配置中有地址，但是地址在电脑中是不存在的，也写入默认地址，并结束函数
        logging.info(f"Settings.ini文件中存在{key}地址配置,{path}地址不存在于电脑中，覆盖写入默认地址")
        settings.setValue(key, default_value)
        settings.sync()
        path = default_value
        return resource_path(path)
    
    return resource_path(path)#正常情况下返回地址

DATABASE = get_PATH("Paths/Database","resources/public/public.db")#公共数据库文件地址
DATABASE_BACKUP_PATH=get_PATH("Paths/DatabaseBackups","resources/public/public_backup/")#公共数据库备份地址
ACTRESSIMAGES_PATH=get_PATH("Paths/Actressimages","resources/public/actressimages/")#女优头像的地址
ACTORIMAGES_PATH=get_PATH("Paths/Actorimages","resources/public/actorimages/")#男优头像的地址


WORKCOVER_PATH=get_PATH("Paths/WorkCovers","resources/public/workcovers/")#作品封面的地址

PRIVATE_DATABASE=get_PATH("Paths/PrivateDatabase","resources/private/private.db")#私有数据库文件地址
PRIVATE_DATABASE_BACKUP_PATH=get_PATH("Paths/PrivateDatabaseBackups","resources/private/private_backup/")#私有数据库库备份地址

SENSITIVE_WORDS_PATH=get_PATH("Paths/SensitiveWords","resources/config/sensitive_words.txt")#敏感词文件地址

TAG_MAP_PATH=get_PATH("Paths/TagMap","resources/config/tag_map.json")#敏感词文件地址

SQLPATH=get_PATH("Paths/Sql","resources/sql/")
ICONS_PATH = get_PATH("Paths/Icons","resources/icons/")#软件图标的地址
TEMP_PATH=get_PATH("Paths/Temp","resources/temp/")#存一些临时文件，包括图片等等
LOG_FILE=get_PATH("Paths/LogFile","log/app.log")#log文件的位置
QSS_PATH=get_PATH("Paths/QSS","styles/")#qss文件的位置

def get_video_path():
    '''获得视频地址，这个是用户自己填的绝对路径'''
    key = "Paths/Videos"
    default_value = "D:/AV/"#这个是绝对地址
    path=settings.value(key)

    if path==None:#配置中无地址，写入默认地址，结束函数
        logging.info(f"Settings.ini文件中不存在{key}地址配置,写入默认地址")
        settings.setValue(key, default_value)
        settings.sync()
        path = default_value
        return Path(path)

    if not Path(path).exists():#配置中有地址，但是地址在电脑中是不存在的，也写入默认地址，并结束函数
        logging.info(f"Settings.ini文件中存在{key}地址配置,{path}地址不存在于电脑中，覆盖写入默认地址")
        settings.setValue(key, default_value)
        settings.sync()
        path = default_value
        return Path(path)
    
    return Path(path)

VIDEO_PATH=get_video_path()#视频文件地址

def check_file():
    '''检查文件夹是否存在并建立'''
    TEMP_PATH.mkdir(parents=True, exist_ok=True) 
    WORKCOVER_PATH.mkdir(parents=True, exist_ok=True) 
    ACTRESSIMAGES_PATH.mkdir(parents=True, exist_ok=True) 

def get_size_pos():
    '''获得.ini中的size和pos数据'''
    size = settings.value("window/size", QSize(800, 600))
    pos = settings.value("window/pos", QPoint(100, 100))
    return size,pos

def set_size_pos(size:QSize,pos:QPoint):
    '''将size和pos数据写入.ini'''
    settings.setValue("window/size", size)
    settings.setValue("window/pos", pos)

def is_max_window():
    '''获得.ini中的是否最大化的值，默认是没有'''
    return settings.value("window/maximized", False, type=bool)

def set_max_window(is_max_window:bool):
    '''记录窗口在退出的时候是否最大化的'''
    settings.setValue("window/maximized", is_max_window)

def is_first_lunch()->bool:
    '''判断软件是否第一次启动'''
    if  settings.value("window/first_lunch", True, type=bool):
        settings.setValue("window/first_lunch", False)
        return True
    else:
        return False

def set_first_luch(value:bool):
    '''设置启动值'''
    settings.setValue("window/first_lunch", value)