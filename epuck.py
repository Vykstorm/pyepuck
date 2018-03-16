
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
    Métodos para activar/desactivar los leds
    '''
    def _set_led_state(self, index, state):
        super()._set_led_state(index, state)
        # TODO
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
    def _set_vision_sensor_params(self, mode = 'RGB', size = (40, 40), zoom = 1, resample = Image.NEAREST):
        super()._set_vision_sensor_params(mode, size, zoom, resample)

        # TODO
        raise NotImplementedError()

    def _get_vision_sensor_image(self):
        super()._get_vision_sensor_image()
        mode, size, zoom, resample = self._vision_sensor_params
        # TODO
        raise NotImplementedError()


    '''
    Métodos para muestrear los sensores del suelo
    '''
    def _get_floor_sensor(self, index):
        super()._get_floor_sensor(index)
        # TODO
        raise NotImplementedError()


    '''
    Método para muestrear el sensor de luz
    '''
    def _get_light_sensor(self):
        super()._get_light_sensor()
        # TODO
        raise NotImplementedError()

    '''
    Actualiza la información de los sensores y hace efectivos los cambios en los actuadores
    (motores / leds)
    '''
    def update(self):
        super().update()
        # TODO
        raise NotImplementedError()