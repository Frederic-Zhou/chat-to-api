# 文本处理和预测逻辑
# app/services/text_processor.py

import spacy
import threading
import json

from app.utils import rabbitmq, db
from app.config.settings import settings
from app.models.schemas.py import TextData
from app.services.handler_caller import call_handler
from app.services.llama_index import get_rules
from app.services.gpt_labeler import gpt_label_text


# 加载最新的 SpaCy 模型
def load_latest_model():
    import os

    model_dir = settings.MODEL_DIR
    models = [
        d for d in os.listdir(model_dir) if os.path.isdir(os.path.join(model_dir, d))
    ]
    if models:
        latest_model = sorted(models)[-1]
        nlp = spacy.load(os.path.join(model_dir, latest_model))
    else:
        nlp = spacy.blank("zh")  # 如果没有模型，创建一个空模型
    return nlp


nlp = load_latest_model()


def process_text_message(ch, method, properties, body):
    text = body.decode("utf-8")
    doc = nlp(text)
    textcat = None
    labels = {}
    # 获取分类结果
    if doc.cats:
        textcat = max(doc.cats, key=doc.cats.get)
        # 如果分类置信度过低，可以认为未分类
        if doc.cats[textcat] < 0.5:
            textcat = None
    # 获取 NER 标签
    if doc.ents:
        for ent in doc.ents:
            labels[ent.label_] = ent.text

    if not textcat:
        # 未识别出分类，记录未识别的文本到数据库
        with db.SessionLocal() as session:
            new_text = TextData(text=text, status="unlabeled")
            session.add(new_text)
            session.commit()
        # 可以在此处调用 GPT 进行智能标注（可选）
    else:
        # 根据分类，调用处理函数
        result = call_handler(textcat, labels)
        # 记录处理结果和 HTTP 状态码
        with db.SessionLocal() as session:
            new_text = TextData(
                text=text, textcat=textcat, labels=labels, status="processed"
            )
            session.add(new_text)
            session.commit()
    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_consumer():
    rabbitmq.consume_from_queue("text_queue", process_text_message)


# 使用线程来运行消费者，以免阻塞主线程
consumer_thread = threading.Thread(target=start_consumer)
consumer_thread.start()
