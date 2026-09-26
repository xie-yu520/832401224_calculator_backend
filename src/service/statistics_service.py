"""统计服务（扩展功能）：汇总历史使用情况。"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict

from ..repository.history_repository import HistoryRepository

# 统计出现次数的运算符（按出现频次排序用）
_OPERATOR_PATTERN = re.compile(r"[+\-*/%^]")

_OPERATOR_LABELS = {
    "+": "加法 +",
    "-": "减法 -",
    "*": "乘法 ×",
    "/": "除法 ÷",
    "%": "取模 %",
    "^": "乘方 ^",
}


class StatisticsService:
    """计算历史统计分析。"""

    @staticmethod
    def overview() -> Dict[str, Any]:
        """返回总览统计：总量、收藏量、结果极值/均值、最常用运算符。"""
        raw = HistoryRepository.statistics()
        total = int(raw.get("total", 0))

        # 抽样最近的 200 条来做运算符频次统计，避免全表扫描
        recent = HistoryRepository.find_all(limit=200, offset=0)
        counter: Counter = Counter()
        for record in recent:
            counter.update(_OPERATOR_PATTERN.findall(record.expression))

        operator_counts = {
            _OPERATOR_LABELS.get(op, op): count for op, count in counter.most_common()
        }
        most_used = (
            _OPERATOR_LABELS.get(counter.most_common(1)[0][0], "-")
            if counter
            else "暂无数据"
        )

        return {
            "total_calculations": total,
            "favorite_count": int(raw.get("favorite_count", 0)),
            "min_result": round(float(raw.get("min_result", 0)), 6),
            "max_result": round(float(raw.get("max_result", 0)), 6),
            "average_result": round(float(raw.get("avg_result", 0)), 6),
            "first_calculation_at": raw.get("first_at", ""),
            "last_calculation_at": raw.get("last_at", ""),
            "most_used_operator": most_used,
            "operator_counts": operator_counts,
        }
