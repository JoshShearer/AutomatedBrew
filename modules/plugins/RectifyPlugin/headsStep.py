# -*- coding: utf-8 -*-

from modules.core.props import Property, StepProperty
from modules.core.step import StepBase
from .baseColletingStep import BaseColletingStep
from modules import cbpi
from datetime import datetime

@cbpi.step
class HeadsStep(StepBase, BaseColletingStep):
    collectingSpeed = Property.Number("Sampling rate, ml / h", configurable=True, default_value=100)
    headsTotal = Property.Number("Number of heads for selection, ml", configurable=True, default_value=100)
    
    total = 0
    time = datetime.utcnow()

    def finish(self):
        self.actor_off(int(self.collectingActor))
        self.notify("", "Head selection completed", type="success", timeout=2000)

    def execute(self):
        self.updateMaxCollectingSpeed()
        self.calculateActorPower()
        self.manageActor()
        self.checkTotalCollecting()
        self.notifySensor()

    def checkTotalCollecting(self):
        time = datetime.utcnow()
        if (time-self.time).total_seconds() >= 10:
            self.time = time
            self.total += float(self.collectingSpeed)/360.0

        if self.total >= int(self.headsTotal):
            next(self)
