"""语法分析器：递归下降法把 Token 序列构造成 AST。

文法（优先级由低到高）：

    expression := term (('+' | '-') term)*
    term       := unary (('*' | '/' | '%') unary)*
    unary      := ('+' | '-') unary | power
    power      := atom ('^' unary)?          # 右结合
    atom       := NUMBER | IDENT '(' args ')' | IDENT | '(' expression ')'

``power`` 的右操作数回落到 ``unary``，因此 ``2^-3`` 合法；
且 ``power`` 递归调用自身形成右结合，``2^3^2 == 2^(3^2) == 512``。
"""

from __future__ import annotations

from typing import List, NamedTuple, Tuple, Union

from .exceptions import InvalidExpressionError
from .tokens import Token, TokenType

AstNode = Union["NumberNode", "ConstantNode", "UnaryNode", "BinaryNode", "FunctionNode"]


class NumberNode(NamedTuple):
    """数字字面量。"""

    value: float


class ConstantNode(NamedTuple):
    """常量，如 pi / e。"""

    name: str


class UnaryNode(NamedTuple):
    """一元运算，如 -5、-(1+2)。"""

    operator: str
    operand: AstNode


class BinaryNode(NamedTuple):
    """二元运算。"""

    operator: str
    left: AstNode
    right: AstNode


class FunctionNode(NamedTuple):
    """函数调用，如 sqrt(9)、max(1, 2)。"""

    name: str
    arguments: Tuple[AstNode, ...]


class Parser:
    """递归下降语法分析器。"""

    def __init__(self, tokens: List[Token]) -> None:
        self._tokens = tokens
        self._index = 0

    # ---------- 公共入口 ----------

    def parse(self) -> AstNode:
        """解析整个表达式；若解析完还有剩余 Token，说明表达式非法。"""
        if self._current().type is TokenType.EOF:
            raise InvalidExpressionError("Expression is empty")

        node = self._parse_expression()
        if self._current().type is not TokenType.EOF:
            token = self._current()
            raise InvalidExpressionError(
                f"Unexpected token '{token.value}' at position {token.position}"
            )
        return node

    # ---------- 各层级解析 ----------

    def _parse_expression(self) -> AstNode:
        node = self._parse_term()
        while self._current_is_operator(("+", "-")):
            operator = self._advance().value
            node = BinaryNode(operator, node, self._parse_term())
        return node

    def _parse_term(self) -> AstNode:
        node = self._parse_unary()
        while self._current_is_operator(("*", "/", "%")):
            operator = self._advance().value
            node = BinaryNode(operator, node, self._parse_unary())
        return node

    def _parse_unary(self) -> AstNode:
        if self._current_is_operator(("+", "-")):
            operator = self._advance().value
            return UnaryNode(operator, self._parse_unary())
        return self._parse_power()

    def _parse_power(self) -> AstNode:
        base = self._parse_atom()
        if self._current_is_operator(("^",)):
            self._advance()
            return BinaryNode("^", base, self._parse_unary())
        return base

    def _parse_atom(self) -> AstNode:
        token = self._current()

        if token.type is TokenType.NUMBER:
            self._advance()
            return NumberNode(float(token.value))

        if token.type is TokenType.LPAREN:
            self._advance()
            node = self._parse_expression()
            self._expect(TokenType.RPAREN, "Missing closing parenthesis ')'")
            return node

        if token.type is TokenType.IDENT:
            self._advance()
            if self._current().type is TokenType.LPAREN:
                return self._parse_function_call(token)
            return ConstantNode(token.value)

        raise InvalidExpressionError(
            f"Unexpected token '{token.value}' at position {token.position}"
        )

    def _parse_function_call(self, name_token: Token) -> FunctionNode:
        self._expect(TokenType.LPAREN)
        arguments: List[AstNode] = []
        if self._current().type is not TokenType.RPAREN:
            arguments.append(self._parse_expression())
            while self._current().type is TokenType.COMMA:
                self._advance()
                arguments.append(self._parse_expression())
        self._expect(
            TokenType.RPAREN, f"Missing closing parenthesis after '{name_token.value}('"
        )
        return FunctionNode(name_token.value, tuple(arguments))

    # ---------- 辅助方法 ----------

    def _current(self) -> Token:
        return self._tokens[self._index]

    def _advance(self) -> Token:
        token = self._tokens[self._index]
        if token.type is not TokenType.EOF:
            self._index += 1
        return token

    def _current_is_operator(self, operators: Tuple[str, ...]) -> bool:
        token = self._current()
        return token.type is TokenType.OPERATOR and token.value in operators

    def _expect(self, token_type: TokenType, message: str = "Invalid expression") -> Token:
        token = self._current()
        if token.type is not token_type:
            raise InvalidExpressionError(f"{message} at position {token.position}")
        return self._advance()


def parse(tokens: List[Token]) -> AstNode:
    """便捷函数：Token 列表 -> AST 根节点。"""
    return Parser(tokens).parse()
