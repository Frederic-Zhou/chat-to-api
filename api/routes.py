# api/routes.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from handlers.input_handler import handle_input

router = APIRouter()


# 定义请求的数据模型
class TextInput(BaseModel):
    text: str


@router.post("/process_text")
async def process_text(input: TextInput):
    text = input.text

    try:
        # 调用输入处理函数
        result = handle_input(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 返回处理结果
    return result
