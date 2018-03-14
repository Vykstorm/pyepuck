

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
                    self.step()
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
        self.epuck.update()
        self.sense()
        self.think()
        self.act()


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
