"""词法分析器：把表达式字符串切分成 Token 序列。

支持：整数、小数（``3.14`` / ``.5`` / ``5.``）、科学计数法（``1e3`` / ``2.5e-4``）、
标识符（函数名与常量）、运算符 ``+ - * / % ^``、括号与逗号。
"""

from __future__ import annotations

import re
from typing import List

from .exceptions import InvalidCharacterError
from .tokens import Token, TokenType

# 顺序敏感：数字必须排在标识符之前，否则 ``1e3`` 会被切成数字 ``1`` + 标识符 ``e3``
TOKEN_SPEC = [
    ("NUMBER", r"(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"),
    ("IDENT", r"[A-Za-z_π][A-Za-z_0-9]*"),
    ("OPERATOR", r"[-+*/%^]"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("COMMA", r","),
    ("SKIP", r"[ \t]+"),
    ("UNKNOWN", r"."),
]

_MASTER_PATTERN = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)
)

_TYPE_MAPPING = {
    "NUMBER": TokenType.NUMBER,
    "IDENT": TokenType.IDENT,
    "OPERATOR": TokenType.OPERATOR,
    "LPAREN": TokenType.LPAREN,
    "RPAREN": TokenType.RPAREN,
    "COMMA": TokenType.COMMA,
}


def tokenize(expression: str) -> List[Token]:
    """将表达式切分为 Token 列表，末尾自动追加 EOF。

    Raises:
        InvalidCharacterError: 遇到白名单之外的字符。
    """
    tokens: List[Token] = []
    position = 0
    length = len(expression)

    while position < length:
        match = _MASTER_PATTERN.match(expression, position)
        if match is None:  # pragma: no cover - 正则含 UNKNOWN 兜底，理论上不会命中
            raise InvalidCharacterError(
                f"Invalid character '{expression[position]}' at position {position}"
            )

        kind = match.lastgroup
        text = match.group()
        position = match.end()

        if kind == "SKIP":
            continue
        if kind == "UNKNOWN":
            raise InvalidCharacterError(
                f"Invalid character '{text}' at position {match.start()}"
            )

        tokens.append(Token(_TYPE_MAPPING[kind], text, match.start()))

    tokens.append(Token(TokenType.EOF, "", length))
    return tokens
