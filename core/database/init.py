import sqlite3
from config import DATABASE,PRIVATE_DATABASE,SQLPATH
import logging
from PySide6.QtSql import QSqlDatabase,QSqlQuery
from PySide6.QtWidgets import QMessageBox
from pathlib import Path
from .connection import QSqlDatabaseManager

def init_private_db():
    """
    初始化私有数据库，然后添加一些数据
    """
    db_path=PRIVATE_DATABASE
    db_path.parent.mkdir(parents=True, exist_ok=True)#上层目录一定要存在
    need_init = not db_path.exists()  # 判断数据库是否需要初始化
    with sqlite3.connect(db_path) as conn:
        if need_init:
            logging.info(f"数据库 {db_path} 不存在，正在初始化...")
            with open(Path(SQLPATH/"initPrivateTable.sql"), "r", encoding="utf-8") as f:
                sql_script = f.read()
            conn.executescript(sql_script)  # 一次性执行建库SQL
            conn.commit()
            logging.info("数据库初始化完成")
        else:
            logging.info(f"数据库 {db_path} 已存在，直接使用")


def init_public_db(db_path:str):
    """
    初始化公有数据库，然后添加一些数据

    """
    pass


def init_database(public_db_path: Path, private_db_path: Path) -> bool:
    """初始化数据库连接
    
    Returns:
        bool: 是否成功初始化所有连接
    """
    db_manager = QSqlDatabaseManager()
    
    # 创建公共数据库连接
    if not db_manager.create_connection("public", public_db_path):
        return False
        
    # 创建私有数据库连接
    if not db_manager.create_connection("private", private_db_path):
        #连不上就创建
        return False
        
    return True
