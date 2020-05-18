import sys
import pika
from LogConsumer import config
from LogConsumer.filewriter import FileWriter

sys.path.append('D:\\Workspaces\\Backend\\Vintter\\Solution')
sys.path.append('D:/Workspaces/Backend/Vintter/Solution')
print(sys.path)

connection = pika.BlockingConnection(pika.ConnectionParameters(host=config.RABBITMQ_PATH))
channel = connection.channel()
file_writer = FileWriter()


def callback(ch, method, properties, log):
    print(f' [x] Received log - {log}')
    try:
        file_writer.write(log)
    except FileNotFoundError:
        exit(-1)
    print(" [x] Done!")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    channel.queue_declare(config.RABBITMQ_Q_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=config.RABBITMQ_Q_NAME,
        on_message_callback=callback)
    print('Waiting to receive log messages. Ctrl+C to exit.')
    channel.start_consuming()


if __name__ == '__main__':
    print('LogConsumer')
    main()
