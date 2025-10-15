# 数据库连接管理

from PySide6.QtSql import QSqlDatabase, QSqlQuery
from typing import Optional, Dict
import logging
from pathlib import Path
import sqlite3
from sqlite3 import Connection, Cursor
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime


class QSqlDatabaseManager:
    """数据库连接管理类
    
    使用单例模式确保整个应用只有一个数据库管理器实例
    """
    _instance = None
    _connections: Dict[str, QSqlDatabase] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QSqlDatabaseManager, cls).__new__(cls)
            cls._instance._init_logger()
        return cls._instance
    
    def _init_logger(self):
        """初始化日志"""
        self.logger = logging.getLogger(__name__)
        
    def create_connection(self, name: str, database_path: Path) -> bool:
        """创建新的数据库连接
        
        Args:
            name: 连接名称（如 "public", "private"）
            database_path: 数据库文件路径
            
        Returns:
            bool: 是否成功创建连接
            
        Example:
            db_manager = DatabaseManager()
            db_manager.create_connection("public", Path("public.db"))
        """
        try:
            # 如果已存在同名连接，先移除
            if name in QSqlDatabase.connectionNames():
                self.logger.debug(f"移除已存在的连接: {name}")
                QSqlDatabase.removeDatabase(name)
            
            # 创建新连接
            db = QSqlDatabase.addDatabase("QSQLITE", name)
            db.setDatabaseName(str(database_path))
            
            if not db.open():
                self.logger.error(f"无法打开数据库 {name}: {db.lastError().text()}")
                return False
                
            # 设置数据库选项
            query = QSqlQuery(db)
            query.exec("PRAGMA foreign_keys = ON;")  # 启用外键约束
            query.exec("PRAGMA journal_mode = WAL;") # 使用 WAL 模式提高性能
            
            self._connections[name] = db
            self.logger.info(f"成功创建数据库连接: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"创建数据库连接失败: {str(e)}")
            return False
    
    def get_connection(self, name: str) -> Optional[QSqlDatabase]:
        """获取指定名称的数据库连接
        
        Args:
            name: 连接名称
            
        Returns:
            Optional[QSqlDatabase]: 数据库连接对象，如果不存在返回None
            
        Example:
            db = db_manager.get_connection("public")
            if db:
                query = QSqlQuery(db)
                # 使用查询...
        """
        db = QSqlDatabase.database(name)
        if not db.isValid():
            self.logger.error(f"无效的数据库连接: {name}")
            return None
        return db
    
    def close_connection(self, name: str):
        """关闭指定的数据库连接（在关闭前做 WAL checkpoint）"""
        if name in self._connections:
            db = self._connections[name]
            if db.isOpen():
                try:
                    self.logger.debug(f"执行 WAL checkpoint: {name}")
                    query = QSqlQuery(db)
                    query.exec("PRAGMA wal_checkpoint(FULL);")
                    query.exec("PRAGMA journal_mode=DELETE;")#强制切回DELETE模式，为了清除-wal模式
                except Exception as e:
                    self.logger.error(f"WAL checkpoint 执行失败: {e}")
                finally:
                    db.close()
            QSqlDatabase.removeDatabase(name)
            del self._connections[name]
            self.logger.info(f"已关闭数据库连接: {name}")
    
    def close_all(self):
        """关闭所有数据库连接"""
        for name in list(self._connections.keys()):
            self.close_connection(name)
        self.logger.info("已关闭所有数据库连接")


    def execute_query(self, connection_name: str, sql: str, params: tuple = ()) -> Optional[QSqlQuery]:
        """执行SQL查询
        
        Args:
            connection_name: 连接名称
            sql: SQL查询语句
            params: 查询参数
            
        Returns:
            Optional[QSqlQuery]: 查询结果
            
        Example:
            query = db_manager.execute_query("public", 
                "SELECT * FROM works WHERE id = ?", 
                (work_id,))
            if query and query.next():
                # 处理结果...
        """
        db = self.get_connection(connection_name)
        if not db:
            return None
            
        try:
            query = QSqlQuery(db)
            query.prepare(sql)
            
            # 绑定参数
            for param in params:
                query.addBindValue(param)
                
            if not query.exec():
                self.logger.error(f"查询执行失败: {query.lastError().text()}")
                return None
                
            return query
            
        except Exception as e:
            self.logger.error(f"执行查询时出错: {str(e)}")
            return None
    
    def begin_transaction(self, connection_name: str) -> bool:
        """开始事务
        
        Args:
            connection_name: 连接名称
            
        Returns:
            bool: 是否成功开始事务
        """
        db = self.get_connection(connection_name)
        if not db:
            return False
        return db.transaction()
    
    def commit(self, connection_name: str) -> bool:
        """提交事务"""
        db = self.get_connection(connection_name)
        if not db:
            return False
        return db.commit()
    
    def rollback(self, connection_name: str) -> bool:
        """回滚事务"""
        db = self.get_connection(connection_name)
        if not db:
            return False
        return db.rollback()
    
    def __del__(self):
        """确保在对象销毁时关闭所有连接"""
        self.close_all()


def get_connection(database,readonly=False)->Connection:
    """
    获取一个SQLite连接，并开启 WAL 与 外键约束
    readonly: True -> 只读模式
    """
    mode = "ro" if readonly else "rwc"  # ro=只读, rwc=可读写，不存在则创建
    conn = sqlite3.connect(f"file:{database}?mode={mode}", uri=True)
    cursor:Cursor = conn.cursor()
    
    # 开启 WAL 模式
    #cursor.execute("PRAGMA journal_mode=WAL;")#这个只需要设置一次就可以了，这个数文件属性
    # 开启外键约束
    cursor.execute("PRAGMA foreign_keys=ON;")
    # 设置繁忙超时
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn