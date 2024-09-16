# app/services/gpt_labeler.py

import openai
from app.config.settings import settings
from app.services.llama_index import get_rules

# 设置 OpenAI API 密钥
openai.api_key = settings.OPENAI_API_KEY


def gpt_label_text(text):
    # 从 LlamaIndex 获取相关的规则说明
    rules = get_rules(text)
    prompt = f"""
你将根据以下规则对输入文本进行标注：

{rules}

### 现在，请根据以上规则标注以下文本：
{text}

### 请以 JSON 格式输出结果，格式如下：
{{
  "textcat": "分类名称",
  "labels": {{
    "LABEL1": "对应的文本",
    "LABEL2": "对应的文本"
  }}
}}
"""

    response = openai.Completion.create(
        engine=settings.GPT_MODEL,
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
        print("Failed to parse GPT output.")
        return None
