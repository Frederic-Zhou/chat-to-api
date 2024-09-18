# handlers/input_handler.py

import json
from services.llama_index import query_rules
from services.gpt_processor import process_with_gpt
from config.settings import settings
import requests

# 定义分类到 API 的映射
api_endpoints = {
    "Greeting": "http://example.com/greeting_api",
    "Order Inquiry": "http://example.com/order_api",
    "Complaint": "http://example.com/complaint_api",
}


def handle_input(text: str) -> dict:
    # 从 LlamaIndex 查询规则
    rules = query_rules(text)

    # 使用 GPT 进行分类和标签提取
    gpt_result = process_with_gpt(text, rules)

    # 解析 GPT 的输出
    try:
        category = gpt_result.get("category")
        labels = gpt_result.get("labels")
    except Exception:
        raise ValueError("无法解析 GPT 的输出。")

    if not category or not labels:
        raise ValueError("分类或标签缺失。")

    # 根据分类获取对应的 API 地址
    api_url = api_endpoints.get(category)
    if not api_url:
        raise ValueError(f"未知的分类：{category}")

    # 调用对应的 API
    try:
        api_response = requests.post(api_url, json=labels)
        api_response.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(f"调用 API 失败：{e}")

    # 返回 API 的响应结果
    return {"api_response": api_response.json()}
