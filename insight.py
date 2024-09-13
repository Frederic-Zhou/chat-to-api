import os
import pika
import spacy
import requests
from langdetect import detect
from spacy.cli import download
import time
import yaml
from db_utils import save_insight  # 导入数据库保存函数
import config


# Load API configuration from YAML file
def load_api_config(file_path="cats_handlers.yaml"):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


api_config = load_api_config()

# 确保模型目录存在
if not os.path.exists(config.MODEL_DIR):
    os.makedirs(config.MODEL_DIR)


# 预加载所有支持的语言模型
def preload_models(supported_languages):
    models = {}
    for lang in supported_languages:
        if lang == "en":
            model_name = "en_core_web_sm"
        elif lang == "zh":
            model_name = "zh_core_web_sm"
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


# 执行 HTTP 请求
def post_to_api(api_url, payload):
    try:
        response = requests.post(
            url=api_url, headers={"Content-Type": "application/json"}, json=payload
        )
        return response.status_code, response.text
    except Exception as e:
        return None, str(e)


# 从 RabbitMQ 通道读取消息并处理
def messageHandler(ch, method, properties, body):
    text = body.decode("utf-8")
    lang = detect(text)
    timestamp = int(time.time())  # 获取当前时间戳

    if lang in models:
        nlp = models[lang]
    else:
        print(f"不支持的语言: {lang}")
        return

    doc = nlp(text)
    labels = {ent.label_: ent.text for ent in doc.ents}
    categories = doc.cats

    print(f"Text: {text}")
    print(f"Language: {lang}")
    print(f"Labels: {labels}")
    print(f"Categories: {categories}")

    if len(categories.items()) == 0:
        response = "未找到任何分类"
        print(response)
        save_insight(timestamp, text, lang, categories, labels, response, is_done=False)
        return
    else:
        # 处理分类并调用相应的API
        for category, score in categories.items():
            if category in api_config:
                api_info = api_config[category]
                required_labels = api_info.get("labels", [])

                # 提取需要的 labels
                filtered_labels = {
                    label: labels[label] for label in required_labels if label in labels
                }

                status_code, response = post_to_api(api_info["api"], filtered_labels)
                if status_code == 200:
                    print(
                        f"API for {category} responded with status {status_code}: {response}"
                    )
                    is_done = True
                else:
                    print(f"Error calling API for {category}: {response}")
                    is_done = False

                save_insight(
                    timestamp,
                    text,
                    lang,
                    categories,
                    labels,
                    response,
                    is_done,
                )

            else:
                response = f"未找到处理 {category} 的 API 配"
                print(response)
                save_insight(
                    timestamp, text, lang, categories, labels, response, is_done=False
                )


# 连接到 RabbitMQ
connection = pika.BlockingConnection(pika.URLParameters(config.RABBITMQ_URL))
channel = connection.channel()
channel.queue_declare(queue=config.CHANNEL)
channel.basic_consume(
    queue=config.CHANNEL, on_message_callback=messageHandler, auto_ack=True
)

print("Waiting for messages. To exit press CTRL+C")
channel.start_consuming()
