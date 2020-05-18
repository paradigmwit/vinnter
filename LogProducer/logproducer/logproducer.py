import pika
from LogProducer import config


class LogProducer:

    _connection = None
    _channel = None

    def __init__(self):
        pass

    def dispatch_logs(self, logs):
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(host=config.RABBITMQ_PATH))
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue=config.RABBITMQ_Q_NAME, durable=True)
        for log in logs:
            # print('Sending msg for log - ', log)
            self._channel.basic_publish(
                exchange='',
                routing_key=config.RABBITMQ_ROUTING_KEY,
                body=str(log),
                properties=pika.BasicProperties(
                    delivery_mode=2
                ))
