# cbpi-ExtendedMenu

This plugin adds an additional menu to your CraftBeerPi

### Installing
If you have installed an old version of cbpi-BetterCharts it's maybe necessare to restore the index.html of your CraftBeerPi

```
cd craftbeerpi3
git checkout -- modules/ui/static/index.html
cd ..
```

Open the console and change the dir to plugins

```
cd craftbeerpi3/modules/plugins
```

clone this repository

```
git clone https://github.com/MiracelVip/cbpi-ExtendedMenu
```

restart your Raspberry

```
sudo reboot
```


## Overview

After rebooting your Raspberry you should see the menu on the bottom of the wab interface. By clicking on the gear-icon you can reach the admin interface where you can edit the links.
Remember: Every change in the admin interface requires a reboot!


![Alt text](images/cbpi-ExtendedMenu-admin.png?raw=true "Admin")
![Alt text](images/cbpi-ExtendedMenu.png?raw=true "cbpi")



## License

This project is licensed under the MIT License.
