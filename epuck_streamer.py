
from threading import Thread, Lock, Condition
from select import select
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from time import sleep
import json
from base64 import b64encode
import zlib
import hashlib
import struct

class EPuckStreamer(Thread):
    '''
    Esta clase crea un servidor TCP que acepta conexiones entrantes. Las conexiones TCP enviarán información
    acerca del estado de los sensores y los actuadores del robot de forma asíncrona.
    '''


    class Client(Thread):
        def __init__(self, streamer, socket):
            super().__init__()

            self.streamer = streamer
            self.socket = socket
            self._active_lock = Lock()
            self._alive = True

            self.start()

        @property
        def alive(self):
            with self._active_lock:
                return self._alive

        @alive.setter
        def alive(self, state):
            with self._active_lock:
                self._alive = state


        def _send_data(self):
            data = self.streamer.get_data(consumer = self)

            total_sent = 0
            while total_sent < len(data):
                sent = self.socket.send(data[total_sent:])
                if sent == 0:
                    raise IOError()
                total_sent += sent

        def _run(self):
            while self.alive:
                self._send_data()

        def run(self):
            try:
                self._run()
            except Exception as e:
                pass
            finally:
                self.alive = False
                self.socket.close()

        def close(self):
            self.alive = False
            self.join()



    def __init__(self, controller, address = 'localhost', port = 19998):
        super().__init__()
        self.controller = controller
        self.epuck = self.controller.epuck
        self.address = address
        self.port = port

        self.server_socket = socket(AF_INET, SOCK_STREAM)

        self._alive_lock = Lock()
        self._alive = True

        self._data_lock = Condition()
        self._data = None

        self._banned_consumers = []
        self.start()

    @property
    def alive(self):
        with self._alive_lock:
            return self._alive

    @alive.setter
    def alive(self, state):
        with self._alive_lock:
            self._alive = state


    def run(self):
        try:
            self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.server_socket.bind((self.address, self.port))
            self.server_socket.listen(1)

            clients = []
            while self.alive:
                readable, writable, errored = select([self.server_socket], [], [], 0)
                if self.server_socket in readable:
                    client_socket, address = self.server_socket.accept()
                    client = self.Client(self, client_socket)
                    clients.append(client)
                    print('Connection opened from: {}'.format(address))

                sleep(.05)
            for client in clients:
                client.close()
        except:
            pass
        finally:
            self.server_socket.close()

    def close(self):
        self.alive = False
        self.join()



    def get_data(self, consumer):
        with self._data_lock:
            self._data_lock.wait_for(lambda: not self._data is None and not consumer in self._banned_consumers)
            self._banned_consumers.append(consumer)
            return self._data

    def broadcast(self):
        def get_sensor_data(sensor):
            return sensor.value if sensor.enabled else False

        def get_sensors_data(sensors):
            return [get_sensor_data(sensor) for sensor in sensors]

        def get_vision_sensor_data():
            return b64encode(self.epuck.vision_sensor.value.tobytes()).decode() if self.epuck.vision_sensor.enabled else False

        data = {
            # Información de sensores
            'prox_sensors' : get_sensors_data(self.epuck.prox_sensors),
            'floor_sensors' : get_sensors_data(self.epuck.floor_sensors),
            'vision_sensor' : get_vision_sensor_data(),
            'vision_sensor_params': self.epuck.vision_sensor.params,
            'light_sensor' : get_sensor_data(self.epuck.light_sensor),

            # Información de actuadores
            'leds' : self.epuck.leds.states,
            'motors' : self.epuck.motors.speeds,

            # Información del controlador
            'elapsed_time' : self.controller.elapsed_time,
            'think_time' : self.controller.think_time,
            'update_time' : self.controller.update_time,
            'steps_per_second' : self.controller.steps_per_second
        }

        data = json.dumps(data).encode()
        data = zlib.compress(struct.pack('!{}s'.format(len(data)), data))

        chunk_size = 1 << 11
        header_size = 16 + 4

        data = struct.pack('!i', len(data)) + data + bytearray(chunk_size - (len(data) + header_size) % chunk_size)

        hasher = hashlib.md5()
        hasher.update(data)
        md5sum = hasher.digest()
        data = struct.pack('!16s', md5sum) + data

        with self._data_lock:
            self._data = data
            self._banned_consumers.clear()
            self._data_lock.notify_all()
