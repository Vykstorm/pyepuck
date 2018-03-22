
'''
Este ejemplo sirve para demostrar como crear un controlador para el robot e-puck.
Solo se conecta a este y no lleva a cabo ninguna acción.
'''

from epuck_controller import EPuckController
from epuck import EPuck as PhysicalEPuck
from vrep_epuck import VRepEPuck as VirtualEPuck


class ConnectExampleController(EPuckController):
    def init(self):
        print('Initializing e-puck controller')

    def close(self):
        print('Closing e-puck controlller')



if __name__ == '__main__':
    '''
    Escoge una de las siguientes líneas, la otra comentala.
    Si escoges la primera, el controlador usará el robot e-puck en una escena
    virtual del simulador V-rep. En caso contrario, se ejecutará sobre un robot
    e-puck físico.
    '''
    epuck = VirtualEPuck(address = '127.0.0.1:19997')
    # epuck = PhysicalEPuck()

    controller = ConnectExampleController(epuck)
    controller.run()
