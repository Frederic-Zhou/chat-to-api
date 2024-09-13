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
    rabbit_connection = pika.BlockingConnection(pika.URLParameters(config.RABBITMQ_URL))
    rabbit_channel = rabbit_connection.channel()
    rabbit_channel.queue_declare(
        queue=config.RABBITMQ_QUEUE
    )  # 声明队列（确保队列存在）


# 在第一次请求之前初始化 RabbitMQ 连接
@app.before_first_request
def setup():
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


# 在程序关闭时关闭 RabbitMQ 连接
@app.teardown_appcontext
def close_rabbitmq_connection(exception):
    if rabbit_connection is not None:
        rabbit_connection.close()


if __name__ == "__main__":
    app.run(debug=True)
