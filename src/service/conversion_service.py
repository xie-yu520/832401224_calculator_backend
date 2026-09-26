"""进制转换服务（扩展功能）：支持 2 / 8 / 10 / 16 进制互转。"""

from __future__ import annotations

from typing import Any, Dict

from ..calculator import CalculatorError

SUPPORTED_BASES = (2, 8, 10, 16)
_BASE_NAMES = {2: "二进制", 8: "八进制", 10: "十进制", 16: "十六进制"}


class ConversionError(CalculatorError):
    """进制转换失败。"""

    code = "CONVERSION_ERROR"
    http_status = 400
    default_message = "Invalid number for the given base"


class ConversionService:
    """整数进制转换。"""

    @staticmethod
    def convert(value: str, from_base: int, to_base: int) -> Dict[str, Any]:
        """把 ``value`` 从 ``from_base`` 进制转换为 ``to_base`` 进制。

        Raises:
            ConversionError: 进制不受支持或数值与进制不匹配。
        """
        if from_base not in SUPPORTED_BASES or to_base not in SUPPORTED_BASES:
            raise ConversionError(f"Only bases {SUPPORTED_BASES} are supported")

        text = (value or "").strip()
        if not text:
            raise ConversionError("Value must not be empty")

        try:
            number = int(text, from_base)
        except ValueError as exc:
            raise ConversionError(
                f"'{text}' is not a valid base-{from_base} number"
            ) from exc

        if to_base == 10:
            formatted = str(number)
        elif to_base == 16:
            formatted = format(number, "X")
        elif to_base == 8:
            formatted = format(number, "o")
        else:
            formatted = format(number, "b")

        return {
            "value": text,
            "from_base": from_base,
            "to_base": to_base,
            "result": formatted,
            "from_base_name": _BASE_NAMES[from_base],
            "to_base_name": _BASE_NAMES[to_base],
            "decimal_value": number,
        }
