
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

    @alive
    def close(self):
        raise NotImplementedError()


    '''
    Implementaciones de los métodos para manejar los motores del robot
    '''

    @alive
    def get_left_motor_speed(self):
        raise NotImplementedError()

    @alive
    def get_right_motor_speed(self):
        raise NotImplementedError()

    @alive
    def set_left_motor_speed(self, speed):
        raise NotImplementedError()

    @alive
    def set_right_motor_speed(self, speed):
        raise NotImplementedError()


    '''
    Implementación del método para muestrar los sensores de proximidad
    '''
    @alive
    def get_prox_sensor_value(self, index):
        raise NotImplementedError()


    '''
    Implementación del método para muestrear el sensor de visión
    '''
    @alive
    def get_vision_sensor_image(self, mode = 'RGB', size = (40, 40), resample = Image.NEAREST):
        raise NotImplementedError()
