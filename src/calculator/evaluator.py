"""AST 求值器：遍历语法树计算最终结果。

只使用标准库 ``math``，不调用 eval / exec；
所有数学定义域错误与溢出都被翻译成明确的领域异常。
"""

from __future__ import annotations

import math
from typing import Callable, Dict, Sequence, Tuple

from .exceptions import (
    DivisionByZeroError,
    InvalidExpressionError,
    MathDomainError,
    ResultOverflowError,
    UnknownConstantError,
    UnknownFunctionError,
)
from .parser import AstNode, BinaryNode, ConstantNode, FunctionNode, NumberNode, UnaryNode

# 支持的数学常量
CONSTANTS: Dict[str, float] = {
    "pi": math.pi,
    "PI": math.pi,
    "π": math.pi,
    "e": math.e,
    "E": math.e,
    "tau": math.tau,
}

# 运算结果保留的小数位数，用于消除 0.1+0.2 这类浮点误差
RESULT_PRECISION = 10


def _factorial(value: float) -> float:
    if not float(value).is_integer() or value < 0:
        raise MathDomainError("factorial expects a non-negative integer")
    if value > 170:
        raise ResultOverflowError("factorial result is out of range")
    return float(math.factorial(int(value)))


def _power(base: float, exponent: float) -> float:
    try:
        result = base ** exponent
    except ZeroDivisionError as exc:
        raise DivisionByZeroError("Zero cannot be raised to a negative power") from exc
    except OverflowError as exc:
        raise ResultOverflowError("Result is out of range") from exc

    if isinstance(result, complex):
        raise MathDomainError("Result is not a real number")
    if math.isnan(result) or math.isinf(result):
        raise ResultOverflowError("Result is out of range")
    return result


# 函数表：名称 -> (参数个数, 实现)
FUNCTIONS: Dict[str, Tuple[int, Callable[..., float]]] = {
    # 三角函数（参数为弧度）
    "sin": (1, math.sin),
    "cos": (1, math.cos),
    "tan": (1, math.tan),
    "asin": (1, math.asin),
    "acos": (1, math.acos),
    "atan": (1, math.atan),
    "sinh": (1, math.sinh),
    "cosh": (1, math.cosh),
    "tanh": (1, math.tanh),
    # 对数与指数
    "ln": (1, math.log),
    "log": (1, math.log10),
    "log2": (1, math.log2),
    "exp": (1, math.exp),
    # 幂与根
    "sqrt": (1, math.sqrt),
    "cbrt": (1, lambda x: math.copysign(abs(x) ** (1 / 3), x)),
    "pow": (2, lambda x, y: _power(x, y)),
    "fact": (1, _factorial),
    "factorial": (1, _factorial),
    # 取整与符号
    "abs": (1, abs),
    "floor": (1, lambda x: float(math.floor(x))),
    "ceil": (1, lambda x: float(math.ceil(x))),
    "round": (1, lambda x: float(round(x))),
    "sign": (1, lambda x: float(math.copysign(1, x)) if x else 0.0),
    # 角度换算
    "rad": (1, math.radians),
    "deg": (1, math.degrees),
    # 多参数
    "max": (2, max),
    "min": (2, min),
    "mod": (2, lambda x, y: _modulo(x, y)),
}


def _modulo(left: float, right: float) -> float:
    if right == 0:
        raise DivisionByZeroError("Modulo by zero")
    return math.fmod(left, right)


def _apply_binary(operator: str, left: float, right: float) -> float:
    """执行二元运算，并对除零/溢出做统一处理。"""
    try:
        if operator == "+":
            return left + right
        if operator == "-":
            return left - right
        if operator == "*":
            return left * right
        if operator == "/":
            if right == 0:
                raise DivisionByZeroError()
            return left / right
        if operator == "%":
            return _modulo(left, right)
        if operator == "^":
            return _power(left, right)
    except OverflowError as exc:
        raise ResultOverflowError("Result is out of range") from exc

    raise InvalidExpressionError(f"Unsupported operator '{operator}'")


def _apply_function(name: str, arguments: Sequence[float]) -> float:
    """按函数表调用函数，校验参数个数并翻译数学异常。"""
    spec = FUNCTIONS.get(name.lower())
    if spec is None:
        raise UnknownFunctionError(f"Unknown function '{name}'")

    arity, implementation = spec
    if len(arguments) != arity:
        raise InvalidExpressionError(
            f"Function '{name}' expects {arity} argument(s), got {len(arguments)}"
        )

    try:
        return float(implementation(*arguments))
    except ValueError as exc:
        raise MathDomainError(str(exc) or f"Math domain error in '{name}'") from exc
    except OverflowError as exc:
        raise ResultOverflowError(f"Result of '{name}' is out of range") from exc
    except ZeroDivisionError as exc:
        raise DivisionByZeroError() from exc


def normalize_result(value: float) -> float:
    """规整结果：消除浮点噪声、过滤 NaN / Inf。"""
    if math.isnan(value) or math.isinf(value):
        raise ResultOverflowError("Result is out of range")

    rounded = round(value, RESULT_PRECISION)
    if rounded == 0:  # 统一 -0.0 与 0.0
        return 0.0
    return rounded


def evaluate(node: AstNode) -> float:
    """递归求值 AST，返回规整后的浮点结果。"""
    if isinstance(node, NumberNode):
        return node.value

    if isinstance(node, ConstantNode):
        if node.name not in CONSTANTS:
            raise UnknownConstantError(f"Unknown constant '{node.name}'")
        return CONSTANTS[node.name]

    if isinstance(node, UnaryNode):
        operand = evaluate(node.operand)
        return operand if node.operator == "+" else -operand

    if isinstance(node, BinaryNode):
        return normalize_result(
            _apply_binary(node.operator, evaluate(node.left), evaluate(node.right))
        )

    if isinstance(node, FunctionNode):
        return normalize_result(
            _apply_function(node.name, [evaluate(arg) for arg in node.arguments])
        )

    raise InvalidExpressionError("Unsupported expression node")
