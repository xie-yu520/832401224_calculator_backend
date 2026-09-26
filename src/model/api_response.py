"""统一的 API 响应模型。

所有接口都返回同一套信封格式：
成功 -> ``{"success": true, ...业务字段}``
失败 -> ``{"success": false, "code": "...", "message": "..."}``
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from flask import jsonify


class ApiResponse:
    """API 响应构造器。"""

    @staticmethod
    def success(data: Optional[Dict[str, Any]] = None, status_code: int = 200):
        """构造成功响应。"""
        payload: Dict[str, Any] = {"success": True}
        if data:
            payload.update(data)
        return jsonify(payload), status_code

    @staticmethod
    def error(message: str, code: str = "INTERNAL_ERROR", status_code: int = 400):
        """构造错误响应。"""
        return (
            jsonify({"success": False, "code": code, "message": message}),
            status_code,
        )
