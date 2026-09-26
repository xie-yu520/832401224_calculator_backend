"""表达式计算核心包。

对外只暴露 ``evaluate_expression`` 一个入口：
``字符串表达式 -> 词法分析 -> 语法分析 -> AST 求值 -> 浮点结果``。

全程不使用 eval / exec，杜绝任意代码执行风险。
"""

from .exceptions import (
    CalculatorError,
    DivisionByZeroError,
    EmptyExpressionError,
    ExpressionTooLongError,
    InvalidCharacterError,
    InvalidExpressionError,
    MathDomainError,
    ResultOverflowError,
    UnknownConstantError,
    UnknownFunctionError,
)
from .expression import evaluate_expression

__all__ = [
    "CalculatorError",
    "DivisionByZeroError",
    "EmptyExpressionError",
    "ExpressionTooLongError",
    "InvalidCharacterError",
    "InvalidExpressionError",
    "MathDomainError",
    "ResultOverflowError",
    "UnknownConstantError",
    "UnknownFunctionError",
    "evaluate_expression",
]
