from modules.core.props import Property, StepProperty
from modules.core.step import StepBase
from modules import cbpi

@cbpi.step
class PauseStep(StepBase):
    def init(self):
            self.notify("Pause!", "Please press the next button to continue", timeout=None)

