from modules import cbpi
from modules.core.controller import KettleController, FermenterController
from modules.core.props import Property


@cbpi.fermentation_controller
class GlycolChillerController(FermenterController):

    chiller_offset_min = Property.Number("Cooler Offset ON", True, 0, description="Offset as decimal number when the cooler is switched on. Should be greater then 'Cooler Offset OFF'. For example a value of 2 switches on the cooler if the current temperature is 2 degrees above the target temperature")
    chiller_offset_max = Property.Number("Cooler Offset OFF", True, 0, description="Offset as decimal number when the cooler is switched off. Should be less then 'Cooler Offset ON'. For example a value of 1 switches off the cooler if the current temperature is 1 degree above the target temperature")

    def stop(self):
        '''
        switch the chiller off when controller stops
        :return: 
        '''
        super(FermenterController, self).stop()
        self.cooler_off()

    def run(self):
        '''
        controller logic 
        :return: 
        '''
        while self.is_running():
            # Read current target temp
            target_temp = self.get_target_temp()

            # Read current temp of the fermenter (sensor1)
            temp = self.get_temp()

            # offset 1 - cast to float value
            offset1 = float(self.chiller_offset_min)

            # offset 2 - cast to float value
            offset2 = float(self.chiller_offset_max)

            if temp >= target_temp + offset1:
                self.cooler_on()

            if temp <= target_temp + offset2:
                self.cooler_off()

            # wait for 1 second
            self.sleep(1)
