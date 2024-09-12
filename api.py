# api.py
from flask import Flask, request, jsonify
import pika
import config

app = Flask(__name__)


@app.route("/send", methods=["POST"])
def send_to_rabbitmq():
    txt = request.json.get("txt")
    if not txt:
        return jsonify({"error": "No txt provided"}), 400

    connection = pika.BlockingConnection(pika.URLParameters(config.RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue=config.CHANNEL)

    channel.basic_publish(exchange="", routing_key=config, body=txt)
    connection.close()

    return jsonify({"status": "Message sent to RabbitMQ"}), 200


if __name__ == "__main__":
    app.run(debug=True)
