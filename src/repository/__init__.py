"""数据访问层：封装 SQLite 连接与表操作。"""

from .database import get_connection, init_database
from .history_repository import HistoryRepository

__all__ = ["HistoryRepository", "get_connection", "init_database"]
