# -*- coding: utf-8 -*-
import time

from modules import cbpi
from modules.core.hardware import ActorBase, SensorPassive, SensorActive
from modules.core.props import Property

try:
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
except Exception as e:
    print e
    pass



@cbpi.actor
class GPIOSimpleInverted(ActorBase):

    gpio = Property.Select("GPIO", options=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27], description="GPIO to which the actor is connected")

    def init(self):
        GPIO.setup(int(self.gpio), GPIO.OUT)
        GPIO.output(int(self.gpio), 1)

    def on(self, power=0):
        print "GPIO ON %s" % str(self.gpio)
        GPIO.output(int(self.gpio), 0)

    def off(self):
        print "GPIO OFF"
        GPIO.output(int(self.gpio), 1)
