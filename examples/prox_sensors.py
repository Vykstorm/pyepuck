'''
Ejemplo demostrativo de como muestrear los sensores de proximidad del robot e-puck en
esta librería
'''

from epuck_controller import EPuckController
from epuck import EPuck as PhysicalEPuck
from vrep_epuck import VRepEPuck as VirtualEPuck
from time import sleep

class ProximitySensorsExampleController(EPuckController):
    def init(self):
        print('Initializing e-puck controller')

        # Activamos todos los sensores de proximidad (Están desactivados por defecto)
        self.epuck.prox_sensors.enabled = True

        # También se pueden activar de forma individual...
        self.epuck.prox_sensor15.enabled = True
        self.epuck.prox_sensor45.enabled = True


    def close(self):
        print('Closing e-puck controlller')

    def sense(self):
        # Esta rutina se ejecuta en cada iteración del bucle principal del controlador.
        # Debes añadir aqui el código para muestrear toda clase de sensores...

        # Muestrear individualmente un sensor de proximidad, devuelve un valor númerico:
        value = self.epuck.prox_sensor15.value

        # Muestrear todos los sensores devuelve una lista de valores numéricos ordenados
        # en función del índice del sensor (IR1, IR2, ...)
        values = self.epuck.prox_sensors.values

        # Almacena los valores en esta instancia para que estén disponibles en los métodos
        # think() y act()
        self.values = values

        # Imprimimos los valores
        print('Proximity sensors: ', self.values)

        sleep(5)

if __name__ == '__main__':
    '''
    Escoge una de las siguientes líneas, la otra comentala.
    Si escoges la primera, el controlador usará el robot e-puck en una escena
    virtual del simulador V-rep. En caso contrario, se ejecutará sobre un robot
    e-puck físico.
    '''
    epuck = VirtualEPuck(address = '127.0.0.1:19997')
    # epuck = PhysicalEPuck()

    controller = ProximitySensorsExampleController(epuck, enable_streaming = True)
    controller.run()
