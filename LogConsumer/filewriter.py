from LogConsumer import config


class FileWriter:

    _path = None
    _name = None

    def __init__(self):
        self._path = config.FILE_PATH
        self._name = config.FILE_NAME
        print('File - ', self._path + self._name)

    def write(self, log):
        try:
            with open(self._path + self._name, 'ab') as log_file:
                log_file.write(log)
                log_file.write(b'\n')
        except FileNotFoundError:
            print("File not accessible. Check and relaunch!")
            exit(-1)
