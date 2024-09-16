# app/api/endpoints.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.utils import rabbitmq
from app.config.settings import settings

router = APIRouter()


class TextInput(BaseModel):
    text: str


@router.post("/send")
async def send_text(input: TextInput):
    text = input.text
    # 文本预处理：去除不可见字符，保留空格和换行，替换制表符为4个空格
    cleaned_text = text.replace("\t", " " * 4)
    # 可以添加其他不可见字符的处理逻辑
    # 去除不可见字符，保留空格和换行
    cleaned_text = "".join(
        c for c in cleaned_text if c.isprintable() or c in [" ", "\n"]
    )

    # 将处理后的文本发送到 RabbitMQ 的 text_queue 队列
    success = rabbitmq.send_to_queue("text_queue", cleaned_text)
    if not success:
        raise HTTPException(
            status_code=500, detail="Failed to send message to the queue."
        )

    return {"message": "Text received and sent to the queue."}
