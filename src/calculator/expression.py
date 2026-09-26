"""表达式求值门面：串起「校验 -> 词法 -> 语法 -> 求值」全流程。

这是 Controller / Service 唯一需要调用的入口。
"""

from __future__ import annotations

import re

from ..config import Config
from .evaluator import evaluate, normalize_result
from .exceptions import (
    EmptyExpressionError,
    ExpressionTooLongError,
    InvalidCharacterError,
)
from .parser import parse
from .tokenizer import tokenize

# 把用户可能粘贴进来的全角/数学符号统一成 ASCII 运算符
_NORMALIZATION_TABLE = str.maketrans(
    {
        "×": "*",
        "✕": "*",
        "÷": "/",
        "−": "-",
        "–": "-",
        "—": "-",
        "＋": "+",
        "＊": "*",
        "／": "/",
        "（": "(",
        "）": ")",
        "，": ",",
        "％": "%",
        "＾": "^",
        "·": "*",
    }
)

# 字符白名单：只有这些字符才允许进入解析流程
_ALLOWED_PATTERN = re.compile(r"^[0-9A-Za-z_π+\-*/%^()., \t]+$")


def normalize_expression(expression: str) -> str:
    """去除首尾空白并把全角/数学符号替换为标准 ASCII 运算符。"""
    return expression.strip().translate(_NORMALIZATION_TABLE)


def validate(expression: str) -> None:
    """长度与字符白名单校验，挡掉明显的恶意/无效输入。

    Raises:
        EmptyExpressionError: 表达式为空。
        ExpressionTooLongError: 超过长度上限。
        InvalidCharacterError: 含白名单之外的字符。
    """
    if not expression:
        raise EmptyExpressionError()

    if len(expression) > Config.MAX_EXPRESSION_LENGTH:
        raise ExpressionTooLongError(
            f"Expression is too long (max {Config.MAX_EXPRESSION_LENGTH} characters)"
        )

    if not _ALLOWED_PATTERN.match(expression):
        raise InvalidCharacterError("Expression contains unsupported characters")


def evaluate_expression(expression: str) -> float:
    """计算表达式，返回结果；任何错误都以 CalculatorError 子类抛出。"""
    normalized = normalize_expression(expression)
    validate(normalized)
    return normalize_result(evaluate(parse(tokenize(normalized))))
