"""计算历史的数据访问对象（DAO）。

所有 SQL 都集中在这一层，Service 只与领域对象打交道。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..model.calculation_history import CalculationHistory
from .database import get_connection


class HistoryRepository:
    """``calculation_history`` 表的增删改查。"""

    @staticmethod
    def insert(history: CalculationHistory) -> CalculationHistory:
        """插入一条记录，并把自增 id 回填到对象上。"""
        sql = """
        INSERT INTO calculation_history (expression, result, created_at, is_favorite)
        VALUES (?, ?, ?, ?)
        """
        with get_connection() as connection:
            cursor = connection.execute(
                sql,
                (
                    history.expression,
                    history.result,
                    history.created_at,
                    int(history.is_favorite),
                ),
            )
            history.id = cursor.lastrowid
        return history

    @staticmethod
    def find_by_id(history_id: int) -> Optional[CalculationHistory]:
        """按主键查询单条记录。"""
        sql = "SELECT * FROM calculation_history WHERE id = ?"
        with get_connection() as connection:
            row = connection.execute(sql, (history_id,)).fetchone()
        return CalculationHistory.from_row(row) if row else None

    @staticmethod
    def find_all(
        limit: int,
        offset: int,
        keyword: str = "",
        only_favorite: bool = False,
    ) -> List[CalculationHistory]:
        """分页查询历史，支持关键字搜索与收藏过滤。

        排序规则：收藏优先，其次按时间倒序、id 倒序。
        """
        conditions = []
        parameters: List[Any] = []

        if keyword:
            # LIKE 中的 % _ 需要转义，避免用户输入被当作通配符
            escaped = keyword.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            conditions.append("(expression LIKE ? ESCAPE '\\' OR CAST(result AS TEXT) LIKE ? ESCAPE '\\')")
            parameters.extend([f"%{escaped}%", f"%{escaped}%"])

        if only_favorite:
            conditions.append("is_favorite = 1")

        where_clause = f" WHERE {' AND '.join(conditions)}" if conditions else ""
        sql = f"""
        SELECT * FROM calculation_history
        {where_clause}
        ORDER BY is_favorite DESC, created_at DESC, id DESC
        LIMIT ? OFFSET ?
        """
        parameters.extend([limit, offset])

        with get_connection() as connection:
            rows = connection.execute(sql, parameters).fetchall()
        return [CalculationHistory.from_row(row) for row in rows]

    @staticmethod
    def count(keyword: str = "", only_favorite: bool = False) -> int:
        """统计满足条件的记录总数，用于分页。"""
        conditions = []
        parameters: List[Any] = []

        if keyword:
            escaped = keyword.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            conditions.append("(expression LIKE ? ESCAPE '\\' OR CAST(result AS TEXT) LIKE ? ESCAPE '\\')")
            parameters.extend([f"%{escaped}%", f"%{escaped}%"])

        if only_favorite:
            conditions.append("is_favorite = 1")

        where_clause = f" WHERE {' AND '.join(conditions)}" if conditions else ""
        sql = f"SELECT COUNT(*) AS total FROM calculation_history{where_clause}"

        with get_connection() as connection:
            row = connection.execute(sql, parameters).fetchone()
        return int(row["total"])

    @staticmethod
    def delete_by_id(history_id: int) -> bool:
        """删除指定记录，返回是否真的删掉了数据。"""
        sql = "DELETE FROM calculation_history WHERE id = ?"
        with get_connection() as connection:
            cursor = connection.execute(sql, (history_id,))
        return cursor.rowcount > 0

    @staticmethod
    def delete_all() -> int:
        """清空全部历史，返回被删除的行数。"""
        with get_connection() as connection:
            cursor = connection.execute("DELETE FROM calculation_history")
        return cursor.rowcount

    @staticmethod
    def toggle_favorite(history_id: int) -> Optional[CalculationHistory]:
        """切换收藏状态，返回更新后的记录。"""
        record = HistoryRepository.find_by_id(history_id)
        if record is None:
            return None

        new_value = 0 if record.is_favorite else 1
        sql = "UPDATE calculation_history SET is_favorite = ? WHERE id = ?"
        with get_connection() as connection:
            connection.execute(sql, (new_value, history_id))

        record.is_favorite = bool(new_value)
        return record

    @staticmethod
    def statistics() -> Dict[str, Any]:
        """聚合统计：总数、收藏数、结果极值与均值。"""
        sql = """
        SELECT
            COUNT(*)                    AS total,
            COALESCE(SUM(is_favorite), 0) AS favorite_count,
            COALESCE(MIN(result), 0)    AS min_result,
            COALESCE(MAX(result), 0)    AS max_result,
            COALESCE(AVG(result), 0)    AS avg_result,
            COALESCE(MIN(created_at), '') AS first_at,
            COALESCE(MAX(created_at), '') AS last_at
        FROM calculation_history
        """
        with get_connection() as connection:
            row = connection.execute(sql).fetchone()
        return dict(row)
