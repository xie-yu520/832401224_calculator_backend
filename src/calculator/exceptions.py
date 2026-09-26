"""计算器领域异常定义。

每个异常都携带一个稳定的错误码（``code``）和建议的 HTTP 状态码。
后端把 code/message 写进 API 响应，前端按 code 映射成中文提示。
"""

from __future__ import annotations

from typing import Dict


class CalculatorError(Exception):
    """计算器异常基类。"""

    code = "CALCULATOR_ERROR"
    http_status = 400
    default_message = "Calculation failed"

    def __init__(self, message: str | None = None, code: str | None = None) -> None:
        """初始化异常，未显式给出 message 时使用类默认文案。"""
        self.message = message or self.default_message
        if code:
            self.code = code
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, str]:
        """转换为可直接写入 JSON 响应的字典。"""
        return {"code": self.code, "message": self.message}


class EmptyExpressionError(CalculatorError):
    """表达式为空。"""

    code = "EMPTY_EXPRESSION"
    default_message = "Expression must not be empty"


class ExpressionTooLongError(CalculatorError):
    """表达式超出长度上限。"""

    code = "EXPRESSION_TOO_LONG"
    default_message = "Expression is too long"


class InvalidCharacterError(CalculatorError):
    """表达式中出现白名单之外的字符。"""

    code = "INVALID_CHARACTER"
    default_message = "Invalid character in expression"


class InvalidExpressionError(CalculatorError):
    """表达式语法不正确（括号不匹配、运算符缺失等）。"""

    code = "INVALID_EXPRESSION"
    default_message = "Invalid expression"


class DivisionByZeroError(CalculatorError):
    """除数为零。"""

    code = "DIVISION_BY_ZERO"
    default_message = "Division by zero"


class MathDomainError(CalculatorError):
    """数学定义域错误，例如 sqrt(-1)、ln(0)、asin(2)。"""

    code = "MATH_DOMAIN_ERROR"
    default_message = "Math domain error"


class ResultOverflowError(CalculatorError):
    """结果溢出或不是有限实数。"""

    code = "RESULT_OVERFLOW"
    default_message = "Result is out of range"


class UnknownFunctionError(CalculatorError):
    """调用了未支持的函数。"""

    code = "UNKNOWN_FUNCTION"
    default_message = "Unknown function"


class UnknownConstantError(CalculatorError):
    """使用了未支持的常量。"""

    code = "UNKNOWN_CONSTANT"
    default_message = "Unknown constant"
