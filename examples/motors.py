'''
Ejemplo que demuestra como modificar los parámetros de los motores del robot e-puck.
- Primero se establece la velocidad del motor izquierdo a pi rad / s y el motor derecho parado durante 4 seg
- Luego el motor izquierdo parado  y el motor derecho a pi rad / s durante otros 4 seg
- A continuación, sendos motores a velocidad máxima (2pi rad / s) durante 4 seg
'''

from epuck_controller import EPuckController
from epuck import EPuck as PhysicalEPuck
from vrep_epuck import VRepEPuck as VirtualEPuck
from math import pi

class MotorsExampleController(EPuckController):
    def init(self):
        print('Initializing e-puck controller')


    def close(self):
        print('Closing e-puck controlller')

    def think(self):
        if self.elapsed_time > 16:
            raise StopIteration()

    def act(self):
        # Este método es ejeuctado en cada iteración del bucle del controlador después de
        # los métodos sense() y think(). Debes colocar aqui el código para modificar los parámetros
        # de los actuadores (leds y motores)

        if self.elapsed_time <= 4:
            # La velocidad de los motores la establecemos en rads / s
            # La velocidad máxima es 2pi rad /s
            self.epuck.left_motor.speed = pi
            self.epuck.right_motor.speed = 0

        elif self.elapsed_time <= 8:
            self.epuck.left_motor.speed = 0
            self.epuck.right_motor.speed = pi

        elif self.elapsed_time <= 12:
            # También podemos asignar la velocidad para sendos motores con una única instrucción...
            self.epuck.motors.speeds = 2 * pi


if __name__ == '__main__':
    '''
    Escoge una de las siguientes líneas, la otra comentala.
    Si escoges la primera, el controlador usará el robot e-puck en una escena
    virtual del simulador V-rep. En caso contrario, se ejecutará sobre un robot
    e-puck físico.
    '''
    epuck = VirtualEPuck(address = '127.0.0.1:19997')
    # epuck = PhysicalEPuck()

    controller = MotorsExampleController(epuck, enable_streaming = True)
    controller.run()
