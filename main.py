# main.py

from fastapi import FastAPI
from api.routes import router
from config.settings import Settings

app = FastAPI(
    title="Chat to API",
    version="1.0.0",
    description="将自然语言转换为 API 请求的工具",
)

# 包含 API 路由
app.include_router(router)

# 读取配置（如需使用，可取消注释）
# settings = Settings()
