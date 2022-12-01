from modules import cbpi
from modules.core.hardware import ActorBase, SensorActive
from modules.core.props import Property
import serial
import time
import logging

@cbpi.initalizer(order=3000)
def init(cbpi):
    cbpi.app.logger.info('initialising serialActor')
    global serialConnection
    global errorMessage
    try:
        serialConnection = serial.Serial('/dev/ttyACM0',9600)
        if serialConnection.isOpen():
            cbpi.app.logger.info('Serial Connection was open. Closing and opening again.')
            serialConnection.close()
            time.sleep(2)
            serialConnection.open()
        else:
            try:
                serialConnection.open()
            except Exception as e:
                cbpi.app.logger.error("FAILED to open Serial Connection to SerActor")
    except Exception as e:
        cbpi.app.logger.error("FAILED to setup Serial Connection to SerActor")

@cbpi.actor
class SerialActor(ActorBase):

    pPower = 0

    def on(self, power):
        cbpi.app.logger.info('turning heater on. power is {}.'.format(power))
        self.set_power(power)

    def off(self):
        cbpi.app.logger.info('turning heater off')
        self.set_power(0)

    def set_power(self, power):
        if power is not None:
            if power != self.pPower:
                power = min(100,power)
                power = max(0,power)
                self.pPower = int(power)
                cbpi.app.logger.info('setting power to {}'.format(power))
        serialConnection.write(str(self.pPower))

@cbpi.sensor
class SerialSensor(SensorActive):
    def execute(self):
        global cache
        while self.is_running():
            try:
                while True:
                    newMessage = serialConnection.readline()
                    if newMessage != errorMessage:
                        errorMessage = newMessage
                        cbpi.app.logger.info('Error from Serial: {}'.errorMessage)
                        self.notify(errorMessage, str(params.Kp), type="danger", timeout=None)
            except:
                pass
            time.sleep(1)
