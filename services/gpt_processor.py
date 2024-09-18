# services/gpt_processor.py

import json
import openai
from config.settings import settings

# 设置 OpenAI API 密钥
openai.api_key = settings.OPENAI_API_KEY


def process_with_gpt(text: str, rules: str) -> dict:
    prompt = f"""
你是一个助手，按照以下规则对用户的输入进行分类，并提取关键标签及其值。

# 规则：

{rules}

请对以下文本进行分类，并提取相应的标签和值。

文本：
{text}

请以 JSON 格式输出结果，格式如下：
{{
  "category": "分类名称",
  "labels": {{
    "label1": "value1",
    "label2": "value2"
  }}
}}
"""

    response = openai.Completion.create(
        engine=settings.OPENAI_MODEL,
        prompt=prompt,
        max_tokens=500,
        temperature=0.5,
        n=1,
        stop=None,
    )

    # 解析 GPT 的输出
    output_text = response.choices[0].text.strip()
    try:
        result = json.loads(output_text)
        return result
    except json.JSONDecodeError:
        raise ValueError("无法解析 GPT 的输出。")
