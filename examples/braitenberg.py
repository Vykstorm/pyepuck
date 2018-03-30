'''
Algoritmo braitenberg para el robot e-puck usando solo sensores de proximidad.
Ha sido extraído de https://github.com/mmartinortiz/pyePuck/blob/master/examples/braitenberg.py
El autor es mmartinortiz
'''


from epuck_controller import EPuckController
from epuck_constraints import max_motor_speed
from epuck import EPuck as PhysicalEPuck
from vrep_epuck import VRepEPuck as VirtualEPuck
import numpy as np
from math import pi


class BraitenbergController(EPuckController):
    def __init__(self, epuck, *args, **kwargs):
        super().__init__(epuck, *args, **kwargs)
        self.weights = np.array(
            ((150, -35), (100, -15), (80, -10), (-10, -10),
             (-10, -10), (-10, 80), (-30, 100), (-20, 150)),
            dtype = np.float64)

    def init(self):
        print('Initializing e-puck controller')
        self.epuck.prox_sensors.enabled = True
        self.epuck.vision_sensor.enabled = True

    def close(self):
        print('Closing e-puck controlller')


    def sense(self):
        self.values = np.array(self.epuck.prox_sensors.values, dtype=np.float64)

    def act(self):
        # Calculamos la velocidad de sendos motores
        values = 1 - self.values / 512
        wheels_speed = (self.weights.T * values).T.sum(axis = 0)


        # Cambiamos la velocidad de los motores de steps/s a rads/s
        wheels_speed = 2 * pi * wheels_speed / 1000

        # Hacemos que la velocidad siempre este en el intervalo [-max_motor_speed, max_motor_speed]
        wheels_speed = wheels_speed.clip(-max_motor_speed, max_motor_speed)

        epuck = self.epuck
        epuck.left_motor.speed, epuck.right_motor.speed = wheels_speed

if __name__ == '__main__':
    '''
    Escoge una de las siguientes líneas, la otra comentala.
    Si escoges la primera, el controlador usará el robot e-puck en una escena
    virtual del simulador V-rep. En caso contrario, se ejecutará sobre un robot
    e-puck físico.
    '''
    epuck = VirtualEPuck(address = '127.0.0.1:19997')
    # epuck = PhysicalEPuck()

    controller = BraitenbergController(epuck, enable_streaming = True)
    controller.run()
