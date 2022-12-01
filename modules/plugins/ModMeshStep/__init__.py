# -*- coding: utf-8 -*-
 # import time needed for calculation sec -> h:m:s
import time

from modules.core.props import Property, StepProperty
from modules.core.step import StepBase
from modules import cbpi



@cbpi.step
class Mod_MashStep(StepBase):
    '''
    Just put the decorator @cbpi.step on top of a method
    '''
    # Properties
    temp = Property.Number("Temperature", configurable=True, description="Target Temperature of Mash Step")
    kettle = StepProperty.Kettle("Kettle", description="Kettle in which the mashing takes place")
    timer = Property.Number("Timer in Minutes", configurable=True, description="Timer is started when the target temperature is reached")

    # Temp Protection modification start
    protection_temp_diff = Property.Number("Temperature Difference", configurable=True, description="Treshold Temperature = Temperature + Temperature Difference. Timer will stop if this temperature si reached and brewing procces will be interrupted",default_value=8)
    protection_actor = StepProperty.Actor("Protective Circuit Actor",  description="Please select an Actor which will be activated if treshold temperature is reached")
    s = False
    # Temp Protection modification  end

    def init(self):
        '''
        Initialize Step. This method is called once at the beginning of the step
        :return:
        '''
        # set target tep
        self.set_target_temp(self.temp, self.kettle)
        self.s = False
        #de-activate temperature protection
        self.actor_off(self.protection_actor)
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

        # Temp Protection modification start
        #de-activate temperature protection
        self.actor_off(self.protection_actor)
        s = False
        # Temp Protection modification end

    def finish(self):
        self.set_target_temp(0, self.kettle)
        # Temp Protection modification start
        #de-activate temperature protection
        self.actor_off(self.protection_actor)
        s = False
        # Temp Protection modification end

    def execute(self):
        '''
        This method is execute in an interval
        :return:
        '''

        # Check if Target Temp is reached
        if self.get_kettle_temp(self.kettle) >= float(self.temp):
            # Check if Timer is Running
            if self.is_timer_finished() is None:
                self.start_timer(int(self.timer) * 60)

        #Temp protection start modification and overshoot deteection. If temperature is over N Celsius, protection will stop the process
        if (int(self.get_kettle_temp(self.kettle)) >= (int(self.temp) + int(self.protection_temp_diff))) and self.s is False:
            self.s = True
            self.notify("ALARM", "Exiting brewing process - critical temperature is reached", timeout=0, type="danger")
            #Activate temperature protection
            self.actor_on(self.protection_actor)
            #Dont go to the next step, show "Alarm" and remaining time
            self.notify( str(time.strftime('%H:%M:%S', time.gmtime(int((self.timer_remaining()))))),"time until the end of this step", timeout=0)
            #Reset and stop timer
            self.timer_end = True
        #Temp protection end modification

        # Check if timer finished and go to next step
        if self.is_timer_finished() == True and self.s == False:
            self.s = True
            self.notify("Mash Step Completed!", "Starting the next step", timeout=None)
            self.next()
