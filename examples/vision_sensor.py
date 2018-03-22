'''
Ejemplo demostrativo de como muestrear el sensor de visión del robot e-puck
'''

from epuck_controller import EPuckController
from epuck import EPuck as PhysicalEPuck
from vrep_epuck import VRepEPuck as VirtualEPuck
from PIL import Image

class VisionSensorExampleController(EPuckController):
    def init(self):
        print('Initializing e-puck controller')

        # Activamos solo el sensor de visión
        self.epuck.vision_sensor.enabled = True

        # Configuramos los parámetros del sensor
        self.epuck.vision_sensor.set_params(mode = 'RGB', size = (400, 400), zoom = 1, resample = Image.NEAREST)


    def close(self):
        print('Closing e-puck controlller')

    def sense(self):
        # Esta rutina se ejecuta en cada iteración del bucle principal del controlador.
        # Debes añadir aqui el código para muestrear toda clase de sensores...

        # Muestreamos la imágen del sensor de visión
        image = self.epuck.vision_sensor.value

        # Mostramos la imágen.
        image.transpose(Image.FLIP_TOP_BOTTOM).show()

        # Después de muestrar una vez el sensor, hacemos el programa finalize...
        raise StopIteration()


if __name__ == '__main__':
    '''
    Escoge una de las siguientes líneas, la otra comentala.
    Si escoges la primera, el controlador usará el robot e-puck en una escena
    virtual del simulador V-rep. En caso contrario, se ejecutará sobre un robot
    e-puck físico.
    '''
    epuck = VirtualEPuck(address = '127.0.0.1:19997')
    # epuck = PhysicalEPuck()

    controller = VisionSensorExampleController(epuck)
    controller.run()
