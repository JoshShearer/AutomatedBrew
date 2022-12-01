# ModMeshStep Plug-in
This plugin is made for CraftBeerPi3 to extend protective capabilities in regards to a problem which could occur with SSR when they fail (shortened).
In situation like that, mash can be cooked and destroyed.
This plugin adds new step called "Mod_MeshStep" to steps and for the implementation it is needed to have relay board (1 relay reserved) and high current circuit breaker (16+ A).
Plugin is only lightly modified base plugin for brewing step. In this version, protection is relaying on the same sensor data as for the kettle which is being protected/monitored.

Idea is to introduce "Protective Circuit" which will, when triggered:
- stop brewing process, after which manual intervention to continue the brewing is needed (by reseting  current step or skipping to next one)
- showing remaining time when protection was activated.
- by activating protective circuit disconnects output of the SSR used for heating, in order to protect the mash from higher temperature.

How to Config:
- Add an Actor which will act as protective circuit/relay. Typically one output of relay board.
- Add the Mod_MeshStep to your brewing steps:
    a) assign  Protective circuit
    b) set temperature difference. (default is 8C)
- Connect high power breaker to your SSR output. (Check schematics)

Additional info:
Temperature threshold is the temperature when protection will kick in and disconnect SSR output.
Threshold temperature = Temperature (for mashing) + temperature difference

