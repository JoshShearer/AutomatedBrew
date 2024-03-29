# -*- coding: utf-8 -*-

from modules.core.props import Property, StepProperty
from modules.core.step import StepBase
from .baseColletingStep import BaseColletingStep
from modules import cbpi

@cbpi.step
class HeartsStep(StepBase, BaseColletingStep):
    temperatureSensor = StepProperty.Sensor("Temperature sensor", description="Датчик температуры в кубе")
    initialCollecting = Property.Number("Start sampling rate, ml / h", configurable=True, default_value=1000)
    endTemp = Property.Number("Selection completion temperature", configurable=True, default_value=93)
    
    collectingSpeed = 0.0
    temperature = 0

    def finish(self):
        self.actor_off(int(self.collectingActor))
        self.notify("", "Body selection completed", type="success", timeout=2000)

    def execute(self):
        self.updateAndCheckTemperature()
        self.recountCollecting()
        self.notifySensor()
        self.updateMaxCollectingSpeed()
        self.calculateActorPower()
        self.manageActor()

    def recountCollecting(self):
        self.collectingSpeed = int(self.initialCollecting)*(6.04 - 0.06*float(self.temperature))

    def updateAndCheckTemperature(self):
        self.temperature = float(self.get_sensor_value(int(self.temperatureSensor)))
        if self.temperature >= int(self.endTemp):
            next(self)