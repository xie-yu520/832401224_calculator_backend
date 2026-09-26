"""计算历史领域模型，与 ``calculation_history`` 表一一对应。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
from datetime import datetime, timedelta, timezone

from ..config import Config

# 固定使用 UTC+8 展示时间，避免依赖服务器本地时区
DISPLAY_TIMEZONE = timezone(timedelta(hours=Config.TIMEZONE_OFFSET_HOURS))

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def current_timestamp() -> str:
    """返回当前时间的字符串表示（UTC+8）。"""
    return datetime.now(DISPLAY_TIMEZONE).strftime(TIME_FORMAT)


@dataclass
class CalculationHistory:
    """一条计算历史记录。"""

    expression: str
    result: float
    created_at: str
    id: Optional[int] = None
    is_favorite: bool = False

    @classmethod
    def create(cls, expression: str, result: float) -> "CalculationHistory":
        """工厂方法：按当前时间创建一条新记录。"""
        return cls(
            expression=expression,
            result=result,
            created_at=current_timestamp(),
        )

    @classmethod
    def from_row(cls, row: Any) -> "CalculationHistory":
        """从 sqlite3.Row 构造对象。"""
        data = dict(row)
        return cls(
            id=data.get("id"),
            expression=data["expression"],
            result=data["result"],
            created_at=data["created_at"],
            is_favorite=bool(data.get("is_favorite", 0)),
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为 API 响应所需的字典。"""
        return {
            "id": self.id,
            "expression": self.expression,
            "result": self.result,
            "created_at": self.created_at,
            "is_favorite": self.is_favorite,
        }
