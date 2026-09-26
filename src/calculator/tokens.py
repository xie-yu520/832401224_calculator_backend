"""表达式的词法单元定义。"""

from __future__ import annotations

from enum import Enum
from typing import NamedTuple


class TokenType(str, Enum):
    """Token 类型枚举。"""

    NUMBER = "NUMBER"
    IDENT = "IDENT"
    OPERATOR = "OPERATOR"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    COMMA = "COMMA"
    EOF = "EOF"


class Token(NamedTuple):
    """一个词法单元。``position`` 用于在报错时指出出错的字符下标。"""

    type: TokenType
    value: str
    position: int
