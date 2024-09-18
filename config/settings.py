# config/settings.py

from pydantic import BaseSettings
from typing import Dict


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "text-davinci-003"

    # 其他配置项

    class Config:
        env_file = ".env"  # 从 .env 文件中加载环境变量


# 实例化配置
settings = Settings()
