
from epuck_interface import EPuckInterface
from PIL import Image
from vrep import Client as VRepClient
from pyvalid import accepts
from random import random
from math import pi
import epuck_constraints

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
        super().__init__(True, address, comm_thread_cycle)


    '''
    Métodos para inicializar / limpiar los recursos utilizados por el robot
    '''

    def init(self, address, comm_thread_cycle):
        self.client = VRepClient(address, comm_thread_cycle)
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
    Métodos para activar/desactivar los leds
    '''
    def _set_led_state(self, index, state):
        super()._set_led_state(index, state)
        # TODO




    '''
    Implementación del método para muestrar los sensores de proximidad
    '''
    def _get_prox_sensor(self, index):
        super()._get_prox_sensor(index)
        value = self.handler.proximity_sensors[index].value
        #return value
        return self._distance_to_ir_measurement(value)



    '''
    Implementación del método para muestrear el sensor de visión
    '''
    def _set_vision_sensor_params(self, mode = 'RGB', size = (40, 40), zoom = 1, resample = Image.NEAREST):
        super()._set_vision_sensor_params(mode, size, zoom, resample)


    def _get_vision_sensor(self):
        super()._get_vision_sensor()
        mode, size, zoom, resample = self._vision_sensor_params
        image = self.handler.camera.get_image(mode = mode, size = size, resample = resample)
        return image



    '''
    Métodos para muestrear los sensores del suelo
    '''
    def _get_floor_sensor(self, index):
        super()._get_floor_sensor(index)
        # TODO



    '''
    Método para muestrear el sensor de luz
    '''
    def _get_light_sensor(self):
        super()._get_light_sensor()
        # TODO


    '''
    Activación / Desactivación de sensores
    '''
    def _enable_prox_sensor(self, index, enabled):
        '''
        No es necesario activar los sensores de Vrep, ya que están disponibles por defecto, pero muestreamos el sensor
        para inicializarlo (la primera medición siempre es más lenta, ya crea es síncrona con respecto
        servidor). El resto de muestreos son asíncronos.
        '''
        super()._enable_prox_sensor(index, enabled)
        if enabled:
            self._get_prox_sensor(index)


    def _enable_floor_sensor(self, index, enabled):
        super()._enable_floor_sensor(index, enabled)
        if enabled:
            self._get_floor_sensor(index)

    def _enable_vision_sensor(self, enabled):
        super()._enable_vision_sensor(enabled)
        if enabled:
            self._get_vision_sensor()

    def _enable_light_sensor(self, enabled):
        super()._enable_light_sensor(enabled)
        if enabled:
            self._get_light_sensor()


    #
    # Métodos auxiliares
    #
    def _distance_to_ir_measurement(self, distance):
        '''
        Método auxiliar para simular la medición de uno de los sensores IR
        de proximidad del e-epuck cuando hay un obstáculo a la distancia que se indica como parámetro.
        Se introduce ruido en la medición en función de la velocidad lineal del robot e-puck
        '''
        # TODO
        # Aproximación. Modificar esto ->
        p = pi * epuck_constraints.wheels_diameter
        distance = min(distance, p) / p
        measure = (distance ** (1 / 3))

        # Añadimos ruido gaussiano
        measure += random() * .1 - .05

        measure *= 3000

        return measure



# Test unitario de este módulo. Debe ejecutarse el simulador V-rep en localhost. El servicio de API
# remota debe estarvalue disponible en el puerto por defecto (19997)
if __name__ == '__main__':
    from time import sleep
    from math import pi
    epuck = VRepEPuck(address = '127.0.0.1')
    epuck.live()

    try:
        epuck.left_motor.speed = pi / 2
        epuck.right_motor.speed = pi / 2
        sleep(2)

        for prox_sensor in epuck.proximity_sensors:
            print(prox_sensor)

        image = epuck.camera.get_image(mode = 'RGB', size = (400, 400))
        image.show()
    finally:
        epuck.kill()