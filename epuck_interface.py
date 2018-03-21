from types import SimpleNamespace as Namespace
from PIL import Image
from pyvalid import accepts
from pyvalid.validators import is_validator
import epuck_constraints


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



# Clase auxiliar. Nos permitirá crear propiedades y/o métodos setter/getter en listas que obtendrán info/modificarán
# todos los items. Por ejemplo, para activar/desactivar todos los sensores de proximidad al mismo tiempo de una
# forma sencilla como epuck.proximity_sensors.enable = True
class CustomListFactory:
    def create(self, *args, **kwargs):
        class CustomList(list):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            def add_global_getter_method(self, method_name, new_name = None):
                def getter(self):
                    result = []
                    for item in self:
                        method = getattr(item.__class__, method_name)
                        ret = method(item)
                        result.append(ret)
                    return result
                getter.__name__ = method_name if new_name is None else new_name
                setattr(self.__class__, getter.__name__, getter)

            def add_global_setter_method(self, method_name, new_name = None):
                def setter(self, value):
                    for item in self:
                        method = getattr(item.__class__, method_name)
                        method(item, value)
                setter.__name__ = method_name if new_name is None else new_name
                setattr(self.__class__, setter.__name__, setter)


            def add_global_property(self, property_name, new_name = None):
                def getter(self):
                    result = []
                    for item in self:
                        prop = getattr(item.__class__, property_name)
                        ret = prop.fget(item)
                        result.append(ret)
                    return result

                def setter(self, value):
                    for item in self:
                        prop = getattr(item.__class__, property_name)
                        prop.fset(item, value)

                getter.__name__ = setter.__name__ = property_name if new_name is None else new_name

                prop = property(getter)
                prop = prop.setter(setter)
                setattr(self.__class__, getter.__name__, prop)

            def __getitem__(self, index):
                items = super().__getitem__(index)
                return CustomList(items) if isinstance(items, list) else items

        return CustomList(*args, **kwargs)



class EPuckInterface:
    '''
    Representa el robot e-puck.
    Es una clase que define una interfaz para interactuar con un robot, ya sea virtual o físico.
    Provee métodos y atributos para muestrar los sensores (de proximidad y de visión),
    establecer la velodidad de los motores, ...

    Las implementaciones de esta interfaz son: Epuck y VrepEPuck
    '''


    class Validators:
        '''
        Clase auxiliar para validar parámetros de algunos métodos de la clase EPuckInterface.
        '''

        @staticmethod
        @is_validator
        def validate_image_size(size):
            '''
            Valida el valor que establece las dimensiones de la imágen devuelta por el método
            _get_vision_sensor_image
            :param size:
            :return:
            '''
            return isinstance(size, tuple) and len(size) == 2

        @staticmethod
        def validate_value_in_range(a, b):
            '''
            Devuelve un método validador que sirve para comprobar si un valor está en intervalo indicado.
            :param a: Extremo izquierdo del intervalo (inclusive)
            :param b: Extremo derecho del intervalo (inclusive)
            :return:
            '''
            @is_validator
            def validator(value):
                return value >= a and value <= b

            return validator



    def __init__(self, asynch_update, *args, **kwargs):
        '''
        Inicializa esta instancia.
        :param asynch_update: Indica si esta clase se engargará de mantener actualizados los valores
        de los sensores y de modificar los parámetros de los actuadores de forma asíncrona o no.
        Si este parámetro es False, deberá invocarse el método update() para obtener información actualizada
        de los sensores del dispositivo y para hacer efectivos los cambios en los parámetros de los
        actuadores.
        :param args:
        :param kwargs:
        '''
        epuck = self

        class LeftMotor:
            def __init__(self):
                self._speed = 0

            @property
            def speed(self):
                return self._speed

            @speed.setter
            def speed(self, amount):
                epuck._set_left_motor_speed(amount)
                self._speed = amount

            def __str__(self):
                return 'Left motor. Speed: {} rads / sec'.format(self.speed)

            def __repr__(self):
                return self.__str__()

        class RightMotor:
            def __init__(self):
                self._speed = 0

            @property
            def speed(self):
                return self._speed

            @speed.setter
            def speed(self, amount):
                epuck._set_right_motor_speed(amount)
                self._speed = amount

            def __str__(self):
                return 'Right motor. Speed: {} rads / sec'.format(self.speed)

            def __repr__(self):
                return self.__str__()

        class Led:
            def __init__(self, index):
                self.index = index
                self._state = False

            @property
            def state(self):
                return self._state

            @state.setter
            def state(self, state):
                epuck._set_led_state(self.index, state)
                self._state = state

            def __str__(self):
                return '{}th led. State: {}'.format(self.index + 1, 'enabled' if self.state else 'disabled')

            def __repr__(self):
                return self.__str__()


        class Sensor:
            def __init__(self):
                self._enabled = False

            @property
            def enabled(self):
                return self._enabled

            @enabled.setter
            def enabled(self, new_state):
                old_state = self._enabled
                self._enabled = new_state
                if new_state ^ old_state:
                    self._enable_state_changed()

            def _enable_state_changed(self):
                raise NotImplementedError()

            def _get_value(self):
                raise NotImplementedError()

            @property
            def value(self):
                if not self.enabled:
                    raise Exception('{} is not enabled. Enable it in order to get sensor data'.format(self.__class__.__name__))
                return self._get_value()

            def __repr__(self):
                return self.__str__()



        class ProximitySensor(Sensor):
            def __init__(self, index):
                super().__init__()
                self.index = index

            def _enable_state_changed(self):
                epuck._enable_prox_sensor(self.index, self.enabled)

            def _get_value(self):
                return epuck._get_prox_sensor(self.index)

            def __str__(self):
                return '{}th proximity sensor. Value: {}'.format(self.index + 1, self.value)



        class FloorSensor(Sensor):
            def __init__(self, index):
                super().__init__()
                self.index = index

            def _enable_state_changed(self):
                epuck._enable_floor_sensor(self.index, self.enabled)

            def _get_value(self):
                return epuck._get_floor_sensor(self.index)

            def __str__(self):
                return '{} floor sensor. Value: {}'.format(self.index, self.value)


        class LightSensor(Sensor):
            def __init__(self):
                super().__init__()

            def _enable_state_changed(self):
                epuck._enable_light_sensor(self.enabled)

            def _get_value(self):
                return epuck._get_light_sensor()

            def __str__(self):
                return 'Light sensor. Value: {}'.format(self.value)



        class VisionSensor(Sensor):
            def __init__(self):
                super().__init__()

            def _enable_state_changed(self):
                epuck._enable_vision_sensor(self.enabled)

            def _get_value(self):
                return epuck._get_vision_sensor()

            @property
            def image(self):
                return self.value

            @property
            def mode(self):
                return epuck._vision_sensor_params[0]

            @property
            def size(self):
                return epuck._vision_sensor_params[1]

            @property
            def zoom(self):
                return epuck._vision_sensor_params[2]

            @property
            def resample(self):
                return epuck._vision_sensor_params[3]


            def set_params(self, *args, **kwargs):
                epuck._set_vision_sensor_params(*args, **kwargs)

            def __str__(self):
                return 'Vision sensor. Mode: {}, Dimensions: {}, Zoom: {}'.format(self.mode, self.size, self.zoom)


        '''
        Constructor de clase. Inicializa la instancia.
        '''
        self.left_motor = LeftMotor()
        self.right_motor = RightMotor()
        self.motors = CustomListFactory().create([self.left_motor, self.right_motor])
        self.motors.add_global_property('speed')

        self.leds = CustomListFactory().create([Led(index) for index in range(0, 8)])
        self.leds.add_global_property('state')

        self.proximity_sensors = CustomListFactory().create([ProximitySensor(index) for index in range(0, 8)])
        self.proximity_sensors.add_global_property('value', new_name = 'values')
        self.proximity_sensors.add_global_property('enabled')
        self.prox_sensor15, self.prox_sensor45, self.prox_sensor90 = self.proximity_sensors[0:3]
        self.prox_sensor135, self.prox_sensor225 = self.proximity_sensors[3:5]
        self.prox_sensor270, self.prox_sensor315, self.prox_sensor345 = self.proximity_sensors[5:8]

        self.vision_sensor = VisionSensor()
        self.camera = self.vision_sensor

        self.floor_sensors = CustomListFactory().create([FloorSensor(index) for index in ['left', 'middle', 'right']])
        self.floor_sensors.add_global_property('value', new_name = 'values')
        self.floor_sensors.add_global_property('enabled')
        self.light_sensor = LightSensor()

        self.alive = False
        self.args = args
        self.kwargs = kwargs

        self._vision_sensor_params = ('RGB', (40, 40), 1, Image.NEAREST)

    @not_alive
    def live(self):
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
    def kill(self):
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

    @not_alive
    def __enter__(self):
        '''
        Puede utilizarse el siguiente código:
        e.g:
        with EPuckInterface(...) as epuck:
            <some code>
        esto será equivalente a ejecutar las siguientes instrucciones:
        epuck = EPuckInterface(...)
        epuck.live()
        try:
            <some code>
        finally:
            if epuck.is_alive():
                epuck.kill()

        :return:
        '''

        self.live()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.is_alive():
            self.kill()


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
        # Desactivamos los leds y reseteamos la velocidad de los motores
        self.leds.state = False
        self.stop()



    @alive
    @accepts(object, Validators.validate_value_in_range(-1, 1))
    def move_forward(self, speed):
        '''
        Modifica los parámetros de los motores del robot de forma que este se mueva hacia
        delante a la velocidad lineal indicada.
        :param speed: Es un valor normalizado en el rango [-1, 1]
        Cuando este valor sea -1 o 1, la velocidad lineal será la máxima posible, que
        es aproximadamente +-0.128 m / s. Cuando sea 0, la velocidad lineal será 0.
        Si el valor es negativo, el sentido del movimiento será el opuesto.
        '''
        v = speed * epuck_constraints.max_motor_speed
        self.motors.speed = v

    @alive
    @accepts(object, Validators.validate_value_in_range(-1, 1))
    def move_backward(self, speed):
        '''
        Es igual que move_forward( -speed )
        :return:
        '''
        self.move_forward(-speed)


    @alive
    @accepts(object, Validators.validate_value_in_range(-1, 1), ('center', 'left', 'right'))
    def rotate(self, speed, axis = 'center'):
        '''
        Modifica los parámetros de los motores del robot de forma que este rote a una velocidad
        angular específica con respecto al eje indicado (en sentido antihorario)
        :param speed: Es un valor en el rango [-1, 1]. Cuando sea 0, la velocidad angular será 0.
        Si es 1 o -1, la velocidad angular será la máxima posible y se rotará en sentido antihorario.
        Si el valor es negativo, se rotará en sentido horario.

        :param axis: Es el eje de rotación. Puede ser 'center', 'left', 'right'
        'center': Rotará con respecto al centro del robot.
        En este caso, la velocidad angular máxima que puede alcanzarse es ~ +-0.585 rads / s
        'left': Rotará con respecto a la rueda izquierda.
        Velocidad angular máxima: ~ +-0.292 rads / s
        'right: Rotará en torno a la rueda derecha.
        Velocidad angular máxima: ~ +-0.292 rads / s
        :return:
        '''
        rb = epuck_constraints.body_radius
        rw = epuck_constraints.wheels_radius
        w = speed * epuck_constraints.max_motor_speed * rw / rb

        if axis == 'center':
            v2 = w * rb
            v1 = -v2
            w1 = v1 / rw
            w2 = v2 / rw
        else:
            w /= 2
            if axis == 'left':
                v2 = 2 * rb * w
                w1 = 0
                w2 = v2 / rw

            else:
                v1 = 2 * rb * w
                w2 = 0
                w1 = v1 / rw

        self.left_motor.speed = w1
        self.right_motor.speed = w2


    @alive
    def stop(self):
        '''
        Modifica los parámetros de los motores para que el robot quede parado.
        '''
        self.motors.speed = 0



    @alive
    @accepts(object, Validators.validate_value_in_range(-epuck_constraints.max_motor_speed, epuck_constraints.max_motor_speed))
    def _set_left_motor_speed(self, speed):
        '''
        Establece la velocidad del motor izquierdo del robot.
        También se puede usar la propiedad left_motor.speed para establecer la velocidad
        de este motor. e.g: epuck.left_motor.speed = 10

        :param speed: Velocidad en radianes / segundo
        Debe estar en el rango [-epuck_constraints.max_motor_speed, epuck_constraints.max_motor_speed]
        :return:
        '''
        pass

    @alive
    @accepts(object, Validators.validate_value_in_range(-epuck_constraints.max_motor_speed, epuck_constraints.max_motor_speed))
    def _set_right_motor_speed(self, speed):
        '''
        Establece la velocidad del motor derecho del robot.
        También se puede usar la propiedad right_motor.speed para establecer la velocidad
        de este motor. e.g: epuck.right_motor.speed = 10

        :param speed: Velocidad en radianes / segundo
        Debe estar en el rango [-epuck_constraints.max_motor_speed, epuck_constraints.max_motor_speed]
        :return:
        '''
        pass


    '''
    Métodos para activar/desactivar los leds
    '''
    @alive
    @accepts(object, tuple(range(0, 8)), bool)
    def _set_led_state(self, index, state):
        '''
        Establece el estado actual de un led del robot.
        :param index: Es el índice del led (en el rango [0, 8))
        :param state: Es un valor booleano que indicará el nuevo estado del led.
        :return:
        '''
        pass



    '''
    Métodos para muestrar los sensores de proximidad.
    '''
    @alive
    @accepts(object, tuple(range(0, 8)))
    def _get_prox_sensor(self, index):
        '''
        Muestrea un sensor de proximidad.
        :param index: Es el índice del sensor de proximidad, 0 para el sensor IR0, 1 para IR1, hasta 7 para
        IR7
        :return: Devuelve el valor actual del sensor de proximidad.
        '''
        pass

    @alive
    @accepts(object, ('RGB', '1', 'L', 'P'), Validators.validate_image_size,
             (1, 4, 8), (Image.BOX, Image.BILINEAR, Image.BICUBIC, Image.HAMMING, Image.LANCZOS, Image.NEAREST))
    def _set_vision_sensor_params(self, mode = 'RGB', size = (40, 40), zoom = 1, resample = Image.NEAREST):
        '''
        Modifica los parámetros del sensor de visión.
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

        :param zoom: El zoom de la cámara. Puede ser 1/4/8

        :param resample: Algoritmo de redimensionamiento que se usará en caso de que la imágen no tenga el
        tamaño deseado. Posibles valores: BOX, BILINEAR, BICUBIC, HAMMING, LANCZOS y NEAREST
        Por defecto es NEAREST (PIL.Image.NEAREST)
        '''
        self._vision_sensor_params = (mode, size, zoom, resample)

    '''
    Métodos para muestrear los sensores de visión.
    '''
    @alive
    def _get_vision_sensor(self):
        '''
        Muestra el sensor de visión. Se usan los parámetros para el sensor establecidos mediante el
        método _set_vision_sensor_params
        :return: Devuelve una imágen PIL creada a partir de la información extraída por el sensor.
        '''
        pass


    '''
    Métodos para muestrear los sensores de suelo
    '''
    @alive
    @accepts(object, ('left', 'right', 'middle'))
    def _get_floor_sensor(self, index):
        '''
        Muestra un sensor de suelo del robot
        :param index: Es el índice del sensor del suelo a muestrear. Puede tener los siguientes valores:
        'left', 'middle', 'right'
        :return:  Devuelve el valor actual del sensor de suelo cuyo índice es el indicado.
        '''
        pass



    '''
    Métodos para muestreear el sensor de luz
    '''
    @alive
    @accepts(object)
    def _get_light_sensor(self):
        '''
        Muestrea el sensor de luz del robot.
        :return:
        '''
        pass

    '''
    Método para sincronizar la información de los sensores y actualizar los parámetros de los actuadores
    '''
    @alive
    def update(self):
        '''
        Después de invocar este método, la información de los sensores se actualizará.
        Además, los cambios en los parámetros de los actuadores se harán efectivos.
        Solo es necesario implementar este método en el caso de que se haya establecido el
        parámetro async_update a False en el constructor de clase.
        :return:
        '''
        pass


    '''
    Métodos para activar/desactivar los sensores
    '''
    @alive
    @accepts(object, tuple(range(0, 8)), bool)
    def _enable_prox_sensor(self, index, enabled):
        pass

    @alive
    @accepts(object, ('left', 'middle', 'right'), bool)
    def _enable_floor_sensor(self, index, enabled):
        pass

    @alive
    @accepts(object, bool)
    def _enable_vision_sensor(self, enabled):
        pass

    @alive
    @accepts(object, bool)
    def _enable_light_sensor(self, enabled):
        pass
