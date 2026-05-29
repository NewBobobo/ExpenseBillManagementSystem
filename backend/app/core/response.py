"""
统一响应包裹与业务异常。

CONTRACTS 规定：所有响应统一为
  { "code": 0, "message": "success", "data": <payload> }

业务错误用 BizError 抛出，由 main.py 注册的异常处理器转成统一响应。
HTTP 状态码统一 200，错误用 code 字段区分。
"""
from typing import Any, Optional

from pydantic import BaseModel


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None


def ok(data: Any = None, message: str = "success") -> dict[str, Any]:
    return {"code": 0, "message": message, "data": data}


def fail(code: int, message: str, data: Any = None) -> dict[str, Any]:
    return {"code": code, "message": message, "data": data}


class BizError(Exception):
    """业务异常：携带业务错误码与提示信息。HTTP 状态码统一 200。"""

    def __init__(self, code: int, message: str, data: Any = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data
