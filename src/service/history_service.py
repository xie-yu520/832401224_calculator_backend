"""历史服务：分页查询、删除、清空、收藏。"""

from __future__ import annotations

from typing import Any, Dict, List

from ..calculator import CalculatorError
from ..config import Config
from ..model.calculation_history import CalculationHistory
from ..repository.history_repository import HistoryRepository

# 收藏记录单独用一张表是不必要的，这里直接走 is_favorite 字段过滤


class HistoryNotFoundError(CalculatorError):
    """历史记录不存在。"""

    code = "HISTORY_NOT_FOUND"
    http_status = 404
    default_message = "History record not found"


class InvalidParameterError(CalculatorError):
    """分页参数非法。"""

    code = "INVALID_PARAMETER"
    http_status = 400
    default_message = "Invalid request parameter"


class HistoryService:
    """计算历史相关用例。"""

    @staticmethod
    def _normalize_paging(limit: Any, offset: Any) -> tuple[int, int]:
        """把分页参数收敛到合法区间，避免 SQL 注入与超大查询。"""
        try:
            limit_value = int(limit) if limit is not None else Config.DEFAULT_PAGE_SIZE
            offset_value = int(offset) if offset is not None else 0
        except (TypeError, ValueError) as exc:
            raise InvalidParameterError("limit and offset must be integers") from exc

        limit_value = max(1, min(limit_value, Config.MAX_PAGE_SIZE))
        offset_value = max(0, offset_value)
        return limit_value, offset_value

    @classmethod
    def list_history(
        cls,
        limit: Any = None,
        offset: Any = None,
        keyword: str = "",
        only_favorite: bool = False,
    ) -> Dict[str, Any]:
        """分页查询历史，附带总数与分页元信息。"""
        limit_value, offset_value = cls._normalize_paging(limit, offset)
        keyword = (keyword or "").strip()

        records: List[CalculationHistory] = HistoryRepository.find_all(
            limit=limit_value,
            offset=offset_value,
            keyword=keyword,
            only_favorite=only_favorite,
        )
        total = HistoryRepository.count(keyword=keyword, only_favorite=only_favorite)

        return {
            "items": [record.to_dict() for record in records],
            "total": total,
            "limit": limit_value,
            "offset": offset_value,
            "has_more": offset_value + len(records) < total,
        }

    @staticmethod
    def delete(history_id: int) -> None:
        """删除指定历史记录。

        Raises:
            HistoryNotFoundError: 记录不存在。
        """
        deleted = HistoryRepository.delete_by_id(history_id)
        if not deleted:
            raise HistoryNotFoundError()

    @staticmethod
    def clear_all() -> int:
        """清空全部历史，返回删除条数。"""
        return HistoryRepository.delete_all()

    @staticmethod
    def toggle_favorite(history_id: int) -> Dict[str, Any]:
        """切换收藏状态。

        Raises:
            HistoryNotFoundError: 记录不存在。
        """
        record = HistoryRepository.toggle_favorite(history_id)
        if record is None:
            raise HistoryNotFoundError()
        return record.to_dict()
