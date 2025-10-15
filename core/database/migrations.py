#这里是迁移数据库的，在软件启动的时候检测数据库与软件所需要的数据库版本是否一致，否则进行升级
import sqlite3
from sqlite3 import Connection
from .connection import get_connection
import logging

def get_db_version(conn:Connection):
    cur = conn.execute("SELECT version FROM db_version ORDER BY applied_at DESC LIMIT 1;")
    row = cur.fetchone()
    return row[0] if row else None

def set_db_version(conn:Connection, version:str, description:str=""):
    conn.execute(
        "INSERT INTO db_version (version, description) VALUES (?, ?)",
        (version, description)
    )
    conn.commit()


from config import REQUIRED_PRIVATE_DB_VERSION,REQUIRED_PUBLIC_DB_VERSION,DATABASE,PRIVATE_DATABASE

def upgrade_public_db(conn, current_version):
    """执行数据库升级逻辑"""
    logging.info(f"公共数据库版本从 {current_version or '无版本'} 升级到 {REQUIRED_PUBLIC_DB_VERSION}")
    #当版本库不一致时就一直不断的升级 
    # 示例升级脚本
    if current_version == "1.0.0":
        logging.info("→ 执行 1.0.0 → 1.1.0 升级...")
        # 举例：新增字段
        # 执行标准
        set_db_version(conn, "1.1.0", "新增字段 birth_date")
    
    # 还可以继续往下扩展版本升级逻辑
    # elif current_version == "1.1.0":
    #     ...

def upgrade_private_db(conn, current_version):
    """执行数据库升级逻辑"""
    logging.info(f"公共数据库版本从 {current_version or '无版本'} 升级到 {REQUIRED_PRIVATE_DB_VERSION}")

    # 示例升级脚本
    if current_version == "1.0.0":
        logging.info("→ 执行 1.0.0 → 1.1.0 升级...")
        # 举例：新增字段
        # 执行标准
        set_db_version(conn, "1.1.0", "新增字段 birth_date")
    
    # 还可以继续往下扩展版本升级逻辑
    # elif current_version == "1.1.0":
    #     ...

def check_and_upgrade_public_db():
    conn=get_connection(DATABASE)

    current_version = get_db_version(conn)
    logging.info(f"当前公共数据库版本：{current_version}")

    if current_version != REQUIRED_PUBLIC_DB_VERSION:
        upgrade_public_db(conn, current_version)
    else:
        logging.info("公共数据库版本匹配，无需升级。")
    conn.close()

def check_and_upgrade_private_db():
    conn=get_connection(PRIVATE_DATABASE)

    current_version = get_db_version(conn)
    logging.info(f"当前私有数据库版本：{current_version}" )

    if current_version != REQUIRED_PRIVATE_DB_VERSION:
        upgrade_private_db(conn, current_version)
    else:
        logging.info("私有数据库版本匹配，无需升级。")
    conn.close()