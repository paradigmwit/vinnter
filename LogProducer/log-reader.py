import subprocess
import sys
from inspect import getsourcefile
from os.path import abspath

# adding current directory to path, was having issues importing modules
# the path should be added to the python setup or as a lib
current_directory = abspath(getsourcefile(lambda: 0))
current_directory = '\\'.join(current_directory.split('\\')[:-2])+'\\'
sys.path.append(current_directory)
sys.path.append(current_directory)
# print(sys.path)


def main(sensor_name):

    from LogProducer.logparser import LogParser
    from LogProducer.logproducer.logproducer import LogProducer
    from LogProducer import config
    log_parser = LogParser()
    log_producer = LogProducer()

    print('Started. Waiting on sensor generator...')
    stdio = b''
    packets_queue = []

    command = [config.APPLICATION_PATH+config.APPLICATION_NAME]

    if sensor_name is not None:
        command.append('-n ' + sensor_name)

    process = subprocess.Popen(command,
                               stdout=subprocess.PIPE,
                               )
    try:
        # Running single threaded as there could be packet loss in the way data is received from emulator
        while True:
            stdio += process.stdout.readline()
            # print(stdio)
            print('Output received.')

            parsed_packets, partial_packet = log_parser.parse(stdio)

            # print('remaining - ', partial_packet, ' - type - ', type(partial_packet))
            stdio = b'' if len(partial_packet) == 0 else partial_packet

            # Packet queue can be made synchronised
            for packet in parsed_packets:
                packets_queue.append(packet)

            print(f'Log Packets added to queue. Current size - {len(packets_queue)}')

            batch_size = config.QUEUE_BUFFER_SIZE if len(packets_queue) >= config.QUEUE_BUFFER_SIZE else len(packets_queue)
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

    if len(sys.argv) > 2:
        print('usage: python3 log-consumer {SensorName}. '
              'There should be one Sensor Name, or None')
        exit()
    elif len(sys.argv) == 2 and sys.argv[1].isalnum():
        main(sys.argv[1])
    else:
        main(None)
