
from epuck_interface import EPuckInterface
from PIL import Image
from epuck_driver import EPuckDriver
from pyvalid.validators import accepts
from math import pi

class EPuck(EPuckInterface):
    '''
    Robot e-puck físico. Implementa el interfaz EPuckInterface
    '''

    @accepts(object, str)
    def __init__(self, address):
        '''
        Inicializa la instancia y configura el robot.
        :param address: Es la dirección MAC del robot con el que se abrirá una conexión bluetooth.
        '''
        super().__init__(False, address)


    '''
    Métodos para inicializar / limpiar los recursos utilizados por el robot
    '''

    def init(self, address):
        self.handler = EPuckDriver(address = address, debug = False)
        self.handler.connect()


    def close(self):
        super().close()
        self.handler.disconnect()


    '''
    Implementaciones de los métodos para manejar los motores del robot
    '''

    def _set_left_motor_speed(self, speed):
        super()._set_left_motor_speed(speed)
        # No es necesario hacer nada en este método, los parámetros de los motores
        # se actualizan en el método update


    def _set_right_motor_speed(self, speed):
        super()._set_right_motor_speed()
        # No es necesario hacer nada en este método, los parámetros de los motores
        # se actualizan en el método update


    '''
    Métodos para activar/desactivar los leds
    '''
    def _set_led_state(self, index, state):
        super()._set_led_state(index, state)

        self.handler.set_led(led_number = index, led_value = 0 if not state else 1)




    '''
    Implementación del método para muestrar los sensores de proximidad
    '''

    def _get_prox_sensor(self, index):
        super()._get_prox_sensor(index)

        # Puede que los índices de los sensores no coincidan?
        values = self.handler.get_proximity()
        return values[index]


    '''
    Implementación del método para muestrear el sensor de visión
    '''
    def _set_vision_sensor_params(self, mode = 'RGB', size = (40, 40), zoom = 1, resample = Image.NEAREST):
        super()._set_vision_sensor_params(mode, size, zoom, resample)

        # TODO
        raise NotImplementedError()


    def _get_vision_sensor(self):
        super()._get_vision_sensor()
        mode, size, zoom, resample = self._vision_sensor_params
        # TODO
        raise NotImplementedError()


    '''
    Métodos para muestrear los sensores del suelo
    '''
    def _get_floor_sensor(self, index):
        super()._get_floor_sensor(index)

        values = dict(zip(['left', 'center', 'right'], self.handler.get_floor_sensors()))
        return values[index]


    '''
    Método para muestrear el sensor de luz
    '''
    def _get_light_sensor(self):
        super()._get_light_sensor()

        return self.handler.get_light_sensor()


    '''
    Método para muestrear el sensor de visión
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

        # Establecemos la velocidad de los motores.
        steps_per_radian = .002 * pi
        self.handler.set_motors_speed(l_motor = self.left_motor.speed * steps_per_radian,
                                      r_motor = self.right_motor.speed * steps_per_radian)

        self.handler.step()


    '''
    Activa / Desactiva sensores
    '''
    def _enable_prox_sensor(self, index, enabled):
        super()._enable_prox_sensor(index, enabled)
        if enabled:
            self.handler.enable('proximity')
        elif not any(self.prox_sensors.enabled):
            self.handler.disable('proximity')

    def _enable_floor_sensor(self, index, enabled):
        super()._enable_floor_sensor(index, enabled)
        if enabled:
            self.handler.enable('floor')
        else:
            self.handler.disable('floor')

    def _enable_vision_sensor(self, enabled):
        super()._enable_vision_sensor(enabled)
        if enabled:
            self.handler.enable('camera')
        else:
            self.handler.disable('camera')

    def _enable_light_sensor(self, enabled):
        super()._enable_light_sensor(enabled)
        if enabled:
            self.handler.enable('light')
        else:
            self.handler.disable('light')
