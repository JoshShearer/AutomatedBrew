# InvertPWM
Inverted GPIOPWM for CraftBeerPi 3.
### This Plugin is for CraftBeerPi 3
This is an add on for the CraftBeerPi 3 that is an inverted form of the GPIOPWM. This Pugin is for people who run there SSRs inverted meaning that the GPIO control pin is on the neg post of the SSRs and the SSRs are being feed power constantly from a header pin. This setup is the same as you would with a Relay Board.  
# InvertLogic
Power step down logic to the InvertPWM actor
### This Plugin is for CraftBeerPi 3 and only for InvertPWM actor on heater
This logic allows the user to pick a percent of power reduction of the currently set power setting.  This step down in power will start at a picked degee from target temp.  The Power level will automatically go back to it's full preselected power level when target temp is outside reduction temp reange.  There is also a ramp up feature that helps with amp draw from the heater.  This setting alows you to pick the percent of power the heater will increase in 1/10 sec cycles until at desired power level.
### Bug!
This logic and actor uses a shared variable for the power level.  Because of this all actors running InvertPWM will share the same power setpoint.  
