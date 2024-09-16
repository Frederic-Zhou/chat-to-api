# 定义数据模型和 Pydantic 模型

# app/models/schemas.py

from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from app.utils.db import Base


class TextData(Base):
    __tablename__ = "text_data"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    textcat = Column(String, nullable=True)
    labels = Column(JSON, nullable=True)
    status = Column(
        String, default="unlabeled"
    )  # unlabeled, labeled_untrained, trained
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class TextcatHandler(Base):
    __tablename__ = "textcat_handlers"

    id = Column(Integer, primary_key=True, index=True)
    textcat = Column(String, unique=True, nullable=False)
    api_url = Column(String, nullable=False)
    labels_required = Column(JSON, nullable=False)
