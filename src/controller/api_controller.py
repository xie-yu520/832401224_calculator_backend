"""计算与历史的 REST 接口。

路由一览：
    GET    /api/health                  健康检查
    POST   /api/calculate               计算表达式（后端算 + 落库）
    GET    /api/history                 分页查询历史（支持 keyword / favorite）
    DELETE /api/history/<id>            删除指定历史（204 No Content）
    DELETE /api/history                 清空全部历史
    PATCH  /api/history/<id>/favorite   切换收藏
    GET    /api/statistics              统计总览
    POST   /api/convert                 进制转换
"""

from __future__ import annotations

from flask import Blueprint, request

from ..model.api_response import ApiResponse
from ..service import (
    CalculatorService,
    ConversionService,
    HistoryService,
    StatisticsService,
)

api_blueprint = Blueprint("api", __name__, url_prefix="/api")

_TRUE_VALUES = {"1", "true", "yes", "on"}


@api_blueprint.route("/health", methods=["GET"])
def health():
    """健康检查，前端用它判断后端是否在线。"""
    return ApiResponse.success({"status": "ok", "service": "calculator-backend"})


@api_blueprint.route("/calculate", methods=["POST"])
def calculate():
    """接收表达式，返回后端计算结果，并写入数据库。"""
    payload = request.get_json(silent=True) or {}
    expression = payload.get("expression", "")

    if not isinstance(expression, str):
        return ApiResponse.error(
            "Field 'expression' must be a string", "INVALID_REQUEST", 400
        )

    data = CalculatorService.calculate(expression)
    return ApiResponse.success(data, 200)


@api_blueprint.route("/history", methods=["GET"])
def list_history():
    """分页查询计算历史，支持关键字搜索与只看收藏。"""
    data = HistoryService.list_history(
        limit=request.args.get("limit"),
        offset=request.args.get("offset"),
        keyword=request.args.get("keyword", ""),
        only_favorite=request.args.get("favorite", "").lower() in _TRUE_VALUES,
    )
    return ApiResponse.success(data, 200)


@api_blueprint.route("/history/<int:history_id>", methods=["DELETE"])
def delete_history(history_id: int):
    """删除指定历史记录，成功返回 204 No Content。"""
    HistoryService.delete(history_id)
    return "", 204


@api_blueprint.route("/history", methods=["DELETE"])
def clear_history():
    """清空全部历史记录。"""
    deleted = HistoryService.clear_all()
    return ApiResponse.success(
        {"deleted": deleted, "message": f"Deleted {deleted} history record(s)"}, 200
    )


@api_blueprint.route("/history/<int:history_id>/favorite", methods=["PATCH"])
def toggle_favorite(history_id: int):
    """切换某条记录的收藏状态。"""
    return ApiResponse.success(HistoryService.toggle_favorite(history_id), 200)


@api_blueprint.route("/statistics", methods=["GET"])
def statistics():
    """返回计算统计总览。"""
    return ApiResponse.success(StatisticsService.overview(), 200)


@api_blueprint.route("/convert", methods=["POST"])
def convert_base():
    """进制转换。"""
    payload = request.get_json(silent=True) or {}
    value = payload.get("value", "")

    try:
        from_base = int(payload.get("from_base", 10))
        to_base = int(payload.get("to_base", 2))
    except (TypeError, ValueError):
        return ApiResponse.error(
            "Fields 'from_base' and 'to_base' must be integers",
            "INVALID_REQUEST",
            400,
        )

    data = ConversionService.convert(str(value), from_base, to_base)
    return ApiResponse.success(data, 200)
