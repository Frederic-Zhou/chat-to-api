# 处理函数调用逻辑
# app/services/handler_caller.py

import requests
from app.utils import db
from app.models.schemas import TextcatHandler


def call_handler(textcat, labels):
    with db.SessionLocal() as session:
        handler = session.query(TextcatHandler).filter_by(textcat=textcat).first()
        if handler:
            api_url = handler.api_url
            required_labels = handler.labels_required
            # 提取需要的 labels
            data = {label: labels.get(label) for label in required_labels}
            # 发送 POST 请求
            try:
                response = requests.post(api_url, json=data, timeout=10)
                status_code = response.status_code
                # 可以根据需要处理响应结果
                return status_code
            except requests.exceptions.RequestException as e:
                print(f"Error calling handler API: {e}")
                return None
        else:
            print(f"No handler found for textcat: {textcat}")
            return None
