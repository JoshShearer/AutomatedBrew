from modules import cbpi
from modules.core.props import Property
from modules.core.hardware import ActorBase

@cbpi.actor
class ScalableDependentActor(ActorBase):
    
    base = Property.Actor(label="Dependent Actor", description="Select the actor which will be dependent to master one.")
    dependency = Property.Actor(label="Master Actor", description="Select the actor that will control the dependent one selected above.")

    def init(self):
        # Switch off the Dependent Actor
        self.api.switch_actor_off(int(self.base))
        # Hide Base Actor
        for idx, value in cbpi.cache["actors"].iteritems():
            if idx == int(self.base):
                value.hide = True
        # Synchronize current power setting with the Base Actor
       
    def set_power(self, power):
        
        potenciaMaster = self.api.actor_power(int(self.dependency))
        
        potenciaDif = 100 - int(potenciaMaster)
                       
        self.api.actor_power(int(self.base), power=int(potenciaDif))
        

    def off(self):
        self.api.switch_actor_off(int(self.base))

    def on(self, power=None):
        dependency_name = ""
        for idx, value in cbpi.cache["actors"].iteritems():
            if idx == int(self.dependency):
                dependency_name = value.name
        for idx, value in cbpi.cache["actors"].iteritems():
            if idx == int(self.dependency):
                if (value.state == 0):
                    self.api.switch_actor_on(int(self.base), power=100)
                elif (value.state == 1) & (self.api.actor_power(int(self.dependency))==100):
                    self.api.switch_actor_off(int(self.base))
                elif (value.state == 1) & (self.api.actor_power(int(self.dependency))<100):
                    potenciaMaster = self.api.actor_power(int(self.dependency))
                    potenciaDif = 100 - int(potenciaMaster)
                    self.api.switch_actor_on(int(self.base), power=potenciaDif)

