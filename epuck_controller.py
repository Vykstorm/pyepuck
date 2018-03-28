
from time import sleep
from time import clock
from pyvalid.validators import accepts
from epuck_interface import EPuckInterface
from epuck_streamer import EPuckStreamer

class EPuckController:
    '''
    Representa un controlador para el robot e-puck.
    '''
    @accepts(object, EPuckInterface, lambda x:isinstance(x, (float, int)) and x > 0)
    def __init__(self, epuck, steps_per_sec = float('inf'), enable_streaming = False, stream_port = 19998):
        '''
        Inicializa la instancia
        :param epuck: Es una instancia de una subclase de EPuckInterface
        :param steps_per_sec: Es el número de pasos por segundo o el número de iteraciones por segundo del bucle
        principal del controlador a ejecutar. Esta cantidad será igual o inferior a este parámetro. Si no se
        indica ningún valor, por defecto será infinito (float('inf')). En tal caso, se intentará obtener el máximo
        número de pasos por segundo posibles.
        :param enable_streaming: Cuando se establece a True, se creará un servidor TCP con el puerto indicado
        al cual se podrán conectar aplicaciones externas para obtener información de los sensores y actuadores.
        Por defecto este parámetro es False.
        :param stream_port: Solo se usa cuando el parámetro enable_streaming es True. Indica el puerto a utilizar
        para crear el servidor TCP
        '''

        self.epuck = epuck

        # Esta variable medirá el tiempo que lleva activa la simulación (se actualiza en cada iteración del bucle)
        self._elapsed_time = 0

        # Esta variable configura el número de veces que el bucle principal debe ejecutarse por unidad de tiempo.
        # El número de veces que el bucle principal se ejecutará por segundo es inferior o igual a esta cantidad
        # (puede ser infinito)
        self._sps = steps_per_sec

        self._think_times = []
        self._update_times = []
        self._step_times = []
        self._think_time = 0
        self._update_time = 0
        self._step_time = float('inf')

        self.streamer = EPuckStreamer(self, address = 'localhost', port = stream_port) if enable_streaming else None

    def run(self):
        '''
        Lanza el controlador. Inicializa el robot y el controlador, ejecuta el método step() de esta misma clase
        de forma indefinida hasta que lanza la excepción StopIteration y por último, cierra la conexión
        y libera los recursos utilizados del robot.
        :return:
        '''
        with self.epuck:
            self.init()
            try:
                while True:
                    t0 = clock()
                    self.step()
                    t1 = clock()
                    step_time = t1 - t0
                    inv_sps = 1 / self._sps
                    if step_time < inv_sps:
                        sleep(inv_sps)

                    self._step_times.append(step_time)
                    if len(self._step_times) > 3:
                        self._step_times.pop(0)
                    self._step_time = sum(self._step_times) / len(self._step_times)

                    self._elapsed_time += inv_sps
            except StopIteration:
                pass
            finally:
                self.close()

    def step(self):
        '''
        Este método es ejecutado múltiples veces por el controlador. Es el cuerpo principal del bucle
        del programa del controlador para el robot. Consta de varias fases:
        - Fase de muestreo de sensores: Se invoca el método sense()
        - Fase de razonamiento: Se invoca el método think()
        - Fase de actuación: Se llamada al método act()
        :return:
        '''
        t0 = clock()
        self.epuck.update()
        t1 = clock()
        update_time = t1 - t0

        self.sense()

        t0 = clock()
        self.think()
        t1 = clock()
        think_time = t1 - t0

        self.act()


        self._think_times.append(think_time)
        if len(self._think_times) > 3:
            self._think_times.pop(0)
        self._think_time = sum(self._think_times) / 3

        self._update_times.append(think_time)
        if len(self._update_times) > 3:
            self._update_times.pop(0)
        self._update_time = sum(self._update_times) / 3

        if not self.streamer is None:
            self.streamer.broadcast()

    def init(self):
        '''
        Inicializa el controlador.
        :return:
        '''
        pass

    def close(self):
        '''
        Elimina el controlador y libera los recursos utilizados.
        :return:
        '''
        pass

    def sense(self):
        '''
        Este método puede ser implementado por las subclases para muestrear datos de los sensores.
        Se puede lanzar la excepción StopIteration para finalizar la ejecución.
        :return:
        '''
        pass


    def think(self):
        '''
        Este método puede ser implementado por las subclases para actualizar los modelos de razonamiento
        del robot
        Se puede lanzar la excepción StopIteration para finalizar la ejecución.
        :return:
        '''
        pass

    def act(self):
        '''
        Este método puede ser implementado por las subclases para modificar los parámetros de los actuadores
        del robot (motores, leds, ...)
        Se puede lanzar la excepción StopIteration para finalizar la ejecución.
        :return:
        '''
        pass



    @property
    def elapsed_time(self):
        '''
        Esta propiedad indica el tiempo total transcurrido desde que se comenzó con la ejecución del controlador.
        :return:
        '''
        return self._elapsed_time

    @property
    def think_time(self):
        '''
        Esta propiedad devuelve una estimación del tiempo necesario para ejecutar el método think() de este
        controlador (se devuelve una media de las últimas mediciones del tiempo transcurrido en las ejecuciones
        de think())
        :return:
        '''
        return self._think_time

    @property
    def update_time(self):
        '''
        Esta propiedad devuelve una estimación del tiempo necesario para ejecutar el método update() de este
        controlador (se devuelve una media de las últimas mediciones del tiempo transcurrido en las ejecuciones
        de update())
        :return:
        '''
        return self._update_time

    @property
    def steps_per_second(self):
        '''
        Esta propiedad devuelve una estimación del número de veces que el bucle principal del controlador se
        ejecuta por segundo.
        :return:
        '''
        return 1 / self._step_time