import os
import pika
import spacy
from langdetect import detect
from spacy.cli import download
import config
import os
import cats_funcs
import inspect


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
        # 为每种语言指定 lg 版本的模型
        if lang == "en":
            model_name = "en_core_web_lg"  # 英语 large 模型
        elif lang == "zh":
            model_name = "zh_core_web_lg"  # 中文 large 模型
        else:
            model_name = f"{lang}_core_web_sm"  # 默认 sm 模型，适用于其他语言

        model_path = os.path.join(config.MODEL_DIR, model_name)

        # 如果模型还没有下载，先下载并保存
        if not os.path.exists(model_path):
            download(model_name)
            nlp = spacy.load(model_name)
            nlp.to_disk(model_path)

        # 加载模型并存储在内存中
        models[lang] = spacy.load(model_path)

    return models


# 加载所有语言模型
SUPPORTED_LANGUAGES = spacy.util.get_lang_class  # 获取支持的语言
models = preload_models(SUPPORTED_LANGUAGES)  # 预加载模型，存入 models 字典

# 获取所有函数及其参数
functions_and_params = get_functions_and_params(cats_funcs)


# 从 RabbitMQ 通道读取消息并处理
def callback(ch, method, properties, body):
    text = body.decode("utf-8")

    # 识别文本的语言
    lang = detect(text)

    # 检查是否有该语言的模型
    if lang in models:
        nlp = models[lang]  # 使用预加载的模型
    else:
        print(f"不支持的语言: {lang}")
        return

    # 使用模型处理文本
    doc = nlp(text)
    labels = [(ent.text, ent.label_) for ent in doc.ents]
    categories = doc.cats

    print(f"Text: {text}")
    print(f"Language: {lang}")
    print(f"Labels: {labels}")
    print(f"Categories: {categories}")

    # 将识别到的标签映射到函数参数并调用对应的函数
    for category, score in categories.items():
        if category in functions_and_params:  # 如果分类名对应函数名
            func = getattr(cats_funcs, category)  # 获取函数
            params = functions_and_params[category]  # 获取该函数的参数列表
            args = {param: None for param in params}  # 初始化参数

            # 赋值 NER 标签到参数
            for label, label_type in labels:
                if label_type in params:
                    args[label_type] = label

            # 调用函数并传递参数
            try:
                func(**args)
            except Exception as e:
                print(f"Error calling function {category}: {e}")
        else:
            print(f"未找到处理函数: {category}")


# 连接到 RabbitMQ
connection = pika.BlockingConnection(pika.URLParameters(config.RABBITMQ_URL))
channel = connection.channel()
channel.queue_declare(queue=config.CHANNEL)
channel.basic_consume(queue=config.CHANNEL, on_message_callback=callback, auto_ack=True)

print("Waiting for messages. To exit press CTRL+C")
channel.start_consuming()
