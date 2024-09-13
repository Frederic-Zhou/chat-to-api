from flask import Flask, request, jsonify
import pika
import config

app = Flask(__name__)

# 全局变量用于保持 RabbitMQ 连接和通道
rabbit_connection = None
rabbit_channel = None


# 初始化 RabbitMQ 连接和通道
def init_rabbitmq():
    global rabbit_connection, rabbit_channel
    if rabbit_connection is None or rabbit_connection.is_closed:
        rabbit_connection = pika.BlockingConnection(
            pika.URLParameters(config.RABBITMQ_URL)
        )
    if rabbit_channel is None or rabbit_channel.is_closed:
        rabbit_channel = rabbit_connection.channel()
        rabbit_channel.queue_declare(
            queue=config.RABBITMQ_QUEUE
        )  # 声明队列（确保队列存在）


# 在每次请求之前检查 RabbitMQ 连接和通道状态
@app.before_request
def ensure_rabbitmq_connection():
    init_rabbitmq()


@app.route("/send", methods=["POST"])
def send_to_rabbitmq():
    txt = request.json.get("txt")
    if not txt:
        return jsonify({"error": "No txt provided"}), 400

    # 使用全局的 RabbitMQ 通道
    rabbit_channel.basic_publish(
        exchange="", routing_key=config.RABBITMQ_QUEUE, body=txt
    )

    return jsonify({"status": "Message sent to RabbitMQ"}), 200


# 在程序关闭时可以选择关闭 RabbitMQ 连接（可选，不推荐在每个请求中关闭）
@app.teardown_appcontext
def close_rabbitmq_connection(exception):
    global rabbit_connection
    if rabbit_connection and not rabbit_connection.is_closed:
        rabbit_connection.close()


if __name__ == "__main__":
    app.run(debug=True)
