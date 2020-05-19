## Information and Instructions

These have been tested on Windows 10
___

### Dependencies 

1. Python 3.8

2. PIP

3. RabbitMQ
    - `docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management`
        - OR
    - https://www.rabbitmq.com/download.html 
        - install Erlang
        - install RabbitMQ
        - start rabbitmq service
            - this should be kept running 
    
4. Python VENV (OPTIONAL, but preferred to keep python installation lib clean). 
   Launch CMD in checked out directory and execute:
    - `python -m venv ./venv`
    - `.\venv\Scripts\activate.bat`

    NOTE - If you are using the virtualenv, then all solution executions should be performed in the virtual environment. **Might be better to let PyCharm take care of VENV stuff.**
   
    
5. Pika and pytz python package dependencies 
    - `pip install pika` for rabbitmq
    - `pip install pytz` for timezone
    
---

### Configuration Files

1. LogProducer\config.py
    - APPLICATION_PATH : Path of the sensor application
    - APPLICATION_NAME : Name of the sensor application

2. LogConsumer\config.py
    - FILE_PATH : Directory where file is to be generated
    - FILE_NAME : Name of the log file 

##### REMEMBER TO SET THE APPLICATION_PATH and FILE_PATH FOR YOUR SYSTEM

---

### Modules
There are two components as part of this solution.
1. LogProducer
2. LogConsumer

Each component will work independent of the other.

![Solution_Design](./Vinnter_solution.jpg)

##### Launch LogProducer - N Instances
- from cmd prompt `start-log-reader.bat` 
- or
- Python 
    - cd to ./LogProducer directory
    - `python log-reader.py {SENSOR_NAME}`

---

##### Launch LogConsumer - 1 Instance
- from cmd prompt `start-log-writer.bat` 
- or
- Python 
    - cd to ./LogConsumer directory
    - `python log-writer.py`

---

#### LogProducer - N Instances

The LogProducer module performs the following operations
1. Launches the sensor emulator and reads the STDIO
2. Parses the packets to json format
3. Saves partial packets received and combines with subsequent sensor data received. No packet loss.
4. Dispatches the logs in configurable batch sizes to the RabbitMQ 

---

#### LogConsumer - 1 Instance

The LogConsumer modules performs the following operations
1. Listens to the RabbitMQ queue for log messages
2. On receiving the message writes to the log file 
3. Multiple instances can be launched, and messages will be shared between the instances
4. There WILL be read-write collisions on the file being accessed if multiple instances are launched. 



