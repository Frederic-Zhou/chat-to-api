# 与 LlamaIndex 的交互
# app/services/llama_index.py

from llama_index import GPTSimpleVectorIndex, SimpleDirectoryReader
from app.config.settings import settings


# 初始化 LlamaIndex
def init_index():
    documents = SimpleDirectoryReader(settings.DOCUMENTS_DIR).load_data()
    index = GPTSimpleVectorIndex.from_documents(documents)
    return index


index = init_index()


def get_rules(query):
    # 查询 LlamaIndex，获取相关的标注规则
    response = index.query(query)
    return response.response
