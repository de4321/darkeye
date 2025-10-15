import os,logging
import sqlite3
from datetime import datetime
import shutil
from pathlib import Path


def backup_database(database:Path,backup_dir:Path)->str:
    #这个也有未知情况下的问题
    #将目标database文件复制到backup_dir备份的文件夹下并打上时间戳
    # 创建 backup 文件夹
    #backup_dir = os.path.join(os.path.dirname(db_path), "av_backup")
    os.makedirs(backup_dir, exist_ok=True)

    # 时间戳格式的文件名
    timestamp = datetime.now().strftime("backup-%Y-%m-%d-%H-%M-%S.db")
    backup_path = os.path.join(backup_dir, timestamp)

    # 原子备份（安全）
    with sqlite3.connect(database) as src_conn:
        with sqlite3.connect(backup_path) as backup_conn:
            src_conn.backup(backup_conn)
            logging.info(f"已使用 sqlite3 原子备份方式成功备份到: {backup_path}")
    return backup_path

def restore_database(backup_path: Path, target_path: Path) -> bool:
    #将备份的.db文件复制到目标.db目录下
    #这个有风险需要后面更改
    if not backup_path.exists():
        return False
    try:
        shutil.copy(backup_path, target_path)
        logging.info("还原数据库成功")
        return True
    except Exception as e:
        logging.warning(f"[ERROR] Restore failed: {e}")
        return False

def restore_backup_safely(backup_db: Path,active_db: Path)->bool:
    """
    安全恢复备份到正在被连接的 SQLite 数据库。
    不会直接覆盖文件，而是通过 SQL 将数据写入 active_db。

    :param active_db: 正在使用的数据库文件路径
    :param backup_db: 备份数据库文件路径
    """
    active_conn = sqlite3.connect(active_db)
    success=False
    try:
        # ATTACH 备份数据库
        active_conn.execute(f"ATTACH DATABASE '{backup_db}' AS backup_db;")
        active_conn.execute("PRAGMA foreign_keys=OFF;")  # 临时关闭外键约束

        # 获取备份数据库中所有表
        tables = active_conn.execute(
            "SELECT name FROM backup_db.sqlite_master WHERE type='table';"
        ).fetchall()
        #logging.debug(tables)
        with active_conn:
            for (table_name,) in tables:
                # 清空当前数据库中的表
                active_conn.execute(f"DELETE FROM {table_name};")
                # 从备份中插入数据
                active_conn.execute(
                    f"INSERT INTO {table_name} SELECT * FROM backup_db.{table_name};"
                )

        active_conn.execute("PRAGMA foreign_keys=ON;")  # 恢复外键约束
        active_conn.execute("DETACH DATABASE backup_db;")
        active_conn.execute("PRAGMA wal_checkpoint(FULL);")
        logging.info(f"已安全恢复备份 {backup_db} 到 {active_db}")
        success=True
    except Exception as e:
        logging.warning(f"[ERROR] Restore failed: {e}")
        success=False
    finally:
        active_conn.close()
        return success



#这里要写根据哈希的增量备份，比较的麻烦 dirsync
import hashlib

def file_hash(path:str):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()