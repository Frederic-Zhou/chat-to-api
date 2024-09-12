import os
import pika
import spacy
from langdetect import detect
from spacy.cli import download
import config
import os
import cats_funcs
import inspect
from db_utils import save_insight  # 导入数据库保存函数
import time


# 提取 spacy_functions 中的函数和参数
def get_functions_and_params(module):
    func_map = {}
    for name, func in inspect.getmembers(module, inspect.isfunction):
        params = inspect.signature(func).parameters
        func_map[name] = list(params.keys())
    return func_map


# 确保模型目录存在
if not os.path.exists(config.MODEL_DIR):
    os.makedirs(config.MODEL_DIR)


# 预加载所有支持的语言模型
def preload_models(supported_languages):
    models = {}
    for lang in supported_languages:
        if lang == "en":
            model_name = "en_core_web_lg"
        elif lang == "zh":
            model_name = "zh_core_web_lg"
        else:
            model_name = f"{lang}_core_web_sm"

        model_path = os.path.join(config.MODEL_DIR, model_name)

        if not os.path.exists(model_path):
            download(model_name)
            nlp = spacy.load(model_name)
            nlp.to_disk(model_path)

        models[lang] = spacy.load(model_path)

    return models


# 加载所有语言模型
SUPPORTED_LANGUAGES = spacy.util.get_lang_class  # 获取支持的语言
models = preload_models(SUPPORTED_LANGUAGES)

# 获取所有函数及其参数
functions_and_params = get_functions_and_params(cats_funcs)


# 从 RabbitMQ 通道读取消息并处理
def callback(ch, method, properties, body):
    text = body.decode("utf-8")
    lang = detect(text)
    timestamp = int(time.time())  # 获取当前时间戳

    if lang in models:
        nlp = models[lang]
    else:
        print(f"不支持的语言: {lang}")
        return

    doc = nlp(text)
    labels = [(ent.text, ent.label_) for ent in doc.ents]
    categories = doc.cats

    print(f"Text: {text}")
    print(f"Language: {lang}")
    print(f"Labels: {labels}")
    print(f"Categories: {categories}")

    # 将识别到的标签映射到函数参数并调用对应的函数
    for category, score in categories.items():
        if category in functions_and_params:
            func = getattr(cats_funcs, category)
            params = functions_and_params[category]
            args = {param: None for param in params}

            for label, label_type in labels:
                if label_type in params:
                    args[label_type] = label

            # 调用函数并捕获结果或错误

            try:
                result = func(**args)
                isDone = True
            except Exception as e:
                result = str(e)
                isDone = False

            save_insight(timestamp, text, lang, categories, labels, result, isDone)

        else:
            print(f"未找到处理函数: {category}")


# 连接到 RabbitMQ
connection = pika.BlockingConnection(pika.URLParameters(config.RABBITMQ_URL))
channel = connection.channel()
channel.queue_declare(queue=config.CHANNEL)
channel.basic_consume(queue=config.CHANNEL, on_message_callback=callback, auto_ack=True)

print("Waiting for messages. To exit press CTRL+C")
channel.start_consuming()
