from modules import cbpi
from modules.core.controller import KettleController
from modules.core.props import Property, StepProperty
from modules.core.step import StepBase
import time


@cbpi.controller
class SimpleBoilLogic(KettleController):

    ramp_power = Property.Number("Ramp Up Power %", True, 100)
    boil_power = Property.Number("Boil Power %", True, 70)

    def stop(self):

        super(KettleController, self).stop()
        self.heater_off()

    def run(self):

        r_power = int(self.ramp_power)
        b_power = int(self.boil_power)


        while self.is_running():
            temp = self.get_temp()
            r_limit = self.get_target_temp()
            if temp < r_limit and r_limit > 0:
                self.heater_on(r_power)
                self.actor_power(r_power)
            if temp >= r_limit and r_limit > 0:
                self.heater_on(b_power)
                self.actor_power(b_power)
            self.sleep(1)
