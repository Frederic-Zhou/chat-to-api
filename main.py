from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


# 定义请求模型
class TextRequest(BaseModel):
    text: str


@app.post("/process-text")
async def process_text(request: TextRequest):
    text = request.text
    # 这里你可以对文本进行处理
    return {"message": f"Received text: {text}"}
