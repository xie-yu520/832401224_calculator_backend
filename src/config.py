"""全局配置。

所有可能随部署环境变化的值都从环境变量读取，保证代码不依赖特定本地环境。
"""

from __future__ import annotations

import os
from pathlib import Path

# 项目根目录（backend 目录本身）
PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Config:
    """应用配置对象。"""

    # 服务监听地址与端口：云端部署时由平台注入 PORT
    HOST = os.environ.get("CALCULATOR_HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT") or os.environ.get("CALCULATOR_PORT") or 5000)
    DEBUG = os.environ.get("CALCULATOR_DEBUG", "false").lower() == "true"

    # SQLite 数据库文件位置
    DB_PATH = os.environ.get("CALCULATOR_DB_PATH", str(PROJECT_ROOT / "data" / "calculator.db"))

    # 允许的跨域来源（默认全部放行，方便前后端分离部署）
    CORS_ORIGINS = os.environ.get("CALCULATOR_CORS_ORIGINS", "*")

    # 计算历史分页参数
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    # 表达式最大长度，防止超长输入拖垮解析
    MAX_EXPRESSION_LENGTH = 256

    # 展示用时区（固定 UTC+8，避免依赖系统 tzdata）
    TIMEZONE_OFFSET_HOURS = 8
