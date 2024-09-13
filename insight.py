import pika
import yaml
import requests
from langdetect import detect
import time
from db_utils import save_insight  # 导入数据库保存函数
import config
from models import models


# Load API configuration from YAML file
def load_handlers_config(file_path="cats_handlers.yaml"):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


api_config = load_handlers_config()


# 执行 HTTP 请求
def post_to_api(api_url, payload, text):
    try:
        payload["text"] = text
        response = requests.post(
            url=api_url, headers={"Content-Type": "application/json"}, json=payload
        )
        return response.status_code, response.text
    except Exception as e:
        return None, str(e)


# 从 RabbitMQ 通道读取消息并处理
def messageHandler(ch, method, properties, body):
    text = body.decode("utf-8")
    lang = detect(text)[:2]  # 检测文本语言
    timestamp = int(time.time())  # 获取当前时间戳

    if lang in models:
        nlp = models[lang]
    else:
        nlp = models["xx"]

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
        save_insight(timestamp, text, lang, categories, labels, response, False)
        return
    else:
        # 处理分类并调用相应的API

        for category, score in categories.items():
            if category in api_config:
                api_info = api_config[category]
                required_labels = api_info.get("labels", [])

                print(f"Processing required_labels: {required_labels}")

                # 提取需要的 labels
                filtered_labels = {
                    label: labels[label] for label in required_labels if label in labels
                }

                print(f"Filtered labels: {filtered_labels}")

                is_done = False
                status_code, response = post_to_api(
                    api_info["api"], filtered_labels, text
                )
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
                response = f"未找到处理 {category} 的 API 配对处理接口"
                print(response)
                save_insight(timestamp, text, lang, categories, labels, response, False)


# 连接到 RabbitMQ
connection = pika.BlockingConnection(pika.URLParameters(config.RABBITMQ_URL))
channel = connection.channel()
channel.queue_declare(queue=config.RABBITMQ_QUEUE)
channel.basic_consume(
    queue=config.RABBITMQ_QUEUE, on_message_callback=messageHandler, auto_ack=True
)

print("Waiting for messages. To exit press CTRL+C")
channel.start_consuming()
