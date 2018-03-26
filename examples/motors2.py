'''
Ejemplo que demuestra como modificar los parámetros de los motores del robot e-puck.
- Primero se mueve hacia delante durante 4 seg a velocidad máxima
- Rota a la derecha sobre el eje central
- Rota a la izquierda sobre el eje izquierdo (rueda izquierda)
- Se mueve hacia atrás durante 4 seg a velocidad máxima
'''

from epuck_controller import EPuckController
from epuck import EPuck as PhysicalEPuck
from vrep_epuck import VRepEPuck as VirtualEPuck
from time import time
from math import pi

class MotorsExampleController(EPuckController):
    def init(self):
        print('Initializing e-puck controller')

        self.initial_time = time()

    def close(self):
        print('Closing e-puck controlller')

    def think(self):
        self.elapsed_time = time() - self.initial_time
        if self.elapsed_time > 16:
            raise StopIteration()

    def act(self):
        # Este método es ejeuctado en cada iteración del bucle del controlador después de
        # los métodos sense() y think(). Debes colocar aqui el código para modificar los parámetros
        # de los actuadores (leds y motores)

        if self.elapsed_time <= 4:
            self.epuck.move_forward(speed = 1)

        elif self.elapsed_time <= 8:
            self.epuck.rotate(speed = .75, axis = 'center')

        elif self.elapsed_time <= 12:
            self.epuck.rotate(speed = .75, axis = 'left')

        else:
            self.epuck.move_backward(speed = 1)


if __name__ == '__main__':
    '''
    Escoge una de las siguientes líneas, la otra comentala.
    Si escoges la primera, el controlador usará el robot e-puck en una escena
    virtual del simulador V-rep. En caso contrario, se ejecutará sobre un robot
    e-puck físico.
    '''
    epuck = VirtualEPuck(address = '127.0.0.1:19997')
    # epuck = PhysicalEPuck()

    controller = MotorsExampleController(epuck)
    controller.run()
