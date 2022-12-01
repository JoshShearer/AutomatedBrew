# -*- coding: utf-8 -*-
import time

from modules.core.props import Property, StepProperty
from modules.core.step import StepBase
from modules import cbpi
import traceback

@cbpi.step
class AutoSwitch(StepBase):

    # Properties
    a_id = StepProperty.Kettle("Kettle")
    b_auto = Property.Select("Auto Setting", options=["On", "Off"])

    def init(self):
        if isinstance(self.a_id, unicode) and self.a_id:
            self.id = (int(self.a_id))
        self.auto_type = self.b_auto
        try:
            kettle = cbpi.cache.get("kettle").get(self.id)
            if kettle.state is False and self.auto_type == "On":
                # Start controller
                if kettle.logic is not None:
                    cfg = kettle.config.copy()
                    cfg.update(dict(api=cbpi, kettle_id=kettle.id, heater=kettle.heater, sensor=kettle.sensor))
                    instance = cbpi.get_controller(kettle.logic).get("class")(**cfg)
                    instance.init()
                    kettle.instance = instance
                    def run(instance):
                        instance.run()
                    t = self.api.socketio.start_background_task(target=run, instance=instance)
                kettle.state = True
                cbpi.emit("UPDATE_KETTLE", kettle)
            elif kettle.state is True and self.auto_type == "Off":
                # Stop controller
                kettle.instance.stop()
                kettle.state = False
                cbpi.emit("UPDATE_KETTLE", kettle)
        except Exception as e:
            cbpi.notify("Auto Error", "Failed to switch auto", type="danger", timeout=0)
            traceback.print_exc()
            
	def finish(self):
		pass

	def execute(self):
		self.next()
