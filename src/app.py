"""Flask 应用工厂：装配蓝图、CORS 与统一异常处理。"""

from __future__ import annotations

from pathlib import Path

from flask import Flask, send_from_directory
from flask_cors import CORS

from .calculator import CalculatorError
from .config import Config
from .controller import api_blueprint
from .repository import init_database


def create_app() -> Flask:
    """创建并配置 Flask 应用。"""
    app = Flask(__name__)
    app.json.ensure_ascii = False

    # 前后端分离部署，允许跨域访问 /api/*
    CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})

    # 启动时确保数据表存在
    init_database()

    app.register_blueprint(api_blueprint)
    _register_static_site(app)
    _register_error_handlers(app)
    return app


def _register_static_site(app: Flask) -> None:
    """把前端静态页面托管在同一服务上（仅部署便利，不改变前后端分离的调用方式）。

    若 ``web/`` 目录不存在（例如只跑后端做接口调试），则完全不注册这些路由。
    """
    web_dir = Path(Config.WEB_DIR).resolve()
    if not web_dir.is_dir():
        return

    @app.route("/", defaults={"path": "calculator.html"})
    @app.route("/<path:path>")
    def serve_static(path: str):
        """返回 web/ 下的静态文件；api/ 前缀与目录穿越一律返回 404。"""
        if path.startswith("api/") or ".." in path:
            return {
                "success": False,
                "code": "NOT_FOUND",
                "message": "Resource not found",
            }, 404

        target = (web_dir / path).resolve()
        if not str(target).startswith(str(web_dir)) or not target.is_file():
            return {
                "success": False,
                "code": "NOT_FOUND",
                "message": "Resource not found",
            }, 404

        return send_from_directory(str(web_dir), path)


def _register_error_handlers(app: Flask) -> None:
    """把领域异常统一翻译成标准 JSON 错误响应。"""
    @app.errorhandler(CalculatorError)
    def handle_domain_error(error):  # type: ignore[no-untyped-def]
        status = getattr(error, "http_status", 400)
        return (
            {
                "success": False,
                "code": getattr(error, "code", "CALCULATOR_ERROR"),
                "message": getattr(error, "message", str(error)),
            },
            status,
        )

    @app.errorhandler(404)
    def handle_not_found(_error):  # type: ignore[no-untyped-def]
        return {"success": False, "code": "NOT_FOUND", "message": "Resource not found"}, 404

    @app.errorhandler(405)
    def handle_method_not_allowed(_error):  # type: ignore[no-untyped-def]
        return {
            "success": False,
            "code": "METHOD_NOT_ALLOWED",
            "message": "HTTP method not allowed",
        }, 405

    @app.errorhandler(500)
    def handle_server_error(_error):  # type: ignore[no-untyped-def]
        return {
            "success": False,
            "code": "INTERNAL_ERROR",
            "message": "Internal server error",
        }, 500
