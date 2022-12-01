import logging
import time

from modules.core.props import Property, StepProperty
from modules.core.step import StepBase
from modules import cbpi

@cbpi.step
class BringToTempOverTime(StepBase):
    # Properties
    kettle = StepProperty.Kettle("Kettle")
    temp = Property.Number("Temperature", configurable=True)
    steps = Property.Number("Number of Steps", configurable=True)
    timer = Property.Number("Timer in Minutes", configurable=True)
    stepsLeft = 0
    timeInc = 0
    currentTargetTemp = 0.0

    def init(self):
        cbpi.app.logger.info("BringToTempOverTime Init called")
        # Start the timer
        if self.is_timer_finished() is None:
            cbpi.app.logger.info("BringToTempOverTime Starting timer for %d minutes", int(self.timer))
            self.start_timer(int(self.timer) * 60)

        # Set the steps left
        self.stepsLeft = int(self.steps)
        
        # Set the time increment
        self.timeInc = ((int(self.timer) * 60) / int(self.steps))
        
    def reset(self):
        cbpi.app.logger.info("BringToTempOverTime Reset called")

        self.stop_timer()
        self.set_target_temp(0, self.kettle)

    def finish(self):
        cbpi.app.logger.info("BringToTempOverTime Finish called")
        self.set_target_temp(0, self.kettle)

    def execute(self):
        # This method is execute in an interval
        #cbpi.app.logger.info("BringToTempOverTime Execute called")

        # Check if Target Temp is reached
        if self.get_kettle_temp(self.kettle) >= float(self.temp):
            cbpi.app.logger.info("BringToTempOverTime Kettle temp is >= temp") 
            # If timer is finished go to the next step
            if self.is_timer_finished() == True:
                cbpi.app.logger.info("BringToTempOverTime Target temp reached and timer finished, moving to next step")
                self.next()
        elif self.currentTargetTemp <= 0.0:
            # If we are out of steps just set the final temp
            if int(self.stepsLeft) <= 0:
                cbpi.app.logger.info("BringToTempOverTime Zero steps left") 
                self.currentTargetTemp = self.temp
            else:
                cbpi.app.logger.info("BringToTempOverTime Kettle currentTargetTemp is <= 0.0") 
                # Calculate the increment of temperature in n steps
                perStepTemp = ((float(self.temp) - self.get_kettle_temp(self.kettle)) / int(self.stepsLeft))
                self.currentTargetTemp = self.get_kettle_temp(self.kettle) + perStepTemp                
                cbpi.app.logger.info("BringToTempOverTime New target temp calculated from perStepTemp of %f with new temp of %f", float(perStepTemp), float(self.currentTargetTemp))
                self.stepsLeft = int(self.stepsLeft) - 1
                cbpi.app.logger.info("BringToTempOverTime Steps left is %d", int(self.stepsLeft))

            # set target temp
            cbpi.app.logger.info("BringToTempOverTime Setting target temp")
            cbpi.app.logger.info("BringToTempOverTime To %f", self.currentTargetTemp)
            self.set_target_temp(self.currentTargetTemp, self.kettle)
        elif self.timer_remaining() <= int(self.stepsLeft) * int(self.timeInc):
            cbpi.app.logger.info("BringToTempOverTime Time for step has expired, moving to next target temp and step") 
            self.currentTargetTemp = 0.0   

