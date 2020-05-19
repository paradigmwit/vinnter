import sys
from inspect import getsourcefile
from os.path import abspath
import pika

# adding current directory to path, was having issues importing modules
current_directory = abspath(getsourcefile(lambda: 0))
current_directory = '\\'.join(current_directory.split('\\')[:-2])+'\\'
sys.path.append(current_directory)
sys.path.append(current_directory)
#print(sys.path)

from LogConsumer.file.filewriter import FileWriter
from LogConsumer import config

connection = pika.BlockingConnection(pika.ConnectionParameters(host=config.RABBITMQ_PATH))
channel = connection.channel()
file_writer = FileWriter()


def callback(ch, method, properties, log):
    print(f' [x] Received - {log}')
    try:
        file_writer.write(log)
    except FileNotFoundError:
        exit(-1)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    try:
        channel.queue_declare(config.RABBITMQ_Q_NAME, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue=config.RABBITMQ_Q_NAME,
            on_message_callback=callback)
        print('Waiting to receive log messages. Ctrl+C to exit.')
        channel.start_consuming()
    except KeyboardInterrupt:
        print('Exiting')
        exit()


if __name__ == '__main__':
    print('LogConsumer')
    main()
