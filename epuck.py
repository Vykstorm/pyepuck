
from epuck_interface import EPuckInterface, alive
from PIL import Image

class EPuck(EPuckInterface):
    '''
    Robot e-puck físico. Implementa el interfaz EPuckInterface
    '''
    def __init__(self):
        super().__init__()


    '''
    Métodos para inicializar / limpiar los recursos utilizados por el robot
    '''

    def init(self):
        raise NotImplementedError()

    def close(self):
        super().close()
        raise NotImplementedError()


    '''
    Implementaciones de los métodos para manejar los motores del robot
    '''

    def _set_left_motor_speed(self, speed):
        super()._set_left_motor_speed(speed)
        raise NotImplementedError()


    def _set_right_motor_speed(self, speed):
        super()._set_right_motor_speed()
        raise NotImplementedError()


    '''
    Implementación del método para muestrar los sensores de proximidad
    '''

    def _get_prox_sensor_value(self, index):
        super()._get_prox_sensor_value(index)
        raise NotImplementedError()


    '''
    Implementación del método para muestrear el sensor de visión
    '''
    def _get_vision_sensor_image(self, mode ='RGB', size = (40, 40), resample = Image.NEAREST):
        super()._get_vision_sensor_image(mode, size, resample)
        raise NotImplementedError()


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

