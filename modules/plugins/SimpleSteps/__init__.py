# -*- coding: utf-8 -*-
################################################################################

from modules.core.props import Property, StepProperty
from modules.core.step import StepBase
from modules import cbpi
import time
from os import system, listdir, remove

LOG_DIR = "./logs/"
APP_LOG = "app.log"
LOG_SEP = "-=-"

################################################################################
@cbpi.step
class SimpleManualStep(StepBase):
    # Properties
    heading = Property.Text("Heading", configurable=True, default_value="Step Alert", description="First line of notification.")
    message = Property.Text("Message", configurable=True, default_value="Press next button to continue", description="Second line of notification.")
    notifyType = Property.Select("Type", options=["success","info","warning","danger"])
    proceed = Property.Select("Next Step", options=["Pause","Continue"], description="Whether or not to automatically continue to the next brew step.")

    #-------------------------------------------------------------------------------
    def init(self):
        if self.notifyType not in ["success","info","warning","danger"]:
            self.notifyType = "info"
        self.notify(self.heading, self.message, type=self.notifyType, timeout=None)
        if self.proceed == "Continue":
            self.next()

################################################################################
@cbpi.step
class SimpleTargetStep(StepBase):
    # Properties
    auto_mode = Property.Select("Auto Mode", options=["Set to ON","Set to OFF","No Change"])
    kettle = StepProperty.Kettle("Kettle")
    target = Property.Number("Target Temp", configurable=True)

    #-------------------------------------------------------------------------------
    def init(self):
        self.set_target_temp(float(self.target), int(self.kettle))
        if self.auto_mode == "Set to ON":
            self.setAutoMode(True)
        elif self.auto_mode == "Set to OFF":
            self.setAutoMode(False)
        self.next()

    #-------------------------------------------------------------------------------
    def setAutoMode(self, auto_state):
        try:
            kettle = cbpi.cache.get("kettle")[int(self.kettle)]
            if (kettle.state is False) and (auto_state is True):
                # turn on
                if kettle.logic is not None:
                    cfg = kettle.config.copy()
                    cfg.update(dict(api=cbpi, kettle_id=kettle.id, heater=kettle.heater, sensor=kettle.sensor))
                    instance = cbpi.get_controller(kettle.logic).get("class")(**cfg)
                    instance.init()
                    kettle.instance = instance
                    def run(instance):
                        instance.run()
                    t = cbpi.socketio.start_background_task(target=run, instance=instance)
                kettle.state = not kettle.state
                cbpi.emit("UPDATE_KETTLE", cbpi.cache.get("kettle")[int(self.kettle)])
            elif (kettle.state is True) and (auto_state is False):
                # turn off
                kettle.instance.stop()
                kettle.state = not kettle.state
                cbpi.emit("UPDATE_KETTLE", cbpi.cache.get("kettle")[int(self.kettle)])
        except Exception as e:
            cbpi.notify("Error", "Failed to set Auto mode {}".format(["OFF","ON"][auto_state]), type="danger", timeout=None)
            cbpi.app.logger.error(e)

################################################################################
@cbpi.step
class SimpleActorTimer(StepBase):
    # Properties
    actor1 = StepProperty.Actor("Actor 1")
    actor2 = StepProperty.Actor("Actor 2")
    timer = Property.Number("Timer in Minutes", configurable=True, description="Timer is started immediately.")

    #-------------------------------------------------------------------------------
    def init(self):
        self.actors = [self.actor1, self.actor2]
        self.actors_on()

    #-------------------------------------------------------------------------------
    def finish(self):
        self.actors_off()

    #-------------------------------------------------------------------------------
    def execute(self):
        # Check if Timer is Running
        if self.is_timer_finished() is None:
            self.start_timer(float(self.timer) * 60)

        # Check if timer finished and go to next step
        if self.is_timer_finished() == True:
            self.notify("{} complete".format(self.name), "Starting the next step", timeout=None)
            self.next()

    #-------------------------------------------------------------------------------
    def actors_on(self):
        for actor in self.actors:
            try: self.actor_on(int(actor))
            except: pass

    def actors_off(self):
        for actor in self.actors:
            try: self.actor_off(int(actor))
            except: pass

################################################################################
@cbpi.step
class SimpleChillToTemp(StepBase):
    # Properties
    actor1 = StepProperty.Actor("Actor 1", description="Actor to turn on until target temp is reached")
    actor2 = StepProperty.Actor("Actor 2", description="Actor to turn on until target temp is reached")
    kettle_prop = StepProperty.Kettle("Kettle", description="Kettle in which the chilling takes place")
    target_prop = Property.Number("Temperature", configurable=True, description="Target temperature of chill step")

    #-------------------------------------------------------------------------------
    def init(self):
        self.actors = [self.actor1, self.actor2]
        self.target = float(self.target_prop)
        self.kettle = int(self.kettle_prop)

        # set target temp
        if self.kettle:
            self.set_target_temp(self.target, self.kettle)
            self.start_time = time.time()
            self.actors_on()
        else:
            cbpi.notify("No kettle defined", "Starting the next step", type="danger", timeout=None)
            self.next()

    #-------------------------------------------------------------------------------
    def reset(self):
        self.set_target_temp(self.target, self.kettle)

    #-------------------------------------------------------------------------------
    def finish(self):
        self.actors_off()

    #-------------------------------------------------------------------------------
    def execute(self):
        # Check if Target Temp is reached
        if float(self.get_kettle_temp(self.kettle)) <= self.target:
            elapsed_time = int(time.time() - self.start_time)
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            if hours:
                elapsed_text = '{}:{:0>2d}:{:0>2d}'.format(hours, minutes, seconds)
            else:
                elapsed_text = '{}:{:0>2d}'.format(minutes, seconds)

            self.notify("{} complete".format(self.name), "Chill temp reached in {}".format(elapsed_text), timeout=None)
            self.next()

    #-------------------------------------------------------------------------------
    def actors_on(self):
        for actor in self.actors:
            try: self.actor_on(int(actor))
            except: pass

    def actors_off(self):
        for actor in self.actors:
            try: self.actor_off(int(actor))
            except: pass

################################################################################
@cbpi.step
class SimpleClearLogsStep(StepBase):
    #-------------------------------------------------------------------------------
    def init(self):
        log_names = listdir(LOG_DIR)
        for log_name in log_names:
            if (log_name[-4:] == ".log") and (log_name != APP_LOG) and (LOG_SEP not in log_name):
                remove(LOG_DIR+log_name)

        self.next()

################################################################################
@cbpi.step
class SimpleSaveLogsStep(StepBase):

    #-------------------------------------------------------------------------------
    def init(self):
        brew_name  = cbpi.get_config_parameter("brew_name", "")
        if brew_name:
            brew_name = "_".join(brew_name.split())
        else:
            brew_name = time.strftime("Brew_%Y_%m_%d")

        log_names = listdir(LOG_DIR)
        for log_name in log_names:
            if (log_name[-4:] == ".log") and (log_name != APP_LOG) and (LOG_SEP not in log_name):
                system("cat {} > {}".format(LOG_DIR+log_name, LOG_DIR+brew_name+LOG_SEP+log_name))

        self.next()

################################################################################
@cbpi.step
class SimpleToggleStep(StepBase):

	# Properties
	actor = StepProperty.Actor("Actor")
	power = Property.Number("Power", configurable=True)
	toggle_type = Property.Select("Toggle Type", options=["On", "Off", "Power Only"])

	def init(self):
		if self.toggle_type == "On":
			if self.power is not None and self.power:
				self.actor_on(int(self.actor), self.power)
			else:
				self.actor_on(int(self.actor))
		if self.toggle_type == "Off":
			self.actor_off(int(self.actor))
		if self.toggle_type == "Power Only" and self.power is not None and self.power:
			self.actor_power(int(self.actor), self.power)

	def finish(self):
		pass

	def execute(self):
		self.next()

################################################################################
@cbpi.step
class SimpleMashInStep(StepBase):
    # Properties
    a_kettle_prop = StepProperty.Kettle("Kettle", description="Kettle in which the mashing takes place")
    b_target_prop = Property.Number("Temperature", configurable=True, description="Target Temperature of Mash Step")
    c_agitator_prop = Property.Select("Run agitator while heating?", options=["Yes","No"])
    d_kill_heat_prop = Property.Select("Turn off heater when target reached?", options=["Yes","No"])

    #-------------------------------------------------------------------------------
    def init(self):
        self.kettle = int(self.a_kettle_prop)
        self.target = float(self.b_target_prop)
        self.agitator_run = self.c_agitator_prop == "Yes"
        self.kill_heat = self.d_kill_heat_prop == "Yes"
        self.done = False

        self.agitator = getAgitator(cbpi.cache.get("kettle")[self.kettle].agitator)

        # set target temp
        self.set_target_temp(self.target, self.kettle)
        if self.agitator and self.agitator_run:
            self.actor_on(self.agitator)

    #-------------------------------------------------------------------------------
    def finish(self):
        self.set_target_temp(0, self.kettle)

    #-------------------------------------------------------------------------------
    def execute(self):
        # Check if Target Temp is reached
        if (self.get_kettle_temp(self.kettle) >= self.target) and (self.done is False):
            self.done = True
            if self.kill_heat:
                self.set_target_temp(0, self.kettle)
            if self.agitator:
                self.actor_off(self.agitator)
            self.notify("{} complete".format(self.name), "Press next button to continue", type='warning', timeout=None)

################################################################################
@cbpi.step
class SimpleMashStep(StepBase):
    # Properties
    a_kettle_prop = StepProperty.Kettle("Kettle", description="Kettle in which the mashing takes place")
    b_target_prop = Property.Number("Temperature", configurable=True, description="Target Temperature of Mash Step")
    c_timer_prop = Property.Number("Timer in minutes", configurable=True, description="Amount of time to maintain taget temperature in this step")
    d_offset_prop = Property.Number("Target timer offset", configurable=True, default_value=0, description="Start timer when temperature is this close to target. Useful for PID heaters that approach target slowly.")
    e_agitator_start_prop = Property.Select("Turn agitator on at start?", options=["Yes","No"])
    f_agitator_stop_prop = Property.Select("Turn agitator off at end?", options=["Yes","No"])
    #-------------------------------------------------------------------------------
    def init(self):
        self.kettle = int(self.a_kettle_prop)
        self.target = float(self.b_target_prop)
        self.timer = float(self.c_timer_prop)
        self.offset = float(self.d_offset_prop)
        self.agitator_start = self.e_agitator_start_prop == "Yes"
        self.agitator_stop = self.f_agitator_stop_prop == "Yes"

        self.agitator = getAgitator(cbpi.cache.get("kettle")[self.kettle].agitator)

        # set target temp
        self.set_target_temp(self.target, self.kettle)
        if self.agitator and self.agitator_start:
            self.actor_on(self.agitator)

    #-------------------------------------------------------------------------------
    @cbpi.action("Start Timer Now")
    def start(self):
        if self.is_timer_finished() is None:
            self.start_timer(self.timer * 60)

    #-------------------------------------------------------------------------------
    def reset(self):
        self.stop_timer()
        self.set_target_temp(self.target, self.kettle)

    #-------------------------------------------------------------------------------
    def finish(self):
        self.set_target_temp(0, self.kettle)
        if self.agitator and self.agitator_stop:
            self.actor_off(self.agitator)

    #-------------------------------------------------------------------------------
    def execute(self):
        # Check if Target Temp is reached
        if self.get_kettle_temp(self.kettle) >= self.target - self.offset:
            # Check if Timer is Running
            if self.is_timer_finished() is None:
                self.start_timer(self.timer * 60)

        # Check if timer finished and go to next step
        if self.is_timer_finished() is True:
            self.notify("{} complete".format(self.name), "Starting the next step", type='success', timeout=None)
            self.next()

################################################################################
@cbpi.step
class SimpleBoilStep(StepBase):
    # Properties
    textDesc = "Brief description of the addition"
    timeDesc = "Time in minutes before end of boil"
    add_1_text = Property.Text("Addition 1 Name", configurable=True, description = textDesc)
    add_1_time = Property.Number("Addition 1 Time", configurable=True, description = timeDesc)
    add_2_text = Property.Text("Addition 2 Name", configurable=True, description = textDesc)
    add_2_time = Property.Number("Addition 2 Time", configurable=True, description = timeDesc)
    add_3_text = Property.Text("Addition 3 Name", configurable=True, description = textDesc)
    add_3_time = Property.Number("Addition 3 Time", configurable=True, description = timeDesc)
    add_4_text = Property.Text("Addition 4 Name", configurable=True, description = textDesc)
    add_4_time = Property.Number("Addition 4 Time", configurable=True, description = timeDesc)
    add_5_text = Property.Text("Addition 5 Name", configurable=True, description = textDesc)
    add_5_time = Property.Number("Addition 5 Time", configurable=True, description = timeDesc)
    add_6_text = Property.Text("Addition 6 Name", configurable=True, description = textDesc)
    add_6_time = Property.Number("Addition 6 Time", configurable=True, description = timeDesc)
    add_7_text = Property.Text("Addition 7 Name", configurable=True, description = textDesc)
    add_7_time = Property.Number("Addition 7 Time", configurable=True, description = timeDesc)
    add_8_text = Property.Text("Addition 8 Name", configurable=True, description = textDesc)
    add_8_time = Property.Number("Addition 8 Time", configurable=True, description = timeDesc)

    kettle_prop = StepProperty.Kettle("Kettle", description="Kettle in which the boiling step takes place")
    target_prop = Property.Number("Temperature", configurable=True, description="Target temperature for boiling")
    timer_prop = Property.Number("Timer in Minutes", configurable=True, default_value=90, description="Timer is started when target temperature is reached")

    warning_addition_prop = Property.Number("Addition Warning", configurable=True, default_value=30, description="Time in seconds to warn before each addition")
    warning_boil_prop = Property.Number("Boil Warning", configurable=True, default_value=1, description="Degrees below target to warn of impending boil")

    #-------------------------------------------------------------------------------
    def init(self):

        self.target = float(self.target_prop)
        self.kettle = int(self.kettle_prop)
        self.timer = float(self.timer_prop) * 60.0
        self.warn_add = float(self.warning_addition_prop)
        self.warn_boil = float(self.warning_boil_prop)

        self.done_boil_warn = False
        self.done_boil_alert = False

        # set the additions dictionary
        self.additions = dict()
        for i in range(1,9):
            additionTime = self.__getattribute__("add_{}_time".format(i))
            additionText = self.__getattribute__("add_{}_text".format(i))
            try:
                if additionText is None:
                    additionText = "Addition {}".format(i)
                self.additions[i] = {
                    'text': additionText,
                    'time': float(additionTime) * 60.0,
                    'mins': int(additionTime),
                    'done': False,
                    'warn': False,
                }
            except:
                # empty or invalid addition
                pass
        # set target temp
        self.set_target_temp(self.target, self.kettle)

    #-------------------------------------------------------------------------------
    @cbpi.action("Start Timer Now")
    def start(self):
        if self.is_timer_finished() is None:
            self.start_timer(self.timer)

    #-------------------------------------------------------------------------------
    def reset(self):
        self.stop_timer()
        self.set_target_temp(self.target, self.kettle)

    #-------------------------------------------------------------------------------
    def finish(self):
        self.set_target_temp(0, self.kettle)

    #-------------------------------------------------------------------------------
    def execute(self):
        # Check if Target Temp is reached
        if self.is_timer_finished() is None:
            self.check_boil_warnings()
            if self.get_kettle_temp(self.kettle) >= self.target:
                self.start_timer(self.timer)
        elif self.is_timer_finished() is True:
            self.notify("{} complete".format(self.name), "Starting the next step", type='success', timeout=None)
            self.next()
        else:
            self.check_addition_timers()

    #-------------------------------------------------------------------------------
    def check_addition_timers(self):
        for i in self.additions:
            addition_time = self.timer_end - self.additions[i]['time']
            warning_time = addition_time - self.warn_add
            now = time.time()
            if not self.additions[i]['warn'] and now > warning_time:
                self.additions[i]['warn'] = True
                self.notify("Warning: {} min Additions".format(self.additions[i]['mins']),
                            "Add {} in {} seconds".format(self.additions[i]['text'],self.warn_add),
                            type='info', timeout=(self.warn_add - 1)*1000)
            if not self.additions[i]['done'] and now > addition_time:
                self.additions[i]['done'] = True
                self.notify("Alert: {} min Additions".format(self.additions[i]['mins']),
                            "Add {} now".format(self.additions[i]['text']),
                            type='warning', timeout=None)

    #-------------------------------------------------------------------------------
    def check_boil_warnings(self):
        if (not self.done_boil_warn) and (self.get_kettle_temp(self.kettle) >= self.target - self.warn_boil):
            self.notify("Warning: Boil Approaching", "Current Temp {:.1f}".format(self.get_kettle_temp(self.kettle)),
                        type="info", timeout=self.warn_add*1000)
            self.done_boil_warn = True
        if (not self.done_boil_alert) and (self.get_kettle_temp(self.kettle) >= self.target):
            self.notify("Alert: Boil Imminent", "Current Temp {:.1f}".format(self.get_kettle_temp(self.kettle)),
                        type="warning", timeout=None)
            self.done_boil_alert = True

################################################################################
@cbpi.step
class SimpleMessageStep(StepBase):

    messagetodisplay = Property.Text("Message To Display", configurable=True, default_value="Message you want to display", description="Message to be displayed")
    timer = Property.Number("Seconds to wait for next step (use 0 to wait for user)?", configurable=True, default_value=1, description="How long should the brew session wait before continuing? If you select 0 then it will wait for user to click Start Next Step.")
    s = False

    @cbpi.action("Start Timer")
    def start(self):
        self.s = False
        if self.is_timer_finished() is None:
            self.start_timer(int(self.timer)+1)

    def reset(self):
        self.stop_timer()

    def execute(self):
        if self.is_timer_finished() is None:
            self.start_timer(int(self.timer)+1)
        if self.s == False:
            self.s = True
            if int(self.timer) == 0:
                self.notify(self.messagetodisplay, "Please select \"Next Step\" to continue", type="warning", timeout=None)
            else:
                self.notify(self.messagetodisplay, "Brewing will continue automatically when the timer completes.", type="info", timeout=((int(self.timer)-1)*1000))
        if self.is_timer_finished() == True:
            if int(self.timer) == 0:
                pass
            else:
                self.next()

################################################################################
@cbpi.step
class SimpleWhirlpoolStep(StepBase):

    kettle = StepProperty.Kettle("Kettle", description="Kettle in which the chilling takes place")
    chiller = StepProperty.Actor("Chiller", description="Actor that controls the Chiller")
    chillerPump = StepProperty.Actor("chillerPump", description="Actor that controls the chillerPump")
    temp = Property.Number("Whirlpool Temperature", configurable=True, default_value=68, description="Target Temperature of Whirlpool")
    timer = Property.Number("Total Whirlpool Timer in Minutes (incl. Santise Time)", configurable=True, default_value=30, description="Timer is started immediately")
    sanitiseTimer = Property.Number("Sanitise Timer in Minutes", configurable=True, default_value=5, description="Time at sanitisation temp")
    sanitiseTemp = Property.Number("Sanitise Temperature", configurable=True, default_value=95, description="Target Temperature for sanitisation")
    s_end = 1
    stage = "init" #This process goes through the following stages: init, waithookup, sanitise, whirlpool
    c_cut = 0
    
    def init(self):
        self.stage = "init"
        self.actor_off(int(self.chillerPump))
        self.actor_off(int(self.chiller))
        self.set_target_temp(self.sanitiseTemp, self.kettle)
        self.s_end = 1
        self.c_cut = 0
    
    def start(self):
        pass

    def reset(self):
        self.stop_timer()

    def finish(self):
        self.actor_off(int(self.chillerPump))
        self.actor_off(int(self.chiller))
    
    @cbpi.action("Chiller Connected")
    def chiller_connected(self):
        if self.stage == "waithookup":
            self.stage = "sanitise"
            self.actor_on(int(self.chillerPump))
            self.s_end = (self.timer_remaining() - (60 * int(self.sanitiseTimer)))
        else:
            self.notify("No Action Taken", "Function only works in \"waithookup\" sub-stage. Current stage: " + self.stage, type="info", timeout=5000)
    
    def execute(self):
        if self.is_timer_finished() is None:
            self.start_timer(int(self.timer) * 60)
        if self.is_timer_finished() == True:
            if self.stage != "whirlpool":
                self.notify("ERROR - Whirlpool incomplete", "Step completed without reaching internal whirlpool stage", type="danger", timeout=None)
            self.actor_off(int(self.chiller))
            self.actor_off(int(self.chillerPump))
            self.next()
        else:
            if self.get_kettle_temp(self.kettle) >= (self.get_target_temp(self.kettle)+10): #This option determines when the chiller is full on
                self.actor_on(int(self.chiller))
            elif self.get_kettle_temp(self.kettle) >= self.get_target_temp(self.kettle): #This option specifies partial activation - alternate 3secs on and off
                self.c_cut = int((self.timer_remaining()/3))
                if self.c_cut%2:
                    self.actor_on(int(self.chiller))
                else:
                    self.actor_off(int(self.chiller))
            else:
                self.actor_off(int(self.chiller))
        if self.stage == "init":
            self.notify("Put on the lid and connect the chiller", "Please select \"Chiller Connected\" to continue", type="warning", timeout=None)
            self.stage = "waithookup"
        elif self.stage == "sanitise":
            if self.s_end >= self.timer_remaining():
                self.stage = "whirlpool"
                self.set_target_temp(self.temp, self.kettle)

################################################################################
@cbpi.step
class SimpleChillStep(StepBase):

    kettle = StepProperty.Kettle("Kettle", description="Kettle in which the chilling takes place")
    chiller = StepProperty.Actor("Chiller", description="Actor that controls the Chiller")
    chillerPump = StepProperty.Actor("chillerPump", description="Actor that controls the chillerPump")
    chillerTemp = StepProperty.Sensor("Chiller Temp", description="Sensor that shows the chiller temperature")
    cutoutvariance = Property.Number("Variance between kettle and chiller for end", configurable=True, default_value=0.3, description="The step will end when the kettle temp falls to within this much of the chiller temp.")
    
    def init(self):
        self.actor_on(int(self.chillerPump))
        self.actor_on(int(self.chiller))
        self.set_target_temp(0, self.kettle)
    
    def start(self):
        pass

    def reset(self):
        pass

    def finish(self):
        self.actor_off(int(self.chillerPump))
        self.actor_off(int(self.chiller))
    
    def execute(self):
        if self.get_kettle_temp(self.kettle) <= (self.get_sensor_value(self.chillerTemp)+float(self.cutoutvariance)):
            self.notify("Chill Stage Complete", "Kettle reached: " + str(self.get_kettle_temp(self.kettle)), type="success", timeout=None)
            self.actor_off(int(self.chiller))
            self.actor_off(int(self.chillerPump))
            self.next()

################################################################################
@cbpi.step
class SimpleMashOutStep(StepBase):

    kettle = StepProperty.Kettle("Kettle", description="Kettle in which the chilling takes place")
    temp = Property.Number("MashOut Temperature", configurable=True, default_value=76.7, description="Target Temperature of Mashout")
    timer = Property.Number("MashOut Timer in Minutes", configurable=True, default_value=10, description="Time to be held at Mashout temp")
    stage = "init" #This process goes through the following stages: init, mashout, sparge, preboil, hotbreak
    preboiltemp = 90
    hotbreaktemp = 99
    wait_user = False

    def init(self):
        self.stage = "init"
        self.wait_user = False
        self.set_target_temp(self.temp, self.kettle)
        # self.preboiltemp = self.api.cache.get("kettle").get(self.kettle).get_config_parameter("e_max_temp_pid")
        # self.hotbreaktemp = 99
    
    def start(self):
        pass

    def reset(self):
        pass

    def finish(self):
        pass
    
    @cbpi.action("Sparge Complete")
    def sparge_complete(self):
        if self.stage == "sparge":
            self.stage = "preboil"
            self.wait_user = False
            self.set_target_temp(self.preboiltemp, self.kettle)
        else:
            self.notify("No Action Taken", "Function only works in \"sparge\" sub-stage. Current stage: " + self.stage, type="info", timeout=5000)

    @cbpi.action("Removed Lid")
    def lid_removed(self):
        if self.stage == "preboil":
            self.stage = "hotbreak"
            self.wait_user = False
            self.set_target_temp(self.hotbreaktemp, self.kettle)
        else:
            self.notify("No Action Taken", "Function only works in \"preboil\" sub-stage. Current stage: " + self.stage, type="info", timeout=5000)

    @cbpi.action("Hotbreak Finished")
    def hotbreak_finished(self):
        if self.stage == "hotbreak":
            self.wait_user = False
            self.next()
        else:
            self.notify("No Action Taken", "Function only works in \"hotbreak\" sub-stage. Current stage: " + self.stage, type="info", timeout=5000)

    def execute(self):
        if self.stage == "init": #let the kettle heat to mash out temp
            if self.get_kettle_temp(self.kettle) >= self.temp:
                self.stage = "mashout"
        elif self.stage == "mashout": #run the mash timer
            if self.is_timer_finished() is None:
                self.start_timer(int(self.timer) * 60) 
            if self.is_timer_finished() == True:
                self.stage = "sparge"
        elif self.stage == "sparge": #wait for user confirmation to continue
            if self.wait_user == False:
                self.notify("MASH OUT COMPLETE", "Sparge and then select \"Sparge Complete\" to continue.", type="warning", timeout=None)
                self.wait_user = True
        elif self.stage == "preboil": #let the kettle heat to pre-boil, then wait for user to remove lid
            if self.get_kettle_temp(self.kettle) >= self.preboiltemp:
                if self.wait_user == False:
                    self.notify("REMOVE THE LID", "Heated to Pre-Boil. Remove the lid and click \"Removed Lid\" to continue.", type="warning", timeout=None)
                    self.wait_user = True
        elif self.stage == "hotbreak": #heat kettle to boil, then wait for user for user to go to boil stage
            if self.get_kettle_temp(self.kettle) >= self.hotbreaktemp:
                if self.wait_user == False:
                    self.notify("WATCH FOR HOTBREAK", "When hotbreak is complete click \"Hotbreak Finished\" to continue.", type="warning", timeout=None)
                    self.wait_user = True
        else: #An error has occured! Not in a valid status
            self.notify("INVALID STAGE", "An invalid stage has been returned. Current stage: " + self.stage, type="dangar", timeout=None)

################################################################################
def getAgitator(value):
    try: return int(float(value))
    except: return 0
