# GPIObutton

This is a CraftBeerPi 3.0 sensor that allows you to have up to 4 physical buttons in order to accept GPIO button press after which it performs an API call. 

The momentary switches are in low state by default and should get 3,3v to be activated. The sensor can be hidden on the dashboard as it does not return a sensor value.

Note: applying voltage on your GPIO pins is at your own risk.



## Config

Base URL: points to your CraftBeerPi, don't use a trailing /

Debounce time: if your switch does not behave increase this value.

Then for every button you need to specify:

GPIO: GPIO port number, set this to 99 for the buttons that you don't use.

GET or POST: API calls use get or post. 

API command: trailing part of the API call, for instance /actor/2/toggle, put in a / for buttons you don't use.

hint: in Chrome use developer tools (ctrl-shift-I), Network. If you click an actor, it will show you the url it used. On an actor it will say something like toggle, click on toggle and then under Request method it will say POST or GET.
