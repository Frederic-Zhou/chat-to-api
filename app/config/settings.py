# app/config/settings.py

from pydantic import BaseSettings, Field
from typing import List


class Settings(BaseSettings):
    # 跨域请求允许的来源
    ALLOW_ORIGINS: List[str] = Field(default=["*"], env="ALLOW_ORIGINS")

    # RabbitMQ 配置
    RABBITMQ_URL: str = Field(..., env="RABBITMQ_URL")

    # 数据库配置
    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    # 模型保存路径
    MODEL_DIR: str = Field(default="./models", env="MODEL_DIR")

    # LlamaIndex 文档目录
    DOCUMENTS_DIR: str = Field(default="./documents", env="DOCUMENTS_DIR")

    # OpenAI API Key
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")

    # GPT-3 模型名称
    GPT_MODEL: str = Field(default="text-davinci-003", env="GPT_MODEL")

    class Config:
        env_file = ".env"  # 从 .env 文件中读取环境变量


# 实例化配置
settings = Settings()
