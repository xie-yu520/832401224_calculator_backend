"""计算服务：串联「解析计算 -> 落库 -> 返回」的完整用例。"""

from __future__ import annotations

from typing import Any, Dict

from ..calculator import evaluate_expression
from ..model.calculation_history import CalculationHistory
from ..repository.history_repository import HistoryRepository


class CalculatorService:
    """计算器核心用例。"""

    @staticmethod
    def calculate(raw_expression: str) -> Dict[str, Any]:
        """计算表达式并写入历史。

        顺序刻意设计为「先算后存」：只有成功算出结果才落库，
        失败的输入不会污染历史记录。

        Raises:
            CalculatorError: 表达式非法、除零、定义域错误等。
        """
        if not isinstance(raw_expression, str):
            raise TypeError("expression must be a string")

        # 1) 后端完成全部计算（前端不参与任何运算）
        result = evaluate_expression(raw_expression)
        normalized = raw_expression.strip()

        # 2) 持久化到数据库
        record = HistoryRepository.insert(
            CalculationHistory.create(expression=normalized, result=result)
        )

        # 3) 组装响应
        payload = record.to_dict()
        payload["success"] = True
        return payload
