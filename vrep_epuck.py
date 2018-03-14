
from epuck_interface import EPuckInterface, alive
from PIL import Image
from vrep import Client as VrepClient
from pyvalid import accepts

class VRepEPuck(EPuckInterface):
    '''
    Robot e-puck virtual que se ejecuta en el simulador V-rep que implementa el interfaz
    EPuckInterface
    '''
    @accepts(object, str, int)
    def __init__(self, address = '127.0.0.1:19997', comm_thread_cycle = 5):
        '''
        :param address: Es la dirección IP del servidor que implementa la API V-Rep. Por defecto
        es 127.0.0.1:19997. Si no se especifica el puerto, por defecto es 19997

        :param comm_thread_cycle: Número de milisegundos que separan dos envíos consecutivos de paquetes por la
        red a la API remota. Reducir esta cantidad mejorará el tiempo de respuesta y la sincronización entre
        cliente y la API remota. Por defecto se establece un valor de 5ms
        '''
        super().__init__(address, comm_thread_cycle)


    '''
    Métodos para inicializar / limpiar los recursos utilizados por el robot
    '''

    def init(self, address, comm_thread_cycle):
        self.client = VrepClient(address, comm_thread_cycle)
        self.simulation = self.client.simulation

        simulation = self.simulation
        scene = simulation.scene
        self.handler = scene.robots.epuck
        simulation.resume()


    def close(self):
        super().close()
        self.simulation.stop()
        self.client.close()


    '''
    Implementaciones de los métodos para manejar los motores del robot
    '''
    def _set_left_motor_speed(self, speed):
        super()._set_left_motor_speed(speed)
        self.handler.left_motor.speed = speed


    def _set_right_motor_speed(self, speed):
        super()._set_right_motor_speed(speed)
        self.handler.right_motor.speed = speed


    '''
    Implementación del método para muestrar los sensores de proximidad
    '''
    def _get_prox_sensor_value(self, index):
        super()._get_prox_sensor_value(index)
        value = self.handler.proximity_sensors[index].value
        return value

    '''
    Implementación del método para muestrear el sensor de visión
    '''
    def _get_vision_sensor_image(self, mode ='RGB', size = (40, 40), resample = Image.NEAREST):
        super()._get_vision_sensor_image(mode, size, resample)
        image = self.handler.camera.get_image(mode = mode, size = size, resample = resample)
        return image

    '''
    Métodos para muestrear los sensores del suelo
    '''
    def _get_floor_sensor(self, index):
        super()._get_floor_sensor(index)
        # TODO
        raise NotImplementedError()

    '''
    Métodos para activar/desactivar los leds
    '''
    def _set_led_state(self, index, state):
        super()._set_led_state(index, state)
        # TODO
        raise NotImplementedError()


# Test unitario de este módulo. Debe ejecutarse el simulador V-rep en localhost. El servicio de API
# remota debe estarvalue disponible en el puerto por defecto (19997)
if __name__ == '__main__':
    from time import sleep
    from math import pi
    epuck = VRepEPuck(address = '127.0.0.1')
    epuck.run()

    try:
        epuck.left_motor.speed = pi / 2
        epuck.right_motor.speed = pi / 2
        sleep(2)

        for prox_sensor in epuck.proximity_sensors:
            print(prox_sensor)

        image = epuck.camera.get_image(mode = 'RGB', size = (400, 400))
        image.show()
    finally:
        epuck.destroy()