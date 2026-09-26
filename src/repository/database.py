"""SQLite 连接管理与建表。

使用标准库 sqlite3，无需额外安装数据库服务；
数据库文件路径可通过环境变量 ``CALCULATOR_DB_PATH`` 覆盖，便于云端部署。
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from ..config import Config

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS calculation_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    expression  TEXT    NOT NULL,
    result      REAL    NOT NULL,
    created_at  TEXT    NOT NULL,
    is_favorite INTEGER NOT NULL DEFAULT 0
);
"""

CREATE_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_history_created_at
    ON calculation_history (created_at DESC);
"""


def get_database_path() -> Path:
    """返回数据库文件路径。"""
    return Path(Config.DB_PATH)


@contextmanager
def get_connection():
    """获取数据库连接（上下文管理器自动提交/关闭）。"""
    path = get_database_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(str(path), timeout=10)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_database() -> None:
    """初始化数据表与索引（幂等，可重复执行）。"""
    with get_connection() as connection:
        connection.execute(CREATE_TABLE_SQL)
        connection.execute(CREATE_INDEX_SQL)
