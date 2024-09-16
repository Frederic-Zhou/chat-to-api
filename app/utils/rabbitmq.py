# app/utils/rabbitmq.py

import pika
from app.config.settings import settings


def send_to_queue(queue_name: str, message: str) -> bool:
    try:
        # 从配置中获取 RabbitMQ 连接参数
        parameters = pika.URLParameters(settings.RABBITMQ_URL)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2),  # 使消息持久化
        )
        connection.close()
        return True
    except Exception as e:
        print(f"Failed to send message to queue: {e}")
        return False


def consume_from_queue(queue_name: str, callback):
    try:
        parameters = pika.URLParameters(settings.RABBITMQ_URL)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=queue_name, on_message_callback=callback)
        print(f"[*] Waiting for messages in {queue_name}. To exit press CTRL+C")
        channel.start_consuming()
    except Exception as e:
        print(f"Failed to consume messages from queue: {e}")
