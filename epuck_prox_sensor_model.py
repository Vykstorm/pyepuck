
from scipy.stats import norm as NormalDistribution
from random import random
import json



class EPuckProxSensorModel:
    '''
    Modelo para predicir el valor de un sensor de proximidad sabiendo la distancia de detección a un obstáculo
    y viceversa. Usa modelos de regresión.
    '''
    def __init__(self, noise_generator = None):
        # Generador de ruido.
        self.noise_generator = EPuckProxSensorNoiseModel() if noise_generator is None else noise_generator

    def train(self, data):
        '''
        Entrena el modelo usando un conjunto de datos de entrenamiento.
        :return:
        '''
        pass

    def _predict_sensor_value(self):
        pass

    def predict_sensor_value(self, distance, generate_noise = False):
        '''
        Predice con este modelo, el valor del sensor sabiendo la distancia de detección.
        :param distance: Es la distancia de detección
        :param generate_noise: Es un valor booleano que en caso de establecerse a True, se añadira ruido al valor
        del sensor estimado por el modelo.
        :return: Devuelve el valor predicho.
        '''
        value = self._predict_sensor_value()
        if generate_noise:
            value = self.noise_generator.add_noise(distance, value)

        return value


    def predict_distance(self, distance):
        '''
        Predice la distancia de detección sabiendo el valor del sensor de proximidad.
        :param distance:
        :return:
        '''
        pass


    def to_string(self):
        '''
        Convierte este modelo a una cadena de caracteres. Esta puede posteriormente recuperase para generar
        una instancia de esta misma clase usando el método estático from_string()
        :return:
        '''
        data = {
            'params' : '',
            'noise_generator' : self.noise_generator.to_string()
        }
        return json.dumps(data)


    @classmethod
    def from_string(cls, s):
        '''
        Genera una instancia de esta clase a partir de una cadena de caracteres creada usando el método de clase
        to_string()
        :param s:
        :return:
        '''
        data = json.loads(s)

        noise_generator = EPuckProxSensorNoiseModel.from_string(data['noise_generator'])
        model = cls(noise_generator = noise_generator)

        params = data['params'] # Use this var to set this model params
        # TODO

        return model


    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.__str__()





class EPuckProxSensorNoiseModel:
    '''
    Modelo para añadir ruido a los valores de los sensores de proximidad.
    '''
    def __init__(self):
        pass


    def train(self, data):
        '''
        Entrena este modelo usando el conjunto de entrenamiento proporcionado como parámetro.
        :param data:
        :return:
        '''
        pass

    def _predict_var(self, distance):
        '''
        Predice la varianza del conjunto de valores de un sensor de proximidad tomados a una distancia
        específica a un obstáculo.
        Si x1, x2, ..., xn es el conjunto de valores del sensor y el parámetro distance es la distancia
        de detección del sensor
        se estima que [x1, x2, ..., xn] sigue una distribución normal de media u y varianza v
        Este modelo calcula de forma aproximada v usando un modelo de regresión y devuelve el valor
        predicho.
        :param value:
        :return:
        '''
        pass

    def add_noise(self, distance, value):
        '''
        Añade ruido a la medición de un sensor.
        Se crea una distribución normal N, tomando como media el parámetro value y el valor calculado
        por _predict_var(distance) como varianza.
        Se genera un valor "x" aleatorio en una distribución uniforme con rango [0, 1].
        Se devolverá nuevo valor del sensor (con ruido) el percentil de x sobre la distribución N

        :param distance:
        :param value:
        :return:
        '''
        var = self._predict_var(distance)
        x = random()
        N = NormalDistribution(value, var)
        value = N.ppf(x)

        return value


    def to_string(self):
        '''
        Convierte este modelo a una cadena de caracteres. Esta puede posteriormente recuperase para generar
        una instancia de esta misma clase usando el método estático from_string()
        :return:
        '''
        data = {
            'params' : ''
        }
        return json.dumps(data)


    @classmethod
    def from_string(cls, s):
        '''
        Genera una instancia de esta clase a partir de una cadena de caracteres creada usando el método de clase
        to_string()
        :param s:
        :return:
        '''
        data = json.loads(s)

        model = cls()
        params = data['params'] # use this var to set this model params
        # TODO

        return model

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.__str__()