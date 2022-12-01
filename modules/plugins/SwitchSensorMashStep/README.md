# SensorSwitchMashStep Plugin for CraftBeerPi 3.0

This is a very simple plugin that adds a second temperature sensor to the MashStep.  This step set the kettle temperature based on the sensor previously assigned to the kettle and turn on a secondary actor (ex. pump, etc.).  Then the step timer will not start until the secondary sensor value is equal to the kettle sensor value.  This is would be useful for a HERMES or similiar system in which you are not directly heating your mash or you are not directly heating your mash with a high-powered heat source.

## Usage
1.  Download the Sensor Switch MashStep plugin from within CraftBeerPi 3.0, and then reboot your Raspberry Pi.
2.  Configure a new brewing step, and select SwitchSensorMashStep as the type.
3.  Enter values for the following settings:
    1.  **temp**: Target Temperature of Mash Step.
    2.  **kettle**: Kettle in which the mashing takes place.
    3.  **timer**: Timer is started when the target temperature is reached.
    4.  **sensor**: Selectable secondary sensor
    5.  **pump**: Pump, et.
    4.  Click **Update** to save your configuration.
