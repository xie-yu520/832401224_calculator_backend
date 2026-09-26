"""接口层：HTTP 路由与请求/响应处理，不含业务逻辑。"""

from .api_controller import api_blueprint

__all__ = ["api_blueprint"]
