
from time import sleep
from time import clock

class EPuckController:
    '''
    Representa un controlador para el robot e-puck.
    '''
    def __init__(self, epuck):
        '''
        Inicializa la instancia
        :param epuck: Es una instancia de una subclase de EPuckInterface
        '''
        self.epuck = epuck

        # Esta variable medirá el tiempo que lleva activa la simulación (se actualiza en cada iteración del bucle)
        self._elapsed_time = 0

        # Esta variable configura el número de veces que el bucle principal debe ejecutarse por unidad de tiempo.
        # El número de veces que el bucle principal se ejecutará por segundo es inferior o igual a esta cantidad
        self.sps = 2

        self._think_times = []
        self._update_times = []
        self._think_time = 0
        self._update_time = 0

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
                    inv_sps = 1 / self.sps
                    if step_time < inv_sps:
                        sleep(inv_sps)

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
    