# CBPi Plugin

## SimpleSteps

Collection of simple CraftBeerPi3 brew steps to do a few useful additional things.

### SimpleManualStep

Display a customizable notification and optionally pause the steps.  Intended to tell you when to take some manual action not automated by CraftBeerPi.

### SimpleTargetStep

Set the Auto mode and/or Target Temperature of a kettle, without waiting for target to be met. For example, to start heating your sparge water somewhere in the middle of your mash.

### SimpleActorTimer

Turn on an actor for a specified time period.

### SimpleChillToTemp

Turn on an actor until temperature is _reduced_ to a target temperature.

### SimpleClearLogsStep

Clears log files (presumably at the start of the brew) so your charts etc. don't include superfluous data.

### SimpleSaveLogsStep

Copies logs and pre-pends brew name

### SimpleToggleStep

This step will turn on, turn off, or set the power on any actor, and then immediately continue with the next step.

### SimpleMashStep

Turn on agitator on mash step start. Turn off agitator in mash step end.

### SimpleMashInStep

Turn on agitator while heating and switch off when target temperature is reached.

### SimpleBoilStep

Notification before starting boil step.
Notificatiom on each hop additions.

### SimpleMashOutStep

### SimpleChillStep

### SimpleWhirlpoolStep
