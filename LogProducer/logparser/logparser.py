from pprint import pprint as pp
from datetime import date, datetime, timezone
from decimal import Decimal

# packet position constants
SIZE_HUMIDITY = 2
SIZE_TEMPERATURE = 3
SIZE_HUMIDITY_AND_TEMP = 5
INDEX_NAME_START = 13
INDEX_TIMESTAMP = 12
INDEX_PACKET_LENGTH = 4


class LogParser:

    def __init__(self):
        pass

    def parse(self, data):

        total_data_length = len(data)
        remaining_data = data
        print('Log Parsing started ... ')

        remaining_data = remaining_data[:-1] if remaining_data[-1] == '\n' else remaining_data
        logs = []
        length_of_packets_parsed = 0
        partial_packet = b''

        while length_of_packets_parsed < total_data_length:

            current_packet_length = int.from_bytes(remaining_data[:INDEX_PACKET_LENGTH], 'big', signed=False)

            print('current_packet_length - ', current_packet_length, ' remaining_data len - ', len(remaining_data))

            if current_packet_length > len(remaining_data):
                partial_packet = remaining_data
                print('partial_packet - ', partial_packet)
                break

            packet = remaining_data[:current_packet_length]
            print('Packet - ', packet)
            length_of_packets_parsed += current_packet_length
            # print(current_packet_length, ' - ', packet, ' - packet data_length - ', current_packet_length)

            logs.append(self.parse_packet(packet))

            remaining_data = remaining_data[current_packet_length:]
            # print('remaining_data - ', remaining_data)

        print(f'Log Parsing ended. {len(logs)} entries parsed.')
        return logs, partial_packet

    def parse_packet(self, packet):
        log_entry = {}

        timestamp = _parse_timestamp(packet)
        log_entry['timestamp'] = timestamp

        name_length = None
        try:
            name_length = packet[INDEX_TIMESTAMP]
        except IndexError as ex:
            print(ex, ', ', packet, ', ', INDEX_TIMESTAMP)

        name = packet[INDEX_NAME_START: INDEX_NAME_START + name_length].decode()
        name = name.strip()
        log_entry['name'] = name

        current_index = INDEX_NAME_START + name_length

        remaining_packet_size = len(packet[current_index:])

        if SIZE_HUMIDITY_AND_TEMP == remaining_packet_size or SIZE_TEMPERATURE == remaining_packet_size:
            temperature = _parse_temperature(current_index, packet)
            log_entry['temperature'] = temperature
            if remaining_packet_size == SIZE_HUMIDITY_AND_TEMP:
                current_index += SIZE_TEMPERATURE

        if SIZE_HUMIDITY_AND_TEMP == remaining_packet_size or SIZE_HUMIDITY == remaining_packet_size:
            humidity = _parse_humidity(current_index, packet)
            log_entry['humidity'] = humidity

        return log_entry


def _parse_packet_length(packet):
    b_packet_length = packet[:INDEX_PACKET_LENGTH]
    packet_length = _convert_packet_length(b_packet_length)
    return packet_length


def _parse_timestamp(packet):
    b_timestamp = packet[INDEX_PACKET_LENGTH:INDEX_TIMESTAMP]
    timestamp = _convert_timestamp(b_timestamp)
    return timestamp


def _convert_timestamp(b_timestamp):
    s_timestamp = int.from_bytes(b_timestamp, 'big', signed=False)
    # print('timestamp - ', s_timestamp)
    timestamp = datetime.fromtimestamp(s_timestamp / 1000, timezone.utc).strftime('%y-%m-%dT%T%z')
    return timestamp


def _convert_packet_length(b_packet_length):
    return int.from_bytes(b_packet_length, 'big', signed=False)


def _parse_temperature(current_index, packet):
    b_temperature = packet[current_index:current_index + SIZE_TEMPERATURE]
    temperature = _convert_temperature(b_temperature)
    return temperature


def _convert_temperature(b_temperature):
    temperature_in_kalvin = int.from_bytes(b_temperature, 'big', signed=False)
    temperature_in_celsius = float((Decimal(str(temperature_in_kalvin/100)) - 273)
                                   .quantize(Decimal('0.01')).to_eng_string())
    return temperature_in_celsius


def _parse_humidity(current_index, packet):
    b_humidity = packet[current_index:]
    humidity = _convert_humidity(b_humidity)
    return humidity


def _convert_humidity(b_humidity):
    humidity = int.from_bytes(b_humidity, 'big', signed=False)
    return float(Decimal(str(humidity / 10)).quantize(Decimal('.1')).to_eng_string())


if __name__ == '__main__':
    inp = b"\x00\x00\x00\x17\x00\x00\x01r\x1e\x9a\xae\xed\x05 Fahd\x05\xcf\x1a\x02\x9e\x00\x00\x00\x14\x00\x00\x01r\x1e\x9a\xbf\xde\x05 Fahd\x01n\x00\x00\x00\x14\x00\x00\x01r\x1e\x9a\xca\x83\x05 Fahd\x02b\x00\x00\x00\x17\x00\x00\x01r\x1e\x9a\xd9\x8e\x05 Fahd\x01\r\x86\x03\xd9\x00\x00\x00\x17\x00\x00\x01r\x1e\x9a\xe0\xce\x05 Fahd\x03\xbd\x93\x00\x0c\x00\x00\x00\x14\x00\x00\x01r\x1e\x9a\xe9\xa6\x05 Fahd\x01]\x00\x00\x00\x17\x00\x00\x01r\x1e\x9a\xfa\xc4\x05 Fahd\x03\xae\xd3\x01\xbb\x00\x00\x00\x17\x00\x00\x01r\x1e\x9b\x04\xf4\x05 Fahd\x04hS\x01I\x00\x00\x00\x15\x00\x00\x01r\x1e\x9b\x13\xde\x05 Fahd\x00\xecX\x00\x00\x00\x17\x00\x00\x01r\x1e\x9b#\x86\x05 Fahd\x03i\xd1\x03\\\x00\x00\x00\x17\x00\x00\x01r\x1e\x9b/\xd0\x05 Fahd\x01S|\x02\xb6\x00\x00\x00\x17\x00\x00\x01r\x1e\x9bA\x94\x05 Fahd\x08\x07\xcf\x01a\x00\x00\x00\x17\x00\x00\x01r\x1e\x9bK/\x05 Fahd\x04\xccw\x00>\x00\x00\x00\x17\x00\x00\x01r\x1e\x9b\\^\x05 Fahd\x01K\t\x01\xc2\x00\x00\x00\x17\x00\x00\x01r\x1e\x9b`\xc3\x05 Fahd\x04\x94p\x004\x00\x00\x00\x14\x00\x00\x01r\x1e\x9bh\x1b\x05 Fahd\x01\xd0\x00\x00\x00\x17\x00\x00\x01r\x1e\x9b{q\x05 Fahd\x04L\x07\x002\x00\x00\x00\x14\x00\x00\x01r\x1e\x9b\x85\xe9\x05 Fahd\x00M\x00\x00\x00\x17\x00\x00\x01r\x1e\x9b\x90\xb1\x05 Fahd\x06\xd4\xd9\x03\xb9\x00\x00\x00\x14\x00\x00\x01r\x1e\x9b\x9f\x96\x05 Fahd\x00\x7f\x00\x00\x00\x17\x00\x00\x01r\x1e\x9b\xa6\x1f\x05 Fahd\x04d\x04\x03z\x00\x00\x00\x15\x00\x00\x01r\x1e\x9b\xb1\xed\x05 Fahd\x06\x94x\x00\x00\x00\x14\x00\x00\x01r\x1e\x9b\xc2\x95\x05 Fahd\x00n\x00\x00\x00\x17\x00\x00\x01r\x1e\x9b\xd2\x05\x05 Fahd\x08\xb3\x98\x03\xa4\x00\x00\x00\x15\x00\x00\x01r\x1e\x9b\xdbS\x05 Fahd\x00\xe6J\x00\x00\x00\x17\x00\x00\x01r\x1e\x9b\xe67\x05 Fahd\x001;\x00\xc7\x00\x00\x00\x17\x00\x00\x01r\x1e\x9b\xed<\x05 Fahd\x00\x92\xb2\x01\x03\x00\x00\x00\x17\x00\x00\x01r\x1e\x9b\xfd\xde\x05 Fahd\x03\xe0\xdd\x03&\x00\x00\x00\x17\x00\x00\x01r\x1e\x9c\x0c\x99\x05 Fahd\x01W\xd5\x02\xb8\x00\x00\x00\x17\x00\x00\x01r\x1e\x9c\x16q\x05 Fahd\x01\x00\x95\x02\x05\x00\x00\x00\x17\x00\x00\x01r\x1e\x9c\x1b'\x05 Fahd\x04\xf2'\x01\r\x00\x00\x00\x17\x00\x00\x01r\x1e\x9c\x1fn\x05 Fahd\x01\x8f|\x00z\x00\x00\x00\x17\x00\x00\x01r\x1e\x9c1\x93\x05 Fahd\x08\xcf\xbc\x01n\x00\x00\x00\x17\x00\x00\x01r\x1e\x9cC\x98\x05 Fahd\x02\x1f\xd3\x03\xd6\x00\x00\x00\x17\x00\x00\x01r\x1e\x9cLV\x05 Fahd\x07\x82\xe6\x01\xd3\x00\x00\x00\x17\x00\x00\x01r\x1e\x9cZj\x05 Fahd\x08[\xe9\x02k\x00\x00\x00\x17\x00\x00\x01r\x1e\x9cd%\x05 Fahd\x00\x924\x03\x1a\x00\x00\x00\x14\x00\x00\x01r\x1e\x9cs9\x05 Fahd\x01_\x00\x00\x00\x15\x00\x00\x01r\x1e\x9c\x80\xee\x05 Fahd\x08\xe2\xc0\x00\x00\x00\x17\x00\x00\x01r\x1e\x9c\x92\x1d\x05 Fahd\x04\x83\x80\x01\xba\x00\x00\x00\x17\x00\x00\x01r\x1e\x9c\x9f\xaf\x05 Fahd\x03\xc6D\x03\x86\x00\x00\x00\x17\x00\x00\x01r\x1e\x9c\xb2\xe3\x05 Fahd\x06\xb2\xd0\x00\xac\x00\x00\x00\x15\x00\x00\x01r\x1e\x9c\xb7&\x05 Fahd\x05\t\x94\x00\x00\x00\x17\x00\x00\x01r\x1e\x9c\xc3k\x05 Fahd\x04n\x7f\x02m\x00\x00\x00\x17\x00\x00\x01r\x1e\x9c\xc8W\x05 Fahd\x07\x1b\x08\x02G\x00\x00\x00\x14\x00\x00\x01r\x1e\x9c\xd4\x8e\x05 Fahd\x01\xc5\x00\x00\x00\x17\x00\x00\x01r\x1e\x9c\xdfv\x05 Fahd\x03\xa4\xf9\x00\xfa\x00\x00\x00\x15\x00\x00\x01r\x1e\x9c\xe5Z\x05 Fahd\x01he\x00\x00\x00\x17\x00\x00\x01r\x1e\x9c\xea\x1a\x05 Fahd\x07b\x8f\x01\xbe\x00\x00\x00\x14\x00\x00\x01r\x1e\x9c\xf1x\x05 Fahd\x01\x0e\x00\x00\x00\x14\x00\x00\x01r\x1e\x9c\xf6\x83\x05 Fahd\x01\xd7\x00\x00\x00\x17\x00\x00\x01r\x1e\x9d\x00F\x05 Fahd\x00w\xc2\x02\x96"
    LogParser().parse(inp)
