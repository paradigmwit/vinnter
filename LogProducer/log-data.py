import subprocess
import sys

sys.path.append('D:\\Workspaces\\Backend\\Vintter\\Solution')
sys.path.append('D:/Workspaces/Backend/Vintter/Solution')
# print(sys.path)


def main(sensor_name):
    print('Started. Waiting on sensor generator...')
    stdio = b''
    packets_queue = []

    from LogProducer.logparser import LogParser
    from LogProducer.logproducer import LogProducer
    from LogProducer.config import QUEUE_BUFFER_SIZE, APPLICATION_NAME

    log_parser = LogParser()
    log_producer = LogProducer()

    process = subprocess.Popen([APPLICATION_NAME, '-n ' + sensor_name],
                               stdout=subprocess.PIPE,
                               # universal_newlines=True,
                               # bufsize=1,
                               )
    try:
        while True:
            stdio += process.stdout.readline()
            print(stdio)
            print('Output received.')

            parsed_packets, partial_packet = log_parser.parse(stdio)

            # print('remaining - ', partial_packet, ' - type - ', type(partial_packet))
            stdio = b'' if len(partial_packet) == 0 else partial_packet

            # Packet queue can be made synchronised
            for packet in parsed_packets:
                packets_queue.append(packet)

            print(f'Log Packets added to queue. Current size - {len(packets_queue)}')

            # TODO- de-queue and send log packets to rabbitMQ
            batch_size = QUEUE_BUFFER_SIZE if len(packets_queue) >= QUEUE_BUFFER_SIZE else len(packets_queue)
            batch, packets_queue = packets_queue[:batch_size], packets_queue[batch_size:]

            log_producer.dispatch_logs(batch)

            print(f'Log Packets removed from queue. Current size {len(packets_queue)}')

            print('Waiting for more output...')

            # Checks if process has finished
            return_code = process.poll()
            if return_code is not None:
                print('RETURN CODE', return_code)
                # Process has finished, read rest of the output
                for stdio in process.stdout.readlines():
                    print(stdio.strip())
                    if stdio != '':
                        parsed_packets = log_parser.parse(stdio)
                break
    except KeyboardInterrupt:
        print('Exiting')
        exit()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python3 log-consumer {SensorName} ')
        exit()
    else:
        main(sys.argv[1])
