from modules import cbpi
from modules.core.controller import KettleController
from modules.core.props import Property

@cbpi.controller
class LauteringAutomation(KettleController):

    minSensorDistance = Property.Number("Minimum Distance to Sensor (High Fill Level)", True, 0)
    maxSensorDistance = Property.Number("Maximum Distance to Sensor (Low Fill Level)", True, 0)
    pumping = False
    currentFillLevel = 0

    def stop(self):
        super(KettleController, self).stop()
        self.heater_off()

    def run(self):
        self.sleep(1)
        while self.is_running():
            self.currentFillLevel = self.get_temp()
            if bool(self.pumping):
                if self.currentFillLevel >= float(self.maxSensorDistance):
                    self.heater_off()
                    self.pumping = False
                else:
                    self.heater_on(100)
            else:
                if self.currentFillLevel <= float(self.minSensorDistance):
                    self.heater_on(100)
                    self.pumping = True
                else:
                    self.heater_off()
            self.sleep(1)

