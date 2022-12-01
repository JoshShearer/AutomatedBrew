
import time
from modules import cbpi
from modules.core.hardware import SensorActive
from modules.core.props import Property

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
except Exception as e:
    print(e)
    pass

def capture_distance_data(GPIO_TRIGGER,GPIO_ECHO):
    #GPIO Mode (BOARD / BCM)
    GPIO.setmode(GPIO.BCM)

    #set GPIO direction (IN / OUT)
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)

    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    StopTime = time.time()

    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2

    return distance

def convert_cm_to_in(distance):
    distance_in = distance * .3937
    return distance_in

def calc_fill_percent(current_height, tank_height, head_height):
    effective_height = current_height - head_height
    max_height = tank_height - head_height
    percent = float((max_height-effective_height)/max_height)*100
    return round(percent, 1)



@cbpi.sensor
class LevelSensorUS100(SensorActive):

    gpio_trigger = Property.Select("Trigger GPIO pin", options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27])
    gpio_echo = Property.Select("Echo GPIO pin", options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27])
    height_units = Property.Select("Height Units", options=["in", "cm"], description="units")
    height_disp = Property.Select("Height Display", options=["Percent", "Height"], description="Height Display")
    head_height = Property.Number("Head Height", configurable=True, default_value=0, description="Height from sensor to max water height")
    tank_height = Property.Number("Tank Height", configurable=True, default_value=23, description="Height from bottom of tank to max water level")


    def init(self):
        print("Initializing")

    def get_unit(self):
        if self.height_disp == "Percent":
            unit = "%"
        else:
            unit = self.height_units
        return unit

    def execute(self):
        while self.is_running():
            #self.api.socketio.sleep(.1)
            #if GPIO.event_detected(int(self.gpio)):
            # if self.gpio_trigger is not None:
            distance = capture_distance_data(self.gpio_trigger, self.gpio_echo)

            if self.height_disp == "Percent":
                if self.height_units == "in":
                    distance = convert_cm_to_in(distance)
                else:
                    fill_percent = calc_fill_percent(distance, self.tank_height, self.head_height)

                fill_percent = calc_fill_percent(distance, self.tank_height, self.head_height)
                self.data_received(fill_percent)
            else:
                if self.height_units == "in":
                    distance = convert_cm_to_in(distance)
                max_height = self.tank_height - self.head_height
                current_height = max_height - distance
                self.data_received(current_height)
            self.api.socketio.sleep(2)

    def stop(self):
        pass

@cbpi.initalizer()
def init(cbpi):
    pass

