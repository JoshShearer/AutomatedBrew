from modules import cbpi
from modules.core.controller import KettleController
from modules.core.props import Property


@cbpi.controller
class OvershootLogic_by_Norn(KettleController):

    # Custom Properties
    overshoot = Property.Number("Overshoot", True, 0)
    state = False
    setpoint = 0

    def stop(self):
        '''
        Invoked when the automatic is stopped.
        Normally you switch off the actors and clean up everything
        :return: None
        '''
        super(KettleController, self).stop()
        self.heater_off()


    def run(self):
        '''
        Each controller is exectuted in its own thread. The run method is the entry point
        :return: 
        '''

        while self.is_running():
            currentTemp = self.get_temp() ## Current temperature
            targetTemp = self.get_target_temp() ## Target Temperature
            ## Current Temp is below Target Temp ... overshoot is on ...  switch heater on
            if(currentTemp + float(self.overshoot) < targetTemp and self.state == False and targetTemp != self.setpoint):
                self.state = True
                self.heater_on(100)
            ## Switch overshoot off if target temp is reached
            if(currentTemp >= targetTemp):
                self.setpoint = targetTemp
            ## Current Temp is below Target Temp ... overshoot is off ...  switch heater on
            if(currentTemp < targetTemp and self.state == False and targetTemp == self.setpoint):
                self.state = True
                self.heater_on(100)
            ## Current Temp is equal or higher than Target Temp ... overshoot is on ... switch Heater off
            if(currentTemp + float(self.overshoot) >= targetTemp and self.state == True and targetTemp != self.setpoint):
                self.state = False
                self.heater_off()
            ## Current Temp is equal or higher than Target Temp ... overshoot is off ... switch Heater off
            if(currentTemp >= targetTemp and self.state == True and targetTemp == self.setpoint):
                self.state = False
                self.heater_off()

            self.sleep(1)
