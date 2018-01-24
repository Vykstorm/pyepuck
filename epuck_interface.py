from types import SimpleNamespace as Namespace
from PIL import Image
from pyvalid import accepts


def alive(unchecked_method):
    '''
    Decorador auxiliar para los métodos de la clase EpuckInterface. Sirve para añadir código de comprobación al inicio de estas
    funciones para lanzar una excepción en caso de que el e-puck no esté activo
    '''
    def checked_method(self, *args, **kwargs):
        if not self.is_alive():
            raise Exception('E-Puck is not connected')
        return unchecked_method(self, *args, **kwargs)

    return checked_method

def not_alive(unchecked_method):
    def checked_method(self, *args, **kwargs):
        if self.is_alive():
            raise Exception('E-Puck is already connected')
        return unchecked_method(self, *args, **kwargs)

    return checked_method


class EPuckInterface:
    '''
    Representa el robot e-puck.
    Es una clase que define una interfaz para interactuar con un robot, ya sea virtual o físico.
    Provee métodos y atributos para muestrar los sensores (de proximidad y de visión),
    establecer la velodidad de los motores, ...

    Las implementaciones de esta interfaz son: Epuck y VirtualEpuck
    '''

    class Validators:
        def validate_speed(self, speed):
            pass


    def __init__(self, *args, **kwargs):
        epuck = self

        class LeftMotor:
            @property
            def speed(self):
                return epuck.get_left_motor_speed()

            @speed.setter
            def speed(self, amount):
                epuck.set_left_motor_speed(amount)

            def __str__(self):
                return 'Left motor of the e-puck robot'

            def __repr__(self):
                return self.__str__()

        class RightMotor:
            @property
            def speed(self):
                return epuck.get_right_motor_speed()

            @speed.setter
            def speed(self, amount):
                epuck.set_right_motor_speed(amount)

            def __str__(self):
                return 'Right motor of the e-puck robot'

            def __repr__(self):
                return self.__str__()

        class ProximitySensor:
            def __init__(self, index):
                self.index = index

            @property
            def value(self):
                return epuck.get_prox_sensor_value(self.index)

            def __str__(self):
                return 'Proximity sensor of the e-puck robot (IR{})'.format(self.index)

            def __repr__(self):
                return self.__str__()

        class VisionSensor:
            def get_image(self, *args, **kwargs):
                return epuck.get_vision_sensor_image(*args, **kwargs)

            def __str__(self):
                return 'Vision sensor of the e-puck robot'

            def __repr__(self):
                return self.__str__()

        '''
        Constructor de clase. Inicializa la instancia.
        '''
        self.left_motor = LeftMotor()
        self.right_motor = RightMotor()
        self.motors = Namespace(left = self.left_motor, right = self.right_motor)
        self.proximity_sensors = [ProximitySensor(index) for index in range(0, 8)]
        self.prox_sensor15, self.prox_sensor45, self.prox_sensor90 = self.proximity_sensors[0:3]
        self.prox_sensor135, self.prox_sensor225 = self.proximity_sensors[3:5]
        self.prox_sensor270, self.prox_sensor315, self.prox_sensor345 = self.proximity_sensors[5:8]

        self.vision_sensor = VisionSensor()
        self.camera = self.vision_sensor

        self.alive = False
        self.args = args
        self.kwargs = kwargs



    @not_alive
    def run(self):
        '''
        Ejecuta el robot. Después de invocar este método, is_alive() devolverá
        True.
        Esta función ejecuta el método init() para inicializar el robot.
        :return:
        '''
        try:
            self.init(*self.args, **self.kwargs)
            self.alive = True
            del self.args
            del self.kwargs
        except NotImplementedError as e:
            raise e
        except Exception as e:
            raise Exception('Failed to initialize e-puck robot: {}'.format(e))

    @alive
    def destroy(self):
        '''
        Después de invocar este método, la instancia queda inutilizable y is_alive() devolverá False.
        Este método llama internamente a close()
        :return:
        '''
        try:
            self.close()
        except Exception as e:
            raise Exception('Failed to close e-puck robot: {}'.format(e))
        finally:
            self.alive = False

    def is_alive(self):
        '''
        :return: Devuelve True si el robot sigue activo.
        '''
        return self.alive


    '''
    Métodos para inicializar / limpiar los recursos utilizados por el robot
    '''


    def init(self, *args, **kwargs):
        '''
        Este método es invocado para inicializar el robot.
        Se pasa como parametros aquellos indicados en el constructor.
        :param args:
        :param kwargs:
        :return:
        '''
        raise NotImplementedError()

    @alive
    def close(self):
        '''
        Este método se encarga de limpiar todos los recursos utilizados.
        :return:
        '''
        raise NotImplementedError()


    '''
    Métodos para obtener / establecer la velocidad de los motores.
    '''

    @alive
    def get_left_motor_speed(self):
        '''
        :return: Devuelve la velocidad actual del motor izquierdo en radianes
        '''
        raise NotImplementedError()

    @alive
    def get_right_motor_speed(self):
        '''
        :return: Devuelve la velocidad actual del motor derecho en radianes
        '''
        raise NotImplementedError()

    @alive
    def set_left_motor_speed(self, speed):
        '''
        Establece la velocidad del motor izquierdo del robot.
        También se puede usar la propiedad left_motor.speed para establecer la velocidad
        de este motor. e.g: epuck.left_motor.speed = 10
        :param speed: Velocidad en radianes / segundo
        Debe estar en el rango [0, epuck_constraints.max_motor_speed]
        :return:
        '''
        raise NotImplementedError()

    @alive
    def set_right_motor_speed(self, speed):
        '''
        Establece la velocidad del motor derecho del robot.
        También se puede usar la propiedad right_motor.speed para establecer la velocidad
        de este motor. e.g: epuck.right_motor.speed = 10
        :param speed: Velocidad en radianes / segundo
        Debe estar en el rango [0, epuck_constraints.max_motor_speed]
        :return:
        '''
        raise NotImplementedError()



    '''
    Métodos para muestrar los sensores de proximidad.
    '''
    @alive
    def get_prox_sensor_value(self, index):
        '''
        Muestrea un sensor de proximidad.
        :param index: Es el índice del sensor de proximidad, 0 para el sensor IR0, 1 para IR1, hasta 7 para
        IR7
        :return: Devuelve el valor actual del sensor de proximidad en metros (Aproximación de la distancia
        al obstáculo detectado en metros)
        '''
        raise NotImplementedError()




    '''
    Métodos para muestrear los sensores de visión.
    '''
    @alive
    def get_vision_sensor_image(self, mode = 'RGB', size = (40, 40), resample = Image.NEAREST):
        '''
        Muestrea el sensor de visión.
        :param mode: Puede ser el modo de la imágen (definidos por la librería PIL). Puede ser RGB, 1, L, P, ...
        Para el robot físico e-puck, se puede optimizar el rendimiento indicando los modos 1 o L (black and
        white o escala de grises). En estos modos, se obtiene un rate de hasta ocho imágenes por segundo con una
        resolución de 40x40 píxeles.
        Para el resto de modos, puede alcanzarse un rate de 4 fps.
        Por defecto está en modo RGB

        :param size: Es el tamaño de la imágen deseado. En el robot físico, si por alguna razón no se puede obtener
        el tamaño de la imágen por limitaciones de hardware, se extaerá la imágen con mayor resolución posible
        y luego se redimensionará al tamaño indicado usando un algoritmo de resampling.
        Por defecto, el tamaño es de 40x40 (tamaño de imágen recomendable para un mayor rendimiento)

        :param resample: Algoritmo de redimensionamiento que se usará en caso de que la imágen no tenga el
        tamaño deseado. Posibles valores: BOX, BILINEAR, BICUBIC, HAMMING, LANCZOS y NEAREST
        Por defecto es NEAREST (PIL.Image.NEAREST)

        :return: Devuelve una imágen PIL creada a partir de la información extraída por
        el sensor.
        '''
        raise NotImplementedError()
