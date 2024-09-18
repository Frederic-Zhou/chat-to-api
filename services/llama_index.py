# services/llama_index.py

import os
from llama_index import GPTSimpleVectorIndex, SimpleDirectoryReader
from llama_index import LLMPredictor, ServiceContext
from config.settings import settings


# 初始化 LlamaIndex
def initialize_index():
    # 从 documents 目录加载文档
    documents = SimpleDirectoryReader("documents").load_data()

    # 初始化 LLMPredictor
    llm_predictor = LLMPredictor(openai_api_key=settings.OPENAI_API_KEY)

    # 创建 ServiceContext
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)

    # 创建索引
    index = GPTSimpleVectorIndex.from_documents(
        documents, service_context=service_context
    )
    return index


# 创建全局索引实例
index = initialize_index()


def query_rules(query_text: str) -> str:
    # 这里可以根据需要调整查询的方式
    response = index.query("提供分类和标签提取的规则。")
    rules = response.response.strip()
    return rules
