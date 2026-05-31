"""
FastAPI 应用入口。
- 注册 /api/auth, /api/orgs, /api/expense-items, /api/users 路由
- 注册 BizError → 统一响应 的全局异常处理器
- 校验异常(RequestValidationError)也走统一响应壳，code=42201
"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api import auth as auth_api
from app.api import expense_items as expense_items_api
from app.api import orgs as orgs_api
from app.api import users as users_api
from app.core.config import settings
from app.core.response import BizError, fail, ok

app = FastAPI(
    title="费用单管理系统",
    description="费用单据填报、管理与打印系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(BizError)
async def _biz_handler(_: Request, exc: BizError):
    return JSONResponse(status_code=200, content=fail(exc.code, exc.message, exc.data))


@app.exception_handler(RequestValidationError)
async def _validation_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=200,
        content=fail(42201, "请求参数不合法", {"errors": exc.errors()}),
    )


# 业务路由统一挂在 /api 下
app.include_router(auth_api.router, prefix="/api")
app.include_router(orgs_api.router, prefix="/api")
app.include_router(expense_items_api.router, prefix="/api")
app.include_router(users_api.router, prefix="/api")

# 静态文件服务：上传的 Logo/公章、导出文件经 /storage 访问（前端 img src 用）。
# storage 下仅存业务上传文件(logos/seals/exports)，无敏感内容。
_storage_dir = Path(settings.STORAGE_PATH)
_storage_dir.mkdir(parents=True, exist_ok=True)
app.mount("/storage", StaticFiles(directory=str(_storage_dir)), name="storage")


@app.get("/")
def read_root():
    return ok({"message": "费用单管理系统 API", "version": "1.0.0", "docs": "/docs"})


@app.get("/health")
def health_check():
    return ok({"status": "ok"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
