# -*- coding: utf-8 -*-
import time


from modules.core.props import Property, StepProperty
from modules.core.step import StepBase
from modules import cbpi

@cbpi.step
class SwitchSensorMashStep(StepBase):
    '''
    Just put the decorator @cbpi.step on top of a method
    '''
    # Properties
    temp = Property.Number("Temperature", configurable=True, description="Target Temperature of Mash Step")
    kettle = StepProperty.Kettle("Kettle", description="Kettle in which the mashing takes place")
    timer = Property.Number("Timer in Minutes", configurable=True, description="Timer is started when the target temperature is reached")
    sensor = StepProperty.Sensor("Sensor", description="Selectable secondary sensor")
    pump = StepProperty.Actor("Pump, etc.")

    def init(self):
        '''
        Initialize Step. This method is called once at the beginning of the step
        :return:
        '''
        # set target tep
        self.set_target_temp(self.temp, self.kettle)
        self.actor_on(int(self.pump))

    @cbpi.action("Start Timer Now")
    def start(self):
        '''
        Custom Action which can be execute form the brewing dashboard.
        All method with decorator @cbpi.action("YOUR CUSTOM NAME") will be available in the user interface
        :return:
        '''
        if self.is_timer_finished() is None:
            self.start_timer(int(self.timer) * 60)

    def reset(self):
        self.stop_timer()
        self.set_target_temp(self.temp, self.kettle)

    def finish(self):
        self.set_target_temp(0, self.kettle)
        self.actor_off(int(self.pump))

    def execute(self):
        '''
        This method is execute in an interval
        :return:
        '''

        # Check if Target Temp is reached
        if cbpi.get_sensor_value(int(self.sensor)) >= float(self.temp):
            if self.is_timer_finished() is None:
                self.start_timer(int(self.timer) * 60)

        # Check if timer finished and go to next step
        if self.is_timer_finished() == True:
            self.notify("Mash Step Completed!", "Starting the next step", timeout=None)
            next(self)
