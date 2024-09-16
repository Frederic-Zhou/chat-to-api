# FastAPI 应用入口
# app/main.py

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api import endpoints  # 导入 API 路由
from app.config.settings import settings  # 导入配置


def create_app() -> FastAPI:
    # 创建 FastAPI 实例
    app = FastAPI(
        title="自训练 SpaCy 系统 API",
        version="1.0.0",
        description="一个使用 SpaCy、LlamaIndex 和 GPT-3 的自训练系统",
    )

    # 配置 CORS（跨域资源共享）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 包含 API 路由
    app.include_router(endpoints.router)

    return app


app = create_app()
