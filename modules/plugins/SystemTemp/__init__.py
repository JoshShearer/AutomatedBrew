import os, threading, time
from modules import cbpi, app
from modules.core.hardware import SensorPassive


class myThread (threading.Thread):

    value = 0


    def __init__(self):
        threading.Thread.__init__(self)
        self.value = 0
        self.runnig = True

    def shutdown(self):
        pass

    def stop(self):
        self.runnig = False

    def run(self):

        while self.runnig:
            try:
                app.logger.info("READ SYSTEM TEMP")
                res = os.popen('vcgencmd measure_temp').readline()
                temp = float(res.replace("temp=","").replace("'C\n",""))
                self.value = temp
            except:
                pass

            time.sleep(4)

@cbpi.sensor
class SystemTempSensor(SensorPassive):
    def init(self):

        self.t = myThread()

        def shudown():
            shudown.cb.shutdown()
        shudown.cb = self.t

        self.t.start()

    def stop(self):
        try:
            self.t.stop()
        except:
            pass

    def read(self):
        if self.get_config_parameter("unit", "C") == "C":
            self.data_received(round(self.t.value, 2))
        else:
            self.data_received(round(9.0 / 5.0 * self.t.value + 32, 2))
